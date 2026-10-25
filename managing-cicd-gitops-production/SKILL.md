---
name: managing-cicd-gitops-production
description: Use when inspecting, troubleshooting, or changing CI/CD pipelines and GitOps delivery for production - GitHub Actions, GitLab CI, Jenkins, deployment pipelines, environments and approvals, pipeline secrets, OIDC, Argo CD applications, sync, prune, self-heal, rollback, app deletion, Flux kustomizations, HelmReleases, suspend, reconcile, drift, failed deployments, OutOfSync, Degraded, upgrades, best practices, configuration audit.
---

# Managing CI/CD and GitOps in Production

## Overview
Reading is free; every change is a **change plan** (references/change-gate.md), executed only after the user approves *that plan*. Violating the letter of the gate violates its spirit. **No change is 100% safe:** end every plan with the safety notice. **Never invent commands, flags, endpoints, tools or output:** tag commands `[doc]`/`[help]`/`[unverified]`; plans use only `[doc]`/`[help]`; unread values are `<not read>`.

## Access model
- **Git is the change path.** A production change is a reviewed commit/PR to the repo GitOps watches; CLI syncs and pipeline re-runs execute what Git already says.
- **Reads:** `argocd app get/diff/history`, `flux get`, `flux diff`, pipeline logs, with read-only tokens. Never print secrets from pipeline variables or logs.
- Name the target: Argo CD server/context and application; Flux `--context` and namespace.
- **Writes:** approved plan steps only. Pipeline changes (workflow files) are code changes: review them like production code.

## Risk tiers
| Tier | Examples | Gate |
|---|---|---|
| T0 read | app get/diff/history, flux get/diff/events/logs, pipeline logs | none |
| T1 additive | new app or Kustomization with prune off, new pipeline in a non-prod path | plan + "approve" |
| T2 modify | merge a deploy PR, `argocd app sync`, `app rollback`, `flux reconcile`, suspend/resume, sync-policy changes, pipeline or approval rule edits | plan + "approve" per item |
| T3 destructive/disruptive | `sync --prune`, enabling auto-prune, `argocd app delete` (cascade), `flux delete` with prune, removing an app from Git, secret rotation, runner/controller upgrades | plan + typed app name; backup first |

## Narrowest option first
- Bad deploy: Git revert (or `app rollback` / suspend) before deleting anything.
- Fighting GitOps: suspend sync, then fix Git; never hand-edit what the controller reverts.
- Diff first: `argocd app diff` / `flux diff kustomization` before every sync.

## Key facts
- `argocd app delete` cascades by default: the app's Kubernetes resources are deleted too.
- With prune, objects removed from Git are deleted from the cluster.
- Flux deletion follows `prune` unless `deletionPolicy` says otherwise.
- `pull_request_target` with untrusted checkout can take over the repository.

## Rationalizations
| Thought | Reality |
|---|---|
| "I'm sure this flag exists" | Prove it: `[doc]` catalog line or `--help` this session. |
| "Just delete the stuck app and recreate it" | Cascade delete removes the workload and its PVCs. |
| "Enable auto-prune, it keeps things clean" | One bad commit deletes production objects. |
| "Re-run the pipeline, it was flaky" | Read the failure; a re-run may redeploy something else. |
| "User said go" | Approval before the plan approves nothing. |

## References
- change-gate.md: plan template, **required for any change**
- command-verification.md / itsm-and-pam.md: **required**
- argocd-command-catalog.md / flux-command-catalog.md: [doc] forms
- cicd-gitops.md: pipeline security, Argo CD, Flux, rollback, tiers
- best-practices.md: configuration audit
- health-and-triage.md / incident-comms.md: health, playbooks, updates
- upgrade-checklist.md / upgrades-and-migration.md: controller and runner upgrades
