"""Deterministic backtest. Owner: Shiv (S4). Reviewer: Talal.

Input: signal rows (ts, symbol, score) from the agent's pipeline.
Constructions: cs_rank (long top_k, short bottom_k, equal weight, rebalance every rebalance_bars)
and ts_sign (per symbol, long if score > 0, else short or flat).
Execution: positions set from the signal at bar t take effect at bar t+1.
Costs: (FEE_BPS + SPREAD_BPS) per unit of turnover.
Output: daily net returns over the research window, and metrics {sr, skew, kurt, t_obs, ann_return, turnover}.
"""


def run(signal, construction: dict, fee_bps: float, spread_bps: float) -> dict:
    raise NotImplementedError("S4")
