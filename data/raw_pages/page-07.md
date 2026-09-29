---
id: page-07
title: "PaySure Payment Processing Access"
space: PLATFORM
owner: "Payments Team"
status: current
document_type: procedure
authority_level: standard
department: payments
labels: [access-request, paysure, compliance]
last_updated: 2026-06-20
effective_date: 2026-06-20
related: []
supersedes: []
superseded_by: []
url: "https://wiki.meridian.example/PLATFORM/PaySure+Payment+Processing+Access"
---

# PaySure Payment Processing Access

PaySure is Meridian's internal payment processor for client transactions and reconciliation. Access requires PCI compliance training and dual approval due to the sensitivity of the system.

## Prerequisites

Before requesting PaySure access, you must:

1. Complete the **PCI Data Security Standard (PCI DSS) training module** — available through the internal Learning Management System. This is mandatory for anyone handling payment data.
2. Confirm with your manager that your role requires PaySure access.

## How to request access

1. Open the ServiceNow Access Catalog and search for **"PaySure Access Request"**.
2. Select the role appropriate to your team (standard roles: `PAYSURE_VIEWER`, `PAYSURE_OPERATOR`, `PAYSURE_ADMIN`).
3. Provide your PCI training completion certificate number in the justification field.
4. Your request routes to the **Payments Team Lead** for the first approval.
5. After Payments Team approval, the request routes to the **Security/Compliance Officer** for the second approval (PCI audit trail).
6. Once both approvals are complete, provisioning is automatic.

**SLA:** Up to 10 business days end-to-end, accounting for PCI compliance review and dual sign-off. Complex requests (cross-department, elevated privileges) may take longer.

## After access is granted

- Access is automatically reviewed quarterly as part of Meridian's PCI compliance audit cycle.
- If your role or team changes, revoke your PaySure access through the same ServiceNow catalog and request a new role if needed.
- Do not share your PaySure credentials. All actions are logged and auditable.

## Related pages

- Internal Learning Management System (PCI training)
- ServiceNow Access Catalog
