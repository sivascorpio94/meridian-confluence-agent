# Security and Responsible Demonstration

## Data boundary

This repository uses fictional Meridian Financial Group content and a personal
Confluence Cloud site. Do not connect it to an employer or client knowledge
base without written authorization, approved data handling, and an enterprise
security review.

## Secrets

- Never commit `.env`, Atlassian API tokens, AWS credentials, or login caches.
- Rotate any credential accidentally printed, recorded, or committed.
- Local Docker mounts AWS configuration only for development.
- Production workloads must use workload identity such as an ECS task role.
- Store production secrets in Secrets Manager or an equivalent approved store.

## Public-demo controls

Before exposing the API publicly, add authentication, per-IP and per-user rate
limits, request-size limits, usage quotas, abuse monitoring, budget alarms, and
an allowlist of permitted Bedrock models. Do not expose the current development
API directly to the internet.

## Reporting

Do not include live credentials or sensitive data in a public issue. Revoke the
credential first, then provide a sanitized reproduction.
