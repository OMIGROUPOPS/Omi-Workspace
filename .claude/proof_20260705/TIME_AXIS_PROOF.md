# TIME-AXIS OUTCOME PROOF — the table decided: **IT DOES NOT SHIP** (2026-07-05)

## Prior art (gate — C45)
- Greps: `dip_surface|dip_timing|premarket_drift|time.bin|A49|A50|P3b` over LESSONS.md, JUNE_VAULT.md(+APPENDIX), .claude/rulings/, analysis/.
- Established: `analysis/exit_charts/premarket_{drift,dip_surface,dip_timing}_{CAT}.csv` (tour cats; per-cell reach-by-depth and cumulative reach-by-time surfaces — THE source data; this block is deployment of that analysis, not new measurement); **A49** (aim = fillable dip, not FV), **A50** (dips cluster late — the timing surfaces quantify it per cell); P3b shape-sequenced replay (decay-curve precedent, Vault 4H#3); the deployed flat aim_table.json (faller MAIN 2/CHALL 3/ITF 4; riser CHALL 3/ITF 3/2 as of `9925dd6`); CLOCK_AUDIT downstream flag (a): every tts quantity inherits the card-marker clock the surfaces were built on.
- Staged-never-armed on this topic: none (first time-axis build). Coupled staged build: **C-PM-CLOCK Part 1** (`per_match_clock`, ce38ca8c) — see the verdict.
- DELTA: the 3-D table {cat × price-bucket × tts-bucket} + the two-lane replay of it against the 147-game box.

## What was built (committed, re-runnable)
`analysis/aim_time_axis.py` → `docs/policy/aim_table_t.json`: per (cat, price-bucket, T8/T6/T4/T2/T1/T30),
`faller_depth` and `riser_post` from **P_remain(D,T) = P_total(D) × (1 − φ(T))** (φ = cumulative reach-by-time
share, D=3 shape; depth = max D with P_remain ≥ 0.50; one read serves both legs — the riser's post is the same
surface read at the riser's own cell). ITF: ATP_CHALL shape anchored to the deployed flat values at T4
(stated assumption). Shape confirms the operator's frame: **deeper early, shallower late** (e.g. ATP_CHALL
60-79: T8/T6 = 3¢ → T4..T30 = 1¢; ITF_M: T8/T6 = 6¢ → T4+ = 4¢).

## THE TWO-LANE VERDICT (replay of the 147-game box, real prints, card clock — same clock as runtime)
| | result |
|---|---|
| population | 256 filled legs graded; **tts-bucket mix: T4 = 255, T2 = 1 — the early buckets (T8/T6) are UNREACHABLE under today's T-240 placement cap** |
| LANE 1 — MECHANISM | **LOSES to flat.** 67 legs no-change (ITF rows reduce to the deployed flat values at T4+ by construction). **Zero legs get deeper aims** in any reachable bucket. **189 legs get SHALLOWER aims → Δaim distribution shifts POSITIVE (worse) by mean +2.23¢/leg** — the flat aims demonstrably filled on the actual tape; time-aware would have paid more for the same fills. Retention question never arises (nothing deepens). |
| LANE 2 — P&L | **−$20.31** across 189 changed legs (secondary; consistent with Lane 1, not needed for the verdict) |
| blind spot (stated) | shallower bids would also capture extra fills on legs that never filled (not in the population — biases against shallow). Cannot rescue a verdict where the mechanism lane is this lopsided, and the just-deployed riser revision's LIVE evidence (83–90% retention at 3¢, current-price-anchored) directly contradicts the surface's cell-anchored P_remain at T4. |

**Pre-registered rule honored: time-aware aims do not beat flat aims on Lane 1 → the fix does not ship.
No flag armed, no restart, the running `9925dd6` untouched.**

## Why it lost — and what that actually says (the coupling finding)
1. **The time axis's value lives in T6/T8 — and we can't post there.** The surfaces say depth pays EARLY;
   under the T-240 cap on the card clock, every real post lands T4-or-later, where remaining-dip probability
   is already spent. **`time_aware_aim` without `per_match_clock` is strictly worse than flat (proven
   tonight). The two staged builds are COUPLED:** Part 1's honest clock + widened fallback windows are what
   make T8/T6 reachable (the real ITF premarket = pre-T-4h on the card clock), and ITF's derived early
   depths (6¢/4¢) are exactly the cells that then apply. Re-run this proof when Part 1 arms.
2. **Anchor mismatch (measurement debt, named):** the surfaces measure dips below the WINDOW-OPEN cell; the
   bot's aims (and tonight's riser Lane-1 win) anchor at CURRENT price at post. Cell-anchored P_remain
   understates current-anchored retention near start. The re-derivation for the honest-clock era should be
   built current-price-anchored (and on honest-anchored time bins).
3. The patch (`_aim_for(cat, bucket, tts)` + aging re-derivation through the freshness path) is **deferred
   with reason** — its only honest table fails Lane 1 in every bucket today's windows can reach; staging a
   consumer now would be ceremony. Build it WITH the Part-1-era re-derivation, gate it on the same proof.

*Machinery: `analysis/aim_time_axis.py` (derivation), `/tmp/proof_time_rows.json` via `proof_time_axis.py`
(replay; committed alongside). Both re-runnable.*
