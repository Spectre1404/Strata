"""S1 data ingest tests. Local only: no network, no Atlas."""
import hashlib
import zipfile
from datetime import date, datetime, timezone
from types import SimpleNamespace

import pandas as pd
import pytest

from core.data import binance, universe as uni
from core.data.load import Window, load_symbol, split_at, to_documents

UTC = timezone.utc
WINDOW = Window(datetime(2020, 1, 1, tzinfo=UTC), datetime(2025, 1, 1, tzinfo=UTC),
                datetime(2026, 10, 1, tzinfo=UTC))

DEC_31_2024_MS = 1735603200000        # 2024-12-31 00:00 UTC, spot files before 2025
JAN_01_2025_US = 1735689600000000     # 2025-01-01 00:00 UTC, spot files from 2025 on
JAN_01_2025_MS = 1735689600000        # 2025-01-01 00:00 UTC, futures premium files
HOUR_MS = 3_600_000


def kline(open_time, step, close=100.0):
    return [open_time, close, close + 1, close - 1, close, 10.0, open_time + step - 1,
            1000.0, 42, 5.0, 500.0, 0]


def write_zip(path, rows, header=False):
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = []
    if header:
        lines.append(",".join(["open_time", "open", "high", "low", "close", "volume", "close_time",
                               "quote_volume", "count", "taker_buy_volume",
                               "taker_buy_quote_volume", "ignore"]))
    lines += [",".join(str(x) for x in r) for r in rows]
    with zipfile.ZipFile(path, "w") as zf:
        zf.writestr(path.with_suffix(".csv").name, "\n".join(lines) + "\n")
    return path


def write_month(data_dir, symbol, kind, year, month, rows, header=False):
    return write_zip(data_dir / binance.archive_path(symbol, "1h", year, month, kind), rows, header)


class FakeDB:
    def __init__(self):
        self.inserted = {}

    def __getattr__(self, name):
        def insert_many(docs, ordered=True):
            self.inserted.setdefault(name, []).extend(docs)
            return SimpleNamespace(inserted_ids=list(range(len(docs))))
        return SimpleNamespace(insert_many=insert_many)


def frame(*stamps):
    return pd.DataFrame({"ts": pd.to_datetime(list(stamps), utc=True), "c": 1.0})


# Timestamps

def test_spot_bars_from_dec_2024_ms_and_jan_2025_us_convert_to_right_dates(tmp_path):
    dec = write_zip(tmp_path / "dec.zip", [kline(DEC_31_2024_MS, HOUR_MS)])
    jan = write_zip(tmp_path / "jan.zip", [kline(JAN_01_2025_US, HOUR_MS * 1000)])
    assert binance.parse_klines(str(dec), "spot").ts.iloc[0] == pd.Timestamp("2024-12-31 00:00", tz="UTC")
    assert binance.parse_klines(str(jan), "spot").ts.iloc[0] == pd.Timestamp("2025-01-01 00:00", tz="UTC")


def test_spot_threshold_is_ten_to_the_fourteenth():
    raw = pd.Series([DEC_31_2024_MS, JAN_01_2025_US, 10**14, 10**14 + 1])
    ts = binance.to_utc(raw, "spot")
    assert ts.iloc[0] == pd.Timestamp("2024-12-31", tz="UTC")
    assert ts.iloc[1] == pd.Timestamp("2025-01-01", tz="UTC")
    assert ts.iloc[2] == pd.Timestamp(10**14, unit="ms", tz="UTC")
    assert ts.iloc[3] == pd.Timestamp(10**11, unit="ms", tz="UTC")


def test_premium_jan_2025_stays_in_ms_and_header_is_skipped(tmp_path):
    path = write_zip(tmp_path / "prem.zip", [kline(JAN_01_2025_MS, HOUR_MS, close=0.0001)], header=True)
    df = binance.parse_klines(str(path), "premium")
    assert df.ts.iloc[0] == pd.Timestamp("2025-01-01 00:00", tz="UTC")
    assert list(df.columns) == ["ts", "o", "h", "l", "c"]


def test_spot_columns_and_types(tmp_path):
    path = write_zip(tmp_path / "s.zip", [kline(DEC_31_2024_MS, HOUR_MS)])
    df = binance.parse_klines(str(path), "spot")
    assert list(df.columns) == ["ts", "o", "h", "l", "c", "v", "qv", "n"]
    assert df.qv.iloc[0] == 1000.0 and df.n.iloc[0] == 42


def test_documents_use_native_types():
    df = pd.DataFrame({"ts": pd.to_datetime([DEC_31_2024_MS], unit="ms", utc=True),
                       "o": [1.0], "h": [1.0], "l": [1.0], "c": [1.0], "v": [1.0], "qv": [1.0], "n": [3]})
    doc = to_documents(df, "BTCUSDT", "spot")[0]
    assert type(doc["ts"]) is datetime and doc["ts"].tzinfo is not None
    assert type(doc["n"]) is int
    assert doc["meta"] == {"symbol": "BTCUSDT", "kind": "spot"}


