"""Fixture documents so Talal can build panels before real data exists.
Owner: Shiv (Phase 0). Uses the admin role. Every document has fixture: true.

Insert into `strata` (live db, filtered out by the app after T6):
- sessions: 3 sessions, start and end events.
- trials: ~60 attempts across the 3 sessions and several families, valid hash chains
  (use core.strata.record.compute_hash), a few with causality "fail".
- trial_groups: one row per trial; include one planted near-duplicate pair.
- audits: one per trial, with n_session, n_total, bars, dsr values that rise with n_total,
  and at least one attempt with pass_session true and pass_total false.
- vault_openings: 2 openings with results.
- blocked: 3 rows (vault_access, forbidden_stage, causality_fail).
- policies: versions 1 and 2 with scores.
"""


def main() -> None:
    raise NotImplementedError("Phase 0")


if __name__ == "__main__":
    main()
