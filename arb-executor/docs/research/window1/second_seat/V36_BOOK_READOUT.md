# The V36 book — full results readout (state-directional, bfde0d8)

Analysis seat only. Read-only. V36 `v36_state_directional_rest_mature_floor` STRICT ledger
on the 804, certified tapes, `prints.jsonl` for the swing paths. Machine artifact:
`.claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/V36_BOOK_READOUT.json`.
V36 was **rejected**; this is its book.

## (1) The haul

| | count |
|---|--:|
| legs credited | **1,035 / 1,608** |
| completed pairs | **270 / 804** |
| one-legged games | **495** |
| skips (zero-fill) | **39** |
| maker fills | 153 |
| taker fills | **882** |

Conservation: 270×2 + 495 = 1,035 legs; 270 + 495 + 39 = 804 games. Overwhelmingly a
**taker book** (882/1035 = 85%). Credited legs by category: ATP_CHALL 469 · ATP_MAIN 207 ·
WTA_MAIN 197 · WTA_CHALL 162. By bell: live_by 556 · exact 305 · schedule 100 · clean 44
· contradictory 30. One-legged side is spread across many players (VAN 9, BAS/MAR/SAN 7…) —
no structural bias to one leg.

## (2) The discount — V36 buys *at* the close, not below it

Per-leg fill minus own pre-match close (telemetry):

| | p25 | median | p75 | mean | total |
|---|--:|--:|--:|--:|--:|
| discount (entry − close) | −2¢ | **0¢** | +2¢ | +0.03¢ | **+30¢** |

**The discount is essentially zero.** V36 fills at the pre-match closing line (median 0,
symmetric ±2). Per category the median is 0 everywhere (totals −134 ATP_CHALL … +106
WTA_MAIN — noise). The book does **not** capture a per-leg edge; whatever margin it holds
comes from the *pair sum*, not the individual price.

**Locked margin per completed pair (100 − combined):**

| | median | mean | total | max |
|---|--:|--:|--:|--:|
| locked margin | **1¢** | 2.48¢ | **670¢** | 68¢ |

270 pairs lock a **median 1¢** and mean 2.48¢ of margin — **razor-thin**; total book
locked margin **670¢**. Per cat: WTA_CHALL mean 3.83 (best), ATP_CHALL 2.7 (one 68¢
outlier), ATP_MAIN 2.01, WTA_MAIN 1.83. This is a marginal-arb book: it completes pairs
barely under par, not deep.

## (3) The swing — post-fill to bell, then to settlement

Bought-YES excursions after each fill (favorable = price up):

| horizon | MFE median | MAE median | drift median | mean | total |
|---|--:|--:|--:|--:|--:|
| fill → bell | **+2¢** | **−2¢** | close-drift 0¢ | — | — |
| fill → settlement | — | — | **−7¢** | +0.8¢ | +742¢ |

**Pre-bell is quiet and symmetric**: ±2¢ MFE/MAE, close-drift 0 — the price barely moves
between fill and bell, and the fill sits at the close. **Post-bell explodes**:
settlement drift spans p25 −38¢ / p75 +41¢ (the match resolving one leg to ~99, the
other to ~1), median −7¢ but mean ≈0 — pure resolution variance, no directional edge.
By category the pre-bell swing is uniform (MFE +1..2 / MAE −1..−2); by entry region the
mid-book (51_75, ge76) skews slightly favorable (MFE +2 / MAE −1) vs the cheap tails
(le25, 26_50: MFE +1 / MAE −2).

## (4) The one-legged book — carrying an unpaired side through the bell

495 naked legs (483 with a price path):

| | value |
|---|--:|
| MFE → bell (median) | +0¢ |
| MAE → bell (median) | −2¢ |
| close-drift (median / total) | −1¢ / **−992¢** |
| settlement: **won / lost** | **212 / 263** |
| settlement drift total | **+214¢** |

Carrying a naked side is a **coin-flip that leans loser** — 263 settle low vs 212 high —
yet the drift **nets +214¢** because the naked legs are cheap (a loss costs entry→0, a win
pays entry→99). Pre-bell they bleed slightly (close-drift total −992¢: the unpaired side
drifts ~1–2¢ against us into the close). Net of the whole one-legged book: small positive,
high variance — **carrying unpaired sides is noise, not skill.**

## Patterns & surprises

- **Discount is flat vs time-to-bell** — median 0¢ whether filled <60m or >24h before the
  bell. V36 pays the close regardless of how early it acts; there is no early-bird edge.
- **Swing symmetry** — MFE ≈ −MAE (+2 / −2) across every category and region; no
  systematic post-fill drift before the bell. The book has no directional read.
- **Surprise 1:** zero per-leg discount despite 882 takes — the "state-directional
  mature-floor" take fires *at* the qualified close, capturing no price edge; the entire
  book value is the 670¢ of pair-sum margin.
- **Surprise 2:** the one-legged book loses more often than it wins (263>212) yet nets
  positive — the cheapness of the fillable side, not selection, carries it.

## Conservation

804 = 270 pairs + 495 one-legged + 39 skips. 1,035 credited = 270×2 + 495. Discount over
1,033 legs (total +30¢); locked margin over 270 pairs (total 670¢). Swing MFE/MAE over
1,014 path-bearing legs; settlement over 923. One-legged 495 (483 path, 475 settled).
