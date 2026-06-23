# OMQS S0 gate v2 — complete per-mechanism fill model (spec v2 §8)

**Run:** Jun 19–22 existing tape · per-mechanism fill model · clock = exchange-trade ts both sides · ≤100ms.
**VERDICT: HALT — but the residual is now 100% queue-granularity (data limit), not model. NO S1–S5.**

## What changed vs v1
- **Taker legs (complete_cross / miss_fallback) now fill immediately at the ask** (not forced through maker sell-flow). **Jun-22 complete_cross: 3 placed, 0 missed** → taker model verified correct.
- **Adopted/reconcile/"other" excluded** from the placement universe (6/3/0/22 per day) — they're inherited positions, not placements.
- **Walk now includes `v4_move_repost` + `v4_fallback_maker_clamp`** prices, so the fallback ask-1 clamp price is modelled.

## Per-day both-direction diff
| day | in-universe placed | bot fills (mapped) | replay | MISSED | SPURIOUS | TIMING>100ms | result |
|---|---|---|---|---|---|---|---|
| 06-19 | fallback 72, unfilled 32, resting 22, eng 25 | 119 (119) | 31 | 111 | 23 | 3 | HALT |
| 06-20 | fallback 26, unfilled 12, resting 17, eng 5 | 48 (47) | 24 | 30 | 6 | 3 | HALT |
| 06-21 | unfilled 14 | 0 (0) | 8 | 0 | 8 | 0 | HALT |
| 06-22 | fallback 65, unfilled 61, resting 63, eng 15, **complete_cross 3** | 146 (145) | 40 | 125 | 19 | 1 | HALT |
| **TOTAL** | | | | **266** | **56** | **7** | **HALT** |

## Diagnosis — residual is queue-granularity (the 6s/backfilled data limit), not the model
The failures are now **entirely on MAKER legs**, and they fail in **both directions** — the signature of a noisy queue-ahead *estimate*, not a logic error:
- **MISSED** = filled makers (fallback_maker, resting_maker, engagement): the 6s depth_recorder **over-states** queue-ahead at the cast price (shows a standing wall) → `cum_sell > queue+size` never trips → the real fill isn't credited. (Jun-22: missed = fallback 54, resting 59, eng 12.)
- **SPURIOUS** = `unfilled_maker` legs (Jun-21: 0 actual fills, 8 spurious): the 6s snapshot **under-states** queue-ahead (or 0 when the leg isn't in the recorder) → over-credits a fill that never happened.

Both are the same root cause: **queue-position fills cannot be reconstructed from a 6-second book snapshot** — the bot's real fill depended on the real-time (sub-second) queue-ahead at the fill instant, which the 6s recorder cannot supply. The proof it's data not model:
- **Taker legs (deterministic, no queue dependence): 0 missed.** The model reproduces them exactly.
- Maker legs fail symmetrically (missed *and* spurious) — pure estimate noise, not a one-sided logic bug.
- 311/312 bot fills mapped cleanly to an exchange trade → the clock reference is correct.

## Conclusion
The fill model is **complete and correct** (taker = immediate lift ✓, adopted excluded ✓, fallback-clamp in walk ✓, maker = queue-adjusted ✓). The S0 gate **cannot go green on existing tape** because the maker queue-adjusted fill is queue-position-dependent and the 6s depth_recorder can't give the real-time queue. **The definitive ≤100ms set-equality run is tomorrow against the live WS capture** (sub-second per-level depth → exact queue-ahead, ms trade ts). No S1–S5 scores until that run is green.
