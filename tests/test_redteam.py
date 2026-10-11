"""Red-team tests: try to break every rule. Owner: Talal (T2). Reviewer: Shiv.

Run against strata_test. Each test must FAIL to break the rule (the attack is denied or caught).
Replace each pytest.skip with a real attack.
"""
import pytest


def test_researcher_cannot_read_vault():
    pytest.skip("T2: connect as researcher, find_one on vault_bars, expect Unauthorized")


def test_researcher_cannot_read_vault_through_aggregation():
    pytest.skip("T2: try $lookup or $unionWith into vault_bars via the query tool; expect rejection and a `blocked` row")


def test_researcher_cannot_edit_or_delete_attempts():
    pytest.skip("T2: update_one and delete_one on trials and preregistrations; expect Unauthorized")


def test_tampered_record_breaks_chain():
    pytest.skip("T2: copy a session's records to a scratch collection, change one metric, expect verify_chain False")


def test_app_cannot_read_vault():
    pytest.skip("T2: connect as app, find_one on vault_bars, expect Unauthorized")


def test_vault_budget_enforced():
    pytest.skip("T2 after S8: open the Vault past VAULT_OPEN_BUDGET in strata_test; expect refusal")


def test_lookahead_pipeline_rejected():
    pytest.skip("T2 after S3: a $setWindowFields window reaching one bar forward; expect causality fail")
