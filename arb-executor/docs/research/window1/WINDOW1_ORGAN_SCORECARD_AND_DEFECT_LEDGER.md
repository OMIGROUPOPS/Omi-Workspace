# Window-1 organ scorecard and defect ledger

## Ruling

The frozen scoreboard remains **23 PC from 598 maker-reachable negative-pair opportunities** under the 10-second true-print-or-opposite-quote law. The 575-event gap is a placement gap, not evidence scarcity.

No organ gets the pen. The only retained fact is the unchanged JOIN control: it produces 23 PC, versus 1 for ATLAS/orientation and 3 for touch-minus-one/one-spread. This document changes no strategy or live code.

## Organ scorecard

| Organ | Comparable evidence | Verdict | Why it cannot sign |
|---|---:|---|---|
| ATLAS | 1,000 recognition rows; median error -4c; 5.7% reach | Actively wrong | Systematically too deep; JOIN gains 22 PC with no ATLAS-only PC. |
| Band B1-B8 | 913 calls; 28.1% actual flat; 238 pulses | Actively wrong except local WTA_CHALL B3 | Every native call is FLAT in a quote-recurrence market. |
| Cohort | 953; median -8c; 1.2% reach | Actively wrong | Deepest systematic miss. |
| AIM_V2 | 547; median -5c; 2.2% reach | Actively wrong | Sparse cells do not recover the floor. |
| Reach | 2,019; 28.57% predicted vs 3.2% actual | Actively overconfident | It magnifies the wrong depth voices. |
| Selector/contention | 1,244; TRADE 1.6% vs DROP 2.9% good | Actively inverted | Selected 29 good targets while 199 fitted tiers contained one. |
| Pair verdict | 582; 582 COMPOSED; 132 false positives | Noise | It synthesizes sibling as 100-current and never discriminates. |
| Flow | 1,020 recognition states | Noise/inverted | Quiet contains more large pulses than warm/open. |
| Orientation | 4/5 pair shapes correct; zero completion change | Provisionally predictive | Only five action payloads survive; mean gap worsens 5.5c to 5.75c. |
| Conviction | 123 rows from July 10 | Unscorable | Not the 804-event population. |
| Last trade / spread | 1,409; below-bid 5/5 directional but n=5 | Sparse weak signal | Only three games have strict joint two-leg evidence. |
| Pair shape | 597 strict two-leg floors; climb sibling falls 73.3% | Provisionally predictive | Strongest shape evidence, but no full pre-entry signed action surface. |

Signed error is target minus the reachable 10-second floor: negative means the order was too deep. `ORGAN_SCORECARD.json` freezes a category+price-region cube for every recognition instrument with a comparable row payload, plus the B1-B8 table. For reach, selector, pair verdict, flow, orientation, conviction, last-trade position, and pair shape, the file explicitly names why a complete comparable category+region cube is unavailable rather than manufacturing one.

## Frozen action comparison

| Action | Filled legs | Completed | PC | IC |
|---|---:|---:|---:|---:|
| ATLAS | 217 | 49 | 1 | 1 |
| ORIENTATION | 217 | 49 | 1 | 1 |
| JOIN | 601 | 86 | 23 | 11 |
| TOUCH_MINUS_1 | 274 | 57 | 3 | 2 |
| ONE_SPREAD_BELOW_MID | 270 | 58 | 3 | 2 |

ATLAS and orientation are outcome-identical. JOIN versus ATLAS has 22 JOIN-only PC, one shared PC, and zero ATLAS-only PC. Touch-minus-one and one-spread each have two PC that JOIN misses, but each loses 22 JOIN PC; they are not replacements.

## Shape, not scalar depth

The pair surface is not two independent depth numbers. The largest joint shape is climb+fall (296 games); among 382 games whose first revealed leg climbs, the sibling falls in 280 (73.3%). The combined-negative pair law and the 100-sum topology must remain explicit. No scalar organ may be applied before a lawful pre-entry cell exists.

Last-trade position relative to the spread is retained as a joint contextual predictor, not authority. Below-bid last trade points climb in all five directional rows, but the full bucket has only 16 observations and only three games have strict joint two-leg evidence.

## Defect ledger, ordered by measured cost

