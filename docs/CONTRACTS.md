# Contracts

This file is the agreement between Shiv's code and Talal's code. If you need a field that is not here, open a PR to this file first. Both approve.

Database: `strata` (live) and `strata_test` (tests, Vault-opening code, fixtures for tests).

Every document written by seed scripts carries `fixture: true`. The app filters fixtures out once T6 lands.

## Collections

### research_bars (time series) and vault_bars (time series)
Same shape. `research_bars` holds RESEARCH_START up to, not including, RESEARCH_END. `vault_bars` holds RESEARCH_END onward.

| Field | Type | Notes |
|---|---|---|
| ts | date | bar open time, UTC |
| meta.symbol | string | e.g. `BTCUSDT` |
| meta.kind | string | `spot` or `premium` |
| o, h, l, c | double | |
| v | double | base volume (spot only) |
| qv | double | quote volume (spot only) |
| n | int | number of trades (spot only) |

### universe
| Field | Type | Notes |
|---|---|---|
| month | date | first day of month |
| symbols | [string] | top UNIVERSE_SIZE by trailing quote volume, using only data before `month` |

### sessions (insert-only events)
| Field | Type | Notes |
|---|---|---|
| session_id | string | |
| event | string | `start` or `end` |
| ts | date | |
| policy_version | int | |
| attempts | int | on `end` only |
| final_hash | string | on `end` only; last hash of the session's chain |

### preregistrations (insert-only)
| Field | Type | Notes |
|---|---|---|
| _id | string | |
| session_id | string | |
| ts | date | written before any data query for this attempt |
| text | string | hypothesis in plain English |
| family | string | one of the families below |
| hash | string | sha256 of the canonical JSON of the fields above |

### trials (insert-only, hash-chained per session)
| Field | Type | Notes |
|---|---|---|
| _id | string | |
| session_id | string | `judge` for hook attempts, `control` for control strategies |
| seq | int | unique per session (unique index on session_id + seq) |
| ts | date | |
| source | string | `researcher`, `judge`, or `control` |
| prereg_id | string | |
| text | string | |
| family | string | |
| pipeline | string | JSON text of the aggregation stages the agent wrote |
| construction | object | `{type: "cs_rank" or "ts_sign", top_k, rebalance_bars}` |
| causality | string | `pass` or `fail`; failed attempts are still recorded and still counted |
| metrics | object | `{sr, skew, kurt, t_obs, ann_return, turnover}`; sr is per-observation on daily returns, not annualized |
| prev_hash | string | previous record's hash in this session; `GENESIS` for seq 0 |
| hash | string | sha256(prev_hash + canonical JSON of this record without `hash`) |

### trial_returns (insert-only)
| Field | Type | Notes |
|---|---|---|
| trial_id | string | |
| freq | string | `1d` |
| start | date | |
| values | [double] | daily net returns over the research window |

### trial_groups (written by grouper, T5)
| Field | Type | Notes |
|---|---|---|
| trial_id | string | |
| embedding | [double] | 1024 dims, voyage-finance-2 |
| semantic_group | int | groups of near-identical hypothesis text |
| numeric_group | int | groups of highly correlated daily returns |
| computed_at | date | |

Effective attempt count = number of distinct `numeric_group` values in scope.

### audits (written by auditor)
| Field | Type | Notes |
|---|---|---|
| trial_id | string | |
| ts | date | |
| n_session, n_total, n_effective | int | attempt counts in each scope |
| sr | double | |
| bar_session, bar_total, bar_effective | double | expected maximum Sharpe under each count |
| dsr_session, dsr_total, dsr_effective | double | |
| pass_session, pass_total | bool | dsr >= PASS_LEVEL |

### vault_openings (written by auditor)
| Field | Type | Notes |
|---|---|---|
| _id | string | |
| trial_id | string | |
| ts | date | |
| requested_by | string | `demo`, `judge`, or a session id |
| result | object | `{sr, ci_low, ci_high, total_return}` on Vault data |
| budget_left | int | |

