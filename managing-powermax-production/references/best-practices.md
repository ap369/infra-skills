# Best practices: configuration audit (PowerMax / VMAX)

Use this for a "best-practice audit" or "config review". Every check is read-only (T0) symcli or Unisphere REST, run as the Monitor identity. Each finding names the fix and its tier, and the fix goes through change-gate.md. Site standards override these defaults. Verify against Dell's PowerMax best-practice guides and host connectivity guides for your PowerMaxOS / HYPERMAX OS.

Report format: **# | Practice | Current value | Status (OK / GAP / N/A) | Risk | Fix (tier)**, then a prioritized summary.

## Protection and resilience

| # | Practice | Why | Check | Fix tier |
|---|---|---|---|---|
| P1 | **SnapVX snapshot schedules** (Unisphere snapshot policies) on every production SG, with retention per RPO | Fast restore | `symsnapvx -sid S list` per SG, Unisphere snapshot policies | T1/T2 |
| P2 | **Secure snapshots** (`-secure`), or SnapVX with a TTL, on critical SGs for ransomware protection. Capacity impact accepted. | Snapshots can't be terminated early | `symsnapvx list -detail` (secure flag) | T3 |
| P3 | **SRDF** for tier-1: SRDF/A in a **consistency group** (`symrdf enable`) so R2 is dependent-write consistent. SRDF/Metro with a **witness** (vWitness or array witness). | DR integrity | `symrdf -g DG query -rdfa`, consistency state, `symcfg list -rdfg all` | T2 |
| P4 | Gold-copy SnapVX on R2 scheduled or scripted before resyncs. DR tests with linked snapshots on R2. | Restartable DR image | R2-side snapshot list | T1 |
| P5 | SRDF/A **DSE** (delta set extension) pool configured, with cycle time within the RPO | Prevents drops on link hiccups | `query -rdfa` | T2 |
| P6 | Restore and DR tests at least quarterly, documented | Untested backups don't count | process | process |

## Provisioning design

| # | Practice | Why | Check | Fix tier |
|---|---|---|---|---|
| P7 | **One SG per application** (child SGs per tier/DB component under a parent SG for masking), with consistent naming `<app>_<env>_SG` | Snapshots, SRDF and SL per app | `symsg list`, parent/child | T2 |
| P8 | Masking views use **cascaded IGs** for clusters, and port groups spread across **≥ 2 directors and ≥ 2 engines** where available | Path redundancy | `symaccess show view -detail`, PG ports by director | T2 |
| P9 | Each host has **≥ 2 paths per fabric**, all logged in | Failover | `symaccess list logins` | fabric/host |
| P10 | Host multipath per Dell's host guide: PowerPath or native MPIO / NMP Round Robin with the recommended settings | Performance and failover | host side | host |
| P11 | **Service levels** and host I/O limits only where intended (PowerMaxOS 10: SL behavior differs, see the release docs) | Predictable performance | `symsg show` SL, host I/O limits | T2 |
| P12 | No orphan devices (not in any SG/MV) and no SGs without an MV, unless documented | Capacity, hygiene | `symdev list -noport`, SGs without views | report |
| P13 | Device IDs and LUN addresses consistent across cluster nodes (cascaded IG) | Clusters | masking detail | T2 |

## Capacity and performance

| # | Practice | Why | Check | Fix tier |
|---|---|---|---|---|
| P14 | SRP used **< 80%**, with subscription within policy and runway > 90 days | Headroom | `symcfg list -srp -detail` | plan |
| P15 | **Data reduction** enabled on eligible SGs, with DRR reviewed | Capacity | SRP / SG data-reduction detail | T2 |
| P16 | Snapshot delta capacity monitored (SnapVX deltas consume SRP) | Surprise capacity | `symsnapvx list -detail` | report |
| P17 | Response time per SG within SL expectations. FE port utilization balanced. | Performance | Unisphere performance | T2 |

## Security and management

| # | Practice | Why | Check | Fix tier |
|---|---|---|---|---|
| P18 | **symauth / Unisphere user authorization** enabled. Monitor role for read-only tools. Admin via AD groups. | Accountability, blast radius | `symauth -sid S list` | T2 |
| P19 | **Symmetrix Access Control (symacl)** restricting which hosts can manage which devices, where used | Prevent rogue management hosts | `symacl list` | T3 |
| P20 | Gatekeepers dedicated per management host (no shared gatekeepers across apps) | Stability | `symgate list` | T2 |
| P21 | Data at Rest Encryption (D@RE) where policy requires, with an external KMIP manager if mandated | Compliance | `symcfg list -v` (encryption) | T3 |
| P22 | Unisphere and Solutions Enabler on supported versions. Audit log forwarded to SIEM. Secure Remote Services (SRS / SCG) connected. | Supportability, detection | versions, `symaudit` forwarding | T2 |
| P23 | PowerMaxOS on a Dell **target code** level | Bugs | `symcfg list -v` | T3 (Dell) |
