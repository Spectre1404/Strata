# Demo

## The sentence

An AI agent that forgets its failures will report its luck as discovery. Strata makes forgetting impossible.

## The hook: "Test my idea"

1. A judge types a trading idea in plain English.
2. The Researcher turns it into a query and backtests it on 2020-2024 data.
3. The raw Sharpe appears. It often looks good.
4. The Auditor judges it against every attempt in Strata and shows the verdict.
5. The judge tweaks the idea and tries again. Each try is recorded, and the bar on Panel B rises.
6. The judge tries "use tomorrow's price." Atlas returns nothing; Panel D logs it.
7. We open the Vault once for the judge's best idea. Openings are counted and capped.

Keep three preset ideas on buttons in case typing or the model is slow.

## Three-minute script

1. The sentence, and the problem in two lines.
2. Panel A: a live session running.
3. The hook with a judge.
4. Panel B: the two bars.
5. Panel C: open the Vault; what each counting method would have shipped, and how it did.
6. Panel D: blocked attempts; the Strategist's old rules against new ones.
7. Where else this applies: the closing table (T7).

## Panels

One page, four panels. The Researcher and Auditor are the product; the page is how judges see them.

### Panel A: Live research
- Left: stream of attempts. For each: hypothesis text, family, pre-registration hash, the query, backtest Sharpe. Source: change stream on `trials`.
- Right: three counters: attempts this session, attempts across all sessions, effective attempts (from `trial_groups`).
- Below: a bar showing attempts per family, so repeated searching in one family is visible.

### Panel B: The bar
- X axis: attempt number across all sessions. One dot per attempt (its Sharpe).
- Lines: best Sharpe so far; the per-session bar (resets each session, so it looks like a sawtooth); the full-memory bar (only rises).
- Highlight any attempt that clears the per-session bar but not the full-memory bar.
- Click a dot: hypothesis, query, daily returns, verdict under both counts. Source: `audits`, `trials`.
- Input box "Test my idea" and three preset buttons. Writes to `requests`.

### Panel C: The verdict
- Button "Open the Vault". Shows budget left.
- Table: strategy; research-window Sharpe; verdict with per-session count; verdict with full count; Vault Sharpe with confidence interval.
- Control rows: buy-and-hold, random strategies, noise. Source: `audits`, `vault_openings`.

### Panel D: Blocked and learned
- Top: blocked attempts: query, what it tried to reach, reason. Source: `blocked`.
- Bottom: Strategist rules, old against new, with surviving results per 100 attempts. Source: `policies`.

## Design notes for Talal

- Subject: an audit of a research notebook. Audience: judges standing at a laptop.
- The one memorable element is Panel B: the dots, the sawtooth, and the rising full-memory bar. Keep everything else quiet.
- Avoid MongoDB-green on black and identical rounded cards; those read as templates.
- Copy: sentence case, plain verbs. Buttons say what they do: "Test my idea", "Open the Vault".
- Errors say what happened and what to do next.

## One-minute video (T8)

1. 0-10 s: the sentence over Panel B.
2. 10-30 s: a typed idea, its verdict, the bar rising.
3. 30-45 s: a blocked future query; the Vault opening.
4. 45-60 s: what was built today, and the repo link.

## Where else this applies (T7)

The same five parts carry over. In every row, MongoDB does the same three jobs: an add-only collection records every attempt, a collection only the Auditor's role can read holds the sealed data, and the Auditor counts attempts from the record before judging.

| Domain | Researcher | One attempt in the record | Vault | Auditor test | Strategist learns |
|---|---|---|---|---|---|
| Trading (built today) | LLM research agent | strategy, query, daily returns | 2025-26 market data | deflated Sharpe at the total attempt count | which strategy families pay off per attempt |
| Self-improving AI agents | harness optimizer | prompt, tool, or rule edit and its task scores | fresh tasks the optimizer never sees | paired test with the bar raised by the number of edits tried | which kinds of edits survive |
| Code agents | coding agent | candidate patch and visible test results | hidden tests | hidden-test pass rate, adjusted for patches tried | which repair approaches hold up |
| Drug and science discovery | hypothesis agent | hypothesis and screen result | validation assay | false-discovery-rate control over every hypothesis scored | which hypothesis classes replicate |
| Product experiments | experimentation agent | variant and its metric | later traffic | false-discovery-rate control over variants tried | which change types hold up |
| Credit and risk models | model-building agent | candidate model and validation score | a later loan cohort | performance on the later cohort, adjusted for models tried | which feature families generalize |
