# FlashArray reference (Purity//FA 6.x)

Syntax drifts between Purity releases. Confirm with `<command> --help` on the target array before putting a command in a change plan.

## Object model

| Object | What it is | Gotchas |
|---|---|---|
| Volume | Block device (thin, deduped) | Same name may exist inside a pod as `pod::vol` |
| Host | Initiator set (WWN / IQN / NQN) + personality (esxi, aix, hpux...) | Wrong personality = path/ALUA issues |
| Host group (hgroup) | Cluster of hosts sharing LUNs | Shared connection LUN must be same on every host |
| Connection | Volume ↔ host/hgroup mapping with LUN id | Disconnect = instant loss of access |
| Protection group (pgroup) | Snapshot + replication policy for volumes/hosts/hgroups | Retention change deletes older snaps on next cycle |
| Pod | Container for ActiveCluster (sync) or ActiveDR | Stretched pod = writes mirrored to 2 arrays |
| Snapshot | Immutable point-in-time `vol.suffix` / `pg.suffix.vol` | Restore via `purevol copy --overwrite` replaces data |
| Destroyed object | Soft-deleted, in eradication pending period | Default 24h; SafeMode may extend/lock |

## Read-only commands (T0)

```
purearray list                       # name, Purity version
purearray list --space               # capacity, data reduction, snapshots, shared
purearray monitor --interval 5 --repeat 6   # IOPS, bandwidth, latency (usec/op)
puremessage list --open              # open alerts
purevol list --space                 # per-volume size, used, snapshots
purevol list --connect               # volume → host/hgroup + LUN
purevol list --snap                  # snapshots
purevol list --pending               # destroyed, awaiting eradication (+ time left)
purevol monitor --interval 5 --repeat 6 <vol>   # live I/O on a volume
purehost list --all                  # initiators, personality, hgroup
purehost list --connect              # host → volumes
purehgroup list --connect
pureport list --initiator            # which initiators are logged in on which target port
purepgroup list --schedule / --retention / --snap
purepod list ; purepod list --array  # pod members, status (online/offline/resyncing)
purearray list --connect             # replication connections and status
purehw list ; puredrive list         # hardware health
```

REST 2.x equivalents (GET): `/arrays`, `/arrays/space`, `/arrays/performance`, `/alerts?filter=state='open'`, `/volumes`, `/volumes/space`, `/volumes/performance`, `/connections`, `/hosts`, `/host-groups`, `/protection-groups`, `/protection-group-snapshots`, `/pods`, `/array-connections`, `/hardware`, `/drives`. Auth: `POST /api/2.x/login` with an `api-token` header, which returns `x-auth-token`.

## Change commands by risk tier

| Tier | Operation | Command | Rollback |
|---|---|---|---|
| T1 | Snapshot volume | `purevol snap --suffix CHG1234 <vol>` | `purevol destroy <vol>.CHG1234` |
| T1 | Snapshot pgroup | `purepgroup snap --suffix CHG1234 <pg>` (`--replicate-now` to also send) | destroy snap |
| T1 | Create volume | `purevol create --size 2T <vol>` | `purevol destroy <vol>` |
| T1 | Create host | `purehost create --wwnlist <wwn,...> <host>` / `--iqnlist` / `--nqnlist` | `purehost delete <host>` |
| T1 | Connect vol → host | `purehost connect --vol <vol> <host>` (`--lun N`) | `purehost disconnect --vol <vol> <host>` |
| T1 | Connect vol → hgroup | `purehgroup connect --vol <vol> <hg>` | disconnect |
| T2 | Grow volume | `purevol setattr --size 6T <vol>` | none (cannot shrink safely) |
| T2 | Rename | `purevol rename <old> <new>` | rename back. Check scripts and backups first. |
| T2 | QoS | `purevol setattr --bw-limit / --iops-limit` | `--bw-limit ''` |
| T2 | pgroup membership | `purepgroup setattr --addvollist / --remvollist` | inverse |
| T2 | pgroup schedule | `purepgroup schedule --snap-frequency / --replicate-frequency` | previous values (record them first) |
| T2 | pgroup retention | `purepgroup retain --all-for / --per-day / --days` (`--target-*` for target side) | previous values. **Snapshots pruned meanwhile are gone.** |
| T2 | Host personality / initiators | `purehost setattr --personality / --addwwnlist / --remwwnlist` | inverse. A wrong value drops paths. |
| T3 | Destroy volume | `purevol destroy <vol>` | `purevol recover <vol>` (within the eradication period) |
| T3 | Eradicate | `purevol eradicate <vol>` | **NONE** |
| T3 | Disconnect | `purehost disconnect --vol <vol> <host>` | reconnect with the **same LUN id** |
| T3 | Shrink | `purevol truncate --size 2T <vol>` | restore from a pre-change snapshot (`purevol copy --overwrite`). **Data past the new size is lost.** |
| T3 | Overwrite from snapshot | `purevol copy --overwrite <snap> <vol>` | only from a snapshot of the current state taken first |
| T3 | Pod unstretch / demote | `purepod remove --array <arr> <pod>`, `purepod demote` | re-stretch means a full resync. Risk of split-brain if done wrongly. |
| T3 | Replication teardown | `purearray disconnect`, `purepgroup setattr --remtargetlist` | re-establish. Target snapshots may be lost. |
| T3 | Eradication / SafeMode config | Pure Support only | n/a |
| T3 | Purity upgrade, controller failover/reboot | Pure Support / Pure1 self-service upgrade | n/a |

