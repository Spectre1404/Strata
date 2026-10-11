"""Raindrop signals. Owner: Talal (T3). Reviewer: Shiv.

Python SDK: raindrop-ai (pip). Verified against the installed 0.0.75 API
(docs: https://www.raindrop.ai/docs/sdk/python), not guessed.

Kinds (see docs/CONTRACTS.md): attempt_logged, audit_pass, audit_fail, blocked_query,
causality_fail, vault_opened, request_done, request_error.

Raindrop distinguishes events (raindrop.track_ai) from signals (raindrop.track_signal,
attached to an event by its event_id) -- send() emits one of each per call, both named
after `kind`, so a single call satisfies "a test event and a test signal appear".

core.config.env() raises on missing values, so the key is read with os.getenv directly:
if RAINDROP_WRITE_KEY is missing, send() does nothing and never raises. A Raindrop
failure (bad key, network, SDK validation) is swallowed the same way -- it must never
crash the caller.
"""
import os

KINDS = {
    "attempt_logged", "audit_pass", "audit_fail", "blocked_query",
    "causality_fail", "vault_opened", "request_done", "request_error",
}

_initialized = False


def send(kind: str, payload: dict) -> None:
    if kind not in KINDS:
        raise ValueError(f"Unknown signal kind {kind}")

    key = os.getenv("RAINDROP_WRITE_KEY")
    if not key:
        return

    global _initialized
    try:
        import raindrop.analytics as raindrop

        if not _initialized:
            raindrop.init(key)
            _initialized = True

        user_id = str(payload.get("session_id") or "system")
        event_id = raindrop.track_ai(
            user_id=user_id,
            event=kind,
            output=kind,
            properties=payload,
        )
        raindrop.track_signal(
            event_id=event_id,
            name=kind,
            properties=payload,
        )
    except Exception:
        pass
