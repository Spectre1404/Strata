# Atlas custom roles

Create in Atlas: Database Access, Custom Roles. Database: `strata` (repeat for `strata_test`). Then create one database user per role.

Grant only the actions listed. No role except admin gets `remove`.

| Role | find on | insert on | update on | changeStream on |
|---|---|---|---|---|
| researcher | research_bars, universe, sessions, preregistrations, trials, trial_returns, trial_groups, audits, policies | sessions, preregistrations, trials, trial_returns, blocked | none | none |
| auditor | every collection | audits, vault_openings, blocked | none | none |
| strategist | research_bars, universe, sessions, trials, trial_returns, trial_groups, audits, policies | policies | none | none |
| grouper | trials, trial_returns, trial_groups | trial_groups | trial_groups | none |
| worker | researcher's find list + requests | researcher's insert list | requests | requests |
| app | sessions, preregistrations, trials, trial_groups, audits, vault_openings, blocked, policies, requests | requests | none | trials, audits, blocked, requests |

No role except auditor and admin can read `vault_bars`. Only auditor, app, and admin can read `vault_openings`; the app displays it on Panel C, and nothing the app reads is passed to the researcher.

`scripts/check_setup.py` must confirm in particular:
- researcher cannot find on `vault_bars` or `vault_openings`
- researcher cannot update or delete `trials` or `preregistrations`
- app cannot find on `vault_bars`
- no role but auditor can insert into `audits`
