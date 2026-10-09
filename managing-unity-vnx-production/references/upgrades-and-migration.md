# Upgrades and migration: Unity / VNX

Use with references/upgrade-checklist.md (generic gates) and references/change-gate.md. Confirm against Dell's Unity OE release notes, the host connectivity guides and E-Lab interoperability.

## Unity OE upgrades
- **How:**
  - the Unisphere upgrade wizard (or `uemcli /sys/soft/upgrade`)
  - the **pre-upgrade health check** runs first and must be clean
  - the SPs reboot one at a time (non-disruptive when hosts multipath to both SPs)
  - drive firmware is a separate bundle
- **Extra readiness checks:**
  - every host has paths to **both SPs** (best-practices.md U10/U11)
  - NAS servers can fail over (interfaces on both SPs, LACP/FSN configured)
  - replication partners on compatible OE versions
  - no replication sync or LUN move in progress
- **Watch:**
  - each SP returns
  - NAS servers fail back
  - paths recover
  - no new alerts

## VNX (end of life)
- Block OE NDU and File OE upgrades are Dell-led **if** a support contract still covers it.
- With EOL, the priority is **migration, not upgrades**. Only apply patches that fix a known issue affecting you.

## Migration / tech refresh (VNX exit and Unity refresh)
Options:
1. **PowerStore native import:** it supports importing from Unity, VNX2 and other Dell sources for block (and file on supported versions), with host-agent or agentless options. Check the PowerStore import compatibility matrix for your exact source OE.
2. **Unity native import:** VNX → Unity block (via SAN Copy-based import) and VNX file → Unity (NFS/SMB import), on supported OE versions.
3. **Host-based:** Storage vMotion, LVM / ASM, Windows Storage Migration Service. Use this when the array-based paths don't fit.
4. **File:** robocopy / rsync class tools for SMB/NFS, preserving ACLs. Plan the cutover of NAS server names and IPs.

**Checklist for any migration:**
- inventory: LUNs, storage groups/hosts, HLU IDs, NAS servers, shares/exports, quotas, snapshot schedules, replication
- the target sized
- cutover per application
- rollback: the source untouched until sign-off
- decommission the source with the staged pattern in unity.md / vnx.md
