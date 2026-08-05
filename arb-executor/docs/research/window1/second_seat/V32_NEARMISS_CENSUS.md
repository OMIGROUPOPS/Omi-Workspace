# V32 near-miss census — sellers who stopped one cent short  ·  `MODEL_FREE_CEILING`

Analysis seat only. Read-only on Codex's V32 package
(`v32_no_chase_state_machine_20260805`, finalized). Machine artifact:
`.claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/V32_NEARMISS_CENSUS.json`.
All figures `MODEL_FREE_CEILING`.

## Population & method

V32's executable no-chase machine credits **41** joints (vs the **201** model-free
ceiling — a **160-game execution gap**, "execution price"). Its uncredited legs carry a
terminal reason Codex named directly: **`RESTING_ORDER_NEVER_RECEIVED_LATER_SELLER_
AGGRESSED_PRINT`** — **607** waited-and-lost rests.

For each, I reconstructed the **rest trajectory** (every `PLACE`/`REPRICE` `target_cents`
from the full decision trace — the bid walking 1c under best, never chasing up) and, at
every **seller-aggressed print** (our `prints.jsonl`, `taker_side == "no"` = a seller
hitting the YES bid; 495,458 of them), measured the gap to the **active** rest level.
A print landing **1c / 2c / 3c above** the standing rest is a seller who **stopped just
short** — the fill our own resting presence plausibly converts.

*(The trajectory matters: censusing against the terminal walked-down level over a late
window gives a spurious ~1%. Against the active level, near-misses are pervasive —
because the discipline rests 1c under best, a seller hitting the bid above us prints at
exactly rest+1.)*

## Density — per category (share of the 607 lost rests with ≥1 near-miss)

| category | lost rests | 1c | 2c | 3c | 1c prints |
|---|--:|--:|--:|--:|--:|
| ATP_MAIN | 104 | **65.4%** | 74.0% | 76.0% | 499 |
| WTA_MAIN | 111 | 45.9% | 58.6% | 64.0% | 332 |
| WTA_CHALL | 105 | 37.1% | 52.4% | 55.2% | 110 |
| ATP_CHALL | 287 | 31.0% | 45.3% | 54.0% | 416 |
| **overall** | **607** | **40.7%** | **53.9%** | **59.8%** | **1,357** |

**Two of every five waited-and-lost rests had a seller print one cent above while the
bid stood** — sellers who came within a cent of hitting us and didn't. Widen to 3c and
it is three in five. ATP_MAIN is the hotspot: two-thirds of its lost rests are 1c
near-misses.

## Implied joint range — if 1c near-misses convert

Converting a 1c near-miss means our resting presence draws the fill at the rest level.
**57** of the 1c-near-miss legs would complete a joint on conversion (the sibling is
already V32-credited, both below close, sum < 100). On top of V32's executable **41**:

| conversion of 1c near-misses | executable joint |
|---|--:|
| 0% (V32 as-shipped) | 41 |
| 25% | **55** |
| 50% | **70** |
| 100% | **98** |
| — model-free ceiling | 201 |

Even **half** the 1c near-misses converting (70) **clears R3's executed 68**; full
conversion (98) reclaims **57 of the 160-game execution gap** — the slice that is a
*single cent of residency* away, not a modelling gain. The remaining gap to 201 needs
more than a 1c draw (deeper prints, 2–3c pulls, or legs with no near-miss at all).

## Conservation

607 waited-and-lost rests censused (of 651 uncredited V32 legs; the other 44 =
`NO_EXECUTABLE_ACTION_BEFORE_GUARDED_RIGHT_EDGE`, no rest). 495,458 seller-aggressed
prints scanned. V32 executable joint 41 · model-free ceiling 201 · execution gap 160 ·
1c-near-miss flip games 57. All `MODEL_FREE_CEILING` — a conversion *hypothesis*
measured against the tape, not an executed fill.
