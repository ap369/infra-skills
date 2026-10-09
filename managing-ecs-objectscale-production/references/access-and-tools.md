# Access: management API, S3 CLI, credentials

There is no MCP server for ECS / ObjectScale, from Dell or the community. Claude reads through its shell tool.

## Read path
- **Management API:** a dedicated **System Monitor** (read-only) management user. Store its password in a file only the operator can read (mode 600) or a vault. Get a token once per session and keep it in a shell variable, never printed:
  ```bash
  TOKEN=$(curl -sk -u "$ECS_RO_USER:$(cat ~/.ecs/ro.pass)" -D - -o /dev/null https://$ECS:4443/login | awk -F': ' 'tolower($1)=="x-sds-auth-token"{print $2}' | tr -d '\r')
  curl -sk -H "X-SDS-AUTH-TOKEN: $TOKEN" -H 'Accept: application/json' https://$ECS:4443/dashboard/zones/localzone
  ```
  Call `GET /logout` with the token at the end of the session. Prefer a trusted CA bundle over `-k`.
- **S3:** an object user (or IAM role on ECS 3.6+) that can only read bucket configuration. Set up a dedicated `aws` profile (`--profile ecs-ro`). Never use the bucket-owner credentials of a production app for operator reads.
- Read verbs Claude may run without a plan:
  - management API `GET` (except anything that returns secrets)
  - `s3api get-*`
  - `s3api list-*` with `--max-items`

## Write path
Changes run from the approved change plan, one call per step with a read after each, under a **System Admin / Namespace Admin** identity that the human enables for the change window. Never reuse the System Admin token for reads "because it's already there".

## Secrets hygiene
- Never print tokens, passwords or S3 secret keys into the transcript. Responses from `/object/user-secret-keys` contain secrets: pipe them through `jq` to keep metadata only, or let the human run them.
- New secret keys go straight to a vault or to the requester over a secure channel.
