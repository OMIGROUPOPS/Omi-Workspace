# Round-2 Window-1 partner-leg starvation forensic

Status: admitted development result; no Round-3 scoring or performance
evaluation was performed.

## Controlling record

- Results commit: `10ac6dbc68d65cb21ab3718e118ff34d7220ad87`
- Authorized Round-2 PRE-RUN:
  `47bfbd4335a435a30054be9007c5029331252eee`
- Independent audit:
  `807e2c865c3cf7384757c54a3b879518568dec4f`
- Audit report blob:
  `9bb51a3dc19fd055156ee958a6f208b1a725cbc4`
- D = 804 for each of eight candidates.
- C = PC = S = IC = 0 for each candidate.
- The eight ledgers contain 82 legitimate guarded Window-1 fill receipts
  in 60 candidate-event rows. Every fill-bearing event is single-leg.

This is a pairing failure of the frozen Round-2 candidates. It is not a
market ceiling and not a verdict on every possible OS policy.

## Mutually exclusive starvation adjudication

The machine-readable event ledger is
`PARTNER_LEG_STARVATION_LEDGER.jsonl`. Each fill-bearing candidate-event
appears once. Its sibling cause is mutually exclusive. Missing evidence is
never counted as a genuine nonfill.

| Candidate | Fill-bearing events | W1 fill receipts | Sibling cause | Count |
|---|---:|---:|---|---:|
| `r2_async_pair__park_join__hold` | 1 | 1 | order never called; no post-eligibility divot | 1 |
| `r2_async_pair__park_join__reaim` | 1 | 1 | reaim armed; no post-eligibility trigger | 1 |
| `r2_async_pair__touch_park__hold` | 29 | 40 | order never called; no post-eligibility divot | 15 |
| same | | | eligibility began after guarded cutoff | 8 |
| same | | | policy horizon ended before sibling reach | 2 |
| same | | | sibling filled only after guarded cutoff | 2 |
| same | | | first fill was partial; response did not arm before cutoff | 2 |
| `r2_async_pair__touch_park__reaim` | 29 | 40 | reaim armed; no post-eligibility trigger | 15 |
| same | | | eligibility began after guarded cutoff | 8 |
| same | | | reaim applied; policy horizon ended before reach | 2 |
| same | | | reaim applied; sibling filled after guarded cutoff | 2 |
| same | | | first fill was partial; response did not arm before cutoff | 2 |

Across all 60 candidate-events, the raw cause counts are:

| Starvation category | Count |
|---|---:|
| sibling order never called; no post-eligibility divot | 16 |
| reaim armed; no post-eligibility trigger | 16 |
| sibling eligibility began after guarded cutoff | 16 |
| first-leg partial response not armed before cutoff | 4 |
| policy horizon ended before sibling reach | 2 |
| sibling filled only after guarded cutoff | 2 |
| reaim applied; policy horizon ended before reach | 2 |
| reaim applied; sibling filled after guarded cutoff | 2 |
| placed but never reached | 0 |
| reached but insufficient positive size | 0 |
| required feature unavailable in the fill-bearing subset | 0 |
| reaim applied without executable improvement | 0 |

The zero counts matter: the admitted fill-bearing population does not
support a queue-shortage or insufficient-size explanation. Those remain
possible elsewhere in D=804, but they did not strand these 82 fills.

## Raw stratification

| Dimension | Raw counts |
|---|---|
| Tournament class | ATP main 46; ATP Challenger 2; WTA main 12; WTA Challenger/125 0 |
| First-filled role | favorite 54; underdog 6 |
| Entry-price band | 01-25: 2; 26-50: 2; 51-75: 48; 76-99: 8 |
| Start source | official/exact 22; proxy 36; clean causal interval 2 |
| First-filled birth band | ATP_CHALL-B6 2; ATP_MAIN-B3 6; ATP_MAIN-B5 34; ATP_MAIN-B8 6; WTA_MAIN-B1 2; WTA_MAIN-B3 8; WTA_MAIN-B6 2 |

Event and first-filled-leg raw counts are in
`PARTNER_LEG_STARVATION_COUNTS.json`; no grouping suppresses a zero-valued
starvation category.

## What broke

1. Round 2 converted fitted `t_deep` into a hard leg eligibility gate.
   Sixteen siblings never obtained an order before the guarded cutoff, and
   sixteen more did not become eligible until after it.
2. Park/walk placement required a recent qualifying divot. An available
   BBO and lawful pair posture were not enough to establish independent
   maker presence.
3. The first-fill chain armed only after a complete five-contract first
   leg. Two distinct partial-fill events, duplicated across hold/reaim,
   therefore did not invoke sibling response before cutoff.
4. `sibling_hold` was bookkeeping, not an order action. It neither rescued
   nor directly prevented a sibling.
5. Reaim was real but too conditional. It changed actual sibling orders in
   327 real D=804 base/reaim comparisons, yet in the fill-bearing subset it
   either lacked a later trigger (16), met a stale policy horizon (2), or
   arrived before a fill that was still outside the guarded cutoff (2).
6. Book-cell changes caused repeated recut cancellation/repost activity:
   the eight candidates emitted 4,989-10,388 reprices and 5,114-10,598
   cancels. That abandoned queue without requiring a new positive print.
7. The Round-2 `join` label did not express a true maker join. It used the
   same depth-subtracted price construction as park/walk.

The two early policy-horizon cases are `CERKEC/KEC` and `DEJBAE/BAE`.
Their bound schedule anchors ended the policy roughly 20.9 and 6 hours
before the ex-post guarded start boundary. No unbound schedule revision is
invented to repair them. The post-cutoff-fill cases include `BORDIM` and
`VANDRO`.

## Reaim and hold proof

The four Round-2 reaim variants changed real orders on 91, 85, 87, and 64
events. For all 327 events, every earlier order decision was byte-identical
to its hold base before the later +1 sibling trigger. All four pairs still
had zero completed Window-1 pairs. The underlying evidence is in
`BASE_REAIM_ORDER_DIFFERENCE_LEDGER.jsonl` and
`ROUND2_CANDIDATE_DECISION_PROOF.json`.

## Interpretation split

- Policy/mechanical defects: hard `t_deep` gating, recent-divot placement
  gating, complete-lot-only sibling arming, book-tick recut churn, a
  mislabeled join posture, and bookkeeping-only hold.
- Unavailable evidence surfaces: lawful independent shape mapping,
  Pinnacle, proved full depth, the latest deployed sealed pair-policy
  object, and timestamped schedule revisions beyond the bound observation.
- Eligible but unexecutable states in the fill-bearing subset: none proved
  by insufficient positive size; two orders were executable only after the
  guarded cutoff.
- Genuine causal nonfills: the full D=804 result ledgers retain genuine
  zero fills separately. This forensic does not relabel them as missingness
  or use them to infer a market ceiling.

No candidate was tuned, no holdout path was opened, and no production or
live surface was accessed.
