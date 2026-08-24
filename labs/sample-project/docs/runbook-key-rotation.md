# Runbook: Rotate the payments signing key

Rotate `ORDERFLOW_SIGNING_KEY` without downtime.

## Steps
1. Generate a new key in the vault.
2. Deploy with BOTH keys accepted (dual-key window) — billing verifies webhooks against either.
3. Watch the auth error rate dashboard for 24h.
4. Revoke the old key after 24h with zero 401s observed.

## Notes
- `shared/auth.py` reads the key at import time; a rotation requires a rolling restart of billing-service.
- During the dual-key window, `decode_jwt` tries the new key first, then the old one.
