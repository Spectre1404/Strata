# Strata

An AI agent that forgets its failures will report its luck as discovery. Strata makes forgetting impossible.

Built at The Harness Engineering & Model Wrangling Hackathon (MongoDB x Cerebral Valley), San Francisco, October 11, 2026, by Team Spectre: Shiv Amba and Talal. All code in this repository was written during the event. See "Built today" at the bottom.

## Design

What this is built toward — see "Built today" below for what actually runs right now.

- **Researcher**: an LLM agent. It will commit a hypothesis before touching data, write a MongoDB aggregation that turns the hypothesis into a signal, and backtest it.
- **Strata**: the agent's memory. Every attempt from every session will be stored in MongoDB Atlas. The agent's database role can add records but cannot edit or delete them — that access control is built and enforced today. Records being hash-chained is planned, not built yet.
- **Vault**: the most recent market data. The agent's database role cannot read it.
- **Auditor**: plain code, no model. It will judge each result against the total number of attempts in Strata, and will be the only role that can open the Vault.
- **Strategist**: will learn the Researcher's search policy from Strata, scored on results that pass the Auditor per attempt.

## Why

- The more ideas an agent tests, the more likely its best result is luck. The statistical bar a result must clear rises with the number of attempts.
- An agent that forgets earlier sessions undercounts its attempts, so the bar is set too low and luck passes as discovery.
- Instructions like "don't use future data" are not enough. The database has to make it impossible.

## How MongoDB enforces it

| Role | Can read | Can write |
|---|---|---|
| researcher | research-window bars, Strata, its own audits | inserts only: attempts, pre-registrations, session events |
| auditor | everything, including the Vault | audits, Vault openings |
| app | display collections | judge requests |

Full definitions: `atlas/roles.md` and `docs/CONTRACTS.md`.

## Data

Binance public market data archive (data.binance.vision): spot klines and USD-M futures premium-index klines for the most-traded USDT pairs. Research window 2020-01-01 to 2024-12-31. Vault 2025-01-01 onward. Raw data is not committed; `core/data/` downloads it.

## Stack

In use today: MongoDB Atlas (Hackathon Sandbox), Raindrop, Modelence. Built with Claude Code.

Planned, not yet integrated: Anthropic API (the Researcher agent itself), Voyage AI via the Atlas Embedding and Reranking API (grouping, T5 — explicitly skipped today unless everything else finishes), ElevenLabs (video narration — pending).

## Problem statement

Statement Two: Long Horizon Engineering. Secondary: Statement One: Recursive Harnessing.

## Run it

See `REPRODUCE.md`.

## References

- Bailey and Lopez de Prado (2014), The Deflated Sharpe Ratio, Journal of Portfolio Management 40(5).
- Bailey, Borwein, Lopez de Prado and Zhu (2014), The Probability of Backtest Overfitting, Journal of Computational Finance.
- Gencay (2026), What survives honest evaluation?, arXiv:2608.27734.
- Wang et al. (2026), AlphaDiverse, arXiv:2609.29014.

## Built today

Everything in this repo was written during the event (10:45 AM – 5:00 PM PT, October 11, 2026, Shack15, SF).

- **Scaffold** — plan, contracts, roles, setup checklist: [`a12e90c`](https://github.com/Spectre1404/Strata/commit/a12e90c)
- **Phase 0** (Shiv) — Atlas collections, indexes, database users, `scripts/check_setup.py` passing 21/21 against the real sandbox: [`2928c00`](https://github.com/Spectre1404/Strata/commit/2928c00) ([PR #1](https://github.com/Spectre1404/Strata/pull/1))
- **S1** (Shiv) — point-in-time universe of 163 pairs (138 research, 25 vault-only); 5,926 hourly files from Binance downloaded and checksum-verified, recorded in `repro/pool.json` and `repro/manifest.json`; `scripts/ingest.py` (download/load/universe/verify) — loading into Atlas, verify result to follow: [PR #7](https://github.com/Spectre1404/Strata/pull/7), merged
- **T1** (Talal) — Modelence app scaffold; Panel A (attempt stream, counters, attempts-by-family chart, polls every 2s) and Panel B (the Sharpe bar — per-session and full-memory thresholds, click-through verdict detail) on fixture data; a data layer that swaps fixtures for the real Atlas `app` role on three env vars (`DATA_SOURCE`, `MONGODB_URI_APP`, `MONGODB_DB`): [`6c60233`](https://github.com/Spectre1404/Strata/commit/6c60233), [`bcea54e`](https://github.com/Spectre1404/Strata/commit/bcea54e) ([PR #2](https://github.com/Spectre1404/Strata/pull/2))
- **T3** (Talal) — Raindrop signals (`core/observe/signals.py`): one event plus one attached signal per call, named after `docs/CONTRACTS.md`'s kinds; never raises except on an unknown kind; a missing key logs a warning rather than failing silently (as of [PR #6](https://github.com/Spectre1404/Strata/pull/6), merged); verified against the live Raindrop API (`200`/`204` responses), not just mocked: [`6cdad59`](https://github.com/Spectre1404/Strata/commit/6cdad59) ([PR #3](https://github.com/Spectre1404/Strata/pull/3)); follow-ups — payload flattening, a secret-key filter, `tests/test_signals.py`
- **T4** (Talal) — Panel B as the page's dominant element, not an equal grid cell; the effective-attempts counter shows "grouping not built yet" instead of a number that looks computed when it isn't: [`38a5538`](https://github.com/Spectre1404/Strata/commit/38a5538), [`500635a`](https://github.com/Spectre1404/Strata/commit/500635a), [`5e77aeb`](https://github.com/Spectre1404/Strata/commit/5e77aeb) ([PR #4](https://github.com/Spectre1404/Strata/pull/4))

## Planned, not built today

- The hash chain on `trials`/`preregistrations` (S5) — the insert-only *role* is already built and enforced (21/21 role checks pass against the real sandbox); the chain itself is not
- The Auditor's statistical verdicts — PSR/DSR (S2)
- Researcher sessions actually running against market data (S5/S6)
- The Strategist (S9)
- Opening the Vault (S8)
- "Test my idea" wired to a real verdict — the UI exists, the insert into `requests` doesn't yet (T4)
- Raindrop signals called from the research/audit pipeline itself — the module is built and verified standalone; nothing calls it yet, since that pipeline doesn't exist
- Voyage embeddings / grouping (T5) — explicitly skipped today per team priority
- ElevenLabs video narration — pending

See `REPRODUCE.md` for how to run what's actually built.
