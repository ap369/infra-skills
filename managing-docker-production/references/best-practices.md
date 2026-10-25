# Best practices: configuration audit (Docker)

> **Command verification status:** reads use forms from the catalogs (`[doc]`). Practices come from docs.docker.com (*Building best practices*, *Build secrets*, *Docker Engine security*, *Protect the Docker daemon socket*, *Configure logging drivers*, *Live restore*), retrieved 2026-10-25. Site standards override them.

Every check is read-only (T0). Report: **# | Practice | Current value | Status (OK / GAP / N/A) | Risk | Fix (tier)**, then a prioritized summary.

## Host and daemon
| # | Practice | Why | Check | Fix tier |
|---|---|---|---|---|
| D1 | Only admins can reach the daemon: `docker` group membership reviewed, no TCP socket without TLS, remote access over SSH/TLS | Daemon access = root | group members, `docker info`, daemon config | T2 |
| D2 | No application container mounts `/var/run/docker.sock` | Container → host takeover | `docker inspect` mounts | T2 |
| D3 | `live-restore` enabled where containers must survive daemon restarts | Fewer outages on daemon restarts | `docker info` (Live Restore Enabled) | T2 (daemon reload) |
| D4 | Log rotation: `log-opts` `max-size`/`max-file`, or the `local` driver ("By default, no log-rotation is performed") | Disk exhaustion | `docker info` (Logging Driver), daemon.json | T2 (applies to new containers) |
| D5 | `/var/lib/docker` on its own filesystem with monitoring | Disk full stops all containers | `docker system df`, `df` | plan |
| D6 | Engine on a supported release, patched | Security | `docker version` | T3 |
| D7 | Rootless mode or user namespaces considered for multi-tenant hosts | Blast radius | `docker info` (Security Options) | T3 |

## Images
| # | Practice | Why | Check | Fix tier |
|---|---|---|---|---|
| D8 | Production images referenced by **digest** or immutable tag, never `latest` | Reproducibility, supply chain | Compose files, `inspect` | T2 |
| D9 | Multi-stage builds; minimal base; rebuilt regularly with `--pull` | Size, CVEs | Dockerfiles, image age | T1 |
| D10 | No secrets in `ENV`/`ARG`/layers; build secrets used | Secret leaks through image history | `docker history`, Dockerfiles | T2 |
| D11 | Non-root `USER`, `HEALTHCHECK` (or orchestrator probes) | Escape impact, self-healing | `inspect` Config.User / Healthcheck | T2 |
| D12 | Images scanned and signed in CI before reaching the registry | Supply chain | CI pipeline | T2 |

## Runtime
| # | Practice | Why | Check | Fix tier |
|---|---|---|---|---|
| D13 | No `--privileged`, `--pid host`, broad `--cap-add` without a documented reason | Escape | `inspect` HostConfig | T2 |
| D14 | Memory, CPU and PID limits on every service | One container can starve the host | `inspect`, `stats --no-stream` | T2 |
| D15 | Read-only root filesystem where possible | Tampering | `inspect` ReadonlyRootfs | T2 |
| D16 | Restart policy plus health checks; crash loops alerted | Hidden failures | `inspect`, restart counts | T2 |
| D17 | Data in named volumes or bind mounts that are backed up; no data in container layers | Data loss on recreate | mounts | T2 |
| D18 | All production containers defined in Git (Compose/orchestrator), no hand-made `docker run` | Drift, recovery | compare `ps` with Git | T2 |
