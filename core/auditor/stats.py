"""Auditor statistics. Owner: Shiv (S2). Reviewer: Talal.

All Sharpe ratios here are per-observation on daily returns (not annualized).
kurt is raw kurtosis (normal = 3), not excess kurtosis.
Formulas follow Bailey and Lopez de Prado (2014), as written in Gencay (2026, arXiv:2608.27734, Eq. 1-2).
"""
import numpy as np

EULER_GAMMA = 0.5772156649015329


def psr(sr: float, t: int, skew: float, kurt: float, sr_star: float = 0.0) -> float:
    """Probabilistic Sharpe ratio.
    PSR(SR*) = Phi( (SR - SR*) * sqrt(T - 1) / sqrt(1 - skew*SR + (kurt - 1)/4 * SR^2) )
    """
    raise NotImplementedError("S2")


def expected_max_sr(n_trials: int, var_sr: float) -> float:
    """Bar a result must clear after n_trials attempts.
    SR0 = sqrt(V) * [ (1 - g) * PhiInv(1 - 1/N) + g * PhiInv(1 - 1/(N*e)) ]
    g = Euler-Mascheroni constant, V = variance of the attempts' Sharpe ratios.
    N = 1 returns 0.0 (a single pre-registered test is not deflated).
    """
    raise NotImplementedError("S2")


def dsr(sr: float, t: int, skew: float, kurt: float, n_trials: int, var_sr: float) -> float:
    """Deflated Sharpe ratio = psr(sr, t, skew, kurt, expected_max_sr(n_trials, var_sr))."""
    raise NotImplementedError("S2")


def pbo_cscv(returns: np.ndarray, s: int = 16) -> float:
    """Probability of backtest overfitting by combinatorially symmetric cross-validation.
    returns: T x N matrix, one column per attempt, same dates.
    Split rows into s blocks. For every choice of s/2 blocks as in-sample:
      pick the in-sample best column by Sharpe; find its relative rank w in (0, 1) out of sample;
      logit = ln(w / (1 - w)).
    PBO = share of logits <= 0.
    """
    raise NotImplementedError("S2")


def bootstrap_sr_ci(returns: np.ndarray, alpha: float = 0.05, reps: int = 2000) -> tuple[float, float]:
    """Stationary-bootstrap (Politis and Romano) confidence interval for the Sharpe ratio.
    Use arch.bootstrap.StationaryBootstrap. Record the block size you choose."""
    raise NotImplementedError("S2")
