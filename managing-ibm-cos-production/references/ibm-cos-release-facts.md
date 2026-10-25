# IBM COS facts from ClevOS release notes

> **Sources:** *IBM Cloud Object Storage System 3.17.2 Release Notes* (ClevOS 3.17.2.40) and *3.15.4 Release Notes* (3.15.4.38), public IBM downloads, retrieved 2026-10-25. They are the newest IBM COS documents found that don't need an IBM login. Facts are `[doc]` for those releases. The full *Manager Administration Guide* and *REST API Developer Guide* aren't public: anything not listed here or in ibm-cos.md stays `[unverified]` (command-verification.md).

## Manager REST API operation names seen in IBM documents
Names only. A name is `[doc]` as an operation that exists; its **parameters are `[doc]` only where listed here**. Confirm everything else in the REST API Developer Guide for the installed release.
| Operation | Documented detail | Source |
|---|---|---|
| `viewSystem.adm`, `listVaults.adm` | read operations (see ibm-cos.md) | earlier IBM sources |
| `createVault.adm`, `editVault.adm` | new parameter `containerVaultObjectLockEnabled` (3.17.2) | 3.17.2 notes |
| `createVaultTemplate.adm`, `editVaultTemplate.adm` | new parameter `containerVaultObjectLockEnabled` (3.17.2) | 3.17.2 notes |
| `configureContainerVaultObjectLock.adm` | Container Mode Object Lock, system level (3.17.2) | 3.17.2 notes |
| `editStoragePoolContainerVaultObjectLock.adm` | Container Mode Object Lock, storage-pool level (3.17.2) | 3.17.2 notes |
| `bulkEditContainerVaultObjectLock.adm` | bulk enable of Container Mode Object Lock at vault level (3.17.2) | 3.17.2 notes |
| `systemOidcConfiguration.adm` | OpenID Connect for Manager GUI/API access (3.17.1) | 3.17.2 notes |
| `createAccount.adm`, `editAccount.adm` | `accountType` value `oidc`; parameter `oidcUsername` (3.17.1) | 3.17.2 notes |
| `createGroup.adm` | `groupType` value `oidc`; parameter `claimValue` (3.17.1) | 3.17.2 notes |
| `systemBackupSettings.adm` | `backupType` values `s3Bucket` (new in 3.17.0) and `ftp` (formerly `remote`, still accepted) | 3.17.2 notes |
| `systemRestore.adm` | Manager DB restore; a backup stored in an S3 bucket must first be copied to local disk | 3.17.2 notes |

Tiering: `create*`, `configure*`, `bulkEdit*` and anything with Object Lock = T3 (Object Lock can't be undone). `edit*` = T2 or more. `systemRestore.adm` = T3, support-led.

## Security and access (3.17.x)
- **MFA for Manager:** from 3.17.1, Manager GUI and API access can go through an OpenID Connect provider (MFA, password rotation). Prefer it over local Manager accounts where available.
- **Manager DB backup** can go to an S3 bucket (3.17.0) or FTP. Check that backups run and are restorable: the Manager database holds the whole system configuration.
- **S3 Object Lock API change (3.17.2, COS-96678):** GETs with Object Lock query parameters, which were silently ignored before, now return 4xx errors per the S3 Object Lock API. Test applications before upgrading to 3.17.2+.

## Upgrades
- **Only IBM-signed upgrade files work** (Software Signature Verification, 3.15.3). The Manager checks the signature on upload and each device checks it again; a bad signature fails the upgrade. Code-signing validation of release files is also available.
- Only **one upgrade file** can be uploaded to the Manager at a time.
- **3.17.0 (COS-85995)** made significant OS changes: "External agents that are not properly self-contained … may be impacted. It is recommended to verify external agent behavior as part of any upgrade activities."
- Product alerts to check before any upgrade: *Multi-Manager communication error during upgrade* (upgrades from before 3.16.6.73), *Software Signature Verification issue* (3.15 and 3.16), and *Device level APIs' required TLS cipher suite updated in 3.16.6.75* (monitoring tools may break).
- From 3.16.0 IBM COS on-premises follows a **Continuous Delivery** support lifecycle: stay on a supported stream.
- COS-77152 (3.15.x notes): Slicestors with more than 48 drives and high traffic could lose disk-management state on shutdown. For systems upgrading to a release with the fix, IBM required `storagectl configure engine.main.stop_timeout 240` on every Slicestor **before** the upgrade (later releases default to 240 s). Check your source release's notes and run it only as IBM directs.
- First Manager upgrade to 3.10.1+ can need an extra 20–30 minutes to come back (schema changes).

## Product alerts that affect operations (3.17.2 notes, table 5)
- **Drive-managed SMR drives are not approved** for named-object workloads.
- **Non-homogeneous storage pool expansions** have performance implications (all releases): expand with like hardware.
- *Potential impact to I/O performance on ZSS Slicestor devices* (all releases). 3.17.2 also fixes a ZSS data-inconsistency issue with rapid overwrite/delete (COS-96766): an upgrade driver for ZSS pools.
- *Issue with adding multiple drives in a Slicestor appliance* (all releases): add drives as the alert directs.
- IBM COS Insight is discontinued.
- Subscribe to "IBM Cloud Object Storage System" in IBM **MyNotifications** for these alerts.

## Known issues to plan around
- **Vault quotas are static (COS-23962):** they don't change when pool capacity changes (expansion, set replacement or removal). After a set removal, a quota can exceed the pool. Review quotas after every capacity change.
- Drive actions in the Manager UI (stop migration, dispose, reset, resume from DIAGNOSTIC) take about 20 seconds. **Don't press the button again**; refresh the page, then follow the disk lifecycle steps in the Manager Administration Guide.
- `storage` (localadmin shell on a Slicestor) resuming many DIAGNOSTIC drives can return error -15 on timeout while the resume continues in the background. Monitor with `storage list`; don't repeat the command.
- Replacing a failed drive with another failed drive leaves a confusing UI state: replace it again with a good drive.
- During failing-disk migration, the event's *Migration Progress* value is the percentage of the migration completed.
- DLM can't process more than 16 hot-swap events at once (COS-58128): replace drives in batches.
- Use the *Reallocation Progress bar* at the top of *Monitor Storage Pool*, not the history graph, to follow data reallocation.
