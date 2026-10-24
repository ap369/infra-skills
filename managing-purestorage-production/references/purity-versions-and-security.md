# Purity versions, security bulletins, access and SAN practices

> **Command verification status:** only the commands in purity-command-catalog.md were confirmed against Everpure documentation (`[doc]`). The Purity//FA CLI Reference Guide isn't public, so **every other Purity command in this skill is `[unverified]`** until confirmed on the array with `<command> --help`. See command-verification.md.


Source: public Everpure documentation at support.everpuredata.com, retrieved 2026-10-13 (FlashArray Security, Directory Services on FlashArray, FlashArray Block Best Practices, FlashArray File Services, ActiveCluster/ActiveDR, and FlashArray security bulletins). The full **Purity//FA Admin and CLI Reference Guide is not public** (it needs a Pure1 login), so most CLI syntax in this skill is still unverified. Confirm it with `<command> --help` on the array.

## Feature / version facts
| Fact | Version |
|---|---|
| ActiveDR available | Purity//FA 6.0.0+ |
| ActiveDR over FC | 6.1.7+ |
| ActiveCluster over FC | 6.1.0+ |
| Replication peers may differ by **at most two minor versions**; matching is best practice | ActiveCluster and ActiveDR |
| File Services enabled automatically on compatible arrays (earlier releases needed Technical Services) | 6.8.2+ |
| ActiveCluster File (stretched Realms) | 6.12.2+ |
| Directory Services | 3.2.0+ |

## Upgrades
- Everpure recommends **Pure1 Self-Service Upgrades** as the primary method. An array-CLI self-service path also exists (the `puresw` command family: catalog, checks, download, interactive upgrade).
- Those procedure pages are marked *"Restricted Content – Do Not Distribute"*, so they **aren't reproduced here**. Open the official "Purity//FA Self-Service Upgrade" pages with your Pure1 account, and follow them together with the current Admin and CLI Reference Guide.
- Agent rule: an upgrade is T3. Never override a failed upgrade check without the vendor's or a qualified engineer's sign-off recorded in the plan.

## Security bulletins: minimum fixed versions (check during audits)
| CVE | Issue | Severity | Fixed in |
|---|---|---|---|
| CVE-2024-3057 | Privilege escalation via a specific endpoint (affects 6.6.2–6.6.5) | **Critical (9.8)** | **6.6.6** |
| CVE-2026-6444 | Low-privilege user can access functions beyond their role (6.10.0–6.10.5) | High | **6.10.6** |
| CVE-2026-6445 | Sensitive information exposure to low-privilege users (6.5.0–6.5.8, 6.10.0–6.10.5) | High | **6.5.9, 6.10.6** |
| CVE-2026-0209 | Snapshot retention applied earlier or later than configured | Medium | 6.5.13, 6.7.7, 6.9.2, 6.10.1 |
| CVE-2025-2327 | KEK logged during key rotation when RDL is configured | Medium | 6.5.11, 6.7.4, 6.8.6 |
| CVE-2023-32572 | Admin could alter the pgroup retention lock and disable pgroup SafeMode (only with retention lock + SafeMode snapshots) | Medium | 6.3.8, 6.4.3 |
| CVE-2023-28373 | Admin configuring an external key manager could affect data availability, including SafeMode snapshots | Low | 6.1.23, 6.2.16, 6.3.7, 6.4.1 |

Check the bulletin pages for the full affected-version lists and any newer bulletins. A SafeMode audit must include the Purity version: on affected releases, SafeMode isn't a complete guarantee against a rogue admin.

## Directory services (AD/LDAP) and roles
- Built-in roles: **array_admin, storage_admin, ops_admin, readonly**. Map AD security groups to them with `pureds role setattr` (the old `pureds setattr --array-admin-group`, `--storage-admin-group`, `--readonly-group` and `--group-base` options are deprecated). Test with `pureds test`. Show with `pureds list` and `pureds list --groups`.
- **For monitoring and MCP tokens, use a `readonly`-role account.**
- Constraints:
  - use **security groups** with a CN, not OUs or distribution groups
  - all Pure groups in the same OU
  - a group that is a user's *primary group* doesn't work
  - one domain only, up to 30 DCs, all `ldap://` or all `ldaps://` (no mixing)
  - the bind user must be able to read `memberOf`
  - users can't be in AD *Protected Users*
  - AD usernames can't collide with local array accounts such as `pureuser`, `root` or `pureadmin`
- Prefer `ldaps://` with `--ca-certificate`, and `pureds enable --checkpeer`.

## SAN best practices (FlashArray Block)
- **FC zoning:** single initiator → multiple Pure targets (with dual fabrics, up to 4 array ports per fabric per host port). Avoid many-initiator zones.
- **Avoid ISLs** between hosts and the array. If you can't, watch for frame discards on the ISLs.
- **Don't mix link speeds two steps apart** (an 8Gb host in a 32Gb path). Find and fix ports hard-set to a lower speed.
- **iSCSI:**
  - don't route it; use a closed network
  - use all interfaces per host, or multiple sessions if the array has fewer than 8 ports
  - MTU 1500 unless jumbo frames are needed. With jumbo frames, MTU 9000 must match on the **whole path** (array `purenetwork setattr <port> --mtu 9000`, switch, host).
- Replace or clean any cable or port with CRC or physical errors. Bypass patch panels when testing.
- Blade chassis with unmanaged ("dumb") switches can't zone, so plan fan-in accordingly.
- Host multipath settings: follow the host-specific Everpure best-practice guides (ESXi, Linux, Windows, AIX).
