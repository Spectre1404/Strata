"""Causality check. Owner: Shiv (S3). Reviewer: Talal.

Why: the database blocks the Vault, but a pipeline can still peek at the next bar
inside the research window (for example a $setWindowFields window that reaches forward).
Statistics cannot catch this; Gencay (2026) shows a leaky strategy passes every test.

Test: for several cutoff dates c inside the research window,
  1. run the agent's pipeline on data with ts <= c (prepend a $match),
  2. run it on the full research window,
  3. compare signal values at timestamps <= c.
If any value differs beyond a tolerance, the pipeline used future rows: fail.
"""


def check(pipeline: list[dict], db, cutoffs: list) -> dict:
    """Return {"passed": bool, "mismatches": int}."""
    raise NotImplementedError("S3")
