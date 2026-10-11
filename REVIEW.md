# Review rules

1. One pull request per task ID. Title format: `[S2] Auditor statistics`.
2. The reviewer runs the "Reviewer checks" for that task in `PLAN.md`, posts the results as a PR comment, and approves only if they pass.
3. A PR that changes `docs/CONTRACTS.md` needs both of us to approve.
4. Commits are trailer-free: no `Co-Authored-By`, no `Claude-Session`, no "Generated with" lines. `.claude/settings.json` turns Claude Code attribution off, and `scripts/git-hooks/commit-msg` strips any that slip through. Run `git log -1` before pushing.
5. No secrets in commits. `.env` is ignored.
6. No raw market data in the repo. Only download scripts.
7. No real Vault opening during the build. Vault code is tested in `strata_test` only.

## Definition of done

- Code merged to `main` after review.
- The task's "Done when" line in `PLAN.md` is true and checked off.
- Any new collection field is in `docs/CONTRACTS.md`.
