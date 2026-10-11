"""Raindrop signals. Owner: Talal (T3). Reviewer: Shiv.

Python SDK: raindrop-ai (pip). Verified against the installed 0.0.75 API
(docs: https://www.raindrop.ai/docs/sdk/python), not guessed.

Kinds (see docs/CONTRACTS.md): attempt_logged, audit_pass, audit_fail, blocked_query,
causality_fail, vault_opened, request_done, request_error.

Raindrop distinguishes events (raindrop.track_ai) from signals (raindrop.track_signal,
attached to an event by its event_id) -- send() emits one of each per call, both named
after `kind`, so a single call satisfies "a test event and a test signal appear".

core.config is imported here (not just relied on elsewhere) so .env is loaded even when
a standalone script imports this module directly without importing core.config/core.db
first -- otherwise RAINDROP_WRITE_KEY reads as unset and send() no-ops silently with no
indication why. core.config.env() itself raises on missing values, so the key is still
read with os.getenv directly: if RAINDROP_WRITE_KEY is missing, send() does nothing and
never raises, but now logs a warning so a missing key is visible instead of silent.

A Raindrop failure (bad key, network, SDK validation) is swallowed the same way -- it
must never crash the caller -- but is also logged, with the kind and the exception's
type only. Never the payload or the key.
"""
import json
import logging
import os

import core.config  # noqa: F401 -- side effect: loads .env
import raindrop.analytics as raindrop

logger = logging.getLogger(__name__)

KINDS = {
    "attempt_logged", "audit_pass", "audit_fail", "blocked_query",
    "causality_fail", "vault_opened", "request_done", "request_error",
}

# Dropped wherever they appear in a payload's dotted key path, case-insensitive --
# a connection string or API key can then never be sent to Raindrop by accident.
SECRET_MARKERS = ("uri", "password", "secret", "token", "key")

_initialized = False


def _flatten(payload: dict, prefix: str = "") -> dict:
    """Flatten a payload into a flat dict of str|int|bool|float for Raindrop's
    `properties` field, which doesn't accept nested values.

    Nested dicts become dotted keys. Lists/tuples become a JSON string. None
    values are dropped. Numpy scalars, datetimes, and anything else unknown
    are coerced to a plain value. Keys matching SECRET_MARKERS anywhere in
    their dotted path are dropped, not just stringified.
    """
    flat: dict = {}
    for key, value in payload.items():
        dotted = f"{prefix}{key}"
        if any(marker in dotted.lower() for marker in SECRET_MARKERS):
            continue
        if value is None:
            continue
        if isinstance(value, dict):
            flat.update(_flatten(value, prefix=f"{dotted}."))
        elif isinstance(value, (list, tuple)):
            flat[dotted] = json.dumps(value, default=str)
        elif isinstance(value, (str, int, bool, float)):
            flat[dotted] = value
        elif hasattr(value, "item"):  # numpy scalar
            flat[dotted] = value.item()
        elif hasattr(value, "isoformat"):  # date/datetime
            flat[dotted] = value.isoformat()
        else:
            flat[dotted] = str(value)
    return flat


def send(kind: str, payload: dict) -> None:
    if kind not in KINDS:
        raise ValueError(f"Unknown signal kind {kind}")

    key = os.getenv("RAINDROP_WRITE_KEY")
    if not key:
        logger.warning("Raindrop signal %r dropped: RAINDROP_WRITE_KEY is not set", kind)
        return

    global _initialized
    try:
        if not _initialized:
            raindrop.init(key)
            _initialized = True

        flat = _flatten(payload)
        user_id = str(payload.get("session_id") or "system")
        event_id = raindrop.track_ai(
            user_id=user_id,
            event=kind,
            output=kind,
            properties=flat,
        )
        raindrop.track_signal(
            event_id=event_id,
            name=kind,
            properties=flat,
        )
    except Exception as exc:
        logger.warning("Raindrop signal %r failed: %s", kind, type(exc).__name__)
