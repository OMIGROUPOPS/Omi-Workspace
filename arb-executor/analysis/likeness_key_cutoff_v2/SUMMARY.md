# Native-cutoff challenge

Bench only. Push held. V1 could not select the native control. Exact-membership audit passed before the new fits.

Validation losses below are equal-game CRPS on exact-control-callable earlier receipts. April has no comparable earlier validation. No zeros are substituted.
Raw model-curve rows with missed_reference_calls > 0 are ineligible partial-support diagnostics, NOT comparable validation scores; their accumulator values must not be ranked or treated as a zero-loss forecast.
All calendar selectors retain FIRST weights. Older = actual positive mass on a member formed before 2026-04-18 UTC. Historical tests are not fresh.

## ATP_MAIN

| Month | Validation games | Family | Exact control CRPS | Date control CRPS | Selected | Selected CRPS | Best older | Older CRPS | Older wins validation? |
|---|---:|---|---:|---:|---|---:|---|---:|---|
| 2026-04 | 0 | COMBINED_SELECTORS | no comparable history | no comparable history | FIRST_EXACT_TICK_MEMBERS | no comparable history | none | no comparable history | False |
| 2026-04 | 0 | COMBINED_WEIGHT | no comparable history | no comparable history | FIRST_EXACT_TICK_MEMBERS | no comparable history | none | no comparable history | False |
| 2026-04 | 0 | ERA_SELECTOR | no comparable history | no comparable history | FIRST_EXACT_TICK_MEMBERS | no comparable history | none | no comparable history | False |
| 2026-04 | 0 | ERA_WEIGHT | no comparable history | no comparable history | FIRST_EXACT_TICK_MEMBERS | no comparable history | none | no comparable history | False |
| 2026-05 | 95 | COMBINED_SELECTORS | 1.38971 | 1.38971 | FIRST_EXACT_TICK_MEMBERS | 1.38971 | COMBINED_SELECTORS:0.25,0.25,0.1 | 1.50457 | False |
| 2026-05 | 95 | COMBINED_WEIGHT | 1.38971 | 1.38971 | FIRST_EXACT_TICK_MEMBERS | 1.38971 | FIRST_SINCE_2026-03 | 1.66321 | False |
| 2026-05 | 95 | ERA_SELECTOR | 1.38971 | 1.38971 | FIRST_EXACT_TICK_MEMBERS | 1.38971 | ERA_SELECTOR:0.1 | 1.60622 | False |
| 2026-05 | 95 | ERA_WEIGHT | 1.38971 | 1.38971 | FIRST_EXACT_TICK_MEMBERS | 1.38971 | FIRST_SINCE_2026-03 | 1.66321 | False |
| 2026-06 | 407 | COMBINED_SELECTORS | 1.01485 | 1.01485 | FIRST_EXACT_TICK_MEMBERS | 1.01485 | COMBINED_SELECTORS:0.25,0.25,0.1 | 1.43767 | False |
| 2026-06 | 407 | COMBINED_WEIGHT | 1.01485 | 1.01485 | FIRST_EXACT_TICK_MEMBERS | 1.01485 | FIRST_SINCE_2026-03 | 1.54846 | False |
| 2026-06 | 407 | ERA_SELECTOR | 1.01485 | 1.01485 | FIRST_EXACT_TICK_MEMBERS | 1.01485 | ERA_SELECTOR:0.25 | 1.49835 | False |
| 2026-06 | 407 | ERA_WEIGHT | 1.01485 | 1.01485 | FIRST_EXACT_TICK_MEMBERS | 1.01485 | FIRST_SINCE_2026-03 | 1.54846 | False |
| 2026-07 | 783 | COMBINED_SELECTORS | 1.13972 | 1.13972 | FIRST_EXACT_TICK_MEMBERS | 1.13972 | COMBINED_SELECTORS:0.25,0.5,0.1 | 1.37415 | False |
| 2026-07 | 783 | COMBINED_WEIGHT | 1.13972 | 1.13972 | FIRST_EXACT_TICK_MEMBERS | 1.13972 | FIRST_SINCE_2026-02 | 1.65480 | False |
| 2026-07 | 783 | ERA_SELECTOR | 1.13972 | 1.13972 | FIRST_EXACT_TICK_MEMBERS | 1.13972 | ERA_SELECTOR:0.25 | 1.41232 | False |
| 2026-07 | 783 | ERA_WEIGHT | 1.13972 | 1.13972 | FIRST_EXACT_TICK_MEMBERS | 1.13972 | FIRST_SINCE_2026-02 | 1.65480 | False |

