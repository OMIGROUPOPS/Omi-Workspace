# Conduct scoreboard v2

Size-positive reachable fills; queue unknown. FIRST-only, all 928 eligible pairs. No engine replay or edit.

RECEIPT-SIM uses both-leg change points plus atlas receipts. GATE-SIM is the separately retained 15-gate simulation.

- receipt_limitation: Second-close library cadence is not a byte-for-byte engine replay: individual BOOK/PRINT receipt ids and intra-second book ordering are absent. The ask-only veto is reconstructed when only ask changes with unchanged last/bid and no count increment; coincident atlas gates are unconditional gate receipts. FIRST only as the scoreboard order, not the installed BASE fallback. No claim of exact installed-fill equality.
- current: R0: FIRST q50 at each receipt where postable, otherwise existing safety hold/pull. Q/X inherit c7825925, including carried-state remaining minima; no future query timestamps used to predict.
- R1: CLIMBER-ANCHOR: first receipt calling CLIMBER binds stored own seen_true_trade_low forever; faller otherwise R0. No future low lookup.
- R2: NAMED-LEVEL: faller never steps below its highest actually posted level; may move up. Memory survives safety cancellation; climber otherwise R0.
- R3: R1 + R2; a bound climber anchor takes priority even through later role flips.
- R4: R3, except unanchored faller takes FIRST q25 instead of q50 before the same no-downward protection.
- R5: JOINT: FIRST side-mask intersection, original w0 counted once per pair, existing ESS floor required. Historical remaining minima translated by own current last minus member current last. Candidates are observed paired levels only, not a Cartesian product. Probability is sum w0 of pairs whose BOTH minima <= proposed levels / total joint w0. Maximize probability * (par - pair sum) among valid-cent/postable/pair-cap/R2-feasible candidates. Exact objective ties: lower sum, then lower favourite level. After one fill its price is fixed and only the other level varies; same joint outcomes/denominator. No feasible candidate means hold; safety may still pull. These definitions explicitly approved by operator.
- R6: R0 plus no-downward protection on BOTH sides regardless of role, unlike faller-only R2. Highest posted-level memory persists through cancellations; post-only and pair cap always override.

## RECEIPT-SIM

| Rule | Completed / eligible | Completion | Capture mean / median completed | Capture mean / median eligible | One-sided (fav failed / dog failed) | Stepped off | Mean fill→bell m | Safety |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| R0 CURRENT | 375 / 928 | 40.41% | 1.805 / 2.000 | 0.730 / 0.000 | 268 (113 / 155) | 297 (32.00%) | 806.026 | 0 |
| R1 CLIMBER-ANCHOR | 211 / 928 | 22.74% | 2.009 / 2.000 | 0.457 / 0.000 | 393 (244 / 149) | 286 (30.82%) | 827.355 | 0 |
| R2 NAMED-LEVEL | 360 / 928 | 38.79% | 1.647 / 1.000 | 0.639 / 0.000 | 282 (125 / 157) | 0 (0.00%) | 880.870 | 0 |
| R3 ANCHOR+NAMED | 214 / 928 | 23.06% | 1.893 / 2.000 | 0.436 / 0.000 | 384 (237 / 147) | 0 (0.00%) | 908.331 | 0 |
| R4 ANCHOR+Q25-NAMED | 199 / 928 | 21.44% | 2.035 / 2.000 | 0.436 / 0.000 | 379 (233 / 146) | 0 (0.00%) | 774.307 | 0 |
| R5 JOINT | 273 / 928 | 29.42% | 2.015 / 2.000 | 0.593 / 0.000 | 343 (173 / 170) | 0 (0.00%) | 904.350 | 0 |
| R6 ALL-SIDE-SAFETY | 361 / 928 | 38.90% | 1.399 / 1.000 | 0.544 / 0.000 | 294 (132 / 162) | 0 (0.00%) | 944.811 | 0 |

### Matched deltas vs R0

| Rule | Δ completion pp | Δ capture / eligible | Joint completions | Δ capture mean / median joint | Δ one-sided pp | Δ stepped-off pp | Joint filled sides | Δ fill→bell m joint |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| R0 CURRENT | 0.000 | 0.000 | 375 | 0.000 / 0.000 | 0.000 | 0.000 | 1018 | 0.000 |
| R1 CLIMBER-ANCHOR | -17.672 | -0.273 | 193 | 0.187 / 0.000 | 13.470 | -1.185 | 764 | 23.990 |
| R2 NAMED-LEVEL | -1.616 | -0.091 | 342 | -0.155 / 0.000 | 1.509 | -32.004 | 975 | 68.816 |
| R3 ANCHOR+NAMED | -17.349 | -0.293 | 188 | 0.032 / 0.000 | 12.500 | -32.004 | 746 | 106.074 |
| R4 ANCHOR+Q25-NAMED | -18.966 | -0.293 | 175 | 0.251 / 0.000 | 11.961 | -32.004 | 714 | -40.372 |
| R5 JOINT | -10.991 | -0.137 | 226 | 0.204 / 0.000 | 8.082 | -32.004 | 804 | 58.292 |
| R6 ALL-SIDE-SAFETY | -1.509 | -0.185 | 317 | -0.388 / 0.000 | 2.802 | -32.004 | 940 | 144.869 |

