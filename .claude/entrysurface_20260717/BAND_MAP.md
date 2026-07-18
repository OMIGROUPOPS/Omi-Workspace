# ENTRY SURFACE — STAGE 1: THE BAND MAP (bands given by the market)

method: k-means on standardized (anchor, net, dip); k by max relative inertia-drop gain over k=2..8 (elbow), deterministic seed 20260717; per-cat HARD partition

## ATP_CHALL — 6 natural bands (n=6008 legs; elbow gains {3: 0.33, 4: 0.21, 5: 0.12, 6: 0.19, 7: 0.08, 8: 0.11})
- **ATP_CHALL-B1** n=1244 · anchors 6–34 (med 22) · FLAT (net med -1.0¢, width p75 7.0¢) · dip med 3.0¢
- **ATP_CHALL-B2** n=918 · anchors 27–79 (med 48) · FALLER (net med -18.0¢, width p75 24.0¢) · dip med 23.0¢
- **ATP_CHALL-B3** n=708 · anchors 21–68 (med 48) · RISER (net med +25.0¢, width p75 32.0¢) · dip med 3.0¢
- **ATP_CHALL-B4** n=1511 · anchors 37–64 (med 50) · FLAT (net med +0.0¢, width p75 6.0¢) · dip med 2.0¢
- **ATP_CHALL-B5** n=251 · anchors 42–93 (med 66) · FALLER (net med -37.0¢, width p75 45.0¢) · dip med 42.0¢
- **ATP_CHALL-B6** n=1376 · anchors 66–94 (med 78) · FLAT (net med +1.0¢, width p75 8.0¢) · dip med 2.0¢
  PAIR MIRROR (fav-band → dog-band, one object): ATP_CHALL-B6→ATP_CHALL-B1 1129 (38%) · ATP_CHALL-B4→ATP_CHALL-B4 623 (21%) · ATP_CHALL-B2→ATP_CHALL-B2 498 (17%) · ATP_CHALL-B5→ATP_CHALL-B2 174 (6%) · ATP_CHALL-B6→ATP_CHALL-B2 163 (5%) · ATP_CHALL-B2→ATP_CHALL-B4 92 (3%)

## ATP_MAIN — 8 natural bands (n=2111 legs; elbow gains {3: 0.35, 4: 0.23, 5: 0.19, 6: 0.12, 7: 0.03, 8: 0.15})
- **ATP_MAIN-B1** n=295 · anchors 5–29 (med 22) · FLAT (net med +0.0¢, width p75 6.0¢) · dip med 2.0¢
- **ATP_MAIN-B2** n=224 · anchors 20–47 (med 36) · FALLER (net med -17.0¢, width p75 22.0¢) · dip med 19.0¢
- **ATP_MAIN-B3** n=387 · anchors 31–49 (med 40) · FLAT (net med +0.0¢, width p75 5.0¢) · dip med 2.0¢
- **ATP_MAIN-B4** n=219 · anchors 22–66 (med 47) · RISER (net med +26.0¢, width p75 34.0¢) · dip med 3.0¢
- **ATP_MAIN-B5** n=423 · anchors 53–71 (med 62) · FLAT (net med +1.0¢, width p75 6.0¢) · dip med 2.0¢
- **ATP_MAIN-B6** n=83 · anchors 41–91 (med 63) · FALLER (net med -37.0¢, width p75 45.0¢) · dip med 40.0¢
- **ATP_MAIN-B7** n=130 · anchors 51–80 (med 65) · FALLER (net med -17.0¢, width p75 23.0¢) · dip med 24.0¢
- **ATP_MAIN-B8** n=350 · anchors 72–95 (med 79) · FLAT (net med +1.0¢, width p75 7.0¢) · dip med 2.0¢
  PAIR MIRROR (fav-band → dog-band, one object): ATP_MAIN-B5→ATP_MAIN-B3 337 (32%) · ATP_MAIN-B8→ATP_MAIN-B1 270 (26%) · ATP_MAIN-B5→ATP_MAIN-B2 75 (7%) · ATP_MAIN-B4→ATP_MAIN-B2 74 (7%) · ATP_MAIN-B7→ATP_MAIN-B4 68 (6%) · ATP_MAIN-B8→ATP_MAIN-B2 67 (6%)

