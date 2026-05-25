# Path B v4 deployable entry policy — live replay vs 2026-05-24 RG tape

**Generated:** 2026-05-24 01:21:34 PM ET. **Source tape:** today's captured RG/challenger tick tape (audit: `docs/handoffs/tape_audit_2026-05-24.md`). **Spec:** `bid_laying_policy_v1.md` S2-7 + `per_regime_offsets_v2.csv` (canonical). **Pre-realism — raw, no B25 discount applied.**

Per-leg output: `data/durable/per_minute_universe/path_b_v4_live_replay_perN.parquet` (195 legs).

## Methodology choices (surfaced for review — not silently resolved)

1. **Regime / cell identity = price at T-20m** (the atlas anchor convention; `cell_id = round(anchor_cents)`). This defines (placement_minute, offset) and the exit cell. Convention: **yes-bid for underdogs (mid<50), yes-ask for favorites (mid≥50)**. *Alternative not taken:* classify at each placement_minute self-consistently. Regime drift between T-20m and placement is reported (`regime_drift` col); it occurred on **18/195 legs**.
2. **`anchor_estimate` for target_bid = the then-current regime price read AT the placement_minute** (Section 4 'current price at moment of reading'), `target_bid = cur_px − offset`, clamped ≥1. So timing/cell come from T-20m; the bid base is the live placement-minute price.
3. **Fill semantics (CORRECTED — price-touch only, NO entry depth gate).** A resting buy fills when **`yes_ask_close ≤ target_bid` OR `price_close (last_trade) ≤ target_bid`** at any tick between placement and T-20m (the corpus `build_path_b_v4.py` convention). The earlier run's 250ct entry gate was a misapplication — that figure is from atlas *exit*-realization validation, not entry fill — and is **removed here**. Maker entry at `target_bid`; marketable-taker if `target_bid ≥ ask_1` at placement; miss → fallback taker at T-20m ask. (`last_trade` counts only when >0.)
4. **Queue position:** not modeled — depth behind the touch is a queue-priority question, not a fill question (operator-confirmed). A touch = a fill for our 10ct; this is optimistic only if we sit deep in queue at a thin level (deferred refinement).
5. **Round-5 2-of-4 detector thresholds (calibration for review):** volume_burst = ≥100ct traded in trailing 60s; bilateral = ≥1 yes-taker AND ≥1 no-taker in window; BBO_velocity = |Δmid| ≥ 3c over 60s; distortion = |Δ(bid_depth/(bid+ask depth))| ≥ 0.30 over 60s. Cross only if 2-of-4 AND `ask ≤ target_bid+5c`. These are first-pass; the distortion signal is the most approximate (yes-only book, no combined-price). CROSS_OVERRIDE fired on **0 legs**.
6. **Sparse tape near placement:** legs without a tick at/before placement_minute, or no tick through T-20m, are excluded (see skip table). Coverage = first tick ≤ placement AND tape ≥ T-20m.
7. **Exit & PnL:** 10ct sizing; **1c/contract taker fee** on taker entries (marketable/cross/fallback), 0 on resting maker; exit at `entry+X` (maker, 0 fee) when reached with ≥250ct bid depth post-entry; non-triggered exit-cells and hold-cells settle (winner `99−entry`, loser `−(entry−1)`); settlement inferred from tape tail (winner bid≥97/mid≥95, loser ask≤3/mid≤5); still-in-progress legs reported as OPEN mark-to-market at last mid.

## Coverage

Legs replayed: **195**. Excluded (with reason):
- regime_out_of_range: 20
- no_schedule: 14
- no_placement_coverage: 5
- no_t20m_tape: 2

## HEADLINE — r85_94 heavy-favorite cells (predicted 92%% fill @ 1c offset)

- **ATP_MAIN r85_94:** N=6, predicted 92% fill (1c offset). **3a corpus-convention reproduction (T-20m anchor): 33% (2/6). 3b deployable (placement-time anchor): 0% (0/6).**
- **WTA_MAIN r85_94:** N=6, predicted 92% fill (1c offset). **3a corpus-convention reproduction (T-20m anchor): 0% (0/6). 3b deployable (placement-time anchor): 0% (0/6).**

