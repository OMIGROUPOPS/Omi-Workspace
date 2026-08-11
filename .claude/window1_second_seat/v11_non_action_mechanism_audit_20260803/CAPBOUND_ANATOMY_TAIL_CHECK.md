# CAP_BOUND anatomy + one-eyed vindication + tail boundary — sealed

Analysis seat only. Read-only. Sealed exam `2bae8931` via the `b26cf548` gauge rows. Machine artifact: `…/CAPBOUND_ANATOMY_TAIL_CHECK.json` (all per-game rows).

## (1) The 45 CAP_BOUND games — who killed the pair?

Per game: the first fill's **richness** (entry − its own achievable floor), the armed cap (99 − entry) vs the sibling's lowest flow (**infeasibility gap**), and the counterfactual — **if the first fill had paid its own floor**, does the sibling's flow fit under the resulting cap?

| verdict | games |
|---|--:|
| **die from FIRST-FILL RICHNESS** (pair completable at own floor) | **31** |
| genuinely infeasible at any price | 14 |

| filled side | RICHNESS | GENUINE |
|---|--:|--:|
| FALLER/SETTLED | 24 | 13 |
| RISER | 7 | 1 |

**31 of 45 (69%) are self-inflicted**: the first fill paid above its own achievable floor, and that richness armed a cap the sibling's real flow could not fit under — **had the first fill paid its floor, the pair completes**. Only 14 were unreachable at any price. The faller/settled-filled side carries most of both columns (24/13) — the rich early faller fill is the cap-killer.

## (2) The 22 one-eyed pairs — did the market vindicate the right eye?

Per game: the filled leg's read was RIGHT (vs realized) while the sibling's read was not its inverse. Test: did the sibling's subsequent flow behave as the **inverse of the right read** predicted (measured against the sibling's book at the filled leg's entry moment)?

| verdict | games |
|---|--:|
| **VINDICATED** (sibling behaved as the inverse predicted) | **20** |
| not vindicated | 2 |

**20 of 22 (91%)** — when one leg read the game right and the sibling contradicted it, the market went on to do what the right read's inverse said **almost every time**. The contradicted sibling read wasn't just incoherent — it was *wrong*, and acting on the right leg's inverse would have positioned the sibling correctly. The mirror is informative: one good eye is enough, if the machine trusts it.

## (3) Top-10 tail — schedule bell vs in-match signature

| game | bell | deep leg | floor ¢ | low at window-frac | terminal monotone | **stamp** |
|---|---|---|--:|--:|:-:|---|
| 26AUG09POUSIM | schedule_only | SIM | 1 | 0.0 | no | **CLEAN_WINDOW** |
| 26AUG10BARLEC | schedule_only | BAR | 1 | 0.06 | no | **CLEAN_WINDOW** |
| 26AUG10ISOMUK | schedule_only | ISO | 1 | 0.47 | no | **CLEAN_WINDOW** |
| 26AUG10MRVBAS | schedule_only | BAS | 1 | 0.67 | no | **CLEAN_WINDOW** |
| 26AUG10PETMCD | schedule_only | PET | 1 | 0.06 | no | **CLEAN_WINDOW** |
| 26AUG10RAWMIT | schedule_only | MIT | 1 | 0.15 | no | **CLEAN_WINDOW** |
| 26AUG10RIBALC | schedule_only | ALC | 1 | 0.24 | no | **CLEAN_WINDOW** |
| 26AUG10VANMEC | schedule_only | VAN | 1 | 0.89 | no | **SUSPECT_INMATCH_LEAK** |
| 26JUL28MAYDUC | schedule_only | MAY | 1 | 0.0 | no | **CLEAN_WINDOW** |
| 26AUG09SAMRYB | schedule_only | SAM | 5 | 0.15 | no | **CLEAN_WINDOW** |

**9 of 10 CLEAN_WINDOW, 1 SUSPECT.** The single-digit floors are overwhelmingly *early*-window deep trades (POUSIM at 0% of the window, BARLEC 6%, PETMCD 6%, RAWMIT 15%) — not terminal collapses; no monotone GANJAN signature fires on any of the ten. Only **VANMEC** (low at 89% of a schedule-only window) is stamped SUSPECT_INMATCH_LEAK. The worst pair-gaps are real pre-match deep flow, not leaked in-match play — with one named exception to hold out of any calibration.

## Conservation

45 CAP_BOUND rows (31 richness + 14 genuine = 45) · 22 one-eyed rows (20+2=22) · 10 tail rows (9 clean + 1 suspect). Source sealed 2bae8931, gauge b26cf548; floors = sealed traded_floor; sibling book at entry from reach_snapshot.