# Sealed regret gauge + miss census + mirror coherence — the 238

Analysis seat only. Read-only. V47 sealed exam (`2bae8931`, STAGE3_ONE_RUN_FINAL_RETRY2). Achievable floor = each leg's `traded_floor_cents` from the sealed MARKET_REGRET_LEDGER (trades-as-truth, post-lawful-stand). Reads = `reach_snapshot.combined_state` at each leg's key moment. Every game's row is in `SEALED_REGRET_GAUGE_238.json` (238 rows). **Caveats flagged**: frozen-path RIGHT/WRONG is not receiptable for the holdout (no reachability artifact; `read_right` is measured vs REALIZED close-vs-entry on the 82 filled legs only); closes exist only for the 82 naked legs.

## Conservation: 238 = 146 completed + 82 one-sided + 10 skips

## Capture efficiency

| ours | best achievable | efficiency |
|--:|--:|--:|
| 571¢ | 3976¢ | **14.4%** |

The sealed tape's trades-as-truth floors offered **3976¢** of pair-lock; V47 banked **571¢ — 14.4%**. The gap is the 146's entry-vs-floor slack (3,164¢) plus the 82/10's missed pairs.

## MIRROR COHERENCE — the new instrument

At each game's sampled decision moments (both legs' key-moment reads), coherent iff B reads as A's inverse (F↔R, S↔S). **Coherence rate: 74/237 = 31.2%** — incoherence is the NORM, not the exception.

| set | incoherent | share |
|---|--:|--:|
| the 146 completed | 93 | 63.7% |
| **the 82 one-sided** | **62** | **75.6%** |

**The operator's contradictory-read class, measured: 62 of 82 misses (75.6%) were mirror-incoherent at decision time** — 12 points above the completed set's rate. Of those, **22** had the filled leg's read RIGHT (vs realized) while the sibling read was not its inverse — the one-eyed pair: one leg saw the game, the other contradicted it, and the contradicted side is the one that never filled.

## THE 146 — pair-gap (ours − best achievable)

| category | n | median ¢ | p75 ¢ | total ¢ |
|---|--:|--:|--:|--:|
| ATP_CHALL | 96 | 15 | 46 | 2570 |
| ATP_MAIN | 24 | 8 | 18 | 382 |
| WTA_CHALL | 9 | 1 | 5 | 91 |
| WTA_MAIN | 17 | 1 | 3 | 121 |
| **ALL** | 146 | **6** | 37 | **3164** |

**ATP_CHALL is the tail** (median 15¢, total 2570¢ of the 3164) — named below: the worst gaps are AUG-10 games whose traded floors crashed to single digits while our entries sat at 98-99.

## THE 82 — filled-leg premium/discount × unfilled geometry

| filled-leg read | WIN | LOSS | FLAT |
|---|--:|--:|--:|
| FALLER/SETTLED | 19 | 24 | 23 |
| RISER | 6 | 4 | 6 |

| unfilled-leg geometry | legs |
|---|--:|
| **CAP_BOUND** | **45** |
| PRETRIGGER | 20 |
| FLOW_ABOVE | 16 |
| FLOW_BELOW | 1 |

**CAP_BOUND dominates the sealed misses (45/82)** — the sibling's floor sat above the 99-minus-entry cap (the dev slate's CAP_UNFEASIBLE organ, confirmed out-of-sample). PRETRIGGER (20) and FLOW_ABOVE (16) are the familiar timing/last-cent classes; FLOW_BELOW is nearly extinct (1).

## THE 10 skips

