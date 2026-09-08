# CEILINGS — ATP_MAIN, RECEIPT-SIM

Bench only. Same 928 eligible pairs; 609,960 archived receipts. Reachable fills, not certain fills. Queue position unknown.

| Diagnostic | Completed | One-sided | Neither | Captured / eligible (cents) | Captured / completed (cents) | Completed sum > par | Ever commitment > par |
|---|---:|---:|---:|---:|---:|---:|---:|
| C0 R0 | 375 (40.4095%) | 268 (28.8793%) | 285 | 0.729526 | 1.805333 | 0 (0.0000% of eligible) | 0 (0.0000%) |
| C1 ORACLE SENTENCE | 607 (65.4095%) | 82 (8.8362%) | 239 | 3.207974 | 4.904448 | 0 (0.0000% of eligible) | 0 (0.0000%) |
| C2 BUDGET RELEASED | 525 (56.5733%) | 124 (13.3621%) | 279 | 0.134698 | 0.238095 | 143 (15.4095% of eligible) | 194 (20.9052%) |

C1 changes only Q to the strictly later positive-size print floor. Original authority status, X, books, cadence and every guard remain. No future print means absent oracle Q. This is a foresight diagnostic under this policy, not a mathematical supremum over all sentences/conduct.

C2 disables only the pair-budget guard. UNSAFE DIAGNOSTIC, NEVER CONDUCT. Individual price bounds, authority fence and post-only/book rules remain. Above-par completion produces negative capture; incomplete pairs receive zero credit. Independent nominal-budget exposure audit accompanies simulator safety counters.

## Matched all-eligible deltas versus R0

| Diagnostic | Completion delta (pp) | One-sided delta (pp) | Captured / eligible delta (cents) |
|---|---:|---:|---:|
| C0 R0 | +0.0000 | +0.0000 | +0.000000 |
| C1 ORACLE SENTENCE | +25.0000 | -20.0431 | +2.478448 |
| C2 BUDGET RELEASED | +16.1638 | -15.5172 | -0.594828 |

## C3 — baseline R0 fill order

Current sentence = latest receipt strictly before the fill. Premium = filled bid minus that Q; placement-Q premium is separate. Effective underdog cap = nominal pair budget minus favourite filled/resting commitment at the first-fill timestamp. Headroom = effective cap minus current Q_dog. Simultaneous fills are ties, not an invented order.

| Outcome | First side | Pairs | Premium to current Q: q10/q25/q50/q75/q90 | Dog headroom: q10/q25/q50/q75/q90 | Negative / zero / positive headroom |
|---|---|---:|---|---|---|
| COMPLETED | favourite | 258 | 0 / 0 / 0 / 0 / 0 | 0 / 1 / 1 / 2 / 3 | 13 / 42 / 186 (missing 17) |
| COMPLETED | underdog | 117 | 0 / 0 / 0 / 0 / 1 | 0 / 0 / 1 / 3 / 7 | 3 / 31 / 76 (missing 7) |
| COMPLETED | SAME_TIMESTAMP | 0 | missing / missing / missing / missing / missing | missing / missing / missing / missing / missing | 0 / 0 / 0 (missing 0) |
| ONE_SIDED | favourite | 155 | 0 / 0 / 0 / 0 / 0 | -1 / 0 / 1 / 2 / 3 | 16 / 42 / 82 (missing 15) |
| ONE_SIDED | underdog | 113 | -1 / 0 / 0 / 0 / 1 | 0 / 1 / 1 / 4 / 68 | 5 / 21 / 83 (missing 4) |
| ONE_SIDED | SAME_TIMESTAMP | 0 | missing / missing / missing / missing / missing | missing / missing / missing / missing / missing | 0 / 0 / 0 (missing 0) |

Full distributions (including means, missing values, fill minutes-to-bell and placement-Q premiums), pair-level evidence, input hashes and unchanged-engine checks are in the adjacent JSON and receipt. No causal attribution is inferred from C3's observational headroom.
