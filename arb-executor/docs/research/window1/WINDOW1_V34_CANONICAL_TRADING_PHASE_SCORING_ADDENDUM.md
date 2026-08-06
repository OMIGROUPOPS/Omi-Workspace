# V34 canonical trading-phase scoring binding

The V34 dual-side residency state machine is unchanged. Joint, frontier, and
regret scoring now consumes only the per-leg `true_close` values from
`THE_603_MAP.json` at commit
`4f35ddea00a877c9b1129702a523abe2d689adb8`, whose exact bytes are bound as
SHA-256 `9188a771a9a8c6ec671485f8d4c1c61ffd60372b0df742cf4ab66ad1afa98c58`.
All action, fill, floor, frontier, and regret evidence is clipped to that same
trading phase. Settlement-basis closes are never consumed.

The canonical map contains 804 events, 1,606 non-null leg closes, two explicit
null closes, and a T1-joint comparison universe of 750. Every non-null close
was matched to its ordered exchange-print identity with zero map mismatches;
the null closes remain unavailable and inherit only the sibling event boundary
for stream clipping.

On this ruler, STRICT-LAW completes 441 pairs and grades 63 JOINT.
CENSUS-PRICED completes 481 pairs and grades 89 JOINT. Every aggregate and
category-by-starting-price-region scorecard prints the comparison universe of
750. The earlier settlement-basis package at `e0fb6a31` is preserved unchanged
as a negative control and is superseded for V34 scoring.

Two clean builds reproduced all 25 regenerable core artifacts byte-for-byte.
The artifact manifest covers 26 files with zero hash mismatches. Focused state
machine and canonical-package tests pass. Holdout, live, network-runtime,
order, position, and settlement-basis scoring accesses are zero.

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/b430bcfff51f89c9466e77b798d4ac5d9fff15ea/.claude/window1_live_v4_replay/v34_dual_side_residency_machine_trading_phase_20260805/SCORECARD_TWO_COLUMN.json

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/b430bcfff51f89c9466e77b798d4ac5d9fff15ea/.claude/window1_live_v4_replay/v34_dual_side_residency_machine_trading_phase_20260805/CANONICAL_CLOSE_BINDING.json

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/b430bcfff51f89c9466e77b798d4ac5d9fff15ea/.claude/window1_live_v4_replay/v34_dual_side_residency_machine_trading_phase_20260805/SETTLEMENT_EVIDENCE_EXCLUSION_RECEIPT.json

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/b430bcfff51f89c9466e77b798d4ac5d9fff15ea/.claude/window1_live_v4_replay/v34_dual_side_residency_machine_trading_phase_20260805/DETERMINISM_RECEIPT.json

