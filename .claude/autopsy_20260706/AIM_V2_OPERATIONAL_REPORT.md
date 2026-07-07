# AIM_V2 OPERATIONAL REPORT — the Plex ruling executed, GATED-OFF (2026-07-06 20:23 ET)

**Nothing arms. Ruling committed verbatim: `.claude/rulings/PLEX_AIM_V2_RULING.md`. Table: `data/shape_corpus/aim_v2_operational_LATCHCAL.json`. Lint: py_compile PASS on all analysis code. No live_v4 change, no flag, no restart.**

## 2 · The OPERATIONAL table under the ruled parameters
Params (verbatim from the ruling, all applied): clock LATCH-CAL canonical (K=600/M=20,000) · **per-event residual gate 25m: 16 events failed → no_bell** · w=0.25 · dip admissibility ITF+CHALL only with P(dip≥3¢)≥0.50, mains NULL full stop (incl. fallback) · complement per-cell gate · **fallback ⑦ ACTIVE** (parents serve only at own honest-n≥30; borrowed_from + resid_sd ×1.5/×2.0).

| serving tier | keys |
|---|---|
| cell | 37 |
| tier2 | 587 |
| tier3 | 751 |
| null | 95 |

True cells collapse to **37** at w=0.25+floor-30 (from 217 at w=1.0) — the ruled weight is honest about how little the card corpus buys; **the hierarchy is what makes the table addressable: 1,338 of 1,470 keys served by a valid parent.** Exclusions: {'thin_prebell': 57, 'no_bell': 1255, 'dead_tape': 536, 'not_two_tickers': 172, 'residual_gate_25m': 16}.

## 3 · RE-VALIDATION (ledger day, C46 two-lane, ratified bars) — reported straight

| grid | pairs (actual 149) | ≤97 | comb med | legs | lazy | gold (actual 14) | B3-conv | serve: cell/t2/t3/null/dip-inadm |
|---|---|---|---|---|---|---|---|---|
| q25 | 21 | 19 | 91 | 128 | 0 | 13 | 14/34 | 651/2378/226/1195/495 |
| q50 | 45 | 42 | 97 | 181 | 0 | 16 | 9/42 | 651/2378/226/1195/436 |

**Participation is still short at w=0.25 — 45/149 pairs at q50 — exactly as the ruling anticipated; stated straight.** The fallback chain's separate contribution: NULL steps fell 66–74% → **26%**; tier-2 serves the majority (2,378 steps) vs true cells 651 — the borrowed tiers ARE the table until cells fill. Where pairs completed: ≤97 on 42/45 (93%), combined med 97, gold-leg production 16 (actual gold wing 14), B3-conversion 14/34 at the counterfactual's measured ceiling, lazy-leg 0 by construction. Lane-2 (+$174/+$237 vs +$32.49, n=141) remains SIM-FLATTERED — flagged, not a verdict.

## 4 · THE RAMP FORECAST — dated, from night-1 real ingestion (linear; caveats below)

| tier | now ≥30 | median cross | p75 cross | zero-rate bins |
|---|---|---|---|---|
| ITF_W cat curve (25 Tbins) | 0 | **2026-07-08** | 2026-07-10 | 0 |
| ATP_CHALL cat curve | 0 | **2026-07-10** | 2026-07-11 | 0 |
| ITF_M cat curve | 0 | 2026-07-20 | 2026-08-04 | 3 |
| WTA_CHALL cat curve | 0 | 2026-07-20 | 2026-07-20 | 0 |
| **§3 trigger (250/500 cells honest-n≥30)** | 287 projectable / 213 zero-rate | **2026-08-04** (linear) | — | 213 |

Read: **the ⑦ fallback parents go honest-valid within 2–14 days (ITF_W by ~July 8) — weeks before full cell coverage (Aug-04 linear).** Caveats, stated: single-night rate; tonight's slate is NOT yet folded (the 04:45 accumulator folds tapes concluded ≥6h — night-1 under-counts); the 213 zero-rate cells are price-buckets×Tbins the current slate mix never visits — tournament rotation may light them or they may be structurally rare; day-of-week variance unmodeled. The schedule re-dates itself nightly from coverage.json.

## 5 · PARKED (no build): the live_scores retention gap
tennis.db `live_scores` (TE) retains only finished/scheduled — the collector overwrites every in-play transition; 19,264 rows, zero observed starts (START_TIME_JOIN.md). A retention change would bank observed TRUE starts from tonight forward — the only path to a real start-time archive found on disk. **PARKED pending its own dispatch.**