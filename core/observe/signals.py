"""Raindrop signals. Owner: Talal (T3). Reviewer: Shiv.

Python SDK: pip install raindrop-ai. Check the docs for init and signal calls.
Kinds (see docs/CONTRACTS.md): attempt_logged, audit_pass, audit_fail, blocked_query,
causality_fail, vault_opened, request_done, request_error.

If RAINDROP_WRITE_KEY is missing, send() does nothing and never raises.
"""

KINDS = {
    "attempt_logged", "audit_pass", "audit_fail", "blocked_query",
    "causality_fail", "vault_opened", "request_done", "request_error",
}


def send(kind: str, payload: dict) -> None:
    if kind not in KINDS:
        raise ValueError(f"Unknown signal kind {kind}")
    raise NotImplementedError("T3")