### blocked
| Field | Type | Notes |
|---|---|---|
| ts | date | |
| session_id | string | |
| actor | string | role name |
| attempted | string | the query or action |
| reason | string | `vault_access`, `forbidden_stage`, `causality_fail`, `write_denied` |

### requests (judge hook)
| Field | Type | Notes |
|---|---|---|
| _id | string | |
| ts | date | |
| text | string | the idea the judge typed |
| status | string | `queued`, `running`, `done`, `error` |
| trial_id | string | set when done |
| error | string | set on error |

### policies (written by strategist)
| Field | Type | Notes |
|---|---|---|
| version | int | |
| parent | int | |
| rules | [string] | plain-English rules placed in the Researcher's prompt |
| budgets | object | `{per_family_max, preregister_first, stop_when_bar_exceeds_best}` |
| score | object | `{surviving_per_100, false_pass_rate}` on the inner split |
| promoted | bool | |
| ts | date | |

## Strategy families

Adapted for crypto from the AlphaDiverse mechanism catalogue (arXiv:2609.29014, Table 8):
`momentum`, `reversal`, `liquidity_volume`, `volatility_range`, `relative_strength`, `intraday_structure`, `futures_premium`, `other`.

## Roles

| Role | find | insert | update | changeStream |
|---|---|---|---|---|
| researcher | research_bars, universe, sessions, preregistrations, trials, trial_returns, trial_groups, audits, policies | sessions, preregistrations, trials, trial_returns, blocked | none | none |
| auditor | all collections, including vault_bars | audits, vault_openings, blocked | none | none |
| strategist | research_bars, universe, sessions, trials, trial_returns, trial_groups, audits, policies | policies | none | none |
| grouper | trials, trial_returns, trial_groups | trial_groups | trial_groups | none |
| worker | researcher's reads + requests | researcher's inserts | requests | requests |
| app | sessions, preregistrations, trials, trial_groups, audits, vault_openings, blocked, policies, requests | requests | none | trials, audits, blocked, requests |

No role except `auditor` and `admin` can read `vault_bars`. Only `auditor`, `app`, and `admin` can read `vault_openings`; the app displays it on Panel C, and nothing the app reads is passed to the researcher. No role except `admin` has `remove`.

## Module interfaces

```python
# core/db.py
get_db(role: str, test: bool = False) -> pymongo.database.Database

# core/strata/record.py
append_trial(db, trial: dict) -> str            # returns hash
verify_chain(db, session_id: str) -> bool

# core/auditor/stats.py
psr(sr, t, skew, kurt, sr_star=0.0) -> float
expected_max_sr(n_trials, var_sr) -> float
dsr(sr, t, skew, kurt, n_trials, var_sr) -> float
pbo_cscv(returns: np.ndarray, s: int = 16) -> float      # returns is T x N
bootstrap_sr_ci(returns: np.ndarray, alpha=0.05, reps=2000) -> tuple[float, float]

# core/auditor/causality.py
check(pipeline: list[dict], db, cutoffs: list) -> dict   # {passed: bool, mismatches: int}

# core/auditor/verdict.py
audit_trial(trial_id: str) -> dict                       # writes to audits

# core/auditor/vault.py
open_vault(trial_id: str, requested_by: str) -> dict     # writes to vault_openings

# core/researcher/backtest.py
run(signal: pd.DataFrame, construction: dict, fee_bps: float, spread_bps: float) -> dict

# core/strata/grouping.py   (Talal)
update_groups(db) -> int                                 # trials grouped this call
effective_count(db, session_id: str | None = None) -> int

# core/observe/signals.py   (Talal)
send(kind: str, payload: dict) -> None
```

## Signal kinds (Raindrop)

`attempt_logged`, `audit_pass`, `audit_fail`, `blocked_query`, `causality_fail`, `vault_opened`, `request_done`, `request_error`.
