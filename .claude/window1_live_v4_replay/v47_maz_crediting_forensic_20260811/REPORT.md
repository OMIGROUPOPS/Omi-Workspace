FORK A — NO LAWFUL V47 MAZ REST EXISTED AT THE THREE 66¢ PRINT RECEIPTS; 66¢ WAS THE TERMINAL HARD-EDGE SNAPSHOT, LATER EXTENDED PAST V47'S WINDOW BY A RECONSTRUCTION.

# MAZ crediting forensic

## Controlling identity

- Event: `KXWTACHALLENGERMATCH-26JUL20MAZSPI`; leg: `MAZ`; category: `WTA_CHALL`; population: dev 804.
- Frozen V47 package commit: `fb74c8b8f0f5fa3bae69fab017ec937b6b13eb34`.
- Frozen event source: `.claude/window1_live_v4_replay/v47_same_tick_arm_20260810/MARKET_EVENT_LEDGER.jsonl.gz`.
- Frozen action source: `.claude/window1_live_v4_replay/v47_same_tick_arm_20260810/ACTION_TRACE.jsonl.gz`.
- Private MAZ BBO tape: SHA-256 `5d96fb846fa6fa5ea339b4f9fdc106af884f06c52ed13ec114cecefbef90aebf`, 654,981 bytes.
- Private canonical dev prints: SHA-256 `e9b5a765b51ddbf0d65364c4f38744ad949ca3c675e5b3a0e472392fbcfabb55`, 1,766,090,446 bytes.
- All timestamps below are normalized from the exchange/BBO epoch field to UTC. Prints and books use the same epoch clock and are directly comparable.

## Binary answer

V47's lawful MAZ span was `[2026-07-20T07:21:12Z, 2026-07-20T18:54:00Z]`. Its last admitted book receipt was `KXWTACHALLENGERMATCH-26JUL20MAZSPI-MAZ.csv.gz#row-2554` at `18:52:36Z`; the next book row, `#row-2555` at `18:54:30Z`, was already outside the hard edge. At the last lawful receipt the modeled rest was 66¢, and the event terminated `REST_UNFILLED_AT_HARD_PREBELL_EDGE` with `resting_target_at_edge_cents=66`.

The three cited prints occurred 52m08.389s, 58m09.647s, and 58m32.196s after that hard edge. V47 therefore had **no lawful active rest** at any of those receipts. The retained 66¢ value is an edge snapshot, not an order state authorized to persist after the edge. There is no V47 cancel receipt because the replay ends by domain boundary; that does not make the snapshot a post-edge rest.

## Full V47 MAZ rest lifecycle

Every price transition in the frozen V47 action trace is below. There was one initial post and eleven reprices. There was no cancel, repost after cancellation, fill, or post-edge transition.

| # | UTC | BBO receipt | Action | Rest before | Rest after | Signing path |
|---:|---|---|---|---:|---:|---|
| 1 | 07:21:12 | `...MAZ.csv.gz#row-2` | PLACE | none | 5 | `V41_RISING_PERSISTENCE_ONLY_JOIN_300S_P2_OVER_P1`; no sibling ask, so the incumbent path remained authoritative |
| 2 | 07:23:45 | `...MAZ.csv.gz#row-51` | REPRICE | 5 | 6 | same V41 rising persistent-level path; guard passed |
| 3 | 07:23:49 | `...MAZ.csv.gz#row-61` | REPRICE | 6 | 7 | same path |
| 4 | 07:23:50 | `...MAZ.csv.gz#row-64` | REPRICE | 7 | 8 | same path |
| 5 | 07:23:50 | `...MAZ.csv.gz#row-75` | REPRICE | 8 | 9 | same path |
| 6 | 07:23:51 | `...MAZ.csv.gz#row-77` | REPRICE | 9 | 10 | same path |
| 7 | 07:24:45 | `...MAZ.csv.gz#row-93` | REPRICE | 10 | 30 | same path |
| 8 | 07:24:45 | `...MAZ.csv.gz#row-94` | REPRICE | 30 | 64 | same path |
| 9 | 07:32:43 | `...MAZ.csv.gz#row-158` | REPRICE | 64 | 65 | same path |
| 10 | 12:23:28 | `...MAZ.csv.gz#row-480` | REPRICE | 65 | 66 | same path |
| 11 | 12:26:52 | `...MAZ.csv.gz#row-513` | REPRICE | 66 | 65 | same path |
| 12 | 14:44:30 | `...MAZ.csv.gz#row-693` | REPRICE | 65 | 66 | same path |
| terminal | 18:52:36 | `...MAZ.csv.gz#row-2554` | HOLD | 66 | 66 | `V41_RISING_PERSISTENCE_ONLY_JOIN_300S_P2_OVER_P1_ALREADY_AT_TARGET` |
| edge | 18:54:00 | boundary ledger | TERMINATE | 66 snapshot | no lawful post-edge order | `REST_UNFILLED_AT_HARD_PREBELL_EDGE` |

