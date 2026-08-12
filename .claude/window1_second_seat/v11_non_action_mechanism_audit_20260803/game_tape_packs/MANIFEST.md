# Game tape packs - five exemplars (raw series only)

Source, coverage, caveats: MANIFEST.json (same directory). Rest paths are V49b LEDGER ANCHORS ONLY
(no ACTION_TRACE in the staged brain) - do not interpolate a continuous rest line. Book gaps >600s are
listed per leg: quiet-or-outage undistinguishable (no heartbeat channel) - flagged, not smoothed.
Trades reconcile per leg with TAPE_VS_EXCHANGE_DIFF @ db470ec8 (column `reconciles`).

| game | leg | book rows (chg) | trades | true | diff ours_n | reconciles | gaps>600s |
|---|---|--:|--:|--:|--:|---|--:|
| 26JUL16MERDRO | DRO | 5600 | 289 | 289 | 289 | True | 6 |
| 26JUL16MERDRO | MER | 2290 | 702 | 702 | 702 | True | 7 |
| 26JUL12POLKUH | KUH | 3174 | 13 | 13 | 13 | True | 5 |
| 26JUL12POLKUH | POL | 2598 | 18 | 18 | 18 | True | 8 |
| 26JUL19ARSMAR | ARS | 678 | 7 | 7 | 7 | True | 12 |
| 26JUL19ARSMAR | MAR | 445 | 13 | 13 | 13 | True | 12 |
| 26JUL13SANDAN | DAN | 1257 | 113 | 113 | 113 | True | 8 |
| 26JUL13SANDAN | SAN | 2036 | 46 | 46 | 46 | True | 10 |
| 26JUL14PUTJEA | JEA | 945 | 4 | 4 | 4 | True | 16 |
| 26JUL14PUTJEA | PUT | 925 | 6 | 6 | 6 | True | 12 |
