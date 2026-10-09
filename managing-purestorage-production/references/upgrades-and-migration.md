# Upgrades and migration: Pure Storage

Use with references/upgrade-checklist.md (generic gates) and references/change-gate.md. Confirm the procedures against Pure's current documentation and support for your Purity version.

## Purity upgrades
- **How:** Pure1 Self-Service Upgrades (SSU) where eligible, otherwise Pure Support-led. Each controller fails over in turn (non-disruptive when hosts multipath correctly).
- **Extra readiness checks:**
  - every host has live paths on **both controllers** (`pureport list --initiator`). Run the host-path check from best-practices.md (FA9).
  - Pure1 upgrade-readiness / health check is clean, with no open Pure support cases blocking
  - ActiveCluster: upgrade **one array at a time**, pods `online` on both, mediator reachable
  - replication peers: confirm the Purity version pairs are supported for async/ActiveDR
- **Watch between controllers:**
  - paths return (host side)
  - latency normal
  - `puremessage list --open` has no new criticals
- **FlashBlade:** Pure-led as well. Check blades/fabric modules healthy and client mounts survive the rolling restarts.

## Migration / tech refresh
Options, from least disruptive to most:
1. **ActiveCluster stretch** (FlashArray → FlashArray): add the new array to the pod (`purepod add --array`), let it resync, move host paths to the new array, then remove the old array (T3, typed pod name). Host-transparent when paths are planned.
2. **Async replication + cutover:** replicate pgroups to the new array, short outage to stop apps, final replication, connect volumes on the new array, start apps.
3. **Host-based:** Storage vMotion (VMware), LVM mirror / ASM rebalance (Linux/Oracle), Storage Migration Service (Windows). No array dependency, but more host work.
4. **FlashBlade:** file migration tools (rsync/robocopy class, or vendor migration services). For buckets, S3 copy tools preserving versioning and lock semantics.

**Checklist for any migration:**
- inventory: volumes, hosts, LUN IDs, pgroups, schedules
- target sized for capacity **and** snapshots/replication
- cutover plan per application, with the app owner
- rollback: keep the source untouched until sign-off
- decommission the source with the staged pattern in flasharray.md
