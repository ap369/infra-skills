# Unity uemcli documented command catalog

> **Command verification status:** every object path and action below appears in Dell's *Dell Unity™ Family Unisphere® Command Line Interface User Guide* **5.5.5** (302-002-578, Rev. A19, September 2026; page numbers refer to that PDF). A form listed here is `[doc]` for Unity OE 5.5.x. Qualifiers (`-name`, `-size`…) are `[doc]` only if they appear in that action's *Format* line in the guide; still confirm on the target with `uemcli -d <mgmt> <object> <action> -help` (older OE releases may lack newer qualifiers). Anything not listed is `[unverified]`.

## Client facts (pp. 22–35)
- Syntax: `uemcli [<switches>] <object> [<object qualifier>] <action> [<action qualifiers>]`. Help: `-help`, `-h` or `-?` after the object or action (`uemcli -d <mgmt> /stor/prov/luns/lun set -?`); `/ -help` lists all object types.
- `show` takes `-detail`, `-brief` or `-filter <value>`, and `-output {nvp | table [-wrap] | csv}`.
- **`-silent` completes a command "without requiring user confirmation".** Never use it for a change step: confirmations are part of the gate (like `-noprompt` on symcli).
- Credentials: `-securePassword` prompts for the password instead of putting it on the command line. `-saveUser` stores credentials in the client's local lockbox: avoid it for admin accounts on shared hosts. Use `-removeUser` / `-removeAllUsers` to clean up.
- Certificates: `-sslPolicy {interactive | reject | accept | store}` (default `interactive`). Don't use `accept` against production; import the array certificate (`-certImport`) or `store` it once after checking the fingerprint.
- `-noHeader` hides the header; `-cmdTime` shows the array's time (useful in evidence); `-enableStdErr` sends errors to stderr.
- Most changes take `-async`. With `-async` the command returns before the work is done: follow the job (`/sys/task/job show`) and read the object back.

## Safety facts from the guide (cite these in plans)
- **`/stor/prov/luns/lun ... set -lunHosts <list>` replaces the whole host list (p. 393):** "This list must include all the hosts that you want to have access to the LUN." A host left out loses access. Use `-addHosts` / `-removeHosts` (incremental) instead; `-removeHosts` is T3.
- **Snapshot restore (pp. 468–469):** "the entire storage resource … is replaced with the contents of the selected snapshot." The system first takes a snapshot of the current state (name it with `-backupName`). Hosts must stop I/O; for LUNs, detach an attached snapshot first and disconnect the LUN on the host.
- **Snapshot delete (p. 469):** "Once you delete a snapshot, you can no longer recover data from it." `-overrideLock` deletes a snapshot locked by an application: never without the owning application's team.
- **LUN / FS / datastore delete:** `-deleteSnapshots {yes | no}` (default `no`). `yes` deletes the snapshots too: say so in the plan.
- **Replication failover (pp. 499–500):** run on the **destination** for an emergency, "with possible data loss"; it "terminate[s] the transfer of data if there is a transfer in progress". A **planned** failover runs on the **source** with `-sync yes` (no data loss). Failback: `failback`. `resume -forceFullCopy` forces a full synchronization of an **asynchronous** session (not for synchronous block replication); DR is unprotected until it completes.
- **Pool extend (p. 313):** needs `-diskGroup <value> -drivesNumber <value>` (or `-disk` for traditional pools). Drives added to a pool can't be removed.
- **Real-time metrics (p. 583):** `/metrics/value/rt -path <value> show -interval <value>`; list valid paths with `/metrics/metric show`.
- **Software upgrade (p. 47):** `/sys/upgrade create -type software [-candId <value>] [-pauseBeforeReboot]`; `/sys/upgrade show | resume | cancel`. Upload the candidate first with `uemcli -upload -f <file> upgrade`. `/sys/general healthcheck` (p. 39): "Before upgrading the system software, a system health check must be performed."

## Corrections (forms that are NOT in the guide)
| Don't use | Use instead |
|---|---|
| `/remote/initiator -id X delete` | No `delete` action exists for `/remote/initiator` (only `create`, `show`, `set`, p. 250–252). Remove access per LUN or host (`-removeHosts`, `/remote/host ... set -removeLuns`), or ask Dell support. |
| `/sys/soft/upgrade` | `/sys/upgrade create -type software` (p. 47). `/sys/soft/ver` lists versions/candidates. |
| `/stor/config/pool ... extend -drivesNumber N` alone | add `-diskGroup <value>` (p. 313) |
| `/metrics/value/rt -path ... show` | add `-interval <value>` (p. 583) |
| `set -lunHosts` to add or remove one host | `set -addHosts` / `set -removeHosts` |