Between transition 12 and the last lawful receipt, V47 emitted `HOLD_REST`; it did not walk or re-aim. The lifecycle ends at the boundary.

## The three print receipts and every crediting evaluation

The raw trade receipts are distinct and are not joined.

| Trade receipt | UTC / price / size | Contemporaneous BBO | V47 rest at receipt | Input admission | `strictPrintCross` | `tradedAtLevel` | `quoteTouch` | Result |
|---|---|---|---|---|---|---|---|---|
| `a6cffc98-30a4-4c51-d8d9-8f66384b68f6` | 19:46:08.388860 / 66 / 176.84 | row 4912 at 19:46:08, 67/69, last 68; age 0.389s | **none**; terminal snapshot was 66 | REJECT: `ts > bound.right` | NOT RUN | NOT RUN | NOT RUN | outside V47 domain by 3,128.389s |
| `015ca52b-b5c5-4cd6-9a50-5204e02f763d` | 19:52:09.646859 / 66 / 62.19 | row 5527 at 19:52:09, 66/68, last 68; age 0.647s | **none**; terminal snapshot was 66 | REJECT: `ts > bound.right` | NOT RUN | NOT RUN | NOT RUN | outside V47 domain by 3,489.647s |
| `a3136da1-75e1-5c52-3c8d-7bbda55f9001` | 19:52:32.195610 / 66 / 64 | row 5531 at 19:52:29, 66/68, last 68; age 3.196s | **none**; terminal snapshot was 66 | REJECT: `ts > bound.right` | NOT RUN | NOT RUN | NOT RUN | outside V47 domain by 3,512.196s |

All three prints are canonical true prints with `taker_side=no` and `taker_book_side=ask`: they are seller-side executions. Had one been inside the frozen V47 span while a 66¢ rest stood, `tradedAtLevel(order, print)` would have been true. That counterfactual does not alter the replay: the prints were discarded at input admission before any crediting organ saw them.

The exact executable clauses are:

- `arb-executor/analysis/build_window1_v38_maker_only.js:177`: `if (!Number.isFinite(ts) || ts < bound.left || ts > bound.right) continue;` — rejects each raw print while loading the leg's lawful print stream.
- `arb-executor/analysis/build_window1_v38_maker_only.js:312`: the simulator's second hard-edge fence, `if (row.ts < base.left || row.ts > base.right) continue;`.
- `arb-executor/analysis/build_window1_v38_maker_only.js:326`: strict print-cross evaluation — not reached.
- `arb-executor/analysis/build_window1_v38_maker_only.js:329`: market-ruler strict print-cross evaluation — not reached.
- `arb-executor/analysis/build_window1_v38_maker_only.js:332`: trades-at-level evaluation — not reached.
- `arb-executor/analysis/build_window1_v38_maker_only.js:345`: quote-touch evaluation — not reached.
- `arb-executor/analysis/window1_v41_maker_machine.js:71-81`: the three credit predicates. None was invoked for these receipts.

