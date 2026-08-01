# Window 1 entry-honesty dependency report

Score-free. Ask-side only. No five-game rerun and no 804 policy replay were run because the decision-time expected-close authority is not bound.

## 1. Honest fill truth

Source: https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/refs/heads/codex/window1-live-consolidated/.claude/window1_live_v4_replay/honest_fill_model_20260801/FOUR_FILL_CLASSIFICATION.json

The four replay credits classify as 0 PROVEN_MAKER, 3 PROVEN_TAKER, and 1 UNPROVEN. NIKVRB is the only honest-model completion (1/2), and it is a two-taker pair. HUR is UNPROVEN because its exact submission-time own book is absent.

## 2. Aggressor split and ceilings

Flow source: https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/refs/heads/codex/window1-live-consolidated/.claude/window1_live_v4_replay/aggressor_ceiling_census_20260801/AGGRESSOR_SPLIT.json

Ceiling source: https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/refs/heads/codex/window1-live-consolidated/.claude/window1_live_v4_replay/aggressor_ceiling_census_20260801/CEILING_CENSUS.json

The 126917 lawful prints partition into 113892 buyer-aggressed, 13025 seller-aggressed, and 0 unknown. At the frozen 516 target prices, 318 events have both legs maker-reachable and 253 have a combined-negative maker floor; the take ceiling remains 516. All category, price-region, spread, and both-clock cells are in the linked raw files.

## 3. Fee-aware take rule

Source: https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/refs/heads/codex/window1-live-consolidated/.claude/window1_live_v4_replay/fee_aware_take_census_20260801/FEE_AWARE_TAKE_CENSUS.json

Using actual W1 closes only as an ex-post oracle, 5/516 clear the operator-specified fee comparison. The executable count is NOT_BOUND because expected close at decision time has no bound source. NIKVRB is 16 cents of ex-post pair edge versus 14 cents of five-lot taker fees; the HURBIG floor oracle fails, and HUR itself is unproven in the replay.

## 4. First-leg commitment

Gap source: https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/refs/heads/codex/window1-live-consolidated/.claude/window1_live_v4_replay/first_leg_commitment_diagnostic_20260801/COMMITMENT_GAP_CENSUS.json

Conditional source: https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/refs/heads/codex/window1-live-consolidated/.claude/window1_live_v4_replay/first_leg_commitment_diagnostic_20260801/SIBLING_FLOOR_CONDITIONAL_CENSUS.json

Both floors exist for 786/804 events. 762 are strictly asynchronous and 24 tie. A strictly later sibling floor exists in all 762 asynchronous cases, but 319 finish at combined cost >=100; only 443 are below 100. No causal commitment threshold is validated.

## 5. Pair wiring

Source: https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/refs/heads/codex/window1-live-consolidated/.claude/window1_live_v4_replay/pair_wiring_correction_20260801/PAIR_WIRING_CORRECTION_RECEIPT.json

Four candidate rows can use the single surviving inverse tuple when each side has its own micro receipt. LAJ/VAN lacked ATP_MAIN_26_50_FLAT_UNMOVED|ATP_MAIN_26_50_FLAT_UNMOVED; V3 adds it as STRUCTURAL_INVERSE_CLOSURE with empirical n=0. This is not a validation fill.

## 6. Gate

Source: https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/refs/heads/codex/window1-live-consolidated/.claude/window1_live_v4_replay/entry_honesty_dependency_20260801/DECISION_GATE_RECEIPT.json

The five-game gate did not run: item 3 cannot make a causal take decision without an expected-close authority. Consequently the 804 policy run was not run. That is the blocking dependency, not an adverse replay result.