## All documented object paths and actions
Tier: `show` = T0, `create` = T1, `set`/`extend`/`pause`/`resume`/`sync`/`attach`/`refresh`… = T2 or more (read the qualifiers), `delete`/`restore`/`failover`/`failback`/`detach`/`shrink`/service actions = T3. Note: `refresh` on `/stor/prov/luns/lun`, `/stor/prov/luns/group` or `/stor/prov/vmware/vmfs` applies to **thin clones** and replaces the clone's data with the source snapshot's (p. 395): T3 for whoever uses the clone. `/prot/snap ... refresh` (p. 466) refreshes the snapshot itself, so its old point in time is gone unless `-copyName` keeps a copy ("If this switch is not specified, no copy is created"): T3, always pass `-copyName`.

| Object | Actions (page) |
|---|---|
| `/env/bat` | `show` p.290 |
| `/env/dae` | `show` p.294 |
| `/env/disk` | `show` p.287, `rescan` p.289, `set` p.289 |
| `/env/dpe` | `show` p.295 |
| `/env/fan` | `show` p.298 |
| `/env/iomodule` | `commit` p.301, `show` p.301 |
| `/env/lcc` | `show` p.292 |
| `/env/mm` | `show` p.296 |
| `/env/ps` | `show` p.291 |
| `/env/sp` | `show` p.285 |
| `/env/ssc` | `show` p.298 |
| `/env/ssd` | `show` p.293 |
| `/event/alert/conf` | `show` p.555, `set` p.555, `testEmailAlert` p.559 |
| `/event/alert/conf/emailto` | `create` p.557, `set` p.557, `show` p.558, `delete` p.559 |
| `/event/alert/hist` | `show` p.551, `ack` p.552, `delete` p.553, `deactivate` p.553 |
| `/event/alert/snmp` | `create` p.560, `show` p.562, `set` p.562, `delete` p.563 |
| `/event/log` | `show` p.550 |
| `/import/session` | `show` p.513 |
| `/import/session/block` | `create` p.515, `set` p.516, `cutover` p.517, `cancel` p.518, `show` p.518 |
| `/import/session/element` | `show` p.532 |
| `/import/session/generic` | `create` p.535, `show` p.536, `set` p.537, `pause` p.538, `resume` p.539, `cancel` p.540, `restart` p.540, `delete` p.541 |
| `/import/session/nas` | `create` p.521, `set` p.526, `cutover` p.527, `commit` p.529, `cancel` p.529, `show` p.531 |
| `/metrics/metric` | `show` p.575 |
| `/metrics/service` | `show` p.573, `set` p.574 |
| `/metrics/value/hist` | `show` p.578 |
| `/metrics/value/rt` | `show` p.583 |
| `/move/session` | `create` p.544, `show` p.545, `set` p.546, `delete` p.547, `cancel` p.547 |
| `/net/dns/config` | `set` p.203, `show` p.203 |
| `/net/fsn` | `create` p.199, `show` p.199, `set` p.200, `delete` p.201 |
| `/net/if` | `create` p.186, `show` p.187, `set` p.188, `delete` p.189 |
| `/net/if/mgmt` | `show` p.183, `set` p.184 |
| `/net/iscsi/config` | `show` p.172, `set` p.172 |
| `/net/iscsi/isns` | `create` p.170, `show` p.170, `delete` p.170, `set` p.171 |
| `/net/iscsi/node` | `show` p.174, `set` p.174 |
| `/net/iscsi/reversechap` | `set` p.168, `show` p.169 |
| `/net/la` | `create` p.195, `show` p.195, `set` p.196, `delete` p.197 |
| `/net/ldap` | `create` p.215, `show` p.217, `set` p.218, `verify` p.220, `refresh` p.220, `delete` p.221 |
| `/net/nas/cava` | `show` p.157, `set` p.157 |
| `/net/nas/cifs` | `create` p.148, `show` p.149, `set` p.150, `delete` p.151 |
| `/net/nas/dhsm` | `show` p.223, `set` p.223 |
| `/net/nas/dhsmconn` | `create` p.225, `show` p.226, `modify` p.227, `delete` p.229 |
| `/net/nas/dns` | `show` p.203, `set` p.204 |
| `/net/nas/event/config` | `show` p.159, `set` p.159 |
| `/net/nas/event/pool` | `create` p.163, `show` p.163, `set` p.164, `delete` p.165 |
| `/net/nas/ftp` | `show` p.122, `set` p.123 |
| `/net/nas/if` | `create` p.132, `show` p.134, `set` p.135, `delete` p.136 |
| `/net/nas/kerberos` | `set` p.141, `show` p.142 |
| `/net/nas/ldap` | `show` p.127, `set` p.128 |
| `/net/nas/ndmp` | `show` p.212, `set` p.213 |
| `/net/nas/nfs` | `create` p.152, `show` p.153, `set` p.154, `delete` p.155 |
| `/net/nas/nis` | `show` p.208, `set` p.209 |
| `/net/nas/route` | `create` p.138, `set` p.138, `show` p.139, `delete` p.140 |
| `/net/nas/server` | `create` p.111, `show` p.113, `set` p.114, `delete` p.118, `update` p.119 |
| `/net/nas/vmwarepe` | `create` p.166, `show` p.166, `delete` p.167 |
| `/net/ntp/server` | `create` p.205, `show` p.206, `set` p.207, `delete` p.207 |
| `/net/port/eth` | `show` p.176, `set` p.177 |
| `/net/port/fc` | `show` p.180, `set` p.180 |
| `/net/port/sas` | `show` p.178 |
| `/net/port/unc` | `show` p.182 |
| `/net/route` | `create` p.190, `show` p.191, `set` p.192, `delete` p.193 |
| `/net/smtp` | `show` p.210, `set` p.211 |
| `/net/tbn` | `show` p.230 |
| `/net/tbn/config` | `show` p.231, `set` p.231 |
| `/net/tenant` | `create` p.144, `show` p.145, `set` p.146, `delete` p.147 |
| `/net/util` | `ping` p.221, `traceroute` p.222 |
| `/net/vlan` | `show` p.143 |
| `/prot/encrypt` | `show` p.506, `set` p.507 |
| `/prot/encrypt/kmip` | `show` p.508, `set` p.508, `verify` p.509 |
| `/prot/rep/session` | `create` p.488, `show` p.492, `set` p.493, `pause` p.495, `resume` p.496, `sync` p.497, `delete` p.498, `failover` p.499, `failback` p.500, `preserveAsync` p.501 |
| `/prot/rep/session/commonbase` | `show` p.542 |
| `/prot/snap` | `create` p.461, `show` p.463, `attach` p.464, `refresh` p.466, `replicate` p.466, `detach` p.468, `restore` p.468, `delete` p.469, `copy` p.470, `set` p.471 |
| `/prot/snap/cifs` | `create` p.479, `show` p.480, `set` p.481, `delete` p.482 |
| `/prot/snap/nfs` | `create` p.473, `show` p.475, `set` p.475, `delete` p.477 |
| `/quota/config` | `set` p.367, `show` p.369 |
| `/quota/tree` | `create` p.362, `show` p.363, `set` p.363, `refresh` p.364, `delete` p.365 |
| `/quota/user` | `create` p.357, `show` p.358, `set` p.359, `refresh` p.360 |
| `/remote/host` | `create` p.235, `show` p.237, `set` p.238, `delete` p.239 |
| `/remote/host/hlu` | `show` p.240, `set` p.241 |
| `/remote/hostgroup` | `create` p.242, `show` p.244, `set` p.244, `delete` p.246 |
| `/remote/hostgroup/hglu` | `show` p.247 |
| `/remote/initiator` | `create` p.250, `show` p.251, `set` p.252 |
| `/remote/initiator/path` | `show` p.254 |
| `/remote/iscsi/chap` | `create` p.255, `show` p.256, `set` p.257, `delete` p.258 |
| `/remote/iscsi/connection` | `create` p.258, `show` p.259, `set` p.259, `delete` p.260 |
| `/remote/iscsi/connection/path` | `create` p.261, `show` p.262, `delete` p.263 |
| `/remote/rpa/chap` | `show` p.504, `set` p.505 |
| `/remote/sys` | `create` p.265, `verify` p.266, `show` p.267, `set` p.268, `delete` p.269, `failover` p.270, `pause` p.270, `resume` p.271 |
| `/service/sp` | `service` p.571, `reboot` p.571, `reimage` p.572 |
| `/service/ssh` | `set` p.570, `show` p.570 |
| `/service/system` | `restart` p.566, `shutdown` p.566, `reinit` p.567, `collect` p.567 |
| `/service/system/dump` | `show` p.568, `delete` p.569 |
| `/service/system/serviceInfo` | `show` p.569 |
| `/service/user` | `set` p.565 |
| `/stor/config/auto` | `set` p.304, `show` p.305 |
| `/stor/config/cp` | `create` p.447, `show` p.448, `set` p.448, `delete` p.449 |
| `/stor/config/dg` | `show` p.336, `recom` p.338 |
| `/stor/config/fastcache` | `create` p.329, `show` p.330, `extend` p.330, `shrink` p.331, `delete` p.332 |
| `/stor/config/fastcache/so` | `show` p.333 |
| `/stor/config/fastvp` | `set` p.327, `show` p.328 |
| `/stor/config/iolimit` | `create` p.451, `delete` p.453, `set` p.454, `show` p.456 |
| `/stor/config/iolimit/config` | `show` p.457, `set` p.457 |
| `/stor/config/pool` | `create` p.308, `set` p.312, `extend` p.313, `show` p.315, `delete` p.317 |
| `/stor/config/pool/fastvp` | `set` p.320, `show` p.321, `start` p.321, `stop` p.322 |
| `/stor/config/pool/sr` | `show` p.325 |
| `/stor/config/pool/tier` | `show` p.323 |
| `/stor/config/profile` | `show` p.334 |
| `/stor/general/system` | `show` p.339 |
| `/stor/general/tier` | `show` p.340 |
| `/stor/prov/fs` | `create` p.347, `show` p.350, `set` p.351, `delete` p.355 |
| `/stor/prov/fs/cifs` | `create` p.380, `show` p.382, `set` p.382, `delete` p.384 |
| `/stor/prov/fs/nfs` | `create` p.372, `show` p.375, `set` p.375, `delete` p.378 |
| `/stor/prov/luns/group` | `create` p.399, `show` p.400, `set` p.401, `delete` p.404, `refresh` p.405 |
| `/stor/prov/luns/lun` | `create` p.387, `show` p.390, `set` p.391, `delete` p.395, `refresh` p.395 |
| `/stor/prov/vmware/nfs` | `create` p.410, `show` p.414, `set` p.415, `delete` p.418 |
| `/stor/prov/vmware/pe` | `show` p.432, `set` p.432 |
| `/stor/prov/vmware/vmfs` | `create` p.422, `show` p.425, `set` p.426, `delete` p.429, `refresh` p.430 |
| `/stor/prov/vmware/vvol` | `show` p.441, `delete` p.442, `createSnap` p.443, `restore` p.444 |
| `/stor/prov/vmware/vvolds` | `create` p.434, `show` p.435, `set` p.436, `delete` p.438 |
| `/stor/prov/vmware/vvolds/alloc` | `show` p.439 |
| `/sys/cert` | `show` p.90, `delete` p.91 |
| `/sys/eula` | `show` p.83, `set` p.83 |
| `/sys/general` | `show` p.37, `set` p.38, `failback` p.39, `healthcheck` p.39 |
| `/sys/info` | `show` p.40, `set` p.41 |
| `/sys/lic` | `show` p.82 |
| `/sys/limits` | `show` p.81 |
| `/sys/rlog` | `create` p.85, `show` p.86, `set` p.87, `verify` p.88, `delete` p.89 |
| `/sys/schedtimezone` | `show` p.55, `set` p.55 |
| `/sys/security` | `show` p.51, `set` p.51 |
| `/sys/soft/ver` | `show` p.42, `prepare` p.43, `delete` p.45 |
| `/sys/support/account` | `show` p.79, `set` p.79, `delete` p.80 |
| `/sys/support/config` | `show` p.57, `set` p.57 |
| `/sys/support/connecthome` | `show` p.68, `set` p.69, `test` p.69 |
| `/sys/support/connectivityservices` | `show` p.63, `initialize` p.64, `checkNetwork` p.65, `set` p.66, `testcallhome` p.67 |
| `/sys/support/esrsc` | `show` p.59, `set` p.59, `checkNetwork` p.60, `test` p.61 |
| `/sys/task/job` | `show` p.103, `resume` p.103, `cancel` p.104, `delete` p.105 |
| `/sys/task/job/step` | `show` p.106 |
| `/sys/task/rule` | `create` p.94, `show` p.97, `set` p.99, `delete` p.101 |
| `/sys/task/sched` | `show` p.92, `delete` p.93 |
| `/sys/time` | `show` p.53, `set` p.54 |
| `/sys/upgrade` | `create` p.47, `show` p.48, `resume` p.49, `cancel` p.50 |
| `/user/account` | `create` p.71, `show` p.72, `set` p.73, `delete` p.74 |
| `/user/account/settings` | `set` p.76, `show` p.78 |
| `/user/role` | `show` p.70 |
| `/virt/vmw/esx` | `create` p.277, `set` p.278, `delete` p.279, `show` p.279, `discover` p.280, `refresh` p.280 |
| `/virt/vmw/vc` | `create` p.273, `set` p.274, `delete` p.275, `show` p.275, `refresh` p.276 |
| `/virt/vmw/vm` | `show` p.281 |
| `/virt/vmw/vmdevice` | `show` p.282 |