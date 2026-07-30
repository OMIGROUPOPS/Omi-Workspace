# Lawful Window-1 aim surface — specification and retention census

## Contract

The primary fit key is:

`(category, FRESH_LAST_TRADE, one-cent cell 5..94)`

The last trade must be the value visible at the exact consultation timestamp.
The consultation timestamp, trade/source timestamp, age, source identity, and
raw-response hash are part of the key lineage.

`TIGHT_MID`, `BBO_MID`, and `BEST_BID` are different populations. Each needs
its own fitted branch. A missing branch returns `NO_CELL`; no branch may reuse
the fresh-last-trade row.

The fit target is strictly forward: after consultation, which named resting
levels were subsequently touched before the guarded actual-start cutoff. The
maker fill model is: rest the order; a later last-traded price at or below it
fills; no depth proof and no five-contract gate.

Every observation also needs same-consultation bid and ask, with timestamps and
staleness. `spread = ask - bid`. If that denominator is missing or nonpositive,
the observation is `NO_DENOMINATOR`.

The only depth regimes are:

| Regime | Exact target |
|---|---|
| JOIN | best bid |
| touch−1 | best bid − 1 cent |
| 1× spread below mid | `floor((bid+ask)/2 − spread)` |
| 2× spread below mid | `floor((bid+ask)/2 − 2×spread)` |

The midpoint has no other role.

Each category × source branch × one-cent cell × regime reports its own `n`.
`n < 20` is `THIN`: no borrowing, smoothing, pooling, or category average.

## What survives from `range_spectrum_v1.jsonl`

The preserved artifact has 6,252 events, 12,361 leg slots, and the named
12,170 ranged anchors.

| Retention class | Legs |
|---|---:|
| anchor value inside lawful 5–94 cells | 11,994 |
| `last_before_t8` value, but anchor timestamp discarded | 9,605 |
| `first_after_t8`, consultation poll timestamp reconstructable | 2,565 |
| never traded | 191 |
| strict fresh-anchor contract, including trade timestamp, age, and raw hash | **0** |

The 2,565 reconstructable rows are not promoted to strict-fresh rows: their
timestamp is the snapshot poll time, not the last-trade occurrence time, and
the artifact does not retain a staleness stamp or raw-response hash.

As a deliberately relaxed diagnostic only, the reconstructable rows yield:

| Branch | lawful 5–94 legs | cells reaching n=20 |
|---|---:|---|
| fresh-last-trade-like | 2,396 | ATP Challenger 37; every other category 0 |
| tight-mid | 118 | 0 in every category |
| missing BBO denominator | 1 | not fit |
| outside 5–94 | 50 | not fit |

Therefore the 12,170-leg range spectrum is **not enough to fit the ratified
surface**. Its large count is mostly retrospective anchor values without the
timestamp needed to prove what the live decision knew.

## Collector fields required now

For every consultation and every leg:

- full event ticker and market ticker;
- decision/consultation timestamp;
- anchor source enum and exact anchor price;
- source event timestamp, receive timestamp, age/staleness, message or REST
  response ID, and raw-response SHA-256;
- best bid and best ask, each with source timestamp and staleness;
- schedule revision identity then known to the OS;
- later guarded actual-start cutoff and its evidence grade;
- immutable link from this consultation to the subsequent tape used for the
  forward outcome.

Without these fields, a future fit can describe the tape but cannot prove the
key the live OS actually possessed.
