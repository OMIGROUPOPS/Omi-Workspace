# Window-1 quote-shape elimination — two cold games only

This is a score-free, leave-two-games-out replay. The quote library contains no NIKVRB or HURBIG training row. The replay consumes no close, bell, reachable-low, or outcome field until after decisions and fills are frozen.

Raw replay and decision receipts:

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/codex/window1-live-consolidated/.claude/window1_live_v4_replay/quote_shape_elimination_20260731/TWO_GAME_REPLAY.json

Raw quote-shape library:

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/codex/window1-live-consolidated/.claude/window1_live_v4_replay/quote_shape_elimination_20260731/QUOTE_SHAPE_LIBRARY.json

## Result table

All deltas are `entry - reference`; negative is cheaper. Pair reference is independently unbound and remains `NOT_BOUND`.

| Category | Price region | Event | Leg | State | Placement T−scheduled / T−bell | Entry | Pair ref / Δ | Own W1 close / Δ | Own bell / Δ | Ask-reachable low / Δ | Surviving shapes at placement |
|---|---:|---|---|---|---:|---:|---|---|---|---|---|
| ATP_CHALL | 51–75 | NIKVRB | VRB | CREDITED | 314.100m / 319.100m | 68 | NOT_BOUND / NOT_BOUND | 83 / −15 | 83 / −15 | 68 / +0 | `UP_CONTINUATION → FLOOR` |
| ATP_CHALL | 26–50 | NIKVRB | NIK | CREDITED | 38.033m / 43.033m | 18 | NOT_BOUND / NOT_BOUND | 19 / −1 | 19 / −1 | 18 / +0 | `DOWN_REBOUND → FLOOR` |
| ATP_CHALL | 26–50 | HURBIG | HUR | CREDITED | 98.567m / 188.567m | 38 | NOT_BOUND / NOT_BOUND | 42 / −4 | 42 / −4 | 37 / +1 | `DOWN_CONTINUATION → FLOOR` |
| ATP_CHALL | 51–75 | HURBIG | BIG | INSUFFICIENT_EVIDENCE | — | — | NOT_BOUND / NOT_BOUND | 60 / — | 60 / — | 55 / — | no placement; terminal survivor `UP_CONTINUATION`; own micro position never supplied lawful placement authority |

Every number in this table is in the raw replay URL above.

## What was built

At the first formed book, all six quote-path topologies in that category and price region are live. Micro eliminates shapes by the exact training-fitted minimum on ask net/dip. Micro-micro may only break the remaining tie with dwell, spread, cadence, displayed top-ask size, and top-five depth. The first direction independently resolved on one book removes non-inverse sibling directions. Either book's tick advances the shared clock and re-evaluates both books.

`PLACE` requires all surviving pair-constrained shapes to say `FLOOR`, a later-timestamp transition on the leg's own ask, an independently observed inverse sibling direction, current ask equal to that leg's observed ask low, ten seconds of continuous ask dwell, and at least five displayed contracts. `HOLD` requires every survivor to say `LOWER`. Every other state is `INSUFFICIENT_EVIDENCE`.

Specification and constant provenance:

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/codex/window1-live-consolidated/arb-executor/docs/research/window1/WINDOW1_QUOTE_SHAPE_ELIMINATION_TWO_GAME_SPEC_V1.json

The ten-second dwell is inherited—not fitted here—from:

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/codex/window1-live-consolidated/arb-executor/docs/research/window1/WINDOW1_ORGAN_SCORECARD_AND_DEFECT_LEDGER.md

## Defect receipt

- Before: the live-book initial-aim branch filled HUR at 47 while its ask later reached 37.
- After: the first HUR book is `INSUFFICIENT_EVIDENCE`; the quote survivor remains `DOWN_CONTINUATION` until the pair-constrained micro and micro-micro layers agree at 38.
- Movement: HUR entry 47 → 38, nine cents cheaper; gap to the ask-reachable low 10 → 1 cent.

The before values are frozen here:

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/codex/window1-live-consolidated/.claude/window1_live_v4_replay/live_book_initial_aim_20260731/REPLAY_AND_REFERENCE_PANEL.json

## Validation fence

This stack is unvalidated beyond two cold games. It preserves the previously reached NIK 18 and VRB 68; it newly changes HUR from 47 to 38 and leaves BIG explicitly insufficient. It has not been run over 804 events, scored, ranked, tuned on either held-out game, or given live authority.

## Charts

NIKVRB raw SVG:

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/codex/window1-live-consolidated/.claude/window1_live_v4_replay/quote_shape_elimination_20260731/NIKVRB_QUOTE_SHAPE_REPLAY.svg

HURBIG raw SVG:

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/codex/window1-live-consolidated/.claude/window1_live_v4_replay/quote_shape_elimination_20260731/HURBIG_QUOTE_SHAPE_REPLAY.svg
