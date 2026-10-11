"""Point-in-time universe. Owner: Shiv (S1). Rules in DECISIONS D12.

Month M's universe is the top UNIVERSE_SIZE eligible USDT pairs by quote volume summed over
the TRAILING months before M, among pairs with volume in each of the MIN_HISTORY months before M.
It uses only data before M. Eligible means an ASCII USDT pair whose base is not a stablecoin,
a fiat currency, a commodity-backed token, a wrapped or staked duplicate, a leveraged token,
or one of the named exclusions.

The pool is every pair in any month's universe (research and Vault months). Pairs in a research
month's universe are research pairs; pairs that first enter in the Vault window are Vault-only
and never reach research_bars. Universe rows are written for research months only, because the
researcher role can read `universe`.

Bars are loaded only for months where a pair is in the universe, plus LOOKBACK months before
each. Research and Vault sides are computed separately and clipped at the cutoff, so what is in
research_bars never depends on the Vault-window universe.
"""
from datetime import date, datetime, timezone

MIN_HISTORY = 6
TRAILING = 3
LOOKBACK = 3

STABLECOINS = {
    "USDC", "BUSD", "TUSD", "USDP", "PAX", "DAI", "FDUSD", "UST", "USDS", "USDSB", "SUSD",
    "USDD", "PYUSD", "EURI", "AEUR", "EURC", "USD1", "USDE", "RLUSD", "BFUSD", "XUSD",
}
FIAT = {
    "EUR", "GBP", "AUD", "TRY", "BRL", "RUB", "NGN", "UAH", "ZAR", "JPY", "MXN", "ARS",
    "PLN", "RON", "CZK", "COP", "KZT", "IDRT", "BIDR", "BKRW", "BVND",
}
COMMODITY = {"PAXG", "XAUT"}
WRAPPED = {"WBTC", "WBETH", "BETH"}
EXCLUDED = {"SNDKB", "SPCXB"}   # plus every non-ASCII symbol, e.g. 币安人生USDT
LEVERAGED_SUFFIXES = ("UP", "DOWN", "BULL", "BEAR")


def base_asset(symbol: str) -> str | None:
    return symbol[:-4] if symbol.endswith("USDT") and len(symbol) > 4 else None


def _is_leveraged(base: str, bases: set[str]) -> bool:
    """BTCUP, ETHBEAR, and the BTC tokens BULL and BEAR. JUP stays: J is not a listed base."""
    if base in ("BULL", "BEAR"):
        return True
    for suffix in LEVERAGED_SUFFIXES:
        if base.endswith(suffix) and base[:-len(suffix)] in bases:
            return True
    return False


def eligible_symbols(symbols: list[str]) -> list[str]:
    bases = {b for b in map(base_asset, symbols) if b}
    out = []
    for symbol in symbols:
        base = base_asset(symbol)
        if (not base or not symbol.isascii() or base in STABLECOINS or base in FIAT
                or base in COMMODITY or base in WRAPPED or base in EXCLUDED
                or _is_leveraged(base, bases)):
            continue
        out.append(symbol)
    return sorted(out)


def prev_month(month: date) -> date:
    return date(month.year - 1, 12, 1) if month.month == 1 else date(month.year, month.month - 1, 1)


def months_before(month: date, n: int) -> list[date]:
    """The n months before `month`, most recent first."""
    out, m = [], month
    for _ in range(n):
        m = prev_month(m)
        out.append(m)
    return out


def month_range(start: date, end_exclusive: date) -> list[date]:
    months, m = [], date(start.year, start.month, 1)
    while m < end_exclusive:
        months.append(m)
        m = date(m.year + 1, 1, 1) if m.month == 12 else date(m.year, m.month + 1, 1)
    return months


def rank_month(volumes: dict[str, dict[date, float]], month: date, size: int,
               min_history: int = MIN_HISTORY, trailing: int = TRAILING) -> list[str]:
    """Top `size` symbols by quote volume over the `trailing` months before `month`, among
    symbols with volume in each of the `min_history` months before it. Ties break by symbol."""
    history = months_before(month, max(min_history, trailing))
    scored = []
    for s, v in volumes.items():
        if any(v.get(m, 0.0) <= 0 for m in history[:min_history]):
            continue
        scored.append((sum(v.get(m, 0.0) for m in history[:trailing]), s))
    scored.sort(key=lambda x: (-x[0], x[1]))
    return [s for _, s in scored[:size]]


def monthly_universe(volumes: dict[str, dict[date, float]], months: list[date], size: int,
                     min_history: int = MIN_HISTORY, trailing: int = TRAILING) -> dict[date, list[str]]:
    return {m: rank_month(volumes, m, size, min_history, trailing) for m in months}


def short_months(universe: dict[date, list[str]], size: int) -> list[date]:
    """Months that ranked fewer than `size` pairs, e.g. because ranking files are missing."""
    return sorted(m for m, syms in universe.items() if len(syms) < size)


def split_pool(universe: dict[date, list[str]], cutoff: date) -> tuple[set[str], set[str]]:
    """Return (research_pairs, vault_only_pairs)."""
    research = {s for m, syms in universe.items() if m < cutoff for s in syms}
    everyone = {s for syms in universe.values() for s in syms}
    return research, everyone - research


def data_months(universe: dict[date, list[str]], start: date, cutoff: date, end: date,
                lookback: int = LOOKBACK) -> dict[str, set[date]]:
    """Months to download and load per symbol: each universe month plus `lookback` months before.

    Research-month memberships give months in [start, cutoff); Vault-month memberships give
    months in [cutoff, end). Neither side reaches across the cutoff.
    """
    out: dict[str, set[date]] = {}
    for m, syms in universe.items():
        lo, hi = (start, cutoff) if m < cutoff else (cutoff, end)
        wanted = {x for x in [m, *months_before(m, lookback)] if lo <= x < hi}
        for s in syms:
            out.setdefault(s, set()).update(wanted)
    return out


def build_universe(db, universe: dict[date, list[str]], cutoff: date) -> int:
    """Insert one `universe` row per research month (month < cutoff). Return rows written."""
    docs = [
        {"month": datetime(m.year, m.month, 1, tzinfo=timezone.utc), "symbols": syms}
        for m, syms in sorted(universe.items()) if m < cutoff
    ]
    if docs:
        db.universe.insert_many(docs)
    return len(docs)
