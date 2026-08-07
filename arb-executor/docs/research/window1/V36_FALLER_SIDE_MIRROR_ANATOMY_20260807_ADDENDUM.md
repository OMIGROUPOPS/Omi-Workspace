# V36 faller-side mirror anatomy — 2026-08-07

This is read-only analysis of frozen V36 `bfde0d8d1135f5c5f48a5f3d619ab30050efab83` against the union-reach gap ledger at `b581cbb58f660939ed9b0c2e88ddc42163dbab9a`. No policy, replay, scorer, live, or trading path was invoked.

## Population and ruler

“Faller side” means V36's combined state was `FALLING` at the union-reach bottom moment. It does not mean the reach ledger's ex-post path-direction label was `FALLING`; disagreement between those two is the diagnostic `STATE_MISLABELED` class.

The frozen population is 511 sides: 399 missed or shallow issue sides and 112 captured controls. Original gap ownership conserves as 75 off-reach missing rests / 297 cents, 54 off-reach shallow rests / 455 cents, 72 shallow takes / 297 cents, 124 cap misses / 411 cents, 39 unimplemented-divot misses / 107 cents, and 35 strict-fill seams / zero policy cents. Total measured issue damage is 1,567 cents.

The mutually exclusive anatomy is 157 `STATE_MISLABELED` / 835 cents, 125 `CAP_BOUND` / 412 cents, 54 `REST_TOO_SHALLOW` / 273 cents, 28 `REST_WALKED_TOO_SLOW` / 47 cents, and 35 `STRICT_FILL_SEAM_NOT_POLICY` / zero cents. The strict seam stays outside policy damage because the rest was resident at-or-above union reach and only the print-cross build-verification ruler withheld credit.

## Candidate slate and lift

No separately committed riser-exam schema was present on the fetched analysis ref. The candidate slate is therefore frozen exactly to the operator-named fields: own and sibling combined state, both pressure reads and their joint tuple, own and sibling spread+dwell, and pair-cap room. Every value is taken from the latest lawful V36 receipt at or before the union-reach evidence; snapshot age is retained.

Lift is descriptive: `P(V36 credited at-or-better than union reach | signal) - same-cell faller control capture rate`, in percentage points. It is reported per category and per category × price region; n<20 stays marked thin and is never pooled.

Among n>=20 category rows, the strongest positive capture lifts are ATP_CHALL own `spread=1 + dwell<10/unknown` (+24.582pp, n=57), ATP_MAIN own pressure `SETTLED` (+12.444pp, n=25), WTA_CHALL own `spread=1 + dwell<10/unknown` (+19.908pp, n=25), and WTA_MAIN sibling pressure `SETTLED` (+5.813pp, n=40). The strongest negative rows are ATP_CHALL own `spread=2 + dwell>=10` (-17.204pp, n=22), ATP_MAIN joint pressure `FALLING|SETTLED` (-8.413pp, n=28), WTA_CHALL joint pressure `FALLING|SETTLED` (-16.092pp, n=36), and WTA_MAIN joint pressure `FALLING|FALLING` (-8.051pp, n=22). These are descriptive lifts, not fitted authority.

## Named anatomy

- GANJAN|GAN is the captured control: reach 20, entry 20. At reach the rest stood 18 under a FALLING quote path, own pressure SETTLED, sibling state RISING/pressure SETTLED, spread 1, and cap exactly at reach.
- KRALOR|KRA is `CAP_BOUND`: reach 95, no entry, rest 93, cap 94. Own state/pressure were FALLING, sibling state/pressure RISING, both spreads 1 with qualified dwell. Damage is one cent.
- WESPAA|PAA is `STATE_MISLABELED`: V36 read FALLING while the frozen reach path was CLIMBING. Reach was 38, rest 37, own pressure RISING, sibling state RISING/pressure FALLING, both spreads 1 with qualified dwell. Damage is one cent.

## Proof

The builder streamed and reconciled all 3,631,920 frozen V36 full-trace rows. Every one of 511 own reach snapshots matched the controlling gap ledger; all sibling snapshots and rest-walk receipts are retained. Two clean builds compared 12 regenerable files byte-for-byte with zero mismatches. Focused tests pass 9/9. Forbidden access and mutation counts are all zero.
