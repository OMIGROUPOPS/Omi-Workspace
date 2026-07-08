# OUTCOME PROOF (C46, two-lane) — sweep containment (ITM-exit-take + no-rebuy-after-cash + continuous audit)

**Candidate SHA: `518764e2`** (re-stamp: proven code SHA `a02a0d78`; the a02a0d78..518764e2 delta is READ-ONLY ANALYSIS PRODUCERS only — slate_ledger v2 pair (S-per-leg render), walk_repost_model.py — zero live_v4/config delta, verified by pathspec diff) (three containment diffs from tonight's emergency sweep; S-per-leg render change rides doc-side).

## Prior art (C45)
Tonight's sweep evidence (`.claude/sweep_20260707/SWEEP_TABLE.txt` — 4 naked legs, per-leg chains); the CLAHER `exit_unpostable_itm` counter (the flag class that turned out to be live nakedness); C-DUP-GUARD/C-NO-REBUY lineage (POTFEL same-pass, TIKCHO cross-lifecycle); C47/C49 (the audit this extends); board-queued "post-only-cross hole" (this closes it — same-shape build check done).

## LANE 1 — MECHANISM (deterministic replay vs tonight's tape)
- **C-ITM-EXIT-TAKE:** replay tonight's two ITM deaths: ISOTOM (entry 16, band 21, two 400s at 20:47-48... booking time, bid ≥ band throughout) and NASLEE (band 34; the sweep's non-post-only post filled INSTANTLY at 45): under the fix the second attempt crosses → both legs exit at ≥ band within seconds of booking instead of resting naked for hours. Zero effect on any postable (OTM) exit: the taker branch requires the first attempt's exact "post only cross" 400. Realization at ≥ band is the band DOING ITS JOB (0A: qty-mechanical, band levels untouched).
- **C-NO-REBUY-AFTER-CASH:** replay tonight: TIKCHO re-buy 15×5 at +34s and KUSTAG 63×5 at +60s after their exits — both conceived via `_repost_missing_siblings` on cashed legs; under the fix both are `pair_cashed_this_session` skips, and had any other path placed them, the audit's new `post_exit_rebuy` assertion fails the book. Legitimate completions unaffected: the guard keys on THIS SESSION'S booked exit fills only.
- **C47-CONTINUOUS:** tonight's four legs went naked at ~20:47-22:2x against a 19:39 boot-PASS with no re-assertion; under the 15-min cadence the first steady audit after 20:47 fails `no_exit`/ITM-flag and the book gets attention within ≤15 min instead of on operator eyesight. Same halt/clear semantics as C49 — no new behavior class.
- Interaction check: the ITM-take fires at booking (before the audit could flag); the rebuy guard fires at conception; the cadence catches whatever neither did. No path both places and cancels the same order.

## LANE 2 — SETTLEMENT P&L
Tonight's four legs at mark vs band: NASLEE's sweep exit already realized 45 vs band 34 (+$0.55 over band on 5). Luck-flagged small-n; not the verdict.

**Verdict: three closures of tonight's proven damage paths, replayed against the same tape that produced them.**
