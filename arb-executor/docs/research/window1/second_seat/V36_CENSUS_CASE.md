# The census case, fully opened — V36 (bfde0d8)

Analysis seat only. Read-only. V36 `v36_state_directional_rest_mature_floor`, certified
tapes, `prints.jsonl`. Machine artifact:
`.claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/V36_CENSUS_CASE.json`.
**The 548 census pairs are the machine's claimed book. This opens every assumption before
anyone acts on it.**

## (1) The offer — three rulers (over all 804, per tier)

| ruler | ≤93 | ≤95 | ≤97 | <100 |
|---|--:|--:|--:|--:|
| **(a) close-anchored print** (both sides printed below own pre-bell close, sum at tier) | 483 | 488 | 492 | 493 |
| **(b) floor-sum ladder** (each leg's deepest print-backed price summed — the tape's bottoms) | 245 | 346 | 503 | **711** |
| **(c) near-miss-adjusted floor-sum** (deepest price a 1c-under-walked-path bid intercepts) | 245 | 346 | 503 | **711** |

**(b) and (c) are identical** — in V36 the print-backed floor *is* the tape bottom, so the
near-miss adjustment buys nothing over the raw floor-sum. The rulers diverge sharply from
each other and from the strict book: close-anchored (493) counts games where a trade merely
printed below close (loose), floor-sum (711) sums absolute bottoms (optimistic).
**Headline provenance:** the operator's **680** is the near-miss/offer ruler read
*any-price* on the full-lawful ceiling (its `strict_sequential_any_price`); **362-class**
is the floor-sum family; **104-class** is the tightest close-anchored/independent-touch
read. The point of the table: *the same book is 104 or 711 depending purely on which ruler
you quote.*

## (2) The census book's composition — 548 = 267 + 281

**267 strict-real** (both legs strict-credited) + **281 conversion-assumed** (≥1 leg on
`CENSUS_PRICED_ONE_CENT_RESIDENCY_CONVERSION`); **355 assumed conversion fills** in total.
(Operator framing 270/278; the 3-pair difference is strict pairs the census ledger did not
re-complete.) Every assumed-fill row — leg, rest level, near-miss print
(price/size/ts/aggressor), rule, pair margin — is in the artifact (`part2_composition.rows`).

**Two structural flags in the 355 conversions:**
- **71 (20%) rest on a BUYER-aggressed near-miss** — a buyer *lifting an ask*, which a
  standing *bid* is never filled by. These conversions are invalid at the mechanism level
  (e.g. CHAJON·CHA credited 40 against a BUYER print at 29; GEOMAG·MAG 84 vs BUYER 75).
- **49 (14%) credit an entry more than 1¢ off the near-miss print** — violating the very
  1c-residency rule the conversion is named for.

## (3) The money — what each book EARNS (not completes)

Per-pair margin = 100 − combined. Kalshi trading fee = `ceil(0.07·p·(1−p))` cents/contract
per fill (maker/resting fills exempt → **net_taker** charges TAKER legs only; **net_all**
charges both).

| book | pairs | gross median | gross total | net_taker total | net_taker <0 | net_all total | net_all <0 |
|---|--:|--:|--:|--:|--:|--:|--:|
| strict-real | 267 | 2¢ | 1,006¢ | 442¢ ($4.42) | 127 (48%) | — | — |
| **full census** | 548 | 2¢ | 2,317¢ ($23.17) | **1,387¢ ($13.87)** | **212 (39%)** | 311¢ ($3.11) | **395 (72%)** |
| assumed only | 281 | 2¢ | 1,311¢ | 945¢ | 85 (30%) | — | — |

**The fees-immaterial ruling is void — here is the arithmetic.** The median census pair
grosses **2¢**. A single taker fee on a leg near 50¢ is `ceil(0.07·0.5·0.5)` = **2¢** —
it erases the whole pair. Result: **net-taker median 0¢**, and **212 of 548 pairs (39%)
lose money** even with makers exempt. Charge both legs (no maker exemption) and the median
pair is **−2¢** and **395 of 548 (72%) are net-negative**. The entire 804-game census book
earns **$13.87 net** at 1 lot (taker-only) or **loses on 72% of pairs** at both-leg fees.

## (4) Sensitivity — census value at conversion X%

| conversion | gross 1-lot | gross 5-lot | **net(taker) 1-lot** | **net(taker) 5-lot** |
|---|--:|--:|--:|--:|
| 25% | $13.34 | $66.69 | $6.78 | $33.91 |
| 50% | $16.61 | $83.08 | $9.14 | $45.73 |
| 75% | $19.89 | $99.46 | $11.51 | $57.54 |
| 100% | $23.17 | $115.85 | **$13.87** | **$69.35** |

Even at **100% perfect conversion**, the whole census book is worth **$13.87 net at 1 lot
/ $69.35 at 5 lot** across all 804 games — and that ignores the 20% invalid buyer-side
conversions and slippage. This is not a book anyone should act on for the dollars.

## (5) The verification spec — what proves or kills the conversion

- **Measure:** at each armed standing level, count **FILLS** (a seller-aggressed print
  actually swept our resting bid) vs **NEAR-MISSES** (a seller print landed 1–3¢ above the
  rest, no sweep). Conversion rate = fills / (fills + near-misses). The census assumes
  ~100%.
- **Read law:** per category, require **≥30 completed test games** and **≥200 armed levels**
  before ruling.
- **The kill number:** break-even conversion = fee / gross-margin per assumed pair. With a
  median assumed margin of **2¢** and a ~2¢ taker fee, **break-even is ≥100% — i.e. there is
  no positive-EV conversion rate after a single taker fee.** The census book is **refuted at
  the first fee-bearing fill** on a ≤2¢-margin pair. On a *gross* basis (fees waived), kill
  at conversion **< 50%** (below which even the gross assumed value halves under the 680
  offer). Any live read showing fill/(fill+near-miss) below the kill number refutes the book.

## Conservation

548 census = 267 strict-real + 281 conversion-assumed; 355 conversion fills (284 SELLER,
71 BUYER-invalid; 49 violate 1c). Money: strict 267 / census 548 / assumed 281 pairs.
Gross totals 1,006 / 2,317 / 1,311¢. Net-taker <0: 127 / 212 / 85 pairs; net-all <0 (census)
395/548. Sensitivity spans $6.78–$13.87 net at 1 lot, 25–100% conversion.
