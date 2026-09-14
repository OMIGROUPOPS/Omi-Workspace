# Corrected reading of the native-cutoff challenge

Bench only, 2026-09-14. No engine change; no commit; push remains held.

## Ruling

The challenge is upheld. V1 did not contain native FIRST as a reachable expert.
Its rank-based era selectors could not express the fixed April 18 boundary,
and its non-FIRST kernels replaced rather than retained FIRST's price weights.
It was not a nested test demonstrating that the larger corpus could not help.

The rerun adds literal April 18 FIRST and exact tick-source FIRST to every
challenged family, plus calendar selectors derived from observed month starts.
Selection is no worse than exact FIRST on its matched earlier-validation CRPS.
That is an in-sample selection guarantee, not a guarantee for later games or
for floor MAE and timing, which are separate promotion requirements.

## Identity audit

All eight shared forecast fields agree between minute tick-only B and its
unified-library rows. Exact tick-source membership reproduces B at every one
of 61,196 formed side-receipts checked. No shared-row corruption was found.

The literal date is not identical to tick-source membership: CHALL includes
33 additional MINUTE-source games, April 18-29. MAIN has no such extras.
Counts: MAIN A=928, B=922, date=922; CHALL A=2,287, B=2,277, date=2,310.
Native A versus minute B also changes first-price ties/eligibility; exact B
reproduction must not be described as byte-identical native tick forecasts.
The outer questions remain the same 928 MAIN and 2,287 CHALL native queries.

## Validation and test are not the same conclusion

MAIN selects exact FIRST in all four families and all four months. CHALL
does so except May's ERA_SELECTOR:0.1 and
COMBINED_SELECTORS:0.1,0.75,0.75. These two genuinely used some older members
on earlier validation and beat its CRPS (2.76709 and 2.73635 versus 2.79797).
They did not clear the full validation bar: timing got worse on both sides;
combined-selector floor benefits were only 0.02823/0.08650 cents; the era
selector worsened favourite floor error by 0.05106 cents.

On May's matched test, era selector improves favourite/underdog floor MAE
by 0.03602/0.09333 cents and timing by 0.50029/5.05158 minutes. Combined
selectors improve floor MAE by 0.05330/0.10933 cents and timing by
1.35814/4.88157 minutes. These are real matched point-estimate gains, not zero.
However, both selected settings have ZERO callable test receipts with positive
pre-April-18 member weight. Their improvement is not evidence that the added
year supplied useful outcomes. Their selected kernels also change weights,
so this is not a pure older-membership intervention.

Coverage falls: May exact FIRST calls 4,289/4,277 favourite/underdog receipts;
era selector 4,279/4,263; combined selectors 4,272/4,256 (8,085 opportunities
per side). Across all months neither selected strategy clears the filed
minimum floor benefit, timing uncertainty, and no-worse-coverage requirements.
Best-older diagnostic settings in later months likewise do not establish the
required two-sided, both-tour improvement. They were chosen before their test
months, not selected retrospectively from test winners.

## What follows

The defensible conclusion is not "the corpus is bad" or "older games cannot
help." The native-safe option repairs the omitted baseline and recovers B.
No tested older-history key earns promotion under the signed bar. CRPS-only
selection must not be presented as floor/timing certification. Retain the
held push; do not promote the unified rebind from these results.

Evidence: ROW_AND_FORECAST_AUDIT.json, VALIDATION_CURVES.json,
VALIDATION_SIDE_METRICS.json, ATP_MAIN_RESULTS.json, ATP_CHALL_RESULTS.json.
These are historical re-tests, not fresh confirmation. Verification includes
all control receipts and five serial/parallel forecast checks per tour; it is
not represented as two full population passes.
