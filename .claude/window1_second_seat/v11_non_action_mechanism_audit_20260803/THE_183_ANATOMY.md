# The 183 anatomy — lawful standability under the CANON ruler

Analysis seat only. Read-only. **`MAKER_REACHABLE_OFFER` (`7fcd6614`) is stamped RULER_VIOLATION**: its maker-reachable floor imposed an **aggressor-side (seller-only) filter and a 10 s dwell filter**, both of which **CANON rejects** — trades-as-truth credits **any** true trade at-or-below a standing rest, traded-at-level imposes **no dwell**. The right question is not *what kind of trade* but **could a rest have lawfully stood at the completing print's level before the print**. Standable = a **post-only bid at the print level was placeable** (best ask > P at the print). PRINT_BEFORE legs assessed under **T5 arming** (first two-sided book). Machine artifact: `…/THE_183_ANATOMY.json`.

## PRINT_ABOVE_REST — could we lawfully have bid at the print?

| verdict | legs |
|---|--:|
| LAWFULLY_STANDABLE (ask > P; a bid at P was placeable) | **14** |
| ONLY_BY_PREDICTION (print at/above the ask — a buyer-lift; a maker bid at P would cross) | **46** |

**77% are ONLY_BY_PREDICTION** — the deep print was a buyer lifting the ask; **no lawful resting bid could have sat there**. The 'we bid under' fault is mostly a mirage: there was no standable level to bid at. Only the minority (ask > P) were real placement misses.

## PRINT_BEFORE_REST_STOOD — could a T5-armed rest have stood at the level before the print?

| verdict | legs |
|---|--:|
| LAWFULLY_STANDABLE (ask > P; a T5-armed rest at P was placeable before the print) | **70** |
| ONLY_BY_PREDICTION | **60** |

**54% are LAWFULLY_STANDABLE** — the ordering-class offers where a rest, armed at first two-sided book, could lawfully have occupied the level before the seller printed. These are the genuinely recoverable ones — earlier presence, not a higher bid.

## Per category (standability of the missing legs)

| category | LAWFULLY_STANDABLE | ONLY_BY_PREDICTION |
|---|--:|--:|
| ATP_CHALL | 36 | 67 |
| ATP_MAIN | 11 | 5 |
| WTA_CHALL | 29 | 24 |
| WTA_MAIN | 8 | 10 |

## Recoverable games — the honest distance from 396 toward 700

A game is **lawfully recoverable** when **every** missing leg is LAWFULLY_STANDABLE (both sides can lawfully fill → the pair completes on trades):

| | games | locked ¢ |
|---|--:|--:|
| **lawfully recoverable** | **62** | **1064** |

| category | recoverable games | locked ¢ |
|---|--:|--:|
| ATP_CHALL | 24 | 248 |
| ATP_MAIN | 10 | 210 |
| WTA_CHALL | 23 | 454 |
| WTA_MAIN | 5 | 152 |

**396 captured + 62 lawfully-recoverable = 458 toward 700 (still 242 short).**

**The honest distance:** perfect lawful placement (bidding at every standable level) *and* T5-earliest arming recover **62 more games** — **396 → 458**. That is the ceiling this tape supports for a lawful resting book: still **242 short of 700**. The remaining gap is **ONLY_BY_PREDICTION** (buyer-lifts at the ask, deep prints no bid could lawfully sit under) — recoverable only by foreknowledge or by taking (which the fee math already showed is net-negative).

## Conservation

Missing legs analyzed 190 (PRINT_ABOVE 60 = 14+46; PRINT_BEFORE 130 = 70+60). **Flagged**: a37bf6a6 stamped the gap classes 183 PRINT_ABOVE / 123 PRINT_BEFORE; my standability recompute classifies the tape-available subset (universe/tape-availability drift) — the standability *rates* and the recoverable-games count are the robust output. Lawfully recoverable 62 games / 1064¢ → 396+62=458 toward 700. Ruler: CANON traded-at-level + trades-as-truth (no aggressor/dwell). Supersedes 7fcd6614. Source V48 e073c606, tapes/prints fit-local.