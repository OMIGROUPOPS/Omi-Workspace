# Window-1 V36 state-directional rest + mature-floor take — rejected

Evidence package: `bfde0d8d1135f5c5f48a5f3d619ab30050efab83`

V36 is an undeployed replay variant derived from V35
`0799fba887f1d1e84f9c0ef3e73096fd9d76019e`. On FALLING, an active rest
obeys the V32 no-chase law: `min(prior rest, best bid - 1c, pair cap)`. On
RISING or SETTLED it preserves V35's continuous bid-minus-one tracking. A
take requires a qualifying ask and a mature evidence floor: no causal new-low
receipt inside the inherited 300-second state horizon, evaluated only on a
later book receipt. A non-falling qualifying shelf may replace an older
minimum only if it was causally re-formed and later matured. There is no timer
or wall-clock action trigger.

V36 is **rejected**. STRICT completed/under-par pairs are `270`, clearing the
`>=264` completion bar, but the `<=93 / <=95 / <=97` frontier is
`9 / 20 / 77`, failing the required `23 / 34 / 68` deep-frontier bar. V35
remains operative. CENSUS_PRICED completed/under-par pairs are `548`.

The named checks are mixed. ARNROM passes at `38 + 56 = 94`; KRALOR|LOR
remains `5`; BOSCOP|BOS remains `32`; ARNROM|ROM remains `38` at zero regret.
GANJAN remains `20 + 79 = 99`, and FETPIE and JONSPI remain incomplete.
Therefore local successes do not override the population rejection.

The adverse-tail claim is also not established. Under the V36 state-at-rest
receipt, STRICT has 24 FALLING-source maker fills; all 24 finish above their
eventual true-print low, with median `7c`, p90 `34c`, max `55c`, and total
`323c`. This receipt uses entry minus eventual true-print low in the same hard
pre-bell window. It is not silently equated to the autopsy's seller-hit-only
measure.

STRICT differential versus V35: 1,353 leg streams are identical; 58 are newly
credited, 40 lose a V35 credit, 51 fill deeper, 33 fill shallower, and 73
change otherwise. Exact state-law rest tracking holds on all 2,018,523 STRICT
and 1,611,503 CENSUS tracked book receipts with zero target gap. Two clean
builds reproduced 45 regenerable files byte-identically. Six focused and
inherited tests passed. Hard-edge violations and close-based grading reads are
zero. Holdout, live, network-runtime, order, position, exit, settlement, DCA,
and deployment accesses are zero.

Report:
https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/bfde0d8d1135f5c5f48a5f3d619ab30050efab83/.claude/window1_live_v4_replay/v36_state_directional_rest_mature_floor_20260806/REPORT.md

Acceptance:
https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/bfde0d8d1135f5c5f48a5f3d619ab30050efab83/.claude/window1_live_v4_replay/v36_state_directional_rest_mature_floor_20260806/ACCEPTANCE_RECEIPT.json

Two-column scorecard:
https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/bfde0d8d1135f5c5f48a5f3d619ab30050efab83/.claude/window1_live_v4_replay/v36_state_directional_rest_mature_floor_20260806/SCORECARD_TWO_COLUMN.json

Strict frontier:
https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/bfde0d8d1135f5c5f48a5f3d619ab30050efab83/.claude/window1_live_v4_replay/v36_state_directional_rest_mature_floor_20260806/STRICT_FRONTIER.json

Strict regret:
https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/bfde0d8d1135f5c5f48a5f3d619ab30050efab83/.claude/window1_live_v4_replay/v36_state_directional_rest_mature_floor_20260806/STRICT_REGRET_GAUGE.json

Named regressions:
https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/bfde0d8d1135f5c5f48a5f3d619ab30050efab83/.claude/window1_live_v4_replay/v36_state_directional_rest_mature_floor_20260806/NAMED_REGRESSION_RECEIPT.json

Adverse tail by fill state:
https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/bfde0d8d1135f5c5f48a5f3d619ab30050efab83/.claude/window1_live_v4_replay/v36_state_directional_rest_mature_floor_20260806/ADVERSE_TAIL_BY_FILL_STATE.json

Rest sanity:
https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/bfde0d8d1135f5c5f48a5f3d619ab30050efab83/.claude/window1_live_v4_replay/v36_state_directional_rest_mature_floor_20260806/REST_SANITY.json

Bleed delta:
https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/bfde0d8d1135f5c5f48a5f3d619ab30050efab83/.claude/window1_live_v4_replay/v36_state_directional_rest_mature_floor_20260806/BLEED_CENSUS_DELTA.json

Differential versus V35:
https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/bfde0d8d1135f5c5f48a5f3d619ab30050efab83/.claude/window1_live_v4_replay/v36_state_directional_rest_mature_floor_20260806/DIFFERENTIAL_VS_V35.json

Differential versus V34-W1:
https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/bfde0d8d1135f5c5f48a5f3d619ab30050efab83/.claude/window1_live_v4_replay/v36_state_directional_rest_mature_floor_20260806/DIFFERENTIAL_VS_V34_W1.json

Determinism:
https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/bfde0d8d1135f5c5f48a5f3d619ab30050efab83/.claude/window1_live_v4_replay/v36_state_directional_rest_mature_floor_20260806/DETERMINISM_RECEIPT.json

Forbidden access:
https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/bfde0d8d1135f5c5f48a5f3d619ab30050efab83/.claude/window1_live_v4_replay/v36_state_directional_rest_mature_floor_20260806/FORBIDDEN_ACCESS_RECEIPT.json

Source manifest:
https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/bfde0d8d1135f5c5f48a5f3d619ab30050efab83/.claude/window1_live_v4_replay/v36_state_directional_rest_mature_floor_20260806/SOURCE_HASH_MANIFEST.json

Artifact manifest:
https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/bfde0d8d1135f5c5f48a5f3d619ab30050efab83/.claude/window1_live_v4_replay/v36_state_directional_rest_mature_floor_20260806/ARTIFACT_HASH_MANIFEST.json

Policy source:
https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/bfde0d8d1135f5c5f48a5f3d619ab30050efab83/arb-executor/analysis/window1_v36_state_directional_rest_mature_floor.js

Builder source:
https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/bfde0d8d1135f5c5f48a5f3d619ab30050efab83/arb-executor/analysis/build_window1_v36_state_directional_rest_mature_floor.js
