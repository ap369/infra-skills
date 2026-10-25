# Docker health checks and incident triage

> **Command verification status:** forms are `[doc]` per the catalogs (Docker 29.10.0, Compose v5.6.1). Thresholds are defaults: site standards override them.

## Health check (T0)
| # | Check | Read | Warning | Critical |
|---|---|---|---|---|
| 1 | Daemon | `docker --context <ctx> info` | warnings in output | daemon unreachable |
| 2 | Containers | `docker --context <ctx> ps -a` | `Restarting`, `unhealthy` | critical service `Exited` |
| 3 | Disk | `docker --context <ctx> system df` and host `df` | > 80% | > 90% |
| 4 | Resources | `docker --context <ctx> stats --no-stream` | memory near limit | OOM kills (exit 137) |
| 5 | Events | `docker --context <ctx> events --since 1h --until 0s` | frequent `die`/`restart` | `oom` events |

## Playbooks
### Container keeps restarting / exited
1. `docker logs --tail 200 <c>` `[doc]`, `docker inspect <c>` (State: ExitCode, OOMKilled, Health).
2. Exit 137 with `OOMKilled: true` → raise the memory limit or fix the leak (T2). Exit 1 → app/config error: compare with the last good image digest.
3. Roll back by redeploying the previous digest (T2). Don't delete and recreate volumes.

### Disk full on /var/lib/docker
1. Read: `docker system df` (images, containers, volumes, build cache) and the largest container logs.
2. Narrowest first: log rotation (D4), remove **named** old images not used by any container, `docker builder prune` for build cache with a filter, then a targeted `system prune --filter until=<h>`, each with the list approved.
3. **Never** `system prune -a --volumes -f` on production: it removes all unused images and anonymous volumes without asking.

### Image pull failures
Registry auth (`docker login` context), rate limits, DNS/proxy, digest no longer present. Keep a mirror or pull-through cache for production.

### Daemon down
Containers stop with the daemon unless live restore is on. Check the system service and logs (host tools, `[unverified]` here), disk space and the daemon config file syntax before restarting. A daemon restart is T3.

## Communication
Use incident-comms.md. Name the host/context and the services affected.
