# LOOP 5 - THE DELTA (dual-fill / per-leg / pair; no exits anywhere)

- iter 1: TRAIN dual 0.205 medPairD -8 negShare 0.93 (n=1140) | HOLDOUT dual 0.110 medPairD -6 negShare 0.75 (n=53)
    adjusted: ATP_CHALL-B1 4->1 - ATP_CHALL-B4 6->3 - ATP_CHALL-B6 4->1 - ATP_MAIN-B1 3->1 - ATP_MAIN-B3 6->3 - ATP_MAIN-B5 2->1 - ATP_MAIN-B8 4->1 - WTA_CHALL-B1 12->9
- iter 2: TRAIN dual 0.437 medPairD -3 negShare 0.81 (n=2436) | HOLDOUT dual 0.202 medPairD -3 negShare 0.78 (n=97)
    adjusted: ATP_CHALL-B1 1->2 - ATP_CHALL-B4 3->1 - ATP_MAIN-B3 3->1 - WTA_CHALL-B1 9->6 - WTA_CHALL-B3 3->1 - WTA_CHALL-B8 2->1 - WTA_MAIN-B1 2->1 - WTA_MAIN-B3 5->2
- iter 3: TRAIN dual 0.627 medPairD -1 negShare 0.68 (n=3494) | HOLDOUT dual 0.317 medPairD -2 negShare 0.72 (n=152)
    adjusted: WTA_CHALL-B1 6->3 - WTA_CHALL-B3 1->2 - WTA_MAIN-B3 2->1
- iter 4: TRAIN dual 0.644 medPairD -1 negShare 0.67 (n=3588) | HOLDOUT dual 0.340 medPairD -2 negShare 0.74 (n=163)
    adjusted: WTA_CHALL-B1 3->1 - WTA_CHALL-B8 1->3
- iter 5: TRAIN dual 0.644 medPairD -1 negShare 0.67 (n=3590) | HOLDOUT dual 0.338 medPairD -2 negShare 0.73 (n=162)
    adjusted: WTA_CHALL-B3 2->1
- iter 6: TRAIN dual 0.655 medPairD -1 negShare 0.66 (n=3649) | HOLDOUT dual 0.342 medPairD -1 negShare 0.73 (n=164)
- STOP: CONVERGED.

## HOLDOUT VERDICT: dual-rate 0.342 - median pair delta -1 - negative-delta share 0.73 - duals n=164
PASS = duals>=10 AND median pair delta < 0: **HOLDOUT-PASS**
- ATP_CHALL-B1: legs 11 - leg-delta med -5 p25 -41 p75 +6
- ATP_CHALL-B4: legs 105 - leg-delta med -1 p25 -11 p75 +11
- ATP_CHALL-B6: legs 10 - leg-delta med +3 p25 -7 p75 +39
- ATP_MAIN-B1: legs 5 - leg-delta med +3 p25 -1 p75 +9
- ATP_MAIN-B3: legs 27 - leg-delta med +0 p25 -3 p75 +4
- ATP_MAIN-B5: legs 26 - leg-delta med -2 p25 -5 p75 +1
- ATP_MAIN-B8: legs 6 - leg-delta med -2 p25 -11 p75 -1
- ITF_M-B1: legs 2 - leg-delta med +7 p25 -7 p75 +7
- ITF_M-B3: legs 4 - leg-delta med +4 p25 -3 p75 +4
- ITF_M-B4: legs 6 - leg-delta med -1 p25 -5 p75 +0
- ITF_M-B6: legs 8 - leg-delta med +26 p25 -2 p75 +44
- ITF_W-B1: legs 16 - leg-delta med -1 p25 -4 p75 +3
- ITF_W-B2: legs 1 - leg-delta med +3 p25 +3 p75 +3
- ITF_W-B5: legs 1 - leg-delta med -13 p25 -13 p75 -13
- ITF_W-B7: legs 16 - leg-delta med +0 p25 -2 p75 +2
- WTA_CHALL-B1: legs 4 - leg-delta med +1 p25 -13 p75 +5
- WTA_CHALL-B3: legs 15 - leg-delta med +2 p25 -1 p75 +11
- WTA_CHALL-B6: legs 15 - leg-delta med -2 p25 -11 p75 -1
- WTA_CHALL-B8: legs 4 - leg-delta med +6 p25 -4 p75 +11
- WTA_MAIN-B1: legs 7 - leg-delta med +0 p25 -5 p75 +3
- WTA_MAIN-B3: legs 29 - leg-delta med -1 p25 -3 p75 +1
- WTA_MAIN-B6: legs 10 - leg-delta med +0 p25 -2 p75 +3
