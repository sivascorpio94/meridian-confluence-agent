---
id: page-06
title: "Orion Gateway Rate Limit Policy"
space: PLATFORM
owner: "API Platform Team"
status: current
document_type: policy
authority_level: standard
department: all
labels: [orion, policy, reference]
last_updated: 2026-06-15
effective_date: 2026-06-15
related: [page-05]
supersedes: []
superseded_by: []
url: "https://wiki.meridian.example/PLATFORM/Orion+Gateway+Rate+Limit+Policy"
---

# Orion Gateway Rate Limit Policy

This document defines the rate limiting policy for Orion Gateway consumers and the process for requesting limit adjustments.

## Standard rate limits

All API consumers connected to Orion Gateway are subject to the following limits:

| Metric | Standard | Burst (30s window) |
|---|---|---|
| Requests per minute | 1,000 | 5,000 |
| Concurrent connections | 100 per service | N/A |
| Request payload size | 10 MB | N/A |

These limits apply to all services equally and are enforced at the gateway level.

## Burst allowance

Orion Gateway allows temporary burst traffic up to 5,000 requests over a 30-second window. Bursts are tracked and counted toward your total request quota once the 30-second window closes. Plan accordingly when running batch jobs or migrations.

## Exceeding limits

If your service exceeds its rate limit:

1. The gateway returns HTTP 429 (Too Many Requests) for all subsequent requests
2. Requests are rejected immediately; no queueing or backoff is performed
3. Standard exponential backoff (2s, 4s, 8s, 16s...) is recommended for client implementations

## Requesting higher limits

Submit a request through ServiceNow:

1. Open **"Orion Gateway Rate Limit Exception"**
2. Provide your service name, current usage metrics, and business justification
3. Include projected peak traffic (requests/minute) for the next 12 months
4. The API Platform Team reviews within 2 business days and either approves or provides guidance

Limit increases are granted on a case-by-case basis and require API Platform Team sign-off. We do not raise limits without evidence of legitimate need.

## Monitoring your usage

Track your usage through the Orion dashboard:

1. Log in to **Orion Admin Portal** (https://orion-admin.meridian.example)
2. Navigate to **Consumer Dashboard** → **Your Service**
3. View 24-hour rolling usage, peak times, and historical trends
4. Set up alerts if your service approaches 80% of your limit

## Compliance

Rate limits are part of Meridian's platform stability and security posture. Attempting to circumvent limits (distributing requests across multiple API keys, using bot networks, etc.) is a violation of Meridian's security policy and may result in permanent access revocation.
