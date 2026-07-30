# NIK–VRB coupling at the VRB divot

## Answer first

`live_v4` does **not** maintain a joint market object before pricing a leg.
It has pair-budget checks and post-fill headroom, but no continuously updated
two-book state, no cross-book flow inference, no lead/lag state, and no rule
that converts “VRB is the riser” plus “the riser divots first” into priority
for VRB.

At VRB's 70-cent print, the books already described the pair clearly:

| Source event | T-minus scheduled | T-minus actual bell | NIK bid/ask/last | VRB bid/ask/last | Combined bid/ask/last |
|---|---:|---:|---:|---:|---:|
| VRB true print, 0.06 contracts at 70 | T−316.064 | T−321.064 | 28 / 29 / 32 | 69 / 70 / 70 | 97 / 99 / 102 |

The 5-minute difference between the two T-minus columns is the exact observed
schedule slip: scheduled start was T−0 scheduled / T−5 actual bell; the exact
bell was T+5 scheduled / T−0 actual bell.

The full table contains 13,123 chronological rows from gate open
(T−480 scheduled / T−485 actual bell) through the bell
(T+5 scheduled / T−0 actual bell):

- 7,318 NIK BBO states and 80 NIK true prints;
- 5,660 VRB BBO states and 63 VRB true prints;
- one gate boundary and one bell boundary.

It uses no constructed midpoint. `combined_bid_total` is bid+bid,
`combined_ask_total` is ask+ask, and `combined_last_total` is last+last.

## 1. Why the selector returned DROP

The DROP was **not** a simultaneous-pair test. The selector never read NIK.

`_selector_verdict(cat, current_price)` at
`arb-executor/live_v4.py:2960-3004` received only:

- category `ATP_CHALL`;
- VRB discovery/consultation price 70;
- the fitted ATLAS page `ATP_CHALL|leader|51_75`.

For each fitted contention tier it computed:

```
aim = current_price - fitted_depth
EV = p_exit*8 + (1-p_exit) *
     [p_win_entry*(100-aim) - (1-p_win_entry)*aim]
yield = 100*EV/aim
```

At the selector decision (T−316.033 scheduled / T−321.033 actual bell):

| Tier | Depth | Aim | p_exit | p_win_entry | Computed yield |
|---|---:|---:|---:|---:|---:|
| p25 | 1 | 69 | 0.137 | 0.617 | −7.5% |
| p50 | 3 | 67 | 0.192 | 0.597 | **−6.5%** |
| p75 | 6 | 64 | 0.284 | 0.538 | −7.9% |

The best tier was −6.5%, below the hard 8% bar, so the leg selector returned
DROP. That verdict says the **VRB page's exit/win arithmetic** failed. It says
nothing about whether NIK and VRB were simultaneously near 99 or whether the
two lows were reachable asynchronously.

A different function, `_pair_verdict` at
`arb-executor/live_v4.py:3014-3055`, ran beside it. That function also did not
read NIK's actual 28/29 book. It manufactured a sibling price as
`100 - VRB current_price = 30`, tried both fitted path compositions, and
obtained 93 and 94. It therefore returned `PAIR-COMPOSED`.

The live seesaw check at `arb-executor/live_v4.py:3057-3098` did read NIK's
current BBO midpoint, but only to ask whether VRB's proposed bid plus NIK's
fitted deep cast exceeded 97. It was a refusal ceiling, not an asynchronous
opportunity or ordering model.

Therefore:

- DROP was a per-leg fitted-return verdict;
- PAIR-COMPOSED was a separate synthetic-complement calculation;
- the seesaw was current-budget arithmetic;
- none of the three evaluated the actual chronological two-book opportunity.

## 2. Orientation knew VRB should go first, but aim did not consume it

At T−316.033 scheduled / T−321.033 actual bell,
`_orientation_prior` called VRB the riser with conviction 1.0:

- cohort vote: VRB riser, weight 2;
- anchor-role vote from bids NIK 28 / VRB 69: VRB riser, weight 1.

That prior influenced the preliminary park role in `_v4_entry_anchor`.
Because VRB was the riser, the preliminary target became its current best bid,
69. But `_initial_entry_aim` then replaced that preliminary price with the
symmetric ATLAS p50 dip, 70−3=67. The only later branch that can restore a
riser-near-now target requires `orientation_live=true`; the deployed config
has it false.

There is also no priority state saying:

1. riser is expected to divot first;
2. its divot is currently present;
3. acquire or rest for that side before casting the faller.

The code therefore held both facts—VRB was the riser, and doctrine expected
the climb-side divot first—but never joined them into the order decision.

## 3. Existing 804-game inter-divot evidence

This section reads the already-built `WINDOW1_T2_GAME_GRID.json`. It does not
run `live_v4`, regenerate the grid, or perform another 804-game replay.

One correction matters: 206 minutes was the interval from VRB's low to the
NIK **fill**, not to NIK's low.

