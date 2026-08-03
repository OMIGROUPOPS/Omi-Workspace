# V11 holdout gate-lag diagnostic

The 83 legs produced 57,912 repeated above-low decisions. Their minimum return gap was 1 cent for 55 legs, at most 2 cents for 66, and at most 3 cents for 73. Category/price-region partitions and the full distribution: https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/refs/heads/codex/window1-live-consolidated/.claude/window1_live_v4_replay/holdout_gate_lag_diagnostic_20260803/ABOVE_OBSERVED_LOW_83_CENSUS.json

At a 1-cent tolerance, 52 legs become actionable, completed pairs move from 41 to 70, and under-par pairs move from 18 to 23. At 2 cents the corresponding values are 63, 79, and 22; at 3 cents they are 72, 87, and 23. The results are not monotone because a wider tolerance acts earlier at a potentially higher ask. Exact event rows: https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/refs/heads/codex/window1-live-consolidated/.claude/window1_live_v4_replay/holdout_gate_lag_diagnostic_20260803/ABOVE_LOW_PAIR_COUNTERFACTUAL_EVENT_LEDGER.jsonl

Every one of the 83 above-observed-low legs and every repeated decision evaluation: https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/refs/heads/codex/window1-live-consolidated/.claude/window1_live_v4_replay/holdout_gate_lag_diagnostic_20260803/ABOVE_OBSERVED_LOW_83_DECISION_EVALUATIONS.jsonl

Per-leg low arrival, eventual floor, close, gap distribution, and one/two/three-cent candidate: https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/refs/heads/codex/window1-live-consolidated/.claude/window1_live_v4_replay/holdout_gate_lag_diagnostic_20260803/ABOVE_OBSERVED_LOW_83_LEG_SUMMARY.jsonl

For the 61 terminal unanimous-lower legs, the first qualified refusal split is 26 bottomed, 23 went lower, and 12 without a qualified refusal receipt. At the last qualified refusal it is 48, 1, and 12. Every leg: https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/refs/heads/codex/window1-live-consolidated/.claude/window1_live_v4_replay/holdout_gate_lag_diagnostic_20260803/UNANIMOUS_LOWER_61_LEG_SUMMARY.jsonl

Bottomed-versus-went-lower conservation by category and price region: https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/refs/heads/codex/window1-live-consolidated/.claude/window1_live_v4_replay/holdout_gate_lag_diagnostic_20260803/UNANIMOUS_LOWER_61_CENSUS.json

The pair counterfactual uses the first fresh exact-five, ten-second ask receipt at one/two/three cents above the missed observed low. It credits that action as PROVEN_TAKER and reports both entry-sum-minus-100 and entry-minus-own-closes; it is diagnostic, not a policy change.