### Test: selected family and best older-admitting challenger

| Month | Key | Side | Matched games | Floor MAE new / exact | Timing MAE new / exact | CRPS new / exact |
|---|---|---|---:|---:|---:|---:|
| 2026-04 | ERA_SELECTOR | favourite | 90 | 1.5506 / 1.5506 | 99.342 / 99.342 | 1.3012 / 1.3012 |
| 2026-04 | ERA_SELECTOR | underdog | 92 | 1.5374 / 1.5374 | 116.635 / 116.635 | 1.2061 / 1.2061 |
| 2026-04 | ERA_WEIGHT | favourite | 90 | 1.5506 / 1.5506 | 99.342 / 99.342 | 1.3012 / 1.3012 |
| 2026-04 | ERA_WEIGHT | underdog | 92 | 1.5374 / 1.5374 | 116.635 / 116.635 | 1.2061 / 1.2061 |
| 2026-04 | COMBINED_WEIGHT | favourite | 90 | 1.5506 / 1.5506 | 99.342 / 99.342 | 1.3012 / 1.3012 |
| 2026-04 | COMBINED_WEIGHT | underdog | 92 | 1.5374 / 1.5374 | 116.635 / 116.635 | 1.2061 / 1.2061 |
| 2026-04 | COMBINED_SELECTORS | favourite | 90 | 1.5506 / 1.5506 | 99.342 / 99.342 | 1.3012 / 1.3012 |
| 2026-04 | COMBINED_SELECTORS | underdog | 92 | 1.5374 / 1.5374 | 116.635 / 116.635 | 1.2061 / 1.2061 |
| 2026-04 | ERA_SELECTOR_BEST_OLDER | favourite | 90 | 1.5506 / 1.5506 | 99.342 / 99.342 | 1.3012 / 1.3012 |
| 2026-04 | ERA_SELECTOR_BEST_OLDER | underdog | 92 | 1.5374 / 1.5374 | 116.635 / 116.635 | 1.2061 / 1.2061 |
| 2026-04 | ERA_WEIGHT_BEST_OLDER | favourite | 90 | 1.5506 / 1.5506 | 99.342 / 99.342 | 1.3012 / 1.3012 |
| 2026-04 | ERA_WEIGHT_BEST_OLDER | underdog | 92 | 1.5374 / 1.5374 | 116.635 / 116.635 | 1.2061 / 1.2061 |
| 2026-04 | COMBINED_WEIGHT_BEST_OLDER | favourite | 90 | 1.5506 / 1.5506 | 99.342 / 99.342 | 1.3012 / 1.3012 |
| 2026-04 | COMBINED_WEIGHT_BEST_OLDER | underdog | 92 | 1.5374 / 1.5374 | 116.635 / 116.635 | 1.2061 / 1.2061 |
| 2026-04 | COMBINED_SELECTORS_BEST_OLDER | favourite | 90 | 1.5506 / 1.5506 | 99.342 / 99.342 | 1.3012 / 1.3012 |
| 2026-04 | COMBINED_SELECTORS_BEST_OLDER | underdog | 92 | 1.5374 / 1.5374 | 116.635 / 116.635 | 1.2061 / 1.2061 |
| 2026-05 | ERA_SELECTOR | favourite | 314 | 1.0739 / 1.0739 | 88.139 / 88.139 | 0.8301 / 0.8301 |
| 2026-05 | ERA_SELECTOR | underdog | 314 | 1.1872 / 1.1872 | 109.870 / 109.870 | 0.8694 / 0.8694 |
| 2026-05 | ERA_WEIGHT | favourite | 314 | 1.0739 / 1.0739 | 88.139 / 88.139 | 0.8301 / 0.8301 |
| 2026-05 | ERA_WEIGHT | underdog | 314 | 1.1872 / 1.1872 | 109.870 / 109.870 | 0.8694 / 0.8694 |
| 2026-05 | COMBINED_WEIGHT | favourite | 314 | 1.0739 / 1.0739 | 88.139 / 88.139 | 0.8301 / 0.8301 |
| 2026-05 | COMBINED_WEIGHT | underdog | 314 | 1.1872 / 1.1872 | 109.870 / 109.870 | 0.8694 / 0.8694 |
| 2026-05 | COMBINED_SELECTORS | favourite | 314 | 1.0739 / 1.0739 | 88.139 / 88.139 | 0.8301 / 0.8301 |
| 2026-05 | COMBINED_SELECTORS | underdog | 314 | 1.1872 / 1.1872 | 109.870 / 109.870 | 0.8694 / 0.8694 |
| 2026-05 | ERA_SELECTOR_BEST_OLDER | favourite | 314 | 1.2425 / 1.0688 | 97.234 / 85.115 | 0.9568 / 0.8260 |
| 2026-05 | ERA_SELECTOR_BEST_OLDER | underdog | 314 | 1.2727 / 1.1834 | 109.519 / 106.356 | 0.9458 / 0.8676 |
| 2026-05 | ERA_WEIGHT_BEST_OLDER | favourite | 314 | 1.7647 / 1.0739 | 129.595 / 88.139 | 1.4127 / 0.8301 |
| 2026-05 | ERA_WEIGHT_BEST_OLDER | underdog | 314 | 1.9073 / 1.1872 | 137.616 / 109.870 | 1.5102 / 0.8694 |
| 2026-05 | COMBINED_WEIGHT_BEST_OLDER | favourite | 314 | 1.7647 / 1.0739 | 129.595 / 88.139 | 1.4127 / 0.8301 |
| 2026-05 | COMBINED_WEIGHT_BEST_OLDER | underdog | 314 | 1.9073 / 1.1872 | 137.616 / 109.870 | 1.5102 / 0.8694 |
| 2026-05 | COMBINED_SELECTORS_BEST_OLDER | favourite | 314 | 1.5447 / 1.0739 | 125.695 / 88.139 | 1.2688 / 0.8301 |
| 2026-05 | COMBINED_SELECTORS_BEST_OLDER | underdog | 314 | 1.7997 / 1.1872 | 136.031 / 109.870 | 1.4316 / 0.8694 |
| 2026-06 | ERA_SELECTOR | favourite | 425 | 1.7090 / 1.7090 | 113.529 / 113.529 | 1.3592 / 1.3592 |
| 2026-06 | ERA_SELECTOR | underdog | 425 | 1.5112 / 1.5112 | 112.309 / 112.309 | 1.1663 / 1.1663 |
| 2026-06 | ERA_WEIGHT | favourite | 425 | 1.7090 / 1.7090 | 113.529 / 113.529 | 1.3592 / 1.3592 |
| 2026-06 | ERA_WEIGHT | underdog | 425 | 1.5112 / 1.5112 | 112.309 / 112.309 | 1.1663 / 1.1663 |
| 2026-06 | COMBINED_WEIGHT | favourite | 425 | 1.7090 / 1.7090 | 113.529 / 113.529 | 1.3592 / 1.3592 |
| 2026-06 | COMBINED_WEIGHT | underdog | 425 | 1.5112 / 1.5112 | 112.309 / 112.309 | 1.1663 / 1.1663 |
| 2026-06 | COMBINED_SELECTORS | favourite | 425 | 1.7090 / 1.7090 | 113.529 / 113.529 | 1.3592 / 1.3592 |
| 2026-06 | COMBINED_SELECTORS | underdog | 425 | 1.5112 / 1.5112 | 112.309 / 112.309 | 1.1663 / 1.1663 |
| 2026-06 | ERA_SELECTOR_BEST_OLDER | favourite | 425 | 1.7084 / 1.7090 | 110.984 / 113.529 | 1.3786 / 1.3592 |
| 2026-06 | ERA_SELECTOR_BEST_OLDER | underdog | 425 | 1.5891 / 1.5112 | 116.257 / 112.309 | 1.2299 / 1.1663 |
| 2026-06 | ERA_WEIGHT_BEST_OLDER | favourite | 425 | 1.9134 / 1.7090 | 121.346 / 113.529 | 1.5579 / 1.3592 |
| 2026-06 | ERA_WEIGHT_BEST_OLDER | underdog | 425 | 1.8880 / 1.5112 | 135.553 / 112.309 | 1.4925 / 1.1663 |
| 2026-06 | COMBINED_WEIGHT_BEST_OLDER | favourite | 425 | 1.9134 / 1.7090 | 121.346 / 113.529 | 1.5579 / 1.3592 |
| 2026-06 | COMBINED_WEIGHT_BEST_OLDER | underdog | 425 | 1.8880 / 1.5112 | 135.553 / 112.309 | 1.4925 / 1.1663 |
| 2026-06 | COMBINED_SELECTORS_BEST_OLDER | favourite | 425 | 1.6865 / 1.7089 | 109.819 / 111.617 | 1.3537 / 1.3585 |
| 2026-06 | COMBINED_SELECTORS_BEST_OLDER | underdog | 425 | 1.5447 / 1.5107 | 114.627 / 111.100 | 1.1905 / 1.1656 |
| 2026-07 | ERA_SELECTOR | favourite | 62 | 0.8874 / 0.8874 | 141.152 / 141.152 | 0.6647 / 0.6647 |
| 2026-07 | ERA_SELECTOR | underdog | 62 | 1.1575 / 1.1575 | 174.749 / 174.749 | 0.8213 / 0.8213 |
| 2026-07 | ERA_WEIGHT | favourite | 62 | 0.8874 / 0.8874 | 141.152 / 141.152 | 0.6647 / 0.6647 |
| 2026-07 | ERA_WEIGHT | underdog | 62 | 1.1575 / 1.1575 | 174.749 / 174.749 | 0.8213 / 0.8213 |
| 2026-07 | COMBINED_WEIGHT | favourite | 62 | 0.8874 / 0.8874 | 141.152 / 141.152 | 0.6647 / 0.6647 |
| 2026-07 | COMBINED_WEIGHT | underdog | 62 | 1.1575 / 1.1575 | 174.749 / 174.749 | 0.8213 / 0.8213 |
| 2026-07 | COMBINED_SELECTORS | favourite | 62 | 0.8874 / 0.8874 | 141.152 / 141.152 | 0.6647 / 0.6647 |
| 2026-07 | COMBINED_SELECTORS | underdog | 62 | 1.1575 / 1.1575 | 174.749 / 174.749 | 0.8213 / 0.8213 |
| 2026-07 | ERA_SELECTOR_BEST_OLDER | favourite | 62 | 0.9115 / 0.8874 | 136.765 / 141.152 | 0.6694 / 0.6647 |
| 2026-07 | ERA_SELECTOR_BEST_OLDER | underdog | 62 | 1.1497 / 1.1575 | 171.156 / 174.749 | 0.8313 / 0.8213 |
| 2026-07 | ERA_WEIGHT_BEST_OLDER | favourite | 62 | 1.0971 / 0.8874 | 165.423 / 141.152 | 0.9312 / 0.6647 |
| 2026-07 | ERA_WEIGHT_BEST_OLDER | underdog | 62 | 1.1880 / 1.1575 | 167.318 / 174.749 | 1.0097 / 0.8213 |
| 2026-07 | COMBINED_WEIGHT_BEST_OLDER | favourite | 62 | 1.0971 / 0.8874 | 165.423 / 141.152 | 0.9312 / 0.6647 |
| 2026-07 | COMBINED_WEIGHT_BEST_OLDER | underdog | 62 | 1.1880 / 1.1575 | 167.318 / 174.749 | 1.0097 / 0.8213 |
| 2026-07 | COMBINED_SELECTORS_BEST_OLDER | favourite | 62 | 0.8998 / 0.8874 | 135.150 / 141.152 | 0.6630 / 0.6647 |
| 2026-07 | COMBINED_SELECTORS_BEST_OLDER | underdog | 62 | 1.1323 / 1.1575 | 170.317 / 174.749 | 0.8193 / 0.8213 |
## ATP_CHALL

