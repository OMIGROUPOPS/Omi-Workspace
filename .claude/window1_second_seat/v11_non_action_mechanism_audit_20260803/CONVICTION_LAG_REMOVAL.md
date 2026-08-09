# Conviction-lag removal — the core-issue test, priced whole

Analysis seat only. Read-only. V41 (`96d33316`) with the confirmation gates removed, CANON crediting, true book = locked + naked P&L on certified closes (`a30f5ccd`). **(1) ARM at first evidence** — a persisted level is joinable from its first observation (no 300 s wait, no seller-hit, no second visit; T5-class, false-arm ~4¢ population-wide). **(2) WALK without lag** — the faller rest reprices every receipt to its running evidence low. Everything else V41 byte-identical. Machine artifact: `…/CONVICTION_LAG_REMOVAL.json`.

## Three machines side by side (+ each removal alone)

| machine | completed | under-par | locked ¢ | naked P&L ¢ | **TRUE BOOK ¢** | ≤93/≤95/≤97/<100 |
|---|--:|--:|--:|--:|--:|---|
| **V41 baseline** | 243 | 243 | 732 | +50 | **782** | 15/35/82/243 |
| **ARM at first evidence** | 313 | 313 | 925 | +76 | **1001** | 17/39/95/313 |
| **WALK without lag** | 284 | 284 | 803 | -8 | **795** | 15/35/89/284 |
| **BOTH (gate-free)** | 363 | 363 | 1010 | -15 | **995** | 17/39/103/363 |

**ARM is the core fix: +219¢ true-book (782 → 1,001; $2.19/contract, +1095¢ at five lots), zero regressions.** The riser join's 300 s + seller-hit + second-visit gate *was* the conviction lag — removing it completes **70 more pairs** (243 → 313) and its new naked legs are **net positive** (+50 → +76: favorites caught deep). **WALK alone is marginal (+13¢)** and self-defeating in combination: its adverse fills turn the naked book negative (+50 → −8 alone; BOTH lands at 995¢, **below ARM-alone's 1,001**). The lag that matters is the *arm*, not the *walk*.

## True book by category (Δ vs V41)

| category | V41 | ARM | WALK | BOTH |
|---|--:|--:|--:|--:|
| ATP_CHALL | 425 | 550 (+125) | 444 (+19) | 553 (+128) |
| ATP_MAIN | 171 | 212 (+41) | 163 (-8) | 202 (+31) |
| WTA_CHALL | 150 | 165 (+15) | 143 (-7) | 160 (+10) |
| WTA_MAIN | 36 | 74 (+38) | 45 (+9) | 80 (+44) |

## The cost columns, honestly

- **False-arm exposure** — arming at first evidence stands rests at levels flow never returns to: **~4¢ population-wide** (the T5 arming false-arm cost, frontier `084df125`). Negligible — a persisted level that was seen once almost always recurs.
- **Adverse fills (walk)** — the unlagged walk fills *earlier in the fall*, at the running evidence low, above the eventual bottom: median **+1¢**, mean 1.5¢, p75 2¢, **max +47¢** over 129 legs. Small per leg, but it is why the walk's new naked legs lose money.
- **New naked legs created** — ARM 59 · WALK 69 · BOTH 103. ARM's are net-positive (deep favorites); WALK's are net-negative (adverse falls).

## Named — mandatory resolution

| game (value) | resolution | combined / locked |
|---|---|---|
| **KIRSEK (55¢)** | **CAUGHT by ARM** — KIR (climbing, pre-trigger) joins at 30 from first evidence; SEK at 17 | **47 / 53¢** |
| **PENTHA (58¢)** | **not completed** — THA converts (walk, 24) but **PEN is NO_FLOW_NEAR** (rest sat 76-77, flow at 22, a 54¢ chasm) → naked, not a pair | — |
| **VANLEE (46¢)** | **not completed** — VAN converts (walk, 55) but **LEE is NO_FLOW_NEAR** (rest 44, flow 1) → naked | — |
| **MCKOUA (9¢)** | **not completed** — MCK converts (walk, 56) but **OUA is NO_FLOW_NEAR** (rest 44, flow 37) → naked | — |

Only **KIRSEK** completes — both legs were reachable and its miss was pure arm-lag. **PENTHA / VANLEE / MCKOUA each have one genuinely-unreachable leg** (the rest sat far from the flow — a *placement*, not a *lag*, failure), so the gate-free machine catches one side (naked) but cannot form the pair. Their top-20 'value' was optimistic — it assumed both legs fillable at reach; one was not.

**No regression:** ARNROM 90, KRUFER 96, BOSCOP 94 — **unchanged across all four machines** (the gates only add conviction; existing completions are byte-identical).

## Verdict

The core issue is the **arm confirmation gate**. Removing it (arm at first evidence) is worth **+219¢ true-book at zero regression and near-zero false-arm cost** — the single biggest lever in the whole program. The walk-lag removal should **not** ride with it: its adverse fills manufacture losing naked legs that erase its own locked gains and drag the combined below arm-alone. **Ship ARM; hold WALK.**

## Conservation

804 games, four machines. V41 243/732¢/+50/782 (baseline reproduced) · ARM 313/925/+76/**1001** · WALK 284/803/-8/795 · BOTH 363/1010/-15/995. Regressions 0/0/0. False-arm ~4¢; adverse median +1¢ (max +47, n 129); new naked 59/69/103. Source V41 MARKET 96d33316, certified closes 57daf3c1, T5 frontier 084df125.