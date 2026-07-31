# NIKVRB ask-side dwell replay

The corrected cold branch fills VRB at **68** and NIK at **18**. Reachability is ask-only and the minimum continuous ask dwell is **10 seconds**. That value is inherited from the already-frozen primary quote-touch comparator in WINDOW1_ORGAN_SCORECARD_AND_DEFECT_LEDGER.md, which defined the 598-event baseline before this NIKVRB correction. It was not selected from this game's outcome. Ten seconds eliminates non-resident quote flickers while retaining VRB's persistent ask-68 state.

## NIK T-178.867 to T-155.067

The retained episode census contains 63 bid-side episodes and zero ask-side episodes. Fifty-nine bid episodes have zero-second trough dwell; the other four dwell 1, 1, 13, and 25 seconds. Because the ask remains 29 throughout, this interval contains zero buy-side reachability opportunities and causes zero corrected target changes. The raw clock also contains 841 NIK BBO receipts and 240 bid changes in this interval; none has reachability authority.

## Corrected chronology

- VRB rests at 68 before the ask returns to 68. The ask persists 32 seconds by receipt sequence 326; the ten-second gate credits 68.
- NIK's 21 is cancelled when the sibling riser resolves. The 24 ask lasts 7 seconds and the 23 ask lasts 2 seconds, so neither releases patience. The 19 ask persists 11 seconds; ask-1 places 18 at sequence 3433. The later 18 ask persists 11 seconds and credits 18 at sequence 4250.

## 598 reconciliation

The old 10-second true-print-or-ask union contains 598 negative-pair opportunities. Ask-only ten-second reachability contains **532**. The 66 removed events depended on a lower true-print floor on at least one leg; they are not ask-reachable under this correction. The threshold table and all 66 identities are frozen in ASK_ONLY_OPPORTUNITY_RECONCILIATION.json.

## Corpus recut

The 392,282 mixed-side episodes become 154,734 ask-side episodes. Dwell bands: 74,391 at zero seconds; 69,363 at 1-9 seconds; 3,785 at 10-29; 2,646 at 30-59; 1,799 at 60-299; and 2,750 at 300 seconds or more. At least ten seconds leaves 10,980 ask-side episodes across 573 events.

The full arithmetic table and four charts are in NIKVRB_ASK_DWELL_TABLE_CHARTS.html. No live code, scorer, holdout, or production system was used.