## Pre-check queries every change needs

1. `purevol list <vol> --space`: does the object exist, and how big is it?
2. `purevol list --connect <vol>`: any host connection means the volume is in use until proven otherwise.
3. `purevol monitor <vol>`: any nonzero I/O means it is active. **Zero I/O over 30 seconds does not mean unused.** Backup, DR and month-end jobs can be idle.
4. `purepgroup list` filtered on the volume: membership affects replication and retention.
5. Pod name prefix (`pod::`) and `purepod list --array`: stretched pods replicate the change to the peer.
6. `purevol list --pending` and the SafeMode state: what can be recovered and for how long.
7. `purearray list --space`: headroom. A snapshot of a hot volume grows as data changes.

## ActiveCluster notes
- Both arrays must show the pod `online` before *any* change. If it is `resyncing` or `offline`, the change waits.
- Failover preference (`purepod setattr --failover-preference`) decides which side survives a mediator or link loss. Changing it is T2.
- The mediator must be reachable (`purepod list --mediator`). If it isn't, a link failure can leave the pod frozen on both sides.
- Host paths: use uniform access with `--preferred-array` set for the local array. A wrong preference gives cross-site latency, not an outage.

## Capacity relief, ranked by safety
1. Check `purevol list --pending`. Destroyed volumes still consume space until eradication. Eradicating them is still T3.
2. Find large snapshot consumers (`purevol list --space --snap`). Before destroying any snapshot, check it isn't the only restore point and that no backup product (Veeam, Commvault, Rubrik) owns it.
3. Tighten pgroup retention (T2). Get the data owner's sign-off.
4. Move workloads to another array (`purevol copy` plus replication, or a host-side migration).
5. Add capacity (Pure1 forecast, Evergreen).

Never "free space fast" by eradicating. The space returns gradually through garbage collection, and the data can't be recovered.

## Decommission pattern (volume / host / pgroup)
1. **Read:**
   - connections (`purevol list --connect`)
   - I/O history (Pure1 / `purevol monitor` over days, not seconds)
   - pgroup membership and replication targets
   - pod membership
   - snapshots the business may still need
2. **Step 0:** take a final snapshot (`purevol snap --suffix decom-<ticket>`), or keep the pgroup's snapshots until the quarantine ends.
3. **Stage 1 (T3, reversible):** disconnect from hosts/hgroups (record the LUN IDs) and remove the volume from its pgroups. Hosts lose access, the data stays intact, and reconnecting with the **same LUN ID** reverses it.
4. **Quarantine:** default 7 days. Watch for anything that breaks.
5. **Stage 2 (T3, separate approval, volume names typed):** `purevol destroy`. It's recoverable during the eradication period.
6. **Eradicate:** let the eradication timer expire. Manual `eradicate` is only for a capacity emergency, as its own approval.
7. **Hosts:** delete host objects only after every volume connection is gone, and record the WWNs/IQNs in the ticket.
