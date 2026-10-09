# infra-skills

[![License: MIT](https://img.shields.io/github/license/ap369/infra-skills)](LICENSE)

Claude Code skills for operating infrastructure in production.

| Skill | Scope |
|---|---|
| `managing-purestorage-production` | Pure Storage FlashArray, FlashBlade, Pure1 and Pure Fusion. Read-only by default (via the Pure Fusion MCP server); every change goes through a gated, approved change plan. |

## Install

Symlink each skill into your personal skills directory:

```
ln -s ~/Documents/infra-skills/managing-purestorage-production ~/.claude/skills/managing-purestorage-production
```

## Prerequisite: Pure Fusion MCP server

1. Get the server binary from github.com/purestorage-openconnect. Run its config command with **read-only** API tokens from each array.
2. Register it: `claude mcp add pure-fusion -- <path-to-binary> --config <config-file>`.

See `managing-purestorage-production/references/fusion-and-pure1.md` for details.
