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

## 2. The Atlas role gate (needs `.env`)

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

## 3. The app, against live Atlas data

**Not fully reproducible yet.** The app's `DATA_SOURCE=mongo` path
(`app/src/server/panels/mongo.ts`) connects and type-checks against the real
`app` role, but `scripts/seed_fixtures.py` — which would put sample data
into Atlas for it to read — is still a stub. Once that lands, this becomes:

```
cd app
DATA_SOURCE=mongo npm run dev
```

Same panels, reading `MONGODB_URI_APP`/`MONGODB_DB` directly instead of the
local JSON fixtures.

## 4. What else needs real data

The Researcher agent, the backtest engine, and the Auditor's statistics
(S2–S9) run against real Binance market data, which isn't committed to this
repo (see `core/data/`) and isn't something a judge can reproduce in the
time available. `docs/DEMO.md` and the submission video are the record of
those in action.

## What's tested where

- Panels A/B: tested locally against fixtures, in a real browser.
- Atlas roles: tested against the live Hackathon Sandbox (`check_setup.py`).
- `core/observe/signals.py`: tested locally — no-op without a key, never
  crashes the caller on a bad key — not yet verified against the live
  Raindrop dashboard (no key as of this writing).
