# Health check (read-only, T0)

Run in this order and report each item as a table row: **Check | Value | Status (OK/WARN/CRIT) | Source + timestamp**.

| # | Check | FlashArray source | WARN | CRIT |
|---|---|---|---|---|
| 1 | Open alerts | `puremessage list --open` / `/alerts` | any warning | any critical |
| 2 | Capacity used | `purearray list --space` | ≥ 80% | ≥ 90% |
| 3 | Capacity runway | Pure1 forecast | < 90 days | < 30 days |
| 4 | Data reduction | `--space` (DRR) | drop > 20% vs. last check | n/a |
| 5 | Latency (read/write) | `purearray monitor` | > 1 ms sustained | > 3 ms sustained |
| 6 | Queue depth / IOPS anomaly | `/arrays/performance` history | 2× baseline | n/a |
| 7 | Hardware | `purehw list`, `puredrive list` | any non-`ok` | controller or multiple drives |
| 8 | Host paths | `pureport list --initiator` vs. host initiators | host with < all paths | host with 0 paths |
| 9 | Replication connections | `purearray list --connect` | n/a | not `connected` |
| 10 | pgroup replication lag | last replicated snapshot age | > 2× frequency | > 4× frequency |
| 11 | Pods (ActiveCluster) | `purepod list --array`, mediator | `resyncing` | `offline` or mediator unreachable |
| 12 | Destroyed, pending | `purevol list --pending` | anything nearing eradication that nobody expects | n/a |
| 13 | SafeMode | eradication config | disabled on a critical array | n/a |
| 14 | Purity version | `purearray list` | not on a supported or recommended release | EOL |

FlashBlade: replace the sources with `/arrays/space`, `/arrays/performance`, `/blades`, `/file-system-replica-links`, `/bucket-replica-links`. For row 8, check NFS and SMB clients per data VIP.

Thresholds are defaults. If the user or a site runbook gives different values, use those.

Output ends with a **Findings** list ordered by severity. Each finding names one recommended next step and its tier. Recommendations are not actions: anything above T0 goes through change-gate.md.
