# Jules API — Claude Code Plugin

A Claude Code plugin for managing [Google Jules](https://jules.google.com) autonomous coding sessions via the REST API.

## Features

- **Create sessions** — Delegate coding tasks to Jules with auto-PR creation
- **Monitor progress** — Track session state, plan steps, and changed files
- **Send messages** — Respond to Jules questions or provide guidance
- **Session lifecycle** — Pause, resume, cancel, or delete sessions
- **Activity summaries** — Compact JSON summaries for automation/monitoring

## Installation

### From Marketplace

```
/plugin marketplace add 6Kmfi6HP/claude-code-jules-plugin
/plugin install jules-api@jules-plugin-marketplace
```

### Setup

Set your Jules API key as an environment variable:

```bash
export JULES_API_KEY="your-api-key-here"
```

> Get your API key from [jules.google.com](https://jules.google.com) → Settings → API Keys

## Commands

| Command | Description |
|---------|-------------|
| `/jules-api:jules-list` | List all Jules sessions with status |
| `/jules-api:jules-create` | Create a new coding session |
| `/jules-api:jules-status` | Get detailed session summary |
| `/jules-api:jules-send` | Send a message to a session |

## Skill

The plugin includes a `jules-api` skill that provides ambient guidance when working with Jules-related files or tasks.

## Python CLI

The plugin ships with `scripts/jules_cli.py` — a standalone Python CLI for the Jules REST API:

```bash
# No dependencies beyond Python 3.8+ stdlib
python3 scripts/jules_cli.py sessions list --page-size 10
python3 scripts/jules_cli.py sessions create --source "sources/github/owner/repo" --prompt "fix the bug"
python3 scripts/jules_cli.py activities summary <session-id>
```

See [API Reference](references/api_endpoints.md) for full endpoint documentation.

## Security

⚠️ **Never commit your API key.** Use environment variables or a secrets manager.

## License

MIT
