---
name: jules-api
description: >
  Interact with the Google Jules REST API v1alpha to manage autonomous coding sessions.
  Use when: user asks to create Jules tasks, check session status, send messages to Jules,
  list activities, get summaries, manage session lifecycle, or automate PR workflows.
  Triggers: "jules", "delegate to Jules", "jules session", "jules task", "jules PR",
  "start a Jules session", "check Jules status", "jules coding agent".
globs:
  - "**/jules*.py"
  - "**/jules*.sh"
---

# Jules API — Google's Autonomous Coding Agent

Jules runs async coding sessions in the cloud, clones your GitHub repo, writes code, then opens a PR for review.

## Setup

1. Get a Jules API key from [jules.google.com](https://jules.google.com)
2. Set the environment variable:
   ```bash
   export JULES_API_KEY="your-api-key-here"
   ```

## CLI Usage

The plugin includes `jules_cli.py` — a deterministic Python CLI for the Jules REST API.

```bash
JULES_CLI="python3 $(dirname "$0")/../scripts/jules_cli.py"

# List sessions
$JULES_CLI sessions list --page-size 10

# Get a session
$JULES_CLI sessions get <session-id>

# Create a session (auto PR, no plan approval needed)
$JULES_CLI sessions create \
  --source "sources/github/OWNER/REPO" \
  --prompt "feat: implement withdrawal endpoint" \
  --title "feat: withdrawal" \
  --automation-mode AUTO_CREATE_PR

# Send a message to a session
$JULES_CLI sessions send <session-id> --prompt "Please add tests."

# Approve a plan (only if created with --require-plan-approval)
$JULES_CLI sessions approve-plan <session-id>

# Compact summary (great for monitoring)
$JULES_CLI activities summary <session-id>

# Last agent message (plain text)
$JULES_CLI activities last-message <session-id>

# List activities with incremental polling
$JULES_CLI activities list <session-id> --since "2026-01-01T00:00:00Z"

# Session lifecycle (unofficial)
$JULES_CLI sessions cancel <session-id>
$JULES_CLI sessions pause <session-id>
$JULES_CLI sessions resume <session-id>
$JULES_CLI sessions delete <session-id>
```

## Output Contract

- **stdout**: valid JSON (always)
- **stderr**: error messages (on failure)
- **exit code**: 0 = success, 1 = error

## Key API Concepts

### AutomationMode
- `AUTO_CREATE_PR` — Jules auto-creates branch + PR when done ✅ (recommended)
- `AUTOMATION_MODE_UNSPECIFIED` — no PR created (default if not set)

### Plan Approval
- `requirePlanApproval: false` (default) — plans auto-approved, Jules codes immediately
- `requirePlanApproval: true` — waits for explicit approval before coding

### Session States
`QUEUED` → `PLANNING` → `IN_PROGRESS` / `AWAITING_PLAN_APPROVAL` / `AWAITING_USER_FEEDBACK` → `COMPLETED` / `FAILED` / `PAUSED`

### Activity Types
`agentMessaged` / `userMessaged` / `planGenerated` / `planApproved` / `progressUpdated` / `sessionCompleted` / `sessionFailed`

## Usage Limits

| Plan  | Daily Tasks (24h rolling) | Concurrent |
|-------|--------------------------|------------|
| Free  | 15                       | 3          |
| Pro   | 100                      | 15         |
| Ultra | 300                      | 60         |

## Alternative: GitHub Issue Label Trigger

Add label `jules` to any GitHub issue → Jules picks it up automatically.
- Does **not** consume API task quota
- Best for simple, non-interactive tasks

## Workflow Tips

- Keep prompts specific: "Add a test for X in Y.js" beats "improve tests"
- Add `AGENTS.md` to your repo root — Jules reads it for codebase conventions
- Use `activities summary` for compact monitoring in cron/watcher scripts
- `sendMessage` returns empty response; agent reply appears as next activity

## References

- [Jules API Overview](https://jules.google/docs/api/reference/overview)
- [Sessions Reference](https://jules.google/docs/api/reference/sessions)
- [Activities Reference](https://jules.google/docs/api/reference/activities)
- [Usage Limits](https://jules.google/docs/usage-limits/)
- [Environment Setup](https://jules.google/docs/environment/)
