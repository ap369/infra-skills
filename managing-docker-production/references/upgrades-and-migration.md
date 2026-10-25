# Docker Engine upgrades and migration

> **Command verification status:** facts from docs.docker.com *Live restore* and the CLI references (catalogs). Package-manager commands for the engine (apt, dnf…) are `[unverified]` here: use Docker's install docs for your OS.

## Engine upgrades
- **Live restore keeps containers running across daemon updates only for patch releases** (`YY.MM.x`), "not for major (`YY.MM`) daemon upgrades". If you skip releases, the daemon may not reconnect to running containers and you must stop them manually.
- So: patch upgrades with live restore can be in place; **major upgrades need a maintenance window** where containers restart (T3), or drain the host first (move services to another host / node).
- Before: record `docker version`, `docker info`, `docker ps -a`, Compose files and daemon config; back up volumes; read the release notes (removed features, storage driver changes).
- One host at a time; health-check services after each host.
- Compose v1 (`docker-compose`, Python) is replaced by the `docker compose` plugin: scripts using the old binary need checking.

## Base-image refresh (routine)
Rebuild with `docker build --pull` (and `--no-cache` for dependency updates), scan, push a new digest, deploy as a normal T2 change with the previous digest as rollback.

## Migration
- **Host to host:** recreate from Git (Compose), copy volumes (stop the writer, archive or storage snapshot), switch DNS/LB, keep the old host stopped (not deleted) for the quarantine.
- **Compose to Kubernetes:** see managing-kubernetes-production. Map volumes to PVCs with a deliberate reclaim policy before cut-over.
