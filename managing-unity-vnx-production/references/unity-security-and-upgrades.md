# Unity security and upgrade facts (from Dell documentation)

> **Sources:** Dell EMC Unity Family *Upgrading Unity Software* 5.x (H14977, Rev. 10, Sept 2021), *Security Configuration Guide* 5.1 (302-002-564, Rev. 13, Oct 2021), *Configuring High Availability* 5.x (H16708, Rev. 06, Aug 2021), retrieved 2026-10-25 from delltechnologies.com. Facts here are `[doc]` for those releases; on newer OE, check the current guide or release notes. CLI forms: unity-command-catalog.md.

## Upgrades (H14977)
- **"There is no way to cancel an upgrade that is in progress. Once you start the upgrade process, you must finish it."** Treat starting an OE upgrade as a one-way T3 step.
- Run a **health check about a week before** the upgrade (Unisphere *Perform Health Checks*, or `/sys/general healthcheck`). If it fails, fix the problem first: "If any system components are degraded, the update will fail." Re-run it just before the window.
- **During the upgrade only one SP handles I/O**, so performance drops: schedule a low-I/O window and check host multipathing on both SPs beforehand. Unisphere disconnects for a few minutes when the primary SP reboots.
- **Upgrade drive firmware first** ("recommended to always upgrade to the latest drive firmware before performing a software upgrade to help mitigate any nondisruptive upgrade issues"). From 5.1, the pre-upgrade health check reports newer drive firmware.
- **Hotfixes installed before the upgrade are removed.** Check in the release notes that each hotfix's issue is fixed in the target OE, or reinstall it afterwards.
- Verify the upgrade file with its **SHA256 checksum** before uploading. Only one upgrade candidate can be on the system at a time; a new upload replaces it.
- Some upgrades require a specific starting version (see the release notes). Estimated time is about **1 hour 15 minutes**; firmware included in an OE update makes it longer.

## Accounts and access (Security Configuration Guide 5.1)
- Factory defaults: Unisphere `admin` / `Password123#` and service account `service` / `service`. Both must be changed at initial configuration. Any system still accepting them is a **critical finding**.
- Local roles: **Operator** (view; can change its own password), Storage Administrator, Security Administrator, Administrator, VM Administrator. LDAP users and groups can be mapped to the same roles. Use **Operator** for every read-only identity (MCP, monitoring, this skill's reads).
- Login lockout: `/user/account/settings set -maxFailedLogins <n> -failedLoginPeriod <s> -lockoutPeriod <s>` (all three must be given together). Session idle timeout is configurable from 1 to 3600 seconds.
- The **service SSH interface** is off unless enabled (Unisphere: *Service > Service Tasks > Enable SSH*). Enable it only for a support session and disable it afterwards.
- TLS: the system supports TLS 1.0, 1.1 and 1.2 by default on older OE. Disabling old TLS versions is a security change (T2): check every client (uemcli, REST scripts, vCenter/VASA, Unisphere Central) first.
- FIPS 140-2 mode: `/sys/security set -fips140Enabled yes|no`, only by an Administrator or Security Administrator. It's a T2 change with client-compatibility impact.
- Audit: user actions are logged as audit events. Not every audit entry shows in the GUI; enable remote logging (`/sys/rlog`, see unity-command-catalog.md) to archive them: the local log keeps about 1.5 million entries and purges the oldest.

## High availability (H16708)
- Network redundancy uses **link aggregation** ("two to four Ethernet port combinations in one logical link") and **fail-safe networking (FSN)**. A link aggregation is created on the same ports of both SPs, and "the cabling on SP A must be identical to the cabling on SP B". Losing one link doesn't fail over to the peer SP: the switch moves traffic to the remaining ports.
- Before any SP reboot, upgrade or trespass, check that every host has paths to **both** SPs. An SP outage on a host with single-SP paths is a host outage.
