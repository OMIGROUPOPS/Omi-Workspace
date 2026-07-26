# Window-1 Range-Attack scoring package PRE-RUN

This additions-only package freezes a deterministic scorer and execution
surface for the two V2 Range-Attack candidates. It does **not** authorize or
perform development scoring.

- Parent V2 PRE-RUN: `851346343eecbff64bd836992876592784874c86`
- Controlling PASS audit: `5579b93774267779ae916eb9cb46766de66a9efe`
- Candidates: `w1_range_attack__macro_hold__combined_headroom`, `w1_range_attack__macro_micro__combined_headroom`
- D per candidate: 804
- Target PC: 603
- Input-bundle SHA-256: `549717d97f08bff4b9e57a7eef06c576de5c9cb2cd28e77fd6556b41e021f2d8`
- Sole fill source: guarded V2 `PRICE_FILLABILITY_RECEIPTS`
- Guarded strict-ask eligibility: 26; raw causal strict-ask actions are not a role
- Reference: last deduplicated positive true print in `[T-8h, V5 guarded cutoff]`
- Ranking/selection: forbidden
- C / PC / S / IC: null
- Execution: not authorized and not performed

A future execute invocation requires a new independent PASS audit commit that
explicitly binds the package commit, execution ID, bundle hash, and exact
command. The unresolved audit note about independently confirming V2
regeneration is preserved in `SCORING_INPUT_MANIFEST.json`.
