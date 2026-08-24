---
type: table
title: orders_fact
description: One row per completed customer order; primary source of truth for revenue and activity metrics.
resource: ../../sample-project/services/orders/orders.py
tags: [analytics, orders, core-model]
timestamp: 2026-08-24T00:00:00Z
---

# orders_fact

One row is appended when an order reaches status `completed`
(`services/orders/orders.py::advance_order`).

## Schema
| Column | Type | Description |
|---|---|---|
| `order_id` | STRING | Globally unique order identifier |
| `customer_id` | STRING | The purchasing customer |
| `total_cents` | INTEGER | Order total in cents |
| `completed_at` | TIMESTAMP | ISO-8601 completion time (UTC) |

## Joins
Joined with the orders table on `order_id`; grouped by `customer_id` for activity metrics.

## Consumed By
- [Weekly Active Users](../metrics/weekly_active_users.md) — reads this table with a 7-day window and tester exclusions.
