# V46 pair-gated gap credit - BLOCKED / V45 REMAINS OPERATIVE

V46 adds one clause to frozen operative V45: on a FALLING leg with an existing rest, a single-receipt ask gap of at least 3 cents licenses a reprice down only after the game's other expression is already credited. Without sibling credit the V45 action stream is unchanged. The reprice posts at min(current ask minus one, pair cap); fills still require an inherited later market-union or strict-print receipt.

- V45_BASELINE: completed 396, under par 396, locked 1936c, naked -162c, true book 1774c, frontier 52/71/142/396; strict 331.
- V46_PAIR_GATED_GAP_CREDIT: completed 396, under par 396, locked 1936c, naked -162c, true book 1774c, frontier 52/71/142/396; strict 331.

- Frozen V45 reproduction: PASS.
- Gap-credit walks: 5 across 3 legs; filled 0.
- Two columns: completion gains 0; new exposure 0.
- Sibling-uncredited refusal receipts: 12650 across 1057 legs. The frozen aa884cc5 footprint's 11 naked-knife legs / median +44c remain an analytical binding, not a coerced replay count.
- PANFAL INCOMPLETE: ORDERED_NAMED_OUTCOME_IS_UNREACHABLE_UNDER_THE_ORDERED_PAIR_GATE_BECAUSE_NEITHER_EXPRESSION_IS_CREDITED_BEFORE_THE_PAN_GAP.
- ARNROM 89; KIRSEK 24; KRUFER 96; BOSCOP 80.
- Bar: completed >=396 PASS; true book >1774c FAIL; zero bound regressions FAIL; named FAIL; overall BLOCKED.
- Market value uses CANON union channels; strict print crossing remains build verification only.
