# OMQS — ERROR LEDGER, CURRENT DEPLOY BOX (entry-side only) — 2026-07-02

**Box:** Jun 30 15:46 ET bisect (`2b23b5d`) → now, full slate. **122 graded positions** (posted/filled). Read-only. **Exits are OUT OF SCOPE (Vault §0A standing order)** — this ledger grades ENTRIES only.

**Scope:** 548 raw Kalshi tennis ticker-events in the box → **122 were actual POSITIONS** (we posted/filled ≥1 leg, graded below). Separately, **82 events were schedule_gap-skipped** (never resolved by ESPN/Odds), of which **57 were book-bearing** (substantial tape) — the never-touched slate. Book-bearing schedule_gap-skips by category: **ITF_W** 33, **ITF_M** 18, **ATP_CHALL** 6. Their achievable-combined census is **ITEM 3's remit** (C-KALSHI-OCC).

**Grade rubric:** A = both filled + combined ≤97 + at/near fillable · B = both + <100 · C = both but ≥100 (locked loss) · D = one-sided · F = missed-both/skipped. **Timing:** each leg `post`/`fill` as T-minus vs **sched**uled start (suffix `s`, e.g. `-4h23ms` = T-4h23m before sched) and **t**rue tape onset (suffix `t`; `n/at` = onset undetected). **best-fillable** = lowest last_trade that printed with size≥5.

> **⚠ In-flight caveat:** the box runs to *now*, so the `26JUL02`(+) tail includes matches **not yet started** — a `NO-FILL` / grade-F there may be "not filled **yet**," not a final miss, and best-fillable is computed on a still-open tape. Read the settled-date events (`26JUN30`/`26JUL01`) as final; treat the newest-date rows as provisional.

## Global grade distribution
| A | B | C | D | F | total |
|--:|--:|--:|--:|--:|--:|
| 2 | 25 | 31 | 38 | 26 | 122 |

## Global error × dollar (primary error CLASS per game, dollar = forfeited lock / overpay / locked-loss)
| primary error | count | $ damage |
|---|--:|--:|
| posted-over-fillable | 52 | $37.40 |
| posted-late/over-fillable | 20 | $30.00 |
| pulled-by-t20m | 12 | $12.15 |
| blocked-by-volume-floor | 4 | $5.70 |
| pulled-by-match-live | 4 | $1.05 |
| — | 18 | $0.90 |
| target-vs-tape misaligned | 8 | $0.75 |
| never-laid | 1 | $0.20 |
| combined>=100 (locked loss) | 1 | $0.00 |
| clean | 2 | $0.00 |
| **TOTAL** | **122** | **$88.15** |

## ATP_MAIN
**24 events** — grades: A:0 · B:1 · C:7 · D:9 · F:7 · **$ damage $16.80**

