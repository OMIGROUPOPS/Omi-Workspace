# STAGE 4b — RE-FRAMED DRILL (each strategy in its own frame; all-window divots, conception casts, touch parks)

- iter 1: TRAIN ROC -0.0300 (bids 10883 fills 4869) · HOLDOUT ROC -0.0192 (bids 988 fills 282) · gap -0.0108
    adjusted: ATP_CHALL-B4 6→9 · ATP_CHALL-B6 4→7 · ATP_MAIN-B1 3→1 · ATP_MAIN-B3 11→14 · ATP_MAIN-B5 2→1 · ATP_MAIN-B8 4→1 · ITF_M-B6 11→14 · WTA_CHALL-B1 12→15 (+6 more)
- iter 2: TRAIN ROC -0.0191 (bids 10895 fills 5322) · HOLDOUT ROC -0.0158 (bids 988 fills 316) · gap -0.0033
    adjusted: ATP_CHALL-B4 9→12 · ATP_CHALL-B6 7→9 · ATP_MAIN-B3 14→17 · ITF_M-B6 14→17 · WTA_CHALL-B1 15→16 · WTA_CHALL-B3 4→1 · WTA_CHALL-B8 2→1 · WTA_MAIN-B1 2→1
- iter 3: TRAIN ROC -0.0129 (bids 10920 fills 5365) · HOLDOUT ROC -0.0168 (bids 992 fills 331) · gap +0.0039
    adjusted: ATP_CHALL-B4 12→15 · ATP_CHALL-B6 9→12 · ATP_MAIN-B3 17→20 · ITF_M-B6 17→20
- iter 4: TRAIN ROC -0.0074 (bids 10918 fills 5136) · HOLDOUT ROC -0.0146 (bids 992 fills 319) · gap +0.0072
    adjusted: ATP_CHALL-B4 15→18 · ATP_CHALL-B6 12→15 · ATP_MAIN-B3 20→23 · ITF_M-B6 20→23
- iter 5: TRAIN ROC -0.0021 (bids 10886 fills 4902) · HOLDOUT ROC -0.0155 (bids 989 fills 311) · gap +0.0134
    adjusted: ATP_CHALL-B4 18→20 · ATP_CHALL-B6 15→18 · ATP_MAIN-B3 23→25 · ITF_M-B6 23→26
- iter 6: TRAIN ROC -0.0017 (bids 10858 fills 4736) · HOLDOUT ROC -0.0142 (bids 989 fills 308) · gap +0.0125
    adjusted: ATP_CHALL-B4 20→23 · ATP_CHALL-B6 18→21 · ITF_M-B6 26→29
- iter 7: TRAIN ROC -0.0011 (bids 10739 fills 4565) · HOLDOUT ROC -0.0129 (bids 989 fills 305) · gap +0.0118
    adjusted: ATP_CHALL-B4 23→26 · ATP_CHALL-B6 21→24 · ITF_M-B6 29→30
- iter 8: TRAIN ROC 0.0016 (bids 10553 fills 4415) · HOLDOUT ROC -0.0119 (bids 982 fills 298) · gap +0.0135
    adjusted: ATP_CHALL-B4 26→28 · ATP_CHALL-B6 24→27
- iter 9: TRAIN ROC 0.0028 (bids 10421 fills 4325) · HOLDOUT ROC -0.0111 (bids 976 fills 298) · gap +0.0139
    adjusted: ATP_CHALL-B6 27→30
- iter 10: TRAIN ROC 0.0029 (bids 10421 fills 4308) · HOLDOUT ROC -0.0110 (bids 976 fills 298) · gap +0.0139
- STOP: CONVERGED.

