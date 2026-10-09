# Upgrades and migration: NetApp

Use with references/upgrade-checklist.md (generic gates) and references/change-gate.md. Confirm against NetApp's upgrade documentation, Digital Advisor's Upgrade Advisor and the Interoperability Matrix Tool (IMT) for your release.

## ONTAP upgrades (ANDU)
- **How:**
  - automated non-disruptive upgrade: `cluster image package get`, then `cluster image validate`, then `cluster image update`, or through System Manager
  - **MetroCluster** and **SnapMirror active sync** clusters have their own procedures
  - firmware for disks, shelves and SP/BMC is usually bundled
- **Extra readiness checks:**
  - Digital Advisor **Upgrade Advisor** plan for the cluster, and `cluster image validate` clean
  - IMT: host OS, HBAs, multipath, host utilities, and the SnapCenter/backup software versions
  - **SnapMirror interoperability:** the version pair between source and destination must be supported. The order of upgrade (often the destination first) follows NetApp's SnapMirror compatibility rules.
  - `storage failover show`: takeover possible on every HA pair. LIFs home. Failover groups span both nodes (best-practices.md N15).
  - no `volume move`, SnapMirror baseline or aggregate reconstruction running
- **Watch between nodes:**
  - giveback complete
  - LIFs back home
  - SAN paths restored
  - no new EMS errors
  - latency normal
- **StorageGRID:** upgrade from the Grid Manager (primary admin node first, then rolling). Check ILM backlog and node health first.

## Migration / tech refresh
Options, from least disruptive to most:
1. **Within a cluster:** `volume move` (non-disruptive, to new aggregates or new nodes added to the cluster), then remove old nodes (`cluster unjoin`, NetApp procedure). This is the classic head swap.
2. **Cluster to cluster:** SnapMirror (or **SVM migrate** / SVM-DR on supported releases) with a planned cutover:
   1. final update
   2. quiesce / break **on the destination**
   3. redirect clients (DNS, LIFs or remount)
   4. keep the source read-only until sign-off
3. **From third-party NAS/SAN:** XCP (NFS/SMB) or Foreign LUN Import (FLI), plus host-based tools.
4. **To StorageGRID / cloud tiers:** FabricPool policies (T2/T3: tiering changes performance and cost).

**Checklist for any migration:**
- inventory: SVMs, volumes, junctions, export policies, shares/ACLs, LUN maps, igroups, snapshot policies, SnapMirror
- the target sized with efficiency assumptions **stated**
- cutover per application
- rollback: the source is untouched until sign-off
- decommission the source with the staged pattern in ontap.md
