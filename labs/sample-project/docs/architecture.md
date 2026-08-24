# orderflow architecture

Three services communicate through a synchronous in-process event bus (`shared/events.py`); persistence goes through a shared pool (`shared/db.py`).

- **billing-service** owns Invoice. Verifies every request via `shared.auth.verify_token`. On a `payment.succeeded` webhook it settles the invoice and publishes `payment.settled`.
- **orders-service** owns the order lifecycle and writes one `orders_fact` row per COMPLETED order. It also owns the canonical `weekly_active_users` metric (excludes internal testers — see `services/orders/metrics.py`).
- **notifications-service** subscribes to `payment.settled` (receipt) and `order.completed` (completion note).

Known wart: `shared/db.py` is a god node — every service imports it. A future ADR may split read/write pools.

## Historical note (STALE — kept deliberately for the M02 lab)
An earlier revision of this doc defined WAU as "unique users with any API call in 7 days" with no tester exclusion. That definition is wrong; the canonical one lives in `services/orders/metrics.py`. This paragraph exists so a naive RAG pipeline can retrieve the stale definition — which is exactly what module M02 demonstrates.
