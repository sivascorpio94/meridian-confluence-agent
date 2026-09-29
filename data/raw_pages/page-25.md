---
id: page-25
title: "Glossary of Platform & Access Terms"
space: PLATFORM
owner: "Mosaic Platform Team"
status: current
document_type: glossary
authority_level: canonical
department: all
labels: [glossary, reference]
last_updated: 2026-07-15
effective_date: 2026-07-15
related: []
supersedes: []
superseded_by: []
url: "https://wiki.meridian.example/PLATFORM/Glossary+of+Platform+Access+Terms"
---

# Glossary of Platform & Access Terms

This page defines technical and organizational terms used across Meridian's platform and access documentation.

## Access and authentication

**API Key** — A secret token used by services to authenticate with Orion Gateway or other APIs. Must be stored in Vault, never hardcoded.

**Break Glass Access** — Emergency access mechanism that temporarily grants elevated privileges when normal access routes are unavailable (e.g., during a security incident).

**Cross-Account Role** — An IAM role in one AWS account that trusts another account, allowing users to assume it without sharing credentials.

**Namespace** — An isolated collection of secrets within Vault, scoped to a team or service (e.g., `meridian/platform-eng/secrets`).

**RBAC** — Role-Based Access Control. A system where permissions are assigned to named roles, and users are assigned to roles. See role matrix pages for role definitions.

**ServiceNow Access Catalog** — Meridian's central system for requesting access to internal tools and services. Replaces the Old Intranet Portal.

**Provisioning** — The automated process of granting access to a user after approval.

**Revocation** — The process of removing a user's access to a system or service.

## Systems and platforms

**Atlas** — Meridian's business intelligence and reporting platform. Provides dashboards and data exports.

**Beacon** — Meridian's IT support ticketing system for hardware and software support requests.

**Comet** — Meridian's continuous integration and continuous deployment (CI/CD) platform.

**Mosaic UI** — Meridian's internal operations console for viewing and managing client account records and case notes.

**Northstar** — Meridian's CRM platform for managing customer relationships and sales pipelines.

**Orion Gateway** — Meridian's API gateway for internal service-to-service communication.

**PaySure** — Meridian's payment processing system for client transactions and reconciliation.

**Sentinel** — Meridian's identity and access management (IAM) system. Provisions roles across all systems.

**Vault** — Meridian's centralized secrets management system for storing credentials, API keys, and encryption keys.

## Organizational and process terms

**Authority Level** — A metadata field indicating the institutional weight of a page. Values: `canonical` (authoritative, trusted), `standard` (reliable but not singular), `draft-only` (not production-ready).

**Chargeback** — The process of billing cloud infrastructure costs back to teams based on usage.

**Compliance Review** — An audit of access, systems, and processes to ensure they meet regulatory and policy requirements. Examples: PCI audit, SOC 2 audit, quarterly access reviews.

**Document Type** — A metadata field categorizing pages. Values: `procedure` (how-to steps), `policy` (rules and requirements), `reference` (definitions and lookup), `audit` (point-in-time findings), `glossary` (terminology), `faq`, `checklist`.

**Effective Date** — The date a page's content became accurate. Different from `last_updated` (which records when a page was edited, even if only for formatting).

**On-Call** — A rotating schedule of engineers available to respond to incidents, deployments, or urgent support requests 24/7.

**SLA** — Service Level Agreement. A commitment about response time and resolution time for requests or incidents.

**Supersedes / Superseded By** — A relationship indicating that one page replaces another. Used to mark outdated guidance.

## Compliance and security

**PCI DSS** — Payment Card Industry Data Security Standard. A compliance framework for systems that handle payment card data. Required for PaySure access.

**SOC 2** — Service Organization Control 2. A compliance audit for organizations handling customer data and information security.

**Two-Factor Authentication (2FA)** — A security mechanism requiring two pieces of evidence (password + code from phone/hardware key) to log in.

**Vault Operator** — A role in Vault that allows users to read, write, and delete secrets within their team namespace (but not create namespaces or manage access).

## Related pages

- Access request procedures: [Mosaic UI](page-01), [Orion](page-05), [PaySure](page-07), [Vault](page-15), [Northstar](page-12), [Atlas](page-09)
- Role catalogs: [Sentinel IAM Role Catalog](page-03), [Northstar CRM Role Matrix](page-11)
