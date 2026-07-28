# Independent Claude Code audit — integrated live safety

Audit `codex/integrated-p0v4-casuka-prerun` without merging it. Do not deploy,
boot, restore cron, run execute mode, or mutate live state.

Controlling identities:

- P0 v4 PRE-RUN: `765083b9bce6940d11a778a862bbd7df14967da4`
- P0 v4 PASS: `cac1a144342de6d99c0d2701e355ce63745063b0`
- CASUKA repair / PASS: `94be41137c0b64bfa448546c8bc3ee7c4ae32a60` / `66136e6240f2adda990ea8fddc7e00cc643cfb4c`
- failed authorization, unusable: `8a142c8623afb498f61be23d4b710af1834c856a`
- integration: `11e70454863e3508d5a7cbc8e83162232e3a4a09` (parent `995a8817c63a118d2bf682339c58c70a3d65f368`)
- rollback: `904a1993030c09c839a56ff78d5a7dc0dfd13b99`
- candidate blob/SHA-256: `d7d7cd1d6e9ca28863e97ed8593e0fbf4c87e223` / `62614501cb9708bb3c3c2b35823ba8431b2e95acdc027f659a4b37a66a777034`
- preimage blob/SHA-256: `f1857199164664037fef41b024e60f27fa373548` / `834b9e04e2cd1781b7f55fdcf80ed90555bd12341b6e98ec75ad4b06d77f1d54`

Recompute the binding correction with real object checks, then reproduce all
five byte-algebra projections and both explained same-boundary insertions.
Verify zero residual bytes; the P0/CASUKA fixture union; SHICHA and 804-event
cold-start behavior; all 21 CASUKA adversarial probes; the one explained
legacy P0 sell-stub interaction; stopped/raw-cron bindings; authorization
fail-closure; P0 readiness before conception; cron restoration only after all
postchecks pass; and parked rollback with zero rollback restart. Rebuild twice
cleanly and exercise only dry-run/no-mutation modes.

On PASS, commit a canonical receipt at `.claude/audit_20260728_integrated_live_safety_prerun/PACKAGE_AUDIT_PASS_RECEIPT.json` from
`PACKAGE_AUDIT_PASS_RECEIPT_TEMPLATE.json`, replacing only
`FINAL_V2_PACKAGE_COMMIT` with the audited package SHA. The verifier consumes
that exact receipt from the separately supplied PASS commit.

Return PASS or BLOCKED. PASS does not deploy. Later authorization must bind the
exact package, PASS, integration, deployment ID, stopped-state/outcome
contracts, and complete ceremony command.
