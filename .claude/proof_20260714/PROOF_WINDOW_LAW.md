# PROOF — C-WINDOW-LAW v1 (W1 · CORRIDOR · W2 as first-class OS surfaces)

**Candidate SHA: 26b18d63** (window stamp v2 + emitter wiring + dossier surface + nightly WINDOW LEDGER + gun-feed repair + tripwires; code across b7100e62 → 26b18d63, cited at HEAD).
**The operator directive (§5), cited on the organ itself:** W1 fill→scheduled · CORRIDOR scheduled→gun · W2 gun→settle; **the corridor opens at schedule, closes at gun, never at a burst.**

## Part 1 — the stamp (v2, hardened by its own acceptance test)
`_window_phase` computes the phase off BOTH clocks with the two-clock spread first-class; stamped at the single emitter on every placement/refusal/re-aim/cancel/completion event and carried as dossier surface #13. **v1 failed its own acceptance test — the burst latch fires the gun, so latch-cancels graded themselves lawful (circularity). v2 closes it: only an EVIDENCE-grade gun (te_scoreboard / schedule_live / fallback_bell / percat_fitted / self_fill) closes the corridor; burst sources (tape_latch, price_divergence) never advance the phase and are branded `burst_latch_active`.** UNKNOWN named on missing joins.

## Part 2 — the consumer census (CONSUMER_CENSUS.md, committed)
19 clock consumers inventoried. **The corridor-blind class is one family: match_live_cancel (burst latch) + grace-kill + latch-sourced entry freeze — rows 8–10.** All other consumers lawful per §5 (T−15 buffer closes W1 at the scheduled boundary; evidence guns open W2; exits are clock-free anchors).

## Part 3 — acceptance on tonight's tape (WINDOW_ACCEPT.txt, committed): CONVICTS, and revises
**3 latch-cancels fired in W1/CORRIDOR with NO evidence-grade gun — convicted by the stamp alone.** And the stamp's deeper finding amends C-REACH-VERDICT honestly: **6 of the 8 touches grade W2 — the evidence gun (percat_fitted) had already spoken when the tape reached the aims.** Under the standing W1-thesis ruling those were NOT lawful fill opportunities; the W1/CORRIDOR discount tonight was ~0–2 touches (two UNKNOWN, no schedule join). Two consequences, both vaulted: (i) the presence proposal's price tag shrinks from "9 forfeited" to "the latch class + 0–2 lawful touches" — the proposal stands for its mechanism, repriced; (ii) **ATLAS-TIMING CHALLENGE filed per the vault-alive law: the atlas prices bottoms 19–27 min BEFORE onset; tonight's realized bottoms landed AFTER the evidence gun — a live-tape contradiction of a vaulted conclusion, review item named, to be re-validated by the same walk-forward standard.**

## Part 4 — the WINDOW LEDGER (nightly, standing)
Entries / refusals / tape touches / fills / cash-via-exit / rode-to-settlement / cancels × W1/CORRIDOR/W2 per cat, every night, with UNKNOWN honest. No night grades without the split again.

## Part 5 — the gun feed, root REPAIRED
**Root: the 17GB multi-writer tennis.db write-locked te_live's bank out of ~59 of every 60 minutes — rows landed ONLY in the hourly :13 WAL-conversion window** (the 07-08 busy_timeout was insufficient; the keepalive kept a starving process alive). Repair: `observed_starts` moves to a dedicated single-writer `state/observed_starts.db` (te_live writes; live_v4 reads with tennis.db fallback for cutover) — the contention class is deleted, not tuned. Tripwires: >30-min staleness prints in the LIVE_STATUS header and the nightly (honest label: minutes since the last NEW in-play sighting).

## Lane 2 — $0
Instrumentation, audit, and feed infra only; no placement, cancel, or aim behavior ships. The presence build (re-place-on-unlatch + status-gated cancels) remains a separate gate awaiting the operator's explicit word.

## Deploy gate
[1/2] lint PASS (at commit) · [2/3] smoke (gate-run; atlas staged) · [3/3] this file, OUTCOME_PROOF_SHA=26b18d63 · [4/4] C50 push (the directive verbatim; the atlas challenge filed) · [5/5] constraints surface.
