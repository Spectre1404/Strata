"""Point-in-time universe. Owner: Shiv (S1).

For each month, pick the top UNIVERSE_SIZE USDT pairs by trailing quote volume,
using only data before that month. Write to the `universe` collection.
Check whether delisted pairs still have archive files; record the answer in DECISIONS.
"""


def build_universe(trailing_days: int = 30) -> int:
    raise NotImplementedError("S1")
