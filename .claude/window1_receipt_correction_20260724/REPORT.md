# Corrected historical replay receipts

This receipt preserves the original replay and corrects only its semantic
bound and post-start classifications.  It does not rerun an alternative
policy, tune a candidate, establish a market ceiling, or judge the full OS
family.

## Corrected bound

- D = 804
- published optimistic upper bound = 240
- corrected receipts-only optimistic upper bound = 226
- corrected rate over D = 28.109453%
- distance from 603 = 377 events
- strict lower bound = 0

The corrected set retains 215 events
from the published set, removes 25, and adds
11.  The 14 censoring-only audit candidates contribute 11
events; three still have an independent hard sibling receipt.  Eighteen
published candidates are removed for a receipt-proven post-start leg.  The
strictest usable live-by correction removes seven more events.

## Proof-law repairs

- cutoff-only non-Window-1 disjuncts removed = 4 legs
- strict live-by events repaired = 7
- newly proven post-start legs from that repair = 11
- exact ten-contract overfill retained outside exact-five = 1

The historical lifecycle census remains 258 exact-five fills, 12
other-quantity fills, 870 exact nonfills, and 468 censored legs.

## Scope

This bound rejects only the historical placements, cancellations, and
non-placements actually represented by the frozen receipt replay.  No
alternative policy was tested.
