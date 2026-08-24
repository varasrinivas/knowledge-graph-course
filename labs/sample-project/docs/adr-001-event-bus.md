# ADR-001: In-process event bus over a message broker

**Status**: accepted (2026-05-14)

## Context
orderflow needs billing → notifications decoupling, but runs as a single deployable in the labs.

## Decision
Use a synchronous in-process bus (`shared/events.py`). Handlers are isolated: one failing consumer is logged and skipped so billing settlement never blocks on notifications.

## Consequences
- Simple, deterministic, easy to graph.
- No durability: events are lost on crash. If orderflow ever runs multi-process, replace with a broker and update the `payment.settled` contract concept in the OKF bundle (M08's enrichment hook should catch this file changing).
