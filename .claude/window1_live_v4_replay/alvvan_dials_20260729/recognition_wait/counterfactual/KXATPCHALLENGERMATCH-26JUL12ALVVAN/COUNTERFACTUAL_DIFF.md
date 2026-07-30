# Counterfactual replay - KXATPCHALLENGERMATCH-26JUL12ALVVAN

Same frozen tape, same clock, same live_v4 source, one changed dial.

## Dial

- Dial: `recognition_before_place`
- Setting: `False` -> `True`
- Rule: PATH placement waits until drift/band recognition is available

## First separation

- Event: `replace`
- Replay timestamp: `None`

## Outcome

| Run | Pair complete | Filled + resting pair cost | Headroom |
|---|---:|---:|---:|
| Baseline | False | 86c | 11c |
| Counterfactual | False | 86c | 11c |

### Leg outcomes

| Leg | Baseline | Counterfactual |
|---|---|---|
| ALV | filled=False, fill=None, resting=70 | filled=False, fill=None, resting=70 |
| VAN | filled=False, fill=None, resting=16 | filled=False, fill=None, resting=16 |

## Downstream layer diff

| Layer | Changed trace blocks | Events affected |
|---|---:|---|
| authority_and_aim | 3 | authority_clamp, conception_stamp, conviction_shadow, dual_divot_steer, entry_dossier, liveaim_shadow, order_placed, os_shadow, paper_order_posted, recognition_wait_before_place, sizing_shadow, staircase_hold_place, trendpath_live_aim, trendpath_shadow, v4_place |
| engine_and_tape | 24 | authority_clamp, authority_mismatch_defect, authority_reanchor, authority_sweep_census, conception_stamp, conviction_shadow, dual_divot_steer, entry_dossier, liveaim_shadow, order_cancelled, order_placed, os_shadow, paper_order_cancelled, paper_order_posted, recognition_wait_before_place, reconcile, sizing_shadow, staircase_hold_place, trendpath_live_aim, trendpath_shadow, v4_place |
| post_hold_walk_park | 244 | authority_clamp, authority_mismatch_defect, authority_reanchor, authority_sweep_census, conception_stamp, conviction_shadow, dual_divot_steer, entry_dossier, liveaim_shadow, order_cancelled, order_placed, os_shadow, paper_order_cancelled, paper_order_posted, recognition_wait_before_place, sizing_shadow, staircase_hold_place, trendpath_live_aim, trendpath_shadow, v4_place |
| recognition_and_dossier | 83 | authority_clamp, authority_mismatch_defect, conception_stamp, conviction_shadow, dual_divot_steer, entry_dossier, liveaim_shadow, order_placed, os_shadow, paper_order_posted, recognition_wait_before_place, sizing_shadow, staircase_hold_place, trendpath_live_aim, trendpath_shadow, v4_place |

The complete aligned downstream diff is in `COUNTERFACTUAL_DIFF.json`; the baseline and counterfactual trace files remain separate and complete.
