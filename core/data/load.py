"""Split at RESEARCH_END and load. Owner: Shiv (S1).

Rows with ts < RESEARCH_END go to research_bars. Rows with ts >= RESEARCH_END go to vault_bars.
Use the admin role for loading only.
"""


def load_symbol(symbol: str) -> dict:
    """Return counts: {research: int, vault: int}."""
    raise NotImplementedError("S1")
