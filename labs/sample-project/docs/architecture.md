# orderflow architecture

Three services communicate through a synchronous in-process event bus (`shared/events.py`); persistence goes through a shared pool (`shared/db.py`).

- **billing-service** owns Invoice. Verifies every request via `shared.auth.verify_token`. On a `payment.succeeded` webhook it settles the invoice and publishes `payment.settled`.
- **orders-service** owns the order lifecycle and writes one `orders_fact` row per COMPLETED order. It also owns the canonical `weekly_active_users` metric (excludes internal testers — see `services/orders/metrics.py`).
- **notifications-service** subscribes to `payment.settled` (receipt) and `order.completed` (completion note).

Known wart: `shared/events.py` is the hub — all three services touch it, so a change to the bus contract reaches everything. `shared/db.py` is next (billing and orders); notifications never persists. A future ADR may split read/write pools.

## Metrics

**Weekly active users (WAU)** is calculated as the number of unique users with
any API call in a rolling 7-day window. Both the ops dashboard and the weekly
exec report read this figure, so keep the window aligned when you change it.
