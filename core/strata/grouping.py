"""Effective attempt count. Owner: Talal (T5). Reviewer: Shiv.

1. Embed each trial's `text` with Voyage (VOYAGE_ENDPOINT, VOYAGE_MODEL=voyage-finance-2, 1024 dims).
2. semantic_group: trials whose embeddings are near-identical (cosine above a threshold you choose and record).
3. numeric_group: trials whose daily returns (trial_returns) correlate above a threshold you choose and record.
   This follows Lopez de Prado's approach of clustering similar strategies to estimate independent trials.
4. Write to trial_groups using the grouper role.

Effective count = number of distinct numeric_group values in scope.
"""


def update_groups(db) -> int:
    raise NotImplementedError("T5")


def effective_count(db, session_id: str | None = None) -> int:
    raise NotImplementedError("T5")
