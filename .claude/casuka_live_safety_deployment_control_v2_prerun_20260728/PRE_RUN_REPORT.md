# CASUKA deployment-control V2 PRE-RUN

Status: **FROZEN FOR INDEPENDENT AUDIT — NOT DEPLOYED**

V2 is an additions-only child of V1 package `ccf95e464ead48ca99cef0be62bc65c6ae8ba832`. It preserves
candidate blob `ebd29103ff2153f3d6ced83995c3eb8c159fe38d` byte-for-byte and does not modify
`live_v4.py` or `deploy_live_v4.sh`.

The exact file-only integration commit is `164f13f70b9c8c89faf26dfc4c65767ab1265404`, whose sole parent
is verified VPS HEAD `b060dabacad7bd384cf01b6490da8b529db3474c`. Its only changed path is
`arb-executor/live_v4.py`. Exact rollback commit `a6dd0686c7406f2211e60f32ce8d85e74aebb90f` is its sole
child and restores preimage blob `f1857199164664037fef41b024e60f27fa373548`.

The V1 authorization `8a142c8623afb498f61be23d4b710af1834c856a` is structurally superseded and
cannot authorize V2. It consumed zero attempts.

V2 supplies:

- a directly runnable authorization verifier;
- a one-shot phase-journaled ceremony controller;
- an active immutable pre-deployment outcome-proof contract;
- a separate post-deployment evidence schema;
- exact deploy and rollback command literals;
- fail-closed single-use, T-0, postcheck, and rollback laws.

Truthful boundary: `deploy_live_v4.sh` does **not itself** consume
`OUTCOME_PROOF`. The ceremony controller validates the contract, materializes
an immutable runtime copy under the single-use results path, and supplies it
to the unchanged child deploy gate.

No deployment, restart, remote backup, live results directory, order,
position, configuration, halt, or T2 mutation occurred.