## GATE-SIM

| Rule | Completed / eligible | Completion | Capture mean / median completed | Capture mean / median eligible | One-sided (fav failed / dog failed) | Stepped off | Mean fill→bell m | Safety |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| R0 CURRENT | 316 / 928 | 34.05% | 1.731 / 1.000 | 0.589 / 0.000 | 295 (139 / 156) | 80 (8.62%) | 641.010 | 0 |
| R1 CLIMBER-ANCHOR | 169 / 928 | 18.21% | 2.225 / 2.000 | 0.405 / 0.000 | 418 (251 / 167) | 80 (8.62%) | 641.760 | 0 |
| R2 NAMED-LEVEL | 319 / 928 | 34.38% | 1.680 / 1.000 | 0.578 / 0.000 | 300 (144 / 156) | 0 (0.00%) | 645.690 | 0 |
| R3 ANCHOR+NAMED | 172 / 928 | 18.53% | 2.203 / 2.000 | 0.408 / 0.000 | 427 (258 / 169) | 0 (0.00%) | 645.553 | 0 |
| R4 ANCHOR+Q25-NAMED | 138 / 928 | 14.87% | 2.217 / 2.000 | 0.330 / 0.000 | 390 (226 / 164) | 0 (0.00%) | 517.495 | 0 |
| R5 JOINT | 215 / 928 | 23.17% | 2.079 / 2.000 | 0.482 / 0.000 | 357 (191 / 166) | 0 (0.00%) | 666.288 | 0 |
| R6 ALL-SIDE-SAFETY | 328 / 928 | 35.34% | 1.668 / 1.000 | 0.589 / 0.000 | 293 (144 / 149) | 0 (0.00%) | 656.121 | 0 |

### Matched deltas vs R0

| Rule | Δ completion pp | Δ capture / eligible | Joint completions | Δ capture mean / median joint | Δ one-sided pp | Δ stepped-off pp | Joint filled sides | Δ fill→bell m joint |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| R0 CURRENT | 0.000 | 0.000 | 316 | 0.000 / 0.000 | 0.000 | 0.000 | 927 | 0.000 |
| R1 CLIMBER-ANCHOR | -15.841 | -0.184 | 159 | 0.358 / 0.000 | 13.254 | 0.000 | 716 | -8.489 |
| R2 NAMED-LEVEL | 0.323 | -0.012 | 312 | -0.045 / 0.000 | 0.539 | -8.621 | 922 | 8.906 |
| R3 ANCHOR+NAMED | -15.517 | -0.181 | 158 | 0.342 / 0.000 | 14.224 | -8.621 | 715 | 3.332 |
| R4 ANCHOR+Q25-NAMED | -19.181 | -0.260 | 124 | 0.468 / 0.000 | 10.237 | -8.621 | 622 | -141.656 |
| R5 JOINT | -10.884 | -0.108 | 180 | 0.261 / 0.000 | 6.681 | -8.621 | 712 | -3.119 |
| R6 ALL-SIDE-SAFETY | 1.293 | 0.000 | 308 | -0.065 / 0.000 | -0.216 | -8.621 | 917 | 23.707 |

## Five named checks

Fills are resting bid cents; dash = no reachable fill. Every incomplete pair is credited zero.

