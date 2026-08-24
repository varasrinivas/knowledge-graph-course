---
type: metric
title: Weekly Active Users (WAU)
description: Unique customers with at least one completed order in a rolling 7-day window, excluding internal test accounts.
resource: ../../sample-project/services/orders/metrics.py
tags: [analytics, orders, canonical]
timestamp: 2026-08-24T00:00:00Z
---

# Weekly Active Users (WAU)

The total unique count of `customer_id` values with **at least one completed
order** whose `completed_at` falls inside a rolling 7-day window ending at the
evaluation time.

## Computation Rules
- Source of truth: `services/orders/metrics.py::weekly_active_users` (the attested computation).
- **Excludes internal test accounts**: `cust_qa_1`, `cust_qa_2`, `cust_loadtest`.
- Malformed `orders_fact` rows are skipped, never counted.

## Related Components
- See [orders_fact](../tables/orders_fact.md) for the fact table this metric reads.
