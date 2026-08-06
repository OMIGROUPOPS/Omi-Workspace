# V34-W1 bleed mechanism census  ·  causal (e56d79a2)

Analysis seat only. Read-only on Codex's V34-W1 causal package
(`v34_w1_causal_capture_measurement_20260805`, e56d79a2), `STRICT_EVENT_LEDGER`. Machine
artifact:
`.claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/V34_BLEED_MECHANISM_CENSUS.json`.

The **254** = V34 STRICT completed pairs (both legs credited, under par). This censuses
the **550 games not in the 254** — one primary bleed mechanism each.

## Method (one primary mechanism per game)

`na` = credited-leg count. **na=1 (naked pair)** → diagnose the uncredited **blocker**:
`NO_OFFER` (blocker never had a floor) · `CAP_STRANGLED` (blocker floor + filled entry ≥
100, *and* it was already over cap at the filled leg's own floor) · `TAKE_PREEMPT`
(blocker would fit under cap if the filled leg had paid its floor, but the filled leg
**overpaid ≥ 2c**, strangling the room) · `STATE_MISLABEL` (blocker had a takeable
qualified ask ≤ cap but **SETTLED decision-share < 5%** — the state stayed FALLING and
the take never fired) · else `REST_STARVED` (rest stood to the hard edge, unfilled).
**na=0** → NO_OFFER / CAP_STRANGLED / STATE_MISLABEL / REST_STARVED / ZERO_FILL. **na=2**
(both filled, over par) → TAKE_PREEMPT if a leg's regret ≥ 2c, else CAP_STRANGLED. Every
V34 blocker terminated `HARD_RIGHT_EDGE_REACHED_WITH_REST_UNFILLED`.

## Census — 550 non-254 games (conservation 804 = 254 + 550)

| mechanism | games | ATP_CHALL | ATP_MAIN | WTA_CHALL | WTA_MAIN | naked | implied recovered if fixed |
|---|--:|--:|--:|--:|--:|--:|--:|
| **REST_STARVED** | **190** | 90 | 23 | 42 | 35 | 183 | **190** |
| **TAKE_PREEMPT** | **169** | 74 | 31 | 27 | 37 | 169 | **169** |
| **CAP_STRANGLED** | **92** | 48 | 4 | 31 | 9 | 83 | 0 (structural) |
| **STATE_MISLABEL** | **90** | 39 | 23 | 15 | 13 | 72 | **90** |
| **NO_OFFER** | **9** | 5 | 2 | 0 | 2 | 0 | 0 (structural) |
| **ZERO_FILL** | **0** | — | — | — | — | 0 | 0 |
| **total** | **550** | 256 | 83 | 115 | 96 | 507 | **449** |

**The bleed is executional, not structural.** The three execution mechanisms —
REST_STARVED + TAKE_PREEMPT + STATE_MISLABEL = **449 games** — each recover a completed
pair if fixed alone (an under-par pair *was* priceable). Only **101** (CAP_STRANGLED 92 +
NO_OFFER 9) are structural: the floors summed ≥ 100 or a side never priced. So V34's 254
sits atop a recoverable **449** and an irreducible **101** — 254 + 449 + 101 = 804.

- **REST_STARVED (190, biggest)** — the maker bid stood to the bell and no seller hit it.
- **TAKE_PREEMPT (169)** — the leg V34 *did* fill overpaid ≥ 2c above its own qualified
  floor; that overpayment ate the cap room the blocker needed. Self-inflicted.
- **STATE_MISLABEL (90)** — a takeable qualified ask ≤ cap was sitting there, but the
  side's SETTLED decision-share was < 5%: the machine read FALLING and never lifted.

## SETTLED decision-share — how rare the flicker (all 1,604 legs)

| mean | p10 | median | p90 | max | legs < 5% | legs < 10% |
|--:|--:|--:|--:|--:|--:|--:|
| 0.138 | **0.015** | 0.114 | 0.30 | 1.0 | **398** | 708 |

The state is SETTLED only **~11% of the time (median)**; **398 of 1,604 legs settle under
5%** of their decisions, and the p10 leg settles **1.5%**. The "take when SETTLED"
trigger barely fires — the machine lives in FALLING/RISING. That flicker is the root of
STATE_MISLABEL directly (90 games) and feeds REST_STARVED (the machine rests because it
almost never reads SETTLED). Nearly half the book's legs are a coin-flick away from never
offering the take at all.

## Exemplars (3 per mechanism, exact-bell preferred)

| mechanism | exemplar games |
|---|---|
| REST_STARVED | DROPIR, HOUJOR, POLKUH |
| TAKE_PREEMPT | KRALOR, CHOSUR (Jul13), NOGBRO (Jul13) |
| CAP_STRANGLED | BINGIL, FUEROS, HOHSUR |
| STATE_MISLABEL | BOSCOP, DEVGON, LAGTEP |
| NO_OFFER | VALNIJ, FORMAK (Jul13), MATMOR (Jul14) |
| ZERO_FILL | — (none: V34 fills ≥1 leg in every non-254 game) |

## Conservation

804 = 254 completed + 550 bleed. Bleed = 190 REST_STARVED + 169 TAKE_PREEMPT + 92
CAP_STRANGLED + 90 STATE_MISLABEL + 9 NO_OFFER + 0 ZERO_FILL. Recoverable-if-fixed 449
(execution) + structural 101 (cap/no-offer) = 550. Of 550, 507 are naked pairs
(one leg filled), 43 both-uncredited; 0 both-filled-over-par. SETTLED-share over 1,604
legs: median 0.114.
