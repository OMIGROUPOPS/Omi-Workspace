# SESSION HANDOFF — current

**Convention:** This file (SESSION_HANDOFF.md) is ALWAYS the current handoff — overwrite it in place at the end of each session. Numbered SESSION{N}_HANDOFF.md files are frozen historical snapshots; do not edit them.

**Last updated:** 2026-05-14 ET.
**Repo state at handoff:** see `git log` — most recent commits are the five-doc currency sweep (TAXONOMY, ANALYSIS_LIBRARY, README, SIMONS_MODE, this file).

**Read order for a fresh chat or CC instance:** README → this file → LESSONS (Section 1 first) → TAXONOMY → ANALYSIS_LIBRARY → ROADMAP → SIMONS_MODE.

---

## WHO YOU'RE WORKING WITH

Operator is Druid, co-founder OMI Group Holdings (trading division OMQS). Algorithmic prediction-market trading on Kalshi tennis binary markets. Direct, technically precise, high-urgency. Pushes back on premature conclusions and is consistently right when he does — treat operator pushback as a probe-trigger, not a defend-trigger.

Four-way coordination, operator is the mandatory routing layer (no inter-agent comms):
- **Chat-side Claude** — strategy, spec drafting, verification, coordination. Drafts and verifies; does not execute server-side.
- **App / CC (Claude Code)** — server-side executor with VPS shell access. Runs commits, scripts, queries.
- **Plex (Perplexity Comet)** — research and synthesis partner. Public GitHub URL read access only; no shell, no write.

## SYSTEMS ACCESS

- **VPS:** `ssh root@104.131.191.95`
- **Workspace:** `/root/Omi-Workspace`, primary subdir `arb-executor/` and `arb-executor/docs/`
- **GitHub:** `github.com/OMIGROUPOPS/Omi-Workspace` (public)
- **Commit pattern:** commits land via the local Windows repo (`C:\Users\omigr\OMI-Workspace\arb-executor`), pushed to origin/main. The VPS git tree runs behind origin/main by design — it only needs a pull when the producer code is re-run, which is an explicit operator decision.

## WHERE THE OPERATION STANDS

The live bot is intentionally PAUSED. All prior bot versions (v1, v2, v3, V4.2c) traded on a foundation now known to be broken. Capital is unused. The entire current arc is foundation rebuild — not tactical trading.

**The foundation is now built and validated.** `data/durable/per_minute_universe/per_minute_features.parquet` — 9,330,878 ticker-minute rows, 88 columns, checkpoint 3 sha256 `9fde4b5d30e56d99efa0637fe042cb6ca4505274e85e42769b4cedc25e3e5ff4`. This is the canonical analysis foundation (TAXONOMY FOUNDATION-TIER). It supersedes the Layer A v1 / G9-parquet anchors. Checkpoint lineage: `c80e5fc2` (raw merge) → `f9a71d5c` (+pair_gap_abs) → `9fde4b5d` (vol/tc trade-tape aligned, LIVE).

**The cell/exit model is locked** (LESSONS E32):
- The cell = the N's Kalshi price at a fixed late-premarket mark, T-20m before match start. One axis: price.
- Tightness (spread, pair-gap coherence, volatility) is a property of the cell, not a gate. A clean stable window before match start is a MINORITY property of N's (~6-27% by category — confirmed on two independent diagnostics, `data/analysis/stable_window_diagnostic.json` + `_v2.json`). The cell definition accepts that most cells are not in a clean stable regime at the mark.
- Objective: average bounce per cell band. No stop — reach the exit target or ride to settlement. Settlement (first touch of 99c/1c) is the answer key, not the objective.
- Two exit windows (premarket + in-match); one entry venue (premarket only — never enter in-match).
- Four category partitions, every split runs across all four: WTA Main / WTA Challenger / ATP Main / ATP Challenger.

**The phase_state classifier is locked at v0.2** (per_minute_universe_spec.md Section 7).

## WHAT JUST HAPPENED (this session)

1. T37 Phase 3 foundation corpus completed and validated; volume-bug saga resolved (checkpoint 3).
2. v0.2 phase_state amendment landed.
3. The cell/exit model was re-derived from first principles and locked (LESSONS E32).
4. Stable-window diagnostic run twice (flat thresholds, then flat-vs-ticker-relative) — established T-20m as the cell mark and confirmed the stable-window-is-a-minority finding.
5. Doc-sync batch 1: ROADMAP T37 status, LESSONS Section 6 resolution, LESSONS E32.
6. Doc-sync batch 2 (the five-doc currency sweep): TAXONOMY (FOUNDATION-TIER + Section 2.5 GRAIN/VECTOR/OBJECTIVE axes), ANALYSIS_LIBRARY (structural readiness), README (bootstrap currency), SIMONS_MODE (currency pass), and this handoff.
7. Plex briefed on the four-point framing delta + the resolved stable-window finding; acknowledged, holding for the unit-of-analysis audit query set.

