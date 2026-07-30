# Counterfactual replay - KXATPCHALLENGERMATCH-26JUL12ALVVAN

Same frozen tape, same clock, same live_v4 source, one changed dial.

## Dial

- Dial: `contention_drop_enforced`
- Setting: `False` -> `True`
- Rule: selector DROP is a placement veto

## First separation

- Event: `replace`
- Replay timestamp: `None`

## Outcome

| Run | Pair complete | Filled + resting pair cost | Headroom |
|---|---:|---:|---:|
| Baseline | False | 86c | 11c |
| Counterfactual | False | 22c | 75c |

### Leg outcomes

| Leg | Baseline | Counterfactual |
|---|---|---|
| ALV | filled=False, fill=None, resting=70 | filled=False, fill=None, resting=None |
| VAN | filled=False, fill=None, resting=16 | filled=True, fill=22, resting=None |

## Downstream layer diff

| Layer | Changed trace blocks | Events affected |
|---|---:|---|
| authority_and_aim | 1 | contention_drop_refused, conviction_shadow, liveaim_shadow, os_shadow, trendpath_live_aim, trendpath_shadow, v4_place |
| engine_and_tape | 429 | authority_mismatch_defect, authority_reanchor, authority_sweep_census, band_call, completion_booking_adoption, completion_shadow, contention_drop_refused, conviction_shadow, entry_dossier, entry_filled, fresh_place_pair_bound, liveaim_shadow, naked_leg_defect, order_cancelled, order_placed, os_shadow, pair_class_read, paper_fill, paper_order_cancelled, paper_order_posted, reconcile, reconcile_v4_adopted, sibling_repost_scan, skipped, staircase_hold_place, trendpath_live_aim, trendpath_shadow, unbooked_fill_defect, v4_exit_posted, v4_place |
| exit_and_settlement | 1 | completion_booking_adoption, contention_drop_refused, entry_dossier, entry_filled, naked_leg_defect, order_placed, paper_order_posted, reconcile_v4_adopted, staircase_hold_place, unbooked_fill_defect, v4_exit_posted |
| fills_and_booking | 2 | completion_booking_adoption, contention_drop_refused, conviction_shadow, entry_dossier, entry_filled, naked_leg_defect, order_placed, os_shadow, paper_fill, paper_order_posted, reconcile_v4_adopted, staircase_hold_place, unbooked_fill_defect, v4_exit_posted |
| headroom_and_sibling | 23 | completion_shadow, contention_drop_refused, conviction_shadow, entry_dossier, os_shadow, sibling_repost_scan, skipped, staircase_hold_place |
| post_hold_walk_park | 151 | authority_mismatch_defect, authority_reanchor, authority_sweep_census, band_call, completion_booking_adoption, completion_shadow, contention_drop_refused, conviction_shadow, entry_dossier, entry_filled, fresh_place_pair_bound, liveaim_shadow, naked_leg_defect, order_cancelled, order_placed, os_shadow, pair_class_read, paper_fill, paper_order_cancelled, paper_order_posted, reconcile_v4_adopted, sibling_repost_scan, skipped, staircase_hold_place, trendpath_live_aim, trendpath_shadow, unbooked_fill_defect, v4_exit_posted, v4_place |
| recognition_and_dossier | 210 | authority_mismatch_defect, authority_reanchor, authority_sweep_census, band_call, completion_booking_adoption, completion_shadow, contention_drop_refused, conviction_shadow, entry_dossier, entry_filled, fresh_place_pair_bound, liveaim_shadow, naked_leg_defect, order_cancelled, order_placed, os_shadow, pair_class_read, paper_fill, paper_order_cancelled, paper_order_posted, reconcile_v4_adopted, sibling_repost_scan, skipped, staircase_hold_place, trendpath_live_aim, trendpath_shadow, unbooked_fill_defect, v4_exit_posted, v4_place |

The complete aligned downstream diff is in `COUNTERFACTUAL_DIFF.json`; the baseline and counterfactual trace files remain separate and complete.
