# Health check and incident triage

## Health check (T0)
Report each item as a row: **Check | Value | Status (OK/WARN/CRIT) | Source + timestamp**.

| # | Check | Source | WARN | CRIT |
|---|---|---|---|---|
| 1 | Events / alerts | `symevent list -start <24h>`, Unisphere alerts | warnings | errors, fatal |
| 2 | SRP capacity | `symcfg list -srp -detail` | ≥ 80% used | ≥ 90% used |
| 3 | Subscription | same | > 150% (site policy) | n/a |
| 4 | Directors / ports | `symcfg list -dir all -v` | port offline | director offline |
| 5 | Drives / spares | `symdisk list -failed` | 1 failed | multiple, or no spare |
| 6 | SRDF state and consistency | `symrdf -sid S list`, `query -rdfa` | Suspended / SyncInProg | Partitioned, R2 not consistent for > RPO |
| 7 | SRDF/A cycle time / DSE | `query -rdfa` | cycle > 2× target | DSE spilling, session dropping |
| 8 | SnapVX space / expiring secure snaps | `symsnapvx list -detail` | growing deltas | snapshots blocking SRP |
| 9 | Host logins per MV | `symaccess list logins` | host with fewer paths than its port group | 0 paths |
| 10 | Response time per SG | Unisphere performance / `symstat` | > 1 ms sustained (flash) | > 5 ms sustained |
| 11 | Code level | `symcfg list -v` | not on the target code | unsupported |

Thresholds are defaults. If the user or a site runbook gives different values, use those. End with **Findings**, ordered by severity, each with one recommended next step and its tier.

## Triage playbooks
Order for every incident: scope → read → hypothesis with evidence → smallest reversible fix (gated, emergency path) → verify → timeline notes.

- **Host lost devices:**
  1. `symaccess show view` for its MV: is the device still in the SG? Is the IG intact?
  2. `list logins`: are the host's WWNs logged in?
  3. `symaudit`: what changed recently?
  4. If the WWNs aren't logged in, it's a fabric or host problem. Hand it over with the evidence.
  5. To restore access, re-add to the SG or recreate the MV from the `symaccess backup` file (T2 when reversing an accidental change).
- **SRDF suspended / dropped:** follow "SRDF/A suspended after a link outage" in powermax-vmax.md. Gold copy on R2 first, then an incremental resume. Never `-full` by reflex.
- **SRP nearly full:**
  1. Find the top SGs and the snapshot deltas.
  2. Expire snapshots by name (T3).
  3. Data-reduction review.
  4. Capacity add (Dell).

  Never deallocate devices to make room without the decommission pattern.
- **Latency:** compare per-SG response time, FE vs. BE, and host I/O limits hit. Check SRDF/S distance and link latency, and whether a SnapVX link-copy or SRDF resync is running. The remediation (host I/O limit, scheduling) is T2. Never disable directors.
- **DR (failover / swap / Metro witness issues):** use the site DR runbook only. Claude prepares the checklist and reads the state.
