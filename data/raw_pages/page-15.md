---
id: page-15
title: "Requesting a Vault Namespace"
space: PLATFORM
owner: "Platform Engineering"
status: current
document_type: procedure
authority_level: standard
department: platform-eng
labels: [access-request, vault, how-to]
last_updated: 2026-07-10
effective_date: 2026-07-10
related: [page-14]
supersedes: []
superseded_by: []
url: "https://wiki.meridian.example/PLATFORM/Requesting+a+Vault+Namespace"
---

# Requesting a Vault Namespace

Vault is Meridian's centralized secrets management system. Use this procedure to request access to a team namespace or request a new namespace for your team.

## Prerequisites

- You must have a Meridian employee account and be listed in the internal directory.
- Your team lead or manager must confirm that your role requires Vault access.

## Request individual access to an existing namespace

If your team already has a Vault namespace and you need access to it:

1. Open the ServiceNow Access Catalog and search for **"Vault Namespace Access"**.
2. Select your team's namespace from the dropdown (e.g. `meridian/platform-eng/secrets`).
3. Provide a brief business justification (e.g. "need to rotate database credentials for my service").
4. Your request routes to your **team lead** for approval.
5. Upon approval, Vault automatically provisions your access — no manual intervention required.

**SLA:** 1 business day

## Request a new namespace for your team

If your team does not yet have a Vault namespace:

1. Open the ServiceNow Access Catalog and search for **"Vault Namespace Creation"**.
2. Fill in your team name, a brief description of what secrets you will store, and identify a **namespace owner** (usually the team lead).
3. Your request routes to **Security/IAM** for review and provisioning.
4. Security/IAM will create the namespace, set the owner, and confirm via email.

**SLA:** 2–3 business days

## After you have access

- Vault access is audited and logged. All reads and writes to secrets are recorded.
- Your access is reviewed quarterly. You may be asked to re-confirm your business need.
- If you leave the team or company, your access is automatically revoked.
- Do not store secrets in Vault that are not secrets (e.g. configuration files, build artifacts).

## Revoke access

If you no longer need Vault access:

1. Open the ServiceNow Access Catalog and search for **"Vault Namespace Access"**.
2. Select **"Revoke"** from the request type dropdown.
3. Select the namespace you want to revoke access from.
4. Your revocation is processed immediately.

## Questions or issues

If you cannot find your team's namespace in the catalog or have trouble provisioning, reach out in `#platform-eng-infra` on Slack or contact the Security/IAM team directly at **vault-support@meridian.example**.
