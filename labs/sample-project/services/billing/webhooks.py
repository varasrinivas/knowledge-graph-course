"""Payment-provider webhook handling for billing-service.

Verifies, settles the invoice, then publishes payment.settled for
notifications-service to consume.
"""
from services.billing.invoice import mark_paid
from shared.events import publish


class WebhookError(Exception):
    """Raised when a webhook payload cannot be processed."""


def handle_payment_webhook(payload: dict) -> dict:
    event_type = payload.get("type")
    if event_type != "payment.succeeded":
        raise WebhookError(f"unsupported webhook type: {event_type!r}")

    invoice_id = payload.get("invoice_id")
    if not invoice_id:
        raise WebhookError("payload missing invoice_id")

    try:
        invoice = mark_paid(invoice_id)
    except KeyError as exc:
        raise WebhookError(str(exc)) from exc

    publish("payment.settled", {
        "invoice_id": invoice["invoice_id"],
        "customer_id": invoice["customer_id"],
        "amount_cents": invoice["amount_cents"],
    })
    return invoice
