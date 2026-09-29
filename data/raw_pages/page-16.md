---
id: page-16
title: "Comet CI/CD Pipeline Access"
space: PLATFORM
owner: "DevOps Team"
status: current
document_type: procedure
authority_level: standard
department: devops
labels: [access-request, comet, cicd]
last_updated: 2026-07-09
effective_date: 2026-07-09
related: []
supersedes: []
superseded_by: []
url: "https://wiki.meridian.example/PLATFORM/Comet+CI+CD+Pipeline+Access"
---

# Comet CI/CD Pipeline Access

Comet is Meridian's continuous integration and continuous deployment (CI/CD) platform. It orchestrates build, test, and deployment workflows for all services.

## Who needs access

- Software engineers building and deploying services
- Platform engineers managing infrastructure and deployments
- DevOps engineers configuring pipelines and monitoring builds

Check with your team lead if you're unsure.

## How to request access

1. Open the ServiceNow Access Catalog and search for **"Comet Pipeline Access"**.
2. Specify your service or team name and the environments you need access to (dev, staging, prod).
3. Provide a brief justification (e.g. "backend engineer, need to deploy my service").
4. Your request routes to the **DevOps Team** for approval.

**SLA:** 1 business day

## Access levels

| Level | Capabilities | Typical user |
|---|---|---|
| Dev/Staging | Trigger builds and deployments, view logs, restart failed jobs | All engineers |
| Production | Deploy to production, manage traffic, trigger rollbacks | Senior engineers, tech leads, on-call engineers |
| Admin | Configure pipelines, manage secrets, add repositories, manage user access | DevOps team leads |

Production access requires your team lead's sign-off and may require additional approval if your service is business-critical.

## Comet basics

- Pipelines are defined in `.comet.yml` at the root of your service repository
- All builds are triggered automatically on git push; manual triggers are also supported
- Deployment gates require approval from the team lead or on-call engineer
- All actions are logged and auditable

## Troubleshooting

For failed builds, deployment issues, or questions about pipeline configuration, reach out in `#devops-support` on Slack or email **devops-team@meridian.example**.