## WHAT'S NEXT

**Immediate — the unit-of-analysis audit (Plex).** Plex reclassifies every prior finding in ANALYSIS_LIBRARY against the GRAIN / VECTOR / OBJECTIVE axes (TAXONOMY Section 2.5). The load-bearing output: every settlement-scored finding gets surfaced as needing recomputation against the exit-optimized model, not silent reclassification. Plex is briefed and waiting for the audit query set from chat-side.

**Then — per-band optimized-exit-target derivation.** With the cell mark locked at T-20m, derive the optimized exit target for each cell band across the price range, per category. Metric: highest average bounce per band.

**App's next-eligible work — Layer B v2** (T38b is also gate-satisfied; sequencing is an operator call). Layer B v2 must use tick-level fill semantics, follow the IncrementalTickerWriter streaming pattern, and consume the trade tape directly (per LESSONS C36). The SESSION10_HANDOFF.md archive has the full T36/Layer-B-v2 briefing including calibration target and the three Coordination Points — that briefing still stands for the Layer B v2 work itself.

## OPEN UNCERTAINTIES (do not underweight)

- Whether the ~6-27% stable-window coverage means one of the three attack vectors must shoulder most of the operation's coverage — this is an explicit question in the Plex audit.
- Whether the four categories want different cell marks (Challengers behave differently — they trade structurally wide; v2 diagnostic confirmed `never_tight_spread` is real structure, not a threshold artifact). T-20m is locked for Main; Challenger mark is an open sub-question deferred to the Plex audit.
- v0.3 phase_state amendment candidates: volume-based surge thresholds (volume bug now fixed); possible PHASE_1→PHASE_2 trade-activity floor pending the Finding-2 diagnostic.

## OPERATING NORMS (carry over — battle-tested)

1. **Single-concern commits.** Never bundle. Each commit one concern, dependency-ordered when sequenced.
2. **One CC prompt per turn, never bundled.** If a workflow is multi-step, sequence it across turns.
3. **Probe-validate-probe-validate.** Cheap probes before expensive compute. Verify data foundations before appending or converting. Five failure modes to probe: provenance, grain, unit, coverage, upstream-filter (D11).
4. **Corpus mutations require a pre-replace validation gate** (C37). Compute `.new`, run hard gates against it, `os.replace` only on all-pass. Gate failures get adjudicated with evidence from disk, not overridden on a summary.
5. **Streaming discipline on the VPS.** ~1.9 GB RAM. >3-4 full columns into pandas risks OOM. Use iter_batches / per-ticker streaming.
6. **Web-fetch / verify every commit against origin.** Don't assume a reported diff matches what landed. Chat-side verifies from the repo.
7. **Recommendation posture.** State a clear recommendation with reasoning; don't present a/b/c menus when the right answer is clear. Resolve uncertainty through probes, not open-ended operator questions.
8. **When you background a job, you own the follow-through.** Poll it, surface the result when it lands — don't wait to be asked.
9. **All times ET. Full player names — never abbreviations or 3-letter Kalshi codes.**
10. **The repo is the shared brain.** Anything that would otherwise be copy-pasted between agents gets committed and read from origin/main.

## KEY FILE PATHS

- Foundation corpus: `data/durable/per_minute_universe/per_minute_features.parquet` (checkpoint 3)
- Diagnostics: `data/analysis/stable_window_diagnostic.json` + `stable_window_diagnostic_v2.json`
- Canonical docs: `docs/{README, SESSION_HANDOFF, LESSONS, TAXONOMY, ANALYSIS_LIBRARY, ROADMAP, SIMONS_MODE}.md`
- Spec docs: `docs/{per_minute_universe_spec, layer_b_v2_spec, t38_books_daemon_spec, forensic_replay_v1_spec, bot_v5_shell_architecture}.md`
- Producer scripts: `data/scripts/build_per_minute_universe.py`, `build_forensic_replay_v1.py`, `live_v3.py`
- Historical archive (Session 10 and earlier): `docs/SESSION10_HANDOFF.md` and `docs/handoffs/`

**End of handoff.**
