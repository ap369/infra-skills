# Incident communication

Claude drafts the messages. The user (or the incident commander) sends them. Keep facts, guesses and plans clearly separate, and never put credentials, internal IPs or customer data in a broadcast.

## Severity and cadence (defaults; use the site's own if one exists)
| Severity | Example | First notice | Updates |
|---|---|---|---|
| P1 | Production down, data unavailable, writes failing, ransomware suspected | within 15 min | every 30 min |
| P2 | Degraded: redundancy lost, latency high, replication broken | within 30 min | every 2 h |
| P3 | No user impact yet: single component failure, capacity warning | same day | daily |

## Status update template
```
[P1][OPEN] <system> – <one-line impact>            <timestamp, timezone>
Impact:      who/what is affected, since when
Known:       facts with evidence (array, command, time)
Not known:   open questions
Doing now:   current actions, who owns them
Next step:   the next change (with its change-plan ID if any)
Next update: <time>
```

## Resolution note
```
[P1][RESOLVED] <system> – <impact>   start <t0> → end <t1> (duration)
Cause (preliminary):  ...
Fix applied:          change plan <id>, steps ...
Residual risk:        e.g. replication still resyncing, redundancy reduced until RMA
Follow-ups:           owner + date
```

## Timeline log (keep it during the incident)
`<timestamp> | <who> | <action or observation> | <evidence>`. Every command that changes state gets a line, with its plan ID.

## Postmortem inputs (blameless)
- Timeline, from detection to resolution, and how we detected it (alert, user report)
- Root cause, plus contributing factors (config, process, capacity, monitoring gaps)
- What went well, and what slowed us down
- Action items: each with an owner, a date, and the risk tier of the fix (fixes go through the change gate)
- Which best-practice checks (references/best-practices.md) would have caught it
