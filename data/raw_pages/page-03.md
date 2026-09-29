---
id: page-03
title: "Sentinel IAM Role Catalog"
space: SECURITY
owner: "Security/IAM Team"
status: current
document_type: reference
authority_level: canonical
department: all
labels: [iam, roles, reference]
last_updated: 2026-06-01
effective_date: 2026-06-01
related: [page-01]
supersedes: []
superseded_by: []
url: "https://wiki.meridian.example/SECURITY/Sentinel+IAM+Role+Catalog"
---

# Sentinel IAM Role Catalog

This page is the single source of truth for role names across systems provisioned through Sentinel. Not every internal system is onboarded to Sentinel yet — systems below are the ones currently covered. If a system you're looking for isn't listed here, it may still be managed by its owning team directly; check that system's own access page.

Role names are case-sensitive and follow the pattern `SYSTEM_SCOPE`.

## Mosaic UI

| Role | Description |
|---|---|
| `MOSAIC_UI_VIEWER` | Read-only access to account views, transaction history, and case notes |
| `MOSAIC_UI_ADMIN` | Full access, including account flag edits and reconciliation triggers |

## Orion Gateway

| Role | Description |
|---|---|
| `ORION_CONSUMER` | Can generate and use API keys against published Orion endpoints |
| `ORION_PUBLISHER` | Can register new endpoints and manage rate limit tiers |

## Northstar CRM

| Role | Description |
|---|---|
| `NORTHSTAR_REP` | View and edit assigned accounts, log calls and notes, and create opportunities |
| `NORTHSTAR_MANAGER` | Sales representative access plus team performance, reassignment, and forecasting |
| `NORTHSTAR_SUPPORT_AGENT` | Read-only customer access with support case logging |
| `NORTHSTAR_ANALYST` | Reporting, data export, and historical pipeline access |
| `NORTHSTAR_ADMIN` | User, workflow, field, and integration administration |

## Vault

| Role | Description |
|---|---|
| `VAULT_READER` | Can read secrets within an assigned namespace |
| `VAULT_NAMESPACE_ADMIN` | Can create and manage a namespace, including access policies |

## Requesting a role change

This catalog is reference-only — it does not process requests. Each system's own access page (linked from the Platform space index) describes how to actually request the roles listed here.

## Change history

Roles are added or retired as systems evolve. If you find a role referenced elsewhere in the wiki that isn't listed on this page, treat it as unverified and confirm with the Security/IAM Team before relying on it.
