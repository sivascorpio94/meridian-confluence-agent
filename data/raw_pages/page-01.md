---
id: page-01
title: "Mosaic UI Access Request Procedure"
space: PLATFORM
owner: "Mosaic Platform Team"
status: current
document_type: procedure
authority_level: canonical
department: all
labels: [access-request, mosaic-ui, how-to]
last_updated: 2026-07-15
effective_date: 2026-07-15
related: [page-03, page-22]
supersedes: [page-02]
superseded_by: []
url: "https://wiki.meridian.example/PLATFORM/Mosaic+UI+Access+Request+Procedure"
---

# Mosaic UI Access Request Procedure

Mosaic UI is the internal operations console used by Platform, Ops, and Support teams to view and manage client account records and case notes. Access is role-based and must be requested through ServiceNow.

## Roles

| Role | Grants | Typical requester |
|---|---|---|
| `MOSAIC_UI_VIEWER` | Read-only access to account views, transaction history, and case notes | Support agents, new engineers during onboarding |
| `MOSAIC_UI_ADMIN` | Everything in `MOSAIC_UI_VIEWER`, plus the ability to edit account flags and trigger reconciliation jobs | Platform engineers, on-call responders |

Role names are case-sensitive and must match the [Sentinel IAM Role Catalog](page-03) exactly. If a request references a role name that isn't in the catalog, Sentinel will reject the provisioning step even if a human approver signs off.

## How to request access

1. Open the ServiceNow Access Catalog and search for **"Mosaic UI Access"**.
2. Select the role you need (`MOSAIC_UI_VIEWER` or `MOSAIC_UI_ADMIN`) and provide a one-line business justification.
3. Your request routes automatically to your manager for the first approval.
4. After manager approval, the request routes to the **Mosaic Platform Team Lead** for the second and final approval.
5. Once approved, Sentinel provisions the role automatically — no manual ticket to Platform is required.

**SLA:** 2 business days end-to-end under normal conditions. If you haven't heard anything after 2 business days, follow up in `#mosaic-platform-support` on Slack rather than re-submitting the request.

## Removing access

Access is reviewed quarterly by the Mosaic Platform Team as part of the standard access recertification cycle. If your role changes and you no longer need Mosaic UI access, ask your manager to submit a revocation request through the same ServiceNow catalog item — select "Revoke" instead of "Request" from the dropdown.

## Related pages

- [Sentinel IAM Role Catalog](page-03) — canonical list of role names across all Meridian systems
- [Meridian Platform Access – Master FAQ](page-22) — general access questions and links to other platform procedures