| grade | event | timing (T-minus: s=sched, t=tape onset) | combined | named error | forfeited / overpay | $ |
|:--:|---|---|:--:|---|---|--:|
| F | 26JUL02SVAMAJ | fav:MAJ post -4h23ms/NO-FILL  dog:SVA post -4h23ms/NO-FILL | — | posted-late/over-fillable +57c [MAJ]; posted-late/over-fillable +24c [SVA] | achievable combined 17 never captured | $4.15 |
| F | 26JUL02FERVIR | fav:VIR post -2h59ms/NO-FILL  dog:FER post -3h25ms/NO-FILL | — | pulled-by-t20m 05:41 (tape touched 42 at 06:52) [FER]; posted-late/over-fillable +7c [FER]; posted-late/over-fillable +56c [VIR] | achievable combined 37 never captured | $3.15 |
| D | 26JUL02DIASON | fav:DIA post -2h39ms/NO-FILL  dog:SON post -3h25ms/fill -54ms·-1h19mt @47 | — | posted-late/over-fillable +49c [DIA] | forfeited combined 51 (missed lock) | $2.45 |
| F | 26JUL02BERFAR | fav:BER post -3h58ms/NO-FILL  dog:FAR post -3h58ms/NO-FILL | — | posted-late/over-fillable +11c [BER]; posted-late/over-fillable +32c [FAR] | achievable combined 53 never captured | $2.35 |
| F | 26JUL02KHAHAN | fav:KHA post -6h39ms/NO-FILL  dog:HAN post -6h39ms/NO-FILL | — | posted-late/over-fillable +38c [HAN] | achievable combined 61 never captured | $1.95 |
| B | 26JUL02LEHMOL | fav:LEH post -5h49ms/fill -3h52ms·-4h37mt @81  dog:MOL post -6h24ms/fill -3h59ms·-4h44mt @18 | **99** | posted +17c over fillable [MOL] | combined 99 (>97), overpay 19c | $0.95 |
| F | 26JUL01MEJZHE | fav:ZHE post -3h44ms/NO-FILL  dog:MEJ post -3h59ms/NO-FILL | — | posted-late/over-fillable +5c [ZHE] | achievable combined 94 never captured | $0.30 |
| D | 26JUL02DEMAN | fav:DE post -2h39ms/NO-FILL  dog:MAN post -3h25ms/fill -59ms·n/at @15 | — | posted-late/over-fillable +6c [DE] | forfeited combined 94 (missed lock) | $0.30 |
| F | 26JUL01BROBUS | fav:BRO post -3h49ms/NO-FILL  dog:BUS post -3h01ms/NO-FILL | — | posted-late/over-fillable +4c [BRO] | achievable combined 95 never captured | $0.25 |
| D | 26JUL02FRIKYP | fav:FRI post -3h25ms/fill -3h19ms·-4h26mt @94  dog:KYP post -3h59ms/NO-FILL | — | pulled-by-match-live 06:12 (tape touched 7 at 06:12) [KYP]; posted-late/over-fillable +6c [KYP] | forfeited combined 95 (missed lock) | $0.25 |
| F | 26JUL01DAVMAR | fav:DAV post -3h59ms/NO-FILL  dog:MAR post -3h59ms/NO-FILL | — | target-vs-tape misaligned 1c too deep [DAV]; posted-late/over-fillable +4c [MAR] | achievable combined 96 never captured | $0.20 |
| D | 26JUL02ROYZVE | fav:ZVE post -4h07ms/fill +7ms·-45mt @95  dog:ROY post -4h24ms/NO-FILL | — | pulled-by-match-live 10:07 (tape touched 4 at 10:16) [ROY]; posted-late/over-fillable +3c [ROY] | forfeited combined 96 (missed lock) | $0.20 |
| D | 26JUL01KWONPAU | fav:PAU post -3h49ms/NO-FILL  dog:KWON post -3h59ms/fill -2h23ms·n/at @12 | — | — | forfeited combined 98 (missed lock) | $0.10 |
| D | 26JUL01HUROFN | fav:HUR post -3h59ms/NO-FILL  dog:OFN post -3h59ms/fill -2h03ms·n/at @25 | — | — | forfeited combined 98 (missed lock) | $0.10 |
| C | 26JUL02DUCCOB | fav:COB post -4h39ms/fill -2h32ms·-3h27mt @71  dog:DUC post -4h39ms/fill -26ms·-1h21mt @30 | **101**⚠≥100 | posted +9c over fillable [COB]; posted +29c over fillable [DUC]; combined 101 >=100 (locked loss) | locked LOSS +1c (combined 101) | $0.05 |
| C | 26JUL02BERFIL | fav:FIL post -3h53ms/fill -2h13ms·-2h55mt @66  dog:BER post -3h59ms/fill -26ms·-1h08mt @35 | **101**⚠≥100 | posted +7c over fillable [BER]; posted +46c over fillable [FIL]; combined 101 >=100 (locked loss) | locked LOSS +1c (combined 101) | $0.05 |
| D | 26JUN29WAWBER | dog:WAW post n/as/fill +3h46ms·+2h24mt @20 | — | — | one-sided; missed leg unfillable/no book | $0.00 |
| D | 26JUL01FUCTIE | fav:TIE post -3h59ms/fill -2h50ms·n/at @74  dog:FUC post -3h59ms/NO-FILL | — | — | forfeited combined 101 (missed lock) | $0.00 |
| D | 26JUL01SAFVAN | fav:SAF post -3h44ms/NO-FILL  dog:VAN post -3h44ms/fill -3h33ms·n/at @45 | — | — | forfeited combined 100 (missed lock) | $0.00 |
| C | 26JUL02HALGIR | fav:GIR post -2h53ms/fill +12ms·-20mt @53  dog:HAL post -3h58ms/fill +13ms·-19mt @47 | **100**⚠≥100 | posted +12c over fillable [GIR]; posted +46c over fillable [HAL]; combined 100 >=100 (locked loss) | locked LOSS +0c (combined 100) | $0.00 |
| C | 26JUL02TIACHO | fav:TIA post -6h13ms/fill -3h51ms·-4h13mt @86  dog:CHO post -6h49ms/fill -1h26ms·-1h48mt @14 | **100**⚠≥100 | posted +33c over fillable [TIA]; combined 100 >=100 (locked loss) | locked LOSS +0c (combined 100) | $0.00 |
| C | 26JUL02FEAMUN | fav:MUN post -3h43ms/fill -1h53ms·-2h10mt @57  dog:FEA post -3h43ms/fill -2h27ms·-2h44mt @43 | **100**⚠≥100 | posted +37c over fillable [FEA]; posted +9c over fillable [MUN]; combined 100 >=100 (locked loss) | locked LOSS +0c (combined 100) | $0.00 |
| C | 26JUL02MENDIM | fav:MEN post -4h33ms/fill -3h35ms·-4h08mt @61  dog:DIM post -4h33ms/fill -2h34ms·-3h07mt @39 | **100**⚠≥100 | posted +17c over fillable [DIM]; posted +60c over fillable [MEN]; combined 100 >=100 (locked loss) | locked LOSS +0c (combined 100) | $0.00 |
| C | 26JUL02JACBUB | fav:BUB post -4h09ms/fill -3h53ms·-4h40mt @78  dog:JAC post -4h09ms/fill -2h45ms·-3h32mt @22 | **100**⚠≥100 | posted +4c over fillable [BUB]; posted +14c over fillable [JAC]; combined 100 >=100 (locked loss) | locked LOSS +0c (combined 100) | $0.00 |

**ATP_MAIN error × dollar:**
| primary error | count | $ |
|---|--:|--:|
| posted-late/over-fillable | 7 | $11.75 |
| pulled-by-t20m | 1 | $3.15 |
| posted-over-fillable | 8 | $1.05 |
| pulled-by-match-live | 2 | $0.45 |
| — | 5 | $0.20 |
| target-vs-tape misaligned | 1 | $0.20 |

## WTA_MAIN
**23 events** — grades: A:0 · B:0 · C:8 · D:5 · F:10 · **$ damage $13.10**

