# Vault addendum — Stage C close-out and frozen V36 evidence

Date: 2026-08-07 ET

- The twelve pre-existing tracked VPS modifications are classified KEEP 0 / RETIRE 12. Every byte is recoverable from the controlling final binary patch; no mixed tracked state survives.
- The controlling final preimage is `VPS_TWELVE_PREIMAGE_FINAL.patch.gz`, SHA-256 `3c18133d83a1465813d458f019cf1f28191cfc12fc9c0ef7ee2c807e70432121`, 48,444 bytes. The preliminary patch is superseded because `audit_log.json` changed before the guarded restore.
- The VPS tracked tree is clean at `27596166f03e040a5e38824748dcd88d70bed93b`; engine count is zero; keepalive cron remains inhibited at SHA-256 `405bd4cf5bf9cc59f26f413c07388b35e595f868201af6f10349a878bfecb149`.
- The V36 pack is frozen evidence, not a replay or a new result. Its policy source is commit `bfde0d8d1135f5c5f48a5f3d619ab30050efab83`, SHA-256 `5db3922d5749e11548bca0c301abec19da5e2dfb993ffc17a44ec90989e34f73`; its certified print archive SHA-256 is `e9b5a765b51ddbf0d65364c4f38744ad949ca3c675e5b3a0e472392fbcfabb55`.
- The six examples are ARNROM (living-rest/evidence-take 56+38=94), KIRSEK (deep clean maker), DAHBAE (wide-spread maker-only 93+5=98), LAJVAN (carried wart +4/-8 to own closes), WESPAA (REST_STARVED), and MATMOR (no V36 decision).
- Two clean evidence builds are byte-identical over all 18 generated files / 95,420,227 bytes. Focused tests pass 11/11. Policy invocations, score invocations, shadow launches, engine launches, live-capital accesses, order accesses, position accesses, and cron mutations are all zero.

This addendum closes the twelve-file blocker only. It does not authorize boot, shadow, cutover, cron restoration, or live capital.
