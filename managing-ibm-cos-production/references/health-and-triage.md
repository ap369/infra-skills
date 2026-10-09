# Health check and incident triage

## Health check (T0)
Report each item as a row: **Check | Value | Status (OK/WARN/CRIT) | Source + timestamp**.

| # | Check | Source (Manager) | WARN | CRIT |
|---|---|---|---|---|
| 1 | Open events / alerts | event and incident views | warnings | critical |
| 2 | Devices per set | device states | any device offline or degraded | **margin ≤ 1** for any vault on the set (available − write threshold) |
| 3 | Drives | drive states per Slicestor | failed or flapping drive | several in one set |
| 4 | Rebuilder | rebuild backlog per set | backlog growing | backlog not draining |
| 5 | Vault health | slices available vs. IDA per vault | below width | below the write threshold (writes failing) / read threshold (unavailable) |
| 6 | Storage pool capacity | usage per pool | ≥ 80% | ≥ 90% |
| 7 | Quotas | vault soft/hard quota vs. usage | soft quota exceeded | at the hard quota |
| 8 | Accessers | access pool members online, error rates | one Accesser down | pool degraded |
| 9 | Mirrors | mirror status | lagging | broken |
| 10 | ClevOS versions | per device and Manager | mixed versions outside an upgrade | unsupported |
| 11 | Certificates | Manager and Accesser certificates | < 30 days | expired |

Thresholds are defaults. If the user or a site runbook gives different values, use those. End with **Findings**, ordered by severity, each with one recommended next step and its tier.

## Triage playbooks
Order for every incident: scope → read → hypothesis with evidence → smallest reversible fix (gated, emergency path) → verify → timeline notes.

- **Noisy or failing drives / Slicestor:**
  1. Read the set's device states and do the IDA margin math for every vault on that set.
  2. Find which drives are alerting.
  3. Fix at the drive level first, all gated:
     - acknowledge or mute the drive's alerts **for a set time** (T1, tell the user that muting can hide a second failure)
     - mark the drive failed (T2)
     - open a drive RMA

  Never take a Slicestor offline or remove it to stop alerts while the margin is ≤ 1 (for example, another device in the set is already down).
- **Writes failing on a vault (503 / errors):**
  1. Vault health: is it below the write threshold?
  2. Which devices in the set are down, and why?
  3. Bring back the device that is fastest to recover (T2).
  4. Check the hard quota and pool capacity.
  5. Check the Accessers.
- **Reads failing / data unavailable:** fewer devices than the read threshold, so this is a P1. Engage IBM support immediately. Don't run rebuild or removal actions without them.
- **App gets 403:** check the access key (deleted or disabled?), the vault ACL/policy, recent Manager changes (audit log), and the client's clock skew.
- **Capacity:** find the top vaults by usage. Relief, ranked by safety:
  1. Owners delete their own data.
  2. Lifecycle expiration, prefix-scoped (T3).
  3. Storage pool expansion (IBM).

  Never delete vaults on the platform side without the owner's named approval.
