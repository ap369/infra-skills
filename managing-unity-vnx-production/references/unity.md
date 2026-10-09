# Unity / Unity XT reference (Unisphere, uemcli, REST)

Syntax drifts between OE versions. Confirm with `uemcli -d <mgmt> <object> -help` before putting a command in a change plan.

## Object model

| Object | What it is | Gotchas |
|---|---|---|
| Pool (traditional / dynamic) | Capacity for all resources | At 100% full, thin LUNs and filesystems stop taking writes, and datastores and VMs pause |
| LUN / consistency group | Block storage, host access list | Removing host access means an instant loss for that host |
| VMware datastore (VMFS / NFS / vVol) | Unity-managed datastore | Deleting it in Unity deletes the datastore |
| NAS server / filesystem | File: interfaces, NFS/SMB shares, quotas | Interface or NAS server changes drop clients |
| Snapshot + schedule | Point-in-time copy, auto-delete settings | `restore` overwrites the source. Attached snapshots are in use. Replication snapshots must not be deleted. |
| Replication session (sync / async) | To another Unity or VNX (import) | Pause, failover and failback are DR operations |
| Host / initiator | Host object with IQNs/WWNs | Removing an initiator drops its paths |
| Host I/O limit | QoS | A too-low limit causes a latency outage |

## Read-only (T0)

MCP (community `dell-unity-mcp-server`, GET-only): pool, LUN, filesystem, snap, replicationSession, alert, host, nasServer, nfsShare, cifsShare instances. Use filters (`filter=...`) and narrow `fields`.

uemcli equivalents:
```
uemcli -d <mgmt> /sys/general show -detail
uemcli -d <mgmt> /event/alert/hist show                # alerts
uemcli -d <mgmt> /env/sp show -detail ; /env/disk show -detail
uemcli -d <mgmt> /stor/config/pool show -detail        # size, used, snapshot use, auto-delete settings
uemcli -d <mgmt> /stor/prov/luns/lun show -detail      # size, alloc, host access, snap schedule
uemcli -d <mgmt> /stor/prov/fs show -detail
uemcli -d <mgmt> /prot/snap show -detail               # source, creation, creator, attached, expiration, auto-delete
uemcli -d <mgmt> /prot/rep/session show -detail
uemcli -d <mgmt> /remote/host show -detail ; /remote/initiator show
uemcli -d <mgmt> /net/nas/server show ; /stor/prov/fs/nfs show ; /stor/prov/fs/cifs show
uemcli -d <mgmt> /metrics/value/rt -path sp.*.storage.lun.*.responseTime show   # check the path names with -help
```
REST: `https://<mgmt>/api/types/<type>/instances?fields=...` (pool, lun, filesystem, snap, replicationSession, alert, host).

## Change operations by tier

| Tier | Operation | uemcli (sketch) | Rollback |
|---|---|---|---|
| T1 | Snapshot | `/prot/snap create -source <res_id> -name CHG123 -keepFor 7d` | delete it |
| T1 | Create LUN / FS / share / host | `/stor/prov/luns/lun create ...` | delete (unused) |
| T1 | Grant host access to a new LUN | `/stor/prov/luns/lun -id X set -lunHosts ...` | remove: T3 once used |
| T2 | Expand LUN / FS | `... -id X set -size <bigger>` | no shrink for LUNs |
| T2 | Pool expansion | `/stor/config/pool -name P extend -drivesNumber ...` | **can't remove drives:** permanent capacity commitment |
| T2 | Snapshot schedule / pool auto-delete thresholds / host I/O limit | `set ...` | previous values recorded |
| T2 | Replication pause / resume / sync | `/prot/rep/session -id X pause` | resume. DR is paused meanwhile. |
| T3 | Delete snapshot | `/prot/snap -id X delete` | **NONE** |
| T3 | Snapshot restore | `/prot/snap -id X restore [-backupName ...]` | data written after the snapshot is lost. Always keep a backup snapshot. |
| T3 | Remove host access / initiator / delete host | `set -lunHosts ...`, `/remote/initiator -id X delete` | re-add. The host outage happens in between. |
| T3 | Delete LUN / FS / datastore / NAS server | `... -id X delete` | **NONE** |
| T3 | Replication failover / failback / delete session | `/prot/rep/session -id X failover` | DR runbook only |
| T3 | OE upgrade, SP reboot/service mode, drive/pool removal | Dell support / NDU procedure | n/a |

## Pool full: relief ranked by safety
1. **Read** where the space goes: pool `-detail` (snapshot vs. data used), the top LUNs and filesystems, and the auto-delete thresholds.
2. **Pool snapshot auto-delete** (T2) may already be configured. Check its thresholds first, since it may be about to reclaim space on its own.
3. Expand the pool with free drives (T2, but permanent).
4. Expire or delete **named** snapshots (T3). The user approves the list they can see: a compact table (ID, source, age, size, reason it's safe). If the user says "don't list them", give the compact table anyway. Approval is for the objects shown, never "the safe set".
   - **Exclude** attached snapshots, replication-owned snapshots (`/prot/rep/session`), snapshots created by AppSync/RecoverPoint/backup apps, and any with a future expiration someone set on purpose.
5. Move resources to another pool (LUN move: online, heavy I/O).
