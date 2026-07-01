# OMQS — FILL-vs-MIDPOINT on rested-hit >=75c FAVORITES (enriched tick recorder, Jun 24-30)

Anchor = MIDPOINT (bid_1+ask_1)/2 at the fill tick from analysis/premarket_ticks (NOT last_traded [22-min stale], NOT is_taker, NOT fv_mid). Corpus: ALL rested-hit (is_taker=maker) >=75c favorites, first buy-yes fill Jun 24-30, settled. n=115 corpus; 79 tick-covered; 78 two-sided-book at fill (mid-anchorable). fill_minus_mid = fill - mid (+ = rested ABOVE midpoint = distortion bid; - = at/below = discount).

## fill_minus_mid distribution (n=78 two-sided)
median -0.5, mean -0.7, min -4, max +5. Rested ABOVE mid: **4 (5%)**. AT/BELOW mid: **74 (95%)**.

## (2) SPLIT — above-mid vs at/below-mid
| bucket | n | deaths | death-rate | $-loss | W1-reach | CORRIDOR-reach | ERHROD (of deaths) |
|---|--:|--:|--:|--:|--:|--:|--:|
| rested ABOVE mid (distortion) | 4 | 0 | 0% | $0.00 | 0% | 0% | 0/0 |
| rested AT/BELOW mid (discount) | 74 | 7 | 9% | $-27.85 | 3% | 0% | 6/7 |

## (3) THE NUMBER
- AT/BELOW-mid absolute death-rate: **9%** (7/74).
- ABOVE-mid death-rate: **0%** (0/4).
- **death-rate delta (ABOVE - AT/BELOW) = -9 pp.**

## (4) INTEGRITY
- tick-recorder coverage: **79 / 115** corpus legs (36 uncovered, mostly Jun24-26).
- two-sided book at fill (bid & ask present, ask>bid): **78 / 79 covered**. locked (bid==ask): 0. one-sided/degenerate: 1.
- book-tick vs fill delta: median 32s, max 43234s (snapshot proximity to the fill instant).

## VERDICT
ABOVE-mid is only 4 legs (0 deaths) -- too thin to load-bear on its own; the AT/BELOW-mid (clean discount) favorites still die at 9% (7/74). ~95% of rested-hit favorite fills are AT/BELOW the midpoint (we sit at/below the best bid as a maker), so the favorite deaths are overwhelmingly clean-priced fills that rode to 0 anyway -- resting-bid quality vs the CURRENT midpoint does NOT explain the favorite ride-to-0. Favorites die by GEOMETRY (high fill, unreachable +band, -bid on the loss), regardless of rested-bid quality. Small-n caveat: only 7 deaths in the two-sided corpus, 4 above-mid legs -- the -9pp delta is noise, but the 95%-at/below-mid + 9%-geometry-death is the robust result.

