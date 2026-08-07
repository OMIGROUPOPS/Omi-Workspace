# Window-1 sealed-171 exam: streaming repair and final result

The serializer repair preserved the frozen V36 and V35 policy bytes. Every
JSONL artifact now streams one row at a time through deterministic gzip, and
each brain is materialized and released before the next brain loads. The
focused writer passed at 1,074,817,990 uncompressed bytes with byte identity
and bounded memory. The post-repair DEV-804 audit reproduced both frozen full
decision traces, scorecards, and frontiers byte-for-byte.

Repair audit and policy-byte receipt:
https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/0a81bcb091959efdcc404e68fb33eb11c04e1701/.claude/window1_fresh_holdout_exam_serializer_repair_20260807/REPAIR_AUDIT_REPORT.md

Post-repair DEV inertness receipt:
https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/0a81bcb091959efdcc404e68fb33eb11c04e1701/.claude/window1_fresh_holdout_exam_serializer_repair_20260807/DEV_INERTNESS_POST_ALL_STREAMING/DEV_INERTNESS_RECEIPT.json

The first newly authorized process attempt evaluated all 171 V36 events and
then failed mechanically at Node's heap limit before V35 and before any score
row or result artifact. Its only generated file was the exact start receipt.
The authorization expressly allowed repair and re-attempt for that precise
pre-score mechanical class. The second attempt completed: total authorized
process attempts 2, permitted pre-score mechanical retries 1, score-emitting
runs 1, final brain invocations V36=1, V35=1, R3=0, score rows=12.

Mechanical failure receipt:
https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/0a81bcb091959efdcc404e68fb33eb11c04e1701/.claude/window1_fresh_holdout_exam_serializer_repair_20260807/MECHANICAL_FAILURE_ATTEMPT1_RECEIPT.json

Execution receipt:
https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/3beebcbbcd3e2d1e29804558ea4db71481890b05/.claude/window1_fresh_holdout_exam_results_20260807_serializer_repair/EXECUTION_COMPLETE_RECEIPT.json

The immutable population is 171 events / 342 legs. Input SHA-256 remains
`06ede0264a196bbebc005785c3ffdee5a840afe1a617f86f0354eedf65ac4313`
for the event list, `70f8b28749d8e1fd60e64af6e3ced41e556b2a20e5898ec692f0e4f7081b7c0a`
for boundaries, and
`f3924d1274e9b79bab2cbba133cc80d2ccd5622e0fa28a5c09bc0ec9448325a2`
for prints.

Control binding:
https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/3beebcbbcd3e2d1e29804558ea4db71481890b05/.claude/window1_fresh_holdout_exam_results_20260807_serializer_repair/CONTROL_BINDING.json

## Scorecard

| Brain | Column | DEV D=804 completed / under par | Sealed D=171 completed / under par | Full frontier <=93 / <=95 / <=97 / <100 / any |
|---|---:|---:|---:|---:|
| V36 | strict | 270 / 270 | 58 / 58 | 3 / 6 / 15 / 58 / 58 |
| V36 | census | 548 / 548 | 128 / 128 | 14 / 18 / 30 / 128 / 128 |
| V35 | strict | 264 / 264 | 59 / 59 | 4 / 7 / 15 / 59 / 59 |
| V35 | census | 550 / 550 | 128 / 128 | 15 / 19 / 28 / 128 / 128 |

V36 scorecard and frontiers:
https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/3beebcbbcd3e2d1e29804558ea4db71481890b05/.claude/window1_fresh_holdout_exam_results_20260807_serializer_repair/V36/SCORECARD_TWO_COLUMN.json

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/3beebcbbcd3e2d1e29804558ea4db71481890b05/.claude/window1_fresh_holdout_exam_results_20260807_serializer_repair/V36/STRICT_FRONTIER.json

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/3beebcbbcd3e2d1e29804558ea4db71481890b05/.claude/window1_fresh_holdout_exam_results_20260807_serializer_repair/V36/CENSUS_PRICED_FRONTIER.json