| Month | Validation games | Family | Exact control CRPS | Date control CRPS | Selected | Selected CRPS | Best older | Older CRPS | Older wins validation? |
|---|---:|---|---:|---:|---|---:|---|---:|---|
| 2026-04 | 0 | COMBINED_SELECTORS | no comparable history | no comparable history | FIRST_EXACT_TICK_MEMBERS | no comparable history | none | no comparable history | False |
| 2026-04 | 0 | COMBINED_WEIGHT | no comparable history | no comparable history | FIRST_EXACT_TICK_MEMBERS | no comparable history | none | no comparable history | False |
| 2026-04 | 0 | ERA_SELECTOR | no comparable history | no comparable history | FIRST_EXACT_TICK_MEMBERS | no comparable history | none | no comparable history | False |
| 2026-04 | 0 | ERA_WEIGHT | no comparable history | no comparable history | FIRST_EXACT_TICK_MEMBERS | no comparable history | none | no comparable history | False |
| 2026-05 | 387 | COMBINED_SELECTORS | 2.79797 | 2.80523 | COMBINED_SELECTORS:0.1,0.75,0.75 | 2.73635 | COMBINED_SELECTORS:0.1,0.75,0.75 | 2.73635 | True |
| 2026-05 | 387 | COMBINED_WEIGHT | 2.79797 | 2.80523 | FIRST_EXACT_TICK_MEMBERS | 2.79797 | COMBINED_WEIGHT:0.1,0.1,0.1 | 3.26329 | False |
| 2026-05 | 387 | ERA_SELECTOR | 2.79797 | 2.80523 | ERA_SELECTOR:0.1 | 2.76709 | ERA_SELECTOR:0.1 | 2.76709 | True |
| 2026-05 | 387 | ERA_WEIGHT | 2.79797 | 2.80523 | FIRST_EXACT_TICK_MEMBERS | 2.79797 | ERA_WEIGHT:0.1 | 3.35925 | False |
| 2026-06 | 914 | COMBINED_SELECTORS | 1.90428 | 1.93727 | FIRST_EXACT_TICK_MEMBERS | 1.90428 | COMBINED_SELECTORS:0.25,0.5,0.1 | 2.12434 | False |
| 2026-06 | 914 | COMBINED_WEIGHT | 1.90428 | 1.93727 | FIRST_EXACT_TICK_MEMBERS | 1.90428 | COMBINED_WEIGHT:0.1,0.1,0.1 | 2.57731 | False |
| 2026-06 | 914 | ERA_SELECTOR | 1.90428 | 1.93727 | FIRST_EXACT_TICK_MEMBERS | 1.90428 | ERA_SELECTOR:0.25 | 2.21056 | False |
| 2026-06 | 914 | ERA_WEIGHT | 1.90428 | 1.93727 | FIRST_EXACT_TICK_MEMBERS | 1.90428 | ERA_WEIGHT:0.1 | 2.72080 | False |
| 2026-07 | 1870 | COMBINED_SELECTORS | 1.46811 | 1.49509 | FIRST_EXACT_TICK_MEMBERS | 1.46811 | COMBINED_SELECTORS:0.25,0.9,0.25 | 1.56464 | False |
| 2026-07 | 1870 | COMBINED_WEIGHT | 1.46811 | 1.49509 | FIRST_EXACT_TICK_MEMBERS | 1.46811 | COMBINED_WEIGHT:0.1,0.25,0.1 | 2.04196 | False |
| 2026-07 | 1870 | ERA_SELECTOR | 1.46811 | 1.49509 | FIRST_EXACT_TICK_MEMBERS | 1.46811 | ERA_SELECTOR:0.25 | 1.59740 | False |
| 2026-07 | 1870 | ERA_WEIGHT | 1.46811 | 1.49509 | FIRST_EXACT_TICK_MEMBERS | 1.46811 | ERA_WEIGHT:0.1 | 2.20417 | False |