## ITF_M — 7 natural bands (n=266 legs; elbow gains {3: 0.58, 4: 0.17, 5: 0.16, 6: 0.01, 7: 0.23, 8: 0.06})
- **ITF_M-B1** n=62 · anchors 8–32 (med 22) · FLAT (net med +0.0¢, width p75 3.0¢) · dip med 1.0¢
- **ITF_M-B2** n=9 · anchors 7–58 (med 40) · RISER (net med +26.0¢, width p75 30.0¢) · dip med 0.0¢
- **ITF_M-B3** n=45 · anchors 35–52 (med 43) · FLAT (net med -1.0¢, width p75 5.0¢) · dip med 3.0¢
- **ITF_M-B4** n=71 · anchors 50–72 (med 63) · FLAT (net med +0.0¢, width p75 4.0¢) · dip med 0.0¢
- **ITF_M-B5** n=12 · anchors 35–81 (med 66) · FALLER (net med -9.0¢, width p75 22.0¢) · dip med 23.0¢
- **ITF_M-B6** n=56 · anchors 73–92 (med 86) · FLAT (net med +0.0¢, width p75 3.0¢) · dip med 1.0¢
- **ITF_M-B7** n=11 · anchors 46–92 (med 92) · FALLER (net med -43.0¢, width p75 55.0¢) · dip med 51.0¢
  PAIR MIRROR (fav-band → dog-band, one object): ITF_M-B6→ITF_M-B1 42 (34%) · ITF_M-B4→ITF_M-B3 32 (26%) · ITF_M-B4→ITF_M-B1 14 (11%) · ITF_M-B3→ITF_M-B4 5 (4%) · ITF_M-B4→ITF_M-B2 3 (2%) · ITF_M-B5→ITF_M-B3 3 (2%)

## ITF_W — 8 natural bands (n=253 legs; elbow gains {3: 0.39, 4: 0.11, 5: 0.23, 6: 0.27, 7: -0.2, 8: 0.28})
- **ITF_W-B1** n=41 · anchors 12–29 (med 21) · FLAT (net med +0.0¢, width p75 3.0¢) · dip med 1.0¢
- **ITF_W-B2** n=57 · anchors 33–50 (med 42) · FLAT (net med +0.0¢, width p75 2.0¢) · dip med 1.0¢
- **ITF_W-B3** n=22 · anchors 21–60 (med 50) · FALLER (net med -7.0¢, width p75 9.0¢) · dip med 9.0¢
- **ITF_W-B4** n=6 · anchors 28–64 (med 57) · RISER (net med +29.0¢, width p75 32.0¢) · dip med 0.0¢
- **ITF_W-B5** n=65 · anchors 53–68 (med 60) · FLAT (net med +1.0¢, width p75 4.0¢) · dip med 0.0¢
- **ITF_W-B6** n=13 · anchors 33–81 (med 66) · FALLER (net med -17.0¢, width p75 18.0¢) · dip med 20.0¢
- **ITF_W-B7** n=48 · anchors 70–88 (med 79) · FLAT (net med +0.0¢, width p75 3.0¢) · dip med 1.0¢
- **ITF_W-B8** n=1 · anchors 82–82 (med 82) · FALLER (net med -50.0¢, width p75 50.0¢) · dip med 57.0¢
  PAIR MIRROR (fav-band → dog-band, one object): ITF_W-B5→ITF_W-B2 42 (36%) · ITF_W-B7→ITF_W-B1 34 (29%) · ITF_W-B7→ITF_W-B3 6 (5%) · ITF_W-B5→ITF_W-B3 5 (4%) · ITF_W-B7→ITF_W-B2 4 (3%) · ITF_W-B3→ITF_W-B2 4 (3%)

