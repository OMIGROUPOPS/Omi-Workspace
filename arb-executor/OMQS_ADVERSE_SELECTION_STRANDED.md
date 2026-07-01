# OMQS — ADVERSE-SELECTION test on the 93 stranded-single events (Jun 24-30)

Do we KEEP the bad-priced (low-cash-rate) leg and STRAND the good-priced (high-cash-rate) leg? Anchor = MIDPOINT (bid_1+ask_1)/2 at the KEPT-leg fill instant, from the enriched tick recorder. fill_minus_mid = leg price - mid (+ = at/above mid = worse; - = below mid = better/more room to band). 93 stranded singles (57 queue-starve + 36 gun-cancel) from OMQS_COMPLETION_FUNNEL. Midpoint coverage: 74/186 legs (older dates thin in the recorder); the 65% kept-loss is on all 92 settled. Read-only.

## Price quality — KEPT (filled) vs MISSED (stranded) leg
| leg | n (mid-covered) | median vs mid | mean vs mid | share above/below mid |
|---|--:|--:|--:|--:|
| KEPT (filled) | 37 | -0.5 | -1.0 | above-mid 8% |
| MISSED (stranded) | 33 | -1.5 | -1.7 | below-mid 94% |

The stranded leg was the BETTER-priced side (median −1.5 below mid, 94% below mid = patient / more band room); the leg we kept was worse-priced (median −0.5, near the mid).

## Paired comparison (events where both legs mid-covered, n=33)
- mean(kept_fmm − missed_bmm) = **+0.6**, median +1.0.
- **KEPT leg was the WORSE-priced side in 23/33 = 70% of events.**

## Outcome — the KEPT leg is a systematic LOSER
- **kept-leg loss rate = 60/92 = 65%** (the leg we filled settled a loser two-thirds of the time).
- kept over-mid loss 67% (n=3) vs at/below-mid 71% (n=34) — loss rate is high regardless; the 1c price gap is a mild symptom, the 65% loss is the signal.

## VERDICT — order-flow adverse selection, confirmed
YES: we KEEP the worse-priced, losing side and STRAND the better-priced, winning side. The mechanism is deeper than a static price gap: **a taker only sells to our resting maker bid when they want OUT of that side = that side is WEAKENING = the eventual LOSER.** So the leg that gets HIT (kept) is the one the market is dumping (loses 65%); the leg that STARVES (missed) is the one the market is accumulating (the winner — no one sells it to our maker, so it sits behind the wall). The price signal confirms it (kept 70% worse-priced, missed 94% below mid), but the 65% kept-loss is the real tell.

**This decides the fix — it is NOT pure completion-mechanics via a maker bid.** A faster maker-completion would still starve on the winning leg (no one sells it to us) while continuing to fill the dumped loser. To complete, the winning leg must be TAKEN (cross the ask) — a maker bid on it is structurally starved. So the real options are: (i) CROSS to complete the winning sibling at the gun (take, not rest — pay the spread to lock the pair), or (ii) treat a maker fill as adversely-selected and NOT hold it naked (cancel/flatten the kept leg if the sibling cannot be completed). Fill-side-selection and completion-mechanics are the SAME problem: the maker only catches the loser.

