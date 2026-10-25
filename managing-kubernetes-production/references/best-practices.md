# Best practices: configuration audit (Kubernetes)

> **Command verification status:** reads use `kubectl`/`helm` forms from the catalogs (`[doc]`). Practices come from kubernetes.io (*RBAC Good Practices*, *Disruptions*, *Persistent Volumes*, *Version Skew Policy*, *Good practices for Kubernetes Secrets*) and common production standards; site standards override them.

Every check is read-only (T0). Each finding names the fix and its tier, and the fix goes through change-gate.md. Report: **# | Practice | Current value | Status (OK / GAP / N/A) | Risk | Fix (tier)**, then a prioritized summary.

## Availability
| # | Practice | Why | Check | Fix tier |
|---|---|---|---|---|
| K1 | Critical Deployments have ≥ 2 replicas spread across nodes/zones (anti-affinity or topology spread) | Node loss | `get deploy -A`, pod placement | T2 |
| K2 | A **PodDisruptionBudget** for every replicated critical app, not set to 0 allowed disruptions permanently | Safe drains | `get pdb -A` | T2 |
| K3 | Readiness and liveness probes on every serving container; liveness not stricter than readiness | Bad probes cause restarts/outages | pod spec | T2 |
| K4 | CPU/memory **requests** on all pods, memory **limits** on all pods | Scheduling, OOM blast radius | pod spec, `top` | T2 |
| K5 | Control plane HA (≥ 3 etcd members) and etcd backups tested | Cluster loss | distribution tooling | T3 |

## Storage
| # | Practice | Why | Check | Fix tier |
|---|---|---|---|---|
| K6 | StorageClasses for production data use **`Retain`**, or every `Delete` class is documented and backed up | PVC delete removes the array volume | `get storageclass -o yaml` | T2 (new class) |
| K7 | Array snapshots or backups exist for every stateful PVC, with restore tested | Data loss | storage skill | T2 |
| K8 | CSI driver version supported for the cluster minor and the array firmware | Attach/mount failures after upgrades | driver pods, vendor matrix | T3 |
| K9 | `allowVolumeExpansion` set deliberately | Capacity emergencies | storage class | T2 |

## Security
| # | Practice | Why | Check | Fix tier |
|---|---|---|---|---|
| K10 | No routine use of `cluster-admin`; nobody in `system:masters` | Unrevocable superuser | `get clusterrolebindings` | T2 |
| K11 | Secret `get/list/watch` granted only where needed | Secret disclosure | `auth can-i --list --as=...` | T2 |
| K12 | Pods run as non-root, no privileged containers, no hostPath/hostNetwork except system DaemonSets (Pod Security Standards *restricted* or *baseline* enforced per namespace) | Container escape | namespace labels, pod specs | T2 |
| K13 | NetworkPolicies: default deny per namespace plus explicit allows | Lateral movement | `get networkpolicy -A` | T2 |
| K14 | `automountServiceAccountToken: false` where the API isn't used | Token theft | pod/SA spec | T2 |
| K15 | Secrets encrypted at rest (API server config) and sourced from an external secret manager where available | Secret exposure | distribution config | T3 |
| K16 | Images pinned by digest or immutable tag, pulled from trusted registries | Supply chain | pod specs | T2 |

## Operations
| # | Practice | Why | Check | Fix tier |
|---|---|---|---|---|
| K17 | Cluster on a supported minor (three newest), components within skew | Security fixes, support | `kubectl version` | T3 |
| K18 | All production changes through GitOps or CI; manual drift detected | Auditability | Argo CD / Flux status | T2 |
| K19 | Resource quotas and LimitRanges per tenant namespace | Noisy neighbours | `get resourcequota -A` | T2 |
| K20 | Logging, metrics and alerting cover nodes, control plane, PVC capacity and certificate expiry | Detection | observability skill | T2 |
