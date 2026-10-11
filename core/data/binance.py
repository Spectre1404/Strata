"""Download Binance public archive files. Owner: Shiv (S1).

Spot monthly klines URL pattern:
  https://data.binance.vision/data/spot/monthly/klines/{SYMBOL}/{interval}/{SYMBOL}-{interval}-{YYYY}-{MM}.zip
Each zip has a .CHECKSUM file; verify it.

USD-M futures premium-index klines: confirm the exact path on data.binance.vision before coding.

Gotcha: Binance states spot timestamps from 2025-01-01 onward are in microseconds.
Earlier files use milliseconds. RESEARCH_END is 2025-01-01, so the Vault side uses the new unit.
Normalize everything to UTC datetimes before loading.

Raw files go in ./data/ (gitignored). Never commit them.
"""


def download_month(symbol: str, interval: str, year: int, month: int, kind: str = "spot") -> str:
    """Download and checksum-verify one monthly file. Return the local path."""
    raise NotImplementedError("S1")


def parse_klines(path: str, kind: str):
    """Return a DataFrame with ts (UTC), o, h, l, c, v, qv, n. Handle ms and us timestamps."""
    raise NotImplementedError("S1")
