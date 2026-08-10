# The 315 gap map — against the true traded offer

Analysis seat only. Read-only. V48 trades-as-truth (`e073c606`): a standing rest credits when **any true trade prints at-or-below its level strictly after the rest stood**. For every game **under-par by the traded floor** that V48 did **not** complete, per missing leg: the completing print vs our rest. Machine artifact: `…/THE_315_GAP_MAP.json`; packs under `exemplar_packs/v48_gapmap/`.

## Population — measured vs V48's stated

My traded-floor universe (deepest in-window true print per leg, both legs sum < 100) = **604 under-par**; V48 completed 322 of them → **gap = 282**. **Flagged**: V48's own traded-floor re-sum reports **711 under-par / 315 gap** — 107 more than mine, a definitional difference (V48 back-fills no-trade legs and/or uses a wider print set). I report my measured set; the class shape below is robust to the count.

## The gap classes — where the completing print fell relative to our rest

| gap class | missing legs |
|---|--:|
| **PRINT_ABOVE_REST (we bid under)** | 183 |
| **PRINT_BEFORE_REST_STOOD (ordering, LUZTSE class)** | 123 |
| **REST_ABSENT (no lawful rest yet)** | 4 |
| **PRINT_AT_REST_UNCREDITED (bug flag — should be 0)** | 0 |
| **total** | **310** |

**PRINT_AT_REST_UNCREDITED = 0** — V48's crediting law is sound; **no leg had a trade land at-or-below a standing rest and go uncredited**. Every miss is upstream of crediting:
- **PRINT_ABOVE_REST (183, 59%)** — the deepest trade stayed **above our rest by k = median 2¢** (p75 3¢, max 52¢). We bid 1-3¢ under the market's real trade; a placement/greed gap.
- **PRINT_BEFORE_REST_STOOD (123, 40%)** — the completing trade (at-or-below our eventual rest) **printed before the rest lawfully stood** — the LUZTSE ordering class. The offer was there; we weren't yet.
- **REST_ABSENT (4)** — the trade came before any rest was placed.

## Per category

| class | ATP_CHALL | ATP_MAIN | WTA_CHALL | WTA_MAIN |
|---|--:|--:|--:|--:|
| PRINT_ABOVE_REST | 91 | 37 | 23 | 32 |
| PRINT_BEFORE_REST_STOOD | 65 | 10 | 37 | 11 |
| REST_ABSENT | 2 | 2 | 0 | 0 |

ATP_CHALL dominates both faults; ATP_MAIN skews PRINT_ABOVE (we sit under), WTA_CHALL skews PRINT_BEFORE (ordering).

## Print-moment taxonomy — when the completing trade fired

| moment (T-minus to edge) | completing prints |
|---|--:|
| EARLY (>3h) | 167 |
| MID (1-3h) | 77 |
| LATE (10-60m) | 51 |
| BELL_APPROACH (<10m) | 15 |

**The completing trades cluster EARLY** (167 of 310, 54%) — deep prints landing long before the rest could lawfully stand, feeding PRINT_BEFORE_REST_STOOD. Only 15 fired in the final 10 minutes. The offer is an *early* phenomenon; the persistence-gated rest is a *late* one — the ordering mismatch is structural.

## Top-10 diagnosable — by name

| value ¢ | game·leg | gap class | completing print | our rest | T-minus | moment |
|--:|---|---|--:|--:|--:|---|
| **88** | 26JUL18LUZTSE·TSE | print before rest stood | 1¢ (sz 1.0) | 79¢ | 1071s | LATE |
| **79** | 26JUL13KHOZHA·KHO | print before rest stood | 6¢ (sz 5.0) | 77¢ | 3853s | MID |
| **69** | 26JUL13PANFAL·FAL | print before rest stood | 30¢ (sz 25.0) | 44¢ | 9629s | MID |
| **69** | 26JUL13PANFAL·PAN | print before rest stood | 1¢ (sz 1.0) | 54¢ | 2417s | LATE |
| **66** | 26JUL13SHIHUA·HUA | print before rest stood | 1¢ (sz 6.81) | 60¢ | 6048s | MID |
| **61** | 26JUL18COLCER·COL | print before rest stood | 1¢ (sz 15.69) | 59¢ | 5940s | MID |
| **60** | 26JUL18MCASHI·MCA | print before rest stood | 1¢ (sz 1.0) | 50¢ | 5267s | MID |
| **60** | 26JUL18MCASHI·SHI | print before rest stood | 39¢ (sz 6.91) | 48¢ | 8842s | MID |
| **58** | 26JUL13PENTHA·PEN | print before rest stood | 22¢ (sz 7.0) | 76¢ | 1622s | LATE |
| **58** | 26JUL13PENTHA·THA | print before rest stood | 20¢ (sz 1.0) | 22¢ | 5433s | MID |

The high-value gap is **PRINT_BEFORE_REST_STOOD**-dominated: LUZTSE·TSE (1¢ at T-1071s, rest 79 — the deep print long before the 79 join stood), KHOZHA, PANFAL, SHIHUA, COLCER. These are ordering losses, not placement — the fix is an earlier lawful stand, not a lower bid.

## Top-3 packs

`DUAL_TIMELINE_V2 + DECISION_MARKS` (with the completing-print receipt per leg) under `exemplar_packs/v48_gapmap/`: **LUZTSE · KHOZHA · PANFAL**.

## Conservation

Gap 282 games (V48 stated 315 — flagged), 310 missing legs each one class: PRINT_ABOVE 183 + PRINT_BEFORE 123 + REST_ABSENT 4 + PRINT_AT_REST_UNCREDITED 0 = 310. PRINT_ABOVE k median 2¢. Timing EARLY 167 / MID 77 / LATE 51 / BELL 15. Source V48 e073c606, prints fit-local, closes 57daf3c1.