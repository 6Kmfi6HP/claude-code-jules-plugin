---
description: List Jules coding sessions with status summary
argument-hint: [--page-size N] [--all-pages]
---

# Jules List Sessions

List all Jules coding sessions and show their current status.

## Instructions

1. Locate the Jules CLI script at `scripts/jules_cli.py` relative to this plugin's root directory (the directory containing `.claude-plugin/plugin.json`). Use the absolute resolved path.

2. Run the Jules CLI to list sessions:
   ```bash
   python3 /path/to/jules-api/scripts/jules_cli.py sessions list --page-size 20
   ```

3. Parse the JSON output and present a clean summary table with columns:
   - **ID** (short form)
   - **Title**
   - **State** (with emoji: ✅ COMPLETED, 🔄 IN_PROGRESS, ⏳ QUEUED, ❓ AWAITING_USER_FEEDBACK, ❌ FAILED, ⏸️ PAUSED)
   - **Created** (relative time)

4. If `$ARGUMENTS` contains `--all-pages`, add `--all-pages` to fetch all sessions.

5. Highlight any sessions in `AWAITING_USER_FEEDBACK` state — these need attention.

## Requirements

- `JULES_API_KEY` environment variable must be set
- Python 3.8+ available
