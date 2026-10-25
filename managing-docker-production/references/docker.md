# Docker reference: images, runtime, volumes, changes by tier

> **Command verification status:** Docker CLI forms are checked against docker-command-catalog.md (docker/cli reference, Docker 29.10.0) and compose-command-catalog.md (docker/compose reference, v5.6.1) and buildx-command-catalog.md (docker/buildx reference, v0.38.1: `docker build` is an alias of `docker buildx build`); those forms are `[doc]`. Facts are from docs.docker.com (*Building best practices*, *Build secrets*, *Docker Engine security*, *Live restore*, *Configure logging drivers*, *Protect the Docker daemon socket*), retrieved 2026-10-25.

## Daemon access is root
- "Only trusted users should be allowed to control your Docker daemon": Docker can share any host directory with a container without limits, so daemon access equals root on the host.
- Never mount `/var/run/docker.sock` into application containers. Remote daemons: SSH or TLS only ("By default, Docker runs through a non-networked UNIX socket"). Rootless mode runs the daemon without root privileges.
- Always name the target: `docker --context <ctx> ...` and check `docker --context <ctx> info` before a change.

## Images (build)
- **Multi-stage builds** keep build tools out of the final image.
- **Pin base images**, by digest for full supply-chain integrity ("even if a publisher replaces the tag with a new image"). Rebuild regularly with `docker build --pull` (fresh base) and `--no-cache` for clean dependency updates.
- `.dockerignore` keeps secrets and junk out of the build context.
- **Secrets:** never in `ENV` or `ARG` (they persist in the image and its history). Use build secrets: `docker build --secret id=<id>,src=<file> .` and `RUN --mount=type=secret,...` in the Dockerfile.
- Run as a non-root `USER`; one service per image; a `HEALTHCHECK` (or orchestrator probes).
- Production references use an **immutable tag or digest**, never `latest`.

## Runtime safety (docker run / Compose)
Flags below are in the catalog for `docker container run`/`create` (confirm with `--help` for older engines):
| Concern | Use | Avoid |
|---|---|---|
| Privileges | `--user`, `--cap-drop ALL` + needed `--cap-add`, `--security-opt no-new-privileges` | `--privileged`, `--pid host`, `--network host` (unless required and documented) |
| Filesystem | `--read-only` + `--tmpfs` for scratch | writable root everywhere, bind-mounting `/` or the docker socket |
| Resources | `--memory`, `--cpus`, `--pids-limit` | unlimited memory (one leak takes the host) |
| Restart | `--restart unless-stopped` / `on-failure` with health checks | restart loops hiding crashes |
| Logs | daemon `log-opts` `max-size` / `max-file`, or the `local` driver | default `json-file` with no rotation |

## Volumes and data
- Named volumes and bind mounts hold the data. **`docker compose down -v` removes named volumes declared in the Compose file**, `docker volume rm` / `volume prune` delete volumes, `docker container rm -v` removes anonymous volumes.
- Back up a volume before any T3 step (stop the writer, copy or snapshot the underlying storage).
- `docker system prune` removes all stopped containers, networks not used by a container, dangling images and build cache; **`-a`** removes all unused images; **`--volumes`** removes anonymous volumes; **`-f`** skips the confirmation.

## Reads (T0)
```
docker --context <ctx> info ; docker --context <ctx> version          [doc]
docker --context <ctx> ps -a                                           [doc]
docker --context <ctx> inspect <container>                             [doc]  (don't print env secrets)
docker --context <ctx> logs --since 30m --tail 200 <container>         [doc]
docker --context <ctx> stats --no-stream                               [doc]
docker --context <ctx> system df                                       [doc]
docker --context <ctx> events --since 1h --until 0s                    [doc]
docker --context <ctx> compose -f <file> ps ; ... compose -f <file> config   [doc]
```

## Changes by tier
| Tier | Operation | Form | Rollback |
|---|---|---|---|
| T1 | Pull a pinned image | `docker pull <repo>@sha256:<digest>` | remove the image |
| T2 | Deploy a changed Compose service | `docker compose -f <file> up -d <service>` after `compose config` review | redeploy the previous file/digest |
| T2 | Restart a service | `docker compose -f <file> restart <service>` / `docker restart <container>` | n/a |
| T2 | Change resource limits live | `docker update --memory <m> --cpus <c> <container>` | `update` back |
| T3 | Remove a container | `docker rm <container>` (stop first; no `-f` in plans) | recreate from Compose/Git |
| T3 | Remove volumes / prune | `docker volume rm <name>`; `docker system prune --filter until=<h>` only with the list shown and approved | **none** |
| T3 | Tear down a stack | `docker compose -f <file> down` (**without `-v`** unless data deletion is the approved goal) | `up -d` |
| T3 | Daemon restart / engine upgrade | upgrades-and-migration.md | n/a |
