# Dynatrace reference: API v2 and Monaco

> **Command verification status:** API facts are from docs.dynatrace.com reference pages (*Authentication*, *Problems API v2 – GET problems list*, *Metrics API – GET metric data points*, *Settings API – GET schemas / GET objects / POST an object / DELETE an object*), retrieved 2026-10-25; `monaco` forms from monaco-command-catalog.md (dynatrace-configuration-as-code 2.31.0 source). Those are `[doc]`. Other endpoints, settings schema IDs and DQL/Grail queries are `[unverified]` until checked in the docs for your environment (SaaS vs. Managed).

## Authentication
- Header `Authorization`: **platform tokens** use the `Bearer` realm; **classic access tokens** use the `Api-Token` realm (`Authorization: Api-Token <token>`).
- Access is "fine-grained": each request lists the scopes it needs. Give monitoring/reporting tokens **read scopes only**: `problems.read`, `metrics.read`, `settings.read` (or the platform-token/OAuth equivalents such as `settings:objects:read`).
- Write scopes (`settings.write` / `settings:objects:write`) only for approved automation, stored in a vault, short-lived where possible. Never print a token; Dynatrace tokens have a recognisable prefix (`dt0c01.`), so redact them in output.
- Base URL: SaaS `https://{your-environment-id}.live.dynatrace.com/api/v2/...`, or through an Environment/Cluster ActiveGate `https://{activegate}:9999/e/{environment-id}/api/v2/...`.

## Reads (T0)
| Endpoint | Scope | Notes |
|---|---|---|
| `GET /api/v2/problems` | `problems.read` | `problemSelector`, `from`; `pageSize` default 50, max 500 |
| `GET /api/v2/metrics/query` | `metrics.read` | `metricSelector`, `entitySelector`, `from`/`to`, `resolution` |
| `GET /api/v2/settings/schemas` | `settings.read` | find the schema ID for what you want to change |
| `GET /api/v2/settings/objects` | `settings.read` | `schemaIds` or `scopes` required for the first page; `pageSize` default 100, max 500 |

**Paging (problems, settings objects):** follow `nextPageKey`; when `nextPageKey` is set, **omit the other query parameters** (problems keeps only the optional `fields`). The metrics query doesn't page: its `nextPageKey` is deprecated and always null.

## Changes by tier
| Tier | Operation | Form | Rollback |
|---|---|---|---|
| T0 | Validate a settings change | `POST /api/v2/settings/objects?validateOnly=true` ("runs only validation … without saving") | n/a |
| T2 | Create/update settings (alerting profiles, maintenance windows, anomaly detection…) | `POST /api/v2/settings/objects` with `settings.write`, after `validateOnly` | export the object first (`GET`), re-apply it |
| T3 | Delete a settings object | `DELETE /api/v2/settings/objects/{objectId}`: "Deletion cannot be undone!" | re-create from the export |
| T2 | Deploy configuration as code | `monaco deploy --dry-run` first, then `monaco deploy` (flags `--environment`, `--group`, `--project`) | redeploy the previous Git revision |
| T3 | Delete configs with Monaco | `monaco delete` (uses a delete file: `--file`) | redeploy |
| T3 | **`monaco purge`** | "Delete ALL configurations from the environments defined in the manifest". Never against production. | full redeploy from Git (if everything is in Git) |
| T3 | Revoke/rotate tokens | token management API (`apiTokens.*` scopes) | issue a new token |

**Maintenance windows** suppress problem alerting/detection for the matched entities: scope them to the entities the change touches and a fixed time window, never the whole environment. Find the maintenance-window schema with `GET /api/v2/settings/schemas` (its schema ID is `[unverified]` here).
