---
id: page-14
title: "Vault Secrets Management – Access Policy"
space: SECURITY
owner: "Security/IAM Team"
status: current
document_type: policy
authority_level: standard
department: security
labels: [vault, secrets, policy]
last_updated: 2026-02-28
effective_date: 2026-02-28
related: [page-15]
supersedes: []
superseded_by: []
url: "https://wiki.meridian.example/SECURITY/Vault+Secrets+Management+Access+Policy"
---

# Vault Secrets Management – Access Policy

This page describes the approval workflow for requesting Vault namespace access.

## Overview

Vault is Meridian's centralized secrets management system. It stores database credentials, API keys, encryption keys, and other sensitive material used by platform services. Access is scoped to individual namespaces and requires explicit approval from the Security/IAM team.

## Email-based request workflow

Use the following process to request access:

1. Send an email to **vault-requests@meridian.example** with:
   - Your name and team
   - The namespace you need access to (or request a new one for your team)
   - A brief business justification
2. The Security/IAM team reviews your request and emails you an approval or denial within 3–5 business days.
3. Upon approval, they manually provision your access and email you connection details.

## Policy: access scope

Regardless of request method:

- Each team is assigned a namespace within Vault (e.g. `meridian/platform-eng/secrets`).
- Individual developers within the team request access to their team's namespace, not arbitrary namespaces.
- Admin access to a namespace is granted only to team leads and senior engineers.
- Namespace ownership is maintained by the Security/IAM team; team leads cannot delegate access independently.

## Access review and revocation

- All Vault access is reviewed quarterly as part of Meridian's access recertification process.
- Access is automatically revoked when an engineer leaves the company or changes teams.
- Revocation is auditable and logged in Vault's access history.
