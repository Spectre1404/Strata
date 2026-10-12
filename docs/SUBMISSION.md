# Submission text draft (Cerebral Valley)

## Project name

Strata

## One-line

An AI agent that forgets its failures will report its luck as discovery.
Strata makes forgetting impossible.

## Description

Strata is a harness designed around an AI research agent that searches for
trading strategies on real market data. The more ideas an agent tests, the
more likely its best result is luck — the statistical bar a result must
clear rises with every attempt. An agent that forgets its own past
sessions undercounts its attempts, so the bar is set too low and luck
passes as discovery. Strata is designed to make that impossible at the
database layer, not with prompt instructions: a custom Atlas role lets the
Researcher add attempt records but never edit or delete them, and a
separate role locks the most recent market data away from it entirely.

**Built today**: the Atlas roles and collections that enforce this (and
pass a 21-point access-control check against the real sandbox), real
market data downloaded and checksum-verified from Binance and loading into
Atlas (163 pairs, 5,926 hourly files), and the page that will be the
window onto it — the attempt
stream, the counters, and the bar chart that is the project's one
memorable element, showing (on fixture data today) the dot that clears a
session's bar but not the full record. Raindrop instrumentation is built
and verified against the live API, standalone.

**Planned, not running yet**: the Researcher agent itself, the hash chain
and insert-only enforcement on real attempts, the Auditor's statistical
verdicts, the Strategist, opening the Vault, and Raindrop signals actually
being called from that pipeline once it exists.

## Problem statement

Statement Two: Long Horizon Engineering. (Secondary: Statement One,
Recursive Harnessing — planned: the Strategist component, not built today,
would target the Raindrop RSI prize.)

## Repo

https://github.com/Spectre1404/Strata (public)

## Demo link

https://strata-mv4cc03i032-prod.cloud.modelence.app

Deployed via `npx modelence deploy` from `app/` (Modelence Cloud, free
plan — carries their "Built with Modelence" badge). Verified live:
`HTTP 200`, and the panels render identically to local dev. Runs on fixture
data by default (same as local), per `REPRODUCE.md`.

## Team

Shiv Amba, Talal — **TODO**: add both on the Cerebral Valley submission
platform itself (separate from GitHub; not done as of this writing).
