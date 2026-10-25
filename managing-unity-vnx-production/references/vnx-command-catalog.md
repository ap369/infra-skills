# VNX Block naviseccli documented command catalog

> **Command verification status:** every command below appears in *EMC VNX Series Version 5.33 Command Line Interface Reference for Block* (P/N 300-015-135 Rev. 08, March 2020; page numbers refer to that PDF). A command listed here is `[doc]` for VNX Block OE 5.32/5.33; switches are `[doc]` only where the reference's SYNTAX shows them. Confirm on the target with `naviseccli -h <SP> <command> -help`. **VNX File commands (`nas_*`, `server_*`, `fs_*`) are not covered** (the File CLI reference isn't publicly downloadable): they stay `[unverified]`.

## Client facts (pp. 18–21)
- `naviseccli [-h <SP address>] [-user <u> -password <p> -scope 0|1|2] [-secfilepath <dir>] [-timeout <s>] [-xml] <CMD> [switches]`. `-scope 0` = global, `1` = local, `2` = LDAP.
- `-AddUserSecurity` stores credentials in a security file (use `-secfilepath` for a protected location) so passwords stay off the command line; `-RemoveUserSecurity` removes them. Create it for a **read-only** account for reads.
- Many commands act only on LUNs **owned by the SP named with `-h`** (e.g. `unbind`, `trespass`): send the command to the right SP.

## Safety facts from the reference (cite these in plans)
- **`-o` "Executes the command without prompting for confirmation"** (on `lun -destroy`, `unbind`, `snap -destroy`, `storagepool -destroy`, `mirror ... -fractureimage/-promoteimage`, `rebootSP`, `shutdownsp`…). **Never use `-o` in a change step**: the prompt is part of the gate.
- **`unbind` "destroys all data on the LUN"** (p. 186). `lun -destroy` (pool LUNs) likewise: T3, no undo.
- **`trespass [all | lun <n> | mine]`** (p. 186): "If trespass is executed while I/O processes are active, I/O errors may occur." `mine` takes back all LUNs whose default owner is that SP; prefer `lun <n>` for a single LUN and never `all` on production without a plan.
- **`storagegroup -removehlu -gname <sg> -hlu <n>`** removes the host LUN from the storage group: the host loses it at once (T3). Record HLU/ALU pairs (`storagegroup -list -gname <sg> -host`) first.
- **`snap -restore -id <snap> [-bakName <name>]`** (p. 628, VNX Snapshots) rolls the LUN back; always pass `-bakName` so a backup snapshot of the current state is taken.
- **`mirror -async|-sync -promoteimage`** makes the secondary the primary; `-fractureimage` stops replication. DR operations (T3).
- `rebootSP [-both]`, `rebootpeerSP`, `shutdownsp`, `ndu -install/-commit/-revert`: Dell-support procedures (T3).
- `lun -list` owner switches (p. 342): **`-owner`** = SP that currently owns the LUN, **`-default`** = default owner, `-alowner` = allocation owner, `-at` = auto-trespass.

## Corrections
| Don't use | Use instead |
|---|---|
| `lun -list -curowner` | `lun -list -owner -default` (`-owner` is the *current* owner) |
| any `-o` on a change | omit `-o` and answer the prompt |

## All documented Block commands (page)
Tier guide: `-list`/`-info`/`get*`/`-status` = T0; `-create`/`-add*`/`bind`/`snap -create` = T1; `-modify`/`-expand`/`-set*`/`-change*`/`trespass`/`-syncimage` = T2+; `-destroy`/`-remove*`/`unbind`/`-restore`/`-promote*`/`-fracture*`/reboot/shutdown/`ndu` = T3.

