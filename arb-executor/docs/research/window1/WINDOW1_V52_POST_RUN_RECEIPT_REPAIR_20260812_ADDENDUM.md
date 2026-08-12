# V52 post-run receipt repair and named-check autopsy

Date: 2026-08-12

## Ruling and scope

The operator authorized a receipt-only repair after the frozen V52 dev-804
run. No V52 policy, fill, event result, score, frontier, regret row, or replay
decision may change. The repair adds the omitted top-level Stage-1 `pass`,
computes the first-post distributions from the earliest `PLACE_REST` per leg
only, and freezes exact-identity traces for the named ARSMAR and POLKUH cases.

Clause 1 of the V52 birth license is bound to the earliest causally valid
candidate from the operator-ratified disjunction:

- A: spread collapse plus cross-leg mid-sum settlement;
- B: sustained trade-cadence arrival.

This A-or-B selection law was ordered by the operator in the V52 Judgment Gate
order of 2026-08-12. Commit `9eff493b48a21af2706895dc4a1aa27e6fae684c`
supplies the fitted onset method, not a replacement ruling. In the exact frozen
five-game identities, ARS selects B; POL and KUH select A.

## Receipt-only repair

- `STAGE1_FLOW_ASSERTIONS.json` now exposes top-level `pass: true`; its five
  nested assertions remain unchanged and pass.
- First-post distributions now contain 1,203 earliest placements, one per
  placed leg. The prior receipt counted 7,236 `PLACE_REST` rows, including
  6,033 later placements/replacements.
- Rest mutations remain 10,743 and `REFLEX_POST` remains zero.
- The V52 policy SHA-256 remains
  `9a4cba7936cabf17b7edc6fbccfffbafee36b36a3ce8765c731dca9e8ba8cc10`.
- The frozen pre-repair hashes of all 25 score, event-ledger, state, action,
  and decision-trace artifacts reproduce byte-for-byte.
- Two clean complete builds reproduce every artifact byte-for-byte.

## Named trace identity correction

The earlier generic substring receipt could select an earlier ARSMAR event.
The trace-only autopsy binds the tape-pack identities exactly:

- `KXATPCHALLENGERMATCH-26JUL19ARSMAR`;
- `KXATPCHALLENGERMATCH-26JUL12POLKUH`.

This is a receipt identity correction only. Replay behavior and all score
artifacts remain unchanged.

## ARSMAR receipt facts

At the first 35-cent ARS print cluster, 275.174 minutes after the frozen window
opened, no licensed rest existed. The immediately preceding gate row is
`POST_ONSET_TRUE_TRADE_LOW_ABSENT`. The next gate row admits the 35-cent diary
receipt but blocks on `PAIR_POST_ONSET_LOWS_NOT_UNDER_PAR`. No S12 deep-gap
withhold row occurs in the critical window. ARS first posts later at 35 cents;
that rest remains uncredited at the hard edge.

## POLKUH receipt facts

Both POL and KUH select onset candidate A. KUH's first licensed post is 18
cents at epoch 1783878062, after its post-onset diary reaches 19 and POL's
reaches 80; KUH later credits at 19. POL never receives a licensed post. Its
gate ledger records the exact per-receipt reason strings and its post-onset
diary level of 80. The receipt also preserves the frozen V49b action/fill
moments beside V52 for each leg.

## Status

V52 remains the same blocked construction result; V49b remains the frozen
baseline. This repair authorizes no deployment and makes no behavioral edit.
