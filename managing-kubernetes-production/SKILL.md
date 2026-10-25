---
name: managing-kubernetes-production
description: Use when inspecting, troubleshooting, or changing Kubernetes clusters or Helm releases, especially production clusters running critical workloads - kubectl, contexts, namespaces, deployments, statefulsets, nodes, drain, rollouts, rollback, RBAC, network policies, secrets, PVs, PVCs, StorageClasses, CSI, Helm, cluster upgrades, version skew, CrashLoopBackOff, best practices, configuration audit.
---

# Managing Kubernetes in Production

## Overview
Reading is free; every change is a **change plan** (references/change-gate.md), executed only after the user approves *that plan*. Violating the letter of the gate violates its spirit. **No change is 100% safe:** end every plan with the safety notice. **Never invent commands, flags, endpoints, tools or output:** tag commands `[doc]`/`[help]`/`[unverified]`; plans use only `[doc]`/`[help]`; unread values are `<not read>`.

## Access model
- **Name the cluster on every command:** `--context <ctx>` and `-n <ns>`, never the current context. Read the API server URL before the first command and every change.
- **Reads** as a read-only identity (a `view`-style role). `get`/`list`/`watch` on Secrets reveals their contents: never print Secret data.
- **Writes:** approved plan steps only, one per step, admin identity enabled by the human. Prefer GitOps (change the repo) over `kubectl` edits that GitOps will revert.
- `kubectl diff` and `--dry-run=server` before every apply.

## Risk tiers
| Tier | Examples | Gate |
|---|---|---|
| T0 read | get, describe, logs, events, top, diff, `auth can-i`, `helm list/status/get` | none |
| T1 additive | create a namespace, ConfigMap, new Deployment; `helm install` of a new release | plan + "approve" |
| T2 modify | apply/patch, scale, rollout restart/undo, cordon, image or resource changes, `helm upgrade/rollback`, RBAC or NetworkPolicy edits | plan + "approve" per item |
| T3 destructive/disruptive | delete namespace/PVC/PV/StatefulSet/CRD, drain, `--force` deletes, `helm uninstall`, removing finalizers, StorageClass or reclaim policy changes, etcd restore, control-plane or node upgrades | plan + typed object name; backup first |

## Narrowest option first
- Bad rollout: `rollout undo` (or a Git revert under GitOps) before deleting anything.
- Node work: cordon, then drain with PDBs respected; never `--disable-eviction`.
- Storage: set `Retain` on the PV before deleting a PVC whose data matters.

## Key facts
- Deleting a PVC whose PV has reclaim policy `Delete` **deletes the volume on the storage array.**
- Deleting a namespace deletes everything in it, PVCs included.
- `kubelet` must not be newer than `kube-apiserver`. Upgrade one minor version at a time.
- GitOps reverts manual edits.

## Rationalizations
| Thought | Reality |
|---|---|
| "I'm sure this flag exists" | Prove it: `[doc]` catalog line or `--help` this session. |
| "Current context is prod" | Contexts change silently. Name it. |
| "It's only a PVC" | With `Delete` reclaim the array volume goes too. |
| "Drain is stuck, add --disable-eviction" | That bypasses PodDisruptionBudgets. Fix the blocker. |
| "Remove the finalizer to unstick it" | Finalizers guard cleanup (volumes, cloud resources). T3. |
| "User said go" | Approval before the plan approves nothing. |

## References
- change-gate.md: plan template, **required for any change**
- command-verification.md / itsm-and-pam.md: **required**
- kubectl-command-catalog.md / helm-command-catalog.md: [doc] forms
- kubernetes.md: objects, reads, tiers, storage and CSI, RBAC, decommission
- best-practices.md: configuration audit
- health-and-triage.md / incident-comms.md: health, playbooks, updates
- upgrade-checklist.md / upgrades-and-migration.md: cluster upgrades, version skew
