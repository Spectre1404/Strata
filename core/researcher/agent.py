"""Researcher session loop. Owner: Shiv (S5/S6). Reviewer: Talal.

The model writes language and the pipeline; code computes everything else.
Per attempt:
  1. Build context: current policy rules, memory_stats, similar_attempts.
  2. Ask the model (ANTHROPIC_MODEL_RESEARCHER) for JSON: text, family, construction, pipeline.
  3. preregister.
  4. backtest (includes the causality check).
  5. append_trial, audit_trial, send signals.
Sessions write start and end events to `sessions`.
"""


def run_session(session_id: str, max_attempts: int, policy_version: int) -> dict:
    raise NotImplementedError("S5/S6")