### Test: selected family and best older-admitting challenger

| Month | Key | Side | Matched games | Floor MAE new / exact | Timing MAE new / exact | CRPS new / exact |
|---|---|---|---:|---:|---:|---:|
| 2026-04 | ERA_SELECTOR | favourite | 358 | 3.1181 / 3.1181 | 44.739 / 44.739 | 2.6315 / 2.6315 |
| 2026-04 | ERA_SELECTOR | underdog | 360 | 2.7713 / 2.7713 | 40.739 / 40.739 | 2.2104 / 2.2104 |
| 2026-04 | ERA_WEIGHT | favourite | 358 | 3.1181 / 3.1181 | 44.739 / 44.739 | 2.6315 / 2.6315 |
| 2026-04 | ERA_WEIGHT | underdog | 360 | 2.7713 / 2.7713 | 40.739 / 40.739 | 2.2104 / 2.2104 |
| 2026-04 | COMBINED_WEIGHT | favourite | 358 | 3.1181 / 3.1181 | 44.739 / 44.739 | 2.6315 / 2.6315 |
| 2026-04 | COMBINED_WEIGHT | underdog | 360 | 2.7713 / 2.7713 | 40.739 / 40.739 | 2.2104 / 2.2104 |
| 2026-04 | COMBINED_SELECTORS | favourite | 358 | 3.1181 / 3.1181 | 44.739 / 44.739 | 2.6315 / 2.6315 |
| 2026-04 | COMBINED_SELECTORS | underdog | 360 | 2.7713 / 2.7713 | 40.739 / 40.739 | 2.2104 / 2.2104 |
| 2026-04 | ERA_SELECTOR_BEST_OLDER | favourite | 358 | 3.1181 / 3.1181 | 44.739 / 44.739 | 2.6315 / 2.6315 |
| 2026-04 | ERA_SELECTOR_BEST_OLDER | underdog | 360 | 2.7713 / 2.7713 | 40.739 / 40.739 | 2.2104 / 2.2104 |
| 2026-04 | ERA_WEIGHT_BEST_OLDER | favourite | 358 | 3.1181 / 3.1181 | 44.739 / 44.739 | 2.6315 / 2.6315 |
| 2026-04 | ERA_WEIGHT_BEST_OLDER | underdog | 360 | 2.7713 / 2.7713 | 40.739 / 40.739 | 2.2104 / 2.2104 |
| 2026-04 | COMBINED_WEIGHT_BEST_OLDER | favourite | 358 | 3.1181 / 3.1181 | 44.739 / 44.739 | 2.6315 / 2.6315 |
| 2026-04 | COMBINED_WEIGHT_BEST_OLDER | underdog | 360 | 2.7713 / 2.7713 | 40.739 / 40.739 | 2.2104 / 2.2104 |
| 2026-04 | COMBINED_SELECTORS_BEST_OLDER | favourite | 358 | 3.1181 / 3.1181 | 44.739 / 44.739 | 2.6315 / 2.6315 |
| 2026-04 | COMBINED_SELECTORS_BEST_OLDER | underdog | 360 | 2.7713 / 2.7713 | 40.739 / 40.739 | 2.2104 / 2.2104 |
| 2026-05 | ERA_SELECTOR | favourite | 529 | 1.2864 / 1.3224 | 36.857 / 37.357 | 1.0367 / 1.1782 |
| 2026-05 | ERA_SELECTOR | underdog | 528 | 0.9685 / 1.0618 | 33.844 / 38.895 | 0.7583 / 0.9075 |
| 2026-05 | ERA_WEIGHT | favourite | 529 | 1.3273 / 1.3273 | 38.408 / 38.408 | 1.1830 / 1.1830 |
| 2026-05 | ERA_WEIGHT | underdog | 528 | 1.0757 / 1.0757 | 39.551 / 39.551 | 0.9164 / 0.9164 |
| 2026-05 | COMBINED_WEIGHT | favourite | 529 | 1.3273 / 1.3273 | 38.408 / 38.408 | 1.1830 / 1.1830 |
| 2026-05 | COMBINED_WEIGHT | underdog | 528 | 1.0757 / 1.0757 | 39.551 / 39.551 | 0.9164 / 0.9164 |
| 2026-05 | COMBINED_SELECTORS | favourite | 529 | 1.2685 / 1.3218 | 35.870 / 37.228 | 1.0174 / 1.1774 |
| 2026-05 | COMBINED_SELECTORS | underdog | 528 | 0.9513 / 1.0606 | 33.818 / 38.700 | 0.7507 / 0.9068 |
| 2026-05 | ERA_SELECTOR_BEST_OLDER | favourite | 529 | 1.2864 / 1.3224 | 36.857 / 37.357 | 1.0367 / 1.1782 |
| 2026-05 | ERA_SELECTOR_BEST_OLDER | underdog | 528 | 0.9685 / 1.0618 | 33.844 / 38.895 | 0.7583 / 0.9075 |
| 2026-05 | ERA_WEIGHT_BEST_OLDER | favourite | 529 | 2.6006 / 1.3273 | 56.334 / 38.408 | 2.2252 / 1.1830 |
| 2026-05 | ERA_WEIGHT_BEST_OLDER | underdog | 528 | 2.4932 / 1.0757 | 61.117 / 39.551 | 1.9899 / 0.9164 |
| 2026-05 | COMBINED_WEIGHT_BEST_OLDER | favourite | 529 | 2.2535 / 1.3273 | 55.626 / 38.408 | 1.9693 / 1.1830 |
| 2026-05 | COMBINED_WEIGHT_BEST_OLDER | underdog | 528 | 2.2046 / 1.0757 | 60.689 / 39.551 | 1.8106 / 0.9164 |
| 2026-05 | COMBINED_SELECTORS_BEST_OLDER | favourite | 529 | 1.2685 / 1.3218 | 35.870 / 37.228 | 1.0174 / 1.1774 |
| 2026-05 | COMBINED_SELECTORS_BEST_OLDER | underdog | 528 | 0.9513 / 1.0606 | 33.818 / 38.700 | 0.7507 / 0.9068 |
| 2026-06 | ERA_SELECTOR | favourite | 949 | 1.2480 / 1.2480 | 38.732 / 38.732 | 1.0623 / 1.0623 |
| 2026-06 | ERA_SELECTOR | underdog | 949 | 1.0179 / 1.0179 | 39.512 / 39.512 | 0.8283 / 0.8283 |
| 2026-06 | ERA_WEIGHT | favourite | 949 | 1.2480 / 1.2480 | 38.732 / 38.732 | 1.0623 / 1.0623 |
| 2026-06 | ERA_WEIGHT | underdog | 949 | 1.0179 / 1.0179 | 39.512 / 39.512 | 0.8283 / 0.8283 |
| 2026-06 | COMBINED_WEIGHT | favourite | 949 | 1.2480 / 1.2480 | 38.732 / 38.732 | 1.0623 / 1.0623 |
| 2026-06 | COMBINED_WEIGHT | underdog | 949 | 1.0179 / 1.0179 | 39.512 / 39.512 | 0.8283 / 0.8283 |
| 2026-06 | COMBINED_SELECTORS | favourite | 949 | 1.2480 / 1.2480 | 38.732 / 38.732 | 1.0623 / 1.0623 |
| 2026-06 | COMBINED_SELECTORS | underdog | 949 | 1.0179 / 1.0179 | 39.512 / 39.512 | 0.8283 / 0.8283 |
| 2026-06 | ERA_SELECTOR_BEST_OLDER | favourite | 949 | 1.2402 / 1.2480 | 38.125 / 38.732 | 1.0258 / 1.0623 |
| 2026-06 | ERA_SELECTOR_BEST_OLDER | underdog | 949 | 1.0064 / 1.0179 | 38.921 / 39.512 | 0.7890 / 0.8283 |
| 2026-06 | ERA_WEIGHT_BEST_OLDER | favourite | 949 | 1.8859 / 1.2480 | 52.547 / 38.732 | 1.7534 / 1.0623 |
| 2026-06 | ERA_WEIGHT_BEST_OLDER | underdog | 949 | 1.7108 / 1.0179 | 54.997 / 39.512 | 1.5191 / 0.8283 |
| 2026-06 | COMBINED_WEIGHT_BEST_OLDER | favourite | 949 | 1.6204 / 1.2480 | 50.340 / 38.732 | 1.5182 / 1.0623 |
| 2026-06 | COMBINED_WEIGHT_BEST_OLDER | underdog | 949 | 1.4757 / 1.0179 | 53.232 / 39.512 | 1.3376 / 0.8283 |
| 2026-06 | COMBINED_SELECTORS_BEST_OLDER | favourite | 949 | 1.2121 / 1.2473 | 37.210 / 38.654 | 0.9945 / 1.0620 |
| 2026-06 | COMBINED_SELECTORS_BEST_OLDER | underdog | 949 | 0.9826 / 1.0162 | 38.532 / 39.338 | 0.7700 / 0.8271 |
| 2026-07 | ERA_SELECTOR | favourite | 360 | 0.9370 / 0.9370 | 38.558 / 38.558 | 0.7760 / 0.7760 |
| 2026-07 | ERA_SELECTOR | underdog | 360 | 0.7338 / 0.7338 | 38.499 / 38.499 | 0.5723 / 0.5723 |
| 2026-07 | ERA_WEIGHT | favourite | 360 | 0.9370 / 0.9370 | 38.558 / 38.558 | 0.7760 / 0.7760 |
| 2026-07 | ERA_WEIGHT | underdog | 360 | 0.7338 / 0.7338 | 38.499 / 38.499 | 0.5723 / 0.5723 |
| 2026-07 | COMBINED_WEIGHT | favourite | 360 | 0.9370 / 0.9370 | 38.558 / 38.558 | 0.7760 / 0.7760 |
| 2026-07 | COMBINED_WEIGHT | underdog | 360 | 0.7338 / 0.7338 | 38.499 / 38.499 | 0.5723 / 0.5723 |
| 2026-07 | COMBINED_SELECTORS | favourite | 360 | 0.9370 / 0.9370 | 38.558 / 38.558 | 0.7760 / 0.7760 |
| 2026-07 | COMBINED_SELECTORS | underdog | 360 | 0.7338 / 0.7338 | 38.499 / 38.499 | 0.5723 / 0.5723 |
| 2026-07 | ERA_SELECTOR_BEST_OLDER | favourite | 360 | 0.9341 / 0.9298 | 38.258 / 38.331 | 0.7328 / 0.7691 |
| 2026-07 | ERA_SELECTOR_BEST_OLDER | underdog | 360 | 0.7200 / 0.7338 | 37.598 / 38.499 | 0.5388 / 0.5723 |
| 2026-07 | ERA_WEIGHT_BEST_OLDER | favourite | 360 | 1.2090 / 0.9370 | 45.173 / 38.558 | 1.2211 / 0.7760 |
| 2026-07 | ERA_WEIGHT_BEST_OLDER | underdog | 360 | 1.0119 / 0.7338 | 47.259 / 38.499 | 1.0237 / 0.5723 |
| 2026-07 | COMBINED_WEIGHT_BEST_OLDER | favourite | 360 | 1.0772 / 0.9370 | 42.957 / 38.558 | 1.0438 / 0.7760 |
| 2026-07 | COMBINED_WEIGHT_BEST_OLDER | underdog | 360 | 0.8722 / 0.7338 | 44.797 / 38.499 | 0.8696 / 0.5723 |
| 2026-07 | COMBINED_SELECTORS_BEST_OLDER | favourite | 360 | 0.9213 / 0.9298 | 37.911 / 38.331 | 0.7263 / 0.7691 |
| 2026-07 | COMBINED_SELECTORS_BEST_OLDER | underdog | 360 | 0.7072 / 0.7338 | 37.391 / 38.499 | 0.5307 / 0.5723 |