| Command | Page |
|---|---|
| `naviseccli` | 18 |
| `alpa -get` | 24 |
| `alpa -set` | 25 |
| `arraycommpath` | 26 |
| `arrayconfig -capture` | 27 |
| `arrayconfig -duplicate` | 28 |
| `arrayname` | 29 |
| `backendbus -analyze` | 30 |
| `backendbus -get -connstate` | 33 |
| `backendbus -get -physical` | 33 |
| `backendbus -get -prominfo` | 34 |
| `backendbus -get -sfpstate` | 35 |
| `backendbus -get -speeds` | 36 |
| `backendbus -get -all` | 36 |
| `backendbus -resetspeed` | 39 |
| `baseuuid` | 40 |
| `bind` | 41 |
| `cachecard -list` | 45 |
| `cachecard -initialize` | 46 |
| `cache -sp -info` | 47 |
| `cache -sp -modify` | 48 |
| `chglun` | 49 |
| `chgrg` | 51 |
| `clearlog` | 52 |
| `clearstats` | 52 |
| `cmdtime` | 53 |
| `copytodisk` | 53 |
| `createrg` | 55 |
| `emconfiguration` | 56 |
| `environment` | 57 |
| `failovermode` | 59 |
| `faults -list` | 60 |
| `flash -ioport` | 61 |
| `flash -iomodule` | 63 |
| `flashleds` | 64 |
| `getagent` | 64 |
| `getall` | 67 |
| `getarrayuid` | 70 |
| `getconfig` | 71 |
| `getcontrol` | 72 |
| `getcrus` | 74 |
| `getdisk` | 78 |
| `getlog` | 85 |
| `getloop` | 86 |
| `getlun` | 87 |
| `getresume` | 94 |
| `getrg` | 97 |
| `getsniffer` | 100 |
| `getsp` | 102 |
| `getsptime` | 104 |
| `getspuptime` | 104 |
| `getunusedluns` | 105 |
| `hotsparepolicy -list` | 105 |
| `hotsparepolicy -set` | 106 |
| `inserttestevent` | 107 |
| `ioportconfig -config -maxvlans` | 107 |
| `ioportconfig -list` | 108 |
| `ioportconfig -list -maxvlans` | 115 |
| `ioportconfig -persist` | 116 |
| `luncache -clear` | 116 |
| `luncache -list` | 117 |
| `managedby` | 118 |
| `managefiles -delete` | 118 |
| `managefiles -list` | 119 |
| `managefiles -retrieve` | 120 |
| `ndu -list` | 121 |
| `ndu -install` | 122 |
| `ndu -runrules` | 125 |
| `ndu -commit` | 126 |
| `ndu -status` | 127 |
| `ndu -revert` | 127 |
| `networkadmin -get` | 128 |
| `networkadmin -mib` | 132 |
| `networkadmin -route` | 133 |
| `networkadmin -set` | 135 |
| `port` | 138 |
| `powersaving` | 149 |
| `rebootSP` | 150 |
| `rebootpeerSP` | 151 |
| `remoteconfig -getconfig` | 151 |
| `remoteconfig -setconfig` | 153 |
| `removerg` | 154 |
| `resetandhold` | 155 |
| `responsetest` | 155 |
| `sc_off` | 157 |
| `setfeature` | 158 |
| `setsniffer` | 159 |
| `setsniffverify` | 160 |
| `setspstime` | 161 |
| `setsptime` | 161 |
| `setstats` | 162 |
| `shutdown` | 163 |
| `shutdownsp` | 164 |
| `shutdownpeersp` | 165 |
| `spcollect -info` | 165 |
| `spcollect -set` | 166 |
| `spcollect` | 166 |
| `spportspeed` | 167 |
| `storagegroup` | 173 |
| `systemtype` | 184 |
| `trespass` | 185 |
| `unbind` | 186 |
| `unitserialnumber` | 187 |
| `metalun -destroy` | 189 |
| `metalun -expand` | 190 |
| `metalun -info` | 195 |
| `metalun -list` | 196 |
| `metalun -modify` | 201 |
| `reserved -lunpool -addlun` | 204 |
| `reserved -lunpool -list` | 205 |
| `reserved -lunpool -rmlun` | 206 |
| `connection -adduser` | 209 |
| `connection -deleteuser` | 210 |
| `connection -getuser` | 211 |
| `connection -getport` | 212 |
| `connection -setport` | 224 |
| `connection -delport` | 226 |
| `connection -route` | 227 |
| `connection -pingnode` | 228 |
| `connection -traceroute` | 229 |
| `connection -setsharedauth` | 230 |
| `connection -delsharedauth` | 231 |
| `connection -getsharedauth` | 232 |
| `connection -addset` | 232 |
| `connection -delset` | 233 |
| `connection -modifyset` | 234 |
| `connection -getset` | 235 |
| `connection -addpath` | 236 |
| `connection -delpath` | 237 |
| `connection -modifypath` | 238 |
| `connection -verifypath` | 239 |
| `isns -addserver` | 240 |
| `isns -deleteserver` | 240 |
| `isns -listserver` | 241 |
| `isns -setprimary` | 242 |
| `migrate -start` | 243 |
| `migrate -cancel` | 244 |
| `migrate -modify` | 245 |
| `migrate -list` | 245 |
| `domain -add` | 251 |
| `domain -list` | 253 |
| `domain -remove` | 254 |
| `domain -uninitialize` | 255 |
| `domain -setmaster` | 256 |
| `ntp -list` | 257 |
| `ntp -set` | 258 |
| `security -adduser` | 260 |
| `security -changeuserinfo` | 261 |
| `security -list` | 262 |
| `security -listrole` | 263 |
| `security -rmuser` | 263 |
| `security -ldap -addserver` | 264 |
| `security -ldap -modifyserver` | 266 |
| `security -ldap -removeserver` | 268 |
| `security -ldap -listserver` | 269 |
| `security -ldap -addrolemapping` | 270 |
| `security -ldap -modifyrolemapping` | 271 |
| `security -ldap -removerolemapping` | 271 |
| `security -ldap -listrolemapping` | 272 |
| `security -ldap -synchronize` | 273 |
| `security -certificate -add` | 273 |
| `security -certificate -remove` | 274 |
| `security -certificate -list` | 274 |
| `security -certificate -alertBeforeExpiration` | 275 |
| `security -pkcs12upload` | 276 |
| `security -SPcertificate -generate` | 276 |
| `security -fipsmode -set` | 277 |
| `security -fipsmode -get` | 277 |
| `security -tls -set` | 278 |
| `security -tls -get` | 279 |
| `security -setport` | 279 |
| `security -trustedclient -enable` | 280 |
| `security -trustedclient -add` | 280 |
| `security -trustedclient -list` | 281 |
| `security -trustedclient -remove` | 281 |
| `-portal -create` | 283 |
| `-portal -list` | 284 |
| `-portal -migrate` | 284 |
| `-portal -destroy` | 285 |
| `-template -list` | 285 |
| `-template -import` | 286 |
| `-template -export` | 286 |
| `-template -destroy` | 287 |
| `-template -findconflict` | 287 |
| `-template -swap` | 288 |
| `-monitor -addsystem` | 289 |
| `-monitor -removesystem` | 289 |
| `-monitor -listmapping` | 290 |
| `-monitor -applytemplate` | 290 |
| `-monitor -stoptemplate` | 291 |
| `-monitor -getlog` | 292 |
| `-monitor -enableresponse` | 293 |
| `-monitor -disableresponse` | 293 |
| `-monitor -getlogsize` | 294 |
| `-monitor -setlogsize` | 295 |
| `-monitor -inserttestevent` | 295 |
| `-monitor -responsetest` | 296 |
| `-monitor -reloadconfig` | 297 |
| `server -volmap` | 299 |
| `server -update` | 301 |
| `server -getagent` | 301 |
| `server -remoteconfig` | 302 |
| `server -register` | 303 |
| `hypervisor -addvirtualcenter` | 304 |
| `hypervisor -modifyvirtualcenter` | 305 |
| `hypervisor -removevirtualcenter` | 305 |
| `hypervisor -addesx` | 306 |
| `hypervisor -modifyesx` | 306 |
| `hypervisor -removeesx` | 307 |
| `hypervisor -listesx` | 307 |
| `hypervisor -bypassCert -set` | 308 |
| `hypervisor -bypassCert -get` | 308 |
| `report` | 314 |
| `storagepool -create` | 321 |
| `storagepool -list` | 324 |
| `storagepool -destroy` | 330 |
| `storagepool -modify` | 331 |
| `storagepool -expand` | 333 |
| `storagepool -cancelexpand` | 334 |
| `storagepool -feature -info` | 335 |
| `storagepool -resumeharvesting` | 336 |
| `lun -create` | 337 |
| `lun -modify` | 339 |
| `lun -expand` | 341 |
| `lun -destroy` | 341 |
| `lun -list` | 342 |
| `deduplication -feature -pause` | 346 |
| `deduplication -feature -resume` | 346 |
| `deduplication -feature -info` | 347 |
| `autotiering -schedule -modify` | 351 |
| `autotiering -relocation -start` | 353 |
| `autotiering -relocation -setrate` | 353 |
| `autotiering -relocation -stop` | 355 |
| `autotiering -info` | 355 |
| `compression -on` | 360 |
| `compression -pause` | 361 |
| `compression -feature -pause` | 362 |
| `compression -resume` | 362 |
| `compression -feature -resume` | 363 |
| `compression -feature -info` | 363 |
| `compression -modify` | 364 |
| `compression -off` | 364 |
| `compression -list` | 365 |
| `cache -fast -create` | 369 |
| `cache -fast -destroy` | 370 |
| `cache -fast -info` | 370 |
| `nqm -getlatestperf` | 374 |
| `nqm -info` | 375 |
| `nqm -ioclass -create` | 376 |
| `nqm -ioclass -destroy` | 378 |
| `nqm -ioclass -list` | 378 |
| `nqm -ioclass -modify` | 380 |
| `nqm -measure` | 382 |
| `nqm -off` | 383 |
| `nqm -policy -create` | 383 |
| `nqm -policy -destroy` | 384 |
| `nqm -policy -list` | 385 |
| `nqm -policy -modify` | 386 |
| `nqm -run` | 387 |
| `nqm -schedule -create` | 388 |
| `nqm -schedule -destroy` | 389 |
| `nqm -schedule -list` | 390 |
| `nqm -schedule -modify` | 391 |
| `nqm -schedule -resume` | 392 |
| `nqm -schedule -suspend` | 393 |
| `nqm -setfallback` | 394 |
| `nqm -setoptions` | 394 |
| `nqm -stop` | 395 |
| `nqm -archive -dump` | 395 |
| `nqm -archive -retrieve` | 402 |
| `analyzer -set` | 407 |
| `analyzer -get` | 408 |
| `analyzer -logging` | 408 |
| `analyzer -start` | 409 |
| `analyzer -stop` | 409 |
| `analyzer -status` | 410 |
| `analyzer -archive` | 410 |
| `analyzer -archivedump` | 412 |
| `analyzer -archiveretrieve` | 425 |
| `analyzer -archivemerge` | 426 |
| `mirror -async -addimage` | 433 |
| `mirror -async -change` | 435 |
| `mirror -async -changeimage` | 436 |
| `mirror -async -create` | 438 |
| `mirror -async -destroy` | 439 |
| `mirror -disablepath` | 440 |
| `mirror -enablepath` | 441 |
| `mirror -async -fractureimage` | 442 |
| `mirror -async -info` | 443 |
| `mirror -async -list` | 445 |
| `mirror -async -promoteimage` | 447 |
| `mirror -async -removeimage` | 449 |
| `mirror -async -setfeature` | 450 |
| `mirror -async -syncimage` | 451 |
| `mirror -async -creategroup` | 452 |
| `mirror -async -destroygroup` | 453 |
| `mirror -async -addtogroup` | 454 |
| `mirror -async -removefromgroup` | 455 |
| `mirror -async -changegroup` | 456 |
| `mirror -async -syncgroup` | 458 |
| `mirror -async -fracturegroup` | 458 |
| `mirror -async -promotegroup` | 459 |
| `mirror -async -listgroups` | 460 |
| `mirror -sync -addimage` | 467 |
| `mirror -sync -allocatelog` | 470 |
| `mirror -sync -change` | 470 |
| `mirror -sync -changeimage` | 472 |
| `mirror -sync -create` | 473 |
| `mirror -sync -deallocatelog` | 475 |
| `mirror -sync -destroy` | 476 |
| `mirror -sync -fractureimage` | 479 |
| `mirror -sync -info` | 480 |
| `mirror -sync -list` | 482 |
| `mirror -sync -listsyncprogress` | 484 |
| `mirror -sync -listlog` | 485 |
| `mirror -sync -promoteimage` | 486 |
| `mirror -sync -removeimage` | 488 |
| `mirror -sync -setfeature` | 489 |
| `mirror -sync -syncimage` | 490 |
| `mirror -sync -creategroup` | 491 |
| `mirror -sync -destroygroup` | 492 |
| `mirror -sync -addtogroup` | 493 |
| `mirror -sync -removefromgroup` | 494 |
| `mirror -sync -changegroup` | 496 |
| `mirror -sync -syncgroup` | 497 |
| `mirror -sync -fracturegroup` | 498 |
| `mirror -sync -promotegroup` | 498 |
| `mirror -sync -listgroups` | 500 |
| `sancopy -create` | 515 |
| `sancopy -destinfo` | 520 |
| `sancopy -duplicate` | 523 |
| `sancopy -info` | 523 |
| `sancopy -mark` | 527 |
| `sancopy -modify` | 528 |
| `sancopy -pause` | 533 |
| `sancopy -remove` | 534 |
| `sancopy -resume` | 535 |
| `sancopy -settings` | 536 |
| `sancopy -start` | 538 |
| `sancopy -stop` | 539 |
| `sancopy -throttle` | 540 |
| `sancopy -transfer` | 541 |
| `sancopy -unmark` | 542 |
| `sancopy -updateconnections` | 543 |
| `sancopy -verify` | 543 |
| `snapview -activatesnapshot` | 583 |
| `snapview -chgrollback` | 584 |
| `snapview -chgsnapshot` | 585 |
| `snapview -createsnapshot` | 586 |
| `snapview -deactivatesnapshot` | 587 |
| `snapview -listrollback` | 588 |
| `snapview -listsessions` | 590 |
| `snapview -listsnapshots` | 593 |
| `snapview -listsnapableluns` | 594 |
| `snapview -lunpool` | 595 |
| `snapview -rmsnapshot` | 596 |
| `snapview -startrollback` | 597 |
| `snapview -startsession` | 599 |
| `snapview -stopsession` | 601 |
| `snap -feature` | 622 |
| `snap -create` | 622 |
| `snap -destroy` | 624 |
| `snap -list` | 624 |
| `snap -modify` | 627 |
| `snap -copy` | 628 |
| `snap -restore` | 628 |
| `snap -attach` | 629 |
| `snap -detach` | 630 |
| `snap -group -create` | 630 |
| `snap -group -destroy` | 631 |
| `snap -group -modify` | 631 |
| `snap -group -list` | 632 |
| `snap -group -addmember` | 633 |
| `snap -group -rmmember` | 633 |
| `snap -group -replmember` | 634 |
| `lun -attach` | 638 |
| `lun -detach` | 638 |
| `storagepool -resumeAutoDelete` | 643 |
| `esrsconfig -agentprovision` | 652 |
| `esrsconfig -agentstatus` | 653 |
| `esrsconfig -configproxy -addproxy` | 654 |
| `esrsconfig -configproxy -list` | 655 |
| `esrsconfig -configproxy -removeproxy` | 655 |
| `esrsconfig -configpolicymanager -addpm` | 655 |
| `esrsconfig -configpolicymanager -list` | 656 |
| `esrsconfig -configpolicymanager -addpolicyproxy` | 657 |
| `esrsconfig -configpolicymanager -removepolicyproxy` | 658 |
| `esrsconfig -configpolicymanager -removePM` | 658 |
| `securedata -feature -activate` | 661 |
| `securedata -feature -info` | 662 |
| `securedata -backupkeys -status` | 663 |
| `securedata -backupkeys -retrieve` | 664 |
| `securedata -auditlog -retrieve` | 665 |
| `securedata -auditlog -cksum` | 666 |
