# AIM_V2 BUILD REPORT — derivation pipeline, 14k corpus, end-to-end, GATED-OFF (2026-07-06 ~18:35 ET)

**Nothing arms. Deliverables: candidate tables (both clock variants) + walk-forward evidence, committed — the Plex ruling in flight slots in with zero rework.**

## Prior art (C45)
AIM_V2_SPEC (estimator law) · PLEX_REGRESSION_RULING · OPERATOR_RULING_2C (pair as ONE STATE — enforced structurally: the cell is keyed on the FAV and carries BOTH legs' curves; no sibling lookup exists anywhere in estimator or replay) · BELL_FEASIBILITY (65% detection; −54.9m 53/53 → the LATCH-CAL variant exists; complement residual = check only) · B3_DISCOUNT_COUNTERFACTUAL (~40% depth / ~60% synchrony mandate) · the exit-surface precedent (same corpus foundation, entry logic now) · TIME_AXIS_PROOF −$20.31 (the standing bar; Lane-1 verdict below stated against its shape).

## 1 · Pair-state extraction (the 65%)
Corpus events folded into ONE pair series (fav-keyed 20¢ bucket × 10-min Tbin; fav = higher-priced side at first common observation). **Exclusions named with counts (BAR variant): thin_prebell 611 · no_bell 262 · dead_tape 522 · not_two_tickers 158.** LATCH-CAL variant: no_bell 1,255 (stricter bar — the detection/coverage trade quantified below).

## 2 · Clock variants — one flag, two table sets, no mixed axes
- **BAR** (150-in-1min / 3000-in-10min): the corpus ramp bar.
- **LATCH-CAL**: grid-fit to the 53-event live-latch overlap → **K=600 / M=20,000, med |bell−latch| = 12.2m (n=46)** — from the −54.9m baseline. Residual 12m stated; not ±5m; the Plex amendment picks the canonical axis with this number in hand.

## 3 · Fit per spec
Per-cell: drift med + resid_sd · dips q25/q50 · n / n_honest / pooled_w (n/(n+50)) / null_reason all first-class · PAV monotone smoothing toward bell-convergence per (cat,bucket,side) · complement residual reported per cell with fat-tail flag (a gate, never an n-doubler) · **HARD floor 30; parked cells are null — the replay treats them as no-aim-derived (resting carry), never interpolated.**

| variant | live cells | parked | untradeable-at-q25 | q50 | coverage w=1.0 | w=0.5 | w=0.25 |
|---|---|---|---|---|---|---|---|
| BAR | 119 | 789 | 39 | 58 | 119 | 57 | 29 |
| LATCH-CAL | **217** | 775 | **18** | 58 | **217** | 100 | 39 |

The prior-weight row is the Plex slot: the pending weight decision moves live coverage 5.6× (217 → 39).

## 4 · Joint aims
Both legs' aims from the one fav-keyed curve; combined-at-dip ≤97 evaluated at derivation; **UNTRADEABLE-AT-Q marked as table facts (18–58 cells)** — participation law untouched (no runtime skip exists).

## 5 · VALIDATION PACK — honest-era holdout (the ledger's day, 178 events prepped), C46 two-lane

| grid | pairs (actual 149) | ≤97 | comb med | legs | lazy (actual 88/177≈50%) | gold legs (actual A+B1=14) | B3-conv | null-steps |
|---|---|---|---|---|---|---|---|---|
| BAR q25 | 44 | 29 | 97.0 | 181 | 72 | 7 | 14/41 | 3293/4450 (74%) |
| **BAR q50** | **59** | **42** | **97.0** | **201** | **41 (20%)** | **18** | 8/45 | 3293/4450 |
| LATCHCAL q25 | 47 | 21 | 101.0 | 180 | 110 | 3 | 8/39 | 2920/4450 (66%) |
| LATCHCAL q50 | 54 | 41 | 97.0 | 194 | 59 | 15 | 12/46 | 2920/4450 |

**LANE-1 VERDICT, stated plainly: participation FAILS at every grid cell (Job-2's fail bar) — and the diagnostic is the finding: 66–74% of replay decision steps landed on PARKED cells.** The failure is **COVERAGE-BOUND, not estimator-bound**: where cells exist, the aims perform — combined med 97.0, ≤97 rate 42/59 completions (71%), **lazy-leg rate halved (20% vs the actual 50%)**, gold-leg production 18 vs the actual wing's 14, and B3-conversion 8–14/41 sits exactly at the counterfactual's measured structural ceiling (~12/44). This quantifies end-to-end what BLOCKED-ON-DATA asserted: **the binding constraint is table reach; the coverage trigger (nightly accumulator) and the Plex prior-weight call are the whole critical path.**

LANE-2 (flagged hard): sim $ +213..+224 vs +32.49 actual on the 141-result subset — **SIM-FLATTERED** (conservative fill convention still books settlement wins at cheap sim fills queue reality might not grant; the subset denominator ≠ the ledger's −19.65/197). Directional only; Lane-1 is the verdict per C46.

## 6 · Gate evidence skeleton
Analysis code: py_compile PASS both scripts; committed 276807b0 (pipeline) + this report; **no live_v4 change in this dispatch, no flag, no deploy, no restart.** Hard constraints honored: floor 30 (prior-w 1.0 pending Plex; 0.5/0.25 rows above) · no silent interpolation (parked = null; replay carries, never borrows) · no sibling conditionals (structural: one read) · exits untouched · **walk-cap honest anchor interaction NOTED not built** — it ships with-or-before any arm, its own gate, per the standing bar.

Artifacts: `arb-executor/data/shape_corpus/aim_v2_candidate_{BAR,LATCHCAL}.json` · `aim_v2_derivation_meta.json` · `aim_v2_validation.json` (this dir) · `analysis/aim_v2_derive.py` / `aim_v2_validate.py` (re-runnable; the accumulator's nightly folds re-derive on the same code).
