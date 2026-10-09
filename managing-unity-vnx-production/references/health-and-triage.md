# Health check and incident triage

## Health check (T0)
Report each item as a row: **Check | Value | Status (OK/WARN/CRIT) | Source + timestamp**.

| # | Check | Unity source | VNX source | WARN | CRIT |
|---|---|---|---|---|---|
| 1 | Alerts / faults | `/event/alert/hist show`, MCP alert | `faults -list`, `nas_checkup` | warnings | errors / critical |
| 2 | SPs | `/env/sp show` | `getagent` both SPs, `getcrus` | degraded component | SP down / service mode |
| 3 | Pool used | `/stor/config/pool show -detail` | `storagepool -list -prcntFull` | ≥ 80% | ≥ 90% |
| 4 | Snapshot space and auto-delete | pool `-detail` | snapshot reserve | auto-delete off near full | n/a |
| 5 | LUN ownership | n/a (Unity balances) | `lun -list -owner -default` | LUNs not on their default SP | n/a |
| 6 | Host paths | `/remote/initiator show` (logged-in state) | `port -list -hba` | missing paths | host with 0 paths |
| 7 | Replication | `/prot/rep/session show -detail` | `mirror -async -list`, `nas_replicate -list` | lag > 2× RPO | session failed / fractured |
| 8 | Drives | `/env/disk show` | `getcrus`, faults | 1 failed | multiple / no hot spare |
| 9 | File side | NAS servers, FS used | Data Mover status, `server_df` | FS ≥ 85% | Data Mover failed over |
| 10 | Software / support | `/sys/soft/ver show` | `ndu -list`, support status | not on the target OE | VNX: no support contract |

Thresholds are defaults. If the user or a site runbook gives different values, use those. End with **Findings**, ordered by severity, each with one recommended next step and its tier.

## Triage playbooks
Order for every incident: scope → read → hypothesis with evidence → smallest reversible fix (gated, emergency path) → verify → timeline notes.

- **Pool full (Unity):** follow "Pool full: relief ranked by safety" in unity.md. Show the user the snapshot list, compactly. Approval covers the listed IDs only.
- **SP reboot / LUNs trespassed (VNX):**
  1. Root cause first: `getlog` on both SPs, `faults -list`, `getcrus`. Confirm the SP is back and on the same revision as its peer.
  2. Run `spcollect` (T1, tell the user) to preserve the evidence.
  3. Verify host paths to the recovered SP (`port -list -hba`, and multipath on the hosts).
  4. Only then trespass back (T2).

  An NDU/patch is a separate T3 change. It is not an incident fix unless the root cause says so.
- **Host lost a LUN:** host access or storage group membership (did the LUN or host get removed?), initiator logins, recent changes (audit log / Unisphere logs). If initiators aren't logged in, it's on the fabric or host side.
- **Replication broken:** session state and the last sync time, then the interfaces and network. Resync or re-create is T3 if it can overwrite data.
- **File: clients lost a share:** NAS server / Data Mover state, interfaces, export or share config, recent failover. A Data Mover failback is T3.
