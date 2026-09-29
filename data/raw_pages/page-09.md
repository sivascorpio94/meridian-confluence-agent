---
id: page-09
title: "Atlas Reporting Dashboard Access"
space: PLATFORM
owner: "Data & Analytics Team"
status: current
document_type: procedure
authority_level: standard
department: data-analytics
labels: [access-request, atlas, reporting]
last_updated: 2026-07-08
effective_date: 2026-07-08
related: [page-10]
supersedes: []
superseded_by: []
url: "https://wiki.meridian.example/PLATFORM/Atlas+Reporting+Dashboard+Access"
---

# Atlas Reporting Dashboard Access

Atlas is Meridian's self-service business intelligence and reporting platform. It provides dashboards and data exports for financial reporting, product analytics, and operational metrics.

## Who needs Atlas access

- Finance and accounting staff (all levels)
- Product managers and analytics engineers
- Operations and support leadership
- Executive sponsors of strategic initiatives

Check with your manager if you're unsure whether your role requires Atlas access.

## How to request access

1. Open the ServiceNow Access Catalog and search for **"Atlas Dashboard Access"**.
2. Select your role or team from the dropdown.
3. Specify which dashboards or datasets you need access to (or request "standard role access" for your department).
4. Provide a brief business justification.
5. Your request routes to the **Data & Analytics Team** for approval.

**SLA:** 1 business day

## Roles and permissions

| Role | Grants | Typical user |
|---|---|---|
| `ATLAS_VIEWER` | Read-only access to published dashboards and standard reports | Finance analysts, operational staff |
| `ATLAS_POWER_USER` | Create and modify dashboards, export data, schedule reports | Product managers, analytics engineers |
| `ATLAS_ADMIN` | Manage data sources, user access, system settings | Data & Analytics Team leads |

## Data access

- Atlas connects to Meridian's data warehouse (Snowflake).
- Your access is restricted to datasets relevant to your department (Finance sees financial data, Product sees product data, etc.).
- Some sensitive datasets (executive-only metrics, customer PII) require additional approval from department heads.
- All data access is logged and auditable.

## Support and troubleshooting

For questions about dashboards, data definitions, or access issues, reach out in `#data-analytics-support` on Slack or email **atlas-support@meridian.example**.

## Related pages

- [Atlas Reporting – Data Dictionary](page-10) — definitions of key metrics and data columns
