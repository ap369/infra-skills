# Purity command catalog (documented forms)

The forms below were found in Everpure's **public** documentation (support.everpuredata.com, retrieved 2026-10-13: ActiveCluster, ActiveDR, Directory Services, FlashArray Block best practices, File Services). They are `[doc]`. The **Purity//FA CLI Reference Guide isn't public**, so **every Purity command elsewhere in this skill is `[unverified]`**: run `<command> --help` (or `<command> <subcommand> --help`) on the array first and quote the usage line (command-verification.md).

| Area | Documented form |
|---|---|
| Identity / hardware | `purearray list` · `purearray list --connect` · `purehw list` |
| Admins / directory | `pureadmin list` · `pureds list` · `pureds list --groups` · `pureds role setattr ...` · `pureds setattr --uri ... --base-dn ... --bind-user ... --bind-password` · `pureds test` · `pureds enable [--checkpeer]` |
| Hosts / ports | `pureport list --initiator` · `purehost setattr --personality <p> <host>` · `purehost setattr --preferred-array <array> <host>` |
| Networking | `purenetwork setattr <port> --mtu 9000` · `purenetwork ping --count ...` |
| Array connections | `purearray connect --management-address ... --connection-key` · `purearray list --connection-key` |
| Pods (ActiveCluster / ActiveDR) | `purepod list` · `purepod create <pod>` · `purepod setattr --failover-preference <array> <pod>` · `purepod promote <pod>` · `purepod demote [--quiesce] <pod>` · `purepod replica-link create <pod> --remote-pod <rpod> --remote <array>` |
| Volumes / pgroups | `purevol move <vol> <pod>` · `purevol add --pgroup <pg> <vol>` · `purevol remove --pgroup <pg> <vol>` · `purepgroup create ...` |
| File (6.8.2+) / Realms (6.12.2+) | `purefs create ...` · `puredir create --path ...` · `puredir export ...` · `purepolicy nfs|snapshot|quota|autodir ...` · `purerealm create|list|add --member|setattr --failover-preference` |
| Upgrades | `puresw list [--catalog]` · `puresw check ...` · `puresw download --version ...` · `puresw upgrade ...`: **procedure pages are restricted**, so follow the official guide with a Pure1 login |

`...` means the documentation shows more parameters. Confirm them with `--help`.

## Common `[unverified]` forms in this skill (check before use)
`purevol list --qos`, `purevol list --pending`, `purevol setattr --bw-limit`, `purevol truncate`, `purevol eradicate`, `purevol recover`, `purepgroup retain ...`, `purepgroup schedule ...`, `purepod add|remove --array`, `purepod list --mediator`, `purehost connect|disconnect --vol`, `puremessage list --open`, `purearray list --space|--phonehome|--ntpserver`, `pureadmin list --api-token`, `purefs list ...`, `pureobjbucket list`, and every FlashBlade command. These are probably right for recent Purity versions, but they aren't documented here.