| grade | event | timing (T-minus: s=sched, t=tape onset) | combined | named error | forfeited / overpay | $ |
|:--:|---|---|:--:|---|---|--:|
| D | 26JUL02SHNSAM | fav:SHN post -2h39ms/NO-FILL  dog:SAM post -3h25ms/fill -35ms·-43mt @42 | — | posted-late/over-fillable +56c [SHN] | forfeited combined 43 (missed lock) | $2.85 |
| F | 26JUL02EALJOI | fav:EAL post -3h59ms/NO-FILL  dog:JOI post -3h59ms/NO-FILL | — | posted-late/over-fillable +32c [EAL]; posted-late/over-fillable +20c [JOI] | achievable combined 47 never captured | $2.65 |
| F | 26JUL02BLIKOS | fav:KOS post -5h19ms/NO-FILL  dog:BLI post -5h19ms/NO-FILL | — | posted-late/over-fillable +13c [BLI]; posted-late/over-fillable +39c [KOS] | achievable combined 47 never captured | $2.65 |
| F | 26JUL02BOLKRU | fav:KRU post -4h18ms/NO-FILL  dog:BOL post -4h18ms/NO-FILL | — | posted-late/over-fillable +13c [BOL]; posted-late/over-fillable +11c [KRU] | achievable combined 74 never captured | $1.30 |
| F | 26JUL02PLISWI | fav:SWI post -3h59ms/NO-FILL  dog:PLI post -3h59ms/NO-FILL | — | posted-late/over-fillable +21c [PLI] | achievable combined 77 never captured | $1.15 |
| D | 26JUL02SNIJEA | fav:SNI post -3h25ms/fill +10ms·-24mt @82  dog:JEA post -2h59ms/NO-FILL | — | posted-late/over-fillable +15c [JEA] | forfeited combined 85 (missed lock) | $0.75 |
| D | 26JUL02NAVSEL | fav:NAV post -3h25ms/fill -59ms·-1h19mt @83  dog:SEL post -3h25ms/NO-FILL | — | pulled-by-match-live 06:10 (tape touched 18 at 06:13) [SEL]; posted-late/over-fillable +12c [SEL] | forfeited combined 89 (missed lock) | $0.55 |
| F | 26JUL02SWAKEY | fav:KEY post -3h59ms/NO-FILL  dog:SWA post -3h59ms/NO-FILL | — | posted-late/over-fillable +8c [SWA] | achievable combined 91 never captured | $0.45 |
| F | 26JUL01GASOSA | fav:OSA post -3h49ms/NO-FILL  dog:GAS post -3h59ms/NO-FILL | — | — | achievable combined 98 never captured | $0.10 |
| F | 26JUL01SONLIU | fav:SON post -3h44ms/NO-FILL  dog:LIU post -3h44ms/NO-FILL | — | — | achievable combined 98 never captured | $0.10 |
| C | 26JUL02GRABOU | fav:BOU post -3h25ms/fill -55ms·n/at @75  dog:GRA post -3h59ms/fill -3h09ms·n/at @27 | **102**⚠≥100 | posted +18c over fillable [BOU]; posted +21c over fillable [GRA]; combined 102 >=100 (locked loss) | locked LOSS +2c (combined 102) | $0.10 |
| D | 26JUL02MERTIM | fav:MER post -5h53ms/fill -1h22ms·-1h44mt @80  dog:TIM post -5h53ms/NO-FILL | — | pulled-by-t20m 09:40 (tape touched 22 at 09:40) [TIM]; posted-late/over-fillable +4c [TIM] | forfeited combined 98 (missed lock) | $0.10 |
| C | 26JUL02CIRBIR | fav:CIR post -5h18ms/fill -5h11ms·-6h18mt @69  dog:BIR post -5h34ms/fill -3h07ms·-4h14mt @33 | **102**⚠≥100 | posted +29c over fillable [BIR]; posted +4c over fillable [CIR]; combined 102 >=100 (locked loss) | locked LOSS +2c (combined 102) | $0.10 |
| F | 26JUL01OSTRUZ | fav:OST post -3h49ms/NO-FILL  dog:RUZ post -3h49ms/NO-FILL | — | — | achievable combined 99 never captured | $0.05 |
| D | 26JUL01PARSAW | fav:PAR post -3h49ms/fill -2h49ms·n/at @58  dog:SAW post -3h49ms/NO-FILL | — | — | forfeited combined 99 (missed lock) | $0.05 |
| C | 26JUL02ANIKEN | fav:ANI post -3h53ms/fill -2h16ms·-3h12mt @86  dog:KEN post -4h29ms/fill -1h06ms·-2h02mt @15 | **101**⚠≥100 | posted +54c over fillable [ANI]; posted +12c over fillable [KEN]; combined 101 >=100 (locked loss) | locked LOSS +1c (combined 101) | $0.05 |
| C | 26JUL02RAKSAK | fav:SAK post -4h40ms/fill -1h39ms·-2h30mt @63  dog:RAK post -4h13ms/fill -59ms·-1h50mt @38 | **101**⚠≥100 | posted +37c over fillable [RAK]; posted +51c over fillable [SAK]; combined 101 >=100 (locked loss) | locked LOSS +1c (combined 101) | $0.05 |
| C | 26JUL02PAOGOL | fav:PAO post -5h28ms/fill -4h57ms·-4h59mt @56  dog:GOL post -5h28ms/fill -2h17ms·-2h19mt @45 | **101**⚠≥100 | posted +18c over fillable [GOL]; posted +14c over fillable [PAO]; combined 101 >=100 (locked loss) | locked LOSS +1c (combined 101) | $0.05 |
| C | 26JUL01TJEKAS | fav:KAS post -3h49ms/fill -3h09ms·n/at @52  dog:TJE post -3h49ms/fill -3h45ms·n/at @48 | **100**⚠≥100 | combined 100 >=100 (locked loss) | locked LOSS +0c (combined 100) | $0.00 |
| F | 26JUL01MUCZHA | dog:ZHA post -3h59ms/NO-FILL | — | target-vs-tape misaligned 1c too deep [ZHA] | missed-both / skipped; no book | $0.00 |
| F | 26JUL01SABKES | dog:KES post -3h59ms/NO-FILL | — | — | missed-both / skipped; no book | $0.00 |
| C | 26JUL02OSONOS | fav:NOS post -5h43ms/fill -57ms·-2h01mt @79  dog:OSO post -5h45ms/fill -3h04ms·-4h08mt @21 | **100**⚠≥100 | posted +20c over fillable [OSO]; combined 100 >=100 (locked loss) | locked LOSS +0c (combined 100) | $0.00 |
| C | 26JUL02MCCRYB | fav:RYB post -3h59ms/fill -2h19ms·-3h29mt @80  dog:MCC post -3h59ms/fill -2h55ms·-4h05mt @20 | **100**⚠≥100 | posted +12c over fillable [MCC]; combined 100 >=100 (locked loss) | locked LOSS +0c (combined 100) | $0.00 |

