"""Order lifecycle for orders-service. Writes one orders_fact row per completed order."""
from datetime import datetime, timezone

from shared.db import POOL
from shared.events import publish

VALID_TRANSITIONS = {
    "pending": {"confirmed", "cancelled"},
    "confirmed": {"shipped", "cancelled"},
    "shipped": {"completed"},
}


def create_order(order_id: str, customer_id: str, total_cents: int) -> dict:
    order = {
        "order_id": order_id,
        "customer_id": customer_id,
        "total_cents": total_cents,
        "status": "pending",
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    POOL.execute("orders", order)
    return order


def advance_order(order_id: str, new_status: str) -> dict:
    rows = POOL.query("orders", order_id=order_id)
    if not rows:
        raise KeyError(f"unknown order {order_id}")
    order = rows[0]
    allowed = VALID_TRANSITIONS.get(order["status"], set())
    if new_status not in allowed:
        raise ValueError(f"cannot go {order['status']} -> {new_status}")

    order["status"] = new_status
    order["updated_at"] = datetime.now(timezone.utc).isoformat()

    if new_status == "completed":
        # orders_fact: one row per completed customer order (see docs + OKF concept)
        POOL.execute("orders_fact", {
            "order_id": order["order_id"],
            "customer_id": order["customer_id"],
            "total_cents": order["total_cents"],
            "completed_at": order["updated_at"],
        })
        publish("order.completed", order)
    return order