| Rank | Defect | Measured cost | Fix / disposition |
|---:|---|---|---|
| 1 | placement_gap_umbrella | maker_opportunities=598; frozen_JOIN_PC=23; missed=575 | Use the following causal layers; do not claim one organ explains all 575. **Retained: false.** |
| 2 | organ_disagreement_without_reliable_arbiter | disagreeing_legs=1013; disagreeing_events=509; events_examined=510; median_target_span_cents=4; p90_target_span_cents=21; negative_opportunity_events=425; disagreement_and_missed_opportunity_events=412 | Preserve JOIN until a pair-shape/recurrence candidate wins a full causal replay; record all voices without granting a pen. **Retained: false.** |
| 3 | ATLAS_deep_target_and_native_anchor_mismatch | versus_JOIN_PC_lost=22; versus_JOIN_completed_pairs_lost=37; versus_JOIN_filled_legs_lost=384; JOIN_PC_lost_to_ATLAS=0; page_changes=31; strict_page_changes=14; strict_role_changes=8 | Demote ATLAS to context and restore its native discovery anchor before any future retest. **Retained: JOIN_BASELINE_ONLY.** |
| 4 | filled_leg_disables_entry_review | filled_legs_with_later_lower_floor=245; events=240; cents_above_later_floor=565; median_cents=2; max_cents=25; NIK_post_fill_callbacks=5534; NIK_ask_at_or_below_fill=5387 | Continue diagnostic price review after fill, but never re-buy: exact-five means the later lower price is opportunity evidence, not entry authority. **Retained: false.** |
| 5 | staircase_quiet_hold_masks_recurrence | NIKVRB_VRB_callbacks=874; cadence_holds=6; quiet_FIFO_holds=868; ask_68_quote_state_visits=9; residence_seconds=641 | Test an episode-keyed recurrence response: recognition receipt cannot fill its action; only strictly later recurrence may credit. **Retained: false.** |
| 6 | band_print_cell_applied_to_quote_recurrence | calls=913; actual_non_flat=656; recurrent_ge_3c_pulses=238; flat_hit_pct=28.1 | Remove band signing authority; preserve B1-B8 only as descriptive print-conditioned context until quote-native validation exists. **Retained: false.** |
| 7 | selector_contention_inversion | selected_good=29; available_good=199; missed_available_good=170; TRADE_good_pct=1.6; DROP_good_pct=2.9 | Do not enable contention enforcement; retest only after native anchors and a causal target outcome are bound. **Retained: false.** |
| 8 | reach_probability_overconfidence | rows=2019; predicted_pct=28.57; observed_pct=3.2; brier=0.1824 | Prevent reach probability from signing price until recalibrated on the quote-or-print law. **Retained: false.** |
| 9 | cohort_and_AIM_V2_too_deep | cohort_rows=953; cohort_reach_pct=1.2; AIM_V2_rows=547; AIM_V2_reach_pct=2.2 | Demote both to context; do not average them into a scalar target. **Retained: false.** |
| 10 | pair_verdict_fabricates_sibling | rows=582; constant_COMPOSED=582; false_positive=132 | Require actual causal sibling book/print state and retain UNKNOWN when absent. **Retained: false.** |
| 11 | window_truth_and_arrival_use_different_reaim_paths | NIKVRB_first_sibling_reaim=65->73; move_reposts=9; window_truth_reaims=5 | Unify receipt-keyed arrival/reaim reason accounting, then replay; do not infer an 804-event cost from one specimen. **Retained: false.** |
| 12 | missing_pre_entry_opinion_payloads | orientation_actions=5; conviction_rows=123; conviction_date=2026-07-10; required_events=804 | Instrument opinions before action without changing actions; score only once the full population exists. **Retained: false.** |

## NIKVRB control

VRB made 874 pre-fill decisions while resting at 65: six cadence holds and 868 quiet-staircase FIFO holds. Its ask occupied 68 in nine quote states for 641 seconds. Those are affirmative non-decisions.

NIK is different. After the five-lot filled at 24, 5,534 BBO callbacks occurred, 5,387 with ask at or below 24. None entered the entry manager because the leg was active. The later 18-cent tape is diagnostic opportunity; exact-five forbids a fourth move or re-buy.

Under the frozen 10-second matrix, JOIN already makes NIKVRB a PC pair (NIK 24, VRB 69, combined delta -9). Therefore a NIKVRB-only recurrence repair cannot claim movement above 23. It must be tested across all 804 games.

## Five exact-start controls

Only NIKVRB under JOIN is PC. HURBIG, LAJVAN, BRAVED, and KORJIM remain incomplete across the five frozen actions. `EXACT_START_VALIDATION.json` preserves every leg result and reachable-floor gap.

## Keep / discard gate

No proposed mechanism is retained. JOIN remains the comparator, not a new strategy. A future recurrence-aware pair-first candidate must:

1. use causal BBO/print receipts and strictly later fill evidence;
2. preserve exact-five and never reinterpret post-fill review as re-buy/DCA;
3. preserve the NIKVRB JOIN PC and all five exact-start memberships;
4. exceed 23 PC on the same 598-opportunity, 804-event, 10-second law;
5. identify a complete pre-entry cell before an organ may sign.

Until then, no one-authority chokepoint is armed.

## Containment

This build reads committed development artifacts only. It does not execute `live_v4.py`, invoke a scorer, access holdout/live/network data, or modify any order, position, exit, settlement, or Window-2 state.
