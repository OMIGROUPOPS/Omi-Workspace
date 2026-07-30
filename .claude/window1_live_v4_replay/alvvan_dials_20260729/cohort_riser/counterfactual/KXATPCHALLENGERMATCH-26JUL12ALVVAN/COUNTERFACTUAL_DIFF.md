# Counterfactual replay - KXATPCHALLENGERMATCH-26JUL12ALVVAN

Same frozen tape, same clock, same live_v4 source, one changed dial.

## Dial

- Dial: `cohort_steer_riser`
- Setting: `False` -> `True`
- Rule: cohort steering may influence the riser as well as the faller

## First separation

- Event: `None`
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

The complete aligned downstream diff is in `COUNTERFACTUAL_DIFF.json`; the baseline and counterfactual trace files remain separate and complete.
