# M07 Lab — The orderflow Bundle

**What you'll build**: the complete OKF bundle for orderflow — root `index.md`, five cross-linked concepts, `log.md` — validated by the M06 lint.
**Time**: 45–60 min · **Prerequisites**: M06 lab.

## Target structure
```
sample-project/knowledge/
├── index.md                      # the agent's pre-flight read
├── log.md
├── services/
│   ├── billing-service.md        # type: Service
│   ├── orders-service.md
│   └── notifications-service.md
└── analytics/
    ├── tables/orders_fact.md     # from M06
    └── metrics/weekly_active_users.md
```

## Step 1: Author the three Service concepts
Follow the canonical shape — swap Google's `# Schema` for `# Responsibilities` / `# Dependencies`:
```markdown
---
type: Service
title: billing-service
description: Handles invoicing and payment webhooks.
resource: services/billing
tags: [billing, payments, python]
timestamp: 2026-08-24T00:00:00Z
---
# Responsibilities
Owns the Invoice domain model. Verifies every request via shared auth.
# Dependencies
- Calls [shared auth](shared-libraries.md) to verify tokens.
- Publishes `payment.settled`, consumed by [notifications-service](notifications-service.md).
```
Rule that matters more than any field: keep the SAME body-section structure across all Service concepts — consistency is what agents parse.

## Step 2: Write index.md (one line per concept)
Title + one-line description pulled from frontmatter. An index bloated with detail defeats progressive disclosure — the whole point is that an agent reads THIS first and loads only what the task needs.

## Step 3: Cross-link both directions
billing-service links to notifications-service (publishes) AND notifications-service links back (consumes). One-directional links are how bundles silently rot.

## Step 4: Lint
```bash
python ../M06-okf-authoring/solution/validate.py knowledge
```
Expected: `5 concepts valid, 0 errors`.

## Step 5: Measure progressive disclosure
Count tokens (≈ chars/4): reading index.md + ONE concept vs reading the whole `services/` source tree. Even on this tiny repo the index path is smaller; on a thousand-file repo it is the difference between a working agent and a context overflow.
