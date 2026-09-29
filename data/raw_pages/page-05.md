---
id: page-05
title: "Orion Gateway Access & API Key Provisioning"
space: PLATFORM
owner: "API Platform Team"
status: current
document_type: procedure
authority_level: standard
department: all
labels: [access-request, orion, api-keys]
last_updated: 2026-07-12
effective_date: 2026-07-12
related: [page-06]
supersedes: []
superseded_by: []
url: "https://wiki.meridian.example/PLATFORM/Orion+Gateway+Access+API+Key+Provisioning"
---

# Orion Gateway Access & API Key Provisioning

Orion Gateway is Meridian's API gateway for internal service-to-service communication. To integrate your service with Orion, you need API consumer access and an API key.

## How to request access

1. Open the ServiceNow Access Catalog and search for **"Orion Gateway Consumer Access"**.
2. Provide your service name, the API endpoints you need to call, and a brief technical justification.
3. Your request routes to the **API Platform Team** for review.
4. Upon approval, an API key is generated and delivered to you securely via ServiceNow.

**SLA:** 2 business days

## API key management

- Each service gets one API key per environment (dev, staging, prod).
- Store your API key securely using Vault (see [Requesting a Vault Namespace](page-06) for details).
- API keys are rotated annually as part of Meridian's security compliance process.
- If your key is compromised, request an immediate rotation through ServiceNow.

## Rate limiting

Orion Gateway enforces rate limits on all consumers:

- Default: 1,000 requests per minute per service
- Burst: up to 5,000 requests over a 30-second window
- Higher limits available upon request; contact the API Platform Team

## Revoke access

If you no longer need Orion Gateway access:

1. Open the ServiceNow Access Catalog and search for **"Orion Gateway Consumer Access"**.
2. Select **"Revoke"** from the request type dropdown.
3. Confirm your service name and the API key(s) to revoke.
4. Your access is revoked immediately and the key is invalidated.

## Troubleshooting

For connection issues, authentication errors, or rate limit questions, reach out in `#api-platform-support` on Slack or email **api-platform@meridian.example**.