- **26AUG09ZINKIN** (ATP_CHALL): KIN: floor NONE vs rest 12 (REST_UNFILLED_AT_HARD_PREBELL_EDGE); ZIN: floor NONE vs rest 55 (REST_UNFILLED_AT_HARD_PREBELL_EDGE)
- **26JUL27BRASUL** (ATP_CHALL): BRA: floor 16 vs rest 13 (REST_UNFILLED_AT_HARD_PREBELL_EDGE); SUL: floor 84 vs rest 85 (REST_UNFILLED_AT_HARD_PREBELL_EDGE)
- **26JUL27PINSAM** (ATP_CHALL): PIN: floor 33 vs rest 31 (REST_UNFILLED_AT_HARD_PREBELL_EDGE); SAM: floor 68 vs rest 68 (REST_UNFILLED_AT_HARD_PREBELL_EDGE)
- **26JUL27SEKCHI** (ATP_CHALL): CHI: floor 72 vs rest 70 (REST_UNFILLED_AT_HARD_PREBELL_EDGE); SEK: floor 30 vs rest 28 (REST_UNFILLED_AT_HARD_PREBELL_EDGE)
- **26JUL27WALDON** (ATP_CHALL): DON: floor 44 vs rest 42 (REST_UNFILLED_AT_HARD_PREBELL_EDGE); WAL: floor 57 vs rest 57 (REST_UNFILLED_AT_HARD_PREBELL_EDGE)
- **26JUL28AJDSUL** (ATP_CHALL): AJD: floor 53 vs rest 52 (REST_UNFILLED_AT_HARD_PREBELL_EDGE); SUL: floor 47 vs rest 46 (REST_UNFILLED_AT_HARD_PREBELL_EDGE)
- **26JUL28TURURS** (ATP_CHALL): TUR: floor 38 vs rest 34 (REST_UNFILLED_AT_HARD_PREBELL_EDGE); URS: floor 64 vs rest 60 (REST_UNFILLED_AT_HARD_PREBELL_EDGE)
- **26JUL27QUISHE** (ATP_MAIN): QUI: floor 28 vs rest 26 (REST_UNFILLED_AT_HARD_PREBELL_EDGE); SHE: floor 73 vs rest 71 (REST_UNFILLED_AT_HARD_PREBELL_EDGE)
- **26JUL28MICMCD** (ATP_MAIN): MCD: floor NONE vs rest 27 (REST_UNFILLED_AT_HARD_PREBELL_EDGE); MIC: floor NONE vs rest 18 (REST_UNFILLED_AT_HARD_PREBELL_EDGE)
- **26JUL27ZARKES** (WTA_MAIN): KES: floor 74 vs rest 73 (REST_UNFILLED_AT_HARD_PREBELL_EDGE); ZAR: floor 19 vs rest 26 (REST_UNFILLED_AT_HARD_PREBELL_EDGE)

## Top-10 worst pair-gaps — by name

| gap ¢ | game | disposition | ours | best |
|--:|---|---|--:|--:|
| **96** | 26AUG10BARLEC | COMPLETED | 98 | 2 |
| **96** | 26AUG10ISOMUK | COMPLETED | 98 | 2 |
| **90** | 26AUG10PETMCD | COMPLETED | 99 | 9 |
| **90** | 26AUG10RIBALC | COMPLETED | 99 | 9 |
| **88** | 26AUG09POUSIM | COMPLETED | 99 | 11 |
| **88** | 26AUG10MRVBAS | COMPLETED | 99 | 11 |
| **87** | 26AUG09SAMRYB | COMPLETED | 99 | 12 |
| **84** | 26JUL28MAYDUC | COMPLETED | 99 | 15 |
| **83** | 26AUG10RAWMIT | COMPLETED | 99 | 16 |
| **75** | 26AUG10VANMEC | COMPLETED | 98 | 23 |

Packs (RECEIPT_TIMELINE_V1 from the sealed ACTION_TRACE + DECISION_MARKS — holdout tape not in fit-local, flagged) for the top 3 under `exemplar_packs/sealed_gauge/`: **26AUG10BARLEC · 26AUG10ISOMUK · 26AUG10PETMCD**.

## Conservation

238 rows (146+82+10). Capture 571/3976¢ = 14.4%. Mirror sampled 237, coherent 74 (31.2%); incoherent 82-share 75.6% vs 146-share 63.7%; one-eyed pairs 22. 146 gap total 3164¢. 82 geometry CAP_BOUND 45/PRETRIGGER 20/FLOW_ABOVE 16/FLOW_BELOW 1. Source 2bae8931 sealed V47 (146/571¢/516¢ net reproduced).