**WTA_MAIN error × dollar:**
| primary error | count | $ |
|---|--:|--:|
| posted-late/over-fillable | 7 | $11.80 |
| pulled-by-match-live | 1 | $0.55 |
| posted-over-fillable | 7 | $0.35 |
| — | 5 | $0.30 |
| pulled-by-t20m | 1 | $0.10 |
| combined>=100 (locked loss) | 1 | $0.00 |
| target-vs-tape misaligned | 1 | $0.00 |

## ATP_CHALL
**37 events** — grades: A:0 · B:9 · C:12 · D:10 · F:6 · **$ damage $17.70**

| grade | event | timing (T-minus: s=sched, t=tape onset) | combined | named error | forfeited / overpay | $ |
|:--:|---|---|:--:|---|---|--:|
| B | 26JUL02PAVKUZ | fav:PAV post -3h25ms/fill -32ms·-47mt @58  dog:KUZ post -4h24ms/fill -21ms·-36mt @39 | **97**✓≤97 | posted +20c over fillable [KUZ]; posted +53c over fillable [PAV] | overpaid 73c vs fillable (comb 97) | $3.65 |
| B | 26JUL02SHISUR | fav:SUR post -3h59ms/fill +40ms·-6mt @54  dog:SHI post -3h59ms/fill -58ms·-1h45mt @43 | **97**✓≤97 | posted +15c over fillable [SHI]; posted +50c over fillable [SUR] | overpaid 65c vs fillable (comb 97) | $3.25 |
| F | 26JUL02COUVAS | fav:VAS post -5h23ms/NO-FILL  dog:COU post -5h23ms/NO-FILL | — | posted-late/over-fillable +54c [VAS] | achievable combined 36 never captured | $3.20 |
| B | 26JUL02HERRIB | fav:RIB post -3h59ms/fill +7ms·-55mt @81  dog:HER post -3h59ms/fill +8ms·-54mt @18 | **99** | posted +33c over fillable [RIB] | combined 99 (>97), overpay 33c | $1.65 |
| D | 26JUL02ABOMEL | fav:MEL post -3h59ms/fill +8ms·n/at @68  dog:ABO post -3h59ms/NO-FILL | — | pulled-by-t20m 10:40 (tape touched 31 at 10:40) [ABO]; posted-late/over-fillable +29c [ABO] | forfeited combined 70 (missed lock) | $1.50 |
| B | 26JUN30GOILIN | fav:GOI post -1h42ms/fill +44ms·-4mt @53  dog:LIN post -1h42ms/fill +45ms·-3mt @45 | **98** | posted +6c over fillable [GOI]; posted +13c over fillable [LIN] | combined 98 (>97), overpay 19c | $0.95 |
| B | 26JUN30ELLSEK | fav:SEK post -1h12ms/fill +49ms·-2h16mt @57  dog:ELL post -1h12ms/fill +1h18ms·-1h47mt @42 | **99** | posted +13c over fillable [ELL] | combined 99 (>97), overpay 15c | $0.75 |
| B | 26JUL02FELXIL | fav:FEL post -3h59ms/fill -2h20ms·n/at @85  dog:XIL post -3h59ms/fill -2h40ms·n/at @14 | **99** | posted +12c over fillable [XIL] | combined 99 (>97), overpay 12c | $0.60 |
| F | 26JUL02DIARAP | fav:DIA post -5h14ms/NO-FILL  dog:RAP post -5h14ms/NO-FILL | — | target-vs-tape misaligned 1c too deep [DIA]; posted-late/over-fillable +10c [RAP] | achievable combined 89 never captured | $0.55 |
| D | 26JUL01ELLBAR | fav:BAR post -3h59ms/NO-FILL  dog:ELL post -3h59ms/fill +11ms·n/at @35 | — | posted-late/over-fillable +4c [BAR] | forfeited combined 92 (missed lock) | $0.40 |
| B | 26JUL02GOIPAC | fav:PAC post -4h39ms/fill -3h18ms·n/at @91  dog:GOI post -4h39ms/fill -8ms·n/at @8 | **99** | posted +7c over fillable [GOI] | combined 99 (>97), overpay 8c | $0.40 |
| B | 26JUN30SURDRA | fav:DRA post -6h57ms/fill -42ms·-37mt @57  dog:SUR post -6h57ms/fill -3h10ms·-3h05mt @42 | **99** | — | combined 99 (>97), overpay 2c | $0.10 |
| D | 26JUL01KASSAN | fav:KAS post -3h52ms/NO-FILL  dog:SAN post -3h52ms/fill -2h24ms·n/at @42 | — | posted-late/over-fillable +4c [KAS] | forfeited combined 98 (missed lock) | $0.10 |
| F | 26JUL01KAOMOE | fav:MOE post -3h59ms/NO-FILL  dog:KAO post -3h59ms/NO-FILL | — | — | achievable combined 98 never captured | $0.10 |
| C | 26JUL02LAMON | fav:LA post -3h59ms/fill +12ms·-44mt @82  dog:MON post -3h59ms/fill -17ms·-1h14mt @20 | **102**⚠≥100 | posted +59c over fillable [LA]; posted +3c over fillable [MON]; combined 102 >=100 (locked loss) | locked LOSS +2c (combined 102) | $0.10 |
| D | 26JUN30BARFIC | fav:BAR post -5h22ms/NO-FILL  dog:FIC post -5h22ms/fill -3h00ms·-3h15mt @42 | — | pulled-by-match-live 21:17 (tape touched 58 at 21:25) [BAR] | forfeited combined 99 (missed lock) | $0.05 |
| C | 26JUN30SUNSHI | fav:SHI post -7h02ms/fill -2h47ms·-3h26mt @52  dog:SUN post -7h02ms/fill +0ms·-38mt @49 | **101**⚠≥100 | posted +3c over fillable [SHI]; posted +3c over fillable [SUN]; combined 101 >=100 (locked loss) | locked LOSS +1c (combined 101) | $0.05 |
| C | 26JUL01MIDGUE | fav:MID post -1h29ms/fill -45ms·n/at @59  dog:GUE post -3h59ms/fill -14ms·n/at @42 | **101**⚠≥100 | posted +5c over fillable [MID]; combined 101 >=100 (locked loss) | locked LOSS +1c (combined 101) | $0.05 |
| D | 26JUL01SMISQU | fav:SQU post -3h42ms/fill -1h56ms·n/at @71  dog:SMI post -3h31ms/NO-FILL | — | posted-late/over-fillable +3c [SMI] | forfeited combined 99 (missed lock) | $0.05 |
| F | 26JUL01PASDAL | fav:PAS post -3h41ms/NO-FILL  dog:DAL post -3h57ms/NO-FILL | — | posted-late/over-fillable +3c [DAL] | achievable combined 99 never captured | $0.05 |
| B | 26JUL02MOLBAS | fav:MOL post -2h59ms/fill +1h00ms·-21mt @69  dog:BAS post -3h58ms/fill -1h35ms·-2h57mt @29 | **98** | — | combined 98 (>97), overpay 1c | $0.05 |
| C | 26JUL02MARJOR | fav:JOR post -1h25ms/fill +1h00ms·+0mt @68  dog:MAR post -3h58ms/fill -3h19ms·-4h19mt @33 | **101**⚠≥100 | posted +59c over fillable [JOR]; combined 101 >=100 (locked loss) | locked LOSS +1c (combined 101) | $0.05 |
| C | 26JUL02CECBRA | fav:CEC post -2h13ms/fill -40ms·-1h30mt @57  dog:BRA post -2h44ms/fill +7ms·-42mt @44 | **101**⚠≥100 | posted +43c over fillable [BRA]; combined 101 >=100 (locked loss) | locked LOSS +1c (combined 101) | $0.05 |
| D | 26JUN30LAHER | dog:HER post n/as/fill +2h06ms·+44mt @27 | — | — | one-sided; missed leg unfillable/no book | $0.00 |
| C | 26JUN30MARRIB | fav:RIB post -1h12ms/fill -12ms·-7mt @86  dog:MAR post -1h12ms/fill -12ms·-7mt @14 | **100**⚠≥100 | posted +5c over fillable [MAR]; combined 100 >=100 (locked loss) | locked LOSS +0c (combined 100) | $0.00 |
| D | 26JUN30LEGBIC | dog:LEG post -1h12ms/fill +29ms·-3h07mt @46 | — | — | one-sided; missed leg unfillable/no book | $0.00 |
| D | 26JUN30SAKLER | fav:SAK post -1h12ms/fill +2h15ms·-2h20mt @91 | — | — | one-sided; missed leg unfillable/no book | $0.00 |
| C | 26JUL01NEDRON | fav:NED post -2h59ms/fill -2h01ms·n/at @66  dog:RON post -3h59ms/fill -2h14ms·n/at @34 | **100**⚠≥100 | posted +6c over fillable [RON]; combined 100 >=100 (locked loss) | locked LOSS +0c (combined 100) | $0.00 |
| D | 26JUL01GIUTOP | fav:TOP post -3h59ms/NO-FILL  dog:GIU post -2h19ms/fill -1h54ms·n/at @47 | — | target-vs-tape misaligned 1c too deep [TOP] | forfeited combined 101 (missed lock) | $0.00 |
| D | 26JUL01HEIBAR | fav:HEI post -3h36ms/NO-FILL  dog:BAR post -3h59ms/fill -6ms·n/at @20 | — | pulled-by-t20m 03:40 (tape touched 81 at 03:40) [HEI] | forfeited combined 100 (missed lock) | $0.00 |
| F | 26JUL01STAMAR | fav:MAR post -3h19ms/NO-FILL  dog:STA post -3h19ms/NO-FILL | — | target-vs-tape misaligned 3c too deep [STA] | achievable combined 101 never captured | $0.00 |
| F | 26JUL01RINERH | fav:RIN post -3h59ms/NO-FILL  dog:ERH post -3h59ms/NO-FILL | — | target-vs-tape misaligned 4c too deep [ERH]; posted-late/over-fillable +3c [RIN] | achievable combined 102 never captured | $0.00 |
| C | 26JUL02MILJUS | fav:JUS post -3h59ms/fill -2h41ms·-4h13mt @64  dog:MIL post -3h59ms/fill -42ms·-2h14mt @36 | **100**⚠≥100 | posted +15c over fillable [MIL]; combined 100 >=100 (locked loss) | locked LOSS +0c (combined 100) | $0.00 |
| C | 26JUL02CHAMON | fav:MON post -4h17ms/fill +9ms·n/at @82  dog:CHA post -4h29ms/fill -1h24ms·n/at @18 | **100**⚠≥100 | posted +11c over fillable [CHA]; posted +17c over fillable [MON]; combined 100 >=100 (locked loss) | locked LOSS +0c (combined 100) | $0.00 |
| C | 26JUL02PALPIR | fav:PIR post -5h43ms/fill -2h47ms·-4h21mt @85  dog:PAL post -5h43ms/fill -8ms·-1h42mt @15 | **100**⚠≥100 | posted +14c over fillable [PAL]; posted +16c over fillable [PIR]; combined 100 >=100 (locked loss) | locked LOSS +0c (combined 100) | $0.00 |
| C | 26JUL02SAKLEG | fav:SAK post -3h29ms/fill -1h00ms·-2h05mt @81  dog:LEG post -3h59ms/fill +11ms·-53mt @19 | **100**⚠≥100 | posted +79c over fillable [SAK]; combined 100 >=100 (locked loss) | locked LOSS +0c (combined 100) | $0.00 |
| C | 26JUL02CANHEM | fav:CAN post -3h28ms/fill +5ms·n/at @52  dog:HEM post -3h28ms/fill +5ms·n/at @48 | **100**⚠≥100 | posted +51c over fillable [CAN]; posted +8c over fillable [HEM]; combined 100 >=100 (locked loss) | locked LOSS +0c (combined 100) | $0.00 |

