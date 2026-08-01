# BIG every-tick elimination diagnosis

Diagnostic only. The frozen gate, library, replay, placements, and fills are unchanged.

Complete 3,645 joint-tick walk: https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/refs/heads/codex/window1-live-consolidated/.claude/window1_live_v4_replay/quote_shape_elimination_big_walk_20260731/BIG_EVERY_JOINT_TICK_ELIMINATION_WALK.csv

Machine-readable diagnosis: https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/refs/heads/codex/window1-live-consolidated/.claude/window1_live_v4_replay/quote_shape_elimination_big_walk_20260731/BIG_ELIMINATION_DIAGNOSIS.json

## Material chronology

The table is a compact index. The linked CSV contains every tick, including both clocks, the joint BIG bid/ask/last/spread/dwell observation, the surviving set, pair-tuple count, state, named missing proof, trigger leg, and both receipts.

| Tick | T-minus scheduled | T-minus bell | BIG bid / ask / last / spread / ask dwell | Surviving BIG shapes | State | Exact missing proof or action | HUR bid / ask / last / direction observed |
|---:|---:|---:|---|---|---|---|---|
| 1 | T-28710s | T-34110s | 54 / 55 / 56 / 1 / 0s | ATP_CHALL_51_75_UP_CONTINUATION:UNKNOWN<br>ATP_CHALL_51_75_DOWN_REBOUND:UNKNOWN<br>ATP_CHALL_51_75_DOWN_CONTINUATION:UNKNOWN<br>ATP_CHALL_51_75_FLAT_RECOVERED:UNKNOWN<br>ATP_CHALL_51_75_FLAT_UNMOVED:UNKNOWN<br>ATP_CHALL_51_75_UP_AFTER_DIP:UNKNOWN | INSUFFICIENT_EVIDENCE | NO_PRIOR_IN_WINDOW_BOOK | not available / not available / not available / not yet independently observed |
| 4 | T-28705s | T-34105s | 54 / 55 / 56 / 1 / 5s | ATP_CHALL_51_75_UP_CONTINUATION:UNKNOWN | INSUFFICIENT_EVIDENCE | SURVIVING_SHAPES_DISAGREE_OR_LIBRARY_GAP | 47 / 48 / 47 / not yet independently observed |
| 14 | T-28380s | T-33780s | 54 / 55 / 56 / 1 / 330s | ATP_CHALL_51_75_UP_CONTINUATION:FLOOR | INSUFFICIENT_EVIDENCE | FLOOR_CONSENSUS_BUT_OWN_MICRO_POSITION_UNOBSERVED | 47 / 48 / 47 / not yet independently observed |
| 156 | T-23222s | T-28622s | 53 / 55 / 56 / 2 / 5488s | ATP_CHALL_51_75_UP_CONTINUATION:LOWER | HOLD | ALL_SURVIVING_SHAPES_SAY_LOWER | 47 / 48 / 47 / not yet independently observed |
| 245 | T-18206s | T-23606s | 53 / 55 / 55 / 2 / 10504s | ATP_CHALL_51_75_UP_CONTINUATION:FLOOR | INSUFFICIENT_EVIDENCE | FLOOR_CONSENSUS_BUT_OWN_MICRO_POSITION_UNOBSERVED | 47 / 48 / 47 / not yet independently observed |
| 359 | T-15251s | T-20651s | 54 / 55 / 55 / 1 / 13459s | ATP_CHALL_51_75_UP_CONTINUATION:FLOOR | INSUFFICIENT_EVIDENCE | FLOOR_CONSENSUS_BUT_OWN_MICRO_POSITION_UNOBSERVED | 45 / 46 / 47 / DOWN |
| 418 | T-13895s | T-19295s | 56 / 57 / 55 / 1 / 0s | ATP_CHALL_51_75_UP_CONTINUATION:FLOOR | INSUFFICIENT_EVIDENCE | FLOOR_CONSENSUS_BUT_CURRENT_ASK_IS_ABOVE_OBSERVED_LOW | 41 / 44 / 43 / DOWN |
| 3474 | T+4669s | T-731s | 59 / 60 / 60 / 1 / 2396s | ATP_CHALL_51_75_UP_CONTINUATION:LOWER | HOLD | ALL_SURVIVING_SHAPES_SAY_LOWER | 40 / 41 / 40 / DOWN |
| 3546 | T+5000s | T-400s | 58 / 59 / 59 / 1 / 125s | ATP_CHALL_51_75_UP_CONTINUATION:FLOOR | INSUFFICIENT_EVIDENCE | FLOOR_CONSENSUS_BUT_CURRENT_ASK_IS_ABOVE_OBSERVED_LOW | 40 / 41 / 41 / DOWN |

## Answers

1. **The floor did not arrive too early and disappear before resolution.** BIG's ask 55 was the first formed ask, remained continuously displayed through its last 55 receipt, and accumulated repeated lawful joint ticks. The eliminator reduced BIG to one `UP_CONTINUATION` shape and called `FLOOR` while 55 was still displayed. This was not an evidence-window miss.

2. **This trace exposes the single-visit-floor structural weakness.** `PLACE` was withheld because `ask_change_after_first_timestamp=false`. When BIG finally supplied a later own-ask transition, the ask had risen above the observed low, so `ask_net != ask_dip` withheld placement. The gate therefore accepts recurrent returns such as VRB but cannot act on a continuously displayed first floor, even after the shape has resolved.

## Pair constraint

The eliminator does consume the sibling. HUR's independently observed `DOWN` direction reduces the pair to the inverse `BIG UP_CONTINUATION | HUR DOWN_CONTINUATION` tuple. It still cannot authorize BIG because the micro-micro gate separately requires a later-timestamp transition on BIG's own ask. Sibling evidence constrains the shape set; it does not satisfy that own-leg reachability clause.

## Evidence a single visit actually supplied

Without changing the gate, this trace lawfully exposes these contemporaneous inputs: continuous ask-55 dwell; positive displayed ask size and top-five ask depth; repeated raw BBO receipts with authoritative chronology; the joint bid/ask/last/spread observation as bid, last, size, depth, and spread evolve while ask stays 55; and HUR's independently resolved inverse direction. Ask reach remains ask-side only. None of these facts permits same-receipt fill credit, and no new threshold is proposed here.

## Validation boundary

This is one cold-game diagnostic against the already frozen two-game replay. It does not validate a replacement gate on the 804 and makes no population claim.
