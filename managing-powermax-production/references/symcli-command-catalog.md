# symcli command catalog (documented forms)

Every form below was found in Dell's public **Solutions Enabler 10.4.0** user guides (SRDF Family CLI, Array Controls and Management CLI, State Tables) or the **TimeFinder SnapVX 10.0.0 CLI User Guide**, retrieved and checked 2026-10-25. These forms are `[doc]`. Anything not listed here, **including extra options added to a listed command**, is `[unverified]`: confirm it with `<command> -h` on the management host first (command-verification.md). Add `-sid <SID>` to everything.

| Area | Documented form |
|---|---|
| Identity / health | `symcfg list [-v]` |
| Identity / health | `symcfg -sid S list -v` |
| Identity / health | `symcfg -sid S list -srp -detail` |
| Identity / health | `symcfg -sid S list -dir all -v` |
| Identity / health | `symcfg -sid S list -rdfg all` |
| Identity / health | `symcfg -sid S list -tdev -gb` |
| Identity / health | `symevent list -sid S -start <time>` |
| Identity / health | `symdisk list -sid S [-v | -state ... | -dskgrp_summary]` |
| Identity / health | `symaudit ... list` |
| Storage groups | `symsg -sid S list` |
| Storage groups | `symsg show <SG> -sid S` |
| Storage groups | `symsg -sid S -sg SG add dev <dev>` |
| Storage groups | `symsg -sg SG -sid S set -bw_max <MBps|NOLIMIT> / -iops_max <IOps|NOLIMIT>` |
| Storage groups | `symsg -sg SG -sid S -sl <SL> [-wl <workload>]  (service level; confirm exact verb with symsg -h)` |
| Storage groups | `symsg create <SG> -nocompression ; compression is set/removed with `symsg set` (exact flag: check symsg -h)` |
| Devices | `symdev list -sid S -sg SG / symdev show <dev> -sid S` |
| Devices | `symdev create -sid S -tdev -cap N -captype gb|tb -N k` |
| Devices | `symdev -sid S free -devs <range> -all   (device unmapped or Not Ready; blocked in replication)` |
| Masking | `symaccess -sid S list view [-detail] / show view <MV> -detail` |
| Masking | `symaccess -sid S list logins` |
| Masking | `symaccess -sid S create -name <G> -type initiator|port|storage` |
| Masking | `symaccess -sid S -name <IG> -type initiator remove -wwn <wwn>` |
| Masking | `symaccess -sid S delete view -name <MV>` |
| SnapVX | `symsnapvx -sid S -sg SG -name <snap> establish [-ttl -delta <days>] [-secure ...]` |
| SnapVX | `symsnapvx list -sid S -dev <dev> -detail / symsnapvx -sid S -sg SG list` |
| SnapVX | `symsnapvx -sid S -sg SG -snapshot_name <snap> -gen <n> restore` |
| SnapVX | `symsnapvx -sid S -sg SG -lnsg <TGT_SG> -snapshot_name <snap> link [-copy]` |
| SnapVX | `symsnapvx ... terminate` |
| SRDF | `symrdf -g DG query [-rdfa]` |
| SRDF | `symrdf -g DG establish  (incremental)` |
| SRDF | `symrdf -g DG establish -full   (initial sync / R2 drive replacement only)` |
| SRDF | `symrdf -g DG resume / suspend / split` |
| SRDF | `symrdf -g DG enable / disable   (SRDF/A consistency)` |
| SRDF | `symrdf -cg CG verify -consistent [-noinvalids] [-i 60]` |
| SRDF | `symrdf -g DG verify -activeactive | -activebias` |
| SRDF | `symrdf -sid S -rdfg N activate -rdfa_wpace / deactivate -rdfa_wpace` |
| SRDF | `symrdf -sid S -rdfg N set rdfa_pace [-wp_autostart on|off] ...` |
| SRDF | `symrdf -g DG write_disable r1|r2 / rw_enable r1|r2` |
| Config | `symconfigure -sid S -file <f> preview | commit` |
| Licensing (SE 10.4) | `symlmf register|deregister -sid S` |
| Metro DR (SE 10.4) | `symmdr -sid S -name ENV modify -add|-remove ... -metro_rdfg ... -dr_rdfg ... -cascaded|-concurrent` |
| Masking | `symaccess backup` / `symaccess restore` exist. Exact flags aren't in the guides used, so check `symaccess -h`. |

## Known `[unverified]` or wrong forms (don't use as written)
| Form | Status |
|---|---|
| `symsg ... set -slo` | wrong: the documented option is `-sl` |
| `symdisk list -failed` | not documented: use `symdisk list -sid S -v` / `-state` |
| `symdev list -noport` | not documented |
| `symsg -sg SG set -compression` | not documented as written: compression is set or removed with `symsg set`, so check `symsg -h` for the flag |
| `symstat ...`, `symgate list` | real commands, documented only in the online CLI Reference (developer.dell.com). Check `-h`. |
