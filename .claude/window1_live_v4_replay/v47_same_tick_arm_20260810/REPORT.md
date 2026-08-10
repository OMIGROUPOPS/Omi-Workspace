# V47 same-tick arm - PASS / OPERATIVE

V47 freezes one pipeline-correctness invariant on operative V45: a changed deep-join qualification and the placement decision are one receipt-local operation. Persistence, first-evidence arming, targets, guards, caps, sanity, fill rulers, and the hard edge are unchanged.

- V45_BASELINE: completed 396, under par 396, locked 1936c, naked -162c, true book 1774c, frontier 52/71/142/396; strict 331.
- V47_SAME_TICK_ARM: completed 396, under par 396, locked 1936c, naked -162c, true book 1774c, frontier 52/71/142/396; strict 331.

- Frozen V45 reproduction: PASS.
- SEG_C qualification rows: 1380318; V45/V47 positive qualification-to-post rows 33125/33125; V47 positive scheduler-latency rows 0. Qualification-to-post delay caused by an unchanged guard is reported separately and is not scheduler latency.
- Changed outcomes: 0; changed action streams: 0.
- SURECH remains unfilled as ordered; the 8877c2d5 render is older L4 archetype evidence, not a frozen V45 trace. The executable V45 baseline already posted each unguarded changed join on its qualifying receipt, so V47's correctness invariant yields zero score delta rather than a manufactured gain.
- Named zero-regression checks: PASS.
- Acceptance: zero scheduler latency PASS; zero regressions PASS; gain required NO; overall PASS.
- Market value uses CANON union channels; strict print crossing remains build verification only.
