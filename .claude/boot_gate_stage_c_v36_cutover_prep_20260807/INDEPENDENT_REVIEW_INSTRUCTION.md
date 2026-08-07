# Independent Stage-C review instruction

Audit runtime commit `896de4108a855abb75fd6bc31330445579f2f2fb` and its Stage-C receipt child.

1. Recompute all Git object types, parentage, blobs, sizes, and SHA-256 values.
2. Reparse all 31 hunks from the immutable `7fb4c9ae.../LIVE_V4_UNCOMMITTED_DIFF.patch`; require one RETIRE/KEEP disposition per hunk and exact `0 KEEP + 31 RETIRE` conservation.
3. Prove the five JS policy files are byte-identical to `bfde0d8d1135f5c5f48a5f3d619ab30050efab83`.
4. Run the 3,456-case JS/Python parity grid, four shadow tests, six exit tests, R3's 18 assertions, compile, and parent/candidate D18 parity.
5. Inspect call graphs: no `v36_shadow_*` result may reach `place_order`, `cancel_order`, API mutation, or position state.
6. Read-only verify VPS HEAD/source hashes, process count zero, inhibited cron/original backup hashes, recorder guard, latest N20 reconciliation, and sealed registry hashes.
7. Treat repository-wide dirty tracked source outside the authorized runtime paths as a launch blocker. PASS may certify Stage-C source preparation only; it may not authorize a boot, cron restore, or live-capital cutover.
