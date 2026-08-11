# V50-R one-directional first-fill price discipline - BLOCKED / V47 REMAINS OPERATIVE

V50-R bounds only an unhedged prospective first fill by 99 minus the sibling's lowest causal true trade so far. The flow-floor bound lifts on sibling credit; V47's fixed pair cap alone governs the second fill, which remains free to seek its own causal floor. Before sibling flow exists, V47 is unchanged. The clause changes price only: the rest remains live, re-evaluates on each sibling print, and uses no clock.

- V47_BASELINE: completed 396, under par 396, locked 1936c, naked -162c, true book 1774c, frontier 52/71/142/396; strict 331.
- V50_FIRST_FILL_PRICE_DISCIPLINE: completed 385, under par 385, locked 1869c, naked -79c, true book 1790c, frontier 54/65/136/385; strict 311.

- Frozen V47 reproduction: PASS.
- CAP_UNFEASIBLE recovery: 35/192 development V47 CAP_UNFEASIBLE pairs recovered.
- Sealed a20e1a85 evidence remains bound as 45 cases (31 first-fill richness / 14 genuinely infeasible); its later exam identities are not joined to development events.
- Price-bound cost: 184 entries delayed and 116 entries lost.
- Bound receipts: 1932400; violations 0; changed action streams 1604/1604.
- Named: PUTJEA 73; ROCBUE INCOMPLETE; KREZHE 97; ARNROM 97; KRUFER 96; BOSCOP 80.
- Mechanism-bound checks: BLOCKED; gains are reported as observed and never forced.
- Market value uses CANON union channels; strict print crossing remains build verification only.
