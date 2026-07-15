# OUTCOME PROOF — −0l STOP-WINDOW FIX (operator word, 2026-07-15: "size the stop window to the book, full gate, now")

**Proven code SHA: `478700d5`** (branch `blend/kalshi-occ-fallback`).

## PRIOR ART (C45)

- **BOARD −0l** (filed tonight, C50 `9370ddcb`): the incident record this fixes.
- **The 02:28 AM incident** (vault, C-FLOW-REST-SEED entry): gate PASSED, stop step failed — script abandoned at 20s, the bot's own 10s force-exit landed at ~35s, **dead book 8 minutes**, healed by manual restart.
- **C-DRAIN-REPLAY 07-10** (restart-amnesia #6): the drain-manifest/boot-replay contract this fix protects — tonight the 10s budget expired **before `shutdown_drain_begin` ever logged** (no manifest written; the jsonl carries no drain events at all for the 02:28 stop; LOOP_LAG was 3.4s at the time), so the replay had nothing to replay.
- **07-08 blackout** (`exit_checker` header): the dead-book class the abandonment branch re-created in miniature.
- **Delta:** both stop paths sized to the book; the abandonment branch is deleted by construction.

## WHAT SHIPS

1. **Bot** (`live_v4.py` signal handler): drain budget = `max(10, min(180, 5 + 0.25 × n_resting_entry_bids))`, computed at signal time from the same criterion the drain cancels; printed with the count; `_force_exit` prints the sized budget. Wedge-backstop semantics unchanged — only sized.
2. **Script** (`deploy_live_v4.sh`): `STOP_WINDOW_SEC=200` (strictly above the bot's 180s cap); polls for actual process death; prints the measured stop time; the only reachable failure branch is "old bot still alive past its own watchdog" → BOT_DOWN-channel alert + exit, with the OLD code still trading — **never a dead book**.

## THE TWO-LANE OUTCOME REPLAY

**Lane 1 — the incident, re-run by arithmetic on tonight's real book:** at 02:28 AM the book held ~200+ resting entry bids (255 resting orders total on the boot audit). Old budget: 10s fixed → expired mid-preamble (no drain_begin line, no manifest, hard exit, script already gone at 20s → 8-minute dead gap). New budget on the same book: 5 + 0.25×200 ≈ **55s** (cap-bounded worst case 180s), inside the 200s script window with ≥20s margin at every book size — the race is closed at all points of the curve, not just tonight's.

**Lane 2 — live verification: the deploy of this fix itself.** This deploy restarts the bot through the NEW stop path on a real book. The measured stop time and the boot verdict are appended below after the gated restart.

<!-- LIVE-LANE -->

## WATCHES

- Every future deploy prints `stopped in Ns` — a stop time approaching the bot's printed budget = the margin thinning, named.
- `shutdown_drain_begin`/`shutdown_drain_done` must BOTH appear on every graceful stop from now on (their absence was tonight's tell); drain-replay accounting resumes meaning.
