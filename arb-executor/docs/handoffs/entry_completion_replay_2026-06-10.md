# Entry-completion economics via TAPE REPLAY — supersedes bbd88feb economics layer

**Read-only.** Envelope layer of `bbd88feb` (window-open keying, traded-print discipline) reused; the decision-theory economics (p_be / EV-dominance / inversion / divergence) are deleted and replaced by a tape replay. Artifact: `data/durable/entry_completion/entry_completion_replay_v1.parquet`
**parquet sha256:** `7883f5c8d99200a5dc9c468c381e39ea20441ff93e1c664ac98a0a334ba911e4`
Producer: `analysis/entry_completion_replay_v1.py`. Atlas/PMF sha-gated (9fde4b5d). C32-unknowns excluded.

## R1 — EQUIVALENCE GATE (hard halt) — **PASS**
Replay with NO completion branch reproduces the locked surface (`path_b_v3_per_n_simulation.parquet`), v3 fill logic verbatim (full premarket tape, raw float prices, no onset gate; per-regime offset = argmax expected_improvement).
| metric | replay | locked | gate |
|---|---|---|---|
| atlas blended ROC | 8.699% | 8.70% | — |
| maker blended ROC (pre-realism) | 12.110% | 12.11% | exact |
| **deployed blended ROC (r=0.60)** | **10.949%** | 10.9% | (i) ±0.3pp ✓ |
| N≥25 cells within ±2pp of locked per-cell ROC | **98.8%** (249 cells) | — | (ii) ≥90% ✓ |
| N≥25 cells beyond ±5pp | **0** | — | (iii) tail ✓ |

(Two replay bugs caught by this gate before the completion branch ran: onset-gating wrongly applied to the economic fill; per-regime LUT not taking the argmax offset. Both fixed → exact reproduction.)

## R2/R3 — completion branch (window-open keyed; sibling repriced to min(s0+X, sib_ask−1, 99−leg1_basis), X∈{1,2,3}; sibling's own tape checked for a premarket touch time-ordered after leg-1's fill; same locked per-cell exit replay; unexited settle).

## R4 — ELIGIBILITY (frozen: completion-leg net ROC > 0 at 0.5× conservative end, N≥25, Wilson-90% LB on fill rate)
| wave | (cat,cell,X) rows | distinct cells |
|---|---|---|
| **SHIP_FIRST** (clears 0.5×, lift≥0.10pp at 0.3×) | **36** | **12** (ATP_CHALL 7, ATP_MAIN 5) |
| REALISM_SENSITIVE (0.5× only) | 0 | 0 |
| INELIGIBLE (completion net ROC ≤ 0) | 51 | — |
| insufficient_data (N<25) | 906 | — |

**SHAPE pre-commit: cells clear completion net ROC>0 at 0.5× → mechanism SHIPS** (this is the eligibility table, not a deploy authorization; Part 2 / wave-gate validation unrun).

Eligible cells: **ATP_CHALL** {25,27,35,53,54,56,58}; **ATP_MAIN** {35,37,39,41,42} — all mid-band (25–58¢). No WTA cells eligible. Completion-leg net ROC 0.4–22.4% (mean 7.1%); top ATP_MAIN c41 22.4% / +12.9¢, ATP_CHALL c53 17.8%. Touch 0.62–0.90; N_conditioning 26–47. All 51 ineligible rows have completion net ROC ≤0 (mean −9.5% — completing locks a loss). Tails: orphan settle-0 mean 0.61, paired settle-0 = 0 (own both YES → pair never settles 0), completed-sibling loses mean 0.43.

## CAVEATS
1. **Realism band mechanics.** Per-completed-sibling net ROC is realism-invariant (quality of completed siblings); the 0.5–0.7× B25 band (bid_laying_policy L105) scales the deployed completion VOLUME, so eligibility = completion net ROC>0 AND blended-lift(0.5× × Wilson-LB fill)>0. REALISM_SENSITIVE is empty because every eligible cell's lift is far above the 0.10pp floor at 0.3× — no marginal cells; the staged-second-wave is unpopulated this run.
2. **Thin eligible set.** All 12 eligible cells sit just above N=25 (26–47 conditioning events); Wilson-90% LB on the fill rate is applied, but power is low — Part-2 wave-gate (N₁≥20 paired outcomes) is the live-validation backstop.
3. **Completion fills are all maker** (the sib_ask−1 cap forces sub-ask resting bids; no taker fee on completion).
4. **Window-open keying** (output cell = leg-1 window-open price) differs from the v3 economic frame (T-20 anchor); leg-1 fill economics use the validated v3 sim unchanged, the cell label uses the ratified window-open envelope.
5. **Tick spot-check** (bbd88feb, retained): minute-bar touch is conservative (bars undercount 0.00–0.13 vs g9 ticks) — completion fill rates are if anything understated.
