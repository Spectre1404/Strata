# Phase 0: Shiv

Goal: Talal can start Phase 1 without asking anything.

## A. Accounts, keys, credits

- [ ] Cursor: claim the $60 credit (link valid October 11-12 only).
- [ ] Anthropic API key with a spending cap. Put in `ANTHROPIC_API_KEY`.
- [ ] Atlas: join the Hackathon Sandbox from the email. Create the project and cluster there (required to be a finalist). Record tier and storage limit in DECISIONS D8.
- [ ] Voyage: create a model API key for the Atlas Embedding and Reranking API. Test one call to `VOYAGE_ENDPOINT` with `voyage-finance-2`.
- [ ] Raindrop: account, project `strata`, write key. Email support@raindrop.ai with "HACKATHON" in the subject.
- [ ] Modelence: account. Ask Aram whether the app can use the sandbox connection string (D7).
- [ ] ElevenLabs: open their hacker guide for T8.
- [ ] Ask organizers about data rights (D6).

## B. Atlas

- [ ] Databases `strata` and `strata_test`.
- [ ] Collections per `docs/CONTRACTS.md`. `research_bars` and `vault_bars` as time-series collections (timeField `ts`, metaField `meta`).
- [ ] Unique index on `trials` (`session_id`, `seq`).
- [ ] Custom roles per `atlas/roles.md`. One database user per role. Save each connection string.
- [ ] Network access: add both laptops' IP addresses (and Modelence's, if D7 says yes).
- [ ] Vector Search index on `trial_groups` from `atlas/vector_index_trial_groups.json`.

## C. Repo

- [ ] Create public repo `strata` under Spectre1404. Push this scaffold as the first commit.
- [ ] Add Talal as a collaborator. Put his handle in `.github/CODEOWNERS` (D9).
- [ ] Branch protection on `main`: require a pull request, 1 approval, review from code owners, no force pushes.
- [ ] Run `git config core.hooksPath scripts/git-hooks` (strips attribution trailers).
- [ ] Claude Code: `.claude/settings.json` already turns attribution off. Install MongoDB Agent Skills and connect the MongoDB MCP Server, per the resource guide. Use the `app` or `researcher` connection string, never `admin`.

## D. Code

- [ ] `core/config.py` and `core/db.py` working.
- [ ] `scripts/check_setup.py` implemented: for each role, try every allowed and forbidden action listed in that file; print a pass/fail table.
- [ ] `scripts/seed_fixtures.py` implemented: fixture documents (`fixture: true`) in `sessions`, `trials`, `audits`, `vault_openings`, `blocked`, `policies`, `trial_groups`, so Talal's panels have data.

## E. Hand-off to Talal

- [ ] Share `.env` values over a private channel. Never commit them.
- [ ] Talal's first 15 minutes:
  1. Clone the repo.
  2. `git config core.hooksPath scripts/git-hooks`
  3. `python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`
  4. `cp .env.example .env` and fill it.
  5. `python scripts/check_setup.py` (all rows must match expectations).
  6. Read `PLAN.md`, `docs/CONTRACTS.md`, `docs/DEMO.md`, `REVIEW.md`.
  7. Start T1, T2, T3.
