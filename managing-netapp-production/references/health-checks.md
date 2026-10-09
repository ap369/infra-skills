# Health check (read-only, T0)

Report each item as a table row: **Check | Value | Status (OK/WARN/CRIT) | Source + timestamp**.

| # | Check | ONTAP source | WARN | CRIT |
|---|---|---|---|---|
| 1 | Cluster / node health | `system health status show`, `cluster show` | any degraded subsystem | node unhealthy / not eligible |
| 2 | Open alerts and EMS | `system health alert show`, `event log show -severity <=ERROR` | warnings | errors / emergencies |
| 3 | HA | `storage failover show` | takeover not possible | node in takeover |
| 4 | Aggregate used | `storage aggregate show -fields percent-used` | ≥ 85% | ≥ 95% |
| 5 | Volume used | `volume show -fields percent-used,autosize-mode` | ≥ 85% without autosize | ≥ 95%, or any LUN offline |
| 6 | Snapshot reserve overflow | `volume show-space` | snapshots spilling into the data area | n/a |
| 7 | Latency | `qos statistics volume latency show` / Harvest | > 2 ms sustained (AFF) | > 10 ms sustained |
| 8 | LIFs off home port | `network interface show -is-home false` | any | data LIF down |
| 9 | SnapMirror health and lag | `snapmirror show -fields healthy,lag-time,state` | lag > 2× schedule | unhealthy, broken-off unexpectedly |
| 10 | Snapshot policy coverage | volumes with snapshot policy `none` holding data | any critical volume | n/a |
| 11 | Ransomware protection | `security anti-ransomware volume show` | ARP off on critical NAS volumes | an active ARP attack alert |
| 12 | Recovery queue | `volume recovery-queue show` *(adv)* | volumes nobody expects | n/a |
| 13 | Hardware | `system node environment sensors show -state !normal`, `storage disk show -broken`, spares | broken disk / low spares | multiple failures |
| 14 | ONTAP version / advisories | `version`, Digital Advisor | not on the recommended release | EOL / critical advisory |

StorageGRID: `/grid/health`, `/grid/alerts`, `/grid/node-health`, storage used per site, ILM backlog (`/grid/metric-query`), CloudMirror errors.

Thresholds are defaults. If the user or a site runbook gives different values, use those.

End with **Findings**, ordered by severity, each with one recommended next step and its tier. Recommendations are not actions: anything above T0 goes through change-gate.md.
