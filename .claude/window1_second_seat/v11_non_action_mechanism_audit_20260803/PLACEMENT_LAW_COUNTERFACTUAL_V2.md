# Placement-law counterfactual v2 — persistent-level JOIN vs the union reach

Analysis seat only. Read-only. **Supersedes** `PLACEMENT_LAW_COUNTERFACTUAL` (v1 tested a parked-**ask** trigger, falsified by the ARN render — no ask stood at 50; the **bid** parked at 50 for ~9 h and was seller-hit). Scored on the **union reach** answer key (`57daf3c1`): rest at R credited iff union reach ≤ R, fill at R; pair lock = 100−combined when both credit and < 100. Baseline = **V38 pulse-floor maker-only** (`2c54d724`); **V36** (`bfde0d8`) census beside. Machine artifact: `…/PLACEMENT_LAW_COUNTERFACTUAL_V2.json`.

## The law under test

**RISER** — (i) **PERSISTENT-LEVEL JOIN**: a bid level that persisted **≥ 300 s** *and* was **seller-hit** (`last_traded == level`) → **rest AT that level** (the union reach), overriding the pulse floor. Persistence + seller-hit are both observable, no prediction. (ii) else **pulse floor**; in **WTA during other-expression-FALLING windows** → hold the **deeper of (pulse floor, own reach low)**. (iii) **SANITY**: rest < best ask everywhere. **FALLER** — V36 walk unchanged.  Riser universe **409**; **JOIN-qualified = 106**.

## Two columns — fills gained vs forfeited (pair-level, union ruler)

| | cents |
|---|--:|
| **GAINED** | **+182** |
| **FORFEITED** | **0** |
| **NET** | **+182 ¢ ($1.82)** |

Baseline pair-lock **308¢** → law **490¢** on the same union ruler. **Zero forfeits**: JOIN rests *at* the persistent level (= the reach), so it never rests below the bottom the way v1's 1 c-under did. V36 census beside (its own looser census pricing, not the maker-reach ruler): 548 pairs / 2317¢.

## Per category × class

| category | games | JOIN games | Δ join ¢ | Δ wta-hold ¢ | net ¢ | base→law lock |
|---|--:|--:|--:|--:|--:|--:|
| ATP_CHALL | 295 | 49 | +62 | +0 | **+62** | 114→176 |
| ATP_MAIN | 128 | 17 | +11 | +0 | **+11** | 121→132 |
| WTA_CHALL | 98 | 14 | +17 | +4 | **+21** | 46→67 |
| WTA_MAIN | 116 | 25 | +19 | +69 | **+88** | 27→115 |

**WTA_MAIN** and **ATP_CHALL** carry it (+88, +62). WTA_MAIN base-lock 27 → 115: the JOIN class plus the WTA falling-window deeper-hold together.

## Riser-side changes (leg grain)

- **JOIN**: 40 sides newly filled + **184¢** deepened, **0 forfeits**.
- **WTA falling-window hold**: 141¢ deepened + 5 newly filled, 0 forfeits.

## Sanity bound — the V36 rest ≥ ask absurdity, sized

Over V36's own decision trace, **6,592 riser receipts** rested at or above the best ask (of 2,179,565 RISING receipts) across **426 riser legs** — the ARN class (V36 rested **56** with the ask at **56**). A post-only buy at/above the ask is nonsensical. The v2 law rests strictly below ask by construction: **0 violations**.

## Faller mislabel — sizing the classifier fix

Op stated **157**; no cut reproduces it exactly (flagged). Actionable set = **115 sides** that ran the V36 faller-walk on a leg whose sealed corrected direction ≠ FALLING (FLAT=SETTLED); **100 forfeit entirely**, 15 credit (+60¢ shallow gap). The classifier fix ≈ **100 pair-completing sides currently lost to the wrong walk** — WESPAA below is one.

## Named games

| game · leg | dir | branch | reach | bid-persist h | seller-hits | rule | base→law fill | V36 rest/ask | pair base→law | lock |
|---|---|---|--:|--:|--:|---|--:|--:|--:|--:|
| ARNROM · ARN | UNKNOWN | RISING | 50 | 6.45 | 16 | join | None→50 | 56/56 | None→89 | 11 |
| ARNROM · ROM | UNKNOWN | FALLING | 38 | 0.3 | 0 | unchanged | 39→39 | 38/38 | None→89 | 11 |
| BOSCOP · BOS | UNKNOWN | FALLING | 28 | 0.19 | 0 | unchanged | 30→30 | 32/32 | None→77 | 23 |
| BOSCOP · COP | UNKNOWN | RISING | 47 | 0.82 | 4106 | join | None→47 | 67/71 | None→77 | 23 |
| NIKVRB · NIK | FALLING | RISING | 18 | 0.0 | 0 | transient_base | 27→27 | 29/29 | 97→97 | 3 |
| NIKVRB · VRB | CLIMBING | RISING | 68 | 0.0 | 0 | transient_base | 70→70 | 70/83 | 97→97 | 3 |
| WESPAA · PAA | CLIMBING | FALLING | 38 | 2.01 | 16 | unchanged | None→None | 35/39 | None→None | 0 |
| WESPAA · WES | CLIMBING | RISING | 60 | 0.1 | 6 | join | None→60 | 60/64 | None→None | 0 |

- **ARNROM · ARN** — JOIN: bid parked **6.5 h** at 50, **16** seller-hits → rest **AT 50**, fills 50 (baseline forfeited). Pair 89, **+11¢ from 0**. ARN reaches the 50 level as required. V36 rested **56 = the ask** (sanity violation).
- **BOSCOP · COP** — JOIN: reach 47 seller-hit **4,106×** → rest **AT 47**, fills 47. Pair **77 / +23¢** — the fix v1 missed (v1's parked-ask rule filled 72). BOS unchanged 30.
- **NIKVRB** — both risers **TRANSIENT** (no bid persisted at the reach; dips were fresh) → **unchanged** pulse floor (97 / 3¢). The exemplar of when **not** to override — see the pack.
- **WESPAA · WES** — JOIN fills WES at 60, but **PAA is a mislabeled climber run as a faller** → forfeits, so the pair stays incomplete despite the JOIN. Under the corrected direction PAA (bid parked **2 h** at 38, **16** seller-hits) would itself JOIN at 38 → combined **98 / +2¢**. WESPAA needs the **classifier fix**, not placement — it sizes the mislabel column.

## NIKVRB exemplar pack

Emitted the standing template (never built before): `exemplar_packs/NIKVRB_DUAL_TIMELINE_V2.csv` (merged BBO+TRADE, both legs, W1 span) + `exemplar_packs/NIKVRB_DECISION_MARKS.json` (ledger facts + v2 law marks). It documents the **transient** case — both risers left on the pulse floor — the negative control for the JOIN override.

## Conservation

637 games; riser universe 409 (106 JOIN-qualified, dwell horizon 300s). GAINED +182 / FORFEITED 0 / **NET +182¢**; base-lock 308→490. Sanity: V36 6,592 rest≥ask receipts / 426 legs; law 0. Mislabel 115 (op 157, flagged), 100 forfeited. V36 census 548/2317¢. Union reach 57daf3c1, V38 2c54d724, V36 bfde0d8, divot census d1ac9497.