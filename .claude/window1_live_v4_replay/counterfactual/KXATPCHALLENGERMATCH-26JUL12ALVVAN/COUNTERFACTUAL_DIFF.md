# Counterfactual replay — KXATPCHALLENGERMATCH-26JUL12ALVVAN

Same frozen tape, same clock, same live_v4 source, one changed dial.

## Dial

- Leg: `ALV`
- Atlas page: `ATP_CHALL|leader|ge75`
- Path depth p50: 5.0¢ → 3.0¢
- Requested aim movement: +2¢
- Executed path aim: 74¢ → 75¢

## First separation

- Event: `trendpath_live_aim`
- Replay timestamp: `1783832721.0`
- The requested aim was passed through every unchanged live_v4 clamp and authority before the order was posted.

## Outcome

| Run | Pair complete | Filled + resting pair cost | Headroom |
|---|---:|---:|---:|
| Baseline | False | 96¢ | 1¢ |
| Counterfactual | False | 94¢ | 3¢ |

### Leg outcomes

| Leg | Baseline | Counterfactual |
|---|---|---|
| ALV | filled=False, fill=None, resting=74 | filled=False, fill=None, resting=72 |
| VAN | filled=True, fill=22, resting=None | filled=True, fill=22, resting=None |

## Downstream layer diff

| Layer | Changed trace blocks | Events affected |
|---|---:|---|
| authority_and_aim | 4 | conviction_shadow, entry_dossier, liveaim_shadow, order_placed, os_shadow, paper_order_posted, repost_no_evidence_hold, trendpath_live_aim, trendpath_shadow, v4_place |
| engine_and_tape | 12 | order_cancelled, paper_order_cancelled, reconcile, skipped, v4_resting_cancel |
| post_hold_walk_park | 56 | conviction_shadow, entry_dossier, liveaim_shadow, order_cancelled, order_placed, os_shadow, paper_order_cancelled, paper_order_posted, repost_no_evidence_hold, sibling_repost_scan, skipped, trendpath_live_aim, trendpath_shadow, v4_place, v4_resting_cancel |
| recognition_and_dossier | 4 | conviction_shadow, entry_dossier, liveaim_shadow, order_placed, os_shadow, paper_order_posted, repost_no_evidence_hold, sibling_repost_scan, skipped, trendpath_live_aim, trendpath_shadow, v4_place |

The complete aligned downstream diff is in `COUNTERFACTUAL_DIFF.json`; the baseline and counterfactual trace files remain separate and complete.