| Game | Rule | RECEIPT-SIM fills; captured | GATE-SIM fills; captured | Failed legs RECEIPT / GATE |
|---|---|---|---|---|
| 26JUL12GIUBAR | R0 CURRENT | GIU 69, BAR —; 0¢ | GIU 69, BAR —; 0¢ | BAR / BAR |
| 26JUL12GIUBAR | R1 CLIMBER-ANCHOR | GIU 69, BAR —; 0¢ | GIU 69, BAR —; 0¢ | BAR / BAR |
| 26JUL12GIUBAR | R2 NAMED-LEVEL | GIU 69, BAR —; 0¢ | GIU 69, BAR —; 0¢ | BAR / BAR |
| 26JUL12GIUBAR | R3 ANCHOR+NAMED | GIU 69, BAR —; 0¢ | GIU 69, BAR —; 0¢ | BAR / BAR |
| 26JUL12GIUBAR | R4 ANCHOR+Q25-NAMED | GIU 69, BAR —; 0¢ | GIU 69, BAR —; 0¢ | BAR / BAR |
| 26JUL12GIUBAR | R5 JOINT | GIU 67, BAR —; 0¢ | GIU 69, BAR —; 0¢ | BAR / BAR |
| 26JUL12GIUBAR | R6 ALL-SIDE-SAFETY | GIU 69, BAR —; 0¢ | GIU 69, BAR —; 0¢ | BAR / BAR |
| 26JUL14LAJSVA | R0 CURRENT | LAJ 55, SVA —; 0¢ | LAJ 54, SVA —; 0¢ | SVA / SVA |
| 26JUL14LAJSVA | R1 CLIMBER-ANCHOR | LAJ —, SVA —; 0¢ | LAJ —, SVA —; 0¢ | LAJ,SVA / LAJ,SVA |
| 26JUL14LAJSVA | R2 NAMED-LEVEL | LAJ 55, SVA —; 0¢ | LAJ 54, SVA —; 0¢ | SVA / SVA |
| 26JUL14LAJSVA | R3 ANCHOR+NAMED | LAJ —, SVA —; 0¢ | LAJ —, SVA —; 0¢ | LAJ,SVA / LAJ,SVA |
| 26JUL14LAJSVA | R4 ANCHOR+Q25-NAMED | LAJ —, SVA —; 0¢ | LAJ —, SVA —; 0¢ | LAJ,SVA / LAJ,SVA |
| 26JUL14LAJSVA | R5 JOINT | LAJ 55, SVA —; 0¢ | LAJ 52, SVA 46; 2¢ | SVA / none |
| 26JUL14LAJSVA | R6 ALL-SIDE-SAFETY | LAJ —, SVA 48; 0¢ | LAJ 54, SVA —; 0¢ | LAJ / SVA |
| 26JUL14URSPAL | R0 CURRENT | URS —, PAL 43; 0¢ | URS —, PAL 39; 0¢ | URS / URS |
| 26JUL14URSPAL | R1 CLIMBER-ANCHOR | URS —, PAL 40; 0¢ | URS —, PAL 40; 0¢ | URS / URS |
| 26JUL14URSPAL | R2 NAMED-LEVEL | URS —, PAL 43; 0¢ | URS —, PAL 39; 0¢ | URS / URS |
| 26JUL14URSPAL | R3 ANCHOR+NAMED | URS —, PAL 40; 0¢ | URS —, PAL 40; 0¢ | URS / URS |
| 26JUL14URSPAL | R4 ANCHOR+Q25-NAMED | URS —, PAL 40; 0¢ | URS —, PAL 40; 0¢ | URS / URS |
| 26JUL14URSPAL | R5 JOINT | URS 58, PAL —; 0¢ | URS —, PAL —; 0¢ | PAL / URS,PAL |
| 26JUL14URSPAL | R6 ALL-SIDE-SAFETY | URS —, PAL 43; 0¢ | URS —, PAL 39; 0¢ | URS / URS |
| 26JUL12ALTGAS | R0 CURRENT | ALT 60, GAS 39; 1¢ | ALT —, GAS 40; 0¢ | none / ALT |
| 26JUL12ALTGAS | R1 CLIMBER-ANCHOR | ALT —, GAS 39; 0¢ | ALT —, GAS 40; 0¢ | ALT / ALT |
| 26JUL12ALTGAS | R2 NAMED-LEVEL | ALT —, GAS 40; 0¢ | ALT —, GAS 40; 0¢ | ALT / ALT |
| 26JUL12ALTGAS | R3 ANCHOR+NAMED | ALT —, GAS 40; 0¢ | ALT —, GAS 40; 0¢ | ALT / ALT |
| 26JUL12ALTGAS | R4 ANCHOR+Q25-NAMED | ALT —, GAS 40; 0¢ | ALT —, GAS 40; 0¢ | ALT / ALT |
| 26JUL12ALTGAS | R5 JOINT | ALT —, GAS 40; 0¢ | ALT —, GAS 42; 0¢ | ALT / ALT |
| 26JUL12ALTGAS | R6 ALL-SIDE-SAFETY | ALT —, GAS 41; 0¢ | ALT —, GAS 41; 0¢ | ALT / ALT |
| 26JUL18DANPRA | R0 CURRENT | DAN —, PRA —; 0¢ | DAN —, PRA —; 0¢ | DAN,PRA / DAN,PRA |
| 26JUL18DANPRA | R1 CLIMBER-ANCHOR | DAN —, PRA —; 0¢ | DAN —, PRA —; 0¢ | DAN,PRA / DAN,PRA |
| 26JUL18DANPRA | R2 NAMED-LEVEL | DAN —, PRA —; 0¢ | DAN —, PRA —; 0¢ | DAN,PRA / DAN,PRA |
| 26JUL18DANPRA | R3 ANCHOR+NAMED | DAN —, PRA —; 0¢ | DAN —, PRA —; 0¢ | DAN,PRA / DAN,PRA |
| 26JUL18DANPRA | R4 ANCHOR+Q25-NAMED | DAN —, PRA —; 0¢ | DAN —, PRA —; 0¢ | DAN,PRA / DAN,PRA |
| 26JUL18DANPRA | R5 JOINT | DAN —, PRA —; 0¢ | DAN —, PRA —; 0¢ | DAN,PRA / DAN,PRA |
| 26JUL18DANPRA | R6 ALL-SIDE-SAFETY | DAN —, PRA 41; 0¢ | DAN —, PRA —; 0¢ | DAN / DAN,PRA |
