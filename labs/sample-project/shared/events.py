"""Minimal synchronous event bus shared by all services."""
from collections import defaultdict
from typing import Callable

_subscribers: dict[str, list[Callable[[dict], None]]] = defaultdict(list)


def subscribe(topic: str, handler: Callable[[dict], None]) -> None:
    _subscribers[topic].append(handler)


def publish(topic: str, payload: dict) -> int:
    """Deliver payload to every subscriber. Returns delivery count.

    A failing handler is logged and skipped — one bad consumer must not
    block billing from settling payments.
    """
    delivered = 0
    for handler in _subscribers.get(topic, []):
        try:
            handler(payload)
            delivered += 1
        except Exception as exc:  # noqa: BLE001 - isolate consumer failures
            print(f"[events] handler {handler.__name__} failed on {topic}: {exc}")
    return delivered
