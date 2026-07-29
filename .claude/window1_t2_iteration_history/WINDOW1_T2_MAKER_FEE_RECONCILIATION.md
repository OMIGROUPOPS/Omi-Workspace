# Window-1 T2 hold-control maker-fee reconciliation

Source: `01_w1_t2__macro_hold__fixed_admission_parent_control_EVENT_LEDGER.jsonl`. Development sample only; D=804.
Holdout sealed. No live, exchange, or trading-system access.

## Fee-adjusted control frontier

| basis | <=93 | <=95 | <=97 | <100 | any price |
|---|---:|---:|---:|---:|---:|
| policy, pre-fee | 0 | 1 | 7 | 100 | 131 |
| policy, maker fee curve | 0 | 1 | 1 | 76 | 131 |
| full-tape five-contract opportunity, pre-fee | 20 | 51 | 156 | 437 | 692 |
| full-tape five-contract opportunity, maker fee curve | 9 | 21 | 76 | 364 | 692 |

Of the 100 pre-fee sub-par policy completions, 76 survive the maker fee curve; 24 do not.

PC/IC/S, pre-fee: **115/37/100**. PC/IC/S, maker fee curve: **103/37/76**.

Policy any-price completions: **131**. Full-tape proven any-price opportunities: **692**. Evidence censored/unproved: **112**.

## Control regret map

The tape proves 692 opportunities; the policy completed 131 and missed 561 (18.93% capture).

| tape floor | tape-proven | achieved at same tier | completed above tier | never completed |
|---|---:|---:|---:|---:|
| LE_93 | 20 | 0 | 3 | 17 |
| LE_95 | 51 | 1 | 13 | 37 |
| LE_97 | 156 | 7 | 54 | 95 |
| LT_100 | 437 | 100 | 29 | 308 |
| ANY_PRICE | 692 | 131 | 0 | 561 |

Misses by policy outcome: naked_single=238, no_fill=323.

Execution-price regret on completed pairs: 217 cents per-contract summed across 131 observed completed pairs.

Execution-price regret on observed legs: 475 cents per-contract summed across 500 legs.

The full machine-readable map, including fit/post-fit splits and per-completion fees, is in the adjacent JSON receipt.
