# Absorption audit and frozen residual test

Bench only. No engine edit, conduct change, or finalist replay. Historical confirmation — not fresh.

## 1. Absorption audit

| Tour | Month | Measured games / games | Measured intervals | Unobserved | Zero denominator |
| --- | --- | --- | --- | --- | --- |
| ATP_CHALL | 2026-04 | 0/430 | 0 | 333195 | 879585 |
| ATP_CHALL | 2026-05 | 75/541 | 363 | 162038 | 667331 |
| ATP_CHALL | 2026-06 | 435/967 | 1274 | 1099034 | 4116390 |
| ATP_CHALL | 2026-07 | 253/364 | 2094 | 114571 | 1519241 |
| ATP_MAIN | 2026-04 | 0/128 | 0 | 374187 | 628497 |
| ATP_MAIN | 2026-05 | 86/322 | 5615 | 767725 | 2045616 |
| ATP_MAIN | 2026-06 | 306/427 | 5655 | 2436733 | 5733200 |
| ATP_MAIN | 2026-07 | 57/62 | 4002 | 412291 | 862535 |

Both audit bars passed: MAIN 449 and CHALL 763 independent measured games; all 6,482 parts hash verified. No unexplained reconciliation failures. Includes prior best quote. Net replenishment is not gross maker activity.

### Why intervals are unobserved

| Reason | Count |
| --- | --- |
| BOUNDARY_SECOND_ORDER_UNKNOWN | 555210 |
| CONSUMED_LEVEL_NOT_VISIBLE_AT_BOTH_SNAPSHOTS | 2205 |
| CROSSES_FORMATION | 9366 |
| LOCKED_OR_CROSSED_CAPTURE | 4909330 |
| NOT_AVAILABLE_BEFORE_BELL | 1822 |
| UNRESOLVED_DIRECTION_OR_BLOCK_STATUS | 926068 |

Reasons can overlap. Unknown boundary ordering, locked/crossed captures, missing direction/block status, or off-screen consumed levels are not assigned a refill value.

### Availability at the actual model gates

| Phase | Tour | Month | Measured games / gate games | Measured states | Unobserved states | Zero-denominator states |
| --- | --- | --- | --- | --- | --- | --- |
| development | ATP_MAIN | 2026-04 | 0/126 | 0 | 2747 | 3149 |
| development | ATP_MAIN | 2026-05 | 46/315 | 341 | 11633 | 4118 |
| development | ATP_MAIN | 2026-06 | 11/347 | 12 | 8039 | 8185 |
| development | ATP_CHALL | 2026-04 | 0/426 | 0 | 4356 | 9768 |
| development | ATP_CHALL | 2026-05 | 32/529 | 90 | 12050 | 5184 |
| development | ATP_CHALL | 2026-06 | 11/949 | 11 | 12323 | 20282 |
| development | ATP_CHALL | 2026-07 | 0/18 | 0 | 72 | 556 |
| confirmation | ATP_MAIN | 2026-06 | 19/78 | 24 | 1323 | 3097 |
| confirmation | ATP_MAIN | 2026-07 | 10/62 | 18 | 1569 | 1817 |
| confirmation | ATP_CHALL | 2026-07 | 32/342 | 38 | 3073 | 8517 |

Gate states are own-leg bid/ask states; partner copies are not double-counted. The full-span audit bar is distinct from gate-time availability. At model gates only 57 MAIN / 43 CHALL development games and 29 MAIN / 32 CHALL confirmation games had measured refill. Neither tour has a powered gate-level rejection of absorption itself.

## 2. Frozen contract

Frozen before fitting. Full text: [CONTRACT.json](CONTRACT.json). SHA256 `f5fc318b71ee3c01aaa618672f996192ac99ea83c56fac8937a7946e3a18a5d1`.

Separate tours; monthly outer freezes and earlier-resolved inner validation; no named checks. Strictly later positive-size floor before the exact library bell. Match identical games/sides/gates, preserve FIRST coverage, average receipts within games, then weight games equally.

Models: unchanged FIRST; baseline-only residual (first prices, time, receipt role); baseline plus six book blocks. Six single-block diagnostics remain diagnostics. Training-only ranks and eigenvalue-derived ridge strengths; explicit ZERO on missing validation or no inner improvement. Translate the original FIRST distribution; do not clip forecasts.

