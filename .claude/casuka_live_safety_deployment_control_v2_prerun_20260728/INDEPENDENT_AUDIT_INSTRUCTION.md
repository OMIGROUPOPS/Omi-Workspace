# Independent audit instruction — CASUKA deployment-control V2

Audit the final tip of `codex/casuka-live-safety-deployment-control-v2`
without merging it. Do not deploy or run execute mode.

Controlling identities:

- V1 package: `ccf95e464ead48ca99cef0be62bc65c6ae8ba832`
- V1 package PASS: `1e62d7e4a2aa4d38e6e71b5e0271725f7e3a6f0e`
- failed authorization, now unusable: `8a142c8623afb498f61be23d4b710af1834c856a`
- integration: `164f13f70b9c8c89faf26dfc4c65767ab1265404` (parent `b060dabacad7bd384cf01b6490da8b529db3474c`)
- rollback: `a6dd0686c7406f2211e60f32ce8d85e74aebb90f`
- candidate blob/SHA-256: `ebd29103ff2153f3d6ced83995c3eb8c159fe38d` /
  `85fdd653ee85dd598388d3cf6f537999decf0f0bdece6b8b3495a19041ee05d4`
- preimage blob/SHA-256: `f1857199164664037fef41b024e60f27fa373548` /
  `834b9e04e2cd1781b7f55fdcf80ed90555bd12341b6e98ec75ad4b06d77f1d54`

Independently verify the integration and rollback trees, candidate byte
identity, P0 exclusion, verifier fail-closure, every adversarial case,
one-shot runner phases, T-0 definitions, outcome contract, post-result schema,
mandatory rollback, source/artifact hashes, and two clean deterministic
regenerations. Exercise only dry-run/no-mutation modes.

On PASS, commit a canonical receipt at:
`.claude/audit_20260728_casuka_deployment_control_v2/PACKAGE_AUDIT_PASS_RECEIPT.json` using
`PACKAGE_AUDIT_PASS_RECEIPT_TEMPLATE.json` with only
`FINAL_V2_PACKAGE_COMMIT` replaced by the audited package SHA. The verifier
requires this exact receipt from the separately supplied PASS commit.

Return PASS or BLOCKED. A PASS does not deploy; a later separate authorization
must bind the exact package, PASS, integration, deployment ID, active outcome
contract, and ceremony command.
