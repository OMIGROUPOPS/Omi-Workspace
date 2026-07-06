# OPERATOR RULING — B SUB-GRADES (2026-07-06, permanent §0E extension)

**Relayed with the x3 ledger amendment order. Permanent rubric change; every future cut carries it.**

- **B1** = W1-filled pair, cashed in W1/CORRIDOR (missed A only on the W1-cash requirement) — the near-gold class
- **B2** = cashed in W2 (worked, but knife-window only)
- **B3** = completed pair, leg RODE to settlement (the −$132 wing)

Wired 2026-07-06 into: `arb-executor/audit/w1_grading.py` (the nightly grading engine — B splits
after the A→B W1 gate; corridor end = gun_ts else latch_ts, no-boundary → B2 conservative);
`slate_ledger_render.py` (the book's cross-tab, matrix and §4 rollup render on the new letters).
The live monitor's board carries stamps, not letters — its cuts flow through w1_grading (nightly
pass), which now emits the split. First measured split (2026-07-06 book, 197 settled):
A 3 · B1 4 · B2 89 · B3 42 events at pair level; leg-level $: B1 +5.62 / B2 +112.35 / B3 −99.91.
§0E in the Vault (blend/agent-derivation) to be amended with this text at the next Vault pass.
