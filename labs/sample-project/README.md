# orderflow — sample monorepo for the Knowledge Graphs course

A deliberately small B2B order-tracking system. Every lab in the course extracts, curates, serves, or monitors knowledge about THIS repo, so you can verify every graph edge by hand.

```
sample-project/
├── services/
│   ├── billing/
│   │   ├── app.py          # FastAPI routes: invoices, webhooks
│   │   ├── invoice.py      # Invoice domain model + creation logic
│   │   └── webhooks.py     # payment webhook handling → publishes events
│   ├── orders/
│   │   ├── orders.py       # order lifecycle, writes orders_fact rows
│   │   └── metrics.py      # weekly_active_users (excludes internal testers)
│   └── notifications/
│       └── worker.py       # consumes billing events, sends notifications
├── shared/
│   ├── auth.py             # verify_token → decode_jwt
│   ├── db.py               # DatabasePool
│   └── events.py           # publish/subscribe event bus
└── docs/
    ├── runbook-key-rotation.md
    ├── architecture.md
    └── adr-001-event-bus.md
```

**Planted defect (for M02).** `docs/architecture.md` defines WAU as "any API call in
7 days" with no tester exclusion. That definition is **wrong** and deliberately left
unlabelled in the doc, because M02's whole lesson is that a naive retriever returns it
confidently and the reader has no way to tell. The canonical definition — unique
customers with a completed order, excluding internal testers — lives in
`services/orders/metrics.py`. This note sits here, outside `docs/`, so the M02 chunker
never retrieves it.

Ground-truth relationships (check your graphs against these):
- `billing/app.py` imports `shared.auth.verify_token` and calls it on every route
- `verify_token` calls `decode_jwt` (same file)
- `billing/webhooks.py` calls `invoice.mark_paid` and `shared.events.publish`
- `notifications/worker.py` subscribes to the `payment.settled` event published by billing
- `orders/orders.py` calls `shared.db.DatabasePool.execute` and `shared.events.publish`
- `orders/metrics.py` reads `orders_fact` and excludes `internal_testers`
- The **hub** is `shared/events.py` — the only module all three services touch (billing publishes, orders publishes, notifications subscribes). `shared/db.py` is next, reached by billing and orders only; notifications never persists anything. Communities ≈ billing / orders / notifications
- Module-level in-degree: `shared/events.py` 3, `shared/db.py` 2, `shared/auth.py` 1. Betweenness is **0 for every `shared/` module** — they are all sinks, so nothing routes *through* them. On a 14-module graph that measure has nothing to say; it only earns its keep at the scale of CAPSTONE-2's Java repo
