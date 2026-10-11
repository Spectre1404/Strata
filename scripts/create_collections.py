"""Create collections and indexes in strata and strata_test. Admin role only. Run once."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pymongo import ASCENDING
from core.db import get_db

TIME_SERIES = ["research_bars", "vault_bars"]
REGULAR = ["universe", "sessions", "preregistrations", "trials", "trial_returns",
           "trial_groups", "audits", "vault_openings", "blocked", "requests", "policies"]


def setup(test: bool) -> None:
    db = get_db("admin", test=test)
    existing = set(db.list_collection_names())
    for name in TIME_SERIES:
        if name not in existing:
            db.create_collection(name, timeseries={"timeField": "ts", "metaField": "meta", "granularity": "hours"})
    for name in REGULAR:
        if name not in existing:
            db.create_collection(name)
    db.trials.create_index([("session_id", ASCENDING), ("seq", ASCENDING)], unique=True)
    db.sessions.create_index([("session_id", ASCENDING), ("event", ASCENDING)], unique=True)
    db.trial_returns.create_index([("trial_id", ASCENDING)], unique=True)
    db.trial_groups.create_index([("trial_id", ASCENDING)], unique=True)
    db.audits.create_index([("trial_id", ASCENDING)])
    db.requests.create_index([("status", ASCENDING), ("ts", ASCENDING)])
    print(db.name, sorted(db.list_collection_names()))


if __name__ == "__main__":
    setup(test=False)
    setup(test=True)