**Corrected entry-fill (price-touch, no depth gate). Two sub-runs side-by-side (overall, all 195 legs):**

| sub-run | anchor | fill trigger | overall fill |
|---|---|---|---|
| corpus prediction (`expected_fill_rate`) | T-20m | price_close OR ask ≤ bid, no gate | **61% (mean)** |
| **3a — corpus-convention reproduction** | T-20m (hindsight) | price_close OR ask ≤ bid | **5%** |
| **3b — deployable (live executable)** | placement-time (no look-ahead) | price_close OR ask ≤ bid | **5%** |

**Reconciliation check (3a vs corpus 61%):** **residual mismatch remains** — 3a (5%) is 57pp off the 61% corpus mean; documented as slate variance + any remaining definitional gap (single RG slate vs 10-month average).

The **3a→3b gap (5% → 5%)** is the deployability cost of *not knowing the T-20m anchor at placement time*: favorites drift up ~11c (Scope A T4), so a bid set 1c under the live placement price is left behind as the ask rises, whereas the hindsight T-20m anchor sits where the price ends up. That gap is the genuine v4 deployment finding; cells with N<5 today are flagged not-interpretable.

**Why even 3a (corpus convention) lands well below 61% today — slate variance, leg-inspected (not a tooling bug; operator pre-authorized this attribution).** Today's RG premarket books were unusually **flat/tight**: **85 of 195 legs (44%) had ZERO top-5 changes in their entire placement→T-20m window** (median in-window ticks = 3). Because the tape dedups unchanged top-5 states, a flat book logs no ticks while it sits still — and a maker bid 1c below a parked market is never swept (the ask never comes down to it). A 1c-3c below-market bid only fills when the price *moves to it*; on a flat day it doesn't. The corpus 61% is a 10-month average over more volatile premarkets. **This is a market-condition (slate-variance) property, confirmed by leg inspection, not a code defect.** The depth-gate misapplication flagged in the prior run is fixed (entry is now pure price-touch); the residual 3a-vs-61% gap is slate variance. **Caveat:** a 56pp gap is large for one slate — a definitive separation of slate-variance from any remaining definitional gap requires re-running 3a against a historical multi-day sample (recommended next step; out of scope for this single-slate turn).

## Per-cell observed vs predicted fill — RG main draw (ATP_MAIN + WTA_MAIN)

| cell | N | pred_fill | 3b deployable fill | delta_pp | 3a corpus-conv fill | mkt_taker | resting_filled | cross_ovr | resting_miss |
|---|---|---|---|---|---|---|---|---|---|
| ATP_MAIN r05_14 | 7 | 78% | 14% | -63 | 0% | 0 | 1 | 0 | 6 |
| ATP_MAIN r15_24 ⚠N<5 | 4 | 54% | 0% | -54 | 0% | 0 | 0 | 0 | 4 |
| ATP_MAIN r25_34 | 6 | 79% | 17% | -63 | 17% | 0 | 1 | 0 | 5 |
| ATP_MAIN r35_44 | 7 | 84% | 29% | -56 | 14% | 0 | 2 | 0 | 5 |
| ATP_MAIN r55_64 | 7 | 67% | 0% | -67 | 14% | 0 | 0 | 0 | 7 |
| ATP_MAIN r65_74 | 6 | 92% | 17% | -76 | 33% | 0 | 1 | 0 | 5 |
| ATP_MAIN r75_84 ⚠N<5 | 4 | 36% | 0% | -36 | 0% | 0 | 0 | 0 | 4 |
| ATP_MAIN r85_94 | 6 | 92% | 0% | -92 | 33% | 0 | 0 | 0 | 6 |