V35 scorecard and frontiers:
https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/3beebcbbcd3e2d1e29804558ea4db71481890b05/.claude/window1_fresh_holdout_exam_results_20260807_serializer_repair/V35/SCORECARD_TWO_COLUMN.json

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/3beebcbbcd3e2d1e29804558ea4db71481890b05/.claude/window1_fresh_holdout_exam_results_20260807_serializer_repair/V35/STRICT_FRONTIER.json

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/3beebcbbcd3e2d1e29804558ea4db71481890b05/.claude/window1_fresh_holdout_exam_results_20260807_serializer_repair/V35/CENSUS_PRICED_FRONTIER.json

The exact-bell core is the headline partition: D=11. Both brains produced
strict 3 completed / 3 under par with frontier 0/0/0/3/3, and census 10/10
with frontier 1/2/2/10/10. Exact-bell collapse-clean <=95 is 0 strict and 2
census for each brain.

The schedule-only partition is D=146. V36 produced strict 50/50 with frontier
2/5/13/50/50 and collapse-clean <=95=5; its census result is 105/105 with
12/15/24/105/105 and collapse-clean <=95=15. V35 produced strict 49/49 with
2/4/12/49/49 and collapse-clean <=95=4; its census result is 105/105 with
13/16/23/105/105 and collapse-clean <=95=16. The live-by-only D=14 partition
is V36 strict/census 5/13 and V35 strict/census 7/13.

Bell-confidence scorecard:
https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/3beebcbbcd3e2d1e29804558ea4db71481890b05/.claude/window1_fresh_holdout_exam_results_20260807_serializer_repair/BELL_CONFIDENCE_SCORECARD.json

V36 strict regret has 223 numeric / 119 null legs, median 1c, p75 3c, p90
11c, total 1,081c; census has 297 / 45, median 1c, p75 2c, p90 7c, total
966c. V35 strict has 223 / 119, median 1c, p75 3c, p90 9c, total 1,031c;
census has 297 / 45, median 1c, p75 2c, p90 6c, total 949c.

V36 regret gauges:
https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/3beebcbbcd3e2d1e29804558ea4db71481890b05/.claude/window1_fresh_holdout_exam_results_20260807_serializer_repair/V36/STRICT_REGRET_GAUGE.json

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/3beebcbbcd3e2d1e29804558ea4db71481890b05/.claude/window1_fresh_holdout_exam_results_20260807_serializer_repair/V36/CENSUS_PRICED_REGRET_GAUGE.json

V35 regret gauges:
https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/3beebcbbcd3e2d1e29804558ea4db71481890b05/.claude/window1_fresh_holdout_exam_results_20260807_serializer_repair/V35/STRICT_REGRET_GAUGE.json

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/3beebcbbcd3e2d1e29804558ea4db71481890b05/.claude/window1_fresh_holdout_exam_results_20260807_serializer_repair/V35/CENSUS_PRICED_REGRET_GAUGE.json

Strict fill evidence is V36 24 proven-maker / 200 proven-taker legs and V35
25 / 199. Both brains credit 224 strict legs. Census credits 298 legs: V36
10 proven-maker / 157 proven-taker / 131 one-cent conversions; V35 9 / 161 /
128.

All 51 manifest-bound result artifacts verify. Both brain packages are
byte-identical across two serialization builds with one policy replay each.
Forbidden access is zero for exam runtime network, live engine, account,
order, position, and trading surfaces; tuning and policy edits are zero.

Result manifest:
https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/3beebcbbcd3e2d1e29804558ea4db71481890b05/.claude/window1_fresh_holdout_exam_results_20260807_serializer_repair/ARTIFACT_HASH_MANIFEST.json

Forbidden-access receipt:
https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/3beebcbbcd3e2d1e29804558ea4db71481890b05/.claude/window1_fresh_holdout_exam_results_20260807_serializer_repair/FORBIDDEN_ACCESS_RECEIPT.json

VAULTED: serializer repaired without policy-byte change; one permitted
pre-score mechanical retry; one final score-emitting sealed run; V36 and V35
frozen results committed; R3 excluded; no tuning or live/trading access.
