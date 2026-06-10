# Entry drift envelope + completion eligibility — PART 1 (consolidated spec)

**Read-only derivation.** Artifact: `data/durable/entry_completion/entry_completion_part1_v1.parquet`
**parquet sha256:** `21a079e939d6083045a8f45ffa543378c4809d82ae00844893db18f19fcc2115`
Producer: `analysis/entry_completion_derivation_v1.py` · tick check: `analysis/entry_completion_tickcheck_v1.py`
PMF sha256-gate `9fde4b5d` PASSED. Unit = locked 90-cell grid 5–94c per category (gated-optima), window-open keyed (first traded print, last-trade discipline), C32-unknowns excluded, premarket = T-240→live-onset (volume-accel, trade_count≥10 within final hour).

## Gates
| gate | result |
|---|---|
| Foundation/equivalence (pairing) | PASS — reused (1907 / legA 69 / legB 34 / comb 103.1 / favwin 0.690) |
| Sanity invariant (ordered ≤ unordered, every cell) | PASS — 0 violations |
| C38 reconciliation (matched-method reach vs entry_table fill) | PASS within noise — mean \|Δ\|=0.059 (≈0.8 binomial SE); 13/248 cells >0.15 = unreplicated grain-mass pooling on deep-favorite off-7 + grid-edge cells |
| Tick spot-check (g9 ticks vs minute-bar, k=1) | bars UNDERCOUNT touch by +0.00…+0.13 → derivation is CONSERVATIVE (B25 direction) |

## Eligibility shape (per-cell; 359 cells = 4 cat × ~90)
| wave | cells | atp_chall | atp_main | wta_main | wta_chall |
|---|---|---|---|---|---|
| WAVE 1 (passes b+c, divergence ≤0.1) | **83** | 31 | 26 | 26 | 0 |
| WAVE 2 (passes b+c, divergence >0.1, HELD) | **33** | 10 | 11 | 12 | 0 |
| INELIGIBLE (fails b or c) | 80 | — | — | — | — |
| insufficient_data (N<25) | 163 | — | — | — | 89 |

**SHAPE pre-commit: eligible pairs exist at the 0.4x B25 haircut → mechanism does NOT auto-fail; proceeds toward Part 2.** (NOT a deploy authorization — eligibility table only.)

## Top eligible cells (mechanically ranked, Wilson-LB margin, j≤3)
| cat | cell | k | j | down_reach | rec_pd | wilson_lb | p_be | div | ev_0.4x | wave |
|---|---|---|---|---|---|---|---|---|---|---|
| atp_main | 66 | 1 | 1 | 0.82 | 0.68 | 0.56 | <0 | 0.10 | 8.4 | W1 |
| wta_main | 53 | 1 | 1 | 0.82 | 0.72 | 0.60 | <0 | 0.00 | 3.4 | W1 |
| atp_chall | 67 | 1 | 1 | 0.79 | 0.73 | 0.63 | <0 | 0.11 | 2.7 | W2 |
| atp_main | 41 | 1 | 1 | 0.88 | 0.62 | 0.52 | <0 | 0.01 | 3.6 | W1 |
| wta_main | 82 | 1 | 2 | 0.96 | 0.52 | 0.37 | <0 | 0.07 | 17.9 | W1 |

drift (cell[window_close] − cell[window_open]) mean −1.01c (range −35.5…+12.6) — quantifies the window-open-keying assumption (PREAMBLE CAVEAT); modest in aggregate, fat left tail = favorites bleeding into onset.

## CAVEATS
1. **Touch-as-fill proxy.** down_reach / recovery / inversion are TOUCH events (traded price_low≤target down; price_high≥target up), an upper bound on maker FILL (queue priority not modeled). Eligibility reads as a fill ceiling.
2. **Minute-cadence understatement (B25), spot-checked.** g9 tick vs minute-bar (k=1): saturated cells 0.000; non-saturated +0.08 (wta_main c71), +0.107 (atp_main c59), +0.133 (atp_chall c11 thin). Bar-aggregation cuts AGAINST touch detection → all touch rates are conservative/understated; true completion feasibility ≥ reported.
3. **p_be is negative for most eligible cells** — by construction, not a bug: the per-cell orphan atlas EV (T-20 frame, gated-optima join) is slightly negative (corpus mean −0.75c; standalone premarket legs ≈ break-even after vig), so the EV-dominance breakeven probability goes ≤0 and criterion (b) reduces to "floor>0 ∧ recovery exists." Real discrimination = floor>0 (k+j>vig≈3), N≥25, and the 0.4x EV-dominance (c).
4. **Window-open vs entry_table anchor.** entry_table/dip-surface anchor on the LAST premarket trade; this derivation keys on the FIRST (window-open) per spec. The matched-method recon (same last-trade anchor) reconciles to 0.059; the window-open deliverable differs by the drift column (caveat 3 of the spec).
5. **Reconciliation residual.** The unreplicated grain-mass pooling + monotonic smoothing in build_premarket_surface accounts for the 13 deep-favorite/edge cells >0.15; touch LOGIC is validated (direction reach≥fill, mean within noise).
6. **WAVE-2 held** (divergence >0.1 = partner-direct and inversion disagree → pinned-sum inversion breaks, books move independently). Inversion is diagnostic only, never gates.
7. **wta_chall** (887 N) is almost entirely insufficient_data — no eligible cells; not ineligible.
