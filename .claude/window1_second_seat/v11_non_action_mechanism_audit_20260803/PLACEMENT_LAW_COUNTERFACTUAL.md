# Placement-law counterfactual — the composed law vs the union reach

Analysis seat only. Read-only. **Law scored against the union reach answer key** (`57daf3c1`): a rest at price R is credited iff the leg's union reach reached ≤ R, filled at R; pair lock = 100−combined when both legs credit and combined < 100. Baseline beside = the **V38 pulse-floor maker-only** realized (`2c54d724`); **V36** (`bfde0d8`, prior directional-rest machine, its own looser ledger) shown as lineage. Machine artifact: `.claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/PLACEMENT_LAW_COUNTERFACTUAL.json`.

## The composed law

**RISER** (i) **PARKED** — a deep ask level stood beyond the 300 s dwell horizon with traded prints at it → rest **1 c under that standing ask**, overriding the pulse floor; (ii) else **pulse floor**, except in **WTA during other-expression-FALLING windows** → hold the **deeper of (pulse floor, own reach low)**. **FALLER** — V36 walk unchanged. Riser universe 409 = **151 parked + 258 transient**.

## Two columns — fills gained vs shallow fills forfeited (pair-level, union ruler)

| | cents |
|---|--:|
| **GAINED** (deeper/new fills complete or deepen pairs) | **+163** |
| **FORFEITED** (1 c-under drops below the bottom, breaks a locked pair) | **−15** |
| **NET** | **+148 ¢ ($1.48)** |

Baseline pair-lock **308¢** → composed law **456¢** on the same union ruler. V36 lineage (own ledger): 270 pairs / 670¢ — a looser fill law (take path + buyer-aggressed prints), not the maker-reach ruler, so not a like-for-like row.

## Per category × class (parked / transient-hold / mislabel)

| category | games | Δ parked | Δ wta-hold | net ¢ | base→law lock |
|---|--:|--:|--:|--:|--:|
| ATP_CHALL | 295 | +31/−3 | — | **+28** | 114→142 |
| ATP_MAIN | 128 | +20/−7 | — | **+13** | 121→134 |
| WTA_CHALL | 98 | +6/−4 | +8/−0 | **+10** | 46→56 |
| WTA_MAIN | 116 | +37/−1 | +61/−0 | **+97** | 27→124 |

**WTA_MAIN carries the law**: net **+97¢** (base-lock 27 → 124), split parked +37 and the WTA falling-window deeper-hold +61 — the measured slide signal converting to cents. The **wta-hold rule forfeits nothing** in either WTA tier (reach is always reachable when you hold at it).

## Riser-side changes (leg grain)

- **Parked override**: 67 sides newly filled, 78¢ of deepening — **but 17 sides forfeited** where the standing ask == the reach bottom, so 1 c-under drops *below* it and nothing fills.
- **WTA falling-window hold**: 129¢ deepened + 2 newly filled, zero forfeits.

## The parked rule's blind spot (sensitivity)

Resting **1 c under the standing ask** only captures the deep reach when the *durable ask itself* is deep. When a transient print dove below a high parked ask, the rule rests far above the bottom. Scored alternative — parked rests **at the traded reach level** instead — locks **574¢** vs the law's **456¢**: the literal 1 c-under specification **leaves 118¢ on the table** (see COP below).

## Faller mislabel — sizing the classifier fix

Op stated **157**; no cut reproduces it exactly (flagged). Scored the actionable set = **115 sides that ran the V36 faller-walk on a leg whose sealed corrected direction ≠ FALLING** (FLAT=SETTLED). Of those, **15 credit** and **100 forfeit entirely** — the classifier fix is worth **≈100 sides currently lost** to the wrong walk (+60¢ shallow-gap on the credited few). Alt state-mislabel cuts: quote≠pressure among fallers **160**, missed-fallers **298**.

## Named games

| game · leg | dir | branch | reach | stand ask | rule | base fill | law fill | pair base→law | lock |
|---|---|---|--:|--:|---|--:|--:|--:|--:|
| ARNROM · ARN | UNKNOWN | RISING | 50 | 56 | parked | None | 55 | None→94 | 6 |
| ARNROM · ROM | UNKNOWN | FALLING | 38 | 42 | unchanged | 39 | 39 | None→94 | 6 |
| BOSCOP · BOS | UNKNOWN | FALLING | 28 | 32 | unchanged | 30 | 30 | None→102 | 0 |
| BOSCOP · COP | UNKNOWN | RISING | 47 | 73 | parked | None | 72 | None→102 | 0 |
| NIKVRB · NIK | FALLING | RISING | 18 | 27 | transient_base | 27 | 27 | 97→97 | 3 |
| NIKVRB · VRB | CLIMBING | RISING | 68 | 68 | transient_base | 70 | 70 | 97→97 | 3 |
| WESPAA · PAA | CLIMBING | FALLING | 38 | 39 | unchanged | None | None | None→None | 0 |
| WESPAA · WES | CLIMBING | RISING | 60 | 60 | transient_base | None | None | None→None | 0 |

- **ARNROM · ARN** — parked; standing ask 56, rest 55, reach 50 ≤ 55 → **fills 55** (baseline forfeited). Pair 94, **+6¢ locked from 0**. The override rescues ARN but at 55, 5¢ shy of the 50 bottom (the ask sat 6 c above reach).
- **BOSCOP · COP** — the blind spot: ask stood at **73** (dwell 25,956 s) while the 47 reach was a transient deep print. 1 c-under = **72**, nowhere near 47 → pair 102, **over par, 0 lock**. Resting at the traded 47 would have locked it. COP is a transient-print case masquerading as parked.
- **NIKVRB** — both risers transient (dwell 11/9 s) → **unchanged** (97, 3¢); the law correctly leaves the fresh-dip pair alone.
- **WESPAA · PAA** — **mislabel exemplar**: a CLIMBING leg run under the FALLING branch → forfeits (reach 38 missed); WES (riser transient) also off-reach. Pair never completes under either law — the classifier fix, not placement, is what WESPAA needs.

## Conservation

637 games; riser universe 409 = 151 parked + 258 transient. GAINED +163 / FORFEITED −15 / **NET +148¢**; base-lock 308→456. Parked-at-reach sensitivity 574¢ (+118¢ over 1c-under). Mislabel 115 (op 157, flagged). Union reach 57daf3c1, V38 2c54d724, V36 bfde0d8, divot census d1ac9497.