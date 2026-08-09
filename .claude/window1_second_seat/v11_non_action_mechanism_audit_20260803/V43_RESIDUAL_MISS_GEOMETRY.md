# V43 residual miss geometry

Analysis seat only. Read-only. The `e17915f3` census re-run against **V43** (composed machine `01a58334` = arm-at-first-evidence + T=10 deep-gap guard + +1c loosen; V43 is BLOCKED/not-operative, scored here as analysis). Every unfilled leg of the **409 uncompleted games** (completed 395 / naked 347 / skip 62) classified **exactly once**, with the new **GUARD_WITHHELD** class. Machine artifact: `…/V43_RESIDUAL_MISS_GEOMETRY.json`.

## The six classes — counts × nearest-miss cents (V41 → V43)

| class | V43 legs | nearest-miss ¢ | (V41 legs) |
|---|--:|--:|--:|
| **FLOW_ABOVE_REST** | 238 | 371 | (349) |
| **FLOW_AT_REST_PRETRIGGER** | 71 | 30 | (172) |
| **FLOW_BELOW_REST** | 39 | 40 | (94) |
| **GUARD_WITHHELD (new)** | 35 | 508 | (0) |
| **NO_FLOW_NEAR (>3c)** | 83 | 955 | (160) |
| **NEVER_PLACED** | 5 | 0 | (4) |
| **total** | **471** | — | (779) |

**Arm-at-first-evidence did its job**: FLOW_AT_REST_PRETRIGGER collapsed **172 → 71** and FLOW_BELOW **94 → 39** (the lag classes shrank). **FLOW_ABOVE_REST is now the dominant residual (238, down from 349 — the +1c loosen took ~110)**, and a **new 35-leg GUARD_WITHHELD** class appears where the deep-gap guard held a rest out while flow reached the target.

## Per category (leg counts)

| class | ATP_CHALL | ATP_MAIN | WTA_CHALL | WTA_MAIN |
|---|--:|--:|--:|--:|
| FLOW_ABOVE_REST | 132 | 29 | 43 | 34 |
| FLOW_AT_REST_PRETRIGGER | 45 | 6 | 15 | 5 |
| FLOW_BELOW_REST | 29 | 2 | 7 | 1 |
| GUARD_WITHHELD | 10 | 7 | 13 | 5 |
| NO_FLOW_NEAR | 34 | 14 | 19 | 16 |
| NEVER_PLACED | 3 | 2 | 0 | 0 |

## The naked book (−162¢) decomposed by the unfilled sibling's miss class

Each naked game's filled-leg P&L (certified close − entry) attributed to why its **sibling** never filled:

| sibling miss class | naked legs | P&L ¢ |
|---|--:|--:|
| FLOW_ABOVE_REST | 171 | -11 |
| FLOW_AT_REST_PRETRIGGER | 43 | -5 |
| FLOW_BELOW_REST | 18 | +42 |
| GUARD_WITHHELD | 10 | +36 |
| NO_FLOW_NEAR | 41 | -224 |
| **total** | — | **-162** |

**NO_FLOW_NEAR is the loss engine: −224¢ across 41 naked legs.** When the sibling is nowhere near any flow (> 3¢ off), the filled leg is an unhedgeable naked directional bet — and it loses. Every other class is small or positive (FLOW_BELOW +42, GUARD_WITHHELD +36). The −162¢ naked book is essentially **the NO_FLOW_NEAR tail the guard fails to catch** at T=10, partly offset by the rest.

## GUARD_WITHHELD — two columns

The guard held **35** rests out while flow reached the withheld target (the PUTJEA·JEA pattern). Removing it:

| | value |
|---|--:|
| **WOULD GAIN** (fill at the withheld target) | **17 completed pairs / +150¢ locked** |
| **GUARD SAVED** (its purpose) | naked losses avoided **37¢**, wins forgone 10¢ → **net +27¢** |

