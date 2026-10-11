"""Audit one attempt. Owner: Shiv (S2/S5). Reviewer: Talal.

Compute DSR three ways: n_session (attempts in this session), n_total (all attempts in Strata),
n_effective (distinct numeric groups, from T5). Failed-causality attempts count toward n.
Write one document to `audits`. Send audit_pass or audit_fail.
"""


def audit_trial(trial_id: str) -> dict:
    raise NotImplementedError("S2/S5")
