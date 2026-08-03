# V11 non-action autopsy — the 896 legs V11 never placed on the 804

Analysis seat only. Descriptive. No policy, scorer, or live/replay code was
changed or invoked. Boundary: `docs/research/window1/WINDOW1_TWO_SEAT_BOUNDARY.md`.

Source: the frozen `V11_NON_ACTION_DECISION_TRACE_896.jsonl.gz`
(SHA-256 `0147a4ec2952a772fad528984a20781df625517671233dafd0f88dc35950335a`,
896 legs, decompresses to 896 JSONL rows). Ask-return behaviour is read from the
per-leg Window-1 quote tapes (`OMI-Window1-private/fit-local/ticks`, 1,608
`*.csv.gz`). Everything here regenerates from
`arb-executor/analysis/second_seat/build_v11_non_action_mechanism_audit.py`.

## Finding

V11 placed nothing on any of the 896 legs (V17 acted on exactly one). Yet **860
of the 896 carried an achievable, print-backed floor, every one of them
par-passing (floor ≤ 97), and 716 of them at or below the leg's own Window-1
close.** The refusals were not the price being gone: on **728 of the 806 legs
whose tape could be scanned (90.3%) the refused floor came back at ten-second
executable dwell** — a median of **3** separate returns totalling a median of
**11,437 seconds (3.2 hours)** at or below the refused price — and on **507
(62.9%) the ask went strictly lower afterward.**

The pricer reports nine different terminal gate names for these refusals. Grouped
by mechanism instead of by gate, one structural defect dominates and it is **not**
one of the five already fixed by hand: at the first instant each leg had an
actionable floor, **the synthetic-sibling veto was the binding constraint on 500
of the 896 (56%).** The five hand-fixes, even fully applied, leave **596 of 896
(66.5%)** still refused, because those legs carry a residual mechanism the fixes
never touch. The single most common terminal excuse — "current ask is above the
observed low," 283 legs — is largely a **symptom**: 183 of those 283 were, at
their first actionable floor, held by the synthetic-sibling veto while the
unattended tape drifted up off the low.

## Clock convention

`t_minus_scheduled` counts back from the scheduled start; `t_minus_bell` from the
observed bell. Challenger bells are largely unobserved in this population (the
trace stores a sentinel where absent), so bell figures are reported only over the
subset where a real bell exists. ET = UTC−4 (EDT) for the July-2026 window.

## Population and coverage

| | legs |
|---|---:|
| non-action legs (V11 acted on 0; V17 on 1) | 896 |
| with an achievable print-backed floor | 860 |
| **fully covered by the five hand-fixed defects** | **300 (33.5%)** |
| **carry ≥1 residual (un-fixed) mechanism** | **596 (66.5%)** |

"Covered" means every binding predicate at the leg's first actionable floor maps
to one of the five hand-fixes. A leg with a floor the shape organ *accepted* but
the sibling gate *vetoed* is **not** covered, however many hand-fixes touch its
other predicates.

## Mechanism catalog

Grouped by the binding predicate set at the first actionable floor, not by the
terminal gate name. `incidence` = legs where the mechanism is *a* binding
constraint (legs can bind several); `primary` = legs where it is *the* binding
residual.

### Already fixed by hand (five)

| # | mechanism | binding predicate | incidence | primary |
|---|---|---|---:|---:|
| 1 | stable-ask-refused-for-no-transition | `STABLE_SIGNING_SUPPORT_UNPROVEN` | 220 | 100 |
| 2 | floor-on-first-descent | `SHAPE_VERDICT_STILL_LOWER` (descent-count signing law) | 228 | 137 |
| 3 | stale-action-book | `NO_FRESH_OWN_BOOK_RECEIPT` / `OWN_MICRO_POSITION_UNOBSERVED` | 19 | 19 |
| 4 | class-cannot-express-member-behaviour | `SHAPE_VERDICT_NOT_UNANIMOUS_FLOOR` with an empty/all-UNKNOWN cell | 332 | 44 |
| 5 | verdict-lagging-tape | `CURRENT_ASK_ABOVE_OBSERVED_LOW` | 34 | 19 |

