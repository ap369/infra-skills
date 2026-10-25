---
name: managing-docker-production
description: Use when inspecting, troubleshooting, building, or changing Docker containers, images, Dockerfiles, Compose stacks, registries or Docker Engine hosts, especially production hosts running critical services - docker run, docker compose, volumes, networks, prune, image security, secrets in builds, container crashes, OOM, disk full, logging, engine upgrades, best practices, configuration audit.
---

# Managing Docker in Production

## Overview
Reading is free; every change is a **change plan** (references/change-gate.md), executed only after the user approves *that plan*. Violating the letter of the gate violates its spirit. **No change is 100% safe:** end every plan with the safety notice. **Never invent commands, flags, endpoints, tools or output:** tag commands `[doc]`/`[help]`/`[unverified]`; plans use only `[doc]`/`[help]`; unread values are `<not read>`.

## Access model
- **Access to the Docker daemon is root on the host** ("only trusted users should be allowed to control your Docker daemon"). Treat the socket, the `docker` group and remote contexts as admin credentials.
- Name the host: `docker --context <ctx>` or `-H`, and read `docker info` (name, version) before every change.
- **Reads:** `ps`, `inspect`, `logs`, `stats --no-stream`, `system df`, `events`, `compose ps/config`. Never print secrets from `inspect` (env vars) or files.
- **Writes:** approved plan steps only, one per step. Production containers should come from Compose files or an orchestrator in Git, not ad-hoc `docker run`.

## Risk tiers
| Tier | Examples | Gate |
|---|---|---|
| T0 read | ps, inspect, logs, stats, system df, image ls, compose ps/config | none |
| T1 additive | pull, build, tag, create a network or volume, start a new container | plan + "approve" |
| T2 modify | restart/stop a service, `compose up -d` with changed config, update resources, image tag change, daemon config change | plan + "approve" per item |
| T3 destructive/disruptive | `rm -f`, `volume rm/prune`, `system prune` (esp. `-a`, `--volumes`), `compose down -v`, `image prune -a`, daemon restart or engine upgrade, registry deletes | plan + typed object name; backup first |

## Narrowest option first
- Disk full: read `system df`, rotate/limit logs, remove named dangling images, then targeted prune with `--filter`; never `prune -a --volumes` on production.
- Broken release: redeploy the previous image digest before rebuilding.

## Key facts
- `docker compose down -v` and `volume prune` delete data volumes.
- The default `json-file` log driver doesn't rotate: logs can fill the disk.
- Live restore survives patch upgrades only, not major ones.
- `ENV`/`ARG` values persist in image layers: use build secrets.

## Rationalizations
| Thought | Reality |
|---|---|
| "I'm sure this flag exists" | Prove it: `[doc]` catalog line or `--help` this session. |
| "Prune only removes unused stuff" | "Unused" includes stopped containers and volumes you still need. |
| "Add -f so it doesn't prompt" | Prompts are part of the gate. |
| "It's just a restart" | Restart drops connections; check health checks and dependants. |
| "User said go" | Approval before the plan approves nothing. |

## References
- change-gate.md: plan template, **required for any change**
- command-verification.md / itsm-and-pam.md: **required**
- docker-command-catalog.md / compose-command-catalog.md / buildx-command-catalog.md: [doc] forms
- docker.md: images, runtime safety, volumes, registries, tiers
- best-practices.md: configuration audit
- health-and-triage.md / incident-comms.md: health, playbooks, updates
- upgrade-checklist.md / upgrades-and-migration.md: engine upgrades, migration
