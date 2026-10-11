"""One connection per role. Owner: Shiv (Phase 0).

Code must ask for the narrowest role it needs. Only setup scripts use 'admin'.
"""
from pymongo import MongoClient
from core.config import env

ROLES = {"admin", "researcher", "auditor", "strategist", "grouper", "worker", "app"}
_clients: dict[str, MongoClient] = {}


def get_db(role: str, test: bool = False):
    if role not in ROLES:
        raise ValueError(f"Unknown role {role}")
    if role not in _clients:
        _clients[role] = MongoClient(env(f"MONGODB_URI_{role.upper()}"))
    name = env("MONGODB_DB_TEST") if test else env("MONGODB_DB")
    return _clients[role][name]
