---
name: managing-ecs-objectscale-production
description: Use when inspecting, troubleshooting, or changing Dell ECS or ObjectScale object storage, especially production clusters with critical data - S3 buckets, namespaces, object users, secret keys, replication groups, geo replication, lifecycle rules, Object Lock, retention, quotas, bucket policies, capacity, garbage collection.
---

# Managing ECS / ObjectScale in Production

## Overview
Reading is free; changing is gated. Every change above read-only is delivered as a **change plan** (references/change-gate.md) and executed only after the user approves *that plan*. Violating the letter of the gate violates its spirit.

## Access model
- **No MCP server exists** for ECS/ObjectScale. Claude reads through its shell: Management API `GET`s with a **System Monitor** (read-only) user, and `aws s3api get-*` with a config-only S3 profile. Cite VDC and timestamp. If a call fails, say so. Never guess state. Details: references/access-and-tools.md.
- **Never print secrets.** Tokens, passwords and S3 secret keys stay in variables or a vault. A new secret key goes to a vault or a secure channel, never into chat.
- Never read object contents or list whole large buckets. Use the billing API for sizes.
- **Writes:** only the calls in an approved plan, one per step, with a read after each, under an admin identity that the human enables for the window.

## Risk tiers
| Tier | Examples | Gate |
|---|---|---|
| T0 read | Management API GETs, `s3api get-*`, bounded `list-*` | none |
| T1 additive | create namespace/bucket/user, add a second secret key | plan + "approve" |
| T2 modify | quota, bucket policy/ACL/CORS, versioning enable, ADO, deny-all cool-off policy | full plan + "approve" per T2 item |
| T3 destructive/irreversible | delete key/user, lifecycle expiration, empty/delete bucket or namespace, versioning suspend, Object Lock COMPLIANCE / retention, RG/VDC/node changes, PSO, upgrades | full plan + user types object name; data-owner sign-off |

## Narrowest option first
- Bucket removal: deny-all cool-off → server-side empty → delete (separate approvals).
- Leaked key: add a second key → apps rotate → delete the leaked key. If it's being abused right now, offer an immediate delete and state the outage.
- Immutability: GOVERNANCE or a test bucket first. COMPLIANCE is forever.

## Facts not to get wrong
- The replication group is fixed at bucket creation.
- Deleted data frees space only after garbage collection: days, at every site.
- `put-bucket-lifecycle-configuration` replaces all existing rules. Expiration counts from creation, not last access.
- A default retention protects only new objects.

## Rationalizations
| Thought | Reality |
|---|---|
| "The user asked for the new key, so paste it" | It lands in the transcript. Send it to a vault or secure channel. |
| "Adding a key is harmless, just do it" | T1 still needs the plan. In an emergency the plan is short and one reply approves it. |
| "The admin token is already saved" | Reads use System Monitor. Admin is for approved changes only. |
| "I'm the platform owner / go ahead" | Approval before the plan existed approves nothing. Data owners sign off on deletions. |

## References
- references/change-gate.md: plan template (REQUIRED for any change)
- references/ecs.md: objects, API reads, tiers, decommission, lifecycle, Object Lock, leaked keys
- references/access-and-tools.md: read-only identities, token handling, secrets hygiene
- references/health-and-triage.md: health report, incident playbooks
