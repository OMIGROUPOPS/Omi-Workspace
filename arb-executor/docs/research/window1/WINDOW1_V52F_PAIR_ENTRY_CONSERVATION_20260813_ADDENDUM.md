# V52f Iteration 5 - pair-entry conservation

Date: 2026-08-13

V52f adds exactly one licensing clause to frozen V52e. Once the other
expression is credited, a rest target is licensed only at
`target_cents <= 99 - credited_sibling_entry_cents`, which is the integer-cents
form of a completed pair settling strictly under 100. The clause bounds the
target; it adds no timing gate and uses no fitted margin. Before sibling
credit it is not applicable. Clauses 1-4, N9 continuous CLEAN priors,
trades-as-truth crediting, scavenger OFF, and `REFLEX_POST=0` are unchanged.

## Observation cohort

The observation set is five frozen pins plus a fresh 25. The four pre-stated
loss identities are fresh and explicitly included so the claim is
falsifiable; the remaining 21 are selected deterministically by category and
paired queue/formation/reflex stamps. The fresh 25 has zero overlap with all
V52b, V52c, V52d, and V52e fresh cohorts. The controlling-parent seed is
`2f4c65da1444a5133e3359f36691bb1c2524034c68fac0721a2e716c87290f12`.

Frozen V52e observes 14 completed pairs: 10 at delta and four at loss. V52f
observes 13 completed pairs, all 13 at delta, plus 11 partial and six neither;
the four states conserve to 30. VANDRO changes from 100 to a lawful partial.
ZHEBOU changes 100 to 99, BERSAI 100 to 99, and BARYUA 100 to 97. Therefore
all four pre-stated cases leave `COMPLETE_AT_LOSS`, and V52f creates zero new
loss pairs. These are 30-game observations only, not a full-804 disposition.

The clause-5 differential records 15,889 decision-receipt differences because
the new clause is present in every license. Only eight leg action streams
change behavior. Every behavioral difference begins at or after the first
clause-5 bind in that game. Clauses 1-4 and N9 have zero receipt differences;
all five pins are unharmed.

## Mechanical build record

Two attempts failed before package emission because Node retained duplicate
market and strict receipt diaries and exhausted 4 GB, then 8 GB heaps. The
mechanical repair suppresses only the unexported strict-ruler diary; strict
decisions and scores remain computed. Full market diaries are emitted in
deterministic five-game gzip chunks so no artifact exceeds GitHub's 100 MB
limit. A post-run proof repair changes differential attribution from leg grain
to the ruled pair-entry grain; policy decisions and cohort bytes are unchanged.

Two final clean builds are byte-identical across 47 files. Twelve focused and
inherited V52-family test files pass 355 assertions with zero failures,
omissions, or deselections. The final candidate trace contains 688,583 rows;
151,067 clause-5 license rows are retained. No full-804 run, sealed or holdout
access, deployment, authorization, live access, network runtime, order action,
position action, exit action, settlement action, or DCA access occurred.

Canonical package:
`.claude/window1_live_v4_replay/v52f_pair_entry_conservation_20260813/`.
