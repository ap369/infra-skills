# infra-skills

[![License: MIT](https://img.shields.io/github/license/ap369/infra-skills)](LICENSE)
[![Claude Code Skills](https://img.shields.io/badge/Claude_Code-skills-D97757)](https://docs.claude.com/en/docs/claude-code/skills)
[![Skills](https://img.shields.io/badge/skills-1-blue)](#infra-skills)

Agent skills (Claude Code, OpenCode) for operating infrastructure in production.

| Skill | Scope |
|---|---|
| `managing-purestorage-production` | Pure Storage FlashArray, FlashBlade, Pure1 and Pure Fusion. Read-only by default (via the Pure Fusion MCP server); every change goes through a gated, approved change plan. |

## Install

```
git clone https://github.com/ap369/infra-skills.git ~/infra-skills
```

### Claude Code

Symlink each skill into your personal skills directory:

```
mkdir -p ~/.claude/skills
ln -s ~/infra-skills/managing-purestorage-production ~/.claude/skills/managing-purestorage-production
```

### OpenCode

OpenCode reads skills from `~/.config/opencode/skills/` (global) or `.opencode/skills/` (per project). It also reads `~/.claude/skills/`, so if you already did the Claude Code install, you're done.

```
mkdir -p ~/.config/opencode/skills
ln -s ~/infra-skills/managing-purestorage-production ~/.config/opencode/skills/managing-purestorage-production
```

Optional: control skill access in `opencode.json`:

```json
{
  "permission": {
    "skill": { "managing-purestorage-production": "allow" }
  }
}
```

## Prerequisite: Pure Fusion MCP server

1. Get the server binary from github.com/purestorage-openconnect. Run its config command with **read-only** API tokens from each array.
2. Register it with your agent:
   - **Claude Code:** `claude mcp add pure-fusion -- <path-to-binary> --config <config-file>`
   - **OpenCode:** add it to `opencode.json`:
     ```json
     {
       "mcp": {
         "pure-fusion": {
           "type": "local",
           "command": ["<path-to-binary>", "--config", "<config-file>"],
           "enabled": true
         }
       }
     }
     ```

See `managing-purestorage-production/references/fusion-and-pure1.md` for details.
