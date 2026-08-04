# Miss ledger v0 — V23, all 1,608 legs

Analysis seat only. Descriptive. Read-only attribution from V23's replay artifacts
(commit 8b50821, `pair_cap_v23_audited_close_20260804/V23_LEG_LEDGER.jsonl.gz` +
`V23_EVENT_LEDGER.jsonl.gz`) and the tape evidence those ledgers carry (each
`traded_low_proof` holds true-print receipts; `qualifying_ask_floor`, `maker_floor`,
`seller_aggressed_floor`, `pair_reference` are tape-derived). Every leg gets exactly
one row. Per-leg rows in `MISS_LEDGER_V23_1608.csv`; grids in
`MISS_LEDGER_V23_SUMMARY.json`.

## Layer stack and tag

Each leg is **CAPTURED** (a leg of a completed pair that cashed under par, <100) or
it died at the first layer it failed. The tag on each dead leg:
**FIXABLE** — the information to act existed on that leg's own tape at decision time
(cite the floor / print / receipt available and unconsumed) — or **CEILING** — it
did not exist (cite the absence).

## Conservation

**1,608 = 386 CAPTURED + 867 FIXABLE + 355 CEILING.** (CAPTURED carries no
fix/ceiling tag.) Every table below sums to this.

| layer | n | FIXABLE | CEILING |
|---|---:|---:|---:|
| CAPTURED | 386 | — | — |
| L0 source | 90 | 56 | 34 |
| L1 book | 0 | 0 | 0 |
| L2 shape identity | 16 | 16 | 0 |
| L3 floor formation | 0 | 0 | 0 |
| L4 verdict | 116 | 116 | 0 |
| L5 anchor-freshness | 149 | 149 | 0 |
| L6 pair authority | 50 | 50 | 0 |
| L7 placement-cap | 160 | 0 | 160 |
| L8 fill | 107 | 79 | 28 |
| L9 completion-carry | 512 | 388 | 124 |
| L10 grading | 22 | 13 | 9 |
| **TOTAL** | **1608** | **867** | **355** |

L1 (book formation) and L3 (floor formation) are unpopulated: book-absence folds
into L0 source, and floor-formation failures present downstream as L2/L4. The
CAPTURED/L10 boundary is the par law (completed & <100 vs completed & ≥100); under
the stricter both-legs-below-audited-close joint objective only 45 of 204 completed
pairs pass — a quality gauge, not a capture boundary.

## The build queue — FIXABLE mass per layer, sorted descending

| rank | layer | FIXABLE | what the tape already offered |
|---:|---|---:|---|
| 1 | **L9 completion-carry** | **388** | sibling maker floor reachable and pair sum <100 — the pair was completable, completion never fired |
| 2 | **L5 anchor-freshness** | **149** | a qualifying / maker floor was print-backed while the freshness/anchor gate stalled |
| 3 | **L4 verdict** | **116** | a qualifying ask floor formed; the shape verdict withheld the sign |
| 4 | L8 fill | 79 | a seller aggressed to the resting price — a fill was available and missed |
| 5 | L0 source | 56 | a reachable maker floor was present despite the source flag |
| 6 | L6 pair authority | 50 | the sibling's own tape carried a floor; the pair direction was observable, unconsumed |
| 7 | L2 shape identity | 16 | a reachable floor was on the tape the class could not name |
| 8 | L10 grading | 13 | a deeper reachable maker floor existed that would have cleared par |
| | **TOTAL** | **867** | of 1,222 dead legs (355 CEILING) |

**L9 completion-carry (388) is the single largest fixable mass** — the miss-ledger
form of the executable-ceiling finding: legs whose pair was completable but never
jointly captured. Next are L5 anchor-freshness (149) and L4 verdict (116); these
three are 653 of 867 fixable legs (75%).

## FIXABLE per layer × category

| layer | ATP_CHALL | ATP_MAIN | WTA_MAIN | WTA_CHALL | TOT |
|---|---:|---:|---:|---:|---:|
| L9 carry | 187 | 76 | 69 | 56 | 388 |
| L5 anchor | 82 | 16 | 26 | 25 | 149 |
| L4 verdict | 53 | 16 | 31 | 16 | 116 |
| L8 fill | 47 | 12 | 8 | 12 | 79 |
| L0 source | 36 | 2 | 12 | 6 | 56 |
| L6 pair | 30 | 5 | 3 | 12 | 50 |
| L2 shape | 7 | 3 | 1 | 5 | 16 |
| L10 grading | — | — | — | — | 13 |

FIXABLE by region: **le25 150 · 26_50 287 · 51_75 293 · ge76 137** (sum 867). The
mass sits in the mid regions (26_50, 51_75) and in ATP_CHALL, matching where the
book is densest.

## Top FIXABLE cells (layer × category × region), sorted descending

| FIXABLE | layer | category | region |
|---:|---|---|---|
| 77 | L9 carry | ATP_CHALL | 51_75 |
| 54 | L9 carry | ATP_CHALL | 26_50 |
| 41 | L9 carry | ATP_MAIN | 51_75 |
| 30 | L4 verdict | ATP_CHALL | 26_50 |
| 29 | L9 carry | ATP_CHALL | le25 |
| 29 | L5 anchor | ATP_CHALL | 51_75 |
| 27 | L9 carry | ATP_CHALL | ge76 |
| 23 | L9 carry | WTA_MAIN | 26_50 |
| 23 | L9 carry | WTA_CHALL | 26_50 |
| 22 | L8 fill | ATP_CHALL | 26_50 |

(Full 40-cell ranking in the JSON; all cells sum to 867.)

## The CEILING — structurally unaddressable (355)

| layer | CEILING | the cited absence |
|---|---:|---|
| L7 placement-cap | 160 | the pair cap sat below the live bid; only a chase above the cap could fill |
| L9 completion-carry | 124 | the sibling was never completable (no sub-100 pair existed on tape) |
| L0 source | 34 | no in-window formed book or lawful print |
| L8 fill | 28 | no seller aggressed to the resting price (dead book) |
| L10 grading | 9 | no deeper reachable price than entry; the pair rode ≥100 |

L7 (160) is the largest ceiling: the pair-cap arithmetic put the target below what
the market ever offered — not a consumption failure, a structural one.

## Reading

Of the 1,222 legs V23 did not capture, **867 (71%) are FIXABLE** — the information
to place or complete existed on the leg's own tape and went unconsumed — and 355
are a genuine CEILING. The build queue is led by completion (L9, 388), anchor-
freshness (L5, 149) and verdict (L4, 116). This is v0: the layer assignment is
monotone-first-failure and the FIXABLE test is per-layer tape-presence with a cited
receipt; each row is auditable in the CSV.

## Artifacts

`MISS_LEDGER_V23_1608.csv` (one row per leg: layer, tag, evidence citation) and
`MISS_LEDGER_V23_SUMMARY.json` (all grids).
