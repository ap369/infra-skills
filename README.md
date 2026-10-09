# infra-skills

[![License: MIT](https://img.shields.io/github/license/ap369/infra-skills)](LICENSE)
[![Claude Code Skills](https://img.shields.io/badge/Claude_Code-skills-D97757)](https://docs.claude.com/en/docs/claude-code/skills)
[![OpenCode Skills](https://img.shields.io/badge/OpenCode-skills-211E1E)](https://opencode.ai/docs/skills/)
[![Skills](https://img.shields.io/badge/skills-1-blue)](#infra-skills)

Agent skills (Claude Code, OpenCode) for operating infrastructure in production.

| Skill | Scope |
|---|---|
| `managing-purestorage-production` | Pure Storage FlashArray, FlashBlade, Pure1 and Pure Fusion. Read-only by default (via the Pure Fusion MCP server); every change goes through a gated, approved change plan. |
| `managing-netapp-production` | NetApp ONTAP (AFF/FAS/ASA), StorageGRID, BlueXP. Uses NetApp's ONTAP MCP server (`--read-only` recommended); every change, including MCP write tools, goes through a gated, approved change plan. |

## Install

```
git clone https://github.com/ap369/infra-skills.git ~/infra-skills
```

### Claude Code

Symlink each skill into your personal skills directory:

```
mkdir -p ~/.claude/skills
ln -s ~/infra-skills/managing-purestorage-production ~/.claude/skills/managing-purestorage-production
ln -s ~/infra-skills/managing-netapp-production ~/.claude/skills/managing-netapp-production
```

### OpenCode

OpenCode reads skills from `~/.config/opencode/skills/` (global) or `.opencode/skills/` (per project). It also reads `~/.claude/skills/`, so if you already did the Claude Code install, you're done.

```
mkdir -p ~/.config/opencode/skills
ln -s ~/infra-skills/managing-purestorage-production ~/.config/opencode/skills/managing-purestorage-production
ln -s ~/infra-skills/managing-netapp-production ~/.config/opencode/skills/managing-netapp-production
```

Optional: control skill access in `opencode.json`:

```json
{
  "permission": {
    "skill": { "managing-*-production": "allow" }
  }
}
```

## Prerequisites: MCP servers

### Pure Fusion MCP server (Pure Storage skill)

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

### ONTAP MCP server (NetApp skill)

1. Write `ontap.yaml` with your clusters under `Pollers:` (see [NetApp/ontap-mcp](https://github.com/NetApp/ontap-mcp)). Use an ONTAP user with a **read-only** role.
2. Start the server in read-only mode, bound to localhost:
   ```
   docker run -d --name ontap-mcp-ro -p 127.0.0.1:8083:8083 \
     -v ~/.config/ontap-mcp/ontap.yaml:/opt/mcp/ontap.yaml:ro \
     ghcr.io/netapp/ontap-mcp:latest start --port 8083 --host 0.0.0.0 --read-only
   ```
3. Register it with your agent:
   - **Claude Code:** `claude mcp add --transport http ontap-mcp http://127.0.0.1:8083`
   - **OpenCode:** add it to `opencode.json`:
     ```json
     {
       "mcp": {
         "ontap-mcp": { "type": "remote", "url": "http://127.0.0.1:8083", "enabled": true }
       }
     }
     ```

See `managing-netapp-production/references/ontap-mcp-and-bluexp.md` for details.
