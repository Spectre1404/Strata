"""Strategist. Owner: Shiv (S9). Reviewer: Talal.

A policy is plain-English rules plus budgets
({per_family_max, preregister_first, stop_when_bar_exceeds_best}).
Score a policy on an inner split inside the research window:
short sessions on 2020-2022, audited on 2023-2024. Never read vault_bars.
Metric: results that pass the Auditor per 100 attempts, and the false-pass rate.
Promote a new version only if it scores higher; store every version in `policies`.
"""


def score_policy(version: int) -> dict:
    raise NotImplementedError("S9")
