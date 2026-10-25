# Kubernetes upgrades and migration

> **Command verification status:** facts are from kubernetes.io *Version Skew Policy* and *Upgrading kubeadm clusters* (v1.37 docs, retrieved 2026-10-25). `kubectl`/`helm` forms: see the catalogs. Distribution-specific upgrade commands (kubeadm, EKS, AKS, GKE, OpenShift, Rancher…) are `[unverified]` here: use that distribution's documentation for the exact version.

## Version skew rules (Version Skew Policy)
- The project maintains the **three most recent minor releases**; 1.19+ get about 1 year of patch support. Stay on a supported minor.
- HA control plane: the newest and oldest `kube-apiserver` must be **within one minor version**.
- `kube-controller-manager`, `kube-scheduler`, `cloud-controller-manager`: same minor as `kube-apiserver` or one older.
- **`kubelet` must not be newer than `kube-apiserver`**; it may be up to three minors older (two for kubelet < 1.25).
- `kubectl` is supported within one minor version (older or newer) of `kube-apiserver`.
- **Skipping minor versions is unsupported** (kubeadm upgrade page). 1.35 → 1.37 means two upgrades.

## Upgrade order
1. Read the release notes (CHANGELOG) of every minor you cross: removed APIs, feature-gate changes, deprecations. Find manifests and Helm charts using removed API versions **before** the upgrade (`kubectl api-resources` `[doc]` and your GitOps repo; tools that scan for deprecated APIs are optional and `[unverified]` here).
2. Back up: etcd snapshot (distribution procedure), all manifests from Git, and application data (array snapshots via the storage skills). `kubeadm upgrade` "does not touch your workloads", but backups are always a best practice.
3. Upgrade the **first control-plane node**, then the other control-plane nodes, then worker nodes.
4. For a **minor** kubelet upgrade you **must drain the node first**: `kubectl --context <ctx> cordon <node>` then `drain` (T3, PDBs respected), upgrade, `uncordon`. One node (or one small batch within PDB limits) at a time.
5. After each node: nodes `Ready`, pods back, PDBs satisfied, storage attachments healthy (CSI node pods running) before the next node.
6. Upgrade add-ons (CNI, CSI drivers, ingress controllers, CoreDNS) only to versions their vendors support for the new Kubernetes minor. **Check CSI driver support** with the storage vendor before the cluster upgrade.

## Helm release upgrades
- Pin chart versions (`--version`). Read the chart's upgrade notes; CRDs in a chart's `crds/` directory are installed but never upgraded or deleted by Helm (Helm docs: "no support at this time for upgrading or deleting CRDs"); upgrade them by the chart's documented procedure.
- `helm upgrade --dry-run` first; record the current revision (`helm history`) for `helm rollback <release> <revision>`.

## Migration patterns
- **Workload to a new cluster:** stand up the target, sync manifests via GitOps, migrate data with storage replication or backup/restore (Velero or array-level replication: `[unverified]` tool commands), switch traffic by DNS or load balancer, keep the old cluster read-only through the quarantine period.
- **Storage class change:** you can't change a PVC's StorageClass in place. Create a new PVC, copy data (application-level or array clone), switch the workload, keep the old PV with `Retain` until verified.
