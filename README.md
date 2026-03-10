# Claude Code Jules Plugin

A [Claude Code plugin marketplace](https://code.claude.com/docs/en/plugin-marketplaces) for managing [Google Jules](https://jules.google.com) — an autonomous AI coding agent.

## Quick Start

```bash
# In Claude Code, add this marketplace
/plugin marketplace add 6Kmfi6HP/claude-code-jules-plugin

# Install the plugin
/plugin install jules-api@jules-plugin-marketplace

# Set your API key
export JULES_API_KEY="your-key"

# Use commands
/jules-api:jules-list
/jules-api:jules-create owner/repo "fix the login bug"
/jules-api:jules-status <session-id>
/jules-api:jules-send <session-id> "add tests please"
```

## What's Included

| Component | Description |
|-----------|-------------|
| **Plugin** (`jules-api`) | Commands, skill, and Python CLI for Jules API |
| **4 Commands** | List, create, status, send |
| **Skill** | Ambient guidance for Jules-related work |
| **Python CLI** | Standalone `jules_cli.py` (no deps, Python 3.8+) |
| **API Reference** | Endpoint docs and activity type reference |

## Setup

1. Get a Jules API key from [jules.google.com](https://jules.google.com)
2. Set `JULES_API_KEY` environment variable
3. Ensure your GitHub repos are connected in the Jules dashboard

## Plugins

- [`jules-api`](plugins/jules-api/) — Full Jules API integration

## License

MIT