Bar: n >= 100 independent games; floor-MAE reduction >= 0.10 cents per side; simultaneous 95% interval excluding zero after 36-comparison Bonferroni adjustment; no mean CRPS or coverage deterioration; no unsafe prediction. 50,000 deterministic date-then-game bootstrap draws. BOOK must beat BASE and FIRST.

Latest 140 MAIN / 344 CHALL reserved; frozen models and member pool; one final confirmation phase, interrupted then resumed without refitting. Label: historically inspected — not fresh. True out-of-sample confirmation deferred to LIVE_PAPER after DESK activation.

## 3. Primary results

MAE and CRPS are in cents. Slash-separated values are FIRST / baseline correction / baseline plus book. No corrections were selected in either primary model.

| Phase | Tour | Side | Matched games / eligible | Scored / gate rows | Calls / gates | MAE: FIRST / BASE / BOOK | CRPS: FIRST / BASE / BOOK | Book incremental pass |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| development | ATP_MAIN | favourite | 738/788 | 7832/9556 | 8467/9556 | 1.5414 / 1.5414 / 1.5414 | 1.2376 / 1.2376 / 1.2376 | False |
| development | ATP_MAIN | underdog | 739/788 | 7671/9556 | 8309/9556 | 1.5027 / 1.5027 / 1.5027 | 1.1801 / 1.1801 / 1.1801 | False |
| development | ATP_CHALL | favourite | 1741/1943 | 12218/16173 | 15067/16173 | 2.0498 / 2.0498 / 2.0498 | 1.7567 / 1.7567 / 1.7567 | False |
| development | ATP_CHALL | underdog | 1711/1943 | 12069/16173 | 15079/16173 | 1.8869 / 1.8869 / 1.8869 | 1.5530 / 1.5530 / 1.5530 | False |
| confirmation | ATP_MAIN | favourite | 140/140 | 1888/1962 | 1925/1962 | 1.4625 / 1.4625 / 1.4625 | 1.2243 / 1.2243 / 1.2243 | False |
| confirmation | ATP_MAIN | underdog | 140/140 | 1874/1962 | 1921/1962 | 1.3147 / 1.3147 / 1.3147 | 1.0123 / 1.0123 / 1.0123 | False |
| confirmation | ATP_CHALL | favourite | 322/344 | 2465/2907 | 2893/2907 | 1.4251 / 1.4251 / 1.4251 | 1.1882 / 1.1882 / 1.1882 | False |
| confirmation | ATP_CHALL | underdog | 314/344 | 2351/2907 | 2894/2907 | 1.1640 / 1.1640 / 1.1640 | 0.9329 / 0.9329 / 0.9329 | False |

### Every predeclared contrast

