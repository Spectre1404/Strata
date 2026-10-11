"""Strata: the permanent record of attempts. Owner: Shiv.

Records are insert-only (enforced by the researcher role) and hash-chained per session:
  hash = sha256(prev_hash + canonical_json(record without 'hash'))
canonical_json = json.dumps(record, sort_keys=True, separators=(",", ":"), default=str)
The first record in a session uses prev_hash = "GENESIS".
"""
import hashlib
import json


def canonical_json(record: dict) -> str:
    return json.dumps(record, sort_keys=True, separators=(",", ":"), default=str)


def compute_hash(prev_hash: str, record: dict) -> str:
    body = {k: v for k, v in record.items() if k != "hash"}
    return hashlib.sha256((prev_hash + canonical_json(body)).encode()).hexdigest()


def append_trial(db, trial: dict) -> str:
    """Set seq, prev_hash, hash; insert into trials. Return hash.
    On a duplicate (session_id, seq) error, re-read the last record and retry."""
    raise NotImplementedError("S5")


def verify_chain(db, session_id: str) -> bool:
    raise NotImplementedError("S5")
