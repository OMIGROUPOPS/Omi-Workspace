# Maker results — three fill channels + union

Analysis seat only. Read-only. Same placements (RISER → recurring ask-divot floor;
FALLER/SETTLED → tracking bid−1), lazy-leg-1, cap law, no clock. Three fill channels, each
crediting a resting bid at L:

- **PRINT_CROSS** — a **seller-aggressed** print lands at ≤ L (seller crosses to us).
- **QUOTE_TOUCH** — the leg's ask **descends to ≤ L and dwells** ≥10s (sealed
  `quote_reachability_20260730`).
- **TRADED_AT_LEVEL** — **any** trade prints at ≤ L while the rest stands (any aggressor;
  a counterparty at our price).
- **UNION** — a leg credits once, **deepest evidence (lowest price) wins**.

Machine artifact:
`.claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/MAKER_RESULTS_THREE_CHANNELS.json`.

## The three channels + union (of 804 games / 1,608 legs)

| channel | games both / one / none | sides filled | under-par games | discount median | discount total | **locked ¢ ($)** |
|---|---|--:|--:|--:|--:|--:|
| **PRINT_CROSS** | 501 / 198 / 105 | 1,200 | 456 | −1¢ | −1,795¢ | 4,541 ($45.41) |
| **QUOTE_TOUCH** | 692 / 0 / 112 | 1,384 | 392 | −1¢ | −1,930¢ | 1,171 ($11.71) |
| **TRADED_AT_LEVEL** | 773 / 11 / 20 | 1,557 | 604 | −1¢ | −2,395¢ | 5,057 ($50.57) |
| **UNION** | **785 / 0 / 19** | **1,570** | **637** | −1¢ | **−2,606¢** | **5,253 ($52.53)** |

**Frontier (both-sides games at combined tier):**

| channel | ≤93 | ≤95 | ≤97 | <100 |
|---|--:|--:|--:|--:|
| PRINT_CROSS | 97 | 140 | 237 | 456 |
| QUOTE_TOUCH | 37 | 74 | 154 | 392 |
| TRADED_AT_LEVEL | 117 | 167 | 312 | 604 |
| **UNION** | **120** | **183** | **345** | **637** |

## Reading the channels

- **QUOTE_TOUCH is the floor of the floors** — dwell-verified ask descents are the
  *shallowest* fills (only $11.71 locked), because a sustained ask sits above the
  momentary trades. This is why the print model was stamped underfloor: it credited
  levels the dwelled ask never reached.
- **TRADED_AT_LEVEL is the deepest single channel** — any trade at our level, regardless
  of aggressor, fills **604** under-par games for **$50.57**: a buyer lifting a low ask
  prints just as validly at our price as a seller hitting it, and those prints reach
  deeper than either the seller-only cross or the dwelled ask.
- **UNION recovers the most** — **637 under-par games, $52.53**, 785 of 804 both-sides
  filled, only 19 games with no fill. Each channel catches evidence the others miss;
  taking the deepest per leg is the fullest honest maker book.

## Discount per fill (fill − own pre-match close)

Every channel's median discount is **−1¢** (maker fills sit a cent under the close); the
depth is in the tail and totals: PRINT_CROSS −1,795¢, QUOTE_TOUCH −1,930¢, TRADED_AT_LEVEL
−2,395¢, UNION **−2,606¢** across all filled sides.

## Delta to par per game (100 − combined) — UNION

Under-par games **637**; locked p25 / median / p75 with the frontier above; **total 5,253¢
($52.53) at 1-lot** (maker-only, zero fee). PRINT_CROSS 4,541¢, TRADED_AT_LEVEL 5,057¢,
QUOTE_TOUCH 1,171¢.

## Named rows — combined per channel

| game | PRINT_CROSS | QUOTE_TOUCH | TRADED_AT_LEVEL | **UNION** | locked (union) |
|---|--:|--:|--:|--:|--:|
| **NIKVRB** | 100 | 86 | 88 | **86** | 14¢ |
| **BOSCOP** | 75 | 91 | 75 | **75** | **25¢** |
| **ARNROM** | 89 | 93 | 88 | **88** | 12¢ |

**BOSCOP** is the clearest recovery: the dwelled ask only reached combined 91 (COP's ask
sat at 63), but a **trade printed at COP's deep 47** — so TRADED_AT_LEVEL (and print-cross)
recover BOSCOP to **combined 75 / 25¢ locked**, which quote-touch alone missed. **ARNROM**:
quote-touch 93 (7¢) → TRADED_AT_LEVEL 88 (ARN 50 / ROM 38), **12¢** locked at union.
**NIKVRB** stays deep on the quote/traded channels (union 86 / 14¢); its seller-cross was
shallow (100).

## Conservation

804 games, 1,608 legs, every channel. UNION: 785 both-sides + 0 one + 19 none = 804;
1,570 filled + 38 unfilled = 1,608. PRINT_CROSS 501/198/105, QUOTE_TOUCH 692/0/112,
TRADED_AT_LEVEL 773/11/20 (all sum 804). Under-par 456 / 392 / 604 / 637; locked 4,541 /
1,171 / 5,057 / **5,253¢**. Discount totals −1,795 / −1,930 / −2,395 / −2,606¢. Prints
scanned 373,203 (sealed reconciliation set). Per category × bell-confidence with min-n in
the artifact.
