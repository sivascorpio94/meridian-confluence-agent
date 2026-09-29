---
id: page-23
title: "Q3 2024 Access Review – Mosaic UI Audit Findings"
space: SECURITY
owner: "Security/IAM Team"
status: current
document_type: audit
department: security
labels: [audit, mosaic-ui, compliance]
last_updated: 2024-10-15
effective_date: 2024-10-15
related: [page-01]
supersedes: []
superseded_by: []
url: "https://wiki.meridian.example/SECURITY/Q3+2024+Access+Review+Mosaic+UI+Audit+Findings"
---

# Q3 2024 Access Review – Mosaic UI Audit Findings

**Report Date:** October 15, 2024  
**Audit Period:** Q3 2024 (July 1 – September 30, 2024)  
**Prepared by:** Security/IAM Team  
**Classification:** Internal Use Only

## Executive summary

The Security/IAM team conducted an access review of Mosaic UI role assignments in Q3 2024. This audit examined role appropriateness, access revocation on role changes, and compliance with our RBAC policy.

**Finding:** 94 active users with Mosaic UI access; 12 access violations detected and remediated.

## Violations identified

| Finding | Count | Resolution |
|---|---|---|
| User retained access after leaving the team | 4 | Immediate revocation; manager notified |
| Role escalation without approval | 5 | Downgrade to appropriate level; audit trail reviewed |
| Stale access (>90 days inactive) | 3 | Revocation with manager notification; reaccess permitted if needed |

All violations were resolved by September 30, 2024.

## Recommendations

1. **Shorten review cycle**: Conduct quarterly access reviews instead of annually to catch stale access sooner
2. **Automate revocation**: Implement automated access revocation on role change (currently manual)
3. **Strengthen approval gates**: Require department head sign-off for `MOSAIC_UI_ADMIN` roles

## Compliance status

Mosaic UI access is compliant with Meridian's RBAC policy as of Q3 2024. No escalations to the Security Committee are required.

---

**Next review scheduled:** Q4 2024 (October–December 2024)

*This is a point-in-time audit report from Q3 2024. For current access procedures, see [Mosaic UI Access Request Procedure](page-01).*
