# Change plan template

Every change above T0 is delivered as this document, filled in completely. Nothing gets executed until the user has approved this exact plan, whether the executor is an MCP write tool, the CLI, or a human. If any value changes after approval (target, size, snapshot, direction), the plan is re-issued and re-approved.

```markdown
## Change plan: <one-line summary>
**Cluster(s)/SVM:** <cluster> / <svm> (ONTAP <version>)   **Tier:** T1 | T2 | T3   **Ticket:** <id or "none — user to supply">
**Requested by:** <user>   **Window:** <now | date/time, business impact>
**Executor:** ONTAP MCP write tools | CLI by human | BlueXP/Grid Manager by human

### 1. Current state (evidence)
| Check | Value | Source + timestamp |
|---|---|---|
| object identity (name + UUID) / size / used | ... | ontap_get ... |
| who uses it (NFS clients, CIFS sessions, LUN maps, I/O) | ... | |
| protection (snapshots, policy, SnapMirror both directions, ARP/SnapLock) | ... | |
| dependencies (FlexClones, junction children, peers) | ... | |
| capacity (volume, aggregate, destination) | ... | |
| HA / cluster health | ... | |
Settings this plan changes, recorded verbatim for rollback: <...>

### 2. Options considered
The narrowest option that meets the goal comes first. Examples: file restore before volume revert, FlexClone before SnapMirror break, grow before snapshot delete. Say why the chosen option was picked.

### 3. Impact
What changes, who is affected (clients, hosts, DR/RPO), worst case if a step goes wrong.

### 4. Steps (one change per step)
| # | MCP tool call / command (exact args, UUIDs, no wildcards) | Expected result | Rollback |
|---|---|---|---|
| 0 | safety snapshot: `create_snapshot` / `volume snapshot create -snapshot <ticket>` | snapshot listed | n/a |
| 1 | ... | ... | ... |

### 5. Post-checks
Reads that prove the change worked and nothing else changed (LUN state and maps, client access, SnapMirror health, latency).

### 6. Approval
T1/T2: "Reply **approve** to execute steps 0–N."
T3:    "Reply with the object name(s) exactly — `<name>` — to approve the irreversible/disruptive step(s)."
```

## Rules for filling it in
- **Approval is scoped to this plan.** "Go ahead", "do it now", "whatever it takes", "I approve", or a title ("I'm the infra manager") said *before* the plan existed approves nothing. It tells you the user wants speed, so make the plan short. It doesn't let you skip it.
- **One request, many changes:** split by tier. T1 items can share one approval. Each T2/T3 item gets its own approval line.
- **Bulk operations:** list every object by name and UUID. The approval names the list. Execute one object at a time, with a read after each, and stop at the first surprise.
- **Executing with MCP write tools:** call one tool per step. Read the result (and `ontap_get` the object) before the next step. On an unexpected result, stop and report. Don't improvise a fix.
- **Emergency path (P1):** the same sections in terse form. Sections 1–3 can be 5 lines total. Approval still comes before execution. The plan text *is* the change record.
- **T3 extras:**
  - a second person or change board, if the site has one
  - never purge the recovery queue as part of the same approval as the delete
  - for SnapMirror, state the **direction** explicitly in every step (source → destination)
