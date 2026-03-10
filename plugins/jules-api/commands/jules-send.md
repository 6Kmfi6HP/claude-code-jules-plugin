---
description: Send a message to an active Jules session
argument-hint: <session-id> "<message>"
---

# Jules Send Message

Send a follow-up message to an active Jules coding session (e.g., to answer a question or provide guidance).

## Instructions

1. Parse `$ARGUMENTS` for:
   - **session-id**: the Jules session ID
   - **message**: the text to send (in quotes)

2. Locate the Jules CLI script at `scripts/jules_cli.py` relative to this plugin's root directory (the directory containing `.claude-plugin/plugin.json`). Use the absolute resolved path.

3. Run:
   ```bash
   python3 /path/to/jules-api/scripts/jules_cli.py sessions send SESSION_ID --prompt "MESSAGE"
   ```

4. Note: `sendMessage` returns an empty response. The agent's reply will appear as the next activity.

5. After sending, automatically fetch the latest status:
   ```bash
   python3 /path/to/jules-api/scripts/jules_cli.py activities last-message SESSION_ID
   ```

6. Confirm the message was sent and show the current session state.

## Requirements

- `JULES_API_KEY` environment variable must be set
- Session must be in an active state (not COMPLETED or FAILED)
