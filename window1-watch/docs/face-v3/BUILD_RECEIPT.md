# FACE v3 build receipt

2026-09-12. Face only. Static mockups and Astra's amendments preceded implementation; see MOCKUP_REVIEW.md. LAB, gated DESK and SCOREBOARD were implemented in that order.

## Verification

- TypeScript: clean. Production static build: clean; bundler's existing large-chunk warning remains.
- Browser: all five loaded games; grade/oracle/source bindings unchanged; no page errors. Fixed inspector, bid-card hover, keyboard game/gate focus, three deep-linkable tabs, mobile layout and prepared-face import checked. A synthetic sealed-source import is rejected. VERIFY_ALL.json records the inputs.
- SCOREBOARD generated twice, byte-identical SHA256 `58ad7bee1a5fddcececd4aac9336e791ac88be934c6ec4cc77a24ac11d9acb4a` (90,787 bytes).
- Loaded cohort: 5 considered, 5 with bid actions, 4 positive-offer games, 2 complete, 2 one-sided, 1 unfilled; 3 cents captured / 23 offered. This is not a population or exchange-listed-universe denominator.
- Existing grade letters: GIUBAR F, LAJSVA F, URSPAL F, ALTGAS C, DANPRA not offered. No grade/rubric/source face was rewritten.
- DESK: disconnected; zero invented games, no API key used, no worker started, no order endpoint or settlement claim.

## Unchanged engine pins

- dual OS: `70b68856cb4f0329048f9ae951e01c19c7d7465e3cc0ee183e325ce6c1fb0346`
- functionable OS: `83f44682de821f754e99ecfdc0b56fd4ac8a03d65b0ee986f39c47f7df4e6c74`
- builder: `6136c8ca9cd2b6742f7a6235a27169cdc97b6b6543368a29d08f18c3185f5a8c`

## Explicit unfinished activation/data boundaries

LAB can load reviewed prepared faces and explicitly classified LIBRARY/TUNE_SAMPLE prepared faces. It cannot yet run arbitrary raw tapes through a pinned local OS adapter. That adapter remains required; selecting a face is not a replay. The old temporary-builder-edit fallback is not connected.

The available compact receipts contain counts/weight sums, not individual member rows; no member rows were reconstructed. Missing depth sizes and maker residuals stay STORE SILENT. Full local receipt/renewal details use the existing local gzip source middleware; the public static build omits 11,710 stage/accountability files totaling 2,370,998,610 bytes. Compact source receipt inspection remains available publicly.

The operator-approved LIVE_PAPER policy is acknowledged, but read-only-key verification, runtime disjoint-cohort enforcement and pinned-worker binding have not been performed. DESK is a gated view/contract, not an activated live paper engine.

## Deployment binding

Verified project `omi-window1-watch`, root `window1-watch/shell`, build `npm run build:demo`, output `dist-demo`, Node 24.x. Connected its Git repository to the verified worktree origin `OMIGROUPOPS/Omi-Workspace` and set production branch `face/window1-watch-20260903`. No other project or repository was changed. [Vercel's branch behavior](https://vercel.com/docs/git) and [its own production-branch API implementation](https://github.com/vercel/terraform-provider-vercel/blob/main/client/project.go) were checked; the settings were read back from the project API.

Static allowlist: 24 files including the shell bundle, five compact face/grade/oracle sets, picker/history, gated DESK contract and SCOREBOARD. No engine, raw tapes, server/auth scaffold or renewal streams in the upload. Asset hash/credential-pattern checks pass. Existing unrelated work, including face_contract.mjs and bench files, is excluded from these commits.
