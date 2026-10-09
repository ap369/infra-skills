# Access: Unity MCP, uemcli, naviseccli

## Unity: community MCP server (sachdev27/dell-unity-mcp-server)
- A community project (MIT, low adoption), not Dell-supported. It auto-generates tools from the Unity OpenAPI spec.
- **GET-only by default** (`ALLOWED_HTTP_METHODS=GET`). Never set POST/PUT/DELETE for production. Changes go through the change plan and uemcli.
- **Credentials are passed on every tool call** (`host`, `username`, `password`). The password therefore lands in the agent transcript and logs. Mitigations, all required:
  1. Use a **dedicated Unity account with the Operator role** (read-only), used only for this purpose. A leaked password can't change anything.
  2. Rotate it regularly, and immediately if the transcript is shared.
  3. Never reuse an admin password or a password shared with other systems.
- Set `UNITY_TLS_VERIFY=true` (the default is false) and keep the CA bundle trusted.
- Bind it to localhost: `python -m unity_mcp.main` (stdio) is preferred over the HTTP mode on `0.0.0.0`.

Claude Code registration (stdio):
```
pip install dell-unity-mcp-server
claude mcp add unity -e ALLOWED_HTTP_METHODS=GET -e UNITY_TLS_VERIFY=true -- python -m unity_mcp.main
```

## Unity: uemcli
- Save credentials per array once, as the human: `uemcli -d <mgmt> -u <user> -p <pass> -saveUser`. Claude then runs commands without seeing the password.
- Save an **Operator** (read-only) account for the read path. Admin and storage-admin accounts are used only for an approved change, by the human or in a separate session.
- Read verbs Claude may run without a plan: `show`, `-help`.

## VNX: naviseccli and Control Station
- Block: create a security file as the human (`naviseccli -AddUserSecurity -scope 0 -user <ro_user>`), using a **read-only (monitor/operator) role** account for reads.
- Read verbs: `getagent`, `getcrus`, `getlog`, `faults -list`, `*-list`, `getlun`, `port -list`, `ndu -list`.
- File: SSH to the Control Station as a read-only user. `nas_*` and `server_*` commands with `-list`, `-info` or `-query` only.

## For all three
- If an approved change needs admin rights, the human switches to the admin identity for that window. Claude never holds or asks for an admin password.
- Never print secrets. Don't run commands that would.
