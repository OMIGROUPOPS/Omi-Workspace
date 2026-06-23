# OMQS Harness — S0 correctness gate result (spec v2 §8)

**Run:** Jun 19–22 existing tape · queue-adjusted fill model · **clock reference = exchange-trade ts on both sides** (bot fills mapped to the realizing Kalshi trade, not the booking ts).
**VERDICT: HALT — fill model not set-equal to the bot's `entry_filled` stream. NO S1–S5 scores.**

## Per-day both-direction diff
| day | leg types placed | bot fills (exch-ts mapped) | replay fills | MISSED | SPURIOUS | TIMING>100ms | PRICE | result |
|---|---|---|---|---|---|---|---|---|
| 2026-06-19 | fallback_maker 72, other 33, engagement 25, staircase 27 | 125 (125) | 24 | **116** | 15 | 3 | 1 | HALT |
| 2026-06-20 | fallback_maker 26, staircase 22, other 10, engagement 5 | 51 (49, 2 no-match) | 22 | **32** | 3 | 3 | 0 | HALT |
| 2026-06-21 | other 8, staircase 6 | 0 | 7 | 0 | **7** | 0 | 0 | HALT |
| 2026-06-22 | (all types) | — | — | **152** | 13 | 2 | 0 | HALT |
| **TOTAL** | | | | **300** | **38** | **8** | **1** | **HALT** |

## Diagnosis — two distinct causes
**(1) ENGINE INCOMPLETENESS — the dominant cause (≈all 300 MISSED).** The replay implements only ONE fill mechanism — a maker bid hit by cumulative taker-NO sell-flow exceeding queue+size (queue-adjusted). But the bot's actual fills span ≥3 mechanisms the model does not yet implement:
- **fallback_maker** (T-20m ask-1 clamp, fills near the gun) — BER@39, ROD@47, FEL@63, CIG@94, DE@95… all MISSED.
- **miss_fallback / complete_cross** (taker lift at ask / at the gun — fill immediately, not via sell-flow-to-our-bid) — MISSED.
- **engagement-join** (joins the standing bid) and **reconcile/"other"** (adopted positions, not fresh placements — these shouldn't be in the placement universe at all) — MISSED / spurious.

The clock fix works: 174/176 bot fills mapped cleanly to an exchange trade (2 no-match). So MISSED is not a clock artifact — it is the engine modeling one mechanism out of several.

**(2) GRANULARITY — the secondary cause (the SPURIOUS + TIMING), expected on existing tape.** 6s depth_recorder under-estimates queue-ahead → the queue-adjusted model over-credits fills (Jun-21: 0 actual fills, 7 spurious). API-backfilled trades give ~0.5–8s timing slop, and two wrong-trade matches (HUM −1253s, SPI −2343s) where the model fired on an earlier sell burst. The definitive ≤100ms validation runs **tomorrow against the sub-second WS capture** (now live), where queue-ahead is exact and trade ts is to the millisecond.

## What it means
The gate did its job: it refused to pass an engine that reproduces only ¼ of the bot's fills, so no stratagem (S1–S5) score can be trusted yet. **Before the gate can go green, the fill model must implement per-mechanism fills** (maker-sell-flow ✓; + fallback-clamp, taker-cross/complete-cross, engagement-join) and **exclude adopted/reconcile legs from the placement universe**. Then re-run — granularity-limited on existing tape, definitive tomorrow on WS.
