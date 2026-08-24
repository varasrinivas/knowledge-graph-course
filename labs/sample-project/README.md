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

Ground-truth relationships (check your graphs against these):
- `billing/app.py` imports `shared.auth.verify_token` and calls it on every route
- `verify_token` calls `decode_jwt` (same file)
- `billing/webhooks.py` calls `invoice.mark_paid` and `shared.events.publish`
- `notifications/worker.py` subscribes to the `payment.settled` event published by billing
- `orders/orders.py` calls `shared.db.DatabasePool.execute` and `shared.events.publish`
- `orders/metrics.py` reads `orders_fact` and excludes `internal_testers`
- The **god node** is `shared/db.py` (everything touches it); communities ≈ billing / orders / notifications
