# Independent deployment-package audit instruction

Audit the final tip of branch
`codex/casuka-live-safety-deployment-prerun` without merging it.

Controlling identities:

- running-source producer:
  `bb085ce06db5932049af85f927a7f9316ad76816`;
- running `live_v4.py` blob:
  `f1857199164664037fef41b024e60f27fa373548`;
- deployment code commit:
  `d256c491c851999047779827bca73de808b5f650`;
- deployment candidate blob:
  `ebd29103ff2153f3d6ced83995c3eb8c159fe38d`;
- audited repair:
  `94be41137c0b64bfa448546c8bc3ee7c4ae32a60`;
- controlling repair PASS:
  `66136e6240f2adda990ea8fddc7e00cc643cfb4c`;
- controlling reproduction:
  `b442908f3b253d1e13d5b2a5e93c3dbf0491320d`.

Independently verify:

1. The final package commit descends from deployment code commit `d256c491`
   and that commit is the sole child in this branch of exact running producer
   `bb085ce0`.
2. Git history independently proves `bb085ce0` introduced blob `f1857199` on
   the frozen VPS lineage, while the receipt-recorded `eca101c6` checkout tree
   contains a different, undeployed file blob.
3. The deployable file set is exactly `arb-executor/live_v4.py`.
4. Candidate source equals exact running blob plus only audited D1-D3
   semantics; no P0 v2/v3 byte or behavior is present.
5. Every named CASUKA method and both D2 blocks are AST-equivalent to repair
   `94be4113`.
6. All five frozen fixtures, all 21 named probes, both organ orderings,
   consecutive-cycle idempotence, and resting-sell conservation pass.
7. FARRIU and VEGKAW cannot be classified filled or pair-incomplete from
   stale membership, zero-booked state, or settlement.
8. The 83-script historical parent surface and 85-script candidate surface
   reproduce with identical 38-failure identity and terminal-cause sets; both
   added tests pass.
9. Compile, AST lint, relevant inherited tests, and exact offline CASUKA smoke
   replay pass.
10. Every source/artifact hash, the complete patch, rollback blob, one-file
    integration law, pre/post invariants, and outcome-proof plan reconcile.
11. No live, network, service, process, configuration, order, position, or
    halt access/mutation occurred.

Return PASS or BLOCKED. A PASS may authorize only a separately operator-bound,
fail-closed deployment ceremony. **Do not deploy, restart, or touch live
state during this audit.**
