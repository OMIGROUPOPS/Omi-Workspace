# No-chase ceiling — model-free replay, all 804  ·  `MODEL_FREE_CEILING`

Analysis seat only. Read-only. **Every number here is labelled `MODEL_FREE_CEILING` —
a measurement of a discipline, not an executable score.** Machine artifact:
`.claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/NOCHASE_CEILING_MODELFREE.json`.

## The state (one coherent state per leg, both evidence types)

At every book receipt each expression is classified from **both**:
- **(a) quote path** (trailing 300 s): new-low ask / seller-hit print = FALLING;
  new-high bid / buyer-lift = RISING; neither = SETTLED.
- **(b) Jul-6 pressure read**: bid depth stacked near best (`depth_ratio ≥ 0.60`) =
  RISING; thin bid / stacked ask (`≤ 0.40`) = FALLING; else SETTLED.

Quote-path is primary; where (a) and (b) point opposite it is logged.
**Disagreement rate (a vs b), per category:** ATP_CHALL 0.117 · ATP_MAIN 0.102 ·
**WTA_CHALL 0.250** · WTA_MAIN 0.093. WTA_CHALL is the outlier — a quarter of its
receipts have the depth-pressure read fighting the quote path.

## The discipline & fill model

Never lift a FALLING ask; while FALLING rest a maker bid 1c under best, walking down
(seller-hits fill us); when SETTLED the standing ask is takeable; either fill arms the
other at cap `99 − fill`; no clock, carry to bell. The no-chase entry is the
**qualifying ask floor** (residency-reachable, dwell/5-lot) — **not** the certified
`maker_floor`, which can require a fleeting seller-aggressed deep print no resting bid
can guarantee. Fill is **maker** if the ask stayed low (faller, our bid is hit),
**taker** if the ask ran up afterward (riser, we took the settled ask).

## Score — conservation 804 (804 scored, 0 no-tape)

| metric | value |
|---|---|
| **No-chase JOINT** | **201 / 804  ·  201 / 391** |
| certified joint (floors) | 390 |
| **R3 executed joint** | **68** |
| fills — maker / taker | 288 / 114 (402 legs) |

**Conservation of the discipline's cost: 201 kept + 189 demoted = 390 certified.**

### Frontier (cumulative pair sum), no-chase joints

| ≤93 | ≤95 | ≤97 | <100 | any-price both-fill |
|--:|--:|--:|--:|--:|
| 39 | 60 | 99 | **201** | 787 |

### Regret gauge — per-leg entry vs certified floor

402 filled legs; **263 zero-regret** (maker at floor); mean **0.54 c**, median 0, max
30 c. The no-chase premium is small on average — the discipline gives up ~half a cent
a leg by refusing to chase the seller-aggressed deep prints.

### The cost column — where waiting *lost* the entry (counted honestly)

**189 certified-winnable games the no-chase discipline demotes** — the residency-only
qualifying floor doesn't clear (not strictly below close, or sum ≥ 100 without the
deeper print, or the ask ran away). By category: **ATP_CHALL 68 · WTA_MAIN 51 ·
ATP_MAIN 45 · WTA_CHALL 25.** This is the honest demote-risk: 390 certified − 189 lost =
201 no-chase. Not chasing is not free.

### No-chase joint per category × region (selected)

ATP_CHALL 116 (51_75/26_50 42, 26_50/51_75 35, le25/ge76 17, ge76/le25 12) ·
ATP_MAIN 47 · WTA_MAIN 24 · WTA_CHALL 14. Full grid in the artifact.

## Named rows (before/after)

| game | no-chase legs | sum | tier | joint? | note |
|---|---|--:|---|---|---|
| **ARNROM** | ARN 56 (taker) + ROM 38 (maker) | **94** | ≤95 | **yes** | matches the expected 38+56=94; ROM the faller filled maker at its floor, ARN the riser taken at 56 before it ran to 62 |
| **LAJVAN** | LAJ 45 (maker) + VAN 50 (taker) | 95 | — | **no** | **demote:** LAJ's qualifying floor 45 = its close 45, not strictly below; certified (mf 43) would pass — the no-chase cost in one row |
| AVEFOR | AVE 48 (taker) + FOR 46 (maker) | 94 | ≤95 | yes | clean maker+taker joint |
| BARREI | BAR 62 (maker) + REI 31 (taker) | 93 | ≤93 | yes | |
| BARVIS | BAR 83 (taker) + VIS 15 (maker) | 98 | <100 | yes | wide-split joint at the frontier edge |
| BOOONC | BOO 20 (taker) + ONC 50 (taker) | 70 | ≤93 | yes | both taken on settle — deepest joint of the six |

## Compare — R3 side by side

| | joint | note |
|---|--:|---|
| R3 (49f6501) executed | **68** | what the live discipline actually completed |
| **No-chase ceiling** | **201** | `MODEL_FREE_CEILING` — best case of the no-chase discipline |
| Certified joint (floors) | 390 | price ceiling incl. seller-aggressed deep prints |

The no-chase discipline's ceiling (201) is **~3× R3's executed 68**, and sits **189
below** the certified 390 — the 189 being the honest cost of never chasing. The headroom
from 68 toward 201 is what a disciplined no-chase standing-floor book could reach without
a single chased lift; the gap from 201 to 390 is only buyable by chasing seller-aggressed
prints, which this discipline forbids by construction.

*All figures `MODEL_FREE_CEILING` — not an executable P&L.*
