# Frozen Round-3 Window-1 policy-family specification

Round 3 is an eight-candidate, score-free development PRE-RUN. D remains
804, the metric contract is unchanged, July 12-20 is the only development
scope, and July 24-26 remains sealed.

## Mechanical changes from Round 2

1. Each leg establishes maker presence at its own first positive-size
   causal BBO after policy activation. The fitted `t_deep` receipt is
   advisory and cannot prevent an order.
2. Touch joins the external bid, join improves it by one cent while
   remaining maker-safe, and park/walk use the frozen causal depth.
3. A causal book update may update a latent recut cell but cannot abandon
   queue. A later receipt-identifiable positive-size print is required for
   a divot recut, walk, or response repost.
4. Any first positive fill, including a partial, arms the sibling response.
   Hold leaves the sibling independently managed. Reaim changes nothing
   immediately; at the sibling's own strictly later lawful print trigger it
   may post exactly base +1.
5. Reaim must pass the maker, band, positive-price, par, pair-cost, and
   maximum-cost guards. Missing response evidence is a named NO_CALL and
   does not censor the underlying leg.
6. Zero, null, malformed, synthetic, unverified, duplicate, or
   receipt-less transitions contribute zero to every microstructure
   surface.

The numeric surface is closed: `free_numeric_parameters` is empty.

## Frozen candidates, in order

1. `r3_pair_presence__park_join__hold`
2. `r3_pair_presence__park_join__reaim`
3. `r3_pair_presence__touch_park__hold`
4. `r3_pair_presence__touch_park__reaim`
5. `r3_causal_steer__park_join__hold`
6. `r3_causal_steer__park_join__reaim`
7. `r3_full_os__walk_park__hold`
8. `r3_full_os__walk_park__reaim`

No ranking or selection rule is frozen. No candidate may be added after
this PRE-RUN.

## Preserved laws

- Pair quantity: exactly five contracts per leg.
- Pair order guard: combined active maker prices cannot exceed 100 cents.
- Scoring contract, if later independently authorized: D=804; C is both
  legs exactly five inside guarded Window 1; PC requires strictly negative
  combined close delta; S requires combined entry cost strictly below 100;
  IC requires both individual deltas strictly negative.
- Official/exact guard remains 60 seconds; proxy guard remains 900 seconds.
- Policy code cannot read realized-start truth.
- Schedule-only evidence can anchor policy but cannot prove a positive
  Window-1 result.
- Missing required data is named and censored; optional module abstention
  is named NO_CALL and the underlying policy continues.

## Unavailable or non-coverage surfaces

- Cohort: all real calls remain below n=30, so the module is
  `NO_CALL_UNAVAILABLE`.
- The latest deployed sealed pair-policy object is not bound in this
  research checkout. Older entry-surface tables are not substituted for it.
- Timestamped schedule revisions beyond the bound exchange observation are
  unavailable. The causal policy horizon may therefore precede ex-post
  actual start.
- Lawful independent shape mapping, Pinnacle, and proved full depth remain
  unavailable.
- Own-order subtraction is loaded as a safety invariant, but zero
  attributable own volume means it is not credited as decision-changing
  coverage.
- Fitted `t_deep` is retained only as an inert diagnostic receipt, not as a
  candidate family or order control.

The executable source is
`arb-executor/analysis/window1_round3_instrument.py`; the exact candidate
surface is
`arb-executor/docs/research/window1/WINDOW1_ROUND3_CANDIDATES_V1.json`.
