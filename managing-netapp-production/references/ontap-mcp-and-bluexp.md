# ONTAP MCP server, BlueXP and monitoring tools

## ONTAP MCP server (github.com/NetApp/ontap-mcp)
- Official NetApp server, distributed as a container: `ghcr.io/netapp/ontap-mcp:latest`. It runs as an HTTP MCP server on port 8083.
- Clusters are listed in `ontap.yaml` under `Pollers:`. Each one has `addr`, `username`, and either `password` or `credentials_script`. Set `use_insecure_tls` to false in production.
- **It exposes write tools by default:**
  - `create_*`
  - `modify_*` in the default `multiplex` mode
  - `update_*` / `delete_*` in `legacy` mode
  - `restore_snapshot`
  - `create_cluster_peer` / `delete_cluster_peer`
- Every tool is annotated with `readOnlyHint`, `destructiveHint` and `idempotentHint`.
- **`--read-only`** registers only the read-only tools. These are the discovery tools: `ontap_get`, `list_ontap_endpoints`, `search_ontap_endpoints`, `describe_ontap_endpoint`, `list_registered_clusters` and `list_qos_policies`.

### Recommended production setup (two layers)
1. **Default instance:** started with `--read-only` **and** connected as an ONTAP user with a read-only role (`security login role create ... -access readonly`, application `http`). Two independent locks, so a server bug or a tool mis-annotation can't write.
2. **Optional change instance** (separate port and config): a least-privilege role scoped to the SVMs that change. Start it only for an approved change window, then stop it.

```bash
# read-only instance
docker run -d --name ontap-mcp-ro -p 127.0.0.1:8083:8083 \
  -v ~/.config/ontap-mcp/ontap.yaml:/opt/mcp/ontap.yaml:ro \
  ghcr.io/netapp/ontap-mcp:latest start --port 8083 --host 0.0.0.0 --read-only

# register (Claude Code)
claude mcp add --transport http ontap-mcp http://127.0.0.1:8083
```
Publishing to `127.0.0.1` keeps the server off the network. Put a reverse proxy with auth (or the server's `McpAuth` OAuth config) in front of it before exposing it any further.

### Using it
1. At session start, list the ONTAP MCP tools (Claude Code: ToolSearch "ontap"; other agents: the tool list). Call `list_registered_clusters`. Note whether any non-read-only tools are present. **If write tools are present, every call to one of them goes through the change gate**, exactly as a CLI command would.
2. For reads, use `ontap_get` with `fields=` to keep responses small. Use `search_ontap_endpoints` / `describe_ontap_endpoint` to find the right endpoint rather than guessing.
3. Cite the cluster and timestamp for every value. If the server fails, say so and give read-only CLI commands. Never guess state.
4. A tool's `destructiveHint=false` doesn't mean it's safe in production. `modify_export_policy_rule` isn't flagged destructive, but it can cut off every NFS client.

### Credential hygiene
- `ontap.yaml` gets mode 600 and is never committed. Prefer `credentials_script` (vault lookup) over a plaintext `password`.
- Never paste credentials into chat, plans or tickets.

## BlueXP (NetApp Console), Digital Advisor, monitoring
- **BlueXP / NetApp Console:** SaaS control plane covering working environments, Cloud Volumes ONTAP, backup and recovery, ransomware protection, and classification. BlueXP actions are changes too (T1–T3, by effect).
- **Active IQ Digital Advisor:** wellness/risk findings, firmware and ONTAP upgrade advisories, capacity forecasts. Read-only and safe to cite.
- **Active IQ Unified Manager (AIQUM):** on-prem monitoring with performance events, capacity trends and an event history.
- **Data Infrastructure Insights** (formerly Cloud Insights): fleet observability.
- Harvest + Grafana (open source, NetApp): if present, it's the best source for latency/IOPS history.
- Put AutoSupport case numbers in change and incident records.
