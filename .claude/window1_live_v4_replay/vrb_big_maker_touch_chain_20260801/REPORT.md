# VRB/BIG maker-touch chain

## VRB early chain

VRB was 67/68 in 9 early episodes totaling 641 state-seconds. Every one of the 60 raw ask-68 ticks in those nine episodes had bid 67. The bid-67 episode containing the replay credit lasted 1128 seconds across 235 raw ticks.

| visit | start scheduled/bell | last observed scheduled/bell | bid/ask | state seconds | receipts |
|---:|---|---|---|---:|---:|
| 1 | T-317:49 / T-322:49 | T-317:37 / T-322:37 | 67/68 | 12 | 6 |
| 2 | T-314:38 / T-319:38 | T-313:39 / T-318:39 | 67/68 | 59 | 4 |
| 3 | T-308:48 / T-313:48 | T-308:40 / T-313:40 | 67/68 | 8 | 6 |
| 4 | T-307:48 / T-312:48 | T-307:40 / T-312:40 | 67/68 | 8 | 4 |
| 5 | T-306:45 / T-311:45 | T-306:40 / T-311:40 | 67/68 | 5 | 4 |
| 6 | T-305:47 / T-310:47 | T-305:40 / T-310:40 | 67/68 | 7 | 5 |
| 7 | T-301:50 / T-306:50 | T-301:40 / T-306:40 | 67/68 | 10 | 4 |
| 8 | T-300:49 / T-305:49 | T-300:40 / T-305:40 | 67/68 | 9 | 9 |
| 9 | T-299:43 / T-304:43 | T-291:00 / T-296:00 | 67/68 | 523 | 18 |

The first lawful bid 67 appeared 2646 seconds before the first ask 68. Before 68, the complete pair-state chain is:

- T-375:27 scheduled / T-380:27 bell: 5/92; 812s to next state; 2 receipts.
- T-361:55 scheduled / T-366:55 bell: 67/77; 19s to next state; 3 receipts.
- T-361:36 scheduled / T-366:36 bell: 67/76; 2607s to next state; 136 receipts.
- T-318:09 scheduled / T-323:09 bell: 67/75; 16s to next state; 5 receipts.
- T-317:53 scheduled / T-322:53 bell: 67/74; 1s to next state; 5 receipts.
- T-317:52 scheduled / T-322:52 bell: 67/76; 0s to next state; 2 receipts.
- T-317:52 scheduled / T-322:52 bell: 67/75; 0s to next state; 4 receipts.
- T-317:52 scheduled / T-322:52 bell: 67/73; 1s to next state; 5 receipts.
- T-317:51 scheduled / T-322:51 bell: 67/72; 0s to next state; 2 receipts.
- T-317:51 scheduled / T-322:51 bell: 67/71; 1s to next state; 2 receipts.
- T-317:50 scheduled / T-322:50 bell: 67/70; 0s to next state; 4 receipts.
- T-317:50 scheduled / T-322:50 bell: 67/69; 1s to next state; 4 receipts.
- T-317:49 scheduled / T-322:49 bell: 67/68; 12s to next state; 6 receipts.

True-print check: 1 print(s) occurred from the first book through the 1,128-second bid episode; 0 were SELL-aggressor prints at or below 67. A resting 67 bid was at touch during every 67/68 visit, but an early maker fill is not proven.

## BIG ask-55 chain

BIG's ask was 55 for 14807 observed seconds across 464 raw ticks. The bid underneath it followed:

| start scheduled/bell | bid/ask | observed span | state to next bid | receipts |
|---|---|---:|---:|---:|
| T-478:30 / T-568:30 | 54/55 | 3524s | 3625s | 101 |
| T-418:05 / T-508:05 | 53/55 | 8785s | 8785s | 180 |
| T-271:40 / T-361:40 | 54/55 | 2397s | 2397s | 178 |
| T-231:43 / T-321:43 | 55/55 | 0s | 8s | 5 |

The bid reached 55 only on 5 same-second raw ticks at the end of the 55-ask episode and the locked state lasted 8 seconds until the next book changed to 56/57. The guarded true-print tape contains 7 prints while ask 55 was displayed: 5 at 55, 1 at 56, and 1 at 57; all were BUY aggressors. There were 0 SELL-aggressor prints at or below the maker-clamped 54. A resting 54 fill is not proven.

The compressed JSONL ledgers contain every requested raw tick with both clocks and the same-tick bid, ask, carried last trade, spread, size, and top-five depth.
