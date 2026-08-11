# The dipless 43 — raw-tape verification, no episode machinery

Analysis seat only. Read-only. The 43 no-dip riser legs (`9ee14bf5`) re-derived with the same detector, then audited at **full tape resolution**: every BBO ask change, every trade print (fit-local + holdout + exam repull), prints below the displayed ask, and the honest floor vs our rest. Machine artifact: `…/THE_DIPLESS_43_RAW.json` (per-leg rows: ask changes, distinct levels, min ask, time within 1/2/3¢ of the low, print counts/lows, below-ask counts).

## The verdict census

| verdict | legs |
|---|--:|
| **GENUINELY_STATIC** (ask never moved below its start; nothing traded under it) | **17** |
| **TRADED_THROUGH** (prints below the displayed ask) | **14** |
| **NO_POSTSTAND_RECORD** (the rest stood at/after the tape's end — vacuously 'dipless') | **12** |
| MICRO_TOUCHED | 0 |

## The episode ruler — stamped PARTIAL_UNDERCOUNT, but the collectability verdict holds

Of the **31 legs with a post-stand record**, **14 (45%) TRADED_THROUGH** — prints landed below the displayed ask, invisible to any ask-episode detector. The ruler under-counts *touches*. **But it does not under-count collectability**: of the 14 traded-through legs, **only 1 had its honest floor at-or-below our rest** — the through-prints landed **1-7¢ above the rest** (BEN +2, BRA +4, PAR +5, ROD +2, SCH +1, DAL +2, ECH +3, ZHU +7…). Deep flow through the book, never deep enough to touch us. The 17 GENUINELY_STATIC legs are absolute: **0 ask changes, 1 distinct level** the entire post-stand span.

## The stand-too-late 12 — a new honest class

**12 legs have no post-stand tape at all** (26JUL12CHAJON, 26JUL13BOUGAN, 26JUL14SQUKUM, 26JUL16BICCAS, 26JUL17DRAGEA, 26JUL20JOHAGU, 26JUL12ALTGAS, 26JUL12DROBLO, 26JUL13RINAST, 26JUL13RISPOH, 26JUL14CARVON, 26JUL20TOTRUG) — the join armed at or after the record's end, so their 'dipless' verdict was vacuous. These belong to the L4/arming organ, not the dip-supply story: nothing could ever have filled them because the rest never stood inside the record.

## The dip-supply split, re-cut on raw touches

| class | legs |
|---|--:|
| genuinely static (no touch, no through-trade) | 17 |
| traded-through above the rest (uncatchable by ≤rest law) | 13 |
| traded-through at/below rest (the one real miss) | 1 |
| stand-too-late (no post-stand record) | 12 |

**The 9ee14bf5 conclusion survives raw verification**: the unfilled risers' problem is absence — of dips, of sub-rest flow, or of a standing rest at all. Exactly **one** leg in the 43 had raw flow reach our rest. The episode ruler is stamped PARTIAL_UNDERCOUNT for touches, HOLDS for collectability.

## Conservation

43 re-derived = 17 static + 14 traded-through + 12 no-post-stand-record (verdicts sum 43). Prints from fit-local + holdout-exam + exam repull (43/43 covered). Sources 9ee14bf5, f40ac8ea, tapes fit-local + exam private + holdout-exam.
## APPEND — capture-quality cross

Per-leg tape provenance and WS-gap census vs the filled-riser calibration density (646.0 ticks/h median). Era census: SUPERVISED_AUG6+ 2 · CLEAN_JUL26_28 3 · DEGRADED_JUL28_AUG6 3 · DEV_FIT_LOCAL 35.

| capture verdict | legs |
|---|--:|
| CAPTURE_SUSPECT (gap share >20% or density <25% of cal) | **41** |
| CAPTURE_CLEAN | 2 |

| dipless verdict | SUSPECT | CLEAN |
|---|--:|--:|
| GENUINELY_STATIC | 16 | 1 |
| TRADED_THROUGH | 13 | 1 |
| NO_POSTSTAND_TAPE | 12 | 0 |

**41 of 43 stamp CAPTURE_SUSPECT — but the metric is CONFOUNDED on change-driven tapes and must be read with care**: a BBO recorder ticks only on changes, so a genuinely quiet static book *naturally* shows huge inter-tick gaps and low density — indistinguishable from a capture outage without heartbeats. The honest statement is two-sided: (a) no visible dips exist on these records; (b) on 41 of 43 the record is sparse enough (gap shares 0.30-0.92, densities often <0.4× calibration) that transient dips *could* have hidden in the gaps — the dipless verdict is a lower bound on dip supply, not a proof of absence. Only 2 legs are clean-capture-confirmed dipless. The degraded-era (JUL28-AUG6) and supervised (AUG6+) legs are uniformly suspect; so are most dev legs — quiet books are exactly where the confound bites.

## APPEND — the 43 identities + census

| # | leg | era | dipless verdict | capture | floor | rest | value ¢ |
|--:|---|---|---|---|--:|--:|--:|
| 1 | 26JUL20MAZSPI·MAZ | DEV_FIT_LOCAL | TRADED_THROUGH | CAPTURE_SUSPECT | 66 | 66 | 1 |
| 2 | 26AUG10RAIVAN·VAN | SUPERVISED_AUG6+ | GENUINELY_STATIC | CAPTURE_SUSPECT | 75 | 64 | 0 |
| 3 | 26JUL27ALBHAS·HAS | CLEAN_JUL26_28 | GENUINELY_STATIC | CAPTURE_SUSPECT | 46 | 39 | 0 |
| 4 | 26JUL28AZKERE·ERE | DEGRADED_JUL28_AUG6 | GENUINELY_STATIC | CAPTURE_SUSPECT | 77 | 76 | 0 |
| 5 | 26JUL28BASRAW·BAS | DEGRADED_JUL28_AUG6 | GENUINELY_STATIC | CAPTURE_SUSPECT | 87 | 84 | 0 |
| 6 | 26AUG09EALBEN·BEN | SUPERVISED_AUG6+ | TRADED_THROUGH | CAPTURE_CLEAN | 54 | 52 | 0 |
| 7 | 26JUL27NAVKEN·KEN | CLEAN_JUL26_28 | GENUINELY_STATIC | CAPTURE_SUSPECT | 30 | 26 | 0 |
| 8 | 26JUL27SHYBRA·BRA | CLEAN_JUL26_28 | TRADED_THROUGH | CAPTURE_SUSPECT | 47 | 43 | 0 |
| 9 | 26JUL28PARWAN·PAR | DEGRADED_JUL28_AUG6 | TRADED_THROUGH | CAPTURE_SUSPECT | 41 | 36 | 0 |
| 10 | 26JUL12CHAJON·JON | DEV_FIT_LOCAL | NO_POSTSTAND_TAPE | CAPTURE_SUSPECT | None | None | 0 |
| 11 | 26JUL12MIYKUZ·KUZ | DEV_FIT_LOCAL | GENUINELY_STATIC | CAPTURE_SUSPECT | 37 | 34 | 0 |
| 12 | 26JUL12RAIZHU·ZHU | DEV_FIT_LOCAL | GENUINELY_STATIC | CAPTURE_SUSPECT | 61 | 56 | 0 |
| 13 | 26JUL13BOUGAN·BOU | DEV_FIT_LOCAL | NO_POSTSTAND_TAPE | CAPTURE_SUSPECT | None | None | 0 |
| 14 | 26JUL13JONPET·PET | DEV_FIT_LOCAL | GENUINELY_STATIC | CAPTURE_CLEAN | 61 | 55 | 0 |
| 15 | 26JUL13RODALK·ROD | DEV_FIT_LOCAL | TRADED_THROUGH | CAPTURE_SUSPECT | 77 | 75 | 0 |
| 16 | 26JUL13SANLOP·LOP | DEV_FIT_LOCAL | GENUINELY_STATIC | CAPTURE_SUSPECT | 13 | 10 | 0 |
| 17 | 26JUL14CASSCH·SCH | DEV_FIT_LOCAL | TRADED_THROUGH | CAPTURE_SUSPECT | 59 | 58 | 0 |
| 18 | 26JUL14DALMAY·MAY | DEV_FIT_LOCAL | GENUINELY_STATIC | CAPTURE_SUSPECT | 83 | 80 | 0 |
| 19 | 26JUL14SQUKUM·SQU | DEV_FIT_LOCAL | NO_POSTSTAND_TAPE | CAPTURE_SUSPECT | None | None | 0 |
| 20 | 26JUL16BICCAS·BIC | DEV_FIT_LOCAL | NO_POSTSTAND_TAPE | CAPTURE_SUSPECT | None | None | 0 |
| 21 | 26JUL16DELDAL·DAL | DEV_FIT_LOCAL | TRADED_THROUGH | CAPTURE_SUSPECT | 40 | 38 | 0 |
| 22 | 26JUL16SMIMAT·SMI | DEV_FIT_LOCAL | GENUINELY_STATIC | CAPTURE_SUSPECT | 82 | 79 | 0 |
| 23 | 26JUL17DRAGEA·GEA | DEV_FIT_LOCAL | NO_POSTSTAND_TAPE | CAPTURE_SUSPECT | None | None | 0 |
| 24 | 26JUL18ALCVIL·ALC | DEV_FIT_LOCAL | GENUINELY_STATIC | CAPTURE_SUSPECT | 73 | 70 | 0 |
| 25 | 26JUL19HERECH·ECH | DEV_FIT_LOCAL | TRADED_THROUGH | CAPTURE_SUSPECT | 78 | 75 | 0 |
| 26 | 26JUL19MARCOL·MAR | DEV_FIT_LOCAL | GENUINELY_STATIC | CAPTURE_SUSPECT | 97 | 92 | 0 |
| 27 | 26JUL20JOHAGU·JOH | DEV_FIT_LOCAL | NO_POSTSTAND_TAPE | CAPTURE_SUSPECT | None | None | 0 |
| 28 | 26JUL20TOKHUR·TOK | DEV_FIT_LOCAL | GENUINELY_STATIC | CAPTURE_SUSPECT | 56 | 54 | 0 |
| 29 | 26JUL20ZHUMAL·ZHU | DEV_FIT_LOCAL | TRADED_THROUGH | CAPTURE_SUSPECT | 43 | 36 | 0 |
| 30 | 26JUL12ALTGAS·ALT | DEV_FIT_LOCAL | NO_POSTSTAND_TAPE | CAPTURE_SUSPECT | None | None | 0 |
| 31 | 26JUL12DROBLO·BLO | DEV_FIT_LOCAL | NO_POSTSTAND_TAPE | CAPTURE_SUSPECT | None | None | 0 |
| 32 | 26JUL12SLADAM·DAM | DEV_FIT_LOCAL | TRADED_THROUGH | CAPTURE_SUSPECT | 84 | 82 | 0 |
| 33 | 26JUL18ROCBUE·BUE | DEV_FIT_LOCAL | GENUINELY_STATIC | CAPTURE_SUSPECT | 83 | 78 | 0 |
| 34 | 26JUL18RUBTAB·TAB | DEV_FIT_LOCAL | TRADED_THROUGH | CAPTURE_SUSPECT | 30 | 27 | 0 |
| 35 | 26JUL18WALDJE·DJE | DEV_FIT_LOCAL | TRADED_THROUGH | CAPTURE_SUSPECT | 96 | 93 | 0 |
| 36 | 26JUL12SOKNUG·NUG | DEV_FIT_LOCAL | GENUINELY_STATIC | CAPTURE_SUSPECT | 73 | 66 | 0 |
| 37 | 26JUL13RINAST·RIN | DEV_FIT_LOCAL | NO_POSTSTAND_TAPE | CAPTURE_SUSPECT | None | None | 0 |
| 38 | 26JUL13RISPOH·POH | DEV_FIT_LOCAL | NO_POSTSTAND_TAPE | CAPTURE_SUSPECT | None | None | 0 |
| 39 | 26JUL14CARVON·CAR | DEV_FIT_LOCAL | NO_POSTSTAND_TAPE | CAPTURE_SUSPECT | None | None | 0 |
| 40 | 26JUL20TOTRUG·RUG | DEV_FIT_LOCAL | NO_POSTSTAND_TAPE | CAPTURE_SUSPECT | None | None | 0 |
| 41 | 26JUL18HONTHA·HON | DEV_FIT_LOCAL | TRADED_THROUGH | CAPTURE_SUSPECT | 85 | 79 | 0 |
| 42 | 26JUL18ITOKNU·ITO | DEV_FIT_LOCAL | GENUINELY_STATIC | CAPTURE_SUSPECT | 50 | 47 | 0 |
| 43 | 26JUL19PRIMAR·PRI | DEV_FIT_LOCAL | TRADED_THROUGH | CAPTURE_SUSPECT | 89 | 87 | 0 |

**The class carries almost no value**: the highest-value dipless leg is **26JUL20MAZSPI·MAZ at 1¢** (honest floor 66 vs rest 66 — the one traded-through-at-rest leg). Standing-template pack (DUAL_TIMELINE_V2, 18,648 rows raw-resolution + DECISION_MARKS) emitted for it under `exemplar_packs/dipless_top/` for Plex's render.
