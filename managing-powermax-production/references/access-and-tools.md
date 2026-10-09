# Access: Solutions Enabler, Unisphere, credentials

There is no production-grade MCP server for PowerMax/VMAX yet. The only one public is github.com/jayanthsd/powermax_mcp: experimental, unlicensed, and it includes a mock server. Don't point it at production. Claude reads through **symcli on a management host** using its shell tool.

## Read path
- A management host (or the Unisphere/eManagement guest) with Solutions Enabler installed and connected to the arrays through gatekeepers or client/server mode (`SYMCLI_CONNECT`).
- **Use a read-only identity.** Run as an OS user mapped to a **Monitor** role in symauth / Unisphere user authorization. Then even a mistyped write command is refused by the array. Never run reads as an admin/StorageAdmin identity "because it's already configured".
- Set `SYMCLI_NOPROMPT` **unset** (prompts stay on). Never pass `-noprompt`, `-force` or `-symforce` in reads.
- Whitelist of read verbs Claude may run without a plan:
  - `list`, `show`, `query`, `verify`, `ping` (SRDF), `-h`
  - `symevent`, `symaudit list`, `symstat`
  - `symaccess backup` (writes a local file only)

  Everything else is a change.
- Unisphere REST with a read-only (Monitor) user is an alternative for scripted reads. Keep the credentials in an environment file or vault, never in chat.

## Write path
Changes run from the approved change plan, either by Claude (one command per step, read after each) or by a human pasting the commands. Use `symconfigure ... preview` before `commit`. Approved steps that need storage admin rights run under a separate identity that the human switches to for the change window.

## Credentials hygiene
- Never echo passwords, `symapi` lockbox contents or Unisphere tokens into the transcript.
- If a command would print secrets, don't run it. Ask the human.
