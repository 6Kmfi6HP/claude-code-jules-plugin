---
description: Create a new Jules coding session to delegate a task
argument-hint: <owner/repo> "<task prompt>" [--title "title"]
---

# Jules Create Session

Delegate a coding task to Google Jules.

## Instructions

1. Parse `$ARGUMENTS` for:
   - **repo**: `owner/repo` format (required)
   - **prompt**: the task description in quotes (required)
   - **title**: optional `--title "..."` flag

2. Locate the Jules CLI script at `scripts/jules_cli.py` relative to this plugin's root directory (the directory containing `.claude-plugin/plugin.json`). Use the absolute resolved path.

3. Run the Jules CLI:
   ```bash
   python3 /path/to/jules-api/scripts/jules_cli.py sessions create \
     --source "sources/github/OWNER/REPO" \
     --prompt "TASK_PROMPT" \
     --title "TITLE_OR_AUTO" \
     --automation-mode AUTO_CREATE_PR
   ```

4. On success, display:
   - Session ID
   - Title
   - State
   - Link to jules.google.com session

5. Remind the user that Jules will auto-create a PR when done (no plan approval needed).

## Requirements

- `JULES_API_KEY` environment variable must be set
- The GitHub repo must be connected at jules.google.com
