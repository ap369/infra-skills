# Prometheus and Alertmanager reference

> **Command verification status:** `promtool` forms are checked against promtool-command-catalog.md (Prometheus 3.15.1 docs); HTTP API paths against the Prometheus 3.15.1 docs (`docs/querying/api.md`, `docs/management_api.md`); `amtool` forms against the Alertmanager 0.34.1 README and CLI source (`cli/*.go`). Those are `[doc]`. Exporter- or Grafana-specific endpoints are `[unverified]` here.

## Reads (T0)
| Endpoint (GET, also POST for queries) | Purpose |
|---|---|
| `/api/v1/query?query=<promql>` / `/api/v1/query_range` | instant / range queries |
| `/api/v1/alerts`, `/api/v1/rules` | firing alerts, rule state and evaluation errors |
| `/api/v1/targets` | scrape target health (`up`, last error) |
| `/api/v1/status/config`, `/api/v1/status/flags`, `/api/v1/status/buildinfo`, `/api/v1/status/runtimeinfo`, `/api/v1/status/tsdb` | config, flags, version, runtime, TSDB cardinality stats |
| `/api/v1/series`, `/api/v1/labels`, `/api/v1/label/<name>/values` | series and label discovery (bounded with `match[]` and time range) |
| `/-/healthy`, `/-/ready` | management health |

`amtool` reads: `amtool alert query <matchers>`, `amtool silence query [<matchers>]`, `amtool config routes [test ...]` `[doc]`.

## Validate before any change
```
promtool check config <prometheus.yml>        [doc]
promtool check rules <rules.yml>              [doc]
promtool test rules <test.yml>                [doc]   (unit tests for alert rules)
amtool config routes test --config.file=<alertmanager.yml> --verify.receivers=<receiver> <labels>   [doc]
```

## Changes by tier
| Tier | Operation | Form | Rollback |
|---|---|---|---|
| T1 | New alert / recording rule | rule file in Git, `promtool check rules`, deploy | revert |
| T2 | Reload config | `POST /-/reload` (**only if `--web.enable-lifecycle` is set**; "disabled by default"), or the service manager's reload | previous config + reload |
| T2 | Silence an alert | `amtool --alertmanager.url=<url> silence add <exact matchers> --duration=<short> --comment="<ticket>" --author=<name>` (flags from amtool source `cli/silence_add.go`, v0.34.1: `--duration` defaults to 1h, a comment is required by default) | `amtool silence expire <id>` |
| T2 | Change thresholds / `for` / routing | Git change + `promtool`/`amtool` validation | revert |
| T3 | Delete series | `POST /api/v1/admin/tsdb/delete_series` (admin API, "not enabled unless the `--web.enable-admin-api` is set"); then `clean_tombstones`. Irreversible. | **none** (snapshot first: `POST /api/v1/admin/tsdb/snapshot`) |
| T3 | Shut down Prometheus | `POST /-/quit` ("graceful shutdown", lifecycle API) | restart the service |

- **Silence matchers:** `amtool silence add alertname=Test_Alert instance=~".+0"` shows matchers can be regexes: a broad regex silences far more than intended. Use exact matchers in production and show `amtool silence query` with the same matchers first.
- `amtool silence expire $(amtool silence query -q)` (README example) expires **every** silence: never in production.

## Rule hygiene
- Every alert: `for` duration, severity label, runbook/summary annotation, owner.
- Alert on symptoms users feel (errors, latency, saturation) plus capacity runways (disk, PVC, array capacity from the storage skills).
- Watch cardinality (`/api/v1/status/tsdb`): high-cardinality labels (IDs, URLs) explode memory.
