---
id: page-11
title: "Northstar CRM Role Matrix"
space: PLATFORM
owner: "CRM Team"
status: current
document_type: reference
authority_level: canonical
department: all
labels: [northstar, roles, reference]
last_updated: 2026-07-05
effective_date: 2026-07-05
related: [page-12, page-13]
supersedes: []
superseded_by: []
url: "https://wiki.meridian.example/PLATFORM/Northstar+CRM+Role+Matrix"
---

# Northstar CRM Role Matrix

Northstar is Meridian's CRM platform for managing customer relationships and sales pipelines. This page is the canonical source for all Northstar role definitions.

## Role overview

| Role | Grants | Provisioning method | Typical user |
|---|---|---|---|
| `NORTHSTAR_REP` | View and edit assigned accounts, log calls and notes, create opportunities | ServiceNow | Sales reps, account executives |
| `NORTHSTAR_MANAGER` | Everything in `NORTHSTAR_REP`, plus view team performance, reassign opportunities, run forecasts | ServiceNow | Sales managers, team leads |
| `NORTHSTAR_SUPPORT_AGENT` | View customer accounts (read-only), log support cases, link to active opportunities | ServiceNow | Support agents answering customer calls |
| `NORTHSTAR_ANALYST` | Run custom reports, export data, access historical pipeline data | ServiceNow | Sales analysts, operations staff |
| `NORTHSTAR_ADMIN` | Manage all users, configure workflows, set up custom fields, manage integrations | Manual request to CRM Team | CRM admins, platform engineers |

## Key policies

- Role names are case-sensitive and must match exactly as listed above
- Access is granted per-role, not per-feature; you cannot mix and match permissions
- Roles are reviewed quarterly; access is automatically revoked on termination
- Admin roles require VP-level sign-off (CRM Team Lead or higher)

## Related pages

- [Northstar CRM Access Request (Sales)](page-12) — Sales team access procedure
- [Northstar CRM Access Request (Support)](page-13) — Support team access procedure
