"""Invoice domain model for billing-service."""
from dataclasses import dataclass, field
from datetime import datetime, timezone

from shared.db import POOL


@dataclass
class Invoice:
    invoice_id: str
    customer_id: str
    amount_cents: int
    status: str = "pending"  # pending | paid | refunded
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


def create_invoice(customer_id: str, amount_cents: int) -> Invoice:
    if amount_cents <= 0:
        raise ValueError("amount_cents must be positive")
    inv = Invoice(
        invoice_id=f"inv_{len(POOL.tables['invoices']) + 1:06d}",
        customer_id=customer_id,
        amount_cents=amount_cents,
    )
    POOL.execute("invoices", inv.__dict__)
    return inv


def mark_paid(invoice_id: str) -> dict:
    rows = POOL.query("invoices", invoice_id=invoice_id)
    if not rows:
        raise KeyError(f"unknown invoice {invoice_id}")
    rows[0]["status"] = "paid"
    return rows[0]