## PER-EVENT ROWS (all 93; mid = "-" where recorder uncovered)
```
event                              cat        kept keptpx k_fmm  miss missbid m_bmm mode kept_out
ATPCHALLENGERMATCH-26JUN30BARFIC   ATP_CHALL  FIC   40    -0   BAR     58      -4  c   no
ATPCHALLENGERMATCH-26JUN30ALBPIR   ATP_CHALL  ALB   26    +1   PIR     72      -2  a   no
ATPCHALLENGERMATCH-26JUN28MILBAR   ATP_CHALL  MIL   44    -0   BAR     52      -4  c   no
ATPCHALLENGERMATCH-26JUN28KUMLAG   ATP_CHALL  KUM   65    -0   LAG     32      -4  a   no
ATPCHALLENGERMATCH-26JUN28PALMAS   ATP_CHALL  PAL   35    -0   MAS     63      -4  c   no
ATPMATCH-26JUN29KOPCHO             ATP_MAIN   KOP   59    -0   CHO     40      -3  c   no
ATPCHALLENGERMATCH-26JUN29RUBWEH   ATP_CHALL  RUB   37    +0   WEH     60      -2  c   no
ATPCHALLENGERMATCH-26JUN29LAGRIB   ATP_CHALL  RIB   42    -0   LAG     57      -2  a   no
ATPCHALLENGERMATCH-26JUN29FENIMA   ATP_CHALL  IMA   46    -1   FEN     51      -3  a   no
ATPCHALLENGERMATCH-26JUN30MATHEM   ATP_CHALL  MAT   39    -0   HEM     58      -2  a   no
ATPCHALLENGERMATCH-26JUN30CANALM   ATP_CHALL  ALM   28    +0   CAN     71      -1  a   no
WTAMATCH-26JUN29BOIRYB             WTA_MAIN   RYB   97    +0   BOI      2      -2  a   yes
ATPCHALLENGERMATCH-26JUN28RYBMOR   ATP_CHALL  MOR   48    +0   RYB     52      -1  a   yes
ATPCHALLENGERMATCH-26JUN30COMDON   ATP_CHALL  DON   18    +0   COM     82      -2  a   no
ATPCHALLENGERMATCH-26JUN28LANBAN   ATP_CHALL  LAN   47    +0   BAN     51      -2  a   no
ATPCHALLENGERMATCH-26JUN29CHALEC   ATP_CHALL  CHA   69    -0   LEC     29      -2  a   no
WTAMATCH-26JUN29SIEBON             WTA_MAIN   SIE   63    -0   BON     36      -2  a   yes
ATPCHALLENGERMATCH-26JUN28FENPOL   ATP_CHALL  FEN   65    -0   POL     34      -2  c   yes
ATPCHALLENGERMATCH-26JUN28VANIMA   ATP_CHALL  IMA   51    -0   VAN     48      -2  a   yes
ATPCHALLENGERMATCH-26JUN28ALBLAT   ATP_CHALL  LAT   25    -4   ALB     67      -6  a   no
ATPMATCH-26JUN30LLASVA             ATP_MAIN   LLA   29    +0   SVA     71      -0  a   no
ATPCHALLENGERMATCH-26JUN30DALTRA   ATP_CHALL  DAL   46    -0   TRA     52      -1  a   yes
ATPCHALLENGERMATCH-26JUN28MARALV   ATP_CHALL  ALV   17    -0   MAR     83      -1  a   no
ATPCHALLENGERMATCH-26JUN28WONGOI   ATP_CHALL  WON   16    -2   GOI     81      -2  a   no
ATPCHALLENGERMATCH-26JUN28PRIMAL   ATP_CHALL  PRI   79    -0   MAL     22      -0  c   no
ATPMATCH-26JUN29MULPAU             ATP_MAIN   MUL    4    -0   PAU     95      -0  a   no
ATPCHALLENGERMATCH-26JUN27VILSEY   ATP_CHALL  VIL   34    -0   SEY     67      -0  c   no
ATPMATCH-26JUN29MOCBAS             ATP_MAIN   BAS   32    -2   MOC     66      -1  a   no
ATPCHALLENGERMATCH-26JUN28URRZEB   ATP_CHALL  ZEB   72    -2   URR     27      -0  c   yes
ATPCHALLENGERMATCH-26JUN28SHIMAR   ATP_CHALL  SHI   79    -2   MAR     19      -0  c   yes
ATPCHALLENGERMATCH-26JUN28CAZWAL   ATP_CHALL  WAL   70    -1   CAZ     31      +1  a   yes
ATPCHALLENGERMATCH-26JUN30FELPIE   ATP_CHALL  PIE   22    -2   FEL     78      +4  a   no
ATPCHALLENGERMATCH-26JUN29DEDDAM   ATP_CHALL  DAM   34   -15   DED     66      -4  c   no
ATPCHALLENGERMATCH-26JUN25SOTVIL   ATP_CHALL  SOT   62     -   VIL     36       -  c   no
ATPCHALLENGERMATCH-26JUN28GULDAM   ATP_CHALL  DAM   14     -   GUL      4       -  a   no
WTAMATCH-26JUN24KUDNGO             WTA_MAIN   NGO   38     -   KUD     60       -  a   no
ATPCHALLENGERMATCH-26JUN28ZHUALM   ATP_CHALL  ZHU   13    -0   ALM     85       -  a   no
WTAMATCH-26JUN24GASJON             WTA_MAIN   GAS   29     -   JON     70       -  a   yes
WTAMATCH-26JUN26RUSMUC             WTA_MAIN   MUC   67     -   RUS     31       -  c   yes
ATPMATCH-26JUN24MEJHEI             ATP_MAIN   HEI   62     -   MEJ     36       -  a   no
ATPCHALLENGERMATCH-26JUN28FORTAB   ATP_CHALL  TAB   33    +0   FOR     64       -  c   yes
WTAMATCH-26JUN24SHYMIN             WTA_MAIN   SHY   15     -   MIN     84       -  a   yes
WTAMATCH-26JUN24ADETAN             WTA_MAIN   ADE   12     -   TAN     87       -  c   no
ATPCHALLENGERMATCH-26JUN28SVACUI   ATP_CHALL  SVA   62    -2   CUI     36       -  c   yes
WTAMATCH-26JUN24PROWAT             WTA_MAIN   PRO   53     -   WAT     46       -  a   no
WTAMATCH-26JUN24VOLYAN             WTA_MAIN   VOL   80     -   YAN     18       -  a   yes
ATPCHALLENGERMATCH-26JUN26ANDSEY   ATP_CHALL  SEY   74     -   AND     24       -  a   yes
ATPMATCH-26JUN24DIAETC             ATP_MAIN   DIA   61     -   ETC     35       -  c   yes
ATPMATCH-26JUN24RODLAJ             ATP_MAIN   ROD   65     -   LAJ     33       -  a   no
WTAMATCH-26JUN24ANDTEI             WTA_MAIN   TEI   36     -   AND     62       -  c   no
ATPMATCH-26JUN24ALTBER             ATP_MAIN   ALT   36     -   BER     62       -  c   no
WTAMATCH-26JUN29SABKOS             WTA_MAIN   KOS    4    -0   SAB     95       -  c   no
ATPMATCH-26JUN24TOMOCO             ATP_MAIN   TOM   32     -   OCO     66       -  a   no
ATPMATCH-26JUN23EVASCH             ATP_MAIN   SCH   61     -   EVA     37       -  a   yes
WTAMATCH-26JUN26MARKEY             WTA_MAIN   KEY   84     -   MAR     15       -  c   yes
ATPCHALLENGERMATCH-26JUN26BALNED   ATP_CHALL  NED   45     -   BAL     55       -  c   no
WTAMATCH-26JUN24WERCHA             WTA_MAIN   WER   12     -   CHA     86       -  c   no
ATPMATCH-26JUN24JUBBAR             ATP_MAIN   JUB   42     -   BAR     56       -  a   no
ATPMATCH-26JUN23FARPAV             ATP_MAIN   PAV   29     -   FAR     70       -  a   no
WTAMATCH-26JUN24VALTOM             WTA_MAIN   VAL   41     -   TOM     56       -  a   yes
WTAMATCH-26JUN24PRILAM             WTA_MAIN   LAM   55     -   PRI     43       -  a   no
WTAMATCH-26JUN24BOLKIN             WTA_MAIN   BOL   42     -   KIN     56       -  a   yes
WTAMATCH-26JUN24TIMPOD             WTA_MAIN   POD   38     -   TIM     60       -  c   no
ATPMATCH-26JUN24FERCER             ATP_MAIN   CER   31     -   FER     64       -  c   yes
WTAMATCH-26JUN24SEBNOH             WTA_MAIN   SEB   35     -   NOH     62       -  a   yes
ATPMATCH-26JUN24CORSAK             ATP_MAIN   COR   14     -   SAK     85       -  c   no
WTAMATCH-26JUN24KESKAL             WTA_MAIN   KAL   45     -   KES     55       -  a   no
ATPMATCH-26JUN24HUMBRO             ATP_MAIN   HUM   64     -   BRO     33       -  a   yes
ATPCHALLENGERMATCH-26JUN28SPEVAL   ATP_CHALL  SPE   70     -   VAL     28       -  c   no
ATPCHALLENGERMATCH-26JUN26KICSEY   ATP_CHALL  KIC   36     -   SEY     60       -  c   no
ATPMATCH-26JUN24HUSHAL             ATP_MAIN   HUS   39     -   HAL     59       -  a   no
ATPMATCH-26JUN24KYMHOL             ATP_MAIN   KYM   52     -   HOL     47       -  c   yes
ATPMATCH-26JUN23DJEZHE             ATP_MAIN   DJE   41     -   ZHE     57       -  a   no
WTAMATCH-26JUN24KRUHON             WTA_MAIN   HON   14     -   KRU     85       -  c   no
ATPMATCH-26JUN24BOYPEL             ATP_MAIN   PEL   34     -   BOY     64       -  c   no
WTAMATCH-26JUN24GARGRA             WTA_MAIN   GAR   43     -   GRA     55       -  a   no
ATPCHALLENGERMATCH-26JUN23KICFER   ATP_CHALL  KIC   78     -   FER     21       -  a   yes
ATPMATCH-26JUN24FRICHO             ATP_MAIN   FRI   85     -   CHO     16       -  a   scalar
ATPMATCH-26JUN23GUEJAC             ATP_MAIN   JAC   71     -   GUE     27       -  a   yes
WTAMATCH-26JUN24BOUKEY             WTA_MAIN   BOU   17     -   KEY     80       -  c   no
WTAMATCH-26JUN24GORJEA             WTA_MAIN   GOR   22     -   JEA     75       -  a   no
ATPMATCH-26JUN24SAMTIR             ATP_MAIN   TIR   41     -   SAM     57       -  c   no
WTAMATCH-26JUN24SWINAV             WTA_MAIN   SWI   74     -   NAV     22       -  c   no
ATPMATCH-26JUN24BASGEN             ATP_MAIN   GEN   64     -   BAS     33       -  a   no
ATPMATCH-26JUN25MEJSCH             ATP_MAIN   SCH   70     -   MEJ     25       -  a   no
ATPCHALLENGERMATCH-26JUN24MICSEL   ATP_CHALL  SEL   22     -   MIC     79       -  c   no
ATPCHALLENGERMATCH-26JUN24ERHMON   ATP_CHALL  MON   72     -   ERH     25       -  a   yes
WTAMATCH-26JUN24KAWSTE             WTA_MAIN   KAW   62     -   STE     35       -  a   yes
ATPMATCH-26JUN23WALDAV             ATP_MAIN   DAV   69     -   WAL     32       -  a   yes
WTAMATCH-26JUN24KORLAZ             WTA_MAIN   LAZ   31     -   KOR     67       -  a   no
WTAMATCH-26JUN24MARBIR             WTA_MAIN   MAR   32     -   BIR     67       -  a   yes
WTAMATCH-26JUN24SEMHIB             WTA_MAIN   SEM   51     -   HIB     48       -  c   yes
ATPMATCH-26JUN24MORMAY             ATP_MAIN   MAY   67     -   MOR     32       -  a   no
```