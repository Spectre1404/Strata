# Strata: instructions for Claude Code

Read first: PLAN.md, docs/CONTRACTS.md, docs/DECISIONS.md, REVIEW.md.

## Rules
1. Work only on the task ID you are given. One branch and one PR per task ID (branch name like `s2-auditor-stats`).
2. Do not change docs/CONTRACTS.md unless asked. If a change is needed, stop and say so.
3. Use the narrowest database role: `core.db.get_db(role)`. The admin role is for scripts/create_collections.py and scripts/seed_fixtures.py only.
4. Only core/auditor/ may read vault_bars. Only core/auditor/ writes vault_openings; the app may read it for display. Vault code runs against strata_test. Never open the real Vault.
5. The model writes language and query text. Deterministic code computes every number.
6. Never commit .env, keys, or market data files.
7. Commits are trailer-free: no Co-Authored-By, no Claude-Session, no "Generated with" lines.
8. Before running commands that change Atlas, GitHub, or installed packages, list them and wait for approval.
9. Say plainly what was tested and where: local, strata_test, or live.
10. Python 3.10+. Tests use pytest.
11. Run every git command from the repo root, the folder that contains this CLAUDE.md. Before the first git command in a session, run `git rev-parse --show-toplevel` and confirm it prints this repo's path. If it prints anything else, stop and tell me.
