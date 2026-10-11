# App (Talal: T1, T4, T6)

Modelence app (TypeScript + MongoDB). Panel spec: `docs/DEMO.md`. Data shapes: `docs/CONTRACTS.md`.

## Start

1. In this folder: `npx create-modelence-app@latest .` (or into a subfolder, then move files here).
2. Connect with `MONGODB_URI_APP` only. The app role cannot read the Vault; keep it that way.
3. Build Panels A and B against fixture documents (`fixture: true`). Panels C and D next (T4).
4. The "Test my idea" input inserts into `requests` with `status: "queued"`. Shiv's worker (S7) does the rest.
5. T6: filter out `fixture: true` and read live data.
6. Deploy on Modelence before the final demo (follow their hacker guide). Check D7 first.
