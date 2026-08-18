# GATE-POLICY EVALUATION IN LIVE COORDINATES [ANALYTICAL_ESTIMATE · MEASUREMENT ONLY]

Analysis seat only. **No selection — the operator rules the pick.** Blocks further wiring by measurement,
not by proposal. Full grid both clocks: `GATE_POLICY_EVAL_LIVE_COORDS.{csv,json}` (30 gates × 2 clocks).

**Corpus & instrument.** 582 simulable role legs (of 596 on verified spans @ `c0056976`; 14 lack an onset or
an open, excluded and counted). Instrument: the published rule @ `e269779b` with the corrected anchor —
**parity now exact @ `a059264d` (V52q: 139,430/139,430 ungated calls)**. Binding rule simulated as the
runtime does it: **bind at the first gate crossing with a directional call · hold unless the instrument
itself flips (re-bind, flip counted) · act per the V52p/q policy** — DOWN binds target open − the
frequency-weighted category down-depth aggregate recomputed from the V52p receipt's own component rows
(ATP_MAIN 8.67¢ · ATP_CHALL 8.37¢ · WTA_MAIN 8.90¢ · WTA_CHALL 10.21¢); UP binds are immediate. Coordinate
zero = max(canonical leg onset, game formation end) — both live-knowable. Gates keyed **only** to
live-knowable coordinates: minutes since onset (MIN) · post-onset trade count (TRD) · cumulative absolute
travel (TRV) · combinations.

## The tautology, named first

**Held-at-end accuracy is 100.0% at every gate on verified spans — by construction, not by merit.** The
held call at span end and the role truth are both the sign of the same end-of-span drift. It appears in the
CSV as the constant it is. **The policy-grain accuracy is FIRST-BIND accuracy** — the role actually acted
on at the moment capital moves — and the flip rate is the price of the hold-until-flip rule. All scoring
below is first-bind.

## The frontier — coverage vs first-bind accuracy (verified spans)

13 of 30 gates are non-dominated; 17 dominated. The frontier, top to bottom:

| gate | coverage | first-bind acc | flip rate | bind median |
|---|--:|--:|--:|--:|
| MIN0 ≡ TRV2 (bind at first call) | 94.2% | 90.3% | 11.7% | 43 min |
| TRD3 | 94.0% | 93.2% | 8.4% | 79 min |
| **TRD5** | **92.4%** | **94.8%** | 6.5% | 120 min |
| **TRV6** | **91.1%** | **94.9%** | 6.6% | 107 min |
| MIN30+TRV6 | 89.9% | 95.6% | 5.7% | 142 min |
| MIN60+TRV6 | 87.6% | 95.9% | 5.3% | 167 min |
| MIN15+TRD10 / MIN30+TRD10 | 86.1 / 85.9% | 96.0 / 96.2% | 5.0 / 4.8% | ~234 min |
| MIN30+TRD20 / MIN60+TRD20 | 70.3 / 68.9% | 96.3 / 96.8% | 4.4 / 4.0% | ~365 min |
| **MIN120+TRD20** | **66.7%** | **97.4%** | 3.1% | 379 min |
| TRD100 | 26.8% | 98.7% | 1.3% | 736 min |

**Dominant region:** the whole span-fraction-free knee between TRD3 and MIN60+TRV6 — ~87–94% coverage at
93–96% first-bind accuracy, flips under 9%. **Dominated region (named):** every pure-minutes gate above
MIN0 (MIN5…MIN240 all dominated — time alone buys accuracy slower than trades or travel do), TRD10–TRD50
alone, TRV10/TRV15 alone, and every tested combo containing TRV4 or TRD10+TRV4. The frontier's whole width
is ~8 accuracy points for ~67 coverage points — it is **shallow**: past TRD5/TRV6, each accuracy point
costs ~10+ points of coverage.

## The downstream that matters — and it is gate-INSENSITIVE

- **DOWN binds: the depth target is kissable on only 29–38% of binds at EVERY gate** (floor-gap median
  −2¢: the category-aggregate target sits 2¢ below the reachable pre-bell floor; p25 −4¢). Gating harder
  does not fix aiming — **the averages-can't-aim-depth proof extends to category aggregates at policy
  grain.** (Best cell: TRV15 at 38.4% kissable — bought with coverage collapsing to 59%.)
- **UP binds: the early catch is spent before any gate opens.** Catch gap at bind: median 4–5.5¢ above the
  open at every gate; open-price still-available afterward on only 10–24% of up-binds, falling as gates
  tighten. Down-binds' first-bind accuracy is uniformly higher than up-binds' (93.9–98.8% vs 87.4–98.8%)
  — the down side is the readable side, as the taxonomy said; the up side is the perishable side.

## The live-fidelity delta at policy grain (composite clock @ `620fe4c1` beside verified spans)

| gate | Δ coverage (live − verified) | Δ first-bind acc |
|---|--:|--:|
| MIN0 | −12.1 | −0.1 |
| TRD5 | −14.2 | **+0.4** |
| TRV6 | −18.5 | **+0.4** |
| MIN120 | −20.7 | −1.2 |
| TRD20 | −28.9 | +0.2 |
| MIN120+TRD20 | −31.5 | −0.4 |

**The live clock costs coverage, never correctness** — first-bind accuracy moves at most 1.2 points at any
gate, while coverage loses 12–31 points (trade-count-heavy gates starve worst: the live span truncates
before counts accumulate). The live clock's early bias (median −4,020 s @ `620fe4c1`) converts to fewer
binds, not wronger binds.

## Three cleanest gate candidates — receipts only, no selection

1. **TRD5** (5 post-onset trades): cov 92.4% · first-bind 94.8% · flip 6.5% · bind median 120 min ·
   DOWN 251 binds / 96.8% first-acc / 29.9% kissable · UP 287 / 93.0% / 16.0% still-avail · live 78.2% /
   95.2%. The trade-count knee; the cheapest 94%+ accuracy on the board.
2. **TRV6** (6¢ cumulative travel): cov 91.1% · 94.9% · 6.6% · 107 min · best high-coverage DOWN kissable
   (32.1%) · live 72.6% / 95.3%. The travel knee; binds earliest among the 94%+ gates.
3. **MIN120+TRD20**: cov 66.7% · 97.4% · flip 3.1% · 379 min · DOWN first-acc 98.8% · live coverage
   collapses to 35.2% — the high-accuracy corner, priced honestly: a third of the board forgone, and half
   of what remains starves under the live clock.

Per-category grids for every gate are in the JSON (`by_category_verified`); the class split is carried in
the DOWN/UP columns throughout.

## Conservation

596 role legs = 582 simulated + 14 excluded (no onset or no open, named in method); 30 gate configs × 2
clocks = 60 scored cells, all in the CSV; non-dominated 13 + dominated 17 = 30; every DOWN/UP bind count
sums to its gate's bound count; provenance triples on the three inputs (truth table @ `c0056976`, V52p
clause-3 receipt @ `020b775c`, live-clock artifact @ `620fe4c1`); depth aggregates recomputed from the
receipt's own component rows, shown in the header. Measurement only — no proposal, no selection, no wiring.
ANALYTICAL_ESTIMATE.
