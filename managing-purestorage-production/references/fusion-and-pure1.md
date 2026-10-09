# Pure Fusion MCP Server & Pure1

## Pure Fusion MCP Server
- An open-source, stateless binary (macOS, Linux, Windows). Run it on an admin workstation or jump host. It sits on top of the FlashArray and FlashBlade REST APIs.
- **Read-only by design (initial release):**
  - fleet and array status
  - inventory
  - configuration discovery
  - telemetry
  - workloads
  - performance metrics
- **Auth:** API tokens generated on each array. Use a dedicated **read-only** user, for example `purecli-ro` with the `readonly` role. A built-in config command validates the tokens, detects API versions and writes the config.
- **Source:** github.com/purestorage-openconnect. Check the README for the current tool list and the config format.

Example registration in Claude Code (adjust the binary path and config):
```
claude mcp add pure-fusion -- /opt/pure/pure-fusion-mcp --config ~/.config/pure-fusion/config.yaml
```

### Using it
1. At session start, list the available `mcp__pure-fusion__*` tools (use ToolSearch, keyword "pure fusion"). Map them to the operations in SKILL.md: fleet status, array space, volumes, hosts and connections, pgroups, pods, alerts, performance.
2. Always say which array, and the time, each data point came from.
3. If a tool fails or no tools are available, report it. Then give the equivalent read-only CLI or REST command for the user to run. **Never fill gaps with assumed values.**
4. Even if a future version adds write tools, they are still subject to the change gate. A tool existing doesn't authorize using it.

### Token hygiene
- Keep tokens in the MCP config file (mode 600) or in a secrets manager. Never put them in chat, plans or git.
- Prefer read-only roles. Generate any write-capable token separately, outside this workflow.

## Fusion concepts
- **Fleet:** arrays joined into one control plane.
- **Availability zones / regions:** placement domains.
- **Storage classes and presets:** templates for workloads (size, QoS, protection).
- **Workloads:** instantiated presets (a set of volumes, file systems and policies).

Changes to presets ripple to every workload created from them. Treat them as T2 at minimum.

## Pure1
- SaaS monitoring at pure1.purestorage.com. Pure1 API: `https://api.pure1.purestorage.com/api/1.latest`, authenticated with a JWT signed by an RSA key pair.
- Useful reads:
  - `/arrays`
  - `/alerts`
  - `/metrics/history` (capacity and performance)
  - `/volumes`
  - `/pods`
  - `/subscriptions`
  - Pure1 Meta forecasts: capacity runway and load
- Pure1 Meta workload planner: run a "what-if" before moving workloads or adding capacity.
- Open support cases from Pure1. Proactive Pure Support (phone-home) case numbers belong in change and incident records.
