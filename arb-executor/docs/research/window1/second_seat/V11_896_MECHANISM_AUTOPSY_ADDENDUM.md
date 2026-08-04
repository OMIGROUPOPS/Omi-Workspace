# Addendum — traded-price floors and the holdout gate-lag test

Analysis seat only. Descriptive. Read-only on every input. Follows
`V11_NON_ACTION_896_MECHANISM_AUTOPSY.md`. Answers two operator questions.

## 1. Maker floor by residency — corrected

**Retraction.** An earlier draft of this section reported a "maker ceiling
halved, 860 → 544" and a both-sides-print-conditioned frontier. That used a
retired frame and is withdrawn. Per the vaulted Aug-1 ruling, **a qualifying ask
at X is maker-reachable by residency**: our bid at X becomes the best bid and the
stepping seller hits us as maker — no historical print at X is required, and its
absence is explained by our absence from the book, not by unavailability.

Corrected definition, full denominator, no both-sides-print conditioning:

```
maker_floor(leg) = min( qualifying_ask_floor , seller_aggressed_traded_low )
```

Per-leg values in `MAKER_FLOOR_REGRET_896.csv`; all cuts in
`MAKER_FLOOR_CORRECTED_SUMMARY.json`.

**Acceptance checks (enforced before commit): PASS.** `maker_floor ≤ ask_floor`
on every leg — **0 violations**; maker-floor leg count ≥ ask-floor leg count on
every cut (ALL, each category, each region, all 16 category×region) — **0
violations**.

The `544` (seller-aggressed present) and `782` (any recorded trade) rows are
**recorded-tape evidence tiers — corroboration that the level traded — not the
availability denominator.** Availability is the residency floor above, defined on
**862** legs (the 860 with a qualifying ask, plus 2 with a seller-aggressed low
but no qualifying ask).

### What moves

| floor | legs | ≤ close | ≤ 97 | median |
|---|---:|---:|---:|---:|
| ask-capacity (taker/prior) | 860 | 716 | 860 | 51 |
| **maker floor (residency)** | **862** | **739** | **862** | **51** |

`maker_floor` is strictly below `ask_floor` on **319** legs (a seller stepped
below our resting bid), equal on the rest. The median barely moves (51 → 51), so
per-leg regret *magnitude* is nearly unchanged; what moves is the joint frontier,
because a 1-2¢ improvement on each of two legs compounds.

### Per category × region (ask-floor legs → maker-floor legs; median ask / maker; maker < ask)

| cut | legs | medAsk | medMkr | mkr ≤ close | mkr ≤ 97 | mkr < ask |
|---|---:|---:|---:|---:|---:|---:|
| ATP_CHALL le25 | 73 | 15 | 14 | 54 | 69 | 24 |
| ATP_CHALL 26_50 | 156 | 38 | 37 | 138 | 156 | 45 |
| ATP_CHALL 51_75 | 140 | 62 | 61 | 124 | 140 | 47 |
| ATP_CHALL ge76 | 69 | 84 | 84 | 61 | 69 | 21 |
| ATP_MAIN 26_50 | 56 | 38 | 38 | 46 | 56 | 22 |
| ATP_MAIN 51_75 | 64 | 62.5 | 61.5 | 58 | 64 | 38 |
| WTA_MAIN 51_75 | 41 | 65 | 64 | 36 | 41 | 19 |
| WTA_CHALL 51_75 | 52 | 62.5 | 61.5 | 42 | 52 | 14 |
| **all** | **896** | **51** | **51** | **739** | **862** | **319** |

(full 16-cell grid in the summary JSON.)

### Joint objective — pair frontier, maker floor vs ask floor

Monotone expansion (maker ≤ ask everywhere ⇒ at least as many completable pairs
at every threshold). Over the both-legs-known non-action events (ask 259 / maker
260):

| pair sum | ask floor | **maker floor** |
|---|---|---|
| ≤ 93 | 9 ev / 18 legs | **11 ev / 22 legs** |
| ≤ 95 | 12 ev / 24 legs | **16 ev / 32 legs** |
| ≤ 97 | 21 ev / 42 legs | **59 ev / 118 legs** |
| < 100 | 88 ev / 176 legs | **171 ev / 342 legs** |

The below-offer depth roughly **triples** the par-completable non-action events
(21 → 59) and doubles the under-100 set (88 → 171).

### V19 comparison — and an independent check on the 500-leg sibling claim

