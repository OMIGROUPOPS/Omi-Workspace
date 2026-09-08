# Conduct scoreboard — reachable, not certain

FIRST-only atlas-gate comparison; all eligible pairs; no engine replay.

| Rule | Complete / eligible | Rate | Captured mean / median completed | Captured mean / median eligible | One-sided | Stepped off | Fill → bell mean m | Safety |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| R0 CURRENT | 316 / 928 | 34.05% | 1.731 / 1.000 | 0.589 / 0.000 | 295 (31.79%) | 80 (8.62%) | 641.065 | 0 |
| R1 CLIMBER-ANCHOR | 169 / 928 | 18.21% | 2.225 / 2.000 | 0.405 / 0.000 | 418 (45.04%) | 80 (8.62%) | 641.804 | 0 |
| R2 NAMED-LEVEL | 319 / 928 | 34.38% | 1.680 / 1.000 | 0.578 / 0.000 | 300 (32.33%) | 0 (0.00%) | 645.745 | 0 |
| R3 ANCHOR+NAMED | 172 / 928 | 18.53% | 2.203 / 2.000 | 0.408 / 0.000 | 427 (46.01%) | 0 (0.00%) | 645.597 | 0 |
| R4 ANCHOR+Q25-NAMED | 138 / 928 | 14.87% | 2.217 / 2.000 | 0.330 / 0.000 | 390 (42.03%) | 0 (0.00%) | 517.500 | 0 |

## Matched deltas vs R0

| Rule | Δ completion | Δ captured / eligible | Joint completions | Δ capture mean / median, joint |
|---|---:|---:|---:|---:|
| R0 CURRENT | 0.00% | 0.000 | 316 | 0.000 / 0.000 |
| R1 CLIMBER-ANCHOR | -15.84% | -0.184 | 159 | 0.358 / 0.000 |
| R2 NAMED-LEVEL | 0.32% | -0.012 | 312 | -0.045 / 0.000 |
| R3 ANCHOR+NAMED | -15.52% | -0.181 | 158 | 0.342 / 0.000 |
| R4 ANCHOR+Q25-NAMED | -19.18% | -0.260 | 124 | 0.468 / 0.000 |

| Rule | Δ one-sided | Δ stepped-off | Joint filled sides | Δ mean fill → bell m, joint |
|---|---:|---:|---:|---:|
| R0 CURRENT | 0.00% | 0.00% | 927 | 0.000 |
| R1 CLIMBER-ANCHOR | 13.25% | 0.00% | 716 | -8.514 |
| R2 NAMED-LEVEL | 0.54% | -8.62% | 922 | 8.906 |
| R3 ANCHOR+NAMED | 14.22% | -8.62% | 715 | 3.307 |
| R4 ANCHOR+Q25-NAMED | 10.24% | -8.62% | 622 | -141.733 |

## Named checks

Original baseline receipt epochs; fills censored by corrected ruler. A dash is no reachable fill. Incomplete pairs receive zero credit.

| Game | Rule | Fills (bid cents) | Captured cents |
|---|---|---|---:|
| 26JUL12GIUBAR | R0 CURRENT | GIU 69.0, BAR — | 0 |
| 26JUL12GIUBAR | R1 CLIMBER-ANCHOR | GIU 69.0, BAR — | 0 |
| 26JUL12GIUBAR | R2 NAMED-LEVEL | GIU 69.0, BAR — | 0 |
| 26JUL12GIUBAR | R3 ANCHOR+NAMED | GIU 69.0, BAR — | 0 |
| 26JUL12GIUBAR | R4 ANCHOR+Q25-NAMED | GIU 69.0, BAR — | 0 |
| 26JUL14LAJSVA | R0 CURRENT | LAJ 54.0, SVA — | 0 |
| 26JUL14LAJSVA | R1 CLIMBER-ANCHOR | LAJ —, SVA — | 0 |
| 26JUL14LAJSVA | R2 NAMED-LEVEL | LAJ 54.0, SVA — | 0 |
| 26JUL14LAJSVA | R3 ANCHOR+NAMED | LAJ —, SVA — | 0 |
| 26JUL14LAJSVA | R4 ANCHOR+Q25-NAMED | LAJ —, SVA — | 0 |
| 26JUL14URSPAL | R0 CURRENT | URS —, PAL 39.0 | 0 |
| 26JUL14URSPAL | R1 CLIMBER-ANCHOR | URS —, PAL 40.0 | 0 |
| 26JUL14URSPAL | R2 NAMED-LEVEL | URS —, PAL 39.0 | 0 |
| 26JUL14URSPAL | R3 ANCHOR+NAMED | URS —, PAL 40.0 | 0 |
| 26JUL14URSPAL | R4 ANCHOR+Q25-NAMED | URS —, PAL 40.0 | 0 |
| 26JUL12ALTGAS | R0 CURRENT | ALT —, GAS 40.0 | 0 |
| 26JUL12ALTGAS | R1 CLIMBER-ANCHOR | ALT —, GAS 40.0 | 0 |
| 26JUL12ALTGAS | R2 NAMED-LEVEL | ALT —, GAS 40.0 | 0 |
| 26JUL12ALTGAS | R3 ANCHOR+NAMED | ALT —, GAS 40.0 | 0 |
| 26JUL12ALTGAS | R4 ANCHOR+Q25-NAMED | ALT —, GAS 40.0 | 0 |
| 26JUL18DANPRA | R0 CURRENT | DAN —, PRA — | 0 |
| 26JUL18DANPRA | R1 CLIMBER-ANCHOR | DAN —, PRA — | 0 |
| 26JUL18DANPRA | R2 NAMED-LEVEL | DAN —, PRA — | 0 |
| 26JUL18DANPRA | R3 ANCHOR+NAMED | DAN —, PRA — | 0 |
| 26JUL18DANPRA | R4 ANCHOR+Q25-NAMED | DAN —, PRA — | 0 |
