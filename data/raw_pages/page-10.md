---
id: page-10
title: "Atlas Reporting – Data Dictionary"
space: ARCH
owner: "Data & Analytics Team"
status: current
document_type: reference
authority_level: standard
department: data-analytics
labels: [atlas, reference, data-model]
last_updated: 2026-06-20
effective_date: 2026-06-20
related: [page-09]
supersedes: []
superseded_by: []
url: "https://wiki.meridian.example/ARCH/Atlas+Reporting+Data+Dictionary"
---

# Atlas Reporting – Data Dictionary

This page defines the core entities and metrics available in Atlas. It is a reference guide for analysts and engineers building dashboards and reports.

## Core entities

### Transactions

- `transaction_id` — Unique identifier for each financial transaction processed by Meridian
- `amount` — Transaction amount in USD
- `currency` — Original currency (if applicable)
- `type` — Transaction type (transfer, payment, withdrawal, deposit, fee, etc.)
- `status` — Current status (pending, completed, failed, reversed)
- `created_at` — Timestamp of transaction initiation
- `settled_at` — Timestamp when transaction was settled (cleared by the bank)

### Accounts

- `account_id` — Unique identifier for each customer account
- `account_type` — Type of account (checking, savings, money market, etc.)
- `customer_id` — Reference to the customer record
- `balance` — Current account balance
- `created_at` — Account open date
- `status` — Account status (active, suspended, closed)

### Customers

- `customer_id` — Unique identifier
- `name` — Customer name
- `email` — Primary email address
- `phone` — Primary phone number
- `created_at` — Customer onboarding date
- `tier` — Customer segment (bronze, silver, gold, platinum)
- `total_assets` — AUM (assets under management)

## Key metrics

### Financial metrics

- `daily_transaction_volume` — Total transaction count per day
- `daily_transaction_value` — Total dollar amount per day
- `average_transaction_size` — Mean transaction amount
- `failed_transaction_rate` — Percentage of transactions that fail to settle
- `customer_lifetime_value` — Projected total revenue from a customer account

### Operational metrics

- `customer_acquisition_cost` — Average cost to acquire a new customer
- `churn_rate` — Percentage of customers who close accounts monthly
- `support_ticket_volume` — Count of support requests per day
- `mean_resolution_time` — Average time from support ticket creation to closure

## Data freshness and latency

- Transactional data: updated every 1 hour (2-hour lag from real-time)
- Customer data: updated daily (24-hour lag)
- Aggregate metrics: computed nightly, available by 6 AM ET

## Access controls

Sensitive fields (customer names, email, phone) are hidden from standard analysts. Contact the Data & Analytics Team if you need access to PII for a legitimate business reason.
