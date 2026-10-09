# Access: Manager REST API, S3 CLI, credentials

There is no MCP server for on-prem IBM COS / Cleversafe dsNet. The community and CData servers target **IBM Cloud** COS and don't speak to a dsNet Manager. Claude reads through its shell.

## Read path
- **Manager REST API:** a dedicated Manager account with the **Read Only** role (or Operator, if the site's monitoring needs it). Keep the password in a mode-600 file or a vault, and use it without printing it:
  ```bash
  MGR_AUTH="$COS_RO_USER:$(cat ~/.cos/ro.pass)"      # never echo
  curl -s --cacert ~/.cos/ca.pem -u "$MGR_AUTH" "https://$MANAGER/manager/api/json/1.0/viewSystem.adm" | jq '<filter>'
  ```
  Filter large responses (`viewSystem`) with `jq` down to the devices, sets and vaults involved.
- **S3:** a config-only access key on a read-only Manager user, with an `aws` profile `cos-ro` pointing at the Accesser / load balancer endpoint. Never use a production app's access key for operator reads.
- Read operations Claude may run without a plan:
  - Manager `view*` / `list*` operations
  - `s3api get-*` / `head-*`
  - `s3api list-*` with `--max-items`

  Everything else is a change.

## Write path
Changes run from the approved change plan, one call per step with a read after each (device state, vault health), under a **System Admin** (or Security Officer, for retention) identity that the human enables for the change window. **Never use the Super User account for reads**, even if it's already saved.

## Secrets hygiene
- Never print Manager passwords, session cookies or S3 secret access keys into the transcript.
- New access keys go straight to a vault or to the requester over a secure channel.
