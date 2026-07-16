# OUTCOME PROOF — C-ONE-TRUTH v1 (07-16)

**PROVEN SHA: 47de52ff** (the machinery commit; symlink migration `92142a4a` rides beside it).

## PRIOR ART (C45 — cited and absorbed per the dispatch)
- `analysis/doctrine_registry_build.py` (C-ONE-RECORD Part 3, 07-15): its scan IS the laws section — the builder subprocesses it and absorbs its 256 entries verbatim. Nothing re-derived.
- HANDOFF disk map (hand-maintained since the seat handoff was founded): now GENERATED between `<!--TRUTH-MAP-->` markers by `truth/build_index.py` — never hand-maintained again; the old map is kept one cycle for diff, then dies.
- The AUTO-GAPS/census patterns: the OT_wiring census key inherits them.

## THE BUILD
- **Part 1 — THE ROOT:** `truth/` = symlinks (canonical paths untouched — every cron and code path keeps working): VAULT, BOARD, STANDARD, LESSONS, CLASS_LEDGER, rulings/, surfaces/ (7 fitted files), archive/ (47 dated studies). Outside the root = doesn't exist.
- **Part 2 — THE INDEX:** `truth/INDEX.json` — laws 256 (absorbed) · surfaces 7 (path → fits → fitted date → consuming probes found in the engine source) · sites 6 (path_chokepoint, entry_dossier, gun_sources, completion_engine, exit_machinery, audit_exchange_truth — each with required surfaces + probes, all 6 wired-in-source at build) · studies 47 (archive pointer → one-line finding, auto-extracted from each study's primary heading). Rebuilt every C50 by `truth/build_index.py` (which also regenerates the HANDOFF map).
- **Part 3 — BOTH CONSUMERS, ENFORCED:** (a) the engine loads INDEX at boot and logs `index_wiring_armed` per site (surface files verified on disk; a missing surface, an unwired site, or an absent INDEX logs `index_wiring_missing`); the nightly census key `OT_wiring` fails on ANY missing → STANDARD DEFECT auto-boarded. (b) Seats: session-zero = INDEX first (the generated HANDOFF map's first line). (c) THE GATE: a push ADDING a ruling, fitted surface, or dated study without `truth/INDEX.json` in the same range = **CLOSE-OUT REFUSED (C-ONE-TRUTH)** — the registration law lives at deploy_gate.sh [4/4].

## BEHAVIOR ISOLATION
The engine change is a boot-time READ + log lines only — no decision path consults the INDEX (the surfaces themselves were already the consultation inputs; the INDEX proves the wiring, it does not carry it). Zero aim/exit/completion delta. The wiring proof = THIS deploy's own boot: `index_wiring_armed` ×6 expected in the boot log (verdict recorded below post-deploy).

**BOOT WIRING VERDICT (the deploy, 12:56:37 PM ET, boot `12019d1a` PID 2610972, `stopped in 21s`, audit PASS): `index_wiring_armed` ×6/6 — path_chokepoint · entry_dossier · gun_sources · completion_engine · exit_machinery · audit_exchange_truth, every one surfaces_ok; zero `index_wiring_missing`. The gate itself printed `one-truth registration OK` on this push (the law's founding live pass).**

## WATCHES
- OT_wiring nightly (armed ≥ sites, missing = 0 or auto-board).
- The gate's registration refusal on the next push that adds a study without rebuilding the INDEX (the law's first live test will be an honest one).
- build_index.py at every C50 (a stale `built` stamp beyond one close-out = defect).
