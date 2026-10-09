# Health check and incident triage

## Health check (T0)
Report each item as a row: **Check | Value | Status (OK/WARN/CRIT) | Source + timestamp**.

| # | Check | Source | WARN | CRIT |
|---|---|---|---|---|
| 1 | Alerts | `/vdc/alerts` (unacknowledged) | warnings | errors / critical |
| 2 | Nodes / disks | `/dashboard/zones/localzone/nodes`, disk status | 1 node or disk down | multiple nodes down, or a whole rack |
| 3 | Capacity per storage pool | `/dashboard/zones/localzone`, `/object/capacity` | ≥ 75% | ≥ 85% (ECS needs headroom for erasure coding, GC and rebalancing) |
| 4 | Geo replication / RPO | replication group dashboard | RPO > 2× normal | replication stalled, site unreachable |
| 5 | Garbage collection | capacity "reclaimable" / GC backlog metrics | growing backlog | GC stalled |
| 6 | Quotas | namespace and bucket quotas vs. usage | > 85% of a hard quota | at the hard quota (writes blocked) |
| 7 | Certificates | management and data certificate expiry | < 30 days | expired |
| 8 | Version / support | `/vdc/nodes` software version | not on the target release | unsupported |

Thresholds are defaults. If the user or a site runbook gives different values, use those. End with **Findings**, ordered by severity, each with one recommended next step and its tier.

## Triage playbooks
Order for every incident: scope → read → hypothesis with evidence → smallest reversible fix (gated, emergency path) → verify → timeline notes.

- **Capacity critical:**
  1. Find the top namespaces and buckets (billing).
  2. Check the GC backlog. Space may already be on its way back.
  3. Check quotas.

  Relief, ranked by safety:
  1. Ask the bucket owners to delete their own data.
  2. Scoped lifecycle rules (T3, prefix/tag, dry-run count).
  3. Capacity add (Dell).

  Never empty or delete buckets on the platform side "to make room" without the owner's named approval.
- **Leaked secret key:** follow "Leaked secret key: the safe pattern" in ecs.md.
- **App gets 403 / AccessDenied:** check the user's keys (expired?), bucket policy and ACL changes, the namespace and bucket owner, and the clock skew of the client's signature. Look at recent policy edits in the audit/event log.
- **App gets 503 / SlowDown / timeouts:** load balancer and node health, a site outage (ADO setting?), capacity, a rebalancing or recovery in progress.
- **Site outage (geo):** read the RG status, ADO settings and RPO. A failover or PSO decision follows the Dell-led DR runbook. Claude prepares the checklist and reads the state.
