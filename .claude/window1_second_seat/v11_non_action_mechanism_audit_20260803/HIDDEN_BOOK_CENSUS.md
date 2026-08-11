# The hidden-book census — every print located against the displayed book

Analysis seat only. Read-only. Every in-window print located vs the contemporaneous displayed BBO (last recorded tick ≤ print time). Dev = the fit-local 373k reconciled corpus; sealed = the 238's canonical prints (holdout + exam repull). Machine artifact: `…/HIDDEN_BOOK_CENSUS.json`.

## The census

| class | dev n | dev share | dev vol | sealed n | sealed share | sealed vol |
|---|--:|--:|--:|--:|--:|--:|
| AT_DISPLAYED_BID | 46,509 | 0.125 | 0.151 | 68,910 | 0.119 | 0.128 |
| AT_DISPLAYED_ASK | 149,005 | 0.399 | 0.348 | 155,932 | 0.269 | 0.24 |
| INSIDE_SPREAD | 4,405 | 0.012 | 0.009 | 5,972 | 0.01 | 0.006 |
| THROUGH | 173,264 | 0.464 | 0.493 | 349,265 | 0.602 | 0.626 |

Located: dev 373,183 (+20 no-tape) · sealed 580,079 (+0 no-tape).

## Reading it — with the staleness caveat carried

- **THROUGH dominates: 46% of dev prints (49% of volume), 60% sealed (63% vol)** — flow printing beyond the last-displayed levels. **Caveat, flagged**: the tape is change-sampled and gappy (9ff18c8c), so a print compared against a stale last tick inflates THROUGH — this figure is an *upper bound* mixing genuine hidden/through fills with tape staleness. Even discounted, the displayed book is a poor map of where flow transacts.
- **INSIDE_SPREAD is the clean hidden-liquidity signal: 4,405 dev / 5,972 sealed prints (~1%)** — strictly between the recorded bid and ask: liquidity the displayed book never showed, unambiguously (staleness cannot create an inside print from a wider book).
- At-displayed flow: ask-side 40% dev / 27% sealed vs bid-side 12%/12% — buyer-lifts outnumber seller-hits ~3:1 dev, consistent with the maker-reachability finding.

## THE CHAIN — the Jul-6 pressure instrument's first measurement

For each inside-spread print, did the displayed book move **toward** the hidden level (nearest-side distance) in the surrounding ±60 s?

| corpus | inside n | moved toward BEFORE | moved toward AFTER |
|---|--:|--:|--:|
| dev | 4,405 | 32% | 37% |
| sealed | 5,972 | 28% | 34% |

**The signature is real but weak**: the book follows the hidden print (after > before by ~4-6 points in both corpora) more than it anticipates it. An inside print is a mild leading indicator of displayed-book movement toward its level — the first measured confirmation of the Jul-6 chain hypothesis, at ~1/3 base rates.

## Named

- **MAZ's 66s** (3 prints): **2 × AT_DISPLAYED_BID** (07-20 19:52:09 and 19:52:32 — sellers hit the displayed 66 bid, the exact level of our rest) and 1 × THROUGH (19:46:08, 66 under a 67/69 book). The two at-bid prints are **seller-aggressed flow at the rest's own level** — the strongest single confirmation that MAZ was collectable; its non-credit is a machine-side crediting nuance, not a market absence.
- **The 14 through-print legs** (dipless census): 26AUG09EALBEN·BEN, 26JUL27SHYBRA·BRA, 26JUL28PARWAN·PAR, 26JUL13RODALK·ROD, 26JUL14CASSCH·SCH, 26JUL16DELDAL·DAL, 26JUL19HERECH·ECH, 26JUL20ZHUMAL·ZHU, 26JUL12SLADAM·DAM, 26JUL18RUBTAB·TAB, 26JUL18WALDJE·DJE, 26JUL20MAZSPI·MAZ, 26JUL18HONTHA·HON, 26JUL19PRIMAR·PRI — their below-displayed-ask prints are this census's THROUGH/INSIDE classes in miniature; on 13 of 14 the through-flow stopped 1-7¢ above our rest (aa1cc301).

## Conservation

Every located print exactly one class: dev 373,183 = 46,509+149,005+4,405+173,264; sealed 580,079 likewise. No-tape dev 20 / sealed 0 reported apart. Chain on all inside prints (4,405+5,972). Sources: fit-local prints+tapes, holdout+exam repull prints, exam private + holdout tapes; staleness caveat 9ff18c8c.