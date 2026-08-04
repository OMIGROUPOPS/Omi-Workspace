# Carry-budget re-cut — pricing the single-leg exposure ruling

Analysis seat only. Descriptive. Read-only. Re-cuts the 359 DISJOINT events from
`V11_896_EXECUTABLE_CEILING.md` by **single-leg carry budget**: the gap between
the two legs' reachable windows is the time you hold the first-filled leg exposed
before the second becomes fillable. Cumulative in budget and in frontier tier.
Numbers in `CARRY_BUDGET_SUMMARY.json`; per-event gaps in
`EXECUTABLE_CEILING_EVENTS.csv`.

**Acceptance (enforced): PASS.** OVERLAP + DISJOINT = 390; disjoint-within-budget
monotonic non-decreasing in budget; all disjoint gaps > 0.

## The 359 sequential events by carry budget (cumulative)

| carry ≤ | ≤93 | ≤95 | ≤97 (par) | <100 | any tier |
|---|---:|---:|---:|---:|---:|
| 1 h | 14 | 22 | 33 | 106 | 106 |
| 2 h | 21 | 33 | 62 | 161 | 161 |
| 4 h | 29 | 49 | 112 | 247 | 247 |
| 8 h | 36 | 68 | 158 | 307 | 307 |
| > 8 h (never affordable) | 21 | 34 | 49 | 52 | 52 |

52 of the 359 need more than 8 hours of single-leg carry — effectively never
lockable within a sane budget.

By category (any tier, cumulative):

| carry ≤ | ATP_CHALL | ATP_MAIN | WTA_MAIN | WTA_CHALL | total |
|---|---:|---:|---:|---:|---:|
| 1 h | 55 | 19 | 12 | 20 | 106 |
| 2 h | 92 | 27 | 17 | 25 | 161 |
| 4 h | 138 | 41 | 35 | 33 | 247 |
| 8 h | 158 | 62 | 52 | 35 | 307 |

## Which side you carry

The earlier-filled leg is the one you hold. **Dearer-first dominates at every
budget (~1.5:1)** — you are usually long the expensive side while chasing the
cheap side:

| carry ≤ | carry the DEARER leg | carry the CHEAPER leg |
|---|---:|---:|
| 1 h | 62 | 44 |
| 2 h | 98 | 62 |
| 4 h | 146 | 100 |
| 8 h | 185 | 121 |

## Combined executable ceiling = the operator's completable count at a risk budget

Zero-carry OVERLAP (31) plus the disjoint events affordable within the budget.
This is the real completable denominator as a function of the allowed single-leg
carry. Shares are of the 804-game book.

| carry budget | ≤97 (par) | %804 | < 100 | %804 |
|---|---:|---:|---:|---:|
| 0 (simultaneous only) | 10 | 1.2% | 31 | 3.9% |
| ≤ 1 h | 43 | 5.3% | 137 | 17.0% |
| ≤ 2 h | 72 | 9.0% | 192 | 23.9% |
| ≤ 4 h | 122 | 15.2% | 278 | 34.6% |
| ≤ 8 h | 168 | 20.9% | 338 | 42.0% |
| ∞ (price ceiling) | 217 | 27.0% | 390 | 48.5% |

Full ≤93/≤95 columns are in the JSON.

## Reading

The completable rate is not a constant — it is a **function of the carry budget
the operator is willing to run**. Buying only simultaneous locks caps you at ~4%
of the book (~1% at par). Accepting up to an 8-hour single-leg carry — long the
expensive side most of the time — reaches ~42% under 100 and ~21% at par, and
even the unbounded price ceiling stops at 48.5% / 27%. **No carry budget brings a
75% book-wide completion target within reach**; the ruling on acceptable single-leg
exposure sets exactly where between 4% and 48% the achievable rate lands.

## Artifacts

`CARRY_BUDGET_SUMMARY.json` (all budget × tier × category grids, carried-side
splits) under `.claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/`.