## PER-LEG ROWS (all 79 covered; two-sided only have mid/fmm)
```
ticker                                   fp  bid ask  mid  f-mid book res w1 cor ERH
ATPCHALLENGERMATCH-26JUN29MALGOI-GOI     84   75  83 79.0     5 2s  yes n n  .
ATPCHALLENGERMATCH-26JUN29MELTEN-MEL     88   85  89 87.0     1 2s  yes n n  .
ATPCHALLENGERMATCH-26JUN28ANDRUI-AND     97   95  98 96.5     0 2s  yes n n  .
ATPCHALLENGERMATCH-26JUN28HIDTEN-TEN     97   95  98 96.5     0 2s  yes - -  .
ATPCHALLENGERMATCH-26JUN30MARRIB-RIB     86   86  87 86.5    -0 2s  yes - -  .
WTAMATCH-26JUN29SEINOS-NOS               91   91  92 91.5    -0 2s  yes - n  .
ATPMATCH-26JUN29WAWBER-BER               80   80  81 80.5    -0 2s  yes - n  .
WTAMATCH-26JUN30TOMBOL-TOM               86   86  87 86.5    -0 2s  no  n n  .
ATPCHALLENGERMATCH-26JUN30CASGAL-CAS     97   97  98 97.5    -0 2s  yes - -  .
WTAMATCH-26JUN29PODKOS-KOS               97   97  98 97.5    -0 2s  yes n n  .
ATPMATCH-26JUN29BLOZVE-ZVE               88   88  89 88.5    -0 2s  yes - n  .
WTAMATCH-26JUN29MERSIE-MER               75   75  76 75.5    -0 2s  yes - n  .
WTAMATCH-26JUN29BOIRYB-RYB               97   97  98 97.5    -0 2s  yes - n  .
ATPMATCH-26JUN29LEHPOP-LEH               78   78  79 78.5    -0 2s  yes n n  .
ATPMATCH-26JUN29KHAHAR-KHA               75   75  76 75.5    -0 2s  yes - n  .
ATPMATCH-26JUN29SWEDIM-DIM               77   77  78 77.5    -0 2s  yes - n  .
WTAMATCH-26JUN29EALZAR-EAL               86   86  87 86.5    -0 2s  yes n n  .
WTAMATCH-26JUN29SHYGOL-GOL               77   77  78 77.5    -0 2s  yes n n  .
WTAMATCH-26JUN29TOWSWI-SWI               86   86  87 86.5    -0 2s  yes n -  .
ATPMATCH-26JUN29MUNCER-CER               77   77  78 77.5    -0 2s  no  n n  E
WTAMATCH-26JUN29ANIGJO-ANI               94   94  95 94.5    -0 2s  yes - n  .
ATPMATCH-26JUN29VIRSHE-SHE               82   82  83 82.5    -0 2s  no  n n  E
ATPCHALLENGERMATCH-26JUN30DIATOB-DIA     84   84  85 84.5    -0 2s  yes n n  .
ATPMATCH-26JUN29DEBUR-DE                 95   95  96 95.5    -0 2s  yes n n  .
ATPMATCH-26JUN30FRILAJ-FRI               94   94  95 94.5    -0 2s  yes n n  .
ITFWMATCH-26JUN30ERCPAN-ERC              98   98  99 98.5    -0 2s  yes n -  .
ATPCHALLENGERMATCH-26JUN30MOELEC-MOE     77   77  78 77.5    -0 2s  yes n n  .
ATPCHALLENGERMATCH-26JUN30MIDHAI-MID     77   77  78 77.5    -0 2s  yes n n  .
ITFWMATCH-26JUN30YAMREN-YAM              91   91  92 91.5    -0 2s  yes n n  .
ATPCHALLENGERMATCH-26JUN29HUSMAN-HUS     78   78  79 78.5    -0 2s  no  n n  E
ATPCHALLENGERMATCH-26JUN29MBISOT-SOT     87   87  88 87.5    -0 2s  yes n n  .
WTAMATCH-26JUN29KORGAU-GAU               94   94  95 94.5    -0 2s  yes n n  .
WTAMATCH-26JUN29YASITO-YAS               82   82  83 82.5    -0 2s  yes n n  .
WTAMATCH-26JUN29OLIKES-KES               84   84  85 84.5    -0 2s  yes n n  .
ATPMATCH-26JUN29NAKPIN-NAK               80   80  81 80.5    -0 2s  yes n -  .
WTAMATCH-26JUN29MUCZAK-MUC               86   86  87 86.5    -0 2s  yes n -  .
WTAMATCH-26JUN29MINKAS-KAS               86   86  87 86.5    -0 2s  yes - n  .
WTAMATCH-26JUN29KREKLU-KRE               91   91  92 91.5    -0 2s  yes n n  .
ATPMATCH-26JUN29DAVCER-DAV               79   79  80 79.5    -0 2s  yes n n  .
ATPMATCH-26JUN29YIBDJO-DJO               93   93  94 93.5    -0 2s  yes n n  .
WTAMATCH-26JUN29ALEUDV-ALE               81   81  82 81.5    -0 2s  yes n n  .
ATPMATCH-26JUN29AUGSHE-AUG               95   95  96 95.5    -0 2s  yes n n  .
WTAMATCH-26JUN29LINAND-AND               82   82  83 82.5    -0 2s  yes n n  .
WTAMATCH-26JUN29JACOSA-OSA               84   84  85 84.5    -0 2s  yes n -  .
ATPMATCH-26JUN29BAUFON-FON               80   80  81 80.5    -0 2s  yes n -  .
ATPMATCH-26JUN29SVRTIE-TIE               88   88  89 88.5    -0 2s  yes - -  .
WTAMATCH-26JUN29PEGVID-PEG               93   93  94 93.5    -0 2s  yes - -  .
WTAMATCH-26JUN29OSTDAR-OST               76   76  77 76.5    -0 2s  yes n n  .
ATPMATCH-26JUN29JODGIL-JOD               85   85  86 85.5    -0 2s  yes n n  .
WTAMATCH-26JUN29CRIJOV-JOV               83   83  84 83.5    -0 2s  yes n -  .
ATPCHALLENGERMATCH-26JUN29GHEPOL-GHE     82   82  83 82.5    -0 2s  yes n -  .
ATPCHALLENGERMATCH-26JUN28KARTRO-TRO     75   75  76 75.5    -0 2s  yes n n  .
ITFMATCH-26JUN28DASTIX-TIX               80   80  81 80.5    -0 2s  yes n n  .
ATPCHALLENGERMATCH-26JUN28PRIMAL-PRI     79   79  80 79.5    -0 2s  no  n n  E
ATPCHALLENGERMATCH-26JUN28KUZSIN-KUZ     94   94  95 94.5    -0 2s  scalar n n  .
ATPCHALLENGERMATCH-26JUN28ROCSEG-ROC     93   93  94 93.5    -0 2s  yes n n  .
ATPCHALLENGERMATCH-26JUN28FOMJEC-FOM     89   89  90 89.5    -0 2s  yes n -  .
ATPCHALLENGERMATCH-26JUN30CREWAL-CRE     75   75  77 76.0    -1 2s  no  n n  E
ATPMATCH-26JUN29DZUFER-FER               78   78  80 79.0    -1 2s  yes - n  .
ITFWMATCH-26JUN30POLTVE-TVE              80   78  84 81.0    -1 2s  yes n -  .
ATPCHALLENGERMATCH-26JUN29DEYUN-DE       90   90  92 91.0    -1 2s  yes n n  .
ATPCHALLENGERMATCH-26JUN29HEIGOM-HEI     84   84  86 85.0    -1 2s  yes n n  .
ITFMATCH-26JUN29DONVAN-DON               82   82  84 83.0    -1 2s  yes n -  .
ATPCHALLENGERMATCH-26JUN29BLAKAO-BLA     80   80  82 81.0    -1 2s  no  n n  E
ATPCHALLENGERMATCH-26JUN28LANES-NES      78   78  80 79.0    -1 2s  yes n n  .
WTAMATCH-26JUN29DAYKEY-KEY               91   92  93 92.5    -2 2s  yes - n  .
ITFWMATCH-26JUN30BOYMIT-BOY              96   96  99 97.5    -2 2s  yes Y -  .
ITFMATCH-26JUN29TANNAK-TAN               88   88  91 89.5    -2 2s  yes n n  .
WTAMATCH-26JUN29JONPAR-PAR               76   77  78 77.5    -2 2s  yes n n  .
ITFWMATCH-26JUN29HEDBOW-BOW              82   82  85 83.5    -2 2s  yes Y -  .
ATPCHALLENGERMATCH-26JUN28BECGHA-GHA     77   77  80 78.5    -2 2s  yes n n  .
ITFMATCH-26JUN29HOSSIN-HOS               90   90  94 92.0    -2 2s  yes n n  .
ATPCHALLENGERMATCH-26JUN28SHIMAR-SHI     79   80  82 81.0    -2 2s  yes n n  .
ATPMATCH-26JUN29TRUDAM-DAM               77   79  80 79.5    -2 2s  yes n n  .
WTAMATCH-26JUN29BENSTO-BEN               88   90  91 90.5    -2 2s  yes n n  .
ITFMATCH-26JUN29GARCAR-GAR               78   78  83 80.5    -2 2s  yes n n  .
ATPCHALLENGERMATCH-26JUN29GULVAL-GUL     82   82  88 85.0    -3 2s  yes n n  .
ATPCHALLENGERMATCH-26JUN29ANDZEB-AND     87   87  95 91.0    -4 2s  yes n n  .
ITFMATCH-26JUN29VANWEI-VAN               89   91  90    -     - 1s  yes n n  .
```