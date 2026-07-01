# OMQS — THREE-PRICE FILL-QUALITY on >=75c RESTED-HIT FAVORITES (enriched-book tick tape)

Source: bot enriched tick recorder (analysis/premarket_ticks/*.csv: bid_1/ask_1/last_trade/mid per tick, ET) at the fill tick + Kalshi /portfolio/fills (fill_ts, fill_price) + /markets/trades (last-trade age, fill-match delta). 78 rested-hit favorites (>=75c, is_taker=maker); 61 have tick-recorder coverage (17 not recorded, mostly 26JUN26). fill_minus_lasttraded = fill - last_traded at fill tick (+ = rested ABOVE recent last-trade = DISTORTION bid; - = discount). NO is_taker, NO fv_mid.

## HEADLINE — fill vs last-traded at the fill tick (n=61 covered w/ last)
fill_minus_lasttraded: median -1.0, mean -0.6, min -13, max +37.
**Rested ABOVE last-traded (distortion bid): 6 (10%). Rested AT/BELOW (discount/at-market): 55 (90%).**

## DISTORTION predicts ride-to-0? (loss = settled 0)
| group | n | loss-rate% | mean fill_minus_last |
|---|--:|--:|--:|
| rested ABOVE last (distortion) | 6 | 33% | +7.3 |
| rested AT/BELOW last (discount) | 55 | 9% | -1.5 |

| fill_minus_last bucket | n | loss-rate% | mean |
|---|--:|--:|--:|
| 1_disc(<=-3) | 8 | 0% | -4.9 |
| 2_slight_disc(-3..0) | 38 | 13% | -1.1 |
| 3_at_last(0) | 9 | 0% | +0.0 |
| 4_slight_over(0..+3) | 4 | 25% | +1.0 |
| 5_distortion(>=+3) | 2 | 50% | +20.0 |

## SPREAD, LOCKED-BOOK, STALENESS (integrity)
- spread_at_fill (ask-bid): median 1 c, max 8 c. LOCKED books (bid==ask) at fill: **0 of 61**.
- last_trade_age (fill_ts - previous trade, sec): median 1353s, p90 7396s, max 32918s, minutes-stale(>60s): 60.
- book-tick vs fill delta (sec): median 32.0, max 102.0. fill vs nearest /markets/trade delta (sec): median 830.0, max 8384.6 (both ~0 => timestamps align, right tick pulled).

## VERDICT
Among the >=75c rested-hit favorites, **90% rested AT or BELOW the last-traded price** (genuine discount / at-market maker fills); only **10% rested above last-traded (distortion bid)**, and the severe-distortion tail (>=+3) is small. Distortion bids DO die somewhat more (ABOVE-last loss-rate 33% vs AT/BELOW 9%), so a few favorite losses ARE fixable-entry (do not rest a bid above recent last-trade). BUT the bulk of favorite fills are good maker prices that still ride to 0 when the favorite loses the match, and staleness is a real confound (median last_trade_age 1353s on these illiquid favorites => "last-traded" is itself a lagging reference). CONCLUSION: distortion-bid entry is a MINORITY, secondary contributor; it does not explain the favorite bleed, which remains dominated by exit geometry (high-price favorite that loses rides -bid regardless of a clean fill). The fixable-entry slice = the 6 above-last legs; the rest is geometry.

## PER-LEG ROWS (all 78; cov=n means no tick recorder)
```
ticker                                 fp  bid ask last mid  f-last spr fpos lock lastage% tickd res knife
ATPCHALLENGERMATCH-26JUN29ROLSHA-ROL   95   56  57   58   56    37   1 39.00    .   1687    -2 no  K
ITFWMATCH-26JUN26DAEVAS-DAE            76  (no tick recorder)                              res=yes
ATPCHALLENGERMATCH-26JUN29ANDZEB-AND   86   87  95   83   91     3   8 -0.12    .  23970   -45 yes .
ATPCHALLENGERMATCH-26JUN28DELLEC-LEC   90  (no tick recorder)                              res=yes
ATPCHALLENGERMATCH-26JUN28PRIMAL-PRI   79   79  80   78   80     1   1 0.00    .   2404   -32 no  K
ATPMATCH-26JUN29DEBUR-DE               95   95  96   94   96     1   1 0.00    .    761   -40 yes .
ATPMATCH-26JUN29LEHPOP-LEH             78   78  79   77   78     1   1 0.00    .    920   -38 yes .
WTAMATCH-26JUN29SEINOS-NOS             91   91  92   90   92     1   1 0.00    .    527   -31 yes .
WTAMATCH-26JUN26WANOSA-OSA             78  (no tick recorder)                              res=yes
WTAMATCH-26JUN26MARKEY-KEY             84  (no tick recorder)                              res=yes
ITFMATCH-26JUN27WALREH-REH             76  (no tick recorder)                              res=yes
ATPCHALLENGERMATCH-26JUN29GHEPOL-GHE   82   82  83   82   82     0   1 0.00    .    113   -13 yes .
ATPMATCH-26JUN29BAUFON-FON             80   80  81   80   80     0   1 0.00    .   2466   -65 yes .
ATPCHALLENGERMATCH-26JUN29HEIGOM-HEI   84   84  86   84   85     0   2 0.00    .  22139   -35 yes .
WTAMATCH-26JUN29YASITO-YAS             82   82  83   82   82     0   1 0.00    .   7396   -14 yes .
WTAMATCH-26JUN29ALEUDV-ALE             81   81  82   81   82     0   1 0.00    .   1223   -64 yes .
WTAMATCH-26JUN29ANIGJO-ANI             94   94  95   94   94     0   1 0.00    .   1125   -23 yes .
ATPMATCH-26JUN30FRILAJ-FRI             94   94  95   94   94     0   1 0.00    .    687    -5 yes .
WTAMATCH-26JUN29SHYGOL-GOL             77   77  78   77   78     0   1 0.00    .   1187     0 yes .
WTAMATCH-26JUN29EALZAR-EAL             86   86  87   86   86     0   1 0.00    .   1353    10 yes .
ATPCHALLENGERMATCH-26JUN26KICZAN-KIC   83  (no tick recorder)                              res=yes
ATPCHALLENGERMATCH-26JUN28CIAKRA-KRA   90  (no tick recorder)                              res=yes
ATPCHALLENGERMATCH-26JUN28CHAALU-CHA   84  (no tick recorder)                              res=yes
ATPCHALLENGERMATCH-26JUN28GELRIB-RIB   90  (no tick recorder)                              res=yes
ATPCHALLENGERMATCH-26JUN28ANDRUI-AND   97   95  98   98   96    -1   3 0.67    .   7245     0 yes .
ATPCHALLENGERMATCH-26JUN29GULVAL-GUL   81   82  88   82   85    -1   6 -0.17    .    352   -34 yes .
ATPMATCH-26JUN29JODGIL-JOD             85   85  86   86   86    -1   1 0.00    .    288   -63 yes .
WTAMATCH-26JUN29CRIJOV-JOV             83   83  84   84   84    -1   1 0.00    .      4  -102 yes .
WTAMATCH-26JUN29OSTDAR-OST             76   76  77   77   76    -1   1 0.00    .    467   -53 yes .
ATPCHALLENGERMATCH-26JUN29BLAKAO-BLA   80   80  82   81   81    -1   2 0.00    .   2536   -69 no  K
WTAMATCH-26JUN29JACOSA-OSA             84   84  85   85   84    -1   1 0.00    .   1233   -57 yes .
ATPCHALLENGERMATCH-26JUN29DEYUN-DE     90   90  92   91   91    -1   2 0.00    .  23857   -23 yes .
ATPMATCH-26JUN29DAVCER-DAV             79   79  80   80   80    -1   1 0.00    .   3855   -72 yes .
WTAMATCH-26JUN29MINKAS-KAS             86   86  87   87   86    -1   1 0.00    .    830   -26 yes .
ATPMATCH-26JUN29AUGSHE-AUG             95   95  96   96   96    -1   1 0.00    .   7218   -92 yes .
WTAMATCH-26JUN29OLIKES-KES             84   84  85   85   84    -1   1 0.00    .   4080   -30 yes .
WTAMATCH-26JUN29KREKLU-KRE             91   91  92   92   92    -1   1 0.00    .   2910   -48 yes .
WTAMATCH-26JUN29LINAND-AND             82   82  83   83   82    -1   1 0.00    .   2495   -29 yes .
WTAMATCH-26JUN29MUCZAK-MUC             86   86  87   87   86    -1   1 0.00    .    974   -16 yes .
WTAMATCH-26JUN29KORGAU-GAU             94   94  95   95   94    -1   1 0.00    .   1190   -24 yes .
WTAMATCH-26JUN29JONPAR-PAR             76   77  78   77   78    -1   1 -1.00    .    630   -31 yes .
ATPMATCH-26JUN29NAKPIN-NAK             80   80  81   81   80    -1   1 0.00    .   2222   -47 yes .
ATPCHALLENGERMATCH-26JUN29HUSMAN-HUS   78   78  79   79   78    -1   1 0.00    .   5563   -53 no  K
ITFWMATCH-26JUN30YAMREN-YAM            91   91  92   92   92    -1   1 0.00    .   1226   -60 yes .
ATPCHALLENGERMATCH-26JUN30MIDHAI-MID   77   77  78   78   78    -1   1 0.00    .   4876  -100 yes .
ATPCHALLENGERMATCH-26JUN30MOELEC-MOE   77   77  78   78   78    -1   1 0.00    .   2527   -62 yes .
ATPCHALLENGERMATCH-26JUN30DIATOB-DIA   84   84  85   85   84    -1   1 0.00    .   2799   -98 yes .
ATPMATCH-26JUN29DZUFER-FER             78   78  80   79   79    -1   2 0.00    .    690   -12 yes .
WTAMATCH-26JUN29TOWSWI-SWI             86   86  87   87   86    -1   1 0.00    .    148   -56 yes .
ATPMATCH-26JUN29MUNCER-CER             77   77  78   78   78    -1   1 0.00    .    391   -30 no  K
ATPMATCH-26JUN29KHAHAR-KHA             75   75  76   76   76    -1   1 0.00    .    317   -11 yes .
WTAMATCH-26JUN29BOIRYB-RYB             97   97  98   98   98    -1   1 0.00    .   2172   -47 yes .
ATPMATCH-26JUN29BLOZVE-ZVE             88   88  89   89   88    -1   1 0.00    .    831    -6 yes .
ATPMATCH-26JUN29SWEDIM-DIM             77   77  78   78   78    -1   1 0.00    .   1245     1 yes .
ATPCHALLENGERMATCH-26JUN30CREWAL-CRE   75   75  77   76   76    -1   2 0.00    .   7724   -79 no  K
WTAMATCH-26JUN29MERSIE-MER             75   75  76   76   76    -1   1 0.00    .    704   -31 yes .
ATPMATCH-26JUN29WAWBER-BER             80   80  81   81   80    -1   1 0.00    .    665   -12 yes .
WTAMATCH-26JUN29PODKOS-KOS             97   97  98   98   98    -1   1 0.00    .  17418   -32 yes .
ITFMATCH-26JUN27KRUMAR-KRU             80  (no tick recorder)                              res=yes
ITFWMATCH-26JUN27SUBLAZ-SUB            76  (no tick recorder)                              res=yes
ITFMATCH-26JUN27RATPET-RAT             81  (no tick recorder)                              res=yes
ITFWMATCH-26JUN27CHAAKL-AKL            79  (no tick recorder)                              res=yes
ATPCHALLENGERMATCH-26JUN28SANBER-SAN   88  (no tick recorder)                              res=yes
ATPCHALLENGERMATCH-26JUN28BILERH-ERH   76  (no tick recorder)                              res=yes
ATPCHALLENGERMATCH-26JUN28FOMJEC-FOM   89   89  90   91   90    -2   1 0.00    .   6463     0 yes .
ATPCHALLENGERMATCH-26JUN28ROCSEG-ROC   93   93  94   95   94    -2   1 0.00    .   6896     0 yes .
ATPCHALLENGERMATCH-26JUN28KARTRO-TRO   75   75  76   77   76    -2   1 0.00    .  32918   -33 yes .
WTAMATCH-26JUN30TOMBOL-TOM             86   86  87   88   86    -2   1 0.00    .   1358    -1 no  K
ATPCHALLENGERMATCH-26JUN28SINYEV-YEV   91  (no tick recorder)                              res=yes
ITFMATCH-26JUN28PICPAS-PAS             77  (no tick recorder)                              res=yes
ATPCHALLENGERMATCH-26JUN28LANES-NES    78   78  80   81   79    -3   2 0.00    .   2589     0 yes .
WTAMATCH-26JUN29BENSTO-BEN             88   90  91   91   90    -3   1 -2.00    .   1201   -34 yes .
ITFMATCH-26JUN29TANNAK-TAN             88   88  91   91   90    -3   3 0.00    .   3621   -28 yes .
WTAMATCH-26JUN29DAYKEY-KEY             91   92  93   94   92    -3   1 -1.00    .     79   -21 yes .
ITFMATCH-26JUN29HOSSIN-HOS             90   90  94   94   92    -4   4 0.00    .   5597   -53 yes .
ATPMATCH-26JUN29TRUDAM-DAM             77   79  80   81   80    -4   1 -2.00    .    376   -55 yes .
ITFMATCH-26JUN29GARCAR-GAR             78   78  83   84   80    -6   5 0.00    .   1246     0 yes .
ITFWMATCH-26JUN29HEDBOW-BOW            82   82  85   95   84   -13   3 0.00    .  13353   -57 yes .
```