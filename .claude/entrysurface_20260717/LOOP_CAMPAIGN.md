# STAGE 4 — THE DRILL CAMPAIGN (holdout law: adjust on train, judged on held-out; gap printed every iteration)

- iter 1: TRAIN ROC -0.0287 (bids 9342 fills 4065) · HOLDOUT ROC -0.0208 (bids 776 fills 220) · gap -0.0079
    adjusted: ATP_CHALL-B1 4→3 · ATP_CHALL-B4 6→9 · ATP_CHALL-B6 4→7 · ATP_MAIN-B1 3→1 · ATP_MAIN-B3 11→13 · ATP_MAIN-B5 2→1 · ATP_MAIN-B8 4→1 · ITF_M-B6 11→14 (+7 more)
- iter 2: TRAIN ROC -0.0185 (bids 9383 fills 4451) · HOLDOUT ROC -0.0185 (bids 776 fills 236) · gap +0.0000
    adjusted: ATP_CHALL-B4 9→12 · ATP_CHALL-B6 7→10 · ATP_MAIN-B3 13→16 · ITF_M-B6 14→17 · WTA_CHALL-B1 15→16 · WTA_CHALL-B3 9→11 · WTA_MAIN-B1 2→1 · WTA_MAIN-B3 11→14
- iter 3: TRAIN ROC -0.0127 (bids 9387 fills 4195) · HOLDOUT ROC -0.0160 (bids 776 fills 228) · gap +0.0033
    adjusted: ATP_CHALL-B4 12→15 · ATP_CHALL-B6 10→13 · ATP_MAIN-B3 16→19 · ITF_M-B6 17→20 · WTA_MAIN-B3 14→16
- iter 4: TRAIN ROC -0.0067 (bids 9387 fills 3981) · HOLDOUT ROC -0.0140 (bids 776 fills 216) · gap +0.0073
    adjusted: ATP_CHALL-B4 15→18 · ATP_CHALL-B6 13→16 · ATP_MAIN-B3 19→22 · ITF_M-B6 20→23 · WTA_MAIN-B3 16→19
- iter 5: TRAIN ROC -0.0004 (bids 9365 fills 3758) · HOLDOUT ROC -0.0141 (bids 773 fills 210) · gap +0.0137
    adjusted: ATP_CHALL-B4 18→21 · ATP_CHALL-B6 16→19 · ATP_MAIN-B3 22→25 · ITF_M-B6 23→26 · WTA_MAIN-B3 19→22
- iter 6: TRAIN ROC 0.0018 (bids 9262 fills 3517) · HOLDOUT ROC -0.0114 (bids 770 fills 205) · gap +0.0132
    adjusted: ATP_CHALL-B4 21→24 · ATP_CHALL-B6 19→21 · ITF_M-B6 26→29 · WTA_MAIN-B3 22→25
- iter 7: TRAIN ROC 0.0041 (bids 9049 fills 3360) · HOLDOUT ROC -0.0121 (bids 768 fills 201) · gap +0.0162
    adjusted: ATP_CHALL-B4 24→27 · ATP_CHALL-B6 21→24 · ITF_M-B6 29→30 · WTA_MAIN-B3 25→28
- iter 8: TRAIN ROC 0.0077 (bids 8834 fills 3217) · HOLDOUT ROC -0.0107 (bids 759 fills 192) · gap +0.0184
    adjusted: ATP_CHALL-B4 27→28 · ATP_CHALL-B6 24→27 · WTA_MAIN-B3 28→30
- iter 9: TRAIN ROC 0.0091 (bids 8726 fills 3151) · HOLDOUT ROC -0.0102 (bids 754 fills 192) · gap +0.0193
    adjusted: ATP_CHALL-B6 27→29
- iter 10: TRAIN ROC 0.0093 (bids 8726 fills 3146) · HOLDOUT ROC -0.0101 (bids 754 fills 192) · gap +0.0194
- STOP: CONVERGED (no accepted step).

