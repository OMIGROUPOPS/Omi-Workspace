# Miss ledger v1 — V23, all 1,608 legs (joint-objective grading)

Analysis seat only. Descriptive. Read-only from V23's replay artifacts (commit
8b50821, `pair_cap_v23_audited_close_20260804/V23_LEG_LEDGER.jsonl.gz` +
`V23_EVENT_LEDGER.jsonl.gz`) and the tape evidence they carry. Supersedes v0's
grading per operator ruling. Per-leg rows in `MISS_LEDGER_V23_V1_1608.csv`; grids
in `MISS_LEDGER_V23_V1_SUMMARY.json`.

## Ruling applied

**Canonical CAPTURED = the joint objective**: completed pair AND sum < 100 AND
**both legs strictly below their own audited close**. Par-only (under 100 but not
both-below-close) is **marginal, never captured**. CAPTURED falls from v0's 386 to
**90** (45 joint pairs).

## Tags

- **CAPTURED** — leg of a joint pair.
- **FIXABLE** — the price/info to act existed on the leg's own tape and went
  unconsumed (receipt cited).
- **ARCH_CEILING** — a reachable price existed but V23's *architecture* blocked it;
  V24 can rework it (cite the V23 mechanism).
- **TAPE_CEILING** — the tape never offered it (cite the absence).
- **SIBLING_FAULT** — an innocent leg (strictly below its own close) whose pair
  failed on the *other* leg; pointer to the culpable leg.

## Conservation

**1,608 = 90 CAPTURED + 945 FIXABLE + 160 ARCH_CEILING + 267 TAPE_CEILING + 146
SIBLING_FAULT.** (sum check: 1608 = 1608.)

| address | n | FIXABLE | ARCH | TAPE | SIBLING | CAPTURED |
|---|---:|---:|---:|---:|---:|---:|
| CAPTURED | 90 | — | — | — | — | 90 |
| L0 source | 90 | 56 | 0 | 34 | — | — |
| L2 shape | 16 | 16 | 0 | 0 | — | — |
| L4 verdict | 116 | 116 | 0 | 0 | — | — |
| L5 anchor-freshness | 149 | 149 | 0 | 0 | — | — |
| L6 pair authority | 50 | 50 | 0 | 0 | — | — |
| L7 placement-cap | 160 | 0 | **160** | 0 | — | — |
| L8 fill | 107 | 79 | 0 | 28 | — | — |
| L9 completion-carry | 512 | 388 | 0 | 124 | — | — |
| L10 grading (rode ≥100) | 22 | 13 | 0 | 9 | — | — |
| **L-AIM** (bought above own landing) | 150 | 78 | 0 | 72 | — | — |
| **SIBLING_FAULT** | 146 | — | — | — | 146 | — |
| **TOTAL** | **1608** | **945** | **160** | **267** | **146** | **90** |

## The 148 marginal pairs — culpability assigned

The 148 under-par-but-not-joint pairs (296 legs) are split per pair by which
side(s) failed the both-below-close test:

- **L-AIM (150 legs)** — the culpable leg(s), bought **at or above their own
  audited close** ("above own landing"). Tagged **FIXABLE (78)** when a
  strictly-below-close price existed on that leg's own tape (a better entry was
  reachable, receipt cited), **TAPE_CEILING (72)** when no below-close price ever
  printed. (150 > 148 because 2 pairs had both legs above their close.)
- **SIBLING_FAULT (146 legs)** — the innocent leg, strictly below its own close;
  it did its job, the pair failed on the sibling. Each row points to its pair's
  culpable leg. Not independently in the build queue — it is fixed by fixing L-AIM.

90 CAPTURED + 296 (L-AIM+SIBLING) + 22 (L10) = 408 completed-pair legs.

## ARCH_CEILING cite — L7 placement-cap (160)

V23's pair cap (`pair_reference_cents`) is **a function of leg-1's fill**: once
leg-1 credits, the leg-2 cap is the joint target minus leg-1, and terminal
`PAIR_CAP_BELOW_CURRENT_LIVE_BID_UNREACHABLE_WITHOUT_CHASING` fires when that cap
sits below the live bid. A reachable price existed on the tape (every one of the
160 carries a `maker_floor`); V23 declined to chase above its own cap. That is an
**architectural** block, not a tape absence — V24 can rework the cap/chase rule.
So all 160 move from v0's "unaddressable ceiling" into the V24-addressable column.