**In the composed machine the guard costs more than it saves**: it blocks **+150¢ of feasible completions** to save **+27¢** of naked losses — a ~123¢ net drag. Arm-at-first-evidence and the +1c loosen make many withheld pairs *feasible* that the standalone T=10 guard (net +73¢ in isolation, `645e035b`) was calibrated against — the guard over-withholds in composition. This is one reason V43 is BLOCKED.

## PUTJEA·JEA — the pattern

JEA's rest at target **64** was withheld (sibling PUT ask 83, implied cap 35, deep-gap 48 > 10¢). PUT filled at 9; JEA held out → PUTJEA is naked. The guard correctly flagged the infeasible cap — but in V43 the same rule withholds legs the composed fills would have completed.

## Top-20 highest-value diagnosable games — by name

| value ¢ | game | class | type | unfilled (reach / rest / diag-fill) | partner |
|--:|---|---|---|---|--:|
| **54** | 26JUL13PENTHA | guard withheld | skip | THA (20 / 22 / 24) | 22 |
| **53** | 26JUL18SHEOLI | guard withheld | skip | SHE (42 / 45 / 46) | 1 |
| **49** | 26JUL13PENTHA | guard withheld | skip | PEN (22 / 76 / 31) | 20 |
| **48** | 26JUL14SALIBR | flow above rest | naked | IBR (44 / 43 / 44) | 8 |
| **38** | 26JUL17SMIYUN | guard withheld | naked | YUN (13 / 60 / 23) | 39 |
| **38** | 26JUL13SAINUG | guard withheld | skip | NUG (50 / 66 / 61) | 1 |
| **28** | 26JUL13PANFAL | guard withheld | skip | PAN (1 / 54 / 42) | 30 |
| **27** | 26JUL13VANLEE | guard withheld | naked | LEE (1 / 44 / 18) | 55 |
| **25** | 26JUL20RUZSAL | guard withheld | skip | RUZ (23 / 58 / 50) | 25 |
| **21** | 26JUL13SAINUG | guard withheld | skip | SAI (1 / 32 / 29) | 50 |
| **12** | 26JUL18SHEOLI | guard withheld | skip | OLI (1 / 46 / 46) | 42 |
| **10** | 26JUL14ZHUYUN | guard withheld | naked | YUN (78 / 90 / 81) | 9 |
| **10** | 26JUL18LUZTSE | guard withheld | naked | TSE (1 / 79 / 79) | 11 |
| **9** | 26JUL14SHUSHI | guard withheld | naked | SHU (77 / 90 / 82) | 9 |
| **8** | 26JUL19VUKGEA | flow below rest | skip | GEA (61 / 64 / 61) | 31 |
| **8** | 26JUL12HERKAZ | flow above rest | naked | HER (46 / 45 / 46) | 46 |
| **7** | 26JUL20PALLEO | guard withheld | naked | PAL (12 / 42 / 36) | 57 |
| **7** | 26JUL15TRUDAV | guard withheld | naked | DAV (54 / 74 / 68) | 25 |
| **7** | 26JUL18COLCER | guard withheld | naked | COL (1 / 59 / 55) | 38 |
| **7** | 26JUL14DILFAL | guard withheld | naked | DIL (19 / 34 / 28) | 65 |

The high-value residual is now **GUARD_WITHHELD-dominated** — PENTHA (54¢), SHEOLI (53¢), SAINUG, RUZSAL — the very games a looser guard tolerance would complete. FLOW_ABOVE (SALIBR 48¢, HERKAZ 8¢) persists as the broad small-cents tail.

## Conservation

471 unfilled legs classified exactly once (True): FLOW_ABOVE 238 + PRETRIGGER 71 + FLOW_BELOW 39 + GUARD_WITHHELD 35 + NO_FLOW_NEAR 83 + NEVER_PLACED 5 = 471. V43 completed 395 / naked 347 / skip 62 = 804. Naked book -162¢ (NO_FLOW_NEAR −224 the driver). Guard withheld 35 (would-complete 17/+150¢; saved +27¢). Source V43 01a58334, certified closes 57daf3c1, guard census 645e035b.