## STAGE 4 VALIDATION REPORT (held-out only; CI = 95% Wilson)
- ATP_CHALL-B1: depth 3¢ · holdout fills 11/24 (CI 0.28–0.65) vs predicted 1.15 · holdout ROC 0.0133 · FAILS (predicted 1.15 outside CI)
- ATP_CHALL-B4: depth 28¢ · holdout fills 10/150 (CI 0.04–0.12) vs predicted n/a · holdout ROC -0.0168 · OK
- ATP_CHALL-B6: depth 29¢ · holdout fills 3/24 (CI 0.04–0.31) vs predicted n/a · holdout ROC -0.0339 · OK
- ATP_MAIN-B1: depth 1¢ · holdout fills 5/5 (CI 0.57–1.00) vs predicted 1.25 · holdout ROC -0.2042 · OK
- ATP_MAIN-B3: depth 25¢ · holdout fills 3/33 (CI 0.03–0.24) vs predicted n/a · holdout ROC -0.0283 · OK
- ATP_MAIN-B5: depth 1¢ · holdout fills 26/38 (CI 0.53–0.81) vs predicted 1.70 · holdout ROC 0.0134 · FAILS (predicted 1.70 outside CI)
- ATP_MAIN-B8: depth 1¢ · holdout fills 4/6 (CI 0.30–0.90) vs predicted 1.13 · holdout ROC 0.0423 · OK
- ITF_M-B1: depth 3¢ · holdout fills 7/19 (CI 0.19–0.59) vs predicted 0.72 · holdout ROC 0.1072 · FAILS (predicted 0.72 outside CI)
- ITF_M-B3: depth 5¢ · holdout fills 9/36 (CI 0.14–0.41) vs predicted 0.80 · holdout ROC -0.0549 · FAILS (predicted 0.80 outside CI)
- ITF_M-B4: depth 11¢ · holdout fills 6/58 (CI 0.05–0.21) vs predicted 0.83 · holdout ROC -0.0052 · FAILS (predicted 0.83 outside CI)
- ITF_M-B6: depth 30¢ · holdout fills 1/39 (CI 0.00–0.13) vs predicted n/a · holdout ROC -0.0087 · OK
- ITF_W-B1: depth 1¢ · holdout fills 14/19 (CI 0.51–0.88) vs predicted 1.14 · holdout ROC -0.0149 · FAILS (predicted 1.14 outside CI)
- ITF_W-B2: depth 4¢ · holdout fills 14/52 (CI 0.17–0.40) vs predicted 1.60 · holdout ROC -0.0380 · FAILS (predicted 1.60 outside CI)
- ITF_W-B5: depth 10¢ · holdout fills 7/70 (CI 0.05–0.19) vs predicted 0.39 · holdout ROC 0.0077 · FAILS (predicted 0.39 outside CI)
- ITF_W-B7: depth 1¢ · holdout fills 22/28 (CI 0.60–0.90) vs predicted 1.14 · holdout ROC -0.0281 · FAILS (predicted 1.14 outside CI)
- WTA_CHALL-B1: depth 16¢ · holdout fills 0/7 (CI 0.00–0.35) vs predicted n/a · holdout ROC 0.0000 · OK
- WTA_CHALL-B3: depth 11¢ · holdout fills 7/36 (CI 0.10–0.35) vs predicted n/a · holdout ROC 0.0190 · OK
- WTA_CHALL-B6: depth 1¢ · holdout fills 20/35 (CI 0.41–0.72) vs predicted 0.88 · holdout ROC 0.0091 · FAILS (predicted 0.88 outside CI)
- WTA_CHALL-B8: depth 2¢ · holdout fills 5/16 (CI 0.14–0.56) vs predicted 0.46 · holdout ROC -0.0042 · OK
- WTA_MAIN-B1: depth 1¢ · holdout fills 8/9 (CI 0.56–0.98) vs predicted 0.85 · holdout ROC -0.0960 · OK
- WTA_MAIN-B3: depth 30¢ · holdout fills 0/37 (CI 0.00–0.09) vs predicted n/a · holdout ROC 0.0000 · OK
- WTA_MAIN-B6: depth 1¢ · holdout fills 10/13 (CI 0.50–0.92) vs predicted 0.64 · holdout ROC -0.0302 · OK

named failures: ['ATP_CHALL-B1', 'ATP_MAIN-B5', 'ITF_M-B1', 'ITF_M-B3', 'ITF_M-B4', 'ITF_W-B1', 'ITF_W-B2', 'ITF_W-B5', 'ITF_W-B7', 'WTA_CHALL-B6']