**ATP_CHALL error × dollar:**
| primary error | count | $ |
|---|--:|--:|
| posted-over-fillable | 19 | $11.55 |
| posted-late/over-fillable | 5 | $3.80 |
| pulled-by-t20m | 2 | $1.50 |
| target-vs-tape misaligned | 4 | $0.55 |
| — | 6 | $0.25 |
| pulled-by-match-live | 1 | $0.05 |

## WTA_CHALL
_no events in box._

## ITF_M  (exits borrow → **ATP_CHALL**)
**21 events** — grades: A:2 · B:8 · C:2 · D:8 · F:1 · **$ damage $18.55**

| grade | event | timing (T-minus: s=sched, t=tape onset) | combined | named error | forfeited / overpay | $ |
|:--:|---|---|:--:|---|---|--:|
| B | 26JUL02YILOZD | fav:YIL post -2h23ms/fill -2h19ms·-4h09mt @87  dog:OZD post -2h53ms/fill +1h31ms·-18mt @12 | **99** | posted +71c over fillable [YIL] | combined 99 (>97), overpay 71c | $3.55 |
| B | 26JUL01TOMFER | fav:FER post -1h29ms/fill +3h05ms·n/at @56  dog:TOM post -1h29ms/fill -11ms·n/at @42 | **98** | posted +18c over fillable [FER]; posted +40c over fillable [TOM] | combined 98 (>97), overpay 58c | $2.90 |
| B | 26JUL02HERGAR | dog:GAR post -2h08ms/fill +1h40ms·n/at @51  dog:HER post -1h57ms/fill +55ms·n/at @48 | **99** | posted +50c over fillable [GAR]; posted +6c over fillable [HER] | combined 99 (>97), overpay 56c | $2.80 |
| B | 26JUL01JONOCH | fav:JON post -1h56ms/fill +0ms·-1h19mt @83  dog:OCH post -2h20ms/fill +53ms·-26mt @16 | **99** | posted +49c over fillable [JON] | combined 99 (>97), overpay 49c | $2.45 |
| D | 26JUL01NASCHA | fav:CHA post -2h29ms/fill -50ms·-1h10mt @59  dog:NAS post -3h06ms/NO-FILL | — | pulled-by-t20m 21:41 (tape touched 41 at 21:41) [NAS]; posted-late/over-fillable +34c [NAS] | forfeited combined 66 (missed lock) | $1.70 |
| B | 26JUL02JASTAK | fav:JAS post -31ms/fill +38ms·-59mt @88  dog:TAK post -31ms/fill +3ms·-1h34mt @9 | **97**✓≤97 | posted +13c over fillable [JAS]; posted +8c over fillable [TAK] | overpaid 21c vs fillable (comb 97) | $1.05 |
| B | 26JUL01BOUHAR | fav:BOU post -2h59ms/fill -6ms·n/at @57  dog:HAR post -3h24ms/fill -57ms·n/at @41 | **98** | posted +13c over fillable [BOU]; posted +5c over fillable [HAR] | combined 98 (>97), overpay 18c | $0.90 |
| D | 26JUN30SHINIS | fav:SHI post -39ms/fill +10ms·-52mt @85  dog:NIS post -39ms/NO-FILL | — | pulled-by-t20m 22:40 (tape touched 15 at 22:41) [NIS]; posted-late/over-fillable +14c [NIS] | forfeited combined 86 (missed lock) | $0.70 |
| B | 26JUL01HUSWEI | fav:WEI post -1h59ms/fill -1h29ms·n/at @94  dog:HUS post -2h05ms/fill -1h30ms·n/at @4 | **98** | posted +9c over fillable [WEI] | combined 98 (>97), overpay 10c | $0.50 |
| F | 26JUL01LUONOR | fav:NOR post -6h18ms/NO-FILL  dog:LUO post n/as/NO-FILL | — | blocked-by-volume-floor x126 (never posted) [LUO]; target-vs-tape misaligned 1c too deep [NOR] | achievable combined 92 never captured | $0.40 |
| D | 26JUL01TOMCHE | fav:TOM post -5h20ms/fill -4h52ms·n/at @67  dog:CHE post n/as/NO-FILL | — | blocked-by-volume-floor x63 (never posted) [CHE] | forfeited combined 92 (missed lock) | $0.40 |
| B | 26JUL01JASSUZ | fav:JAS post -2h02ms/fill -24ms·n/at @91  dog:SUZ post -2h32ms/fill -1h26ms·n/at @8 | **99** | posted +5c over fillable [JAS]; posted +3c over fillable [SUZ] | combined 99 (>97), overpay 8c | $0.40 |
| C | 26JUL01TSIFUN | fav:FUN post -25ms/fill +2h42ms·n/at @98  dog:TSI post -3h44ms/fill -2h48ms·n/at @10 | **108**⚠≥100 | posted +18c over fillable [FUN]; posted +9c over fillable [TSI]; combined 108 >=100 (locked loss) | locked LOSS +8c (combined 108) | $0.40 |
| D | 26JUL02SHIIMA | dog:IMA post -31ms/fill +38ms·-27mt @42  dog:SHI post n/as/NO-FILL | — | never-laid [SHI] | forfeited combined 96 (missed lock) | $0.20 |
| D | 26JUL01RYAKOU | fav:KOU post -4h03ms/NO-FILL  dog:RYA post -3h49ms/fill +22ms·n/at @41 | — | pulled-by-t20m 02:41 (tape touched 59 at 07:48) [KOU] | forfeited combined 98 (missed lock) | $0.10 |
| D | 26JUL01VOLWIS | fav:WIS post -1h54ms/NO-FILL  dog:VOL post -1h54ms/fill -1h05ms·n/at @8 | — | — | forfeited combined 99 (missed lock) | $0.05 |
| C | 26JUL01MARDEL | fav:MAR post -3h38ms/fill -1h55ms·-5h14mt @54  dog:DEL post -2h29ms/fill +44ms·-2h34mt @47 | **101**⚠≥100 | posted +4c over fillable [DEL]; posted +47c over fillable [MAR]; combined 101 >=100 (locked loss) | locked LOSS +1c (combined 101) | $0.05 |
| D | 26JUL01BARSAK | fav:BAR post -1h29ms/fill +7ms·n/at @52  dog:SAK post -1h03ms/NO-FILL | — | target-vs-tape misaligned 2c too deep [SAK] | forfeited combined 100 (missed lock) | $0.00 |
| D | 26JUL01HOMDAG | fav:DAG post -1h13ms/fill +5ms·n/at @52  dog:HOM post -1h13ms/NO-FILL | — | target-vs-tape misaligned 3c too deep [HOM] | forfeited combined 100 (missed lock) | $0.00 |
| A | 26JUL01DELTAK | fav:DEL post -1h15ms/fill +11ms·-17mt @67  dog:TAK post -1h15ms/fill -14ms·-43mt @30 | **97**✓≤97 | clean | clean lock 97 | $0.00 |
| A | 26JUL01OKIISO | dog:ISO post -3h59ms/fill -3h47ms·-4h41mt @51  dog:OKI post -3h39ms/fill +39ms·-14mt @44 | **95**✓≤97 | clean | clean lock 95 | $0.00 |

