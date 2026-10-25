# Icinga 2 reference: CLI and REST API

> **Command verification status:** CLI forms are checked against icinga2-command-catalog.md (Icinga 2 v2.16.5 docs, `doc/11-cli-commands.md`); API facts and endpoints against `doc/12-icinga2-api.md` of the same release. Those are `[doc]`. Icinga Web 2 / Icinga DB / Director commands are `[unverified]` here.

## CLI
- **Validate before every reload:** `icinga2 daemon -C` (alias of `--validate`) `[doc]` checks the configuration without starting. A config that fails validation won't load: reload only after it passes.
- Features: `icinga2 feature list` (T0), `icinga2 feature enable|disable <name>` (T2: e.g. disabling `notification` stops all notifications on that node; `api` turns the API off).
- `icinga2 object list` (T0), `icinga2 ca list` (pending CSRs, T0), `icinga2 ca sign <fingerprint>` (T2: admits a node to the cluster), `icinga2 pki ...`, `icinga2 node wizard|setup` (T2/T3: node identity).

## API basics (doc 12)
- HTTPS only, default port **5665** (shared with the cluster stack). Basic auth or client certificates against an `ApiUser` object.
- **Permissions** per ApiUser: least privilege, e.g. read-only object queries `permissions = [ "objects/query/Host", "objects/query/Service" ]`; avoid `[ "*" ]`.
- All requests except `GET` require `Accept: application/json`. URLs are prefixed with `/v1`. Responses contain a `results` list.
- `X-HTTP-Method-Override: GET` lets you send a POST body (complex filters) for a query.
- **Never `curl -k`** in production (the docs' examples use it for brevity): pass the CA with `--cacert`.

## Reads (T0)
| Endpoint | Purpose |
|---|---|
| `GET /v1/status` | instance and feature status |
| `GET /v1/objects/hosts`, `/v1/objects/services` (with `filter`, `attrs`) | object state |
| `GET /v1/objects/downtimes`, `/v1/objects/comments` | current downtimes / acknowledgement comments |
| `GET /v1/types`, `GET /v1/templates/hosts` | object types and templates |
| `GET /v1/config/packages`, `/v1/config/stages` | config packages deployed via the API |

## Actions and changes by tier (POST `/v1/actions/<action>`)
| Tier | Action | Notes |
|---|---|---|
| T2 | `schedule-downtime` | Takes a **filter** and can target many objects (the docs' example uses `match("*satellite*", host.name)` plus `all_services=true`). Run the same filter as a `GET /v1/objects/...` query first, show the matched objects, and set `author`, `comment`, `start_time`, `end_time`, `fixed`. |
| T2 | `remove-downtime` | remove only the named downtime(s) |
| T2 | `acknowledge-problem` / `remove-acknowledgement` | an ack suppresses re-notification: set an expiry where supported |
| T2 | `reschedule-check` | harmless for one object, load for thousands |
| T2/T3 | `process-check-result` | **injects a fake result** (e.g. OK): hides real failures; only for passive checks by design |
| T3 | `send-custom-notification`, `delay-notification` | changes who gets paged |
| T3 | `restart-process`, `shutdown-process` | restarts/stops Icinga on that node |
| T3 | `DELETE /v1/objects/<type>/<name>` with `cascade=1` | deletes the object **and** dependants (e.g. services on a host); API-created objects only |
| T3 | `/v1/console/execute-script` | arbitrary DSL execution: never in production plans |

Every action plan names the exact filter, the matched object list, and the reverse action (`remove-downtime`, `remove-acknowledgement`).
