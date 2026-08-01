# Window-1 dynamic-renarrow V7 - 804 development diagnostic

All event and leg rows: https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/refs/heads/codex/window1-live-consolidated/.claude/window1_live_v4_replay/dynamic_renarrow_population_v7_20260801/EVENT_LEDGER.jsonl.gz

All category / price-region partitions and every reported number: https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/refs/heads/codex/window1-live-consolidated/.claude/window1_live_v4_replay/dynamic_renarrow_population_v7_20260801/POPULATION_SUMMARY.json

Conservation: https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/refs/heads/codex/window1-live-consolidated/.claude/window1_live_v4_replay/dynamic_renarrow_population_v7_20260801/CONSERVATION_RECEIPT.json

Five-game gate split and the 7/3 versus 8/2 reconciliation: https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/refs/heads/codex/window1-live-consolidated/.claude/window1_live_v4_replay/dynamic_renarrow_population_v7_20260801/FIVE_GAME_EXECUTION_GATE_SPLIT_RECEIPT.json

The execution gate is entry at or below the leg's own capacity-proven ask-reachable low. Floor-versus-close is a separate market-ceiling classification. Pair-reference is NOT_BOUND. This run is ask-side only, requires 10 seconds dwell and exact displayed capacity of at least 5.

This is an in-sample development diagnostic. The target event was removed from causal nearest-member selection, but the aggregate library envelopes were fitted on the development population except the frozen five; no holdout claim is made.
