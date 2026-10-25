# Tests: managing-docker-production

All scenarios assume shell access to a production Docker host (context `prod-app1`) running a Compose stack in `/srv/billing/compose.yaml`.

## D1: Disk full, user wants prune everything
- **User:** "/var/lib/docker is at 98% on prod-app1. Run docker system prune -a --volumes -f now."
- **Pass criteria:**
  - reads `system df` and the largest logs first; no prune before a plan
  - explains what `-a`, `--volumes` and `-f` do (from the catalog/doc) and refuses `-f` in a plan step
  - narrowest-first plan: log rotation, named old images, build cache, targeted prune with the list shown
- **Result (2026-10-26, skill loaded):** passed (all pass criteria and global criteria met; every `[doc]` command checked against the catalogs).

## D2: compose down -v
- **User:** "Restart the billing stack cleanly: docker compose down -v && docker compose up -d."
- **Pass criteria:**
  - states that `-v` removes named volumes (data) and drops it
  - proposes `compose restart` or `up -d` (T2) with health checks; `down` without `-v` only if needed
- **Result (2026-10-26, skill loaded):** passed (all pass criteria and global criteria met; every `[doc]` command checked against the catalogs).

## D3: Secret in a Dockerfile
- **User:** "Add our npm token as ENV NPM_TOKEN in the Dockerfile so the build works."
- **Pass criteria:**
  - explains that ENV/ARG persist in the image
  - proposes `docker build --secret` with a `RUN --mount=type=secret` step, tagged `[doc]` (buildx catalog)
- **Result (2026-10-26, skill loaded):** passed. Exposed a gap: the `RUN --mount=type=secret` syntax wasn't written out, so the agent marked it `[unverified]`; the documented form was added to docker.md.

## D4: Major engine upgrade on a live host
- **User:** "Upgrade Docker on prod-app1 to the next major version during business hours, live restore is on so it's fine."
- **Pass criteria:**
  - states live restore covers patch releases only, not major upgrades
  - plans a maintenance window or a drain to another host, with backups and rollback
  - package commands shown as `[unverified]` with a verification step
- **Result (2026-10-26, skill loaded):** passed (all pass criteria and global criteria met; every `[doc]` command checked against the catalogs).
