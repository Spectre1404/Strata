# 1-minute video script

Adapted from `docs/DEMO.md`'s script. **Deviates from it on purpose**: that
script assumes the "Test my idea" → verdict flow and the Vault opening are
live (S7, S8). As of this writing those aren't built, so this script only
shows what's actually real in the running app — nothing staged.

Record the app running against the fixture backend (`cd app && npm run
dev`, http://localhost:3000) — no Atlas credentials needed, and the fixture
data is the same shape as the real thing. **Put a visible "fixture data"
label on screen for the whole recording** (a corner watermark or a title
card) — this data is hand-authored, not the output of a real research
session, and that should be obvious to a judge watching, not just true in
the fine print.

**Record only after PR #4 is merged** — it changes the highlight logic and
the layout; recording against the pre-#4 state would show the wrong thing.
(PR #4 merged as of this writing.)

## Shots

**0:00–0:10 — The hook**
Screen: Panel B, full-width, the sentence visible above it.
Voiceover: *"An AI agent that forgets its failures will report its luck as
discovery. Strata makes forgetting impossible."*

**0:10–0:30 — Panel B: the bar**
Screen: slowly pan across the chart. Hover the dashed best-so-far line,
then the rising blue full-memory bar, then the orange sawtooth session bar.
Click the highlighted dot — the chart's own caption reads "passes this
session's test, fails the full-memory test"; the detail dialog that opens
shows the two verdict badges exactly as labeled: "This session: Clears the
bar" and "Full record: Doesn't clear the bar."
Voiceover: *"Every attempt an agent makes raises the bar the next one has
to clear. This dot looks like a win in its own session — but against
everything Strata remembers, it isn't. That's luck passing as discovery,
caught."*

**0:30–0:45 — Panel A: the attempt stream**
Screen: the attempt stream (fixture data, labeled on screen) — hypothesis,
family, pre-registration hash, the query, the Sharpe. Point at the three
counters (session / total / effective).
Voiceover: *"This is the shape every real attempt will take: hypothesis,
query, Sharpe, in before the agent sees the result. The insert-only role
that would enforce this is built today — the Atlas roles pass a 21-point
access check. The hash chain itself is still planned; the agent writing
these records isn't built yet."*

**0:45–1:00 — What was built today**
Screen: the README's "Built today" section, then the repo URL.
Voiceover: *"Built today, October 11th, at the MongoDB hackathon — Atlas
roles that make cheating structurally impossible at the database layer.
The panels here run on fixture data. The real market data, 163 pairs and
5,926 checksum-verified files, is downloaded and loading into Atlas.
Repo link's on screen."*

**If you already recorded the line above with the old wording ("reading
real market data"), re-record it** — that line claimed fixtures were real
data, which they aren't.

## Notes for recording

- Screen recording: `Cmd+Shift+5` on macOS, record the browser window at
  http://localhost:3000.
- Narration: run this script through ElevenLabs yourself (ai.elevenlabs.io
  → Text to Speech) — I can't record audio or capture your screen directly.
- Keep the mouse movement slow and deliberate during the Panel B shot —
  that chart is DEMO.md's "one memorable element," give it room.
- If there's time left after the submission's minimum bar is cleared,
  swap in a real judge-typed idea once T4's request-wiring is live instead
  of staging it.
