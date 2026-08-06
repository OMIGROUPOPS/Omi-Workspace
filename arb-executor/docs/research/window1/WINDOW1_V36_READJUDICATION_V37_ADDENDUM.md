# Window-1 V36 re-adjudication and V37 floor-arithmetic take-bound ruling

Date: 2026-08-06

## Standing ruling

V36 at `bfde0d8d1135f5c5f48a5f3d619ab30050efab83` is OPERATIVE.
Its earlier rejection used the schedule-contaminated V34 deep-frontier bar
`23/34/68`. The independently frozen hygiene census at
`03bac97b12777d751fbb334fa6ae0f605445498a` shows that V34's 34 `<=95`
deep pairs contain only 9 exact-bell rows and that 25/34 (73.5%) use estimated
right edges. Under the exact-bell, terminal-collapse-clean ruler, the lawful
comparison is V34/V35/V36 = `9/5/7`. V36 also has 270 strict completions versus
V35's 264 and preserves ARNROM at 38+56=94. V36 therefore dominates V35 on
the clean instruments and is the operative floor.

Hygiene census:

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/03bac97b12777d751fbb334fa6ae0f605445498a/.claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/DEEP_PAIR_HYGIENE_CENSUS.json

Frozen re-adjudication receipt:

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/ceaed0b21e5269660731320f256960fdcf4b8565/.claude/window1_live_v4_replay/v37_floor_arithmetic_take_bound_20260806/V36_READJUDICATION_RECEIPT.json

## V37 result

V37 adds one parameter-free decision-time check to a V36 TAKE. Where the
other expression has a causally observed running true-print low, the take is
lawful only when `100 - entry > other_running_print_backed_floor`. Equality is
forbidden. If no sibling print floor is yet bound, V37 has no authority and
the V36 decision remains unchanged.

V37 is REJECTED. It produces 242 strict completed/under-par pairs and 5
exact-bell, terminal-collapse-clean `<=95` pairs. Both are below the operative
V36 floors of 270 and 7. V36 remains operative.

Full report:

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/ceaed0b21e5269660731320f256960fdcf4b8565/.claude/window1_live_v4_replay/v37_floor_arithmetic_take_bound_20260806/REPORT.md

Acceptance receipt:

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/ceaed0b21e5269660731320f256960fdcf4b8565/.claude/window1_live_v4_replay/v37_floor_arithmetic_take_bound_20260806/ACCEPTANCE_RECEIPT.json

Two-column scorecard:

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/ceaed0b21e5269660731320f256960fdcf4b8565/.claude/window1_live_v4_replay/v37_floor_arithmetic_take_bound_20260806/SCORECARD_TWO_COLUMN.json

Floor-arithmetic receipt:

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/ceaed0b21e5269660731320f256960fdcf4b8565/.claude/window1_live_v4_replay/v37_floor_arithmetic_take_bound_20260806/FLOOR_ARITHMETIC_TAKE_BOUND_RECEIPT.json

## Causal tripwire contradiction

The requested named tripwires conflict with the decision-time law and were
not forced to pass:

- At ARN 56, ROM's observed print floor was first 49 and then 45. The
  arithmetic was `44 > 49` and then `44 > 45`, both false. ROM 38 arrived
  40,304 seconds after the first ARN decision; using it at ARN 56 would leak
  future evidence. ARN 56 is therefore lawfully forbidden and ARNROM does not
  complete under V37.
- At JAN 79, GAN had no observed running print floor. V37 therefore had no
  authority and left V36 unchanged. GAN's eventual 18 cannot retrospectively
  authorize JAN 79. GANJAN remains 99.
- The V37 implementation was not retuned after these observations. Its
  rejection is the result.

Causal contradiction receipt:

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/ceaed0b21e5269660731320f256960fdcf4b8565/.claude/window1_live_v4_replay/v37_floor_arithmetic_take_bound_20260806/CAUSAL_TRIPWIRE_CONTRADICTION_RECEIPT.json

## Validation and safety

- Two clean builds were byte-identical across 53 compared artifacts.
- D=804 and 1,608 legs conserve in both output columns.
- Six intended inherited/focused tests passed: V35 policy/package, V36
  policy/package, and V37 policy/package.
- Post-edge machine rows: 0.
- Holdout, live, network-runtime, order, position, exit, settlement, DCA, and
  deployment accesses: 0.
- No deployment or live mutation occurred.

Determinism receipt:

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/ceaed0b21e5269660731320f256960fdcf4b8565/.claude/window1_live_v4_replay/v37_floor_arithmetic_take_bound_20260806/DETERMINISM_RECEIPT.json

Forbidden-access receipt:

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/ceaed0b21e5269660731320f256960fdcf4b8565/.claude/window1_live_v4_replay/v37_floor_arithmetic_take_bound_20260806/FORBIDDEN_ACCESS_RECEIPT.json
