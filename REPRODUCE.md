# Reproduce this

What's actually runnable right now, and what isn't yet. Written for a judge
or anyone else checking this out cold.

## 1. The app, against fixture data (no credentials needed)

This is the fastest way to see Panels A and B exactly as built.

```
cd app
npm install
npm run dev
```

Open http://localhost:3000. No `.env` or Atlas access required — this runs
against hand-authored fixture JSON in `app/src/server/panels/fixtures/`,
shaped exactly like `docs/CONTRACTS.md`.

Node 24.13.0 was used to build this; the `mongodb` driver (v7) needs a
recent Node version.

## 2. Atlas setup (admin only — Shiv's side, included for completeness)

Creates the collections, custom roles, and the six per-role database users.
Needs `MONGODB_URI_ADMIN` and Atlas project/cluster details; not something a
judge can run.

```
.venv/bin/python scripts/create_collections.py
bash scripts/create_roles.sh <PROJECT_ID>
bash scripts/create_users.sh <PROJECT_ID> <CLUSTER_HOST>
```

## 3. The Atlas role gate (needs `.env`)

`.env` has real credentials and is never committed — Shiv shares it
privately. Copy `.env.example` to `.env` and fill it in, then:

```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
.venv/bin/python scripts/check_setup.py
```

Every row should print `expected == actual` (21/21 as of this writing).
This proves the custom Atlas roles in `atlas/roles.md` actually enforce
what `docs/CONTRACTS.md` says they should — the researcher role can't read
the Vault, can't edit its own records, and so on.

If you're on venue Wi-Fi: it blocked at least one Atlas node on port 27017
for us. A phone hotspot, with that hotspot's IP added to the Atlas project's
IP Access List, worked.

## 4. Data ingest (S1 — Shiv, on branch `s1-data-ingest` as of this writing)

```
.venv/bin/python scripts/ingest.py download --pool repro/pool.json
.venv/bin/python scripts/ingest.py load --test
.venv/bin/python scripts/ingest.py universe --test
.venv/bin/python scripts/ingest.py verify --test
```

(`--live` instead of `--test` loads into the real `strata` database rather
than `strata_test`.) `repro/pool.json` and `repro/manifest.json` are the
checked-in record of what was downloaded and checksum-verified — see the
"Built today" list in the root README for the actual counts.

## 5. The app, against live Atlas data

**Not verified against real Atlas as of this writing.** The app's
`DATA_SOURCE=mongo` path (`app/src/server/panels/mongo.ts`) type-checks and
reads `MONGODB_URI_APP`/`MONGODB_DB` from the environment — the same `.env`
from step 3, not anything Modelence manages — but I haven't run it against
the live sandbox myself; `scripts/seed_fixtures.py`, which would put sample
data in for it to read, is still a stub. Once that lands:

```
cd app
DATA_SOURCE=mongo npm run dev
```

Same panels, reading `MONGODB_URI_APP`/`MONGODB_DB` directly instead of the
local JSON fixtures.

## 6. What else needs real data

The Researcher agent, the backtest engine, and the Auditor's statistics
(S2–S9) are still stubs as of this writing and aren't something a judge can
run — they'll run against the real market data step 4 ingests. `docs/DEMO.md`
and the submission video are the record of those running, once they do.

## What's tested where

- Panels A/B: tested locally against fixtures, in a real browser.
- Atlas roles: tested against the live Hackathon Sandbox (`check_setup.py`).
- `core/observe/signals.py`: tested locally (mocked, `pytest tests/test_signals.py`)
  and against the live Raindrop API with a real key — `200`/`204` responses
  confirmed for both the event and the signal.
- Data ingest (S1): not run by me — see Shiv's own testing notes once that
  branch has a PR.
