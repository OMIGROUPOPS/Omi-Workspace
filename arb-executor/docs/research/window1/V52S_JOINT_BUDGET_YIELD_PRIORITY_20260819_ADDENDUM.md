# V52s joint-budget invariant with yield-priority depth — 2026-08-19

## Status

V52s is a deterministic full-development observation over the adopted V52l lineage at `96597c98910f7ef45b62e2bc7dfab5ed9ee5f5a7`. It is **rejected / not adopted**. The closed-loop arithmetic invariant is correct, but the executable mechanism fails the controlling L17 value bar and does not preserve the 68 simulation-identified knife-edge games.

The replay used `W1_GROUND_TRUTH_TABLE` from `c0056976c446afcb4d9603796a2e06c068ee94d6` as its sole grader. Population `D=804`; 784 games are gradeable and 20 `UNKNOWN_BELL` games remain a separate non-gradeable class. No sealed population, live system, deployment, network, order, position, exit, settlement, or DCA path was accessed.

## Frozen mechanism and provenance

The mechanism is licensed by `LAW_INDEX.md` at `ae731326` and consumes L14, L17, and L18. The rejected open-loop simulation is bound to `SLACK_CONDITIONAL_SHIFT.json` at `f30ea3ebeca4eec15790bb013a9c8e9f5a4fb852`; its exact 68-game knife-edge set is frozen in the package.

At every receipt, bought and standing lane targets must sum to at most 99 cents. Incumbent targets are senior. A standing side may use available slack to stand one market tick inside its running post-onset session low. A senior target rise forces the junior lift to yield on that receipt before market interaction. The one-cent tick is the tape's integer unit, not a fitted constant. The V52l policy closure contains 21 files and is byte-identical to the parent.

## Executable result

| Instrument | V52l | V52s | Delta |
|---|---:|---:|---:|
| valid-fill completed / under-par pairs | 311 | 310 | -1 |
| banked cents | 714 | 581 | -133 |
| frontier `<=93 / <=95 / <=97 / <100 / any` | `17 / 31 / 83 / 311 / 311` | `6 / 25 / 55 / 310 / 310` | `-11 / -6 / -28 / -1 / -1` |
| resolved exposures | 387 | 383 | -4 |
| unresolved exposures | 350 | 367 | +17 |

The strict print-cross build-verification ruler records 235 completed/under-par pairs and 385 banked cents, with frontier `3 / 11 / 28 / 235 / 235`.

The continuous invariant was evaluated in 53,316,659 receipt phases: 255,087 depth lifts, 249,642 yield events, maximum joint target 99 cents, zero invariant violations, zero `COMPLETE_AT_LOSS`, and both clocks on every lift/yield receipt. `REFLEX_POST=0`.

Only 51 of the 68 simulation knife edges remain complete. The 17 losses are frozen by canonical event identity in `V52S_KNIFE_EDGE_68_PRESERVATION.json`. Consequently, the completion floor passes (`310 >= 305`), while the controlling value bar fails (`581` is not greater than `714`) and the preservation claim fails. V52s does not supersede V52l.

## Mechanical repair and verification

The first completed replay stopped before score emission because the simulation stores short `26JUL...` codes while the replay ledger stores canonical Kalshi event IDs. The receipt adapter now performs a unique suffix join while retaining both source identities; all 68 joins prevalidate one-to-one. This is receipt-only and changes no decision, target, fill, or grade.

Two subsequent clean builds produced 846 byte-identical pre-determinism artifacts with zero mismatches. The final package contains 848 files, including 802 full decision-trace chunks and 8,032,326 decision rows. A publication-size check found the 504,729-row depth action ledger serialized as a 415,846,030-byte monolithic JSON file. A mechanical, score-inert repair externalized those rows to deterministic streaming gzip (4,175,830 bytes) and retained a compact JSON summary. The two repaired packages remain byte-identical; the scorecard, bar, preservation, invariant, exposure, and per-game outcome hashes are unchanged. The focused mechanism unit test and JavaScript syntax checks pass. Git diff and whitespace checks pass.

The controlling package is `.claude/window1_live_v4_replay/v52s_joint_budget_yield_priority_804_20260819/`. `REPORT.md`, `TWO_RULER_SCORECARD.json`, `V52S_MECHANISM_BAR.json`, `V52S_KNIFE_EDGE_68_PRESERVATION.json`, `V52S_JOINT_BUDGET_INVARIANT_RECEIPT.json`, `V52S_DEPTH_LIFT_AND_YIELD_LEDGER.jsonl.gz`, `V52S_SERIALIZATION_RECEIPT.json`, `V52S_EXPOSURE_DELTA.json`, `PER_GAME_OUTCOME_TABLE.jsonl.gz`, `TRACE_CHUNK_MANIFEST.json`, `DETERMINISM_RECEIPT.json`, and `ARTIFACT_HASH_MANIFEST.json` are its controlling receipts.

VAULTED: V52s proves the closed-loop joint-target invariant and same-receipt junior yield mechanically, but fails L17 value (`581c <= 714c`) and loses 17/68 protected knife-edge games; it is rejected and the adopted V52l lineage remains operative.
