# ActiveCluster and ActiveDR (from Everpure public documentation)

Source: public documentation at support.everpuredata.com (Pure Storage is now **Everpure**). Retrieved 2026-10-13: the *ActiveCluster*, *ActiveDR*, *ActiveCluster with VMware*, *ActiveDR with VMware* and *Oracle DR with ActiveDR* guides. Summarized in our own words. Check the current guide for your Purity//FA release before acting. Every promote, demote, stretch, unstretch or preference change is a change and goes through change-gate.md.

## Common requirements
| | ActiveCluster (sync) | ActiveDR (continuous async) |
|---|---|---|
| Min Purity//FA | **6.1.0** for FC replication (IP minimum: see the current guide) | **6.0.0**; FC interconnect from **6.1.7** |
| Version skew between arrays | Allowed temporarily, **within two minor versions**. Matching versions are best practice. | Within two minor versions |
| Distance / latency | Synchronous connection, **≤ 11 ms RTT**. Above that, use an async connection (ActiveDR / async). | Any distance |
| Replication ports | 4 replication ports per array, and resilient management connectivity to the mediator | 4 replication IPs per array (IP), every IP reachable from every peer IP |
| RPO | 0 (a write is acknowledged once in NVRAM on both arrays) | Near zero (typically single-digit seconds) |
| Unit | Pod (namespace and consistency group) | Pod + replica link |

## ActiveCluster

### Mediator and pre-election
- The **Pure1 Cloud Mediator** is the default. In the pod overview it shows as `purestorage`. Sites that can't reach it use the **ActiveCluster On-Premises Mediator** (deployed separately).
- **Each site needs an independent network path to the mediator** (management network, TCP 443 outbound for the Cloud Mediator). It must not share fate with the replication links.
- The mediator is only consulted when replication is lost (passive heartbeats).
- **Pre-election:** when both arrays lose the mediator, each pod is pre-elected to stay online on one array (following its failover preference). If the replication link then fails **5 or more minutes later**, the pod stays online there.

### Failure behaviour (per pod)
| Event | Result |
|---|---|
| Controller failover in one array | Short pause, I/O continues on both arrays, RPO 0 kept |
| Replication link loss | Short pause, then I/O only on the array that **won the mediator race** (the failover preference gives the preferred array a head start). Non-uniform hosts at the losing site lose access. Host clustering must restart apps. |
| Mediator loss alone | No effect |
| Whole array or site loss | The survivor (which must reach the mediator) continues automatically |
| **Mediator lost, then replication link / array / site lost within 5 minutes** | **I/O lost on both arrays (double failure).** Recover by restoring mediator or link access. The last resort is cloning the pod to new LUN serials so hosts can't split-brain, then re-identifying the LUNs on every host. |
| Mediator lost, then replication link lost **5+ minutes later** | Pre-election keeps the pod online on the pre-elected array |

**Agent rule:** when the mediator is unreachable, treat the pod as one failure away from a full outage. No other change on the pod or replication network until the mediator is back.

### Host and pod settings
- **Preferred array (per host, ALUA):** `purehost setattr --preferred-array <array> <host>`. Use it for **uniform** access (hosts see both arrays) when inter-array latency is above about 500 µs. It avoids remote reads and the 2× WAN round trip on writes. It isn't needed for non-uniform hosts. A wrong preference costs latency, not availability.
- **Pod failover preference:** `purepod setattr --failover-preference <array> <pod>`. **Best practice for clustered apps on non-uniform hosts.** Align each pod with the site where its application runs. A *preference* lets the non-preferred array win if the preferred one fails, whereas a fixed bias could cause a total outage. Pods and file Realms are arbitrated **independently**, so align preferences across containers serving the same cluster.
- Write I/O is acknowledged only after it's in NVRAM on both arrays, so expect latency to grow with RTT.

### Stretch, unstretch, re-stretch
- **Add existing volumes before you stretch.** Once a pod is stretched, existing volumes can't be moved in (only new volumes can be created in it) until it's unstretched. Move volumes in with `purevol move <vol> <pod>`.
- **Stretch:** add the second array (GUI Pods → Arrays +). Data resyncs, and active/active access starts only when the resync finishes and both arrays show `online`.
- **Unstretch (T3):** remove an array from the pod. Purity **refuses if the array being removed still has host connections** to pod volumes, so disconnect them first. The removed array keeps the pod in *Destroyed Pods* for **24 hours**. Re-adding the array within 24h re-stretches it without a full resend. Eradicating the destroyed pod early is T3 and irreversible.
- **ActiveCluster File** (Realms, `purerealm create|add --member|setattr --failover-preference`) needs Purity//FA **6.12.2+**. It uses the same 11 ms budget and the same mediator model.

## ActiveDR

### Model
- A new pod is **promoted** (read/write). A **demoted** pod is read-only. The remote pod must be **demoted** before a replica link can be created.
- Setup, from the Oracle guide:
  1. `purepod create <pod>` on the source
  2. move the volumes into it (`purevol move <vol> <pod>`), with protection groups inside the pod
  3. on the target, `purepod create <pod-dr>` and `purepod demote <pod-dr>`
  4. `purepod replica-link create <pod> --remote-pod <pod-dr> --remote <target-array>` (baselining), and watch the lag

### Promote / demote semantics (T3 except test promotions)
- **Test failover:** promoting the target pod gives read/write volumes at the last replicated point **while replication continues**. Demoting the target afterwards **discards all changes made during the test**.
- **Demoting a target pod after a test:**
  - stop its I/O first (check the pod's performance)
  - **compare volume counts with the source pod**: any volume created in the target pod while it was promoted is **removed** on demote
- **Planned failover:**
  1. stop the apps and unmount
  2. `purepod demote --quiesce <source-pod>` (waits for the remaining data to replicate)
  3. wait until it shows `demoted`
  4. `purepod promote <target-pod>`

  ActiveDR then **reverses the replication direction automatically**.
- **Real failover:**
  1. promote the DR pod
  2. if the source array is still reachable, demote the source pod (preferably with `--quiesce`)

  `--skip-quiesce` discards any not-yet-replicated changes. Use it only when you're certain they aren't needed.
- **Undo protection:** every demote creates an **undo** copy (`.undo-remote` snapshot / undo pod) in the destroyed area for the eradication window (**24h by default**; Everpure support can extend it). It can be copied to a new pod to recover data from just before the demote.

### VMware notes
- VAAI **XCOPY doesn't work across pod boundaries**: Storage vMotion, clone or deploy-from-template between pods becomes host copies, which are slow. Keep templates inside the pod.
- UNMAP is replicated, but reclaim on the target is delayed.
- After a promote, datastores may need resignaturing and RDMs updating. Follow the *ActiveDR with VMware* guide.
