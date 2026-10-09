# Best practices: configuration audit (Unity / VNX)

Use this for a "best-practice audit" or "config review". Every check is read-only (T0) through the GET-only MCP, `uemcli ... show`, or `naviseccli` list commands, run as a read-only account. Each finding names the fix and its tier, and the fix goes through change-gate.md. Site standards override these defaults. Verify against Dell's Unity best-practices guide and host connectivity guides for your OE.

Report format: **# | Practice | Current value | Status (OK / GAP / N/A) | Risk | Fix (tier)**, then a prioritized summary.

## Unity: protection

| # | Practice | Why | Check | Fix tier |
|---|---|---|---|---|
| U1 | **Snapshot schedule** on every production LUN, CG, FS and datastore, with retention per RPO | Fast restore | `/stor/prov/luns/lun show -detail` (schedule), `/sched/schedule show` | T2 |
| U2 | Related LUNs (DB data and logs) in a **consistency group** with CG snapshots | Crash consistency | `/stor/prov/luns/group show` | T2 |
| U3 | **Pool snapshot auto-delete** thresholds set (for example start 95%, stop 85%) or pool harvesting configured deliberately | Prevents pool-full outages | `/stor/config/pool show -detail` | T2 |
| U4 | **Replication** (async/sync) for tier-1 to a second array, RPO monitored, DR tests done | DR | `/prot/rep/session show -detail` | T2 |
| U5 | **Snapshots with a retention lock** / secure snapshots where the OE supports them, for ransomware | Snapshots can't be deleted early | snapshot detail | T3 |

## Unity: provisioning and capacity

| # | Practice | Why | Check | Fix tier |
|---|---|---|---|---|
| U6 | Pool used **< 80%**, with runway > 90 days. Dynamic pools on newer models. | Headroom | `/stor/config/pool show -detail` | plan |
| U7 | Thin provisioning **with** pool monitoring and alert thresholds set | Avoid surprise full | pool alert threshold | T2 |
| U8 | **Data reduction** (+ advanced dedupe) on eligible all-flash resources | Capacity | LUN/FS detail | T2 |
| U9 | **Host I/O limits** only where intended, and documented | An undocumented limit looks like an outage | `/stor/config/iolimit show` | T2 |
| U10 | Hosts registered with **all initiators, ≥ 2 paths per SP** | SP failover | `/remote/initiator show`, paths | fabric/host |
| U11 | Multipath per Dell's host guide (PowerPath, or native with ALUA). Correct host OS type. | Failover | host side | host |
| U12 | NAS: NAS servers on **both SPs** (balanced), LACP / FSN on interfaces, SMB signing, no SMB1, NFS exports least privilege (no `*` rw, root squash) | Availability, security | `/net/nas/server show`, share and export detail | T2 |
| U13 | FAST Cache / FAST VP configured as designed (hybrid models) | Performance | pool tiering detail | T2 |

## Unity: management and security

| # | Practice | Why | Check | Fix tier |
|---|---|---|---|---|
| U14 | LDAP/AD accounts with roles. **Operator** role for monitoring and MCP. `admin` vaulted. | Accountability | `/user/account show` | T2 |
| U15 | NTP, DNS, syslog/remote logging, alert email/SNMP configured | Detection | `/net/ntp/server show`, `/event/alert/conf show` | T2 |
| U16 | Secure Connect Gateway / ESRS connected | Proactive support | support config | T2 |
| U17 | Data at Rest Encryption enabled and keystore backed up (if licensed) | Compliance | `/prot/encrypt show` | T3 |
| U18 | OE on a supported, recommended release | Bugs, security | `/sys/soft/ver show` | T3 |

## VNX (end of life, so stabilize and migrate)

| # | Practice | Why | Check | Fix tier |
|---|---|---|---|---|
| V1 | **Migration plan** to supported storage, with support status documented | EOL risk | support contract | plan |
| V2 | LUNs on their **default SP owner**, balanced across SPs | Performance, clean failover | `lun -list -default -owner -curowner` | T2 |
| V3 | Host failover mode **4 (ALUA)** for supported OSes, or PowerPath | Transparent trespass | `storagegroup -list -host`, port `failovermode` | T2 |
| V4 | Each host has ≥ 2 paths to **both SPs** | SP failure tolerance | `port -list -hba` | fabric/host |
| V5 | Hot spares available per drive type (VNX1), or unbound drives for permanent sparing (VNX2) | Rebuild | `getdisk`, faults | hardware |
| V6 | Pools < 80%, and FAST Cache healthy | Headroom | `storagepool -list -prcntFull` | plan |
| V7 | VNX Snapshots / SnapView schedules on critical LUNs. MirrorView/Replicator monitored. | Restore, DR | `snap -list`, `mirror -async -list`, `nas_replicate -list` | T2 |
| V8 | File: Data Mover standby configured, checkpoints scheduled, exports least privilege | Availability, security | `nas_server -list`, `fs_ckpt`, `server_export` | T2 |
| V9 | Management security: non-default passwords, security file per admin, Unisphere on a management network | Security | account review | T2 |
