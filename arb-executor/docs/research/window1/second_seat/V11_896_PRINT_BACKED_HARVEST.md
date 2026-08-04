# Print-backed harvest and carry accounting

Analysis seat only. Descriptive. Read-only. Two tightenings on
`V11_896_CARRY_CENTS.md`, same 359 disjoint population, same exit-band source
(`arb-executor/data/durable/spike_volatility_map/{cat}_adaptive_exit_bands.parquet`,
`band_exit_X = +X cents`, `live_v4.py:660`). Rows in
`PRINT_BACKED_HARVEST_EVENTS.csv`; numbers in `PRINT_BACKED_HARVEST_SUMMARY.json`.

## 1. Accounting

**The missing event.** The prior per-bucket × side table summed the DEARER and
CHEAPER columns only (358). The 359th is **`KXWTAMATCH-26JUL17PUTSHE`** — held leg
PUT, fill 19¢, in the ≤2h bucket — whose two maker floors are **equal**, so it is
`held_side = TIE`, neither dearer nor cheaper. Full split: **DEARER 219 · CHEAPER
139 · TIE 1 = 359.**

**The 19 zero-length carries.** These are events whose held-leg fill and completion
coincide (an instantaneous fill, e.g. a seller-aggressed print with no dwell), so
there are no mid samples in the carry window. Disposition: they are **counted in
the bucket conservation and in the band-touch denominators**; `net/MAE/MFE` are
blank; `band_touched = False` for all 19 by construction (empty window). They fall
in buckets ≤1h 17 · ≤2h 1 · ≤8h 1, categories ATP_CHALL 8 · ATP_MAIN 7 · WTA_CHALL
2 · WTA_MAIN 2 (18 banded + 1 HOLD-cell). They live in the "true exposure — not
harvested" column, never in a harvest count.

Conservation stands: **31 OVERLAP + 359 DISJOINT = 390**; banded 327 + HOLD 32 =
359.

## 2. Print-backed harvest vs residency-exit

A band-touch is a real harvest only if a buyer was actually there to take the exit.
Print-backed = a **buyer-aggressed true print** (`taker_side = "yes"`, i.e. BUY per
the dual-ledger aggressor law) at `price ≥ fill + X` during the carry window, read
from `prints.jsonl`. Residency-exit = `best_bid ≥ fill + X` (a resting buyer).

| measure | banded events | harvests | rate |
|---|---:|---:|---:|
| residency-exit (bid touch) | 327 | 55 | 17% |
| **print-backed (buyer lifted ≥ fill+X)** | 327 | **62** | **19%** |

**The two are consistent and the print measure is the superset:** all **55**
bid-touches are print-confirmed (**0** bid-touch was *not* backed by a trade), and
**7** additional events had a buyer lift through `fill+X` without a bid ever
resting there. So print-backing does not shrink the harvest rate — it slightly
**raises** it (17% → 19%) and validates the residency proxy as conservative.

### Both rates by carry-budget bucket

| bucket | banded | bid-touch | print-backed |
|---|---:|---:|---:|
| ≤1h | 100 | 14 (14%) | 17 (17%) |
| ≤2h | 45 | 7 (16%) | 8 (18%) |
| ≤4h | 75 | 10 (13%) | 12 (16%) |
| ≤8h | 56 | 9 (16%) | 9 (16%) |
| >8h | 51 | 15 (29%) | 16 (31%) |

### Both rates by category

| category | banded | bid-touch | print-backed |
|---|---:|---:|---:|
| ATP_CHALL | 152 | 19 | 23 |
| ATP_MAIN | 82 | 20 | 22 |
| WTA_MAIN | 63 | 7 | 7 |
| WTA_CHALL | 30 | 9 | 10 |

## Reading

Requiring an actual buyer-aggressed print at the exit band does not weaken the
harvest story — **62 of 327 banded carries (19%) had a real buyer take at or above
`fill+X` during the wait**, a superset of the 55 residency touches. Four in five
carries still never reach the band and remain true single-leg exposure (favorable-
drifting but unharvested); the harvest, where it happens, is now execution-confirmed.

## Artifacts

`PRINT_BACKED_HARVEST_EVENTS.csv` (per banded event: bucket, held leg, exit band,
residency bid-touch, print-backed) and `PRINT_BACKED_HARVEST_SUMMARY.json`.
