# Window-1 V25 estimator-overlay ruling

## A new layer is an overlay, never a gate

Where a new layer lacks authority—coverage absent, identity unresolved, causal state unresolved, minimum support unmet, or validation error bar not beaten—the incumbent path runs unchanged and byte-identical. Abstention cannot veto, replace, suppress, or delay an incumbent action. V19's abstention fallback is the canonical template.

## Standalone estimator accuracy

The walk-forward estimator covered `336/1,608` legs (`0.208955223880597`). Its aggregate q50 MAE was `1.7708333333333333` cents versus `1.7083333333333333` cents for decision-time live ask used as the close baseline. Bias was `+0.14583333333333334` cents. The q25–q75 interval contained `203/336` audited closes (`0.6041666666666666`).

Direct category×path-family fits covered `183` legs: MAE `1.4262295081967213`, bias `-0.2568306010928962`, interval coverage `0.6994535519125683`. Parent-pooled fits covered `153`: MAE `2.183006535947712`, bias `+0.6274509803921569`, interval coverage `0.49019607843137253`.

Cell authority was pre-stated as: validation `n>=30`; q50 MAE strictly lower than the decision-time-live-ask baseline MAE; q25–q75 empirical coverage at least `0.50`. Zero category×price-region cells satisfied all three checks. Therefore the estimator earned no placement authority.

Sources:

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/2373631762e0af9d3ab4620a55ad8fe43a0729fc/.claude/window1_live_v4_replay/landing_estimator_accuracy_census_20260804/ESTIMATOR_ACCURACY_CENSUS.json

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/2373631762e0af9d3ab4620a55ad8fe43a0729fc/.claude/window1_live_v4_replay/landing_estimator_accuracy_census_20260804/ESTIMATOR_ACCURACY_LEDGER.jsonl.gz

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/2373631762e0af9d3ab4620a55ad8fe43a0729fc/.claude/window1_live_v4_replay/landing_estimator_accuracy_census_20260804/OVERLAY_CELL_AUTHORITY.json

## V25 result

V25 evaluates the estimator only as an overlay. With zero authorized cells it executes the V19-style fallback on all `1,608` leg streams. The V25 event ledger and leg ledger are byte-identical to V23: zero differing leg streams, `1,608` identical streams, and zero overlay actions.

Consequently V25 exactly preserves V23: `1,027` acted legs, `920` credited legs, `204` completed pairs, `193` under-par pairs, `45` audited JOINT pairs, and `88` carried pairs. The 1,608-row miss ledger contains `920` incumbent captures, `581` incumbent no-actions, and `107` incumbent actions without credit.

Sources:

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/2373631762e0af9d3ab4620a55ad8fe43a0729fc/.claude/window1_live_v4_replay/landing_estimator_overlay_v25_20260804/DIFFERENTIAL_RECEIPT.json

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/2373631762e0af9d3ab4620a55ad8fe43a0729fc/.claude/window1_live_v4_replay/landing_estimator_overlay_v25_20260804/FRONTIER.json

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/2373631762e0af9d3ab4620a55ad8fe43a0729fc/.claude/window1_live_v4_replay/landing_estimator_overlay_v25_20260804/REGRET_GAUGE.json

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/2373631762e0af9d3ab4620a55ad8fe43a0729fc/.claude/window1_live_v4_replay/landing_estimator_overlay_v25_20260804/MISS_LEDGER_CONSERVATION.json

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/2373631762e0af9d3ab4620a55ad8fe43a0729fc/.claude/window1_live_v4_replay/landing_estimator_overlay_v25_20260804/OVERLAY_AUTHORITY_RECEIPT.json

## Integrity

The standalone census and V25 package each passed two clean byte-identical builds: six census artifacts and thirteen V25 artifacts compared, with zero mismatches. The combined focused and inherited pass was `26/26`: four estimator-census tests, six V25 overlay tests, nine V24 tests, six V23 tests, and one simultaneous-cap test. No holdout, live, network, order, position, exit, settlement, DCA, Window-2, deployment, or authorization action occurred.

Sources:

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/2373631762e0af9d3ab4620a55ad8fe43a0729fc/.claude/window1_live_v4_replay/landing_estimator_accuracy_census_20260804/DETERMINISM_RECEIPT.json

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/2373631762e0af9d3ab4620a55ad8fe43a0729fc/.claude/window1_live_v4_replay/landing_estimator_overlay_v25_20260804/DETERMINISM_RECEIPT.json

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/2373631762e0af9d3ab4620a55ad8fe43a0729fc/.claude/window1_live_v4_replay/landing_estimator_overlay_v25_20260804/ARTIFACT_HASH_MANIFEST.json

V23 remains operative. V25 validates the overlay fallback but does not establish predictive authority for the current landing estimator.
