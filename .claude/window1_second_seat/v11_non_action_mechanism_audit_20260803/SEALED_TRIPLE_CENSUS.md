# Sealed-238 triple census — queue + formation + reflex on the exam book [ANALYTICAL_ESTIMATE]

Analysis seat only. Read-only. The `1d5564b5` method applied **unchanged** to the sealed exam's V47 run
(`2bae8931`): 146 completes' 292 legs + 82 credited one-sided legs = **374 credited fills**. Terminology
binding: prints = contracts sold at P; book side = contracts of standing bids at P. **Coverage caveat inline:
sealed print/tape coverage is partial (holdout + run2 repull); NO_BOOK_AT_MOMENT / NO_PRINT_AT_MOMENT are
named gap classes, never guessed.** Per-fill rows: `SEALED_TRIPLE_CENSUS.json`.

## The three stamps (374 fills)

| stamp | counts |
|---|---|
| ① QUEUE | PLAUSIBLE 83 (22.2%) · **IMPROBABLE 275 (73.5%)** · NO_BOOK_AT_MOMENT 16 (named gap; 0 NO_PRINT) |
| ② FORMATION | **PRE_ONSET_UNDER_ALL 245 (65.5%)** · BRACKET_DEPENDENT 113 · POST_ONSET_UNDER_ALL **16 (4.3%)** · NO_SPLIT 0 |
| ③ REFLEX | **REFLEX_POST 374 (100%)** · READ_LICENSED_POST 0 |

Posting T-minus (all 374): p25 708 · median 812 · p75 890 minutes before the scheduled bell; **374/374 rests
posted within 300 s of window open** — the sealed exam's entire credited book was born before the machine had
read a single tick, same structural law as dev (V47 posts at the first two-sided receipt).

**Honest sealed number: 0 of 146** — no complete survives both legs QUEUE_PLAUSIBLE + POST_ONSET_UNDER_ALL +
READ_LICENSED_POST.

**Money per excluded class** (sealed completes' pair delta = 571¢ — the exam lock; overlaps stated):

| excluded class | games | ¢ |
|---|--:|--:|
| ≥1 leg QUEUE_IMPROBABLE | 136 | **527** |
| ≥1 leg PRE_ONSET | 122 | 424 |
| ≥1 leg REFLEX_POST | 146 | **571 — the entire lock** |
| overlaps | q∩f 114 · q∩r 136 · f∩r 122 · q∩f∩r 114 | |

**BRACKET_DEPENDENT: 113 legs; 61 complete games / 374¢** move on the §8 wake-up qualifier ruling.

## Dev vs sealed, side by side

| | dev (`1d5564b5`, 1,143 fills) | sealed (this census, 374 fills) |
|---|--:|--:|
| QUEUE_IMPROBABLE | 643 (56.3%) | **275 (73.5%)** |
| QUEUE_PLAUSIBLE | 469 (41.0%) | 83 (22.2%) |
| PRE_ONSET_UNDER_ALL | 518 (45.3%) | **245 (65.5%)** |
| POST_ONSET_UNDER_ALL | 144 (12.6%) | **16 (4.3%)** |
| BRACKET_DEPENDENT | 478 (41.8%) | 113 (30.2%) |
| REFLEX_POST | 1,140 (99.7%) | **374 (100%)** |
| honest completes | **0** / 393 | **0** / 146 |
| reflex-born ¢ | 1,666 (all) | 571 (all) |
| queue-improbable ¢ | 1,436 / 1,666 | 527 / 571 |

The sealed book is **worse than dev on every axis**: more queue-thin (73.5% vs 56.3% improbable), more
formation-era (65.5% vs 45.3% pre-onset), post-onset fills nearly absent (4.3%). The out-of-sample exam that
graded 14.4% capture was, by these lenses, almost entirely formation-chaos credits against displayed queues
the replay rest never actually joined — consistent with, and sharpening, the §7 terminal reading. The
16-leg post-onset × 83-leg queue-plausible sealed minority is the exam's only territory resembling live
capture.

## Conservation

374 = 275+83+16 = 245+113+16 = 374+0; completes 292 legs / one-sided 82; honest 0; excluded sets over 146
completes with all overlaps; gaps: 16 NO_BOOK (named), 0 NO_PRINT, 0 NO_SPLIT. Sources: sealed 2bae8931
ledger (staged), run2 + holdout tapes (header-resolved columns), holdout + run2 prints (trade_id-deduped
across the two pulls), bells from machine t_minus fields. ANALYTICAL_ESTIMATE.
