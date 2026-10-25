# Kubernetes reference: objects, reads, changes by tier

> **Command verification status:** `kubectl` and `helm` forms here are checked against the official references in kubectl-command-catalog.md (kubernetes.io, v1.37) and helm-command-catalog.md (helm.sh, Helm 3); those forms are `[doc]`. Facts are from kubernetes.io concept pages (*Persistent Volumes*, *Disruptions*, *Version Skew Policy*, *RBAC Good Practices*), retrieved 2026-10-25. Resource fields: confirm with `kubectl explain` on the target (`[help]`).

## Always
- Every command carries `--context <ctx>` (global kubectl flag) and `-n <namespace>` (or `-A` for reads only).
- Before a change: `kubectl --context <ctx> diff -f <file>` `[doc]` and `kubectl --context <ctx> apply -f <file> --dry-run=server` `[doc]`.
- Record the current state to a file named after the ticket before changing it: `kubectl --context <ctx> -n <ns> get <kind>/<name> -o yaml > CHG123-before.yaml` `[doc]`.

## Objects and their traps
| Object | What can go wrong |
|---|---|
| Namespace | Deleting it deletes every object inside, PVCs included |
| Deployment / ReplicaSet | A new template rolls pods; bad image or probe = outage. `rollout undo` reverts to the previous revision. |
| StatefulSet | Ordered, sticky identity and volumes (volumeClaimTemplates). Scaling down doesn't delete PVCs, but deleting PVCs loses data. |
| DaemonSet | Runs on every (matching) node: a bad change hits all nodes at once |
| Service / Ingress / Gateway | Selector or port changes drop traffic immediately |
| PodDisruptionBudget | Limits voluntary disruptions; drain respects it unless eviction is bypassed |
| PersistentVolumeClaim / PersistentVolume | **Reclaim policy decides the array volume's fate** (below) |
| StorageClass | Dynamically provisioned PVs inherit its reclaim policy |
| Secret | `get`, `list` and `watch` all reveal contents |
| CRD | Deleting a CRD deletes **all** its custom resources cluster-wide |
| Finalizers | Block deletion until a controller cleans up external resources. Removing them by hand can leak or orphan volumes, load balancers, DNS records. |

## Storage and CSI (the link to the storage skills)
- **`Delete` reclaim policy:** "deletion removes both the PersistentVolume object from Kubernetes, as well as the associated storage asset in the external infrastructure." Dynamically provisioned volumes inherit the StorageClass reclaim policy (usually `Delete`).
- **`Retain`:** when the PVC is deleted the PV stays "released" with its data; an administrator reclaims it manually.
- **Storage Object in Use Protection:** a PVC in use by a pod, or a PV bound to a PVC, isn't removed while in use: deletion waits (`Terminating`). Don't force it.
- Before deleting a PVC that holds data: read the bound PV's reclaim policy (`kubectl get pv <pv> -o jsonpath='{.spec.persistentVolumeReclaimPolicy}'` `[doc]`), switch it to `Retain` (T2), take an array snapshot through the storage skill, then delete (T3).
- CSI drivers map PVs to array objects (NetApp Trident, Pure Portworx, Dell CSM for PowerMax / Unity…). Find the array volume behind a PV in `spec.csi.volumeHandle` and check it with the matching storage skill before any T3 storage step. Driver-specific commands and parameters are `[unverified]` here: use the driver's own documentation.
- PVC expansion works only if the StorageClass allows volume expansion; shrinking isn't supported.