## WTA_CHALL — 8 natural bands (n=1423 legs; elbow gains {3: 0.34, 4: 0.22, 5: 0.12, 6: 0.22, 7: -0.14, 8: 0.24})
- **WTA_CHALL-B1** n=214 · anchors 6–29 (med 19) · FALLER (net med -2.0¢, width p75 7.0¢) · dip med 3.0¢
- **WTA_CHALL-B2** n=95 · anchors 16–51 (med 34) · RISER (net med +16.0¢, width p75 20.0¢) · dip med 1.0¢
- **WTA_CHALL-B3** n=250 · anchors 30–50 (med 41) · FLAT (net med +0.0¢, width p75 4.0¢) · dip med 2.0¢
- **WTA_CHALL-B4** n=190 · anchors 25–78 (med 49) · FALLER (net med -18.0¢, width p75 23.0¢) · dip med 22.0¢
- **WTA_CHALL-B5** n=91 · anchors 22–69 (med 53) · RISER (net med +29.0¢, width p75 39.0¢) · dip med 3.0¢
- **WTA_CHALL-B6** n=279 · anchors 53–71 (med 62) · FLAT (net med +0.0¢, width p75 5.0¢) · dip med 2.0¢
- **WTA_CHALL-B7** n=57 · anchors 46–91 (med 66) · FALLER (net med -39.0¢, width p75 50.0¢) · dip med 40.0¢
- **WTA_CHALL-B8** n=247 · anchors 73–94 (med 82) · FLAT (net med +1.0¢, width p75 10.0¢) · dip med 2.0¢
  PAIR MIRROR (fav-band → dog-band, one object): WTA_CHALL-B6→WTA_CHALL-B3 219 (31%) · WTA_CHALL-B8→WTA_CHALL-B1 201 (28%) · WTA_CHALL-B4→WTA_CHALL-B2 59 (8%) · WTA_CHALL-B5→WTA_CHALL-B4 44 (6%) · WTA_CHALL-B7→WTA_CHALL-B5 32 (5%) · WTA_CHALL-B8→WTA_CHALL-B4 27 (4%)

## WTA_MAIN — 6 natural bands (n=2109 legs; elbow gains {3: 0.34, 4: 0.23, 5: 0.2, 6: 0.15, 7: 0.09, 8: 0.07})
- **WTA_MAIN-B1** n=438 · anchors 6–34 (med 22) · FLAT (net med -1.0¢, width p75 8.0¢) · dip med 3.0¢
- **WTA_MAIN-B2** n=332 · anchors 26–74 (med 46) · FALLER (net med -19.0¢, width p75 25.0¢) · dip med 24.0¢
- **WTA_MAIN-B3** n=508 · anchors 37–63 (med 50) · FLAT (net med +1.0¢, width p75 6.0¢) · dip med 2.0¢
- **WTA_MAIN-B4** n=246 · anchors 20–67 (med 50) · RISER (net med +27.0¢, width p75 35.0¢) · dip med 2.0¢
- **WTA_MAIN-B5** n=81 · anchors 46–91 (med 65) · FALLER (net med -43.0¢, width p75 51.0¢) · dip med 47.0¢
- **WTA_MAIN-B6** n=504 · anchors 66–94 (med 77) · FLAT (net med +1.0¢, width p75 9.0¢) · dip med 2.0¢
  PAIR MIRROR (fav-band → dog-band, one object): WTA_MAIN-B6→WTA_MAIN-B1 417 (40%) · WTA_MAIN-B3→WTA_MAIN-B3 211 (20%) · WTA_MAIN-B3→WTA_MAIN-B2 129 (12%) · WTA_MAIN-B2→WTA_MAIN-B3 105 (10%) · WTA_MAIN-B5→WTA_MAIN-B3 62 (6%) · WTA_MAIN-B6→WTA_MAIN-B2 59 (6%)

