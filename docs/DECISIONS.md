# Decisions

Status: OPEN until answered. Record the answer, who decided, and when.

| ID | Question | Options | Affects | Status |
|---|---|---|---|---|
| D1 | Data shape | A: hourly bars, ~30 pairs. B: minute bars, ~5 pairs | S1, S6, storage, demo sentence | DECIDED Oct 11 (Shiv): A, hourly bars, ~30 pairs |
| D2 | Second domain for the "works beyond trading" moment | A: Strategist's own changes. B: outside dataset. C: table only | T7 | DECIDED Oct 11 (Shiv): C, a use-case table showing how Strata applies in each domain; no second adapter |
| D3 | Talal's strongest language | Python, TypeScript, or both | T3, T5, T7 owner | DECIDED Oct 11 (Shiv): both; T3 and T5 stay with Talal |
| D4 | Project name | Strata (proposed) | README, app, video | OPEN |
| D5 | Trading costs | fee bps and spread bps, with source | S4 | Shiv sets in S4 |
| D6 | Data rights | Ask organizers: Binance public archive stored in the sandbox, only download scripts in the repo | S1 | Shiv asks in Phase 0 |
| D7 | Modelence and the sandbox | Can the Modelence app use the Atlas Sandbox connection string? Ask Aram | T1, T6 | Shiv asks in Phase 0 |
| D8 | Sandbox tier and storage limit | Record what the sandbox allows. Estimate for D1: ~59,000 hourly bars per pair from 2020-01 to 2026-09; spot plus premium for 30 pairs is ~3.5M documents, more if the candidate pool is larger than 30 | S1 | DECIDED Oct 11 (Shiv): M10, AWS us-west-1, 10 GB storage |
| D9 | Talal's GitHub handle | For CODEOWNERS and collaborator invite | Repo | DECIDED Oct 11 (Shiv): talal2725 |
| D10 | Problem statement on the submission form | Statement Two (proposed), Statement One secondary | Submission | OPEN |
| D11 | Windows | Research 2020-01-01 to 2024-12-31; Vault 2025-01-01 to 2026-09-30 (proposed) | S1 | DECIDED Oct 11 (Shiv): research 2020-01-01 to 2024-12-31, Vault 2025-01-01 to 2026-09-30 |
| D12 | Point-in-time universe and candidate pool | Rank month M by quote volume in month M-1 | S1 | DECIDED Oct 11 (Shiv): rank month M by spot quote volume in month M-1, summed from 1d kline files. Not 1mo: the archive's 1mo files are missing 2024-03, 2026-03, 2026-07 and 2026-08 across all pairs, which would leave those months' successors unranked. pool stops if any month ranks fewer than 30 pairs. Eligible: USDT pairs, excluding stablecoins, fiat (EUR, GBP, AUD, TRY, and similar), commodity-backed tokens (PAXG, XAUT), wrapped or staked duplicates (WBTC, WBETH, BETH) and leveraged tokens. Request only months in each pair's archive listing. Ranking files skip checksums; hourly files are checksum-verified. 16 parallel downloads. Pool = every pair in any month's top 30; stop if above 100. research_bars gets only pairs in a top 30 during 2020-01 to 2024-12; pairs that first enter in 2025 or later go to vault_bars only. Universe rows only for 2020-01 to 2024-12. Delisted pairs in the archive: to record after the pool run |