No dwell, aggressor-side, arrival-direction, or queue-position filter withheld these credits. The controlling fact is the frozen hard-right edge. Campaign-wide Fork-B impact counting is therefore **NOT APPLICABLE**: zero crediting-organ evaluations for these receipts share a withholding clause, because no crediting-organ evaluation occurred.

## Fork-A reconstruction defect

Commit `9ff18c8c68ab130266781701720229b52b5b41bc` created a later “dipless” reconstruction whose MAZ span was `14:10:00Z` through `20:25:00Z`. It copied V47's terminal `resting_target_at_edge_cents=66` into that different span and treated the copied value as though the V47 order remained alive. That is the source of the “66 all window” statement. It is not machine truth from V47.

The direct inherited artifacts are:

1. `.claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/THE_DIPLESS_43_RAW.json`
2. `.claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/THE_DIPLESS_43_RAW.md`
3. `.claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/exemplar_packs/dipless_top/26JUL20MAZSPI_DECISION_MARKS.json`
4. `.claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/exemplar_packs/dipless_top/26JUL20MAZSPI_DUAL_TIMELINE_V2.csv`
5. `.claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/HIDDEN_BOOK_CENSUS.json` at commit `6bc169bfcc448d6df8a6cd0b8dae5638e3853ebf`
6. `.claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/HIDDEN_BOOK_CENSUS.md` at the same commit

The hidden-book classifications of the later prints against their contemporaneous displayed BBO can remain descriptively correct. The inherited defect is the attribution that a lawful V47 66¢ rest was still present. No artifact in the frozen V47 package inherits the extension: V47 records the later 66¢ reach outside its edge and terminates the rest at the edge.

The raw MAZ tape independently contains a consecutive displayed-bid-66 run from row 4926 at `19:46:19Z` through row 5775 at `19:56:57Z`: 850 rows over 638 seconds. The previously reported 712-row count is a subset/reconstruction count, not the full raw consecutive-row count; neither count extends V47's order lifecycle.

## LUZTSE control

The control receipt at commit `61b47a8478163adc5777d2422a5979f40ff6b4cf` correctly classifies `LUZTSE|TSE` as `CHAIN_L6_PRESENT_BUT_NO_COUNTERPARTY`: a rest and causal level existed, but no qualifying counterparty trade reached it after lawful stand inside the relevant span. Its low prints were pre-trigger.

MAZ does have later counterparty prints. Under unchanged V47, however, they are post-edge and therefore out of domain before the receipt-pull → causal-level → counterparty chain. LUZTSE remains a known-correct no-credit; MAZ is not an opposite-facts crediting failure inside V47. It is a later reconstruction crossing two different boundaries.

## Determinism and byte identity

A fresh clean V47 replay was run from the unchanged policy on all 804 dev events and compared with the frozen package. `DETERMINISM_RECEIPT.json` reports:

- clean builds: 2
- compared artifacts: 35
- byte-identical: `true`
- mismatches: `[]`

Policy/source identities before and after the rerun were unchanged:

| Source | SHA-256 |
|---|---|
| `arb-executor/analysis/build_window1_v38_maker_only.js` | `04e741b34e22e113cfe708fc2a9fb96e66844005b7b7511d4bc132ac426d97f6` |
| `arb-executor/analysis/window1_v41_maker_machine.js` | `c81a9265f320c27848405b779877e22820243ba6765501879cbdded9c5fdc532` |
| `arb-executor/analysis/window1_v47_same_tick_arm.js` | `73728d9902fbd19f7ef7c67cd0d406324faed140f86e65f2a8ded71f528f95b0` |
| `arb-executor/analysis/build_window1_v47_same_tick_arm.js` | `6b503eb0f8db8b242d717edc1a528729ef4459522dbc00e01afb33733557a788` |

No replay decision code, policy code, tape, print source, boundary, score, or frozen artifact was modified. This report is the only added file.
