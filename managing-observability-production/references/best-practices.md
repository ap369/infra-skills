# Best practices: configuration audit (observability)

> **Command verification status:** reads use forms and endpoints from prometheus.md, icinga.md, dynatrace.md and the catalogs (`[doc]`). Practices come from the Prometheus, Alertmanager, Icinga 2 and Dynatrace documentation cited there, plus common SRE standards; site standards override them.

Every check is read-only (T0). Report: **# | Practice | Current value | Status (OK / GAP / N/A) | Risk | Fix (tier)**, then a prioritized summary.

## Coverage and alert quality
| # | Practice | Why | Check | Fix tier |
|---|---|---|---|---|
| O1 | Every production service has symptom alerts (errors, latency, availability) and capacity alerts (disk, PVC, array pools, buckets) | Missed incidents | rules / checks inventory | T1 |
| O2 | Every alert has severity, owner, runbook link and a `for`/check-attempt delay | Actionable paging | rule annotations, Icinga vars | T2 |
| O3 | Alert rules unit-tested (`promtool test rules`) and validated in CI (`promtool check rules`, `icinga2 daemon -C`) | Broken rules fail silently | CI pipeline | T2 |
| O4 | **Dead-man's switch**: an always-firing watchdog alert proves the alert pipeline works end to end | Silent monitoring outage | Alertmanager routes / external heartbeat | T1 |
| O5 | Scrape targets / checks for every node and storage system are up | Blind spots | `/api/v1/targets`, Icinga UNKNOWNs | T2 |

## Silences, downtimes, maintenance windows
| # | Practice | Why | Check | Fix tier |
|---|---|---|---|---|
| O6 | No silences/downtimes without author, comment (ticket) and end time; none longer than the change window | Hidden incidents | `amtool silence query`, `/v1/objects/downtimes`, Dynatrace maintenance windows | T2 |
| O7 | No broad regex silences or hostgroup-wide downtimes left active | Hidden incidents | same | T2 |
| O8 | Acknowledgements have expiry | Forgotten problems | `/v1/objects/comments` acknowledgements with `acknowledgement_expiry==0` | T2 |

## Security
| # | Practice | Why | Check | Fix tier |
|---|---|---|---|---|
| O9 | Prometheus admin API and lifecycle API disabled unless needed, and protected when enabled | `delete_series`, `/-/quit` | `/api/v1/status/flags` | T2 |
| O10 | Icinga ApiUsers least privilege (no `[ "*" ]` for tools); TLS verified by clients | Takeover, token theft | api-users config | T2 |
| O11 | Dynatrace tokens scoped minimally, owned, rotated; no write scopes on dashboards/reporting tokens | Abuse | token management | T2 |
| O12 | Monitoring configuration in Git (rules, Icinga config/Director exports, Monaco projects) | Recovery, review | repos | T2 |

## Platform health
| # | Practice | Why | Check | Fix tier |
|---|---|---|---|---|
| O13 | Prometheus HA (pairs) or remote write, retention sized, cardinality watched | Data loss, OOM | `/api/v1/status/tsdb`, runtime info | T2 |
| O14 | Alertmanager clustered; notification channels tested | Missed pages | Alertmanager status | T2 |
| O15 | Icinga HA zones / satellites configured; config sync healthy | Monitoring outage | `/v1/status` | T3 |
| O16 | Versions supported (Prometheus, Alertmanager, Icinga 2, Monaco/ActiveGate) | Security | buildinfo, `icinga2 --version`, `monaco version` | T3 |
