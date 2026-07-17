# OUTCOME PROOF — P3 escape-hatch · P5 ⑮ LIVE · P6 retreat (one gated deploy; carries the floor chokepoint 7760cc5f already proven in PROOF_FLOOR_CHOKEPOINT.md)
Proven SHA: **793db396**
Operator words (07-17, verbatim): P3 "A fitting-gap refusal on a leg whose sibling is posted does not satisfy the pair law — those legs get a priced bid or the event doesn't trade. Wire that into the invariant's check." · P5 (Fable under delegation) "⑮ LIVE. Not shadow… join or improve best bid +1¢ on the strengthening side; the cast holds deep only where the tape shows the deep print real… This is the arm that ends watch-but-don't-touch." · P6 "every open unfilled event whose lifetime volume sits under 1,500 gets both resting bids withdrawn together — one pair-level retreat… Events with a filled leg are positions, not conceptions."

## Lane 1 — per-game replay
- **P3:** COLVAC — COL posted 53, VAC = TRUE ABSENCE (9 log lines, all tape-seed/audit echoes; no dossier, no refusal, no attempt) — already one of the audit's 5 pair_incomplete flags. Under the split, a `no_path_page_refused`/`aim_unresolved_refused` sibling of a POSTED leg now also flags (state `fitting_gap:<class>`); doctrine-honest refusals (floors, gun, caps, horizon, seesaw, corridor-preference) still satisfy.
- **P5:** BRO (rested 18 vs prints 54–77, its own reprice 54 inside bound 65 NOT taken) and COL (53 under best 58) — under `window_truth_live` the hold yields at hold-review when no window print at/below the held level exists (the deep cast not real): re-aim = min(best_bid+1, machinery's own computed target, ask−1), logged `window_truth_reaim {old, proposed, new, best_bid, best_ask}`. BRO replays 18→54 (join capped by its own bound); COL 53→54+… capped at its target. A leg WITH a real deep print holds lawfully (`path_mode_hold deep_print_real=true`).
- **P6:** the 31-event bypass census (FLOOR_BYPASS_CENSUS) is the retreat's target list — unfilled sub-floor ITF events with resting bids withdraw BOTH legs on the first volume refresh post-boot; BROBRA (filled BRA leg) is exempt by the filled-event guard (never-hold-naked; the position is exit territory). Retreat census posts in the C50 from the `below_discovery_floor_retreat` lines.

## Lane 2 — behavior isolation
- P3 rides `pair_invariant_enabled` (alarm-only; no behavior).
- P5 gated `window_truth_live` (DECREED-cited); flag off = byte-identical hold. Scope: up-moves on entry bids of UNFILLED events only (the completion guard precedes); execution rides the EXISTING repost machinery (walk caps, band clamps, cancel races unchanged); every re-aim logged with the tape evidence.
- P6 gated `discovery_floor_retreat` (DECREED-cited); cancels ride `_cancel_entry_and_resolve` + `_untombstone_entry` (the deliberate cancel-and-free pattern, seesaw-lift precedent); once per event per boot; ITF unfilled events only.

## Gate
lint + smoke via deploy/deploy_gate.sh (this file is OUTCOME_PROOF; OUTCOME_PROOF_SHA=793db396).
