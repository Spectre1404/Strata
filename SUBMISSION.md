# Submission text draft (Cerebral Valley)

## Project name

Strata

## One-line

An AI agent that forgets its failures will report its luck as discovery.
Strata makes forgetting impossible.

## Description

Strata is a harness around an AI research agent that searches for trading
strategies on real market data. The more ideas an agent tests, the more
likely its best result is luck — the statistical bar a result must clear
rises with every attempt. An agent that forgets its own past sessions
undercounts its attempts, so the bar is set too low and luck passes as
discovery.

Strata makes that impossible at the database layer, not with prompt
instructions. Every attempt from every session is recorded in MongoDB
Atlas, hash-chained and insert-only — the Researcher's database role can
add records but can't edit or delete them. The most recent market data
sits behind a separate role the Researcher can't read at all. An Auditor —
plain deterministic code, no model — judges every result against the full
attempt count before it ships, and is the only role that can open that
sealed data.

Built today: the Atlas custom roles and collections that enforce this, the
live research page (the attempt stream, the counters, and the bar chart
that is the project's one memorable element — the dot that clears a
session's bar but not the full record, caught), and the Raindrop
instrumentation around it.

## Problem statement

Statement Two: Long Horizon Engineering. (Secondary: Statement One,
Recursive Harnessing — the Strategist component targets the Raindrop RSI
prize.)

## Repo

https://github.com/Spectre1404/Strata (public)

## Demo link

**TODO — not deployed yet.** Needs `npx modelence deploy` from `app/`
(Modelence Cloud) before this can be filled in. Flagging this now since
it's the one hard blocker left for submission.

## Team

Shiv Amba, Talal (both added on the submission platform)
