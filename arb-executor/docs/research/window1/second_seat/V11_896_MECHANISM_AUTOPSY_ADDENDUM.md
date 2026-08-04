# Addendum — traded-price floors and the holdout gate-lag test

Analysis seat only. Descriptive. Read-only on every input. Follows
`V11_NON_ACTION_896_MECHANISM_AUTOPSY.md`. Answers two operator questions.

## 1. Dual floor — ask-reachable vs traded, per leg

The prior audit's floor was `qualifying_ask_floor_cents` — an **ask**
(taker-reachable offer). Per the Aug-1 ruling the objective is stated against
**traded** prices, and an ask-based floor cannot see seller-aggressed prints
below the best offer. Both are now reported side by side for all 896 legs in
`DUAL_FLOOR_REGRET_896.csv` (joined from the committed dual-floor ledger; the
ask floor matches the prior audit's floor on **all 896**, zero mismatches).

Sources of each floor per leg: `ask_capacity_floor_cents` (offer with ≥10s
dwell and ≥5 top capacity), `lowest_traded_price_cents` (with aggressor side),
`seller_aggressed_trade_floor` (lowest price a **seller** aggressed into — the
price a resting **maker** buy would have been filled at), and its size-5 form.

### What moves

| achievable-floor definition | legs w/ floor | ≤ close | ≤ 97 | median |
|---|---:|---:|---:|---:|
| ask-capacity floor (taker, prior audit) | 860 | 716 | 860 | 51 |
| lowest traded price (any aggressor) | 782 | 739 | 782 | 51 |
| **seller-aggressed maker floor** | **544** | **502** | **544** | **50.5** |
| seller-aggressed, size-5 | 505 | 465 | 505 | 50 |

The lowest traded print is **seller-aggressed on 391 legs, buyer-aggressed on
391**, absent on 114.

**The ask floor is wrong in both directions, and the errors nearly cancel in the
median but not in the population:**

- **Overstatement.** **318 of the 860** ask-floor legs had **no seller
  aggression at all** in-window — a resting maker buy would never have been hit.
  The ask floor credited an achievable price where a maker could not have been
  filled. The count of maker-achievable legs falls **860 → 544**.
- **Understatement.** Of the 542 legs with both an ask floor and a seller
  aggression, the maker floor is **below** the ask on **319**, equal on 147,
  above on 76. On 319 legs a seller printed **below the best offer**, so the
  achievable maker entry was deeper than the ask floor showed.

What does **not** move: the per-leg price is nearly identical where a maker floor
exists (median 51 → 50.5), so per-leg regret *magnitude* is unchanged; the moves
are entirely in *which legs* count as achievable. Mechanism attribution,
coverage, and the ask-tape return metrics are independent of floor definition and
do not move.

### Frontier under each floor

| pair sum | ask floor (259 both-known ev) | seller-aggressed maker (119 both-known ev) |
|---|---|---|
| ≤ 93 | 9 ev / 18 legs | 4 ev / 8 legs |
| ≤ 95 | 12 ev / 24 legs | 7 ev / 14 legs |
| ≤ 97 | 21 ev / 42 legs | **34 ev / 68 legs** |
| < 100 | 88 ev / 176 legs | **108 ev / 216 legs** |

The maker frontier is computed over the 119 events where **both** sides had a
seller aggression (a maker fill was reachable on both). On that subset the deeper
below-offer prints push **more** pairs under par: completable-≤97 rises from 21 to
**34 events**, completable-<100 from 88 to **108**. At the tight thresholds
(≤93, ≤95) the count falls, because deep-completable events lose a leg to the
maker-reachability filter. The frontier is non-monotone in the floor definition,
for the same reason the tolerance counterfactual is: a traded objective both adds
below-offer depth and removes legs that never traded on the seller side.

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
