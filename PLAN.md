# Strata build plan: Team Spectre (Shiv + Talal)

## Rules

- Phase 0 is Shiv's. Talal starts Phase 1 once `python scripts/check_setup.py` passes on his machine.
- Every task has an ID, one owner, and one reviewer: the other person. One pull request per task ID. `main` is protected; nothing merges without the reviewer's approval.
- `docs/CONTRACTS.md` is the agreement between us: collection names, fields, roles, function signatures. Change it only through a PR both approve.
- Until real data lands, Talal builds against fixture documents (`fixture: true`) seeded in Phase 0.
- Tests and Vault-opening code run against the `strata_test` database only. The real Vault is opened for the first time in the demo.
- Submissions close at 5:00 PM. The end of Phase 2 is the minimum demo. Phase 3 adds the judge hook and the Strategist.
- Decisions are in `docs/DECISIONS.md`. D1 to D3 are decided. Still open: D4 (name), D9 (Talal's GitHub handle), D10, D11.

## Phase 0: Shiv (setup)

Checklist: `setup/PHASE0.md`.

Done when Talal can clone, fill `.env`, install, run `scripts/check_setup.py`, and see every allowed action pass and every forbidden action fail.

## Phase 1: parallel

| ID | Owner | Task | Depends on | Done when | Reviewer checks |
|---|---|---|---|---|---|
| S1 | Shiv | Data ingest: download hourly spot klines and premium-index klines for the candidate pool, normalize timestamps, select universe point-in-time, split at RESEARCH_END into `research_bars` and `vault_bars`, load | P0, D1 | Row counts per symbol match source files. No `research_bars` row at or after RESEARCH_END. No `vault_bars` row before it. | Talal reruns the count queries and spot-checks 3 random bars against the source CSVs |
| S2 | Shiv | Auditor statistics: PSR, DSR at three trial counts, PBO by CSCV, stationary-bootstrap CI | P0 | `tests/test_stats.py` passes | Talal runs the tests and checks each formula against its docstring |
| S3 | Shiv | Causality check: reject signal pipelines that use future rows inside the research window | P0 | A planted look-ahead pipeline is rejected; a valid one passes | Talal writes one more look-ahead pipeline of his own and confirms it is rejected |
| T1 | Talal | Modelence app scaffold; Panels A and B on fixtures (spec: `docs/DEMO.md`) | P0 | Panels render fixture data through the `app` role | Shiv compares the counters and chart lines to his own aggregation over fixtures |
| T2 | Talal | Red-team tests: try to break every rule in `tests/test_redteam.py` | P0; S3 for the last case | All red-team tests pass | Shiv adds one attack of his own |
| T3 | Talal | Signals module (Raindrop) in `core/observe/signals.py` | P0, D3 | A test event and a test signal appear in Raindrop; the module does nothing when the key is missing | Shiv checks event names match `docs/CONTRACTS.md` |

## Phase 2

| ID | Owner | Task | Depends on | Done when | Reviewer checks |
|---|---|---|---|---|---|
| S4 | Shiv | Backtest engine: one-bar execution lag, fees and spread (D5), daily returns stored | S1 | Buy-and-hold on one symbol matches a hand calculation; costs lower returns by the expected amount | Talal reruns the buy-and-hold check |
| S5 | Shiv | Researcher agent and tools: query, memory stats, similar attempts, pre-register, backtest | S1-S4 | One session of 10 attempts completes; every attempt is in `trials` with a valid hash chain | Talal runs `verify_chain` on the session and reads 3 attempts end to end |
| S6 | Shiv | Session runner; start real sessions running in the background | S5 | Proposed target: 10 sessions of 20 attempts, adjusted to time and API spend | Talal checks session counts and that per-session and total attempt counts add up |
| T4 | Talal | Panels C and D on fixtures; the "Test my idea" input writes to `requests` | T1 | Panel C renders fixture audits; submitting the input creates a `requests` document | Shiv submits two ideas and checks the documents |
| T5 | Talal | Grouping: Voyage embeddings, vector index, return-correlation groups, effective attempt count, written to `trial_groups` | P0, D3 | Effective count is at most the total; a planted near-duplicate fixture pair lands in one group | Shiv plants a third near-duplicate and checks the grouping |

**Cut line:** end of Phase 2 is a demo on real sessions with Panels A to D.

## Phase 3

| ID | Owner | Task | Depends on | Done when | Reviewer checks |
|---|---|---|---|---|---|
| S7 | Shiv | Request worker for the judge hook: request, then one attempt, then audit | S5, T4 | A typed idea returns a verdict; target under 60 seconds | Talal times 3 runs from the app |
| S8 | Shiv | Vault opening with a budget (VAULT_OPEN_BUDGET); every opening is recorded | S2 | Budget enforced in `strata_test`; each opening counted | Talal tries to open past the budget |
| S9 | Shiv | Strategist: policy versions scored on an inner split inside the research window (inner research 2020-2022, inner check 2023-2024) | S6 | Two policy versions scored and stored in `policies` | Talal checks that no Strategist code touches `vault_bars` |
| T6 | Talal | Switch the app from fixtures to live data; Panel D bottom shows policies | S6, S9 | No fixture documents on screen | Shiv compares Panel B against `audits` |
| T7 | Talal | Use-case table: how Strata applies beyond trading (`docs/DEMO.md`), shown as a closing section on the app page and as the video's last frame | T1 | Table renders in the app; every row names the Researcher, the attempt, the Vault, the Auditor test, and what the Strategist learns | Shiv checks each row against `docs/DEMO.md` |
| T8 | Talal | One-minute video with ElevenLabs narration; README "Built today"; submission text draft | All | Video plays with audio; README lists every component built today | Shiv reviews video and text |

## Phase 4: both

- Rehearse `docs/DEMO.md` twice; fix what breaks.
- Deploy the app on Modelence before the final demo (credits).
- Both read the README and the submission text.
- Submit on Cerebral Valley. Check the video has audio. Check both members are on the submission.
