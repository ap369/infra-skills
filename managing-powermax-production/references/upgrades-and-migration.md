# Upgrades and migration: PowerMax / VMAX

Use with references/upgrade-checklist.md (generic gates) and references/change-gate.md. Confirm against Dell's PowerMaxOS / HYPERMAX OS release notes, the Dell host connectivity guides and E-Lab interoperability for your code.

## Code upgrades
- **How:** PowerMaxOS / HYPERMAX OS code loads are **Dell-led** (non-disruptive, director by director). The customer upgrades Solutions Enabler and Unisphere: management first, and they must support the target code.
- **Extra readiness checks:**
  - every host has paths through **≥ 2 directors** (`symaccess list logins`, best-practices.md P8/P9)
  - SRDF partner arrays are on code levels supported against the target. Dell plans the order for SRDF pairs.
  - no SRDF resync, SnapVX link-copy or data movement in progress. SRDF/A cycle times normal.
  - `symevent` clean, no failed drives or directors
- **Watch:** director/port status returns, host paths recover, SRDF stays Consistent/Synchronized, response times normal.

## Migration / tech refresh
Options, from least disruptive to most:
1. **NDM (Non-Disruptive Migration)**, VMAX → PowerMax for supported code and host combinations (`symdm`). It moves an SG with host paths kept, using a temporary SRDF-based link. Dell-documented steps: create, cutover, commit (commit is T3).
2. **SRDF-based migration:** replicate the SGs to the new array, then a planned cutover (application stop, final sync, split, mask on the new array, host rescan).
3. **Host-based:** PowerPath Migration Enabler, Storage vMotion, LVM / ASM.

**Checklist for any migration:**
- inventory: SGs (parent/child), MVs, IGs, PGs, device sizes, SLs, SnapVX policies, SRDF groups
- the target SRP sized including snapshot deltas
- cutover per application
- rollback: keep the source masked off but intact until sign-off
- decommission the source with the staged pattern in powermax-vmax.md (unmask → quarantine → deallocate)
