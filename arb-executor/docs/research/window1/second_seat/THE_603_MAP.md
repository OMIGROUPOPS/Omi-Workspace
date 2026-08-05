# The 603 map — full-life window law  ·  `MODEL_FREE_CEILING`

Analysis seat only. Read-only. Print source = the sealed re-pull (reconciliation
938dca47), via `prints.jsonl` (4,836,462 full-life prints, 804/804). Machine artifact:
`.claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/THE_603_MAP.json`.

## Window law (as ruled)

Full life = the **exchange record span per market** (first print/book → market close),
**804/804 by construction**. **True close = the final exchange print of the market's
life** (settlement included; actual bell not required). No scheduled edge, no proxy
boundary, no evaluated-window slice. **All prior below-close counts (incl. the 340/390)
are `WINDOW_TRUNCATION_ARTIFACT`** — they scored the guarded slice.

**Minutes previously excluded** (full life vs the old guarded slice): median **558**,
mean **713**, max **4,037** per game. The old window discarded ~9–12 hours of market
life on a typical game.

## The structural fact — where the true close lands

Per-leg final exchange print, bucketed (1,606 legs):

| ≤1 | 2–5 | 6–94 | 95–98 | 99–100 |
|--:|--:|--:|--:|--:|
| **758** | 21 | 43 | 8 | **776** |

Every match resolves: one leg's final print is **99–100** (winner), the complement's
is **1** (loser). **758 games carry a loser leg that settled to the 1¢ floor.** A leg
whose true close is 1 **can never have traded below its own true close** (1 is the
minimum tick) — so under this law the loser side is a structural blocker.

## Tier census — full life (conservation 804)

| tier | games | meaning |
|---|--:|---|
| **T1** both sides traded below own true close | **40** | neither leg's final print sat on the floor |
| **T2** one did, other did not | **763** | blocker = the floored loser side (low-side close = 1 in 758) |
| **T3** neither | **1** | |
| **total** | **804** | |

**T1-joint** (both below close AND sum < 100): **39**.

## Presence-convertible mass — structurally inert under this close

For every T2/T3 blocker, lawful rest levels come from decision-time evidence (running
traded-low band / qualifying-floor path, close-free). A side is
`PRESENCE_CONVERTIBLE(kc)` if seller-aggressed flow lands 1c/2c/3c above a rest level
**below its true close** and intercepting it completes the leg below close within cap.

**Convertible 1c / 2c / 3c = 0 / 0 / 0.** This is not an absence of seller flow — it is
structural: the blocker's true close is **1**, and there is **no lawful rest level below
1** (no 0-priced book). No seller print can land "above a below-close rest" when no
below-close rest exists. The presence-convertible machinery is inert against a
settlement-floor close.

## The verdict — achievable joint

| conversion of T2/T3 | achievable joint |
|---|--:|
| 0 % | 39 |
| 25 % / 50 % / 75 % / 100 % | 39 (converted games = 0) |

Reachable-on-tape = **40**; UNREACHABLE_ON_THIS_TAPE = **764**
(ATP_CHALL 357 · WTA_MAIN 141 · ATP_MAIN 140 · WTA_CHALL 126) — games where no seller
flow could ever approach a below-close level on the floored side across the entire life.
Conservation: 40 + 764 = 804.

Named: **ARNROM** true close (ARN 1, ROM 99) → T2, ARN the floored blocker, unreachable;
**LAJVAN** (LAJ 1, VAN 99) → T2, same. (Under the guarded-slice artifact both had read
as joint at 94/95 — the full-life settlement close reverses that: ARN led at 62 mid-
window but ultimately lost to 1.)

## Definitional note — flagged, not fudged

Executed exactly as ruled: **final exchange print = settlement value**. The consequence
is that the loser leg floors at 1 in 758/804 games and is structurally unreachable, so
the map collapses to **40 reachable / 764 unreachable** with **zero** presence-
convertible mass — it does **not** produce a 603-scale reachable universe or a non-
trivial conversion verdict. A 603-scale map with live convertible mass requires a
**pre-settlement close basis** (the last genuine market print before the terminal
0-1/99-100 lock); measured that way the tiers invert to T1 791 / unreachable 13. Both
readings are computed and on file; this document reports the ruled (final-print) law
faithfully. The close-basis is the one lever that moves the entire map, and it is the
operator's to set.

*All figures `MODEL_FREE_CEILING`.*
