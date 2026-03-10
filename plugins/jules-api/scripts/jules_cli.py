#!/usr/bin/env python3
"""jules_cli.py — Jules REST API v1alpha client.

Deterministic CLI wrapper for the Google Jules REST API.
Reference: https://jules.google/docs/api/reference/

Design goals:
- Strict JSON output (stdout=JSON, stderr=error text, exit code signals failure)
- Correct field names per official API schema
- Full pagination + incremental polling support
- Conservative timeouts
- No bash quoting foot-guns

Auth:
  Set JULES_API_KEY env var (preferred) or pass --api-key.

Usage:
  jules_cli.py sources list [--page-size N] [--all-pages]
  jules_cli.py sources get <source-name>

  jules_cli.py sessions list [--page-size N] [--all-pages]
  jules_cli.py sessions get <session-id>
  jules_cli.py sessions create --prompt TEXT [--title TEXT] [--source NAME]
                               [--branch BRANCH] [--automation-mode MODE]
                               [--require-plan-approval]
  jules_cli.py sessions send <session-id> --prompt TEXT
  jules_cli.py sessions approve-plan <session-id>
  jules_cli.py sessions delete <session-id>

  jules_cli.py activities list <session-id> [--page-size N] [--all-pages]
                                            [--since ISO8601]
  jules_cli.py activities get <session-id> <activity-id>
  jules_cli.py activities summary <session-id>
  jules_cli.py activities last-message <session-id>

  Unofficial session lifecycle (may change):
  jules_cli.py sessions cancel <session-id>
  jules_cli.py sessions pause <session-id>
  jules_cli.py sessions resume <session-id>
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

BASE_URL = "https://jules.googleapis.com/v1alpha"
DEFAULT_TIMEOUT = 60.0
MAX_AUTO_PAGES = 10
MAX_RETRIES = 3
RETRY_BASE_SEC = 5.0


def eprint(*args: object) -> None:
    print(*args, file=sys.stderr)


def die(msg: str, code: int = 1) -> None:
    eprint(f"Error: {msg}")
    sys.exit(code)


def dump(obj: Any) -> None:
    print(json.dumps(obj, ensure_ascii=False, indent=2))


class JulesClient:
    def __init__(self, api_key: str, base_url: str = BASE_URL, timeout: float = DEFAULT_TIMEOUT):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def _headers(self) -> dict[str, str]:
        return {
            "x-goog-api-key": self.api_key,
            "Content-Type": "application/json",
        }

    def request(
        self,
        method: str,
        path: str,
        *,
        query: dict[str, Any] | None = None,
        body: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        url = f"{self.base_url}{path}"
        if query:
            filtered = {k: str(v) for k, v in query.items() if v is not None}
            if filtered:
                url = f"{url}?{urllib.parse.urlencode(filtered)}"

        data = json.dumps(body).encode("utf-8") if body is not None else None
        req = urllib.request.Request(url=url, method=method, data=data, headers=self._headers())

        for attempt in range(MAX_RETRIES + 1):
            try:
                with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                    raw = resp.read()
                    return json.loads(raw.decode("utf-8")) if raw else {}
            except urllib.error.HTTPError as ex:
                if ex.code == 429 and attempt < MAX_RETRIES:
                    wait = RETRY_BASE_SEC * (2 ** attempt)
                    eprint(f"Rate limited (429), retrying in {wait:.0f}s (attempt {attempt+1}/{MAX_RETRIES})...")
                    time.sleep(wait)
                    req = urllib.request.Request(url=url, method=method, data=data, headers=self._headers())
                    continue

                raw_body = ex.read()
                text = raw_body.decode("utf-8", errors="replace") if raw_body else ""
                try:
                    detail = json.loads(text) if text else {}
                except Exception:
                    detail = {"raw": text}
                api_error = detail.get("error", {}) if isinstance(detail, dict) else {}
                raise RuntimeError(json.dumps({
                    "error": {
                        "http_status": ex.code,
                        "reason": ex.reason,
                        "url": url,
                        "api_code": api_error.get("code"),
                        "api_message": api_error.get("message"),
                        "api_status": api_error.get("status"),
                        "detail": detail,
                    }
                }, ensure_ascii=False))
            except urllib.error.URLError as ex:
                raise RuntimeError(json.dumps({
                    "error": {"type": "url_error", "reason": str(ex.reason), "url": url}
                }, ensure_ascii=False))
        raise RuntimeError(json.dumps({"error": {"type": "max_retries", "url": url}}))

    def paginate(self, path: str, result_key: str, page_size: int | None, all_pages: bool) -> dict[str, Any]:
        items: list[Any] = []
        page_token: str | None = None
        pages = 0

        while True:
            query: dict[str, Any] = {}
            if page_size:
                query["pageSize"] = page_size
            if page_token:
                query["pageToken"] = page_token

            resp = self.request("GET", path, query=query or None)
            items.extend(resp.get(result_key, []))
            page_token = resp.get("nextPageToken")
            pages += 1

            if not all_pages or not page_token or pages >= MAX_AUTO_PAGES:
                break

        result: dict[str, Any] = {result_key: items, "_pages_fetched": pages}
        if page_token:
            result["nextPageToken"] = page_token
        return result

    # -- Sources -----------------------------------------------------------

    def sources_list(self, page_size: int | None = None, all_pages: bool = False, filter_expr: str | None = None) -> dict:
        if filter_expr:
            ps = page_size or 100
            return self.request("GET", "/sources", query={"pageSize": ps, "filter": filter_expr})
        return self.paginate("/sources", "sources", page_size, all_pages)

    def sources_get(self, name: str) -> dict:
        if not name.startswith("sources/"):
            name = f"sources/{name}"
        return self.request("GET", f"/{name}")

    # -- Sessions ----------------------------------------------------------

    def sessions_list(self, page_size: int | None = None, all_pages: bool = False) -> dict:
        return self.paginate("/sessions", "sessions", page_size, all_pages)

    def sessions_get(self, session_id: str) -> dict:
        return self.request("GET", f"/sessions/{session_id}")

    def sessions_create(
        self,
        *,
        prompt: str,
        title: str | None = None,
        source: str,
        starting_branch: str = "main",
        automation_mode: str = "AUTO_CREATE_PR",
        require_plan_approval: bool = False,
    ) -> dict:
        body: dict[str, Any] = {
            "prompt": prompt,
            "sourceContext": {
                "source": source,
                "githubRepoContext": {"startingBranch": starting_branch},
            },
            "automationMode": automation_mode,
            "requirePlanApproval": require_plan_approval,
        }
        if title:
            body["title"] = title
        return self.request("POST", "/sessions", body=body)

    def sessions_send(self, session_id: str, prompt: str) -> dict:
        return self.request("POST", f"/sessions/{session_id}:sendMessage", body={"prompt": prompt})

    def sessions_approve_plan(self, session_id: str) -> dict:
        return self.request("POST", f"/sessions/{session_id}:approvePlan", body={})

    def sessions_cancel(self, session_id: str) -> dict:
        return self.request("POST", f"/sessions/{session_id}:cancel", body={})

    def sessions_pause(self, session_id: str) -> dict:
        return self.request("POST", f"/sessions/{session_id}:pause", body={})

    def sessions_resume(self, session_id: str) -> dict:
        return self.request("POST", f"/sessions/{session_id}:resume", body={})

    def sessions_delete(self, session_id: str) -> dict:
        return self.request("DELETE", f"/sessions/{session_id}")

    # -- Activities --------------------------------------------------------

    def activities_list(self, session_id: str, page_size: int | None = None, all_pages: bool = False, since: str | None = None) -> dict:
        if since:
            ps = page_size or 100
            return self.request("GET", f"/sessions/{session_id}/activities", query={"pageSize": ps, "createTime": since})
        return self.paginate(f"/sessions/{session_id}/activities", "activities", page_size, all_pages)

    def activities_get(self, session_id: str, activity_id: str) -> dict:
        return self.request("GET", f"/sessions/{session_id}/activities/{activity_id}")


# ---------------------------------------------------------------------------
# Activity helpers
# ---------------------------------------------------------------------------

def _activity_type(a: dict) -> str:
    for key in ("agentMessaged", "userMessaged", "planGenerated", "planApproved",
                "progressUpdated", "sessionCompleted", "sessionFailed"):
        if key in a:
            return key
    return "unknown"


def _activity_text(a: dict) -> str:
    atype = _activity_type(a)
    if atype == "agentMessaged":
        return a["agentMessaged"].get("agentMessage", "")
    if atype == "userMessaged":
        return a["userMessaged"].get("userMessage", "")
    if atype == "planGenerated":
        steps = a["planGenerated"].get("plan", {}).get("steps", [])
        return f"Plan ({len(steps)} steps):\n" + "\n".join(f"  {s['index']+1}. {s['title']}" for s in steps)
    if atype == "planApproved":
        return f"Plan approved: {a['planApproved'].get('planId', '')}"
    if atype == "progressUpdated":
        pu = a["progressUpdated"]
        return f"{pu.get('title', '')}: {pu.get('description', '')}"
    if atype == "sessionCompleted":
        return "Session completed"
    if atype == "sessionFailed":
        return f"Session failed: {a['sessionFailed'].get('reason', '')}"
    return a.get("description", "")


def _extract_changed_files(activities: list[dict]) -> list[str]:
    files: list[str] = []
    for a in activities:
        for artifact in a.get("artifacts", []):
            diff = artifact.get("changeSet", {}).get("gitPatch", {}).get("unidiffPatch", "")
            for line in diff.splitlines():
                if line.startswith("+++ b/"):
                    fname = line[6:]
                    if fname not in files:
                        files.append(fname)
    return files


def _extract_pr_url(session: dict) -> str:
    for out in session.get("outputs", []):
        url = out.get("pullRequest", {}).get("url", "")
        if url:
            return url
    return ""


def activities_summary(session: dict, activities: list[dict]) -> dict:
    last_agent_msg = ""
    for a in reversed(activities):
        if _activity_type(a) == "agentMessaged":
            last_agent_msg = a["agentMessaged"].get("agentMessage", "")
            break

    last_progress = ""
    for a in reversed(activities):
        if _activity_type(a) == "progressUpdated":
            pu = a["progressUpdated"]
            last_progress = f"{pu.get('title', '')}: {pu.get('description', '')}"
            break

    plan_steps: list[str] = []
    for a in reversed(activities):
        if _activity_type(a) == "planGenerated":
            steps = a["planGenerated"].get("plan", {}).get("steps", [])
            plan_steps = [f"{s.get('index', i)+1}. {s.get('title', '')}" for i, s in enumerate(steps)]
            break

    failure_reason = ""
    for a in reversed(activities):
        if _activity_type(a) == "sessionFailed":
            failure_reason = a["sessionFailed"].get("reason", "")
            break

    return {
        "session_id": session.get("id", ""),
        "title": session.get("title", ""),
        "state": session.get("state", ""),
        "url": session.get("url", ""),
        "pr_url": _extract_pr_url(session),
        "last_agent_message": last_agent_msg[:500] if last_agent_msg else "",
        "last_progress": last_progress,
        "plan_steps": plan_steps,
        "changed_files": _extract_changed_files(activities),
        "failure_reason": failure_reason,
        "activity_count": len(activities),
        "last_activity_time": activities[-1].get("createTime", "") if activities else "",
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="jules_cli.py", description="Jules REST API v1alpha CLI")
    p.add_argument("--api-key", default=None, help="Jules API key (overrides JULES_API_KEY env)")
    p.add_argument("--base-url", default=BASE_URL)
    p.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT)

    sub = p.add_subparsers(dest="resource", required=True)

    # sources
    src = sub.add_parser("sources")
    src_sub = src.add_subparsers(dest="action", required=True)
    src_list = src_sub.add_parser("list")
    src_list.add_argument("--page-size", type=int, default=None)
    src_list.add_argument("--all-pages", action="store_true")
    src_list.add_argument("--filter", default=None, dest="filter_expr")
    src_get = src_sub.add_parser("get")
    src_get.add_argument("name")

    # sessions
    ses = sub.add_parser("sessions")
    ses_sub = ses.add_subparsers(dest="action", required=True)
    ses_list = ses_sub.add_parser("list")
    ses_list.add_argument("--page-size", type=int, default=None)
    ses_list.add_argument("--all-pages", action="store_true")
    ses_get = ses_sub.add_parser("get")
    ses_get.add_argument("session_id")
    ses_create = ses_sub.add_parser("create")
    ses_create.add_argument("--prompt", required=True)
    ses_create.add_argument("--title", default=None)
    ses_create.add_argument("--source", required=True, help="Source name, e.g. sources/github/owner/repo")
    ses_create.add_argument("--branch", default="main")
    ses_create.add_argument("--automation-mode", default="AUTO_CREATE_PR",
                            choices=["AUTO_CREATE_PR", "AUTOMATION_MODE_UNSPECIFIED"])
    ses_create.add_argument("--require-plan-approval", action="store_true", default=False)
    ses_send = ses_sub.add_parser("send")
    ses_send.add_argument("session_id")
    ses_send.add_argument("--prompt", required=True)
    ses_approve = ses_sub.add_parser("approve-plan")
    ses_approve.add_argument("session_id")
    for cmd in ("cancel", "pause", "resume", "delete"):
        sp = ses_sub.add_parser(cmd)
        sp.add_argument("session_id")

    # activities
    act = sub.add_parser("activities")
    act_sub = act.add_subparsers(dest="action", required=True)
    act_list = act_sub.add_parser("list")
    act_list.add_argument("session_id")
    act_list.add_argument("--page-size", type=int, default=None)
    act_list.add_argument("--all-pages", action="store_true")
    act_list.add_argument("--since", default=None)
    act_get = act_sub.add_parser("get")
    act_get.add_argument("session_id")
    act_get.add_argument("activity_id")
    act_summary = act_sub.add_parser("summary")
    act_summary.add_argument("session_id")
    act_summary.add_argument("--since", default=None)
    act_last = act_sub.add_parser("last-message")
    act_last.add_argument("session_id")
    act_last.add_argument("--since", default=None)

    return p


def run(args: argparse.Namespace, client: JulesClient) -> None:
    resource = args.resource
    action = args.action

    if resource == "sources":
        if action == "list":
            dump(client.sources_list(args.page_size, args.all_pages, getattr(args, "filter_expr", None)))
        elif action == "get":
            dump(client.sources_get(args.name))

    elif resource == "sessions":
        if action == "list":
            dump(client.sessions_list(args.page_size, args.all_pages))
        elif action == "get":
            dump(client.sessions_get(args.session_id))
        elif action == "create":
            dump(client.sessions_create(
                prompt=args.prompt, title=args.title, source=args.source,
                starting_branch=args.branch, automation_mode=args.automation_mode,
                require_plan_approval=args.require_plan_approval,
            ))
        elif action == "send":
            dump(client.sessions_send(args.session_id, args.prompt))
        elif action == "approve-plan":
            dump(client.sessions_approve_plan(args.session_id))
        elif action == "cancel":
            dump(client.sessions_cancel(args.session_id))
        elif action == "pause":
            dump(client.sessions_pause(args.session_id))
        elif action == "resume":
            dump(client.sessions_resume(args.session_id))
        elif action == "delete":
            dump(client.sessions_delete(args.session_id))

    elif resource == "activities":
        if action == "list":
            dump(client.activities_list(args.session_id, args.page_size, args.all_pages, getattr(args, "since", None)))
        elif action == "get":
            dump(client.activities_get(args.session_id, args.activity_id))
        elif action == "summary":
            session = client.sessions_get(args.session_id)
            since = getattr(args, "since", None)
            acts_resp = client.activities_list(args.session_id, page_size=100, all_pages=(since is None), since=since)
            dump(activities_summary(session, acts_resp.get("activities", [])))
        elif action == "last-message":
            since = getattr(args, "since", None)
            acts_resp = client.activities_list(args.session_id, page_size=100, all_pages=(since is None), since=since)
            for a in reversed(acts_resp.get("activities", [])):
                if _activity_type(a) == "agentMessaged":
                    print(a["agentMessaged"].get("agentMessage", ""))
                    return
            for a in reversed(acts_resp.get("activities", [])):
                if _activity_type(a) == "progressUpdated":
                    pu = a["progressUpdated"]
                    print(f"{pu.get('title', '')}: {pu.get('description', '')}")
                    return
            print("")


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    api_key = args.api_key or os.environ.get("JULES_API_KEY", "")
    if not api_key:
        die("JULES_API_KEY not set. Export it or pass --api-key.")

    client = JulesClient(api_key=api_key, base_url=args.base_url, timeout=args.timeout)

    try:
        run(args, client)
    except RuntimeError as ex:
        eprint(str(ex))
        sys.exit(1)
    except Exception as ex:
        eprint(f"Unexpected error: {ex}")
        sys.exit(1)


if __name__ == "__main__":
    main()
