---
name: managing-observability-production
description: Use when inspecting, troubleshooting, or changing production monitoring and alerting - Prometheus, PromQL, alert rules, recording rules, Alertmanager silences and routes, amtool, promtool, Grafana dashboards, Icinga 2 checks, downtimes, acknowledgements, Icinga API, Dynatrace problems, metrics, settings, maintenance windows, API tokens, Monaco configuration as code, alert fatigue, missing alerts, best practices, configuration audit.
---

# Managing Observability in Production

## Overview
Reading is free; every change is a **change plan** (references/change-gate.md), executed only after the user approves *that plan*. Violating the letter of the gate violates its spirit. **No change is 100% safe:** end every plan with the safety notice. **Never invent commands, flags, endpoints, tools or output:** tag commands `[doc]`/`[help]`/`[unverified]`; plans use only `[doc]`/`[help]`; unread values are `<not read>`.

## Access model
- **Monitoring is a safety system.** Silencing, downtiming or deleting an alert hides the next incident: those are changes, never "just reads".
- **Reads:** PromQL queries, `/api/v1/*` GETs, `amtool ... query`, Icinga API `GET /v1/objects/*` with a read-only ApiUser, Dynatrace API v2 GETs with `*.read`-scoped tokens. Never print tokens or passwords.
- **TLS verified on every call:** never `curl -k` (the Icinga docs examples use it; production must not).
- **Writes:** approved plan steps only; config changes validated first (`promtool check`, `icinga2 daemon -C`, Dynatrace `validateOnly`, `monaco deploy --dry-run`).

## Risk tiers
| Tier | Examples | Gate |
|---|---|---|
| T0 read | queries, rule/target/alert status, silence/downtime listing, Dynatrace GETs, config validation | none |
| T1 additive | new alert rule, dashboard, check, notification test | plan + "approve" |
| T2 modify | silences, downtimes, acknowledgements, rule/threshold/routing changes, config reloads, Dynatrace settings changes, `monaco deploy` | plan + "approve" per item; scope, expiry and owner stated |
| T3 destructive | TSDB `delete_series`, `/-/quit`, deleting checks/objects (`cascade`), `monaco purge`/`delete`, Dynatrace settings DELETE, token revocation, monitoring server upgrades | plan + typed name; backup first |

## Narrowest option first
- Silence or downtime **one** alert/host for a **fixed, short** time with an author and comment, never a wildcard or open-ended one.
- Fix a noisy alert's threshold or `for` duration rather than silencing it for weeks.

## Key facts
- An Icinga action `filter` can match many objects: query with the same filter first.
- TSDB delete and Dynatrace settings DELETE can't be undone.
- `monaco purge` deletes ALL configurations in the manifest's environments.
- Prometheus `/-/reload` and admin APIs need `--web.enable-lifecycle` / `--web.enable-admin-api`.

## Rationalizations
| Thought | Reality |
|---|---|
| "I'm sure this flag/endpoint exists" | Prove it: `[doc]` catalog line or help this session. |
| "Silence it, it's noise" | Read why it fires; silence narrowly with an expiry. |
| "curl -k is fine internally" | It disables certificate checks: tokens can be stolen. |
| "Downtime the whole hostgroup for the change" | Show the matched objects; downtime only what the change touches. |
| "User said go" | Approval before the plan approves nothing. |

## References
- change-gate.md: plan template, **required for any change**
- command-verification.md: source tags, **required**
- promtool-command-catalog.md / icinga2-command-catalog.md / monaco-command-catalog.md: [doc] forms
- prometheus.md / icinga.md / dynatrace.md: APIs, safe changes, tiers
- best-practices.md: configuration audit
- health-and-triage.md / incident-comms.md: health, playbooks, updates
- upgrade-checklist.md / upgrades-and-migration.md: upgrades, migration
