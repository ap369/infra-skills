# Observability health checks and incident triage

> **Command verification status:** endpoints and CLI forms are `[doc]` per prometheus.md, icinga.md, dynatrace.md and the catalogs.

## Health check (T0)
| # | Check | Read | Warning | Critical |
|---|---|---|---|---|
| 1 | Prometheus targets | `GET /api/v1/targets` | some targets down | a whole job down |
| 2 | Rule evaluation | `GET /api/v1/rules` (health, lastError) | slow groups | evaluation errors |
| 3 | Alert pipeline | watchdog alert received end to end | delayed | missing |
| 4 | Active silences | `amtool silence query` | without comment/expiry | broad regex / long silences |
| 5 | Icinga | `GET /v1/status`; `icinga2 daemon -C` on the config | UNKNOWN storms | API or config sync down |
| 6 | Downtimes / acks | `GET /v1/objects/downtimes`, `/v1/objects/comments` | open-ended | covering production during an incident |
| 7 | Dynatrace | `GET /api/v2/problems` (open problems) | many open | critical problems without owner |

## Playbooks
### "We got no alert"
1. Was the condition visible in metrics/checks? Query it for the incident window.
2. Did the rule fire (`/api/v1/alerts`, rule state history)? Was it silenced (`amtool silence query`) or downtimed / in a maintenance window?
3. Did Alertmanager route it (`amtool config routes test ...`) and did the receiver work?
4. Fix the gap as a change: rule, route or receiver, validated before deploy.

### Alert storm / noise
Read what fires and why (one root cause behind many alerts?). Use inhibition/grouping or dependency rules rather than silencing everything. Any silence is narrow, short and documented (T2).

### Prometheus out of memory / slow
Cardinality (`/api/v1/status/tsdb`), heavy queries/dashboards, retention. Reduce label cardinality at the source; don't `delete_series` (T3, irreversible) to fix load.

### Icinga config reload failed
`icinga2 daemon -C` output points at the file/line. The running daemon keeps the last valid config: fix and validate, then reload.

### Monitoring during a storage or platform change
Silence/downtime only the objects the change touches, for the window, with the change ticket in the comment. Remove the silence/downtime as the last plan step and confirm alerts flow again.
