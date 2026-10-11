"""Settings loaded from .env. Owner: Shiv (Phase 0)."""
import os
from dotenv import load_dotenv

load_dotenv()


def env(name: str, default: str | None = None) -> str:
    value = os.getenv(name, default)
    if value is None or value == "":
        raise RuntimeError(f"Missing setting {name}. Fill it in .env (see .env.example).")
    return value