## VALIDATION REPORT v2 (holdout only) + VERDICT DELTAS vs 4a
- ATP_CHALL-B1: depth 4¢ · holdout 12/26 (CI 0.29–0.65) vs pred 0.88 · ROC 0.0809 · FAILS · 4a-FAIL → STILL FAILS: REAL
- ATP_CHALL-B4: depth 28¢ · holdout 11/160 (CI 0.04–0.12) vs pred n/a · ROC -0.0153 · OK
- ATP_CHALL-B6: depth 30¢ · holdout 3/24 (CI 0.04–0.31) vs pred n/a · ROC -0.0321 · OK
- ATP_MAIN-B1: depth 1¢ · holdout 11/11 (CI 0.74–1.00) vs pred 1.25 · ROC -0.1135 · OK
- ATP_MAIN-B3: depth 25¢ · holdout 2/32 (CI 0.02–0.20) vs pred n/a · ROC -0.0135 · OK
- ATP_MAIN-B5: depth 1¢ · holdout 28/36 (CI 0.62–0.88) vs pred 1.70 · ROC 0.0129 · FAILS · 4a-FAIL → STILL FAILS: REAL
- ATP_MAIN-B8: depth 1¢ · holdout 9/10 (CI 0.60–0.98) vs pred 1.13 · ROC -0.0250 · FAILS
- ITF_M-B1: depth 3¢ · holdout 14/38 (CI 0.23–0.53) vs pred 0.72 · ROC 0.0522 · FAILS · 4a-FAIL → STILL FAILS: REAL
- ITF_M-B3: depth 5¢ · holdout 16/75 (CI 0.14–0.32) vs pred 0.80 · ROC -0.0214 · FAILS · 4a-FAIL → STILL FAILS: REAL
- ITF_M-B4: depth 11¢ · holdout 10/84 (CI 0.07–0.21) vs pred 0.83 · ROC 0.0021 · FAILS · 4a-FAIL → STILL FAILS: REAL
- ITF_M-B6: depth 30¢ · holdout 9/64 (CI 0.08–0.25) vs pred n/a · ROC -0.0220 · OK
- ITF_W-B1: depth 1¢ · holdout 21/32 (CI 0.48–0.80) vs pred 1.14 · ROC -0.0061 · FAILS · 4a-FAIL → STILL FAILS: REAL
- ITF_W-B2: depth 4¢ · holdout 24/89 (CI 0.19–0.37) vs pred 1.60 · ROC -0.0293 · FAILS · 4a-FAIL → STILL FAILS: REAL
- ITF_W-B5: depth 10¢ · holdout 7/92 (CI 0.04–0.15) vs pred 0.39 · ROC 0.0059 · FAILS · 4a-FAIL → STILL FAILS: REAL
- ITF_W-B7: depth 1¢ · holdout 28/40 (CI 0.55–0.82) vs pred 1.14 · ROC -0.0269 · FAILS · 4a-FAIL → STILL FAILS: REAL
- WTA_CHALL-B1: holdout n=4 — TOO THIN (said so).
- WTA_CHALL-B3: depth 1¢ · holdout 34/45 (CI 0.61–0.86) vs pred 1.20 · ROC -0.0488 · FAILS
- WTA_CHALL-B6: depth 1¢ · holdout 21/35 (CI 0.44–0.74) vs pred 0.88 · ROC -0.0103 · FAILS · 4a-FAIL → STILL FAILS: REAL
- WTA_CHALL-B8: depth 1¢ · holdout 12/17 (CI 0.47–0.87) vs pred 0.54 · ROC 0.0197 · OK
- WTA_MAIN-B1: depth 1¢ · holdout 9/9 (CI 0.70–1.00) vs pred 0.85 · ROC 0.0300 · OK
- WTA_MAIN-B3: depth 11¢ · holdout 7/40 (CI 0.09–0.32) vs pred 0.31 · ROC -0.0401 · OK
- WTA_MAIN-B6: depth 1¢ · holdout 10/13 (CI 0.50–0.92) vs pred 0.64 · ROC -0.0302 · OK

named failures v2: ['ATP_CHALL-B1', 'ATP_MAIN-B5', 'ATP_MAIN-B8', 'ITF_M-B1', 'ITF_M-B3', 'ITF_M-B4', 'ITF_W-B1', 'ITF_W-B2', 'ITF_W-B5', 'ITF_W-B7', 'WTA_CHALL-B3', 'WTA_CHALL-B6']