- VRB low: T−316.064 scheduled / T−321.064 actual bell.
- NIK fill: T−110.050 scheduled / T−115.050 actual bell.
- NIK tape low: T−51.172 scheduled / T−56.172 actual bell.
- VRB-low → NIK-fill: 206.0 minutes.
- VRB-low → NIK-low, the actual inter-divot gap: **264.9 minutes**.
- The five-contract floor-proof gap was 266.6 minutes.

The existing grid provides two tape-low timestamps and a resolvable climb-side
proxy for 752 of 804 games. Forty-nine lack one or both tape lows; three have
no resolvable side. The proxy is the grid's native `leader` where available
(466 games), otherwise the higher-priced leg at the retained Window-1 open
(286). This is not presented as 804 live `_orientation_prior` calls.

| Scope | n | Gap p25 | p50 | p75 | p90 | Riser first |
|---|---:|---:|---:|---:|---:|---:|
| All usable | 752 | 49.7m | **122.5m** | 234.0m | 324.6m | 453 / 752 = **60.2%** |
| Native-leader role only | 466 | 51.6m | **111.8m** | 204.9m | 285.0m | 290 / 466 = **62.2%** |
| ATP Challenger | 346 | 58.0m | **123.3m** | 226.2m | 297.3m | 215 / 346 = **62.1%** |
| ATP Main | 138 | 64.2m | **173.3m** | 311.1m | 376.0m | 76 / 138 = **55.1%** |
| WTA Challenger | 133 | 41.4m | **90.4m** | 153.7m | 244.2m | 82 / 133 = **61.7%** |
| WTA Main | 135 | 40.1m | **131.1m** | 255.3m | 378.8m | 80 / 135 = **59.3%** |

The old 41–62 minute p50 does not reproduce on this 804-game corpus. It came
from the earlier 2,435 detected-bell-pair SEQFLOOR population, including ITF
and different retention/boundary conventions. On the present corpus,
climb-side-first is directional but weaker than the old 2:1 summary:
approximately 60–62%.

NIK–VRB's 264.9 minutes is above the ATP Challenger p75 and below its p90.
It is a long separation, but not an isolated impossibility in this corpus.

## 4. What reads both books today

There is no pre-price joint-book object.

| Existing path | Both books? | What it actually does |
|---|---|---|
| `_orientation_prior` | Yes | Reads both bids to name leader/dog and combine orientation votes; cached for 300 seconds |
| `_pair_verdict` | No | Replaces the sibling with `100-current_price`; tests fitted compositions |
| `_pair_seesaw_state` | Partly | Reads sibling BBO midpoint and deep fitted aim; refuses only if combined target exceeds 97 |
| `_v4_entry_anchor` faller branch | Partly | Checks own bid + sibling bid against the combined budget |
| `_reaim_sibling_on_arrival` | Yes, after fill | Carries `combined_goal - filled_basis` to the remaining leg |

None computes:

- the combined bid, ask, and last-trade totals on every tick;
- which side's bid is strengthening while the inverse ask loosens;
- paired print direction or signed taker flow;
- cross-leg quote velocity, lead/lag, or absorption;
- whether a live riser divot should be acted on before the faller cast;
- whether one leg's tightening predicts the other's next loosening.

## Joint-book-state specification

The missing object should be event-scoped and recomputed whenever either leg
receives a BBO update or true print, before either leg is priced:

```text
JointBookState(event, timestamp)
  leg_a: bid, ask, top sizes, last, print size/side, source timestamps, ages
  leg_b: bid, ask, top sizes, last, print size/side, source timestamps, ages
  totals:
    bid_total = bid_a + bid_b
    ask_total = ask_a + ask_b
    last_total = last_a + last_b
    bid_headroom_to_100
    ask_excess_over_100
  flow:
    rolling signed print count and volume per leg
    bid/ask size change per leg
    spread tightening/loosening per leg
    cross-leg inverse move and lead/lag
    absorbing_leg, distributing_leg, confidence, evidence
  orientation:
    riser, faller, conviction, source votes
    expected_first_divot_side
  lifecycle:
    first_divot_seen, side, price, timestamp
    second_cast_active, remaining budget
  validity:
    both books present, freshness per source, crossed/one-sided refusal reason
```

The aim chokepoint should receive one immutable `JointBookState` snapshot and
return a pair decision, not two unrelated leg decisions:

```text
PairAimDecision
  first_priority_leg
  first_resting_price and reason
  sibling_cast_price and reason
  asynchronous_sequence thesis
  joint-state input hash
  refusal reason if either book is missing/stale
```

The state does not require simultaneous fills. Its purpose is the opposite:
read the match as one inverse market, identify which side is presenting the
first divot, and preserve the other side's cast for its later moment. Budget
arithmetic remains a constraint on that decision, not the market-reading
engine itself.
