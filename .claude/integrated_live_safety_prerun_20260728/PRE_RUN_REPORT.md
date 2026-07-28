# Integrated P0 REAL-START v1-v4 + CASUKA D1-D3 PRE-RUN

Status: **FROZEN FOR INDEPENDENT AUDIT — NOT DEPLOYED**

This additions-only package is the sole child of P0 v4 PRE-RUN
`765083b9bce6940d11a778a862bbd7df14967da4`. The deployable candidate exists only in file-only commit
`11e70454863e3508d5a7cbc8e83162232e3a4a09` and has blob `d7d7cd1d6e9ca28863e97ed8593e0fbf4c87e223`, SHA-256
`62614501cb9708bb3c3c2b35823ba8431b2e95acdc027f659a4b37a66a777034`, and 1,047,115 bytes. This package does not
modify inherited `live_v4.py` or `deploy_live_v4.sh`.

The integration commit's computed parent is VPS HEAD `995a8817c63a118d2bf682339c58c70a3d65f368`;
its only changed path is `arb-executor/live_v4.py`. Rollback commit
`904a1993030c09c839a56ff78d5a7dc0dfd13b99` is its sole child and restores `f1857199164664037fef41b024e60f27fa373548` while leaving
the engine stopped and keepalive cron inhibited.

`P0_BINDING_CORRECTION_RECEIPT.json` corrects the P0 audit material-binding
defect. Every operative commit is validated by both required object checks;
parents, trees, and blobs are computed from Git. The malformed historical
value appears only as superseded evidence in that receipt.

CASUKA-only authorization `8a142c8623afb498f61be23d4b710af1834c856a` and source-material package
`135f3efae1c3d6f4e7fbcbab658f41b4733a403c` cannot authorize this integrated candidate.

The package supplies an executable verifier, a phase-journaled one-shot
controller, a GET-only paginated T-0 census, an immutable outcome contract,
post-result schema, exact deploy and parked-rollback literals, and exact cron
restoration only after every post-boot invariant passes.

`deploy_live_v4.sh` does **not itself** consume `OUTCOME_PROOF`; the controller
enforces it. Read-only construction revalidation found process count 0, raw
inhibited cron SHA `0e2af22e4ab536b4273e61d9251359eda71e369fb8591f22443c66aa88709926`, zero tennis entry buys, and 10
exits / 40 contracts covering all whole-contract holdings (40.58 total with
the named 0.58 residue).

No deployment, boot, restart, backup, live results directory, order,
position, configuration, cron restoration, authorization, scoring,
performance measurement, or T2 mutation occurred. Deployment/performance
result fields are null.
