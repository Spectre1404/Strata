# Strata

An AI agent that forgets its failures will report its luck as discovery. Strata makes forgetting impossible.

Built at The Harness Engineering & Model Wrangling Hackathon (MongoDB x Cerebral Valley), San Francisco, October 11, 2026, by Team Spectre: Shiv Amba and Talal. All code in this repository was written during the event. See "Built today" at the bottom.

## What it does

Strata is a harness around an AI research agent that searches for trading strategies on real market data.

- **Researcher**: an LLM agent. It commits a hypothesis before touching data, writes a MongoDB aggregation that turns the hypothesis into a signal, and backtests it.
- **Strata**: the agent's memory. Every attempt from every session is stored in MongoDB Atlas. The agent's database role can add records but cannot edit or delete them. Records are hash-chained.
- **Vault**: the most recent market data. The agent's database role cannot read it.
- **Auditor**: plain code, no model. It judges each result against the total number of attempts in Strata, and it is the only role that can open the Vault.
- **Strategist**: learns the Researcher's search policy from Strata, scored on results that pass the Auditor per attempt.

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

MongoDB Atlas (Hackathon Sandbox), Anthropic API, Voyage AI via the Atlas Embedding and Reranking API, Raindrop, Modelence, ElevenLabs (video narration). Built with Claude Code in Cursor.

## Problem statement

Statement Two: Long Horizon Engineering. Secondary: Statement One: Recursive Harnessing.

## Run it

Filled in during the build. Start with `setup/PHASE0.md`.

## References

- Bailey and Lopez de Prado (2014), The Deflated Sharpe Ratio, Journal of Portfolio Management 40(5).
- Bailey, Borwein, Lopez de Prado and Zhu (2014), The Probability of Backtest Overfitting, Journal of Computational Finance.
- Gencay (2026), What survives honest evaluation?, arXiv:2608.27734.
- Wang et al. (2026), AlphaDiverse, arXiv:2609.29014.

## Built today

To be completed in task T8: a list of every component built on October 11, 2026, with links to the commits.