Two mappings are asserted, not self-evident, and are flagged: `SHAPE_VERDICT_STILL_LOWER`
is treated as the surface the *floor-on-first-descent* fix operates on (the
descent-count signing law); `SHAPE_VERDICT_NOT_UNANIMOUS_FLOOR` is split — an
empty or all-UNKNOWN cell is a library gap (#4, covered), a cell that carries
both FLOOR and LOWER is genuine disagreement (a new mechanism, below).

### Not covered — new mechanisms (named)

- **synthetic-sibling-veto** — *incidence 500, primary 500.* A floor every other
  organ has already accepted is withheld for an independent reading of the paired
  leg that the pricer never takes: it prices the sibling from its own `100 − p`
  mirror instead of the sibling's book, so the "independently observed sibling
  direction" the gate demands can never arrive.

- **no-formed-book-source-gap** — *incidence 90, primary 90.* No in-window formed
  book or lawful print ever existed, so no price organ could run — a non-decision
  by data absence, not a refusal. (These have no book to scan; 54 still carry a
  floor from the objective record.)

- **class-splits-floor-vs-lower** — *incidence 42, never primary alone.* The cell
  exists, but its surviving shapes carry both FLOOR and LOWER for the same member,
  so unanimity is structurally unreachable and the class abstains on its own
  internal disagreement. It never surfaces as the *primary* residual only because
  every one of the 42 is also under the synthetic-sibling veto.

- **microstructure-nonexecutable** — *incidence 21, primary 6.* The observed low
  never cleared the pricer's own liquidity gates (ten-second dwell, five-lot top).
  This is the one bucket where standing pat was defensible: the price was not
  genuinely executable.

## Gate name vs mechanism — the reconciliation

The pricer's *terminal* excuse and the *first-actionable-moment* binding mechanism
diverge sharply. Rows are terminal gates; columns are the first-moment mechanism.

| terminal gate (pricer's excuse) | legs | SIB | DESC | STABLE | LIBGAP | LAG | SRC | MICRO |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| FLOOR_CONSENSUS_BUT_CURRENT_ASK_IS_ABOVE_OBSERVED_LOW | 283 | **183** | 17 | 45 | 24 | 12 | 0 | 2 |
| ALL_SURVIVING_SHAPES_SAY_LOWER | 183 | 66 | **97** | 8 | 7 | 5 | 0 | 0 |
| FLOOR_CONSENSUS_BUT_SIBLING_DIRECTION_NOT_INDEP_OBSERVED | 147 | **126** | 5 | 9 | 4 | 2 | 0 | 1 |
| FLOOR_CONSENSUS_BUT_STABLE_SAME_PRICE_ASK_LACKS_SUPPORT | 110 | **67** | 6 | 30 | 6 | 0 | 0 | 1 |
| SOURCE_UNAVAILABLE | 90 | 0 | 0 | 0 | 0 | 0 | **90** | 0 |
| SURVIVING_SHAPES_DISAGREE_OR_LIBRARY_GAP | 74 | **53** | 12 | 6 | 2 | 0 | 0 | 1 |
| FLOOR_CONSENSUS_BUT_MICRO_MICRO_NOT_READY | 6 | 3 | 0 | 2 | 0 | 0 | 0 | 1 |
| OBSERVED_DESCENT_OUTSIDE_SURVIVING_SHAPE_TRAINING_SUPPORT | 2 | 1 | 0 | 0 | 1 | 0 | 0 | 0 |
| FLOOR_CONSENSUS_AWAITING_FRESH_OWN_BOOK_RECEIPT | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 |

SIB=synthetic-sibling-veto, DESC=floor-on-first-descent (descent law),
STABLE=stable-ask, LIBGAP=class-cannot-express, LAG=verdict-lagging-tape,
SRC=source-gap, MICRO=microstructure-nonexecutable.

Only **12 of the 283** "current ask above observed low" refusals are genuinely
tape-lag at the first actionable moment; **183** are the synthetic-sibling veto
holding the sign while the price walks off the low. Grouping by gate name would
have reported tape-lag as the leading defect (283) and hidden the sibling veto;
grouping by mechanism shows the reverse.

## Regret gauge

Achievable print-backed floor vs nothing = the full regret; each leg attributed to
its primary mechanism. `≤cls` = floor at or below own Window-1 close; `≤97` =
par-passing; `ret≥10` = refused floor later returned at ≥10s dwell; `wentLo` = ask
later fell below the refused floor.

| primary mechanism | legs | floor-backed | med floor | ≤cls | ≤97 | ret≥10 | wentLo |
|---|---:|---:|---:|---:|---:|---:|---:|
| synthetic-sibling-veto | 500 | 500 | 55 | 411 | 500 | 452 | 316 |
| floor-on-first-descent | 137 | 137 | 40 | 117 | 137 | 120 | 81 |
| stable-ask-refused-for-no-transition | 100 | 100 | 55 | 88 | 100 | 97 | 66 |
| no-formed-book-source-gap | 90 | 54 | 55 | 44 | 54 | 0* | 0* |
| class-cannot-express-member-behaviour | 44 | 44 | 41 | 36 | 44 | 44 | 31 |
| verdict-lagging-tape | 19 | 19 | 48 | 15 | 19 | 10 | 8 |
| microstructure-nonexecutable | 6 | 6 | 56 | 5 | 6 | 5 | 5 |
| **all** | **896** | **860** | **51** | **716** | **860** | **728** | **507** |

*source-gap legs have no book to scan.

The floors sit a median of ~1 cent below the leg's own close: these are not deep
directional discounts, they are the maker touches the operation exists to capture.
The regret is 860 never-taken par-passing maker fills, not foregone edge.

## Post-refusal ask return — "did the price come back?"

Per primary mechanism, over the scanned legs: `ret%` = share whose refused floor
returned at ≥10s dwell; medians over the returners.

| primary mechanism | scanned | ret% | med returns | med sec ≤ floor | med longest return | wentLo% |
|---|---:|---:|---:|---:|---:|---:|
| synthetic-sibling-veto | 500 | 90% | 3 | 12,664 | 8,701 | 63% |
| floor-on-first-descent | 137 | 88% | 3 | 7,944 | 5,085 | 59% |
| stable-ask-refused-for-no-transition | 100 | 97% | 4 | 10,510 | 6,733 | 66% |
| class-cannot-express-member-behaviour | 44 | 100% | 4 | 13,558 | 9,378 | 70% |
| verdict-lagging-tape | 19 | 53% | 4 | 13,260 | 7,267 | 42% |
| microstructure-nonexecutable | 6 | 83% | 1 | 6,731 | 6,731 | 83% |

verdict-lagging-tape is the only mechanism whose refused price mostly did **not**
come back (53% return, 42% went lower) — consistent with it being the genuine
"the low left the tape" case. Every other mechanism refused prices that returned
for hours.

## Both clocks, per mechanism (median minutes)

| primary mechanism | med T-scheduled | bell observed | med T-bell |
|---|---:|---:|---:|
| synthetic-sibling-veto | 457.5 | 164 | 309.0 |
| floor-on-first-descent | 265.4 | 44 | 246.3 |
| stable-ask-refused-for-no-transition | 456.6 | 30 | 309.9 |
| no-formed-book-source-gap | — | 0 | — |
| class-cannot-express-member-behaviour | 477.8 | 14 | 320.6 |
| verdict-lagging-tape | 185.6 | 8 | 941.4 |
| microstructure-nonexecutable | 475.0 | 1 | 6.8 |

The refusals are early: most binding decisions land 4–8 hours before the scheduled
start, with hours of tape left in which the refused floor returns.

## Per price region and per category (never flattened)

Price region (legs / floor-backed / ≤close / scanned / returned≥10s / wentLo / median floor):

| region | legs | floor | ≤close | scan | ret≥10 | wentLo | med floor |
|---|---:|---:|---:|---:|---:|---:|---:|
| le25 | 175 | 140 | 109 | 126 | 112 | 76 | 16 |
| 26_50 | 287 | 287 | 243 | 271 | 249 | 185 | 38 |
| 51_75 | 297 | 297 | 254 | 282 | 254 | 179 | 62 |
| ge76 | 137 | 136 | 110 | 127 | 113 | 67 | 83 |

Category:

| category | legs | floor | ≤close | scan | ret≥10 | wentLo | med floor |
|---|---:|---:|---:|---:|---:|---:|---:|
| ATP_CHALL | 438 | 434 | 368 | 398 | 369 | 294 | 50 |
| ATP_MAIN | 158 | 146 | 123 | 144 | 120 | 69 | 50.5 |
| WTA_MAIN | 167 | 147 | 132 | 137 | 117 | 60 | 51 |
| WTA_CHALL | 133 | 133 | 93 | 127 | 122 | 84 | 56 |

Per-mechanism × category and × region matrices are in `MECHANISM_SUMMARY.json`.

## Frontier — how many sat on completable games

A game is completable at threshold *T* when both sides' achievable floors sum to
≤ *T*. Computed over the **259 events whose both never-placed legs carry a known
floor in the trace** (the other 342 events contribute a single non-action leg;
their sibling is not in the never-placed set, so pair completion needs the
placed/other side, which this trace does not carry).

| pair floor sum | events | legs | by region (le25/26_50/51_75/ge76) | by cat (ATPc/ATPm/WTAm/WTAc) |
|---|---:|---:|---|---|
| ≤ 93 | 9 | 18 | 3/7/4/4 | 8/0/0/10 |
| ≤ 95 | 12 | 24 | 3/10/7/4 | 14/0/0/10 |
| ≤ 97 | 21 | 42 | 6/16/13/7 | 28/4/0/10 |
| < 100 | 88 | 176 | 28/63/57/28 | 96/50/14/16 |

**176 of the 896 legs sat on games where both never-placed sides could have been
bought together for under 100** — a guaranteed-completion pair the operation
declined on both legs — and **42 of those on games completable at par (≤ 97).**

## Fix-regression questions

1. Does the sibling organ read the paired leg's own book, or is 500-leg
   synthetic-sibling-veto still pricing the sibling from `100 − p`? This is the
   dominant residual; the other four fixes cannot reach it.
2. For the 183 "current-ask-above-observed-low" terminals that were sibling-vetoed
   at their first floor: does resolving the sibling let the sign fire before the
   ask leaves the low, or does the tape-lag gate then become binding?
3. On the 137 descent-law refusals, 56 never went lower (the class insisted LOWER
   and was wrong). Does the descent-count law expire, or defer forever?
4. Do the 90 source-gap legs have any lawful in-window book at all, or is this an
   ingestion boundary rather than a pricing one?
5. Does any proposed placement preserve chronology, so a receipt recognizing the
   floor's return cannot fill the action it creates?

## Machine-readable artifacts

Under `.claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/`:

- `V11_NON_ACTION_MECHANISM_LEDGER_896.csv` — one enriched row per leg: mechanism,
  coverage, book at decision, both clocks, floor/close/objective, and the full
  ask-return metrics.
- `MECHANISM_SUMMARY.json` — every table above, plus per-mechanism × category and
  × region matrices.
- `AUDIT_RECEIPT.json` — source hashes, tape provenance, method, conservation.

Regenerate with `arb-executor/analysis/second_seat/build_v11_non_action_mechanism_audit.py`.