| Phase | Tour | Side | Variant - control | n | Delta MAE | Adjusted MAE interval | Delta CRPS | Pass |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| development | ATP_MAIN | favourite | BASE_CORRECTION - FIRST | 738 | 0.0000 | [0.0, 0.0] | 0.0000 | False |
| development | ATP_MAIN | favourite | BOOK_CORRECTION - FIRST | 738 | 0.0000 | [0.0, 0.0] | 0.0000 | False |
| development | ATP_MAIN | favourite | BOOK_CORRECTION - BASE_CORRECTION | 738 | 0.0000 | [0.0, 0.0] | 0.0000 | False |
| development | ATP_MAIN | favourite | BASE_PLUS_API_FLOW - BASE_CORRECTION | 738 | 0.0000 | [0.0, 0.0] | 0.0000 | False |
| development | ATP_MAIN | favourite | BASE_PLUS_PER_LEVEL_MAKER - BASE_CORRECTION | 738 | 0.0000 | [0.0, 0.0] | 0.0000 | False |
| development | ATP_MAIN | favourite | BASE_PLUS_CONSUMED_LEVEL_REFILL - BASE_CORRECTION | 738 | 0.0000 | [0.0, 0.0] | 0.0000 | False |
| development | ATP_MAIN | favourite | BASE_PLUS_IMBALANCE - BASE_CORRECTION | 738 | 0.0000 | [0.0, 0.0] | 0.0000 | False |
| development | ATP_MAIN | favourite | BASE_PLUS_SPREAD - BASE_CORRECTION | 738 | 0.0000 | [0.0, 0.0] | 0.0000 | False |
| development | ATP_MAIN | favourite | BASE_PLUS_PAIR_GAP - BASE_CORRECTION | 738 | 0.0000 | [0.0, 0.0] | 0.0000 | False |
| development | ATP_MAIN | underdog | BASE_CORRECTION - FIRST | 739 | 0.0000 | [0.0, 0.0] | 0.0000 | False |
| development | ATP_MAIN | underdog | BOOK_CORRECTION - FIRST | 739 | 0.0000 | [0.0, 0.0] | 0.0000 | False |
| development | ATP_MAIN | underdog | BOOK_CORRECTION - BASE_CORRECTION | 739 | 0.0000 | [0.0, 0.0] | 0.0000 | False |
| development | ATP_MAIN | underdog | BASE_PLUS_API_FLOW - BASE_CORRECTION | 739 | 0.0000 | [0.0, 0.0] | 0.0000 | False |
| development | ATP_MAIN | underdog | BASE_PLUS_PER_LEVEL_MAKER - BASE_CORRECTION | 739 | 0.0000 | [0.0, 0.0] | 0.0000 | False |
| development | ATP_MAIN | underdog | BASE_PLUS_CONSUMED_LEVEL_REFILL - BASE_CORRECTION | 739 | 0.0000 | [0.0, 0.0] | 0.0000 | False |
| development | ATP_MAIN | underdog | BASE_PLUS_IMBALANCE - BASE_CORRECTION | 739 | 0.0000 | [0.0, 0.0] | 0.0000 | False |
| development | ATP_MAIN | underdog | BASE_PLUS_SPREAD - BASE_CORRECTION | 739 | 0.0000 | [0.0, 0.0] | 0.0000 | False |
| development | ATP_MAIN | underdog | BASE_PLUS_PAIR_GAP - BASE_CORRECTION | 739 | 0.0000 | [0.0, 0.0] | 0.0000 | False |
| development | ATP_CHALL | favourite | BASE_CORRECTION - FIRST | 1741 | 0.0000 | [0.0, 0.0] | 0.0000 | False |
| development | ATP_CHALL | favourite | BOOK_CORRECTION - FIRST | 1741 | 0.0000 | [0.0, 0.0] | 0.0000 | False |
| development | ATP_CHALL | favourite | BOOK_CORRECTION - BASE_CORRECTION | 1741 | 0.0000 | [0.0, 0.0] | 0.0000 | False |
| development | ATP_CHALL | favourite | BASE_PLUS_API_FLOW - BASE_CORRECTION | 1741 | 0.0000 | [0.0, 0.0] | 0.0000 | False |
| development | ATP_CHALL | favourite | BASE_PLUS_PER_LEVEL_MAKER - BASE_CORRECTION | 1741 | 0.0000 | [0.0, 0.0] | 0.0000 | False |
| development | ATP_CHALL | favourite | BASE_PLUS_CONSUMED_LEVEL_REFILL - BASE_CORRECTION | 1741 | -0.0001 | [-0.00046541572466788267, 0.00020302453276740067] | -0.0000 | False |
| development | ATP_CHALL | favourite | BASE_PLUS_IMBALANCE - BASE_CORRECTION | 1741 | 0.0000 | [0.0, 0.0] | 0.0000 | False |
| development | ATP_CHALL | favourite | BASE_PLUS_SPREAD - BASE_CORRECTION | 1741 | 0.0000 | [0.0, 0.0] | 0.0000 | False |
| development | ATP_CHALL | favourite | BASE_PLUS_PAIR_GAP - BASE_CORRECTION | 1741 | 0.0000 | [0.0, 0.0] | 0.0000 | False |
| development | ATP_CHALL | underdog | BASE_CORRECTION - FIRST | 1711 | 0.0000 | [0.0, 0.0] | 0.0000 | False |
| development | ATP_CHALL | underdog | BOOK_CORRECTION - FIRST | 1711 | 0.0000 | [0.0, 0.0] | 0.0000 | False |
| development | ATP_CHALL | underdog | BOOK_CORRECTION - BASE_CORRECTION | 1711 | 0.0000 | [0.0, 0.0] | 0.0000 | False |
| development | ATP_CHALL | underdog | BASE_PLUS_API_FLOW - BASE_CORRECTION | 1711 | 0.0000 | [0.0, 0.0] | 0.0000 | False |
| development | ATP_CHALL | underdog | BASE_PLUS_PER_LEVEL_MAKER - BASE_CORRECTION | 1711 | 0.0000 | [0.0, 0.0] | 0.0000 | False |
| development | ATP_CHALL | underdog | BASE_PLUS_CONSUMED_LEVEL_REFILL - BASE_CORRECTION | 1711 | 0.0000 | [0.0, 0.0] | 0.0000 | False |
| development | ATP_CHALL | underdog | BASE_PLUS_IMBALANCE - BASE_CORRECTION | 1711 | 0.0000 | [0.0, 0.0] | 0.0000 | False |
| development | ATP_CHALL | underdog | BASE_PLUS_SPREAD - BASE_CORRECTION | 1711 | 0.0000 | [0.0, 0.0] | 0.0000 | False |
| development | ATP_CHALL | underdog | BASE_PLUS_PAIR_GAP - BASE_CORRECTION | 1711 | 0.0000 | [0.0, 0.0] | 0.0000 | False |
| confirmation | ATP_MAIN | favourite | BASE_CORRECTION - FIRST | 140 | 0.0000 | [0.0, 0.0] | 0.0000 | False |
| confirmation | ATP_MAIN | favourite | BOOK_CORRECTION - FIRST | 140 | 0.0000 | [0.0, 0.0] | 0.0000 | False |
| confirmation | ATP_MAIN | favourite | BOOK_CORRECTION - BASE_CORRECTION | 140 | 0.0000 | [0.0, 0.0] | 0.0000 | False |
| confirmation | ATP_MAIN | favourite | BASE_PLUS_API_FLOW - BASE_CORRECTION | 140 | 0.0000 | [0.0, 0.0] | 0.0000 | False |
| confirmation | ATP_MAIN | favourite | BASE_PLUS_PER_LEVEL_MAKER - BASE_CORRECTION | 140 | 0.0000 | [0.0, 0.0] | 0.0000 | False |
| confirmation | ATP_MAIN | favourite | BASE_PLUS_CONSUMED_LEVEL_REFILL - BASE_CORRECTION | 140 | 0.0000 | [0.0, 0.0] | 0.0000 | False |
| confirmation | ATP_MAIN | favourite | BASE_PLUS_IMBALANCE - BASE_CORRECTION | 140 | 0.0000 | [0.0, 0.0] | 0.0000 | False |
| confirmation | ATP_MAIN | favourite | BASE_PLUS_SPREAD - BASE_CORRECTION | 140 | 0.0000 | [0.0, 0.0] | 0.0000 | False |
| confirmation | ATP_MAIN | favourite | BASE_PLUS_PAIR_GAP - BASE_CORRECTION | 140 | 0.0000 | [0.0, 0.0] | 0.0000 | False |
| confirmation | ATP_MAIN | underdog | BASE_CORRECTION - FIRST | 140 | 0.0000 | [0.0, 0.0] | 0.0000 | False |
| confirmation | ATP_MAIN | underdog | BOOK_CORRECTION - FIRST | 140 | 0.0000 | [0.0, 0.0] | 0.0000 | False |
| confirmation | ATP_MAIN | underdog | BOOK_CORRECTION - BASE_CORRECTION | 140 | 0.0000 | [0.0, 0.0] | 0.0000 | False |
| confirmation | ATP_MAIN | underdog | BASE_PLUS_API_FLOW - BASE_CORRECTION | 140 | 0.0000 | [0.0, 0.0] | 0.0000 | False |
| confirmation | ATP_MAIN | underdog | BASE_PLUS_PER_LEVEL_MAKER - BASE_CORRECTION | 140 | 0.0000 | [0.0, 0.0] | 0.0000 | False |
| confirmation | ATP_MAIN | underdog | BASE_PLUS_CONSUMED_LEVEL_REFILL - BASE_CORRECTION | 140 | 0.0000 | [0.0, 0.0] | 0.0000 | False |
| confirmation | ATP_MAIN | underdog | BASE_PLUS_IMBALANCE - BASE_CORRECTION | 140 | 0.0000 | [0.0, 0.0] | 0.0000 | False |
| confirmation | ATP_MAIN | underdog | BASE_PLUS_SPREAD - BASE_CORRECTION | 140 | 0.0000 | [0.0, 0.0] | 0.0000 | False |
| confirmation | ATP_MAIN | underdog | BASE_PLUS_PAIR_GAP - BASE_CORRECTION | 140 | 0.0000 | [0.0, 0.0] | 0.0000 | False |
| confirmation | ATP_CHALL | favourite | BASE_CORRECTION - FIRST | 322 | 0.0000 | [0.0, 0.0] | 0.0000 | False |
| confirmation | ATP_CHALL | favourite | BOOK_CORRECTION - FIRST | 322 | 0.0000 | [0.0, 0.0] | 0.0000 | False |
| confirmation | ATP_CHALL | favourite | BOOK_CORRECTION - BASE_CORRECTION | 322 | 0.0000 | [0.0, 0.0] | 0.0000 | False |
| confirmation | ATP_CHALL | favourite | BASE_PLUS_API_FLOW - BASE_CORRECTION | 322 | 0.0000 | [0.0, 0.0] | 0.0000 | False |
| confirmation | ATP_CHALL | favourite | BASE_PLUS_PER_LEVEL_MAKER - BASE_CORRECTION | 322 | 0.0000 | [0.0, 0.0] | 0.0000 | False |
| confirmation | ATP_CHALL | favourite | BASE_PLUS_CONSUMED_LEVEL_REFILL - BASE_CORRECTION | 322 | -0.0001 | [-0.001886912119659898, 0.0013979753185852292] | 0.0002 | False |
| confirmation | ATP_CHALL | favourite | BASE_PLUS_IMBALANCE - BASE_CORRECTION | 322 | 0.0000 | [0.0, 0.0] | 0.0000 | False |
| confirmation | ATP_CHALL | favourite | BASE_PLUS_SPREAD - BASE_CORRECTION | 322 | 0.0000 | [0.0, 0.0] | 0.0000 | False |
| confirmation | ATP_CHALL | favourite | BASE_PLUS_PAIR_GAP - BASE_CORRECTION | 322 | 0.0000 | [0.0, 0.0] | 0.0000 | False |
| confirmation | ATP_CHALL | underdog | BASE_CORRECTION - FIRST | 314 | 0.0000 | [0.0, 0.0] | 0.0000 | False |
| confirmation | ATP_CHALL | underdog | BOOK_CORRECTION - FIRST | 314 | 0.0000 | [0.0, 0.0] | 0.0000 | False |
| confirmation | ATP_CHALL | underdog | BOOK_CORRECTION - BASE_CORRECTION | 314 | 0.0000 | [0.0, 0.0] | 0.0000 | False |
| confirmation | ATP_CHALL | underdog | BASE_PLUS_API_FLOW - BASE_CORRECTION | 314 | 0.0000 | [0.0, 0.0] | 0.0000 | False |
| confirmation | ATP_CHALL | underdog | BASE_PLUS_PER_LEVEL_MAKER - BASE_CORRECTION | 314 | 0.0000 | [0.0, 0.0] | 0.0000 | False |
| confirmation | ATP_CHALL | underdog | BASE_PLUS_CONSUMED_LEVEL_REFILL - BASE_CORRECTION | 314 | 0.0000 | [0.0, 0.0] | 0.0000 | False |
| confirmation | ATP_CHALL | underdog | BASE_PLUS_IMBALANCE - BASE_CORRECTION | 314 | 0.0000 | [0.0, 0.0] | 0.0000 | False |
| confirmation | ATP_CHALL | underdog | BASE_PLUS_SPREAD - BASE_CORRECTION | 314 | 0.0000 | [0.0, 0.0] | 0.0000 | False |
| confirmation | ATP_CHALL | underdog | BASE_PLUS_PAIR_GAP - BASE_CORRECTION | 314 | 0.0000 | [0.0, 0.0] | 0.0000 | False |

