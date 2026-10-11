"""Open the Vault for one attempt. Owner: Shiv (S8). Reviewer: Talal.

Only the auditor role can read vault_bars. Every opening is recorded in vault_openings
and counts against VAULT_OPEN_BUDGET. Test in strata_test only during the build.
"""


def open_vault(trial_id: str, requested_by: str) -> dict:
    raise NotImplementedError("S8")
