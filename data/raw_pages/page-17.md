---
id: page-17
title: "Nimbus Cloud Infra – AWS Account Vending"
space: PLATFORM
owner: "Cloud Platform Team"
status: current
document_type: procedure
authority_level: standard
department: platform-eng
labels: [access-request, nimbus, aws]
last_updated: 2026-07-14
effective_date: 2026-07-14
related: [page-18]
supersedes: []
superseded_by: []
url: "https://wiki.meridian.example/PLATFORM/Nimbus+Cloud+Infra+AWS+Account+Vending"
---

# Nimbus Cloud Infra – AWS Account Vending

Nimbus is Meridian's cloud infrastructure automation platform. It provisions AWS accounts, configures networking and security, and manages cross-account access.

## Prerequisites

- Your team must have a business case for a new AWS account (dedicated environment, isolated workload, new line of business, etc.)
- Your tech lead or manager must provide sign-off and approval

## How to request an AWS account

1. Open the ServiceNow Access Catalog and search for **"Nimbus AWS Account Vending"**.
2. Provide:
   - Account name (will become the AWS account nickname)
   - Team and owner name
   - Business justification (what workload will run in this account)
   - Expected monthly spend (estimate)
   - Compliance requirements (PCI, SOC 2, HIPAA, etc.)
3. Your request routes to the **Cloud Platform Team** for review and provisioning.

**SLA:** 3–5 business days

## After account provisioning

Once your AWS account is created:

1. The Cloud Platform Team emails you the account ID and initial cross-account role setup
2. You can assume the `NimbusAdmin` role from your primary Meridian AWS account
3. Initial networking (VPC, subnets, security groups) is pre-configured by the Cloud Platform Team
4. You are responsible for all workload-specific configuration and security hardening

## Cost management

- All AWS spending is tracked and billed back to your team via Meridian's chargeback system
- Budget alerts are configured automatically; you'll be notified if spending exceeds projections
- Cost anomalies are reviewed quarterly by the Finance and Cloud teams

## Compliance and audit

- All AWS API calls are logged to CloudTrail and Meridian's central logging account
- Your account is subject to quarterly security audits by the Security team
- Compliance requirements (PCI, SOC 2, etc.) are enforced through automated controls

## Questions

Reach out to the Cloud Platform Team in `#cloud-infra-support` on Slack or email **cloud-platform@meridian.example**.
