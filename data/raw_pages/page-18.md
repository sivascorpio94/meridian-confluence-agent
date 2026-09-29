---
id: page-18
title: "Nimbus Cloud Infra – Break Glass Emergency Access"
space: SECURITY
owner: "Security/IAM Team"
status: current
document_type: procedure
authority_level: standard
department: security
labels: [nimbus, emergency, security]
last_updated: 2026-07-13
effective_date: 2026-07-13
related: [page-17]
supersedes: []
superseded_by: []
url: "https://wiki.meridian.example/SECURITY/Nimbus+Cloud+Infra+Break+Glass+Emergency+Access"
---

# Nimbus Cloud Infra – Break Glass Emergency Access

Break glass access is an emergency escalation mechanism for accessing AWS accounts when normal access routes are unavailable or during active security incidents.

## When to use break glass

Break glass access should only be used when:

- The normal cross-account IAM role is unavailable or compromised
- A security incident requires immediate remediation (malware, data breach, account compromise)
- An outage is affecting production and normal access channels are blocked
- Authorized approvers are unreachable and immediate action is required

Do NOT use break glass for routine access or to bypass normal approval workflows.

## How to request break glass access

1. Contact the **Security Incident Response Team** immediately via Slack (@sec-incident-response) or call the emergency hotline (listed in Meridian's internal directory)
2. Describe the emergency, which account you need access to, and why normal access won't work
3. A Security engineer will verify your identity and escalate to a manager or director for authorization
4. Once approved, you'll be granted temporary AWS root access (or equivalent) to the account

**SLA:** 15 minutes for verification and approval (24/7 on-call team)

## Limitations and safeguards

- Break glass access is automatically revoked after 4 hours (can be extended for up to 12 hours with additional approval)
- All break glass access is logged and reviewed by the Security team; a post-incident review will follow
- Misuse of break glass access (accessing accounts without legitimate emergency, data exfiltration, etc.) is a security violation and may result in account suspension or termination
- You must file an incident report within 24 hours describing what actions you took and why they were necessary

## Incident reporting

After using break glass access:

1. Open an incident in Meridian's incident management system (PagerDuty/Slack)
2. Document:
   - When you accessed the account and for how long
   - Which account(s) and resources you touched
   - What actions you took to remediate the emergency
   - The root cause of the incident (if known)
3. The Security team will review and follow up within 24 hours

## Prevention

Break glass access should be a rarity. To prevent emergencies:

- Ensure your team's AWS cross-account roles are up-to-date and accessible
- Use Vault to store AWS credentials securely; never hardcode them in code or config
- Test access procedures regularly during normal business hours, not during crises
- Maintain on-call rotations so critical systems have coverage 24/7