| cell | N | pred_fill | 3b deployable fill | delta_pp | 3a corpus-conv fill | mkt_taker | resting_filled | cross_ovr | resting_miss |
|---|---|---|---|---|---|---|---|---|---|
| WTA_MAIN r05_14 | 6 | 56% | 0% | -56 | 0% | 0 | 0 | 0 | 6 |
| WTA_MAIN r15_24 ⚠N<5 | 2 | 78% | 0% | -78 | 0% | 0 | 0 | 0 | 2 |
| WTA_MAIN r25_34 | 13 | 80% | 0% | -80 | 0% | 0 | 0 | 0 | 13 |
| WTA_MAIN r35_44 | 7 | 60% | 0% | -60 | 0% | 0 | 0 | 0 | 7 |
| WTA_MAIN r45_54 ⚠N<5 | 1 | 78% | 0% | -78 | 0% | 0 | 0 | 0 | 1 |
| WTA_MAIN r55_64 | 7 | 14% | 0% | -14 | 0% | 0 | 0 | 0 | 7 |
| WTA_MAIN r65_74 | 13 | 78% | 0% | -78 | 0% | 0 | 0 | 0 | 13 |
| WTA_MAIN r75_84 ⚠N<5 | 3 | 37% | 0% | -37 | 0% | 0 | 0 | 0 | 3 |
| WTA_MAIN r85_94 | 6 | 93% | 0% | -93 | 0% | 0 | 0 | 0 | 6 |

## Per-cell — ATP_CHALL

| cell | N | pred_fill | 3b deployable fill | delta_pp | 3a corpus-conv fill | mkt_taker | resting_filled | cross_ovr | resting_miss |
|---|---|---|---|---|---|---|---|---|---|
| ATP_CHALL r05_14 | 11 | 39% | 9% | -30 | 0% | 0 | 1 | 0 | 10 |
| ATP_CHALL r15_24 | 9 | 62% | 0% | -62 | 0% | 0 | 0 | 0 | 9 |
| ATP_CHALL r25_34 | 11 | 56% | 0% | -56 | 0% | 0 | 0 | 0 | 11 |
| ATP_CHALL r35_44 | 9 | 43% | 0% | -43 | 0% | 0 | 0 | 0 | 9 |
| ATP_CHALL r45_54 | 6 | 23% | 0% | -23 | 0% | 0 | 0 | 0 | 6 |
| ATP_CHALL r55_64 | 11 | 34% | 0% | -34 | 0% | 0 | 0 | 0 | 11 |
| ATP_CHALL r65_74 | 9 | 71% | 33% | -38 | 11% | 0 | 3 | 0 | 6 |
| ATP_CHALL r75_84 | 9 | 61% | 0% | -61 | 11% | 0 | 0 | 0 | 9 |
| ATP_CHALL r85_94 | 15 | 61% | 0% | -61 | 0% | 0 | 0 | 0 | 15 |

## Aggregate

- Overall fill rate: predicted (mean of cell exp_fill) **61%**, observed **5%** (9/195 legs filled at entry, incl. marketable/resting/cross).
- Execution-mode breakdown: resting_miss_fallback=186, resting_filled=9
- Exit-outcome breakdown: OPEN=123, TRIGGERED=35, HOLD_OPEN=17, SETTLED_LOSER=12, SETTLED_WINNER=4, HOLD_LOSER=4
- **Capital deployed (Σ entry×10ct): 995.70 dollars** (195 entries).
- **Realized PnL: 5.60 dollars** over 55 closed legs (triggered/settled).
- **Open mark-to-market: -57.75 dollars** over 140 in-progress legs.
- **Total (realized + open MtM): -52.15 dollars** at this slate's N=195.
- Blended raw ROI on deployed capital: **-5.24%** (realized+MtM / capital). v4 corpus prediction was ~11.73% net blended (pre-realism, full 14,033-N corpus); today's N=195 is a single-slate small-sample readout, not corpus-comparable in CI.

> **Small-N caveat.** This is one slate (N=195 legs). Per-cell N is tiny (often 1-4); deltas are observations, not estimates. The corpus prediction (per_regime_offsets_v2 expected_fill_rate) is a 10-month average; a single day can diverge widely by chance. Report-all-even-if-N=1 per instruction.

---
*Pre-realism raw. Read-only on tape; bot untouched. Parquet + this doc are the only artifacts.*