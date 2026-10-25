# Kubernetes health checks and incident triage

> **Command verification status:** `kubectl` forms are `[doc]` per kubectl-command-catalog.md (v1.37). Thresholds are this skill's defaults: site standards override them.

## Health check (T0)
| # | Check | Read | Warning | Critical |
|---|---|---|---|---|
| 1 | Nodes | `kubectl --context <ctx> get nodes` | any `SchedulingDisabled` unexplained | any `NotReady` |
| 2 | Pods not running | `kubectl --context <ctx> get pods -A --field-selector=status.phase!=Running` | Pending > 5 min | CrashLoopBackOff on a critical app |
| 3 | Restarts | `kubectl --context <ctx> get pods -A` (RESTARTS column) | rising | OOMKilled repeatedly |
| 4 | Node pressure | `kubectl --context <ctx> describe node <n>` (Conditions) | MemoryPressure / DiskPressure | PIDPressure, evictions |
| 5 | Capacity | `kubectl --context <ctx> top nodes` | > 80% CPU or memory | > 90% |
| 6 | Storage | `kubectl --context <ctx> get pvc -A` | Pending PVCs | PVs `Failed` / `Released` unexpectedly |
| 7 | Events | `kubectl --context <ctx> events -A` | FailedScheduling, BackOff | FailedMount, FailedAttachVolume |
| 8 | Rollouts | `kubectl --context <ctx> -n <ns> rollout status deployment/<d>` | progressing slowly | stuck / exceeded deadline |

## Playbooks (read first, change through the gate)
### CrashLoopBackOff
1. `kubectl --context <ctx> -n <ns> logs <pod> -c <container> --previous` `[doc]`, `describe pod` (exit code, last state, probes).
2. Exit 137 / `OOMKilled` → memory limit too low or leak. Exit 1/2 → app error or bad config. Probe failures → probe too aggressive or dependency down.
3. If it started with a rollout: `rollout undo` (T2) is the narrowest fix. Don't delete pods in a loop.

### ImagePullBackOff
`describe pod` → wrong tag/digest, registry auth (imagePullSecrets), registry down, rate limits. Fix the reference in Git; don't switch to `:latest`.

### Pending pods
`describe pod` → Insufficient CPU/memory, taints/tolerations, node affinity, PVC unbound (StorageClass, CSI driver, array capacity: check the storage skill), quota.

### Node NotReady
`describe node`: kubelet stopped, network, disk pressure, certificate expiry. Pods there are evicted after the toleration timeout. Don't drain a NotReady node without understanding StatefulSet volume attachments (RWO volumes may stay attached to the dead node; the CSI driver and storage skill decide when it's safe to force-detach).

### FailedMount / FailedAttachVolume
Usually CSI or array side: CSI controller/node pod logs, VolumeAttachment objects, the array (host access, LUN mapping, capacity). Use the matching storage skill. Never delete the VolumeAttachment or PV to "unstick" it without the storage owner.

### DNS failures
CoreDNS pods and logs in `kube-system`, Service/Endpoints for the target, NetworkPolicies blocking UDP/TCP 53.

### API server slow or unreachable
Control-plane node health, etcd health and disk latency (distribution tooling), admission webhooks timing out (a failing webhook can block all creates). Avoid mass `get -A -o yaml` loops during an incident: they add load.

## Communication
Use incident-comms.md. Name the cluster (context and API URL), namespace and workload in every update.
