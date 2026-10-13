# SnapVX and SRDF (from Dell public documentation)

Sources (public PDFs at dl.dell.com, retrieved 2026-10-14):
- *Solutions Enabler 10.0.0 TimeFinder SnapVX CLI User Guide* (Jul 2022, the latest SnapVX guide; 10.4 has no SnapVX CLI changes)
- *Solutions Enabler 10.4.0 SRDF Family CLI User Guide* (Apr 2026)
- *SRDF Family State Tables Guide 10.4.0* (Apr 2026)
- *SRDF Introduction* (Oct 2025, Rev 07)
- *SRDF/Metro vWitness Configuration Guide* (Jun 2025, Rev 12)

Summarized in our own words. Before any SRDF control, check the **State Tables Guide**, which lists which actions are allowed in each pair state.

## TimeFinder SnapVX
- **Supported:** HYPERMAX OS 5977 and PowerMaxOS 5978 or later. Snapshots are always consistent. Cross-array consistency needs the devices in a **composite group**.
- **Limits per source volume:** up to **256 manual** snapshots, and **1,024 total** (manual + policy + legacy TimeFinder sessions). Up to 1,024 linked targets.
- **Snapshot types:**
  - manual (`symsnapvx establish`)
  - **policy / automated**: TTL is set by the policy (≤ 400 days). Deleting the policy marks its snapshots `_Orphaned`.
  - zDP (mainframe, report-only from open systems)
- **TTL / secure expiration:** `-ttl -delta <days[:hh]>` or `-absolute <MM/DD/YYYY[:HH]>`, **1–400 days**.
- **Secure snaps** (`establish -secure ...`, or convert an existing snap): they can't be terminated before they expire. **When the SRP hits Reserved Capacity they keep growing, and they take priority over host writes if the SRP fills completely.** They protect against attacks and runaway apps, but they can starve production writes. Automated snapshots **can't** be converted to secure; use secure snapshot policies instead.
- **Restore:** `symsnapvx -sid S -sg SG -snapshot_name N -gen G restore`.
  - It's differential: only changed tracks are copied back to the source.
  - **An expired snapshot (secure or regular) can't be restored.**
  - **Terminate the restore session before terminating the original snapshot.**
  - Devices added to an SG after a snapshot was taken don't have that snapshot, so check before restoring an SG.
- **Link / relink:** link snapshots to target SGs (`-lnsg`) for test or dev copies or recovery. `-copy` makes a full copy that **overwrites the target devices' data**.
- **`-both_sides`** (local and remote snapshots in one command): only valid for SRDF/S in the Synchronous state, or SRDF/Metro in ActiveActive/ActiveBias. Every RDF device must be in the same RDF group, with no R1/R2 mix.

## SRDF modes and states
| Mode | Behaviour | Guidance |
|---|---|---|
| SRDF/S | Write acknowledged after it's in cache on both arrays | Recommended distance **≤ 200 km (125 mi)** |
| SRDF/A | Asynchronous cycles, dependent-write consistent R2 when consistency is enabled | Extended distance. Use DSE, transmit idle and write pacing to ride out link problems. |
| SRDF/Metro | R1 and R2 both read/write with the same identity (WWN, geometry) | Witness (Array Witness or vWitness) or bias decides the survivor |
| Adaptive copy | Bulk / migration copy, not for DR consistency | |

- **Metro pair states:**
  - **ActiveActive** is the normal state with a witness.
  - **ActiveBias** means bias is used: requested, or **the witness isn't available**. An unexpected ActiveBias is a health finding.
  - **Suspended** means I/O accumulates as invalid tracks owed to the other side.
- Verify with:
  - `symrdf -g DG verify -activeactive|-activebias`
  - `symrdf -cg CG verify -consistent [-noinvalids] [-i 60]` (waits for "Consistent with no invalid tracks")
  - `symrdf query -rdfa` (SRDF/A)

## Control operations: what each one is for (SRDF CLI guide)
| Operation | Use it for | Risk |
|---|---|---|
| `establish -full` | **Initial synchronization**, or after **replacing a failed R2 drive** | Full copy. R2 not usable as a consistent image until it finishes. **T3.** |
| `establish` (incremental) | Rejoin a **split** pair, or pairs made RW on the link after being NR. Only changed tracks are copied. **Use it only if the R2 data can be discarded.** R2 is write-disabled during the operation, and its invalid tracks are refreshed from R1. | T2 (T3 if R2 holds data you need) |
| `resume` | Resume I/O on links of a **suspended** pair | T2 |
| `suspend` / `split` | Stop link I/O / stop mirroring. Protection pauses, and invalid tracks accumulate. `-immediate` drops an SRDF/A session at once. | T2 |
| `restore [-full]` | Copy R2 → R1 | **T3: overwrites production** |
| `failover` / `failback` / `update` / `swap` | DR moves, failback after repair, refreshing R1 while R2 runs | **T3, DR runbook only** |
| `invalidate r1|r2` | Mark all tracks invalid on one side so they're recopied | **T3** |
| `write_disable` / `rw_enable r1|r2` | Change host write access per side | T3 (host impact) |
| `enable` / `disable` | Consistency protection for SRDF/A | T2 |
| `createpair` / `deletepair` / `swap` (dynamic) | Pair and group configuration | T3 when devices hold data |

**Gold copy:** Dell's SRDF/Star procedures strongly recommend a gold copy at the target **before** reconnecting or resyncing. The skill applies the same rule to every resync: take a SnapVX snapshot of the R2 SG first.

## Group attributes worth knowing (SRDF CLI guide)
- **Link limbo:** delays declaring links down. Not recommended in synchronous mode. Over 10 s in SRDF/S can make apps or hosts fail. To ride out short drops in SRDF/A, use **transmit idle** instead.
- **Domino mode:** stops all writes to R1 and R2 when R2 can't be updated. It protects integrity in rolling disasters at the cost of an outage. It's a deliberate design choice (T3 to change).
- **Autolink recovery** (`-autolink_recovery on|off`, default off): restores the pre-failure SRDF states when links return.
- **DSE (Delta Set Extension):** spills SRDF/A cycles into the SRP during link problems. Capacity-manage it so it doesn't fill the SRP.

## SRDF/Metro witness (vWitness guide)
- **At least two vWitness instances** per Metro configuration, on different servers, ideally at a **third site** separate from both arrays.
- Size the witnesses for the number of arrays, pairs and Metro groups they serve (see the guide's limits table). Keep UTC time synchronized.
- With the witness lost, pairs fall back to **bias** (ActiveBias), and a later array or link failure is decided by bias. Treat witness loss as reduced protection, and freeze Metro changes until it's restored.

## SRDF/Metro Smart DR (SE 10.4)
- `symmdr` manages Metro + DR environments. From 10.4, modify works from **cascaded** as well as concurrent staging (`symmdr -sid S -name ENV modify -add|-remove ... -metro_rdfg ... -dr_rdfg ... -cascaded|-concurrent`). T3 on production environments.