**ITF_M error × dollar:**
| primary error | count | $ |
|---|--:|--:|
| posted-over-fillable | 10 | $15.00 |
| pulled-by-t20m | 3 | $2.50 |
| blocked-by-volume-floor | 2 | $0.80 |
| never-laid | 1 | $0.20 |
| — | 1 | $0.05 |
| target-vs-tape misaligned | 2 | $0.00 |
| clean | 2 | $0.00 |

## ITF_W  (exits borrow → **WTA_CHALL**)
**17 events** — grades: A:0 · B:7 · C:2 · D:6 · F:2 · **$ damage $22.00**

| grade | event | timing (T-minus: s=sched, t=tape onset) | combined | named error | forfeited / overpay | $ |
|:--:|---|---|:--:|---|---|--:|
| F | 26JUL02ZELSLA | fav:ZEL post -3h25ms/NO-FILL  dog:SLA post -3h59ms/NO-FILL | — | pulled-by-t20m 04:11 (tape touched 11 at 05:56) [SLA]; posted-late/over-fillable +6c [SLA]; pulled-by-t20m 04:11 (tape touched 87 at 05:58) [ZEL]; posted-late/over-fillable +66c [ZEL] | achievable combined 26 never captured | $3.70 |
| B | 26JUL02KOVPOC | fav:POC post -1h44ms/fill +2h11ms·-1h26mt @58  dog:KOV post -2h54ms/fill +2h09ms·-1h27mt @41 | **99** | posted +12c over fillable [KOV]; posted +47c over fillable [POC] | combined 99 (>97), overpay 59c | $2.95 |
| F | 26JUL02EVABRE | fav:EVA post -28ms/NO-FILL  dog:BRE post -28ms/NO-FILL | — | posted-late/over-fillable +8c [BRE]; posted-late/over-fillable +40c [EVA] | achievable combined 47 never captured | $2.65 |
| D | 26JUL01COLCHA | dog:COL post -3h59ms/fill -2h53ms·n/at @45  dog:CHA post n/as/NO-FILL | — | blocked-by-volume-floor x79 (never posted) [CHA] | forfeited combined 50 (missed lock) | $2.50 |
| B | 26JUL02STAIVA | fav:IVA post -2h53ms/fill -2h50ms·-5h50mt @61  dog:STA post -3h24ms/fill -3h03ms·-6h03mt @19 | **80**✓≤97 | posted +50c over fillable [IVA] | overpaid 50c vs fillable (comb 80) | $2.50 |
| D | 26JUL01GARLOP | dog:LOP post -3h59ms/fill -2h58ms·n/at @42  dog:GAR post n/as/NO-FILL | — | blocked-by-volume-floor x123 (never posted) [GAR] | forfeited combined 52 (missed lock) | $2.40 |
| B | 26JUL01VANVER | fav:VER post -3h22ms/fill +26ms·n/at @53  dog:VAN post -3h22ms/fill +22ms·n/at @46 | **99** | posted +17c over fillable [VAN]; posted +15c over fillable [VER] | combined 99 (>97), overpay 32c | $1.60 |
| B | 26JUN30WANCHO | fav:WAN post -1h21ms/fill -1h21ms·-4h14mt @86  dog:CHO post -1h21ms/fill +2h19ms·-33mt @13 | **99** | posted +12c over fillable [CHO]; posted +14c over fillable [WAN] | combined 99 (>97), overpay 26c | $1.30 |
| D | 26JUN30AHNYUA | fav:YUA post -42ms/fill -4ms·-31mt @79  dog:AHN post -42ms/NO-FILL | — | pulled-by-t20m 23:11 (tape touched 20 at 23:42) [AHN]; posted-late/over-fillable +19c [AHN] | forfeited combined 80 (missed lock) | $1.00 |
| B | 26JUL02MIHNAG | fav:NAG post -2h14ms/fill -1h50ms·n/at @85  dog:MIH post -2h53ms/fill +2h00ms·n/at @14 | **99** | posted +9c over fillable [MIH]; posted +3c over fillable [NAG] | combined 99 (>97), overpay 12c | $0.60 |
| B | 26JUN30DESGUO | fav:GUO post -43ms/fill -22ms·-1h53mt @83  dog:DES post -43ms/fill +1h24ms·-6mt @15 | **98** | posted +3c over fillable [DES]; posted +7c over fillable [GUO] | combined 98 (>97), overpay 10c | $0.50 |
| D | 26JUL01YAMSNI | fav:YAM post -59ms/NO-FILL  dog:SNI post -1h04ms/fill -0ms·-38mt @41 | — | pulled-by-t20m 21:41 (tape touched 57 at 21:43) [YAM] | forfeited combined 97 (missed lock) | $0.15 |
| B | 26JUL02YAMKOI | fav:KOI post -5h44ms/fill -4h27ms·n/at @54  dog:YAM post -5h44ms/fill -4h07ms·n/at @45 | **99** | — | combined 99 (>97), overpay 2c | $0.10 |
| D | 26JUL02CEMDRU | fav:CEM post -2h04ms/fill -0ms·n/at @59  dog:DRU post -2h04ms/NO-FILL | — | pulled-by-t20m 02:41 (tape touched 41 at 02:41) [DRU] | forfeited combined 99 (missed lock) | $0.05 |
| C | 26JUL01KALMUN | fav:MUN post -3h34ms/fill -5ms·n/at @92  dog:KAL post -3h59ms/fill -2h23ms·n/at @8 | **100**⚠≥100 | posted +9c over fillable [MUN]; combined 100 >=100 (locked loss) | locked LOSS +0c (combined 100) | $0.00 |
| D | 26JUL01HUIAHN | fav:AHN post -59ms/fill -20ms·-1h52mt @73  dog:HUI post -1h09ms/NO-FILL | — | pulled-by-t20m 16:10 (tape touched 31 at 16:10) [HUI] | forfeited combined 102 (missed lock) | $0.00 |
| C | 26JUL02BOJKOV | dog:KOV post -2h24ms/fill -52ms·-4h20mt @55  dog:BOJ post -2h54ms/fill +2h01ms·-1h26mt @45 | **100**⚠≥100 | posted +30c over fillable [BOJ]; posted +52c over fillable [KOV]; combined 100 >=100 (locked loss) | locked LOSS +0c (combined 100) | $0.00 |

**ITF_W error × dollar:**
| primary error | count | $ |
|---|--:|--:|
| posted-over-fillable | 8 | $9.45 |
| pulled-by-t20m | 5 | $4.90 |
| blocked-by-volume-floor | 2 | $4.90 |
| posted-late/over-fillable | 1 | $2.65 |
| — | 1 | $0.10 |
