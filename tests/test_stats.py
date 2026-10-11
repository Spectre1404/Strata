"""Known-answer tests for the Auditor. Target for S2 (Shiv). Talal reviews and runs them."""
import numpy as np
import pytest

from core.auditor import stats


def test_psr_is_half_when_sharpe_equals_benchmark():
    assert stats.psr(sr=0.0, t=1000, skew=0.0, kurt=3.0, sr_star=0.0) == pytest.approx(0.5)


def test_single_attempt_is_not_deflated():
    assert stats.expected_max_sr(1, var_sr=0.01) == 0.0
    a = stats.dsr(sr=0.05, t=1000, skew=0.0, kurt=3.0, n_trials=1, var_sr=0.01)
    b = stats.psr(sr=0.05, t=1000, skew=0.0, kurt=3.0, sr_star=0.0)
    assert a == pytest.approx(b)


def test_bar_rises_with_attempts():
    bars = [stats.expected_max_sr(n, var_sr=0.01) for n in (2, 10, 100, 1000)]
    assert bars == sorted(bars)


def test_bar_at_90_attempts_vs_18():
    # Same spread of results: the bar at 90 attempts is about 1.345x the bar at 18.
    ratio = stats.expected_max_sr(90, 0.01) / stats.expected_max_sr(18, 0.01)
    assert ratio == pytest.approx(1.345, abs=0.01)


def test_pbo_near_half_for_pure_noise():
    rng = np.random.default_rng(0)
    noise = rng.normal(0, 0.01, size=(1600, 40))
    assert 0.3 < stats.pbo_cscv(noise, s=16) < 0.7


def test_pbo_near_zero_with_one_real_edge():
    rng = np.random.default_rng(1)
    rets = rng.normal(0, 0.01, size=(1600, 40))
    rets[:, 0] += 0.004  # one planted edge
    assert stats.pbo_cscv(rets, s=16) < 0.1
