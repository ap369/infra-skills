# ObjectScale / ECS facts from Dell's best-practices white paper

> **Source:** Dell *ObjectScale Best Practices* white paper **H16016.15** (September 2026, covers ObjectScale up to 4.3 and ECS heritage features), retrieved 2026-10-25 from Dell Info Hub. Facts here are `[doc]` for that paper; check the release notes and Security Configuration Guide of your release (those need a Dell support login). This file holds no API paths or CLI forms: those stay `[unverified]` (see command-verification.md).

## Set once, never changed (Table 1)
The settings below "can only be configured during creation time; once set, they cannot be modified". A wrong choice means a new object and a data migration, so plan them as T3 decisions.
| Level | Fixed at creation |
|---|---|
| Storage pool | erasure coding: 12+4, 10+2, and from 4.3 24+2, 24+4 |
| Replication group | *Replicate to all sites*. **Replication groups can't be deleted** |
| Namespace | name, server-side encryption, compliance |
| Bucket | name, namespace, replication group, server-side encryption, file system (NFS), CAS, metadata search |
| VDC | names must be unique and **can't be reused** |
| User scope | GLOBAL (default) or NAMESPACE: fixed once the **first object user** is created in a VDC |

## Capacity
- "Keep the total capacity lower than 80 percent. **When the storage pool reaches 90 percent of its capacity, it does not accept write requests, and it becomes a read-only system.**"
- Add capacity to a VDC **before it reaches 85%**, and earlier if growth is fast. Account for rebalancing time after an expansion.
- In multisite setups, keep enough free space for a temporary site outage and for permanent site removal. When you expand one site, expand the others as needed.
- Minimum nodes per EC scheme: 12+4 needs 5, 10+2 needs 7, 24+4 needs 8, 24+2 needs 14. On 4.3, 12+4 suits pools of about 5–8 nodes, and 24+4 suits larger pools.
- Garbage collection works per replication group. Mixing short-term and long-term retention data in one replication group hurts space reclamation, so separate them (common for backup/archive).
- Object version limit: 50k per object from ECS 3.6 on new installs, with alerts at 50% and 80%.

## Replication and outages
- Create the **minimum number of replication groups**, because each storage pool / replication group pair adds indexing overhead. The usual layout is one local group plus one spanning all VDCs; add others only for sovereignty or compliance needs. Federate all VDCs first.
- Up to **8 VDCs** per federation or replication group. Don't build a replication group from VDCs that all sit in one site.
- XOR efficiency (3+ sites) needs writes at two or more sites. Balance writes with a global load balancer and expect WAN latency for reads that aren't local.
- Replication bandwidth must be at least the ingest rate; otherwise RPO grows (throttle with QoS or ask Dell).
- **ADO (access during outage)** is best enabled **when the bucket is created**. During a temporary site outage: FS (NFS) buckets are read-only, listing some buckets can fail, and on rejoin "conflict resolution favors secondary site, though it is nondeterministic".
- Create buckets at the VDC closest to the application, because remote object ownership adds lookup overhead.

## Accounts and security
- **Management users (local or domain) are not replicated between VDCs**, except domain-based namespace administrators. Create each admin at every VDC; a password change at one VDC doesn't propagate.
- A namespace administrator administers **one** namespace. An AD group can be namespace admin for only one namespace; LDAP *groups* aren't used.
- Management users and object users are separate and not correlated. Object users authenticate with secret keys, so don't give local accounts domain-style names.
- IAM (S3 only): one IAM user per person, groups for permissions, roles and temporary credentials for applications, least-privilege policies, regular key rotation, delete unused credentials.
- Change the default passwords at once (node `admin`, portal `root`). Use named accounts for daily work, not the built-in account.
- **Platform lockdown** disables SSH to the nodes. **Audit events** record configuration changes, logins and sudo on nodes, bucket permission changes and user/password operations: review them regularly.
- D@RE is set per namespace or per bucket at creation. Avoid double encryption (for example with Isilon/PowerScale CloudPools encryption). On 4.1+ XF960, SED keys are managed by iDRAC iLKM: change the default passphrase and rotate it.
- **Object Lock:** enabling it turns on versioning, and **it can't be disabled** (nor can versioning be suspended). Compliance-mode retention can't be shortened or removed by anyone, root included. Governance mode can be bypassed by users with special permission. Only locked versions are protected: objects can still get delete markers.
- Load balancers: terminate TLS at the LB for performance, **except for PII workflows** (keep TLS to the nodes, with Layer 4 pass-through and certificates on the nodes). Deploy redundant LBs, use only the LB's HA function for NFS, and prefer global DNS/LB over DNS round robin. ObjectScale 4.3 has an integrated load balancer (optional).

## Infrastructure
- DNS: at least two servers, with forward and reverse entries for every node.
- NTP: **4 to 7 servers**, with common sources across sites. Unstable NTP "can result in data corruption or excessive system journal activity".
- DHCP: use persistent MAC reservations. Federated VDCs can't use NAT on the public, replication and management networks.
- Names: lowercase letters, digits and hyphens only (no uppercase, no underscores) for every construct. Never use personal data in names.

## Operations
- Monitor CPU, memory and network imbalance between nodes, failed-request rates, events and audit logs. Know the normal baseline.
- Dell Secure Connect Gateway is "highly recommended". Subscribe to Dell product advisories for ObjectScale and read the release notes before every upgrade.
- Hardware expansion: new nodes must have capacity and performance at least equal to the existing VDC. Rack-awareness rules apply (Table 3); `rack_awareness_enabled` isn't changed by upgrades, so review it with Dell when racks are imbalanced.
