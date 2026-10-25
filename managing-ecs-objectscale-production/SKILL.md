---
name: managing-ecs-objectscale-production
description: Use when inspecting, troubleshooting, or changing Dell ECS or ObjectScale object storage, especially production clusters with critical data - S3 buckets, namespaces, object users, secret keys, replication groups, geo replication, lifecycle rules, Object Lock, retention, quotas, bucket policies, capacity, garbage collection, upgrades, migration, best practices, configuration audit.
---

# Managing ECS / ObjectScale in Production

## Overview
Reading is free; every change is a **change plan** (references/change-gate.md), executed only after the user approves *that plan*. Violating the letter of the gate violates its spirit. **No change is 100% safe:** end every plan with the safety notice. **Never invent commands, flags, endpoints, tools or output:** tag commands `[doc]`/`[help]`/`[unverified]`; plans use only `[doc]`/`[help]`; unread values are `<not read>`.

## Access model
- **No MCP server exists.** Read via shell: Management API `GET`s as a **System Monitor** user, and `aws s3api get-*` with a config-only profile. Cite VDC and timestamp; never guess.
- **Never print secrets.** Tokens, passwords and keys stay in variables or a vault, never in chat.
- Never read objects or list whole buckets; use the billing API.
- **Writes:** approved plan calls only, one per step, admin identity enabled by the human.

## Risk tiers
| Tier | Examples | Gate |
|---|---|---|
| T0 read | Management API GETs, `s3api get-*`, bounded `list-*` | none |
| T1 additive | create namespace/bucket/user, add a second secret key | plan + "approve" |
| T2 modify | quota, bucket policy/ACL/CORS, versioning enable, ADO, deny-all cool-off | plan + "approve" per item |
| T3 destructive/irreversible | delete key/user, lifecycle expiration, empty/delete bucket or namespace, versioning suspend, Object Lock COMPLIANCE/retention, RG/VDC/node changes, PSO, upgrades | plan + typed object name; data-owner sign-off |

## Narrowest option first
- Bucket removal: deny-all cool-off → server-side empty → delete (separate approvals).
- Leaked key: second key → apps rotate → delete leaked key (immediate delete if actively abused; state the outage).
- Immutability: GOVERNANCE or a test bucket first; COMPLIANCE is permanent.

## Key facts
- A bucket's replication group is fixed; replication groups can't be deleted. At 90% a pool stops taking writes.
- Deleted data frees space only after garbage collection: days, at every site.
- `put-bucket-lifecycle-configuration` replaces all rules; expiration counts from creation.
- A default retention protects only new objects.

## Rationalizations
| Thought | Reality |
|---|---|
| "I'm sure this command/flag exists" | Prove it: `[doc]` or help output this session. Otherwise `[unverified]`, never a plan step. |
| "User asked for the new key, so paste it" | It lands in the transcript. Vault or secure channel. |
| "Adding a key is harmless, just do it" | T1 still needs the plan; in an emergency one reply approves it. |
| "The admin token is already saved" | Reads use System Monitor. |
| "I'm the platform owner / go ahead" | Approval before the plan approves nothing; data owners sign deletions. |

## References
- change-gate.md: plan template, **required for any change**
- command-verification.md: source tags, **required**
- best-practices.md / objectscale-dell-best-practices.md: audit
- ecs.md: objects, API reads, tiers, decommission, lifecycle, Object Lock, leaked keys
- access-and-tools.md: read-only identities, tokens, secrets
- health-and-triage.md / incident-comms.md: health, playbooks, status updates
- upgrade-checklist.md / upgrades-and-migration.md: upgrades, migration