## Reads (T0)
```
kubectl --context <ctx> get nodes -o wide                                   [doc]
kubectl --context <ctx> get pods -A --field-selector=status.phase!=Running  [doc]
kubectl --context <ctx> -n <ns> describe pod <pod>                          [doc]
kubectl --context <ctx> -n <ns> logs <pod> -c <container> --previous        [doc]
kubectl --context <ctx> events -n <ns>                                      [doc]
kubectl --context <ctx> top nodes ; kubectl --context <ctx> top pods -n <ns>  [doc]
kubectl --context <ctx> -n <ns> rollout status deployment/<name>            [doc]
kubectl --context <ctx> -n <ns> rollout history deployment/<name>           [doc]
kubectl --context <ctx> auth can-i --list                                   [doc]
kubectl --context <ctx> get pv,pvc -A ; kubectl --context <ctx> get storageclass  [doc]
helm --kube-context <ctx> -n <ns> list ; helm --kube-context <ctx> -n <ns> status <release> ; helm --kube-context <ctx> -n <ns> history <release>  [doc]
```

## Changes by tier
| Tier | Operation | Form | Rollback |
|---|---|---|---|
| T2 | Apply a reviewed manifest | `kubectl --context <ctx> apply -f <file>` after `diff` and `--dry-run=server` | apply the saved `-before.yaml` |
| T2 | Restart pods of a Deployment | `kubectl --context <ctx> -n <ns> rollout restart deployment/<name>` | n/a (watch `rollout status`) |
| T2 | Roll back a Deployment | `kubectl --context <ctx> -n <ns> rollout undo deployment/<name> [--to-revision=<n>]` | `rollout undo` again |
| T2 | Scale | `kubectl --context <ctx> -n <ns> scale deployment/<name> --replicas=<n> --current-replicas=<m>` (`--current-replicas` makes it fail if someone changed it) | scale back |
| T2 | Cordon / uncordon a node | `kubectl --context <ctx> cordon <node>` / `uncordon <node>` | uncordon |
| T2 | Helm upgrade | `helm --kube-context <ctx> -n <ns> upgrade <release> <chart> --version <v> -f values.yaml` after a `--dry-run` review | `helm rollback <release> <revision>` |
| T3 | Drain a node | `kubectl --context <ctx> drain <node> --ignore-daemonsets --delete-emptydir-data` only if emptyDir data loss is accepted; **never `--disable-eviction`** ("bypass checking PodDisruptionBudgets") | uncordon |
| T3 | Delete a namespace / PVC / StatefulSet / CRD | `kubectl --context <ctx> delete <kind> <name> -n <ns>`; never `--force --grace-period=0` on StatefulSet pods without understanding the storage | **none** for data |
| T3 | Helm uninstall | `helm --kube-context <ctx> -n <ns> uninstall <release>` (`--keep-history` keeps the record) | reinstall; data in deleted PVCs is gone |
| T3 | Remove a finalizer | patch only with the owning controller's documented procedure | n/a |

`kubectl delete` options to watch: `--all`, `-A`/`--all-namespaces`, `--selector` and `--field-selector` widen the blast radius; list the exact objects (`get` with the same selector) and get them approved first.

## RBAC (RBAC Good Practices)
- Use least privilege. Admins shouldn't use `cluster-admin` day to day; prefer a low-privilege account with impersonation rights.
- **Never add users to `system:masters`**: it "bypasses all RBAC rights checks" and can't be revoked by removing bindings.
- `get`/`list`/`watch` on Secrets reveal them; `escalate`, `bind` and `impersonate` verbs, CSR approval and pod creation in privileged namespaces are privilege-escalation paths.
- Set `automountServiceAccountToken: false` where pods don't call the API.
- Check effective rights with `kubectl auth can-i --list --as=<user>` `[doc]` (impersonation needs rights).

## Decommission pattern (namespace or application)
1. Read: all objects, PVCs and their PVs (reclaim policy, `volumeHandle`), ingress/DNS, external dependencies, GitOps ownership.
2. Step 0: export manifests (`get -o yaml`), set data PVs to `Retain`, array snapshots via the storage skill.
3. Stage 1 (T2, reversible): scale to 0 / suspend GitOps sync; keep objects.
4. Quarantine: default 7 days.
5. Stage 2 (T3, separate approval, name typed): delete the namespace or release; then release the retained PVs and array volumes through the storage skill.
