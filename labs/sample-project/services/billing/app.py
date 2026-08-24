"""billing-service HTTP API (FastAPI).

Routes:
  POST /invoices            create an invoice
  POST /webhooks/payment    payment-provider callback
"""
from fastapi import FastAPI, Header, HTTPException

from services.billing.invoice import create_invoice
from services.billing.webhooks import WebhookError, handle_payment_webhook
from shared.auth import AuthError, verify_token

app = FastAPI(title="billing-service")


@app.post("/invoices")
def post_invoice(body: dict, authorization: str | None = Header(default=None)):
    try:
        claims = verify_token(authorization)
    except AuthError as exc:
        raise HTTPException(status_code=401, detail=str(exc))

    try:
        inv = create_invoice(
            customer_id=claims["sub"],
            amount_cents=int(body["amount_cents"]),
        )
    except (KeyError, ValueError) as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    return inv.__dict__


@app.post("/webhooks/payment")
def post_payment_webhook(body: dict):
    try:
        return handle_payment_webhook(body)
    except WebhookError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
