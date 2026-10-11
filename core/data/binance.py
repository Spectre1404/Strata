"""Download and parse Binance public archive files. Owner: Shiv (S1).

Spot monthly klines:
  data/spot/monthly/klines/{SYMBOL}/{interval}/{SYMBOL}-{interval}-{YYYY}-{MM}.zip
USD-M futures premium-index klines:
  data/futures/um/monthly/premiumIndexKlines/{SYMBOL}/{interval}/{SYMBOL}-{interval}-{YYYY}-{MM}.zip
Each zip has a .CHECKSUM file (sha256). Hourly files are verified; ranking files are not (D12).

Gotcha: Binance spot timestamps from 2025-01-01 onward are in microseconds; earlier files use
milliseconds. Any spot value above 10^14 is microseconds and is divided by 1000. Futures premium
files stay in milliseconds. Everything becomes a UTC datetime before loading.

Raw files go in ./data/ (gitignored). Never commit them.
"""
import hashlib
import io
import re
import threading
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

import pandas as pd
import requests

BASE_URL = "https://data.binance.vision/"
LIST_URL = "https://s3-ap-northeast-1.amazonaws.com/data.binance.vision"
DATA_DIR = Path(__file__).resolve().parents[2] / "data"
US_THRESHOLD = 10**14
KLINE_COLUMNS = ["open_time", "o", "h", "l", "c", "v", "close_time", "qv", "n",
                 "taker_base", "taker_quote", "ignore"]
KIND_PREFIX = {
    "spot": "data/spot/monthly/klines",
    "premium": "data/futures/um/monthly/premiumIndexKlines",
}
_S3 = "{http://s3.amazonaws.com/doc/2006-03-01/}"
_MONTH_RE = re.compile(r"-(\d{4})-(\d{2})\.zip$")
_local = threading.local()


class ChecksumError(Exception):
    pass


def _session() -> requests.Session:
    """One session per thread; requests.Session is not thread-safe."""
    if not hasattr(_local, "session"):
        _local.session = requests.Session()
    return _local.session


def archive_dir(symbol: str, interval: str, kind: str) -> str:
    return f"{KIND_PREFIX[kind]}/{symbol}/{interval}"


def archive_path(symbol: str, interval: str, year: int, month: int, kind: str) -> str:
    return f"{archive_dir(symbol, interval, kind)}/{symbol}-{interval}-{year}-{month:02d}.zip"


def verify_checksum(data: bytes, checksum_text: str) -> None:
    expected = checksum_text.split()[0].strip().lower()
    actual = hashlib.sha256(data).hexdigest()
    if actual != expected:
        raise ChecksumError(f"sha256 {actual} != expected {expected}")


def download_month(symbol: str, interval: str, year: int, month: int, kind: str = "spot",
                   verify: bool = True, data_dir: Path = DATA_DIR) -> str:
    """Download one monthly file (checksum-verified when verify=True). Return the local path.

    An existing local file is reused; with verify=True it is re-checked first.
    """
    rel = archive_path(symbol, interval, year, month, kind)
    local = data_dir / rel
    session = _session()
    checksum = None
    if verify:
        r = session.get(BASE_URL + rel + ".CHECKSUM", timeout=60)
        r.raise_for_status()
        checksum = r.text
    if local.exists():
        if checksum is None:
            return str(local)
        try:
            verify_checksum(local.read_bytes(), checksum)
            return str(local)
        except ChecksumError:
            local.unlink()
    r = session.get(BASE_URL + rel, timeout=120)
    r.raise_for_status()
    if checksum is not None:
        verify_checksum(r.content, checksum)
    local.parent.mkdir(parents=True, exist_ok=True)
    tmp = local.with_suffix(".part")
    tmp.write_bytes(r.content)
    tmp.replace(local)
    return str(local)


def list_prefix(prefix: str) -> tuple[list[str], list[str]]:
    """List one level of the archive bucket. Return (sub-prefixes, keys), following pagination."""
    prefixes, keys, marker = [], [], ""
    while True:
        params = {"delimiter": "/", "prefix": prefix}
        if marker:
            params["marker"] = marker
        r = _session().get(LIST_URL, params=params, timeout=60)
        r.raise_for_status()
        root = ET.fromstring(r.content)
        page_prefixes = [p.text for p in root.iter(f"{_S3}Prefix") if p.text and p.text != prefix]
        page_keys = [k.text for k in root.iter(f"{_S3}Key") if k.text]
        prefixes += page_prefixes
        keys += page_keys
        if root.findtext(f"{_S3}IsTruncated") != "true":
            return prefixes, keys
        marker = root.findtext(f"{_S3}NextMarker") or (page_keys + page_prefixes)[-1]


def list_symbols(kind: str) -> list[str]:
    prefixes, _ = list_prefix(KIND_PREFIX[kind] + "/")
    return sorted(p.rstrip("/").rsplit("/", 1)[-1] for p in prefixes)


def list_months(symbol: str, interval: str, kind: str) -> list[tuple[int, int]]:
    """Months that exist in the archive for this symbol, as (year, month)."""
    _, keys = list_prefix(archive_dir(symbol, interval, kind) + "/")
    months = set()
    for key in keys:
        m = _MONTH_RE.search(key)
        if m:
            months.add((int(m.group(1)), int(m.group(2))))
    return sorted(months)


def to_utc(values: pd.Series, kind: str) -> pd.Series:
    """Raw open_time integers to UTC datetimes. Spot values above 10^14 are microseconds."""
    raw = values.astype("int64")
    if kind == "spot":
        raw = raw.where(raw <= US_THRESHOLD, raw // 1000)
    return pd.to_datetime(raw, unit="ms", utc=True)


def _read_csv(path: str) -> pd.DataFrame:
    with zipfile.ZipFile(path) as zf:
        data = zf.read(zf.namelist()[0])
    has_header = not data[:1].isdigit()
    df = pd.read_csv(io.BytesIO(data), header=0 if has_header else None)
    df = df.iloc[:, :len(KLINE_COLUMNS)]
    df.columns = KLINE_COLUMNS[:df.shape[1]]
    return df


def parse_klines(path: str, kind: str) -> pd.DataFrame:
    """Return ts (UTC), o, h, l, c, plus v, qv, n for spot. Handles ms and us timestamps."""
    df = _read_csv(path)
    out = pd.DataFrame({"ts": to_utc(df["open_time"], kind)})
    for col in ("o", "h", "l", "c"):
        out[col] = df[col].astype("float64")
    if kind == "spot":
        out["v"] = df["v"].astype("float64")
        out["qv"] = df["qv"].astype("float64")
        out["n"] = df["n"].astype("int64")
    return out
