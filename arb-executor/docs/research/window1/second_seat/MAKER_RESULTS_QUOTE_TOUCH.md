# The maker results table — quote-touch fill law (Jul-30 divot doctrine)

Analysis seat only. Read-only. Fill law: a resting bid at L is credited when the leg's
ask descends to ≤ L and **dwells** (tiers 10/30/60s) — reuses the sealed
`quote_reachability_20260730` floor limits (nothing recomputed). Placement per the vaulted
schedule hypothesis: RISER → recurring ask-divot floor; FALLER/SETTLED → tracking bid−1.
Pair coupling lazy-leg-1, cap law, no clock. Print-model results (`d40bc010`/`be8f8d18`)
stamped **`PRINT_MODEL_UNDERFLOOR`**. Machine artifact:
`.claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/MAKER_RESULTS_QUOTE_TOUCH.json`.

## GAMES (of 804) — quote-touch, per dwell tier

| dwell | both sides | one side | none |
|---|--:|--:|--:|
| **10s** | **692** | 0 | 112 |
| 30s | 692 | 0 | 112 |
| 60s | 692 | 0 | 112 |

## SIDES (of 1,608) — filled count & fill price

| dwell | sides filled | fill price p25 / median / p75 |
|---|--:|---|
| **10s** | **1,384** | 32 / **49** / 66 |
| 30s | 1,384 | 32 / 49 / 67 |
| 60s | 1,384 | 32 / 49 / 67 |

## MAKER FILL VALUE — discount to own pre-match close (fill − close)

| dwell | n | p25 / median / p75 | total |
|---|--:|---|--:|
| **10s** | 1,307 | −2 / **−1** / 0 | **−1,930¢** |
| 30s | 1,307 | −2 / −1 / 0 | −1,887¢ |
| 60s | 1,307 | −2 / −1 / 0 | −1,838¢ |

Maker fills sit a median **1¢ below** the close — a thin dwell-verified discount, not the
deep momentary spikes the print model counted.

## DELTA TO PAR — both-sides games, 100 − combined = locked cents

| dwell | under-par games | locked p25/median/p75 | frontier ≤93/≤95/≤97/<100 | **locked total** |
|---|--:|---|---|--:|
| **10s** | **392** | 1 / **2** / 4 | 37 / 74 / 154 / 392 | **1,171¢ ($11.71)** |
| 30s | 384 | 1 / 2 / 4 | 35 / 72 / 149 / 384 | 1,129¢ ($11.29) |
| 60s | 378 | 1 / 2 / 4 | 33 / 70 / 142 / 378 | 1,082¢ ($10.82) |

## Per category × bell-confidence (quote-touch 10s; min-n law)

| cell | pairs | locked ¢ | evidence |
|---|--:|--:|---|
| ATP_CHALL · live_by | 198 | 328 | native n≥30 |
| ATP_CHALL · exact | 108 | 232 | native n≥30 |
| ATP_MAIN · live_by | 77 | 173 | native n≥30 |
| WTA_MAIN · live_by | 61 | 114 | native n≥30 |
| WTA_MAIN · exact | 49 | 62 | native n≥30 |
| WTA_CHALL · live_by | 48 | 17 | native n≥30 |
| WTA_CHALL · exact | 40 | 24 | native n≥30 |
| ATP_MAIN · exact | 37 | 128 | native n≥30 |
| ATP_CHALL · schedule | 22 | 24 | POOLED (<30) |
| WTA_MAIN · schedule | 11 | 22 | POOLED (<30) |
| WTA_MAIN · clean_interval | 8 | 2 | POOLED (<30) |

By category (10s): ATP_CHALL 202 pairs / 605¢ · ATP_MAIN 94 / 316¢ · WTA_MAIN 72 / 205¢ ·
WTA_CHALL 24 / 45¢.

## Side by side — divot recovery vs the print-model baseline

| model | under-par games | locked ¢ |
|---|--:|--:|
| **print-model baseline** (`d40bc010`, PRINT_MODEL_UNDERFLOOR) | **106** | **2,003** |
| quote-touch **10s** | **392** | 1,171 |
| quote-touch 30s | 384 | 1,129 |
| quote-touch 60s | 378 | 1,082 |
| (CSV print-floor, Jul-30) | 519 | 1,632 |

The quote-touch law completes **3.7× more under-par games** (392 vs 106) but locks **fewer
total cents** (1,171 vs 2,003): the dwell-verified ask floors sit **above** the momentary
seller-hit prints the print model credited — so the print model's deep floors were an
underfloor (unreachable by a resting bid), and the realistic book is wider but thinner.

## Named rows

| game | leg (dir) | close | print floor | q10 | q30 | q60 | q10 disc |
|---|---|--:|--:|--:|--:|--:|--:|
| **NIKVRB** | NIK (FALLING) | 19 | 18 | 18 | 18 | 18 | −1 |
| | VRB (CLIMBING) | 83 | 70 | **68** | 68 | 68 | **−15** |
| | combined | — | 88 | **86** | 86 | 86 | locked **14¢** |
| **BOSCOP** | BOS | 28 | 28 | 28 | 29 | 29 | 0 |
| | COP | 72 | **47** | **63** | 71 | 71 | −9 |
| | combined | — | **75** | **91** | **100** | 100 | locked 9¢ (10s only; ≥30s not under par) |
| **ARNROM** | ARN | 62 | **50** | **56** | 56 | 56 | −7 |
| | ROM | 39 | 38 | 38 | 38 | 38 | −1 |
| | combined | — | 88 | **93** | 94 | 94 | locked 7¢ |

NIKVRB stays a genuine deep pair (VRB's climbing-side ask-divot floor 68, −15¢ to close;
combined 86 / 14¢ locked). BOSCOP and ARNROM show the underfloor plainly: COP's print floor
47 was a spike — the dwelled ask only reached 63 (10s) / 71 (30–60s), pushing BOSCOP to par
by 30s; ARN's print floor 50 vs the dwelled 56 (the tick-story qualifying floor), combined
93 / 7¢ locked.

## Conservation

804 games = 692 both-sides + 0 one-side + 112 none (q10, all tiers). 1,608 legs = 1,384
filled + 224 unfilled. Under-par games 392/384/378 at 10/30/60s; locked 1,171/1,129/1,082¢.
Discount over 1,307 filled sides with a known close. Print-model baseline 106 games /
2,003¢.
