# Deep-pair autopsy + rest adverse-selection census — V35 / V35.1 vs V34-W1

Analysis seat only. Read-only. V34-W1 `e56d79a2`, V35 `0799fba` (living-rest, retained),
V35.1 `3f073c4` (directional-evidence-aging, **rejected**). Machine artifact:
`.claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/DEEP_PAIR_AUTOPSY_V35.json`.

## Headline — the living rest trades depth for volume

| | STRICT completed | STRICT deep ≤95 | CENSUS completed | CENSUS deep ≤95 |
|---|--:|--:|--:|--:|
| V34-W1 | 254 | **34** | 279 | 39 |
| V35 | 264 | 25 | 550 | 91 |
| V35.1 | **283** | **24** | 552 | 89 |

V35→V35.1 raise total strict completions (254→283) but the **deep (≤95) pairs fall
34→24**. The living/tracking rest fills *more* pairs and *shallower* ones.

## (1) The vanished deep pairs — 32 of 34

Of V34-W1's 34 strict deep pairs, **32 vanish or degrade in V35.1**: **8 LOST** (not
completed at all) + **24 WORSE** (completed at a higher combined). Only 2 survive.
Mechanism per leg: **TAKE_FIRED_SHALLOWER 18 · REST_SWEPT_SHALLOWER 13 · LOST_FILL 10**.
The take path firing at a higher evidence-floor is the dominant deep-pair killer.

| exemplar | V34 combined | V35.1 combined | mechanism |
|---|--:|--:|---|
| **GANJAN** | **23** | **99** | JAN take fired **+76c shallower** — deepest pair in the book collapses to barely-under-par |
| FETPIE | 87 | LOST | FET take +23c shallower; PIE rest never filled |
| JONSPI | 63 | LOST | both legs' rests unfilled at the edge |

## (2) Rest adverse selection — 143 strict maker fills

Depth of fill vs the leg's eventual pre-bell seller-hit low (`adverse = entry − low`;
>0 = filled above where the leg later traded):

| | n | median | mean | p90 | max | at/below low |
|---|--:|--:|--:|--:|--:|--:|
| all maker fills | 125 | **−1¢** | +1.5¢ | 5¢ | 56¢ | **95/125 (76%)** |

**State at fill (169 maker fills incl. census): RISING 140 · FALLING 23 · SETTLED 6.**
The living rest is *mostly well-selected* — 76% fill at or below the eventual low, and
140/169 catch a seller dumping into a **rising** book (price rose after: non-adverse).
The adverse tail (to +56¢) is the **23 FALLING fills** — the rest swept **mid-decline**,
filled before the leg kept falling. That tail, not the median, is the deep-pair leak on
the maker side. Per-category adverse medians all ≤0 (ATP_CHALL/ATP_MAIN/WTA_MAIN −1,
WTA_CHALL 0).

## (3) Census depth check — 50 census-only deep pairs (≤95)

50 games are census-completed at ≤95 but not strict-completed. Per game the census
credits a one-cent residency conversion against a seller-aggressed near-miss print.
**Only 1 of 50 assumes more than the 1c rule** — the rest are honest 1c conversions
(census entry = near-miss print price − 1). Exemplars: **BOSCOP** (80), **MUNLEO** (94),
**OUALIN** (20) — all within the 1c rule. *(Computed 50 census-only deep for V35.1; the
operator's "67" appears to reference V35's cut or a broader threshold — flagged, not
forced.)*

## (4) The untouched — 248, all offerable

**248 games complete by neither strict nor census in V35.1.** Every one of the 248 is in
the **680 offer** (under-par completable per the full-lawful ceiling). Primary blocker:
**246 `HARD_RIGHT_EDGE_REACHED_WITH_REST_UNFILLED`** (the living rest never got hit) + 2
`NO_OWN_TWO_SIDED_BOOK`. Exemplars: BARREI (both legs' rests unfilled), BARVIS, BINGIL.
The living rest improved *placement* but 248 offerable pairs still die because the rest,
though tracking, is never swept — the take path can't rescue them on a maker-only book.

## Verdict

V35.1's rejection is earned by this autopsy: the directional-evidence-aging living rest
**buys shallow volume at the cost of deep pairs** (34→24 deep, 32 of V34's 34 gone),
mostly because the **take fires at a shallower evidence-floor** (18 legs) rather than a
maker-placement fault — the maker fills themselves are 76% non-adverse. The floor under
everything is still the unswept rest: 248 offerable pairs, 246 blocked by rest-unfilled.

## Conservation

804 = 283 V35.1-strict + 269 census-only + 248 untouched + 4 strict-only-not-census.
Deep ≤95: V34 34 → V35 25 → V35.1 24. Vanished 32 = 8 LOST + 24 WORSE. Maker fills 169
(143 strict): RISING 140 + FALLING 23 + SETTLED 6. Census-only deep 50 (1 over-1c).
Untouched 248 (248 in offer; 246 rest-unfilled + 2 no-book).
