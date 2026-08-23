# L19a PASS-1 COUNTER-GRADE — @e5c6212c

License: LAW_INDEX @ e5c6212c, sha256 c7c72715… · L8 L11 L17 L18 L19a L20 L22 · honest ruler · one denominator · process-first (F-VS-078).
Seat: CC verification. Data: L19A_PASS1_COUNTER_GRADE.json · L19A_PASS1_IDENTITY_SETS.json (frozen; sha256 c41f0761…).
Scope: read-only; no 804 run, no sealed read, no retune.

## 1 — Integrity

| item | verdict |
|---|---|
| Honest scoreboard | reproduced independently from PER_GAME_OUTCOME_TABLE + truth table @c0056976 + offer ledger: **77/680 · 226¢ · mean Δ2.935**; by-category equal; hard floor 77 < 311 SELF-STOP honest |
| Identity | champion 311 re-derived from V52l ledger @96597c98 under the same rule; retained/lost/gained 53/258/24 and all three id lists byte-equal to SCORECARD |
| Invalid completes | 526 completed − 77 valid = 449: **367 post-bell fills**, 60 not offered-under-par, 16 pre-formation, 6 not gradeable |
| Leave-self-out | bookkeeping exact: Σ_e(n − n_loo(e)) = n on 16/16 cells; 28 non-OK-span events remove 0 everywhere; 24-event spot-check: removal counts match rebuilt per-event counts on 16/24 (LAJSVA, GIUBAR, DANPRA exact; 8 differ where fitted-pass fills changed the stage population) |
| Fit population | **243,630 records are NOT receipted**: they come from the prefit replay (surface=null), which is neither committed nor custodied; the sentence archive is the fitted replay (rebuild 235,355: OPEN cells +1,836/+851, HALF_PAIR −321/−295). Coefficients cannot be re-derived from banked bytes; OPEN-cell refits agree to ~0.3 intercept, HALF_PAIR NO_DIP cells diverge (slope 5.08 vs 0.85) |
| Sealed | 0 overlap of the 171 sealed events with corpus 12,509 / historical 5,879 / range spectrum 6,252 / Foundation 9,000 / dev 804 / prints 804 events (4,836,462 rows = report's scanned count); no late-July event in any store; FORBIDDEN_ACCESS holdout=false holds |
| Determinism | two clean builds PASS; artifact hashes equal; sentence archive 800793c6… present in custody at the stated bytes |
| Fit-error clamp | code clamps predicted error at 0 (Math.max); HALF_PAIR NO_DIP cells have negative intercepts (−1.85/−1.78) so OWN_TAPE/REFLEX run at multiplier 1 for phase < ~0.12; sentences cite the clamped 0, law text does not state the clamp |

## 2 — 53 / 258 / 24 decomposed

| set | n | ATP_CHALL / ATP_MAIN / WTA_CHALL / WTA_MAIN | legs STILL / MOVER | mean Δ pass-1 | mean Δ champion |
|---|---:|---|---|---:|---:|
| RETAINED | 53 | 9 / 29 / 1 / 14 | 62 / 44 | 2.736 | 2.491 |
| LOST | 258 | 115 / 40 / 46 / 57 | 361 / 155 | — | 2.256 |
| GAINED | 24 | 6 / 12 / 1 / 5 | 25 / 23 | 3.375 | — |

Basis that priced the rest (from the sentences, dominant normalized weight):

- RETAINED (at pass-1 fill): REFLEX_TRACKING 83/106, GRADED 16, OWN_TAPE 5, TIME_BEARING 2; touch BELOW_BEST_BID_1C 67, AT_BEST_BID 27.
- GAINED (at pass-1 fill): REFLEX 27/48, GRADED 12, OWN_TAPE 5, TIME_BEARING 4. Champion on these 24: 14 single-leg, 4 completed post-bell, 6 completed pre-formation — gains are ruler-side, not new captures.
- LOST (rest standing at the champion's fill moment, 508 legs): REFLEX 313, TIME_BEARING 175, GRADED 12, OWN_TAPE 8; touch BELOW_BEST_BID_1C 204 · 2C 97 · 3C 40 · AT_BID 33. Champion entry − pass-1 rest: **median 2¢, mean 2.96¢; rest at/above the champion's entry on 12.6%**. By basis: REFLEX median 1¢ (n 313), TIME_BEARING median 4¢ (n 175), GRADED 3.5¢. Pass-1 then filled those legs POST_BELL 257, never 109, valid 149. Per game: POST_BELL+VALID 95 · POST_BELL×2 53 · NONE+POST_BELL 56 · NONE+VALID 53.

Mechanism: the print that filled the champion passed 1–4¢ above pass-1's rest; the rest filled later, in play, or never. ATP_CHALL/WTA_CHALL carry the TIME_BEARING tail (97/44 of 175).

## 3 — Thirty sentences

Draw: sha256("CC_P1_DRAW|set|event") order; LOST 18 · RETAINED 6 · GAINED 6. One derivation each: LOST = the rest at the champion's fill (widest-gap leg); others = the later-filled leg at its fill.

- sentence == action: 30/30. FITNESS_WEIGHTS == structured basis_weights: 30/30.
- citation == receipt: fit_n / predicted error / multiplier / fit_source checked against loo_by_event[event][cell] of the committed surface: 29/30; MOLDAV cites "0" where the LOO line gives −0.605/−0.608 (clamp).
- Read as sentences — incoherences filed:
  1. "no placement constant" vs `REFLEX_TRACKING depth_cents: 1` (literal) and `OWN_TAPE_PRESENCE 0`: the blend's candidate depths are {q50, q50, 0, 1}; reflex-dominated blends round to 1 → rest = bid − 1 (18/30 rows show REFLEX 0.41–0.71, CHOSEN 1–2).
  2. CHOSEN_DEPTH > WEIGHTED_DEPTH on 7/30 (rounding up and PAIR_REQUIRED_DEPTH: MARARS 0→5).
  3. Crossed/locked books cited as live touch: HERALM bid/ask 58/54, PODLEE 57/56, COLSKA 88/88; post-only cap (ask−1) then sets the depth (HERALM final depth 5 vs chosen 1).
  4. BLEND_FITNESS_MASS 0.002–0.03 on most rows — the "continuous contribution" is a normalization of near-zero masses; the sentence states mass but not that it is negligible.
  5. WESCOP: neighbors 0.498/0.501 at depth 12, own/reflex 0.000 at formation+180 s → rest 4 against bid 16 (champion filled 16).

## 4 — Pass-2 standing watch

Not landed: branch codex/window1-v54-l19a-neighbor-voted-composition-pass2-20260823 tip = e5c6212c (pass 1); only OMI-Window1-private/stage1/v54_l19a_neighbor_voted_composition_pass2/build1 exists (in progress, not banked). Validation targets frozen now: LOST_258 and GAINED_24 in L19A_PASS1_IDENTITY_SETS.json (sha256 c41f0761…). Pass-2 counter-grade order on landing: enrichment integrity (≥10 library games' floor-capture attributions vs own bounded tapes) · LAJSVA neighbor-vote verbatim · recovery vs the frozen sets · full-804 honest numbers · floor verdict.
