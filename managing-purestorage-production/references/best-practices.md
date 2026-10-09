# Best practices: configuration audit (Pure FlashArray / FlashBlade)

Use this for a "best-practice audit" or "config review". Every check is read-only (T0). Each finding names the fix and its tier, and the fix goes through change-gate.md. Site standards override these defaults. Verify vendor-specific values against the current Pure support KBs (host connectivity guides) for your Purity version.

Report format: **# | Practice | Current value | Status (OK / GAP / N/A) | Risk | Fix (tier)**, then a prioritized summary.

## FlashArray: protection and resilience

| # | Practice | Why | Check | Fix tier |
|---|---|---|---|---|
| FA1 | **SafeMode enabled** on production arrays (eradication delay ≥ 7 days, manual eradication locked) | Ransomware or an insider can't eradicate data or snapshots | eradication config / SafeMode status (Pure1 or support) | T3 (Pure Support) |
| FA2 | Every production volume is in **a protection group** with a local snapshot schedule | No snapshots means no fast restore | `purevol list` vs. `purepgroup list` members (volumes, hosts, hgroups) | T1/T2 |
| FA3 | pgroup retention matches the RPO/RTO policy (e.g. hourly for 1d, daily for 7–30d) | Too short loses restore points. Too long wastes capacity. | `purepgroup list --retention --schedule` | T2 |
| FA4 | **Replication** (async, ActiveDR or ActiveCluster) for tier-1 data, with the RPO monitored | DR | `purepgroup list` targets, `purepod list`, replica lag | T2 |
| FA5 | SafeMode-protected (retention-locked) pgroups for critical data, where licensed | Locked snapshots | pgroup retention-lock attribute | T3 |
| FA6 | ActiveCluster: the **mediator** reachable from both arrays (Pure1 cloud mediator or an on-prem mediator at a third site), and the failover preference set per pod | Avoids split-brain and frozen pods | `purepod list --mediator`, failover preference | T2 |
| FA7 | Restore tests: a pgroup snapshot copied to a test volume and mounted at least quarterly | Untested backups don't count | ask / check for recent `purevol copy` test volumes | process |

## FlashArray: hosts and connectivity

| # | Practice | Why | Check | Fix tier |
|---|---|---|---|---|
| FA8 | Correct **host personality** set where the OS needs it (per Pure's host guide, e.g. for AIX, HP-UX, Solaris, some ESXi/vSphere Metro cluster cases) | Path and ALUA behavior | `purehost list --personality` | T2 |
| FA9 | **Every host has ≥ 2 paths on both controllers** (CT0 and CT1) | A controller failover must not drop the host | `pureport list --initiator` per host's initiators | fabric/host |
| FA10 | Clustered hosts share LUNs through a **host group** (consistent LUN IDs) | Inconsistent LUN IDs break clusters and VMFS | `purehgroup list --connect` vs. per-host connections | T2 |
| FA11 | Host multipath set per Pure's guide: ESXi Round Robin with IOPS=1 (or latency-based PSP on newer ESXi), Linux multipath.conf per KB, Windows MPIO | Performance and failover | host side (ask the host team) | host |
| FA12 | No volume connected to a host that isn't in the CMDB, and no orphan volumes (unconnected, no recent I/O) | Hygiene, capacity | `purevol list --connect`, volumes without connections | report |
| FA13 | iSCSI on dedicated VLANs and jumbo frames end to end, or FC zoning single-initiator / single-target (or peer zoning) | Stability | network / fabric review | network |

## FlashArray: capacity and performance

| # | Practice | Why | Check | Fix tier |
|---|---|---|---|---|
| FA14 | Array used **< 80%** steady state, with Pure1 forecast runway > 90 days | GC and performance headroom, time to procure | `purearray list --space`, Pure1 forecast | plan capacity |
| FA15 | Eradication-pending space reviewed (destroyed volumes nobody expects) | Hidden capacity use | `purevol list --pending` | T3 |
| FA16 | QoS limits only where intended, and documented | An undocumented limit looks like an outage | `purevol list --qos` | T2 |
| FA17 | Purity on a **supported, recommended** release (Pure1 recommendations), with upgrades via Pure1 self-service or Support | Bugs, security | `purearray list`, Pure1 | T3 |

## FlashArray: security and management

| # | Practice | Why | Check | Fix tier |
|---|---|---|---|---|
| FA18 | Directory service (LDAP/AD) with role groups. Local `pureuser` password vaulted and only used for break-glass. | Accountability | `pureds list`, `pureadmin list` | T2 |
| FA19 | Least-privilege API tokens (read-only for monitoring and MCP), rotated | Blast radius | `pureadmin list --api-token` (no secrets shown) | T2 |
| FA20 | Phone-home and remote assist policy per security standards, Pure1 connected | Proactive support | `purearray list --phonehome`, remote assist status | T2 |
| FA21 | NTP, DNS, syslog, SNMP/alert email configured. Alert recipients reach a monitored queue. | Detection | `purearray list --ntpserver`, `purealert list` (recipients) | T2 |
| FA22 | Management interfaces on a management network only, with a trusted cert installed | Attack surface | `purenetwork list`, cert | T2 |
| FA23 | Encryption at rest (always on), and KMIP if policy requires external key management | Compliance | array info | T3 |

## FlashBlade

| # | Practice | Why | Check | Fix tier |
|---|---|---|---|---|
| FB1 | **SafeMode** enabled, and snapshot policies locked for critical file systems and buckets | Ransomware | support / policies | T3 |
| FB2 | Snapshot policy on every production FS, with retention matching the RPO | Restore | `purefs list` + `purepolicy list` | T2 |
| FB3 | Replica links (FS and bucket) for tier-1 data, with lag monitored | DR | `/file-system-replica-links`, `/bucket-replica-links` | T2 |
| FB4 | NFS export rules **least privilege**: no `*` rw clients, root-squash on unless needed, NFSv4.1 with Kerberos where possible | Data exposure | export policies | T2 |
| FB5 | SMB: shares on AD-joined servers, access-based enumeration, no Everyone:Full | Data exposure | SMB policies | T2 |
| FB6 | S3: one object store account per tenant, keys per application, **versioning + object lock for backup targets** (Veeam, Commvault, ...) | Ransomware-proof backups | `/buckets` versioning and lock | T2 / T3 |
| FB7 | Hard limits only where they're intended. Default quotas documented. | Surprise ENOSPC | `purefs list` hard-limit | T2 |
| FB8 | Capacity < 80%, and data VIPs spread across the fabric | Headroom, balance | `/arrays/space`, network | plan |
