"""notifications-service: consumes billing and order events."""
from shared.events import subscribe

SENT: list[dict] = []  # in-memory outbox for the labs


def send_receipt(payload: dict) -> None:
    if "customer_id" not in payload:
        raise ValueError("payment.settled payload missing customer_id")
    SENT.append({
        "to": payload["customer_id"],
        "template": "receipt",
        "amount_cents": payload.get("amount_cents", 0),
    })


def send_completion_note(payload: dict) -> None:
    SENT.append({
        "to": payload.get("customer_id", "unknown"),
        "template": "order-completed",
        "order_id": payload.get("order_id"),
    })


def start() -> None:
    """Register all consumers. Called once at service boot."""
    subscribe("payment.settled", send_receipt)
    subscribe("order.completed", send_completion_note)