## V24-addressable = FIXABLE + ARCH_CEILING = 1,105, per layer (descending)

This combined column is what V24 can touch.

| rank | address | V24-addressable | tag |
|---:|---|---:|---|
| 1 | L9 completion-carry | **388** | FIXABLE |
| 2 | L7 placement-cap | **160** | ARCH_CEILING |
| 3 | L5 anchor-freshness | 149 | FIXABLE |
| 4 | L4 verdict | 116 | FIXABLE |
| 5 | L8 fill | 79 | FIXABLE |
| 6 | L-AIM (bought above landing) | 78 | FIXABLE |
| 7 | L0 source | 56 | FIXABLE |
| 8 | L6 pair authority | 50 | FIXABLE |
| 9 | L2 shape | 16 | FIXABLE |
| 10 | L10 grading | 13 | FIXABLE |
| | **TOTAL** | **1105** | |

Not addressable: **TAPE_CEILING 267** (the tape never offered it — L9 124, L-AIM
72, L0 34, L8 28, L10 9) and **SIBLING_FAULT 146** (fixed via the culpable leg).
1105 + 267 + 146 + 90 = 1608.

### V24-addressable per layer × category

| layer | ATP_CHALL | ATP_MAIN | WTA_MAIN | WTA_CHALL | TOT |
|---|---:|---:|---:|---:|---:|
| L9 carry | 187 | 76 | 69 | 56 | 388 |
| L7 cap (ARCH) | 47 | 39 | 37 | 37 | 160 |
| L5 anchor | 82 | 16 | 26 | 25 | 149 |
| L4 verdict | 53 | 16 | 31 | 16 | 116 |
| L8 fill | 47 | 12 | 8 | 12 | 79 |
| L-AIM | 31 | 25 | 13 | 9 | 78 |
| L0 source | 36 | 2 | 12 | 6 | 56 |
| L6 pair | 30 | 5 | 3 | 12 | 50 |
| L2 shape | 7 | 3 | 1 | 5 | 16 |
| L10 grading | 3 | 0 | 7 | 3 | 13 |

By region: **le25 193 · 26_50 382 · 51_75 366 · ge76 164** (sum 1105).

### Top V24-addressable cells (layer × category × region)

| n | layer | category | region |
|---:|---|---|---|
| 77 | L9 carry | ATP_CHALL | 51_75 |
| 54 | L9 carry | ATP_CHALL | 26_50 |
| 41 | L9 carry | ATP_MAIN | 51_75 |
| 30 | L4 verdict | ATP_CHALL | 26_50 |
| 29 | L9 carry | ATP_CHALL | le25 |
| 29 | L5 anchor | ATP_CHALL | 51_75 |
| 27 | L9 carry | ATP_CHALL | ge76 |
| 24 | L7 cap | ATP_MAIN | 26_50 |
| 23 | L9 carry | WTA_MAIN | 26_50 |
| 23 | L9 carry | WTA_CHALL | 26_50 |

(Full ranking in the JSON; all cells sum to 1105.)

## Reading

Under joint-objective grading, V23 captures **90 of 1,608** legs. Of the rest,
**1,105 (69%) are V24-addressable** — 945 where V23 held the info and did not act,
plus 160 where V23's leg-1-coupled pair cap architecturally blocked a reachable
price. The build queue is led by completion (L9, 388) and the pair-cap rework
(L7, 160), then anchor-freshness (149) and verdict (116). Genuinely out of reach:
267 TAPE_CEILING legs (no price ever printed) and 146 SIBLING_FAULT legs (fixed by
fixing their culpable partner). The L-AIM address is new in v1: 150 legs bought at
or above their own landing, half of them (78) with a below-close price they could
have taken.

## Artifacts

`MISS_LEDGER_V23_V1_1608.csv` (one row per leg: address, tag, sibling pointer,
evidence) and `MISS_LEDGER_V23_V1_SUMMARY.json`.
