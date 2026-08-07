# V36 faller-side mirror anatomy

Read-only anatomy of frozen V36 at bfde0d8d1135f5c5f48a5f3d619ab30050efab83 against the b581cbb union-reach gap ledger. No policy or replay was invoked.

Population: 511 faller sides with reach = 399 issue sides + 112 captured controls. Measured issue cents: 1567.

## Miss taxonomy

| class | sides | measured cents |
|---|---:|---:|
| STATE_MISLABELED | 157 | 835 |
| CAP_BOUND | 125 | 412 |
| REST_TOO_SHALLOW | 54 | 273 |
| REST_WALKED_TOO_SLOW | 28 | 47 |
| STRICT_FILL_SEAM_NOT_POLICY | 35 | 0 |

Signal lift is descriptive capture-rate lift against the complete faller control within category and category x price-region. Thin n<20 cells remain marked thin and are never pooled.

Named rows for GANJAN, KRALOR, and WESPAA are frozen in NAMED_GAMES.json. Every issue side has its exact reach evidence, own and sibling snapshot, both clocks, pressure reads, spread/dwell, cap room, action receipt, and full rest-walk history.
