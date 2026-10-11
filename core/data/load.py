"""Split at RESEARCH_END and load. Owner: Shiv (S1).

Rows with ts < RESEARCH_END go to research_bars. Rows with ts >= RESEARCH_END go to vault_bars.
Rows outside [RESEARCH_START, VAULT_END) are skipped. Vault-only pairs (D12) send nothing to
research_bars. Loading is insert-only; the caller (scripts/ingest.py, admin role) passes the db
and refuses to run if a target collection already has data.
"""
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from core.config import env
from core.data.binance import DATA_DIR, archive_dir, parse_klines

KINDS = ("spot", "premium")
BATCH = 10_000


@dataclass(frozen=True)
class Window:
    start: datetime   # RESEARCH_START
    cutoff: datetime  # RESEARCH_END: first Vault timestamp
    end: datetime     # VAULT_END, exclusive

    @classmethod
    def from_env(cls) -> "Window":
        def ts(name: str) -> datetime:
            return datetime.fromisoformat(env(name)).replace(tzinfo=timezone.utc)
        return cls(ts("RESEARCH_START"), ts("RESEARCH_END"), ts("VAULT_END"))


def split_at(df: pd.DataFrame, window: Window, in_research: bool) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return (research rows, vault rows). Vault-only pairs get an empty research frame."""
    research = df[(df.ts >= window.start) & (df.ts < window.cutoff)]
    vault = df[(df.ts >= window.cutoff) & (df.ts < window.end)]
    if not in_research:
        research = research.iloc[0:0]
    return research, vault


def read_bars(symbol: str, kind: str, interval: str = "1h", data_dir: Path = DATA_DIR,
              months: set[tuple[int, int]] | None = None) -> pd.DataFrame:
    """All local monthly files for one symbol and kind, sorted, duplicates dropped."""
    paths = sorted((data_dir / archive_dir(symbol, interval, kind)).glob("*.zip"))
    if months is not None:
        paths = [p for p in paths if (int(p.stem[-7:-3]), int(p.stem[-2:])) in months]
    if not paths:
        return pd.DataFrame(columns=["ts"])
    df = pd.concat([parse_klines(str(p), kind) for p in paths], ignore_index=True)
    return df.drop_duplicates("ts").sort_values("ts", ignore_index=True)


def to_documents(df: pd.DataFrame, symbol: str, kind: str) -> list[dict]:
    meta = {"symbol": symbol, "kind": kind}
    docs = []
    for row in df.to_dict("records"):
        row["ts"] = row["ts"].to_pydatetime()
        if "n" in row:
            row["n"] = int(row["n"])
        docs.append({"meta": meta, **row})
    return docs


def _insert(coll, docs: list[dict]) -> int:
    n = 0
    for i in range(0, len(docs), BATCH):
        n += len(coll.insert_many(docs[i:i + BATCH], ordered=True).inserted_ids)
    return n


def load_symbol(db, symbol: str, window: Window, in_research: bool, interval: str = "1h",
                data_dir: Path = DATA_DIR, months: set[tuple[int, int]] | None = None) -> dict:
    """Load spot and premium bars for one symbol.

    Return counts: {research: int, vault: int, kinds: {kind: {source, research, vault, skipped}}}.
    source is rows read from files (after de-duplication); source == research + vault + skipped.
    """
    kinds = {}
    for kind in KINDS:
        df = read_bars(symbol, kind, interval, data_dir, months)
        research, vault = split_at(df, window, in_research) if len(df) else (df, df)
        r = _insert(db.research_bars, to_documents(research, symbol, kind)) if len(research) else 0
        v = _insert(db.vault_bars, to_documents(vault, symbol, kind)) if len(vault) else 0
        kinds[kind] = {"source": len(df), "research": r, "vault": v, "skipped": len(df) - r - v}
    return {
        "research": sum(k["research"] for k in kinds.values()),
        "vault": sum(k["vault"] for k in kinds.values()),
        "kinds": kinds,
    }
