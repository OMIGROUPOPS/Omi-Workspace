# The par sheet — all 804 dev games vs the market's perfect trade [ANALYTICAL_ESTIMATE]

Analysis seat only. Read-only. Machine records only. **PAR** per game = Σ per leg of the lowest true traded
price inside that leg's W1 window (CANON trades-as-truth channel, raw fit-local prints, no reconstruction, no
stand-conditioning — the market's perfect trade, not ours). **OURS** = the staged V49b ledger (operator-cited
`47b51fd2`; the staged ledger carries no embedded brain SHA — stated provenance, flagged not forced).
Row-level machine artifacts: `PAR_SHEET_804.csv` (804 rows) · `PAR_SHEET.json`.

## Conservation and the offer reconciliation

- States: **COMPLETE 393 + PARTIAL 357 + NEITHER 54 = 804.** ✓
- Offer: **OFFERED 711 + NO_OFFER 93 = 804 — reconciles EXACTLY with `e995c81b`'s 711/93.** NO_OFFER = par ≥ 100
  or a leg never traded in-window (16 of 1,608 legs had no true print).
- Offered games by state: COMPLETE 393 (all completes are on offered games) · PARTIAL 309 (48 partials sat in
  NO_OFFER games) · NEITHER 9 (45 of the 54 were NO_OFFER — most do-nothing games had nothing to do).
- Lawful skips separated: **2 NEITHER games** are `NO_TWO_SIDED_BOOK` lawful skips (both inside the NO_OFFER 45).

## The headline — cents at par vs cents captured

| | ¢ |
|---|--:|
| **total at par** (711 offered games) | **7,051** |
| **captured** (completes' pair delta) | **1,666 (23.6%)** |
| gap on completes (paid above par) | 3,677 |
| forgone on partials (offered) | 1,666 |
| forgone on neithers (offered) | 42 |
| conservation | 1,666+3,677+1,666+42 = 7,051 ✓ |

Two reads worth stating plainly: the completes themselves only keep **31.2%** of their own par (1,666 of 5,343)
— even winning pairs pay well above the perfect trade; and the partial bucket's forgone par (1,666¢) exactly
equals everything the completes captured — the half-finished games are, at par, a second entire campaign.

## Gap distributions per state × category (offered games; ¢ per game)

| state | cat | n | p25 | med | p75 | max | total |
|---|---|--:|--:|--:|--:|--:|--:|
| COMPLETE | ATP_CHALL | 155 | 1 | 3 | 7 | 91 | 1,512 |
| COMPLETE | ATP_MAIN | 90 | 2 | 4 | 7 | 83 | 943 |
| COMPLETE | WTA_CHALL | 55 | 0 | 1 | 5 | 78 | 493 |
| COMPLETE | WTA_MAIN | 93 | 1 | 3 | 7 | 78 | 729 |
| PARTIAL | ATP_CHALL | 158 | 2 | 3 | 5 | 89 | 887 |
| PARTIAL | ATP_MAIN | 49 | 3 | 5 | 8 | 33 | 313 |
| PARTIAL | WTA_CHALL | 50 | 1 | 2 | 4 | 42 | 196 |
| PARTIAL | WTA_MAIN | 52 | 2 | 3 | 6 | 48 | 270 |
| NEITHER | ATP_CHALL | 5 | 1 | 2 | 3 | 4 | 11 |
| NEITHER | ATP_MAIN | 2 | 1 | 2 | 2 | 3 | 3 |
| NEITHER | WTA_CHALL | 1 | 1 | 1 | 1 | 1 | 1 |
| NEITHER | WTA_MAIN | 1 | 27 | 27 | 27 | 27 | 27 |

Medians are small (2–5¢) in every cell; the totals are driven by long tails (maxes 78–91¢ — deep-par games
where the market briefly offered near-free pairs).

## The mechanism league table — which organ forgoes the most, campaign-wide

Attribution: completes → each credited leg's paid-above-par by its fill authority (`fill_source_state`);
partials → the whole forgone par to the unfilled leg's class; neithers → to the deeper-offered unfilled leg.
Uncredited-leg classes from ledger fields only (cap vs window low, first-action vs low timestamp, withhold
span, rest-at-edge vs low).

| organ (anatomy site) | ¢ forgone | n (legs/games) |
|---|--:|--:|
| **S4/S6 join placement** | **2,133** | 261 |
| **S7/S10 tracking placement** | **1,645** | 235 |
| S16 pair cap | 799 | 159 |
| S7/S10 timing (rest not standing at the low) | 749 | 125 |
| S12 deep-gap guard | 59 | 3 |
| S17 arrived-after-low / S11 no-lawful-rest / lawful-skip / market | 0 | — |
| **total** | **5,385** | = 3,677+1,666+42 ✓ |

**The placement organs are the campaign's whole bill.** S4/S6 + S7/S10 (including timing) = 4,527¢ of 5,385
(84%) — the level chosen, not the gate, not the window. The cap (S16) is third at 799¢ — consistent with its
two prior faces (sealed richness kills, won-pair overpay). The guard, the edge, and lawfulness organs are
noise at par scale. This is the same ordering the overpay census found on won pairs (join > cap > tracking),
now weighted campaign-wide.

## Conservation (full)

804 = 393+357+54 states = 711+93 offer. League cents 2,133+1,645+799+749+59 = 5,385 = total gap
(7,051 − 1,666). Per-state×category n sums: complete 393, partial 309, neither 9 (offered). 1,592/1,608 legs
had a window low; the 16 without sit entirely inside NO_OFFER games. Denominators: dev-804, ledger W1 windows,
fit-local prints, V49b staged ledger. ANALYTICAL_ESTIMATE (organ attribution on uncredited legs uses
edge-snapshot rest levels, not full rest paths).