### Primary optimizer outcomes

| Tour | Side | Fit month | Model | Training games | Choice | ZERO inner MAE | Best nonzero inner MAE | Reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ATP_MAIN | favourite | 2026-04 | BASE_CORRECTION | 0 | ZERO | no data | no data | NO_EARLIER_TRAINING |
| ATP_MAIN | favourite | 2026-04 | BOOK_CORRECTION | 0 | ZERO | no data | no data | NO_EARLIER_TRAINING |
| ATP_MAIN | underdog | 2026-04 | BASE_CORRECTION | 0 | ZERO | no data | no data | NO_EARLIER_TRAINING |
| ATP_MAIN | underdog | 2026-04 | BOOK_CORRECTION | 0 | ZERO | no data | no data | NO_EARLIER_TRAINING |
| ATP_MAIN | favourite | 2026-05 | BASE_CORRECTION | 83 | ZERO | no data | no data | NO_INNER_VALIDATION; ZERO_CORRECTION |
| ATP_MAIN | favourite | 2026-05 | BOOK_CORRECTION | 83 | ZERO | no data | no data | NO_INNER_VALIDATION; ZERO_CORRECTION |
| ATP_MAIN | underdog | 2026-05 | BASE_CORRECTION | 86 | ZERO | no data | no data | NO_INNER_VALIDATION; ZERO_CORRECTION |
| ATP_MAIN | underdog | 2026-05 | BOOK_CORRECTION | 86 | ZERO | no data | no data | NO_INNER_VALIDATION; ZERO_CORRECTION |
| ATP_MAIN | favourite | 2026-06 | BASE_CORRECTION | 386 | ZERO | 1.2351 | 1.3543 | ZERO_WEIGHT_BY_VALIDATION; NO_STRICT_INNER_MAE_IMPROVEMENT |
| ATP_MAIN | favourite | 2026-06 | BOOK_CORRECTION | 386 | ZERO | 1.2351 | 1.3556 | ZERO_WEIGHT_BY_VALIDATION; NO_STRICT_INNER_MAE_IMPROVEMENT |
| ATP_MAIN | underdog | 2026-06 | BASE_CORRECTION | 387 | ZERO | 1.2977 | 1.4417 | ZERO_WEIGHT_BY_VALIDATION; NO_STRICT_INNER_MAE_IMPROVEMENT |
| ATP_MAIN | underdog | 2026-06 | BOOK_CORRECTION | 387 | ZERO | 1.2977 | 1.4497 | ZERO_WEIGHT_BY_VALIDATION; NO_STRICT_INNER_MAE_IMPROVEMENT |
| ATP_MAIN | favourite | CONFIRMATION_FROZEN | BASE_CORRECTION | 724 | ZERO | 1.5641 | 1.6609 | ZERO_WEIGHT_BY_VALIDATION; NO_STRICT_INNER_MAE_IMPROVEMENT |
| ATP_MAIN | favourite | CONFIRMATION_FROZEN | BOOK_CORRECTION | 724 | ZERO | 1.5641 | 1.6688 | ZERO_WEIGHT_BY_VALIDATION; NO_STRICT_INNER_MAE_IMPROVEMENT |
| ATP_MAIN | underdog | CONFIRMATION_FROZEN | BASE_CORRECTION | 725 | ZERO | 1.4897 | 1.5811 | ZERO_WEIGHT_BY_VALIDATION; NO_STRICT_INNER_MAE_IMPROVEMENT |
| ATP_MAIN | underdog | CONFIRMATION_FROZEN | BOOK_CORRECTION | 725 | ZERO | 1.4897 | 1.5808 | ZERO_WEIGHT_BY_VALIDATION; NO_STRICT_INNER_MAE_IMPROVEMENT |
| ATP_CHALL | favourite | 2026-04 | BASE_CORRECTION | 0 | ZERO | no data | no data | NO_EARLIER_TRAINING |
| ATP_CHALL | favourite | 2026-04 | BOOK_CORRECTION | 0 | ZERO | no data | no data | NO_EARLIER_TRAINING |
| ATP_CHALL | underdog | 2026-04 | BASE_CORRECTION | 0 | ZERO | no data | no data | NO_EARLIER_TRAINING |
| ATP_CHALL | underdog | 2026-04 | BOOK_CORRECTION | 0 | ZERO | no data | no data | NO_EARLIER_TRAINING |
| ATP_CHALL | favourite | 2026-05 | BASE_CORRECTION | 332 | ZERO | no data | no data | NO_INNER_VALIDATION; ZERO_CORRECTION |
| ATP_CHALL | favourite | 2026-05 | BOOK_CORRECTION | 332 | ZERO | no data | no data | NO_INNER_VALIDATION; ZERO_CORRECTION |
| ATP_CHALL | underdog | 2026-05 | BASE_CORRECTION | 329 | ZERO | no data | no data | NO_INNER_VALIDATION; ZERO_CORRECTION |
| ATP_CHALL | underdog | 2026-05 | BOOK_CORRECTION | 329 | ZERO | no data | no data | NO_INNER_VALIDATION; ZERO_CORRECTION |
| ATP_CHALL | favourite | 2026-06 | BASE_CORRECTION | 815 | ZERO | 1.7785 | 1.9535 | ZERO_WEIGHT_BY_VALIDATION; NO_STRICT_INNER_MAE_IMPROVEMENT |
| ATP_CHALL | favourite | 2026-06 | BOOK_CORRECTION | 815 | ZERO | 1.7785 | 2.1721 | ZERO_WEIGHT_BY_VALIDATION; NO_STRICT_INNER_MAE_IMPROVEMENT |
| ATP_CHALL | underdog | 2026-06 | BASE_CORRECTION | 802 | ZERO | 1.6028 | 1.7440 | ZERO_WEIGHT_BY_VALIDATION; NO_STRICT_INNER_MAE_IMPROVEMENT |
| ATP_CHALL | underdog | 2026-06 | BOOK_CORRECTION | 802 | ZERO | 1.6028 | 1.7583 | ZERO_WEIGHT_BY_VALIDATION; NO_STRICT_INNER_MAE_IMPROVEMENT |
| ATP_CHALL | favourite | 2026-07 | BASE_CORRECTION | 1715 | ZERO | 1.7454 | 1.8283 | ZERO_WEIGHT_BY_VALIDATION; NO_STRICT_INNER_MAE_IMPROVEMENT |
| ATP_CHALL | favourite | 2026-07 | BOOK_CORRECTION | 1715 | ZERO | 1.7454 | 1.8956 | ZERO_WEIGHT_BY_VALIDATION; NO_STRICT_INNER_MAE_IMPROVEMENT |
| ATP_CHALL | underdog | 2026-07 | BASE_CORRECTION | 1685 | ZERO | 1.5451 | 1.6494 | ZERO_WEIGHT_BY_VALIDATION; NO_STRICT_INNER_MAE_IMPROVEMENT |
| ATP_CHALL | underdog | 2026-07 | BOOK_CORRECTION | 1685 | ZERO | 1.5451 | 1.6021 | ZERO_WEIGHT_BY_VALIDATION; NO_STRICT_INNER_MAE_IMPROVEMENT |
| ATP_CHALL | favourite | CONFIRMATION_FROZEN | BASE_CORRECTION | 1721 | ZERO | 1.7473 | 1.8303 | ZERO_WEIGHT_BY_VALIDATION; NO_STRICT_INNER_MAE_IMPROVEMENT |
| ATP_CHALL | favourite | CONFIRMATION_FROZEN | BOOK_CORRECTION | 1721 | ZERO | 1.7473 | 1.8961 | ZERO_WEIGHT_BY_VALIDATION; NO_STRICT_INNER_MAE_IMPROVEMENT |
| ATP_CHALL | underdog | CONFIRMATION_FROZEN | BASE_CORRECTION | 1691 | ZERO | 1.5502 | 1.6556 | ZERO_WEIGHT_BY_VALIDATION; NO_STRICT_INNER_MAE_IMPROVEMENT |
| ATP_CHALL | underdog | CONFIRMATION_FROZEN | BOOK_CORRECTION | 1691 | ZERO | 1.5502 | 1.6079 | ZERO_WEIGHT_BY_VALIDATION; NO_STRICT_INNER_MAE_IMPROVEMENT |

Every fold, candidate, and single-block outcome is in OPTIMIZER_OUTCOMES.json and OPTIMIZER_SUMMARY.json. Missing validation is explicit; rejected fitted candidates are not described as numerical stalls.

## Verification and ruling

The interrupted CHALL zero-atlas game is preserved in denominators. The only runner repair returns no predictions for no receipts; AST comparison proves the rest of the runner unchanged. All 484 reserved games have a checkpoint, including zero-atlas games. No completed game was refitted or reopened by the continuation.

No engine promotion from this run. Primary BASE and BOOK policies selected zero correction in every outer/confirmation fit; see diagnostic block results separately.

This rejects promotion of the specified residual policy, not absorption as a universal mechanism. Inspect gate coverage before claiming refill itself received a powered test. Zero chosen adjustments produce exact zero paired intervals; they do not bound an untested nonzero correction. Out-of-range FIRST calls are disclosed in RUN_RECEIPT, not silently repaired.

Scripts, metadata and aggregates only are published. Private audit intervals stay on droplet; model pickles, training rows and per-receipt scores stay local. Fresh LIVE_PAPER confirmation remains outstanding.
