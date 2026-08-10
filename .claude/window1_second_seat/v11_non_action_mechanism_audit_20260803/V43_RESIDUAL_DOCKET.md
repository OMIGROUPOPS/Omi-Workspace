# V43 residual docket — the individual-forensics queue

Analysis seat only. Read-only. Against operative V43 (`01a58334`, census `639e8b19`). Every uncompleted game ranked by **value at stake = 100 − (each leg's fill-or-best-reach)** — the under-par cents the pair would yield if the missing leg(s) captured their nearest observed flow. **Both-legs-dry skips excluded** (the market's no). Machine artifact: `…/V43_RESIDUAL_DOCKET.json`; top-5 packs under `exemplar_packs/v43_docket/`.

## Population

**409 uncompleted** = **178 ranked** (value > 0) + **9 both-dry skips** + 7 naked/skip with a no-flow missing leg + 215 reachable-but-over-par. The last three (231 games) are the **market's no** — no completable pair was ever on offer. Only the **178** carry recoverable value.

## Top 15 by value at stake

| # | value ¢ | game | type | cat | miss story |
|--:|--:|---|---|---|---|
| 1 | **88** | 26JUL18LUZTSE | naked | ATP_MAIN | TSE: guard held rest out at 79c while flow reached 1c [GUARD_WITHHELD] |
| 2 | **79** | 26JUL13KHOZHA | naked | WTA_CHALL | KHO: rest 77c, flow 6c (71c off) [NO_FLOW_NEAR] |
| 3 | **69** | 26JUL13PANFAL | skip | WTA_CHALL | FAL: rest 44c, flow 30c (14c off) [NO_FLOW_NEAR]; PAN: guard held rest out at 42c while flow reached 1c [GUARD_WITHHELD] |
| 4 | **66** | 26JUL13SHIHUA | naked | WTA_CHALL | HUA: rest 60c, flow 1c (59c off) [NO_FLOW_NEAR] |
| 5 | **61** | 26JUL18COLCER | naked | ATP_MAIN | COL: guard held rest out at 55c while flow reached 1c [GUARD_WITHHELD] |
| 6 | **58** | 26JUL13PENTHA | skip | WTA_CHALL | PEN: guard held rest out at 31c while flow reached 22c [GUARD_WITHHELD]; THA: guard held rest out at 24c while flow reached 20c [GUARD_WITHHELD] |
| 7 | **57** | 26JUL18SHEOLI | skip | WTA_MAIN | OLI: guard held rest out at 46c while flow reached 1c [GUARD_WITHHELD]; SHE: guard held rest out at 46c while flow reached 42c [GUARD_WITHHELD] |
| 8 | **52** | 26JUL17ZAKPRO | naked | WTA_CHALL | PRO: rest 51c, flow 1c (50c off) [NO_FLOW_NEAR] |
| 9 | **52** | 26JUL20RUZSAL | skip | WTA_MAIN | RUZ: guard held rest out at 50c while flow reached 23c [GUARD_WITHHELD]; SAL: rest 40c, flow 25c (15c off) [NO_FLOW_NEAR] |
| 10 | **49** | 26JUL13SAINUG | skip | WTA_CHALL | NUG: guard held rest out at 61c while flow reached 50c [GUARD_WITHHELD]; SAI: guard held rest out at 29c while flow reached 1c [GUARD_WITHHELD] |
| 11 | **48** | 26JUL17SMIYUN | naked | ATP_CHALL | YUN: guard held rest out at 23c while flow reached 13c [GUARD_WITHHELD] |
| 12 | **48** | 26JUL14SALIBR | naked | WTA_MAIN | IBR: rest 43c a shade too deep, flow dwelled 44c just above [FLOW_ABOVE_REST] |
| 13 | **44** | 26JUL13VANLEE | naked | WTA_CHALL | LEE: guard held rest out at 18c while flow reached 1c [GUARD_WITHHELD] |
| 14 | **44** | 26JUL16ZAKSHU | naked | WTA_CHALL | SHU: rest 44c, flow 1c (43c off) [NO_FLOW_NEAR] |
| 15 | **43** | 26JUL13KRASAL | naked | ATP_CHALL | KRA: rest 78c, flow 43c (35c off) [NO_FLOW_NEAR] |

## Reading the docket

- The queue is **GUARD_WITHHELD- and NO_FLOW_NEAR-heavy** — the two classes the V43 recalibration targets. GUARD_WITHHELD games (LUZTSE, COLCER, PENTHA, SHEOLI, SAINUG…) are recoverable by the composition fix (guard removed); NO_FLOW_NEAR games (KHOZHA, SHIHUA, ZAKPRO…) have one leg whose flow never came near its rest — the dry-sibling withhold turns those from naked losers into costless skips, not completions.
- **Value-at-stake is potential, not realized**: it credits the missing leg at its *nearest observed flow*, which for a GUARD_WITHHELD or NO_FLOW_NEAR leg is often far below where its rest could actually fill. LUZTSE's 88¢ counts TSE's 1¢ trade, but a released rest fills at ~79¢ (≈10¢ realized). The docket ranks **where to look**, the miss story says **why**, and the pack shows the tape.
- **SALIBR (#12, FLOW_ABOVE_REST)** is the lone genuinely-loosenable near-miss in the top 15 — IBR's rest sat 1¢ too deep under a dwelled ask; a further loosen (not a recalibration) catches it.

## Top-5 walkthrough packs (standing template)

Emitted `DUAL_TIMELINE_V2.csv` + `DECISION_MARKS.json` for the five highest-value games under `exemplar_packs/v43_docket/`:

| # | game | value ¢ | class of the miss |
|--:|---|--:|---|
| 1 | **26JUL18LUZTSE** | 88 | GUARD_WITHHELD |
| 2 | **26JUL13KHOZHA** | 79 | NO_FLOW_NEAR |
| 3 | **26JUL13PANFAL** | 69 | GUARD_WITHHELD |
| 4 | **26JUL13SHIHUA** | 66 | NO_FLOW_NEAR |
| 5 | **26JUL18COLCER** | 61 | GUARD_WITHHELD |

## Conservation

409 uncompleted games = 178 ranked (value>0) + 9 both-dry skips + 7 no-flow-missing + 215 over-par (check 409). Top 15 named; top 5 packed. Source V43 01a58334, census 639e8b19, certified closes 57daf3c1, fit-local tapes.