# Checksums

def test_checksum_mismatch_raises():
    data = b"klines"
    binance.verify_checksum(data, f"{hashlib.sha256(data).hexdigest()}  X.zip\n")
    with pytest.raises(binance.ChecksumError):
        binance.verify_checksum(b"tampered", f"{hashlib.sha256(data).hexdigest()}  X.zip\n")


# Split at RESEARCH_END

def test_split_puts_last_2024_hour_in_research_and_first_2025_hour_in_vault():
    research, vault = split_at(frame("2024-12-31 23:00", "2025-01-01 00:00"), WINDOW, in_research=True)
    assert list(research.ts) == [pd.Timestamp("2024-12-31 23:00", tz="UTC")]
    assert list(vault.ts) == [pd.Timestamp("2025-01-01 00:00", tz="UTC")]


def test_split_skips_rows_outside_the_window():
    research, vault = split_at(frame("2019-12-31 23:00", "2020-01-01 00:00", "2026-09-30 23:00",
                                     "2026-10-01 00:00"), WINDOW, in_research=True)
    assert len(research) == 1 and len(vault) == 1


# Universe and pool

def test_eligible_symbols_drop_stablecoins_fiat_commodity_wrapped_and_leveraged_tokens():
    symbols = ["BTCUSDT", "ETHUSDT", "JUPUSDT", "USDCUSDT", "FDUSDUSDT", "EURUSDT", "TRYUSDT",
               "PAXGUSDT", "XAUTUSDT", "WBTCUSDT", "WBETHUSDT", "BETHUSDT",
               "BTCUPUSDT", "ETHDOWNUSDT", "BULLUSDT", "ETHBEARUSDT", "BTCBUSD"]
    assert uni.eligible_symbols(symbols) == ["BTCUSDT", "ETHUSDT", "JUPUSDT"]


def test_rank_uses_only_the_previous_month():
    volumes = {"AUSDT": {date(2020, 1, 1): 5.0, date(2020, 2, 1): 1.0},
               "BUSDT": {date(2020, 1, 1): 1.0, date(2020, 2, 1): 1e12}}
    assert uni.rank_month(volumes, date(2020, 2, 1), size=1) == ["AUSDT"]


def test_month_with_missing_ranking_files_is_reported_short():
    volumes = {f"P{i}USDT": {date(2024, 2, 1): float(i + 1)} for i in range(3)}
    universe = uni.monthly_universe(volumes, [date(2024, 3, 1), date(2024, 4, 1)], size=3)
    assert uni.short_months(universe, size=3) == [date(2024, 4, 1)]


def test_pair_first_ranked_in_2025_is_excluded_from_research_bars(tmp_path):
    universe = {date(2024, 12, 1): ["BTCUSDT"], date(2025, 1, 1): ["BTCUSDT"],
                date(2025, 2, 1): ["BTCUSDT", "NEWUSDT"]}
    research_pairs, vault_only = uni.split_pool(universe, cutoff=date(2025, 1, 1))
    assert research_pairs == {"BTCUSDT"} and vault_only == {"NEWUSDT"}

    for sym in ("BTCUSDT", "NEWUSDT"):
        write_month(tmp_path, sym, "spot", 2024, 12, [kline(DEC_31_2024_MS, HOUR_MS)])
        write_month(tmp_path, sym, "spot", 2025, 1, [kline(JAN_01_2025_US, HOUR_MS * 1000)])
    db = FakeDB()
    new = load_symbol(db, "NEWUSDT", WINDOW, "NEWUSDT" in research_pairs, data_dir=tmp_path)
    assert new["research"] == 0 and new["vault"] == 1
    assert new["kinds"]["spot"] == {"source": 2, "research": 0, "vault": 1, "skipped": 1}
    assert "research_bars" not in db.inserted

    btc = load_symbol(db, "BTCUSDT", WINDOW, "BTCUSDT" in research_pairs, data_dir=tmp_path)
    assert btc["research"] == 1 and btc["vault"] == 1
    assert {d["meta"]["symbol"] for d in db.inserted["research_bars"]} == {"BTCUSDT"}
    assert {d["meta"]["symbol"] for d in db.inserted["vault_bars"]} == {"BTCUSDT", "NEWUSDT"}


def test_universe_rows_only_for_research_months():
    universe = {date(2024, 11, 1): ["A"], date(2024, 12, 1): ["B"], date(2025, 1, 1): ["C"]}
    db = FakeDB()
    assert uni.build_universe(db, universe, cutoff=date(2025, 1, 1)) == 2
    assert [d["month"] for d in db.inserted["universe"]] == [
        datetime(2024, 11, 1, tzinfo=UTC), datetime(2024, 12, 1, tzinfo=UTC)]
