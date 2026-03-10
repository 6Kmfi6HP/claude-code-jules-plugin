---
description: Get detailed status and summary of a Jules session
argument-hint: <session-id>
---

# Jules Session Status

Get a compact summary of a Jules coding session including state, progress, changed files, and PR link.

## Instructions

1. Extract the session ID from `$ARGUMENTS`.

2. Locate the Jules CLI script at `scripts/jules_cli.py` relative to this plugin's root directory (the directory containing `.claude-plugin/plugin.json`). Use the absolute resolved path.

3. Run the summary command:
   ```bash
   python3 /path/to/jules-api/scripts/jules_cli.py activities summary SESSION_ID
   ```

4. Present the summary clearly:
   - **State** with emoji indicator
   - **Title**
   - **PR URL** (if available, as clickable link)
   - **Last Agent Message** (truncated to key info)
   - **Plan Steps** (numbered list)
   - **Changed Files** (file list)
   - **Failure Reason** (if failed)

5. If the session is `AWAITING_USER_FEEDBACK`, show the last agent message prominently and suggest responding with `/jules-api:jules-send`.

## Requirements

- `JULES_API_KEY` environment variable must be set
