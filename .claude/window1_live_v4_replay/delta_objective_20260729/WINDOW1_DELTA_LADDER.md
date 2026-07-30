# Window-1 close-relative delta ladder

**This is not the cost-under-par ladder.** Delta is `reachable price − authoritative Window-1 close`, per leg. Combined delta is the sum of the two leg deltas. The frozen PC scorer uses this close-relative quantity and a zero-cent frozen fee.

Fill model: resting order, later true-price touch fills; no depth proof and no five-contract capacity gate.

## Headline

- **340 of 804** had both legs reachable strictly below their own authoritative Window-1 close.
- **580 of 804** had negative combined reachable delta.
- The comparison is defined for **622 of 804**. The other **182** are not assigned a synthetic close or opportunity.

## Ladder

| combined reachable delta | independent touch | strict sequential touch |
|---|---:|---:|
| ≤ −1¢ | 580 | 580 |
| ≤ −2¢ | 477 | 477 |
| ≤ −3¢ | 362 | 362 |
| ≤ −5¢ | 177 | 177 |
| ≤ −10¢ | 34 | 34 |
| ≤ −15¢ | 6 | 6 |
| ≤ −20¢ | 4 | 4 |
| exactly 0¢ | 42 | 42 |

The two columns are equal here. Both leg orderings were tested by the strict oracle; sequencing did not change the attainable close-relative minima in this population.

## By category

| category | defined | both legs < close | combined delta < 0 |
|---|---:|---:|---:|
| ATP_CHALL | 291 | 158 | 270 |
| ATP_MAIN | 117 | 83 | 115 |
| WTA_CHALL | 87 | 27 | 73 |
| WTA_MAIN | 127 | 72 | 122 |

## Denominator

There are 693 games with a measurable nonzero guarded Window 1. Of those, 680 have a two-leg touch floor. A further 58 do not have an authoritative two-leg close under the scorer's latest-timestamp tie law, leaving 622 defined delta comparisons. The other 111 games have no lawful nonzero evaluator window.
