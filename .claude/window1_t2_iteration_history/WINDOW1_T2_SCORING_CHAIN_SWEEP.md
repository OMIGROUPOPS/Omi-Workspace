# Window-1 T2 scoring-chain unit and horizon sweep

**This is a separate post-grid diagnostic. It is not a package or audit.**

## What moved

- First fee-unit correction already made: recognized strict under-par **41 -> 90**.
- Additional fee-unit correction found by this sweep: recognized **90 -> 91**; all 804 **207 -> 208**.
- Inclusive frozen-right endpoint: recognized **91 -> 92**; all 804 **208 -> 209**.
- Close-reference horizon correction changes **285** leg references across **163** events.
- Among the 131 completed games, **45** leg deltas across **28** events change; **23** combined deltas change.
- Recognition target scope **501 -> 500** because KXATPCHALLENGERMATCH-26JUL20CREMAT is read after its frozen right.
- Frozen five-contract floor prices move **0**. Their ladder already used the correct right edge.

## Completed-game metric movement

| metric | ledger reference | corrected right-bound reference | lost | gained |
|---|---:|---:|---:|---:|
| prefee_PC | 115 | 113 | 3 | 1 |
| prefee_IC | 37 | 37 | 3 | 3 |
| maker_PC | 103 | 104 | 3 | 4 |
| maker_IC | 37 | 37 | 3 | 3 |

## Upstream horizon contamination

- Asynchronous sibling episodes: **3195/6501** are after frozen right, across **18** events.
- Decision attribution: **26/47** rows choose an earliest opportunity after frozen right, across **13** events.
- T2 sibling target surfaces: **3415924/4576794** surface rows and **2099955/2996560** lawful target entries are after frozen right.
- Final credited fills across all candidates: **0/3252** are after frozen right.

## Every source occurrence

| kind | status | source | finding |
|---|---|---|---|
| fee_unit | fixed_active | `arb-executor/analysis/window1_t2_target_laps.py`; strict_sequential_floor pair total | A five-contract fee total had been added to a per-contract pair price. The comparison is now total-to-total. |
| fee_unit | fixed_active | `arb-executor/analysis/window1_t2_target_laps.py`; cheapest_fill_after ranking | The target price was per contract while maker_fee_cents was for the five-contract order. Ranking now uses target*5+fee. |
| fee_unit | correct | `arb-executor/analysis/window1_t2_maker_fee_reconciliation.py`; control and tape maker-fee reconciliation | All comparisons either divide total fee by five before joining per-contract prices or multiply price/delta by five before joining order-total fees. |
| fee_unit | correct_unit_wrong_schedule_superseded | `arb-executor/analysis/window1_t2_control_reconciliation.py`; control fee reconciliation | The unit conversion is correct; the formula is taker, not maker, and the maker reconciliation supersedes it. |
| fee_unit | latent_zero_only | `arb-executor/analysis/window1_range_attack_scorer_v1.py`; combined_delta = sum(deltas) + FEE_CENTS | This expression is per contract. Frozen FEE_CENTS is 0, so no number moves. A future order-total fee would be invalid. |
| fee_unit | latent_zero_only | `arb-executor/analysis/window1_t2_scoring_adapter_v1.py; window1_range_attack_instrument.py; window1_range_attack_instrument_v2.py; window1_t2_causal_divot_instrument.py`; b2_max and d1+d2+fee headroom | d1 and d2 are per-contract cents. Fee is frozen integer 0. No current number moves, but the contract lacks an explicit per-contract unit. |
| fee_unit | unused_constant | `arb-executor/analysis/window1_t2_frontier_regret_scorer_v1.py`; FEE_CENTS = 0 | The constant is declared but not used by this module. |
| horizon | correct | `arb-executor/analysis/window1_range_attack_prerun_builder.py`; range ladder and interval evaluation | Uses inclusive min(policy_decision_horizon, guarded_cutoff); the five-contract floors and fillability rows are correct. |
| horizon | correct | `arb-executor/analysis/window1_range_attack_guarded_fill_adapter_v1.py and v2`; credited fill validation | Enforces evaluated_right_ts as well as guarded cutoff. No credited fill in the control ledger is after frozen right. |
| horizon | active_defect | `arb-executor/analysis/window1_range_attack_reference_adapter_v1.py and v2`; Window-1 close reference | Reads through guarded cutoff without min with scheduled policy horizon. This propagates through Range-Attack runners, T2 runners V1-V5, and window1_t2_reference_boundary_v3. |
| horizon | active_defect | `arb-executor/analysis/window1_asynchronous_opportunity_policy_census_v2.py`; raw sibling episode preparation and qualification | Uses boundary guarded_cutoff_ts as right instead of the shorter frozen range right. |
| horizon | downstream_contamination | `arb-executor/analysis/window1_decision_layer_attribution.py`; fixed witness resolution | Consumes the contaminated V2 episode ledger and independently reads raw books/prints through guarded cutoff. |
| horizon | downstream_contamination | `arb-executor/analysis/window1_t2_causal_divot_prerun.py and window1_t2_causal_divot_instrument.py`; T2 sibling opportunity and target surfaces | Consumes decision-layer attribution and emits trigger/target surfaces after frozen right; exact census is in this report. |
| horizon | secondary_validation_gap_no_observed_late_credit | `arb-executor/analysis/window1_t2_scoring_package_builder_v1.py`; _derive_unique_fills | Rechecks guarded cutoff but not evaluated_right_ts. Upstream fill facts were already bounded, and the control census finds zero credited fills after frozen right. |
| horizon | active_defect | `arb-executor/analysis/window1_t2_recognition_laps.py`; recognition event cutoff | Passes control guarded_cutoff_ts instead of frozen range right; one target-lap event is recognized after its horizon. |
| horizon | fixed_active | `arb-executor/analysis/window1_t2_target_laps.py`; raw V5 oracle reader | Now uses frozen range_right_ts and treats the frozen right endpoint as inclusive, matching the ladder builder. |

No additional nonzero fee-unit error was found in completed delta or in the five-contract floor. The delta does move because the reference reader crossed the frozen horizon; the floor does not.

Holdout stayed sealed. Live and network access stayed off.
