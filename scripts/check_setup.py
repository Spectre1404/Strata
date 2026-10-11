"""Phase 0 gate: confirm each role can do what it should and nothing else.
Owner: Shiv (Phase 0). Runs against strata_test so it never touches live data.

Usage: python scripts/check_setup.py
Every row must show expected == actual.

Status: passed 21/21 against Atlas on Oct 11, 2026.
"""
import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pymongo.errors import OperationFailure  # noqa: E402
from core.db import get_db  # noqa: E402

# (role, action, collection, expected_allowed)
EXPECTATIONS = [
    ("researcher", "find", "research_bars", True),
    ("researcher", "find", "vault_bars", False),
    ("researcher", "find", "vault_openings", False),
    ("researcher", "insert", "trials", True),
    ("researcher", "update", "trials", False),
    ("researcher", "delete", "trials", False),
    ("researcher", "update", "preregistrations", False),
    ("researcher", "insert", "audits", False),
    ("auditor", "find", "vault_bars", True),
    ("auditor", "insert", "audits", True),
    ("auditor", "delete", "trials", False),
    ("strategist", "find", "vault_bars", False),
    ("strategist", "insert", "policies", True),
    ("grouper", "update", "trial_groups", True),
    ("grouper", "insert", "audits", False),
    ("worker", "update", "requests", True),
    ("worker", "find", "vault_bars", False),
    ("app", "find", "vault_bars", False),
    ("app", "find", "audits", True),
    ("app", "insert", "requests", True),
    ("app", "insert", "audits", False),
]


def attempt(role: str, action: str, collection: str) -> str:
    db = get_db(role, test=True)
    coll = db[collection]
    marker = {"_id": f"check-{uuid.uuid4()}", "fixture": True, "check": True}
    if collection == "trials":
        marker.update({"session_id": marker["_id"], "seq": 0})
    try:
        if action == "find":
            coll.find_one({})
        elif action == "insert":
            coll.insert_one(marker)
        elif action == "update":
            coll.update_one({"_id": "__no_such_doc__"}, {"$set": {"check": True}})
        elif action == "delete":
            coll.delete_one({"_id": "__no_such_doc__"})
        else:
            return "error: unknown action"
        return "allowed"
    except OperationFailure as exc:
        if exc.code == 13:  # Unauthorized
            return "denied"
        return f"error: {exc.code} {exc.details}"
    except Exception as exc:  # connection or config problems
        return f"error: {exc}"


def main() -> int:
    failures = 0
    print(f"{'role':<11} {'action':<7} {'collection':<17} {'expected':<9} actual")
    for role, action, collection, expected_allowed in EXPECTATIONS:
        result = attempt(role, action, collection)
        expected = "allowed" if expected_allowed else "denied"
        ok = result == expected
        failures += 0 if ok else 1
        flag = "" if ok else "   <-- MISMATCH"
        print(f"{role:<11} {action:<7} {collection:<17} {expected:<9} {result}{flag}")
    print(f"\n{len(EXPECTATIONS) - failures}/{len(EXPECTATIONS)} as expected")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