V19 (pair-couple abstention, the built sibling fix; V18 was retracted for
treating category monoliths as couples) acted on exactly **138 of the 896** V11
non-actions, **all 138 resolved by the pair hypothesis alone** — no single-leg
hypothesis could place them. Its entries sit at the maker floor on **67 of 138**
and a median **1¢** above it, confirming the residency fill model. Globally V19
lifts V11 **712 → 850** acted legs, **185 → 251** completed pairs, **94 → 102**
under-par; its completed-pair frontier over 804 is LE_97 = 34, LT_100 = 102.

This is the independent test of the prior report's "synthetic-sibling veto binds
500" and it **refines** it. The 500 is a count of a *binding predicate* at the
first actionable floor, not a placement forecast. The actual pair-couple fix —
which also supplies a coupled shape verdict — converts only **138** of them,
because most of the 500 carry co-binding shape or anchoring predicates that the
sibling read alone does not clear. After V19, **758 of the 896 remain stopped**,
dominated by anchoring (257 current-ask-above-low), unanimous-lower (126),
still-unresolved sibling (119), stable-same-price (94), and source (90). So:
sibling is real and the largest single lever actually built (138), but "fix
sibling ⇒ place 500" does not hold — the residual is anchoring + shape-unanimity +
source, exactly the mechanisms named in the main autopsy.

## 2. Holdout gate-lag test — is the anchoring fix worth building?

The holdout (Jul 24-26) has **268** V11 never-placed legs. Terminal-reason
distribution:

| terminal reason | legs |
|---|---:|
| FLOOR_CONSENSUS_BUT_CURRENT_ASK_IS_ABOVE_OBSERVED_LOW | 83 |
| ALL_SURVIVING_SHAPES_SAY_LOWER | 61 |
| SOURCE_UNAVAILABLE | 42 |
| FLOOR_CONSENSUS_BUT_SIBLING_DIRECTION_NOT_INDEPENDENTLY_OBSERVED | 31 |
| FLOOR_CONSENSUS_BUT_STABLE_SAME_PRICE_ASK_LACKS_SIGNING_SUPPORT | 29 |
| SURVIVING_SHAPES_DISAGREE_OR_LIBRARY_GAP | 19 |
| three singleton reasons | 3 |

### Of the 83 "current ask above observed low" legs, how many were sibling-vetoed at their first actionable floor? **Zero.**

- Across all **57,912** recorded above-low decisions for the 83, the only binding
  predicates are the anchoring/executability stack:
  `CURRENT_ASK_ABOVE_OBSERVED_LOW` on **100%**, `NO_FRESH_OWN_BOOK_RECEIPT` on
  20,636, `TOP_ASK_CAPACITY_BELOW_FIVE` on 4,182, `ASK_DWELL_BELOW_10_SECONDS`
  on 2,992. `INVERSE_SIBLING_UNRESOLVED` appears in **none** of them, and no
  shape predicate appears at all.
- **None of the 83** carries `INVERSE_SIBLING_UNRESOLVED` anywhere in its full
  holdout ledger record. The only 26 holdout legs that touch the sibling
  predicate are all `CREDITED_ON_STRICTLY_LATER_EXECUTABLE_ASK` — **placed**
  legs where the sibling resolved.
- These were real, long-lived floors, not fleeting liquidity: e.g. INCSMI-INC
  formed a qualifying ask floor at 34 with a **263-second** dwell and a
  seller-aggressed maker touch at 34; the ask then sat a median **1 cent** above
  the observed low (55 of 83 at 1¢, 66 at ≤2¢, 73 at ≤3¢).

**Caveat.** The above-low decision ledger is scoped to post-rise decisions, so the
at-low qualifying-floor instant's predicates are not separately published. But the
sibling predicate appears in zero of the 83's full records and zero of their
57,912 decisions, and had it bound terminally these legs would carry the sibling
terminal — 31 other holdout legs do; none of the 83.

### Verdict

This is the **opposite** of training, where **183 of 283** above-low terminals
were synthetic-sibling-vetoed at their first floor (the above-low gate was a
symptom of the sibling veto). On the holdout, the above-low population is a
genuine anchoring/freshness failure: the ask returned to sit 1-3¢ above the
observed low and never re-touched it with a fresh qualifying book, with
`NO_FRESH_OWN_BOOK_RECEIPT` the dominant co-gate. **For the holdout's 83, the
anchoring fix (paired with book-freshness) is the binding lever, not the sibling
fix.** Codex's own counterfactual bounds the prize: a 1¢ tolerance makes 52 of 83
actionable and moves completed pairs 41 → 70.

## Artifacts

Under `.claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/`:
`DUAL_FLOOR_REGRET_896.csv` (per-leg ask vs traded vs maker floor with aggressor)
and `DUAL_FLOOR_AND_HOLDOUT_ADDENDUM.json` (both computations, machine-readable).
