# Window-1 local validation report

## Plain result

- Empirical Window-1 definition: **not selected**. The fit-only candidate grid and selection law are frozen, but missing data prevents boundary sensitivity.
- Validation gate: **failed before event-level comparison**.
- `D`: not computable from local disk.
- `C`: not computed.
- `S`: not computed.
- `C/D >= 75%`: not adjudicated.
- Combined entry cost and combined-vs-par delta: not computed.
- Individual-leg fill-minus-W1-close deltas: not computed.
- Material macrostructure or microstructure variables: not adjudicated.
- Distance from target: not measurable.
- Honest ceiling: not measurable.
- Window 2 and exits: untouched.

The values above are intentionally not printed as zero. Zero would falsely imply an observed denominator and a completed replay.

## Gate blockers

The local checkout lacks the complete event catalog, exact July-12–20 entry order and non-fill receipts, exchange fill clocks, January-present subsecond store, receipt-identifiable public tape, full top-five files, depth-recorder archive, and full WebSocket sequence epochs. July-20 corruption and reconnect gaps cannot be enumerated without the missing archive.

The prior 187-row operational substrate is a non-exhaustive seed ending with one Jul-18 row and no right-edge fields. The tracked live-validation summary lacks exact order identity, ordered quantity, and exchange clocks. Neither can be promoted into ground truth.

## Instrument repair completed locally

`window1_benchmark.py` now enforces:

- all-big-4 default inclusion and one evidence-backed void/cancel exclusion;
- an immutable ledger hash;
- named schedule corridors;
- true-print source allowlisting;
- zero-size-is-zero;
- receipt-identity deduplication;
- exchange-clock ordering;
- full WebSocket epoch requirements;
- exact engine order fingerprints;
- bounded queue uncertainty;
- event-level fill and non-fill comparison with a 100-percent pass rule;
- separate combined-vs-par, pair-reference, and individual-leg-reference metrics;
- physically separate fit and one-shot holdout commands;
- no exit or Window-2 consumption.

Twelve isolated unit tests pass with Python bytecode disabled. They cover the nine defect guards, exact fill, exact non-fill, denominator retention under missing data, and raw `D/C/S` metric separation.

## Work required on the VPS corpus

Normalize the external evidence to `DATA_CONTRACT.md`, run manifest, ledger, and validation, and repair every mismatch until the gate is clean. Only then may the fit policy runner emit boundary, policy, and ablation outcomes. Freeze once on fit and run the holdout command once.

No candidate, ablation, or holdout result is authoritative until those receipts exist.
