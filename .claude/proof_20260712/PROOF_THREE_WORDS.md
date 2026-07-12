# PROOF — C-THREE-WORDS (three operator armings, one gated deploy)

**Candidate SHA: 9b26fc17** (percat arm + honest-anchor flip + completion policy LIVE + nightly live-vs-shadow grading + replay harness).

## The three words (verbatim in the vault entry, executed as given)
1. **Percat bell** — armed as an ADDITIONAL bell source (`percat_gun_armed`, gun source seven: `percat_fitted`) under the fused freeze. Legacy trigger deletion still rides tomorrow's 6:10 regrade scorecard.
2. **−0j** — `walk_cap_honest_anchor` armed: the Plex-ratified table (ITF_W 20 / ITF_M 14 / CHALL 2 / MAIN 1, honest first-target anchor) now catches every leg the `_window_open` void left uncapped (CORBRU's 24¢ walk class).
3. **Taker word** — `operator_taker_word=true` + `completion_live_enabled=true`: the completion policy's verdicts ACT.

## Prior art / staged Lane-1 per arm (C45/C46)
- **Percat**: staged Lane-1 = the C-PERCAT-GUN July-8 replay + nightly shadow would-fires + the cutover file (`.claude/cutover/CUTOVER_EVIDENCE.md`: 07-11 12 rows, 07-12 chase cohort 6/6 + 55-row census). Code delta = 3 lines (the `_gun_stamp` call inside the existing evaluated-and-logged block); the gate smoke exercises `_gun_poll`.
- **−0j**: staged Lane-1 = PLEX_WALK_CAP_SIZES ratification + the staged clamp block (in-code since 07-11, subtractive-only semantics identical to the armed premarket cap); flag flip, zero code delta; smoke exercises the walk path. Escalation lineage: C-CHASE-KILL Part 4 proved the void live.
- **Completion live**: staged Lane-1 = C-COMPLETION-POLICY's 44/44-strand shadow replay + two days of nightly COMPLETION-SHADOW records. NEW execution code gets its own harness (below).

## Lane 1 — the execution replay (`.claude/replay_20260712/replay_completion_live.py`, run at 9b26fc17 on the VPS, REPLAY PASS 5/5)
Real `_completion_execute`, real `_log`, stubbed exchange I/O:
- **taker_complete + word + BELLED event**: sibling maker bid cancelled (`completion_live_resolve`) → deliberate taker BUY on the sibling at ask, IOC/taker_at_cross, qty = kept 5 — **and it passes the fused-gun guard via the one-shot exemption** (the policy's cross is the single legitimate buy on a live match; a second buy would be refused).
- **once-per-event dedup**: second evaluation acts nothing (a flipped verdict after action is the adjudication's business, not a re-trade).
- **word=false**: the taker gate holds — nothing placed, nothing cancelled.
- **flatten_kept**: sibling bid AND kept maker exit cancelled → IOC sell at the bid (never-hold-naked ends now).
- **hold**: nothing touched.

## Lane 2 — economics, stated plainly
The policy trades where its own per-leg math clears (M15-priced EV, pair-97 consulted nowhere — constraint #11). Taker crosses spend spread + taker fees ONLY on verdicts where EV_hold is negative enough that completing/flattening beats riding (the shadow's two-day record: taker_complete verdicts were rare — 4 on 07-12 — and flatten_kept ~10/day). Cost bound per action ≤ qty × spread at cross, one action per event per boot. Divergence discipline: the nightly's new **COMPLETION LIVE-vs-SHADOW** section names every action-vs-verdict mismatch AND every actionable verdict that produced no action.

## Boot resolution orders (the operator's two live bids)
MIYKUZ-KUZ 32¢ and CALRAD-CAL 57¢ resting completions resolve by the live engine's verdict on the first check_fills pass after boot; outcomes with prices in the deploy report.

## Deploy gate
[1/2] lint PASS · [2/3] smoke · [3/3] this file, OUTCOME_PROOF_SHA=9b26fc17 · [4/4] C50 push · [5/5] constraints. Knobs armed same commit, all DECREED (operator words 07-12), cited in knob_citations.json; census regenerates at deploy.
