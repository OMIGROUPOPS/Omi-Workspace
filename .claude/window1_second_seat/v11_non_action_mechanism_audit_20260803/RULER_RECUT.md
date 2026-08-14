# THE RULER RE-CUT — actual bells, pre-bell floors, post-formation opens [ANALYTICAL_ESTIMATE]

Analysis seat only. Read-only over every score artifact. Full data: `RULER_RECUT.json` (bell table,
corrected 30-game table, receipts) · `ACTUAL_BELL_TABLE_804.{json,csv}` · `RULER_RECUT_LEGS.csv` (per-leg
re-cut, 1,608 rows). Review tape packs pushed separately @ `76f82dd8`.

## ① Actual-bell determination — all 804

Sources, ranked; every game carries its source and receipt:

1. **MACHINE_RECEIPT — 192 games.** The dev-804 ledger's own `t_minus_actual_bell` observation fields
   (@ `4716657a`); within-game spread of the derived epoch is zero on all 192.
2. **TAPE_SIGNATURE — 591 games.** The tape's in-play signature: **earliest sustained mirrored repricing
   regime** — joint ≥60 true prints in 30 min with each leg printing ≥10 times, traveling ≥3¢, and
   reversing direction ≥3 times, the regime sustaining ≥60 further prints over the following hour (refined
   to the first 5-minute burst ≥25). **Validated against the 192 machine-known bells: median error +1 min,
   89% within ±30 min** (14 detect >30 min early, 6 late, 3 undetected — the error model travels with every
   estimate).
3. **SETTLEMENT_NO_MATCH — 1 game.** DJECIN: Kalshi finalized `result=scalar` (match never began, per the
   settlement audit @ `3f4b0046`) — the detected burst is overridden by the settlement receipt; no bell.
4. **BELL_UNRESOLVED — 20 games.** No sustained regime in the tape (quiet or capture-ended); named in the
   CSV; left on the old ruler, flagged.

`observed_starts.db` is corroboration only (128 rows, Jul 14–29, `first_inplay_at` lags the bell by hours —
recorder discovery time — and leg-suffix keys collide); it never decides a bell.

**The headline: 142 of the 784 bell-resolved games have their actual bell >60 s BEFORE `w1_right` — the
recorded "pre-match" window's tail is in-play.** The 19 violent-collapse pairs (@ `3f4b0046`) lead the
order: **17 of 19 have bells 1.5–12 h before the window edge** (GUEGOM −10,740 s, KUMTUR −11,340 s,
BALHUA −7,860 s — just 580 s after its window *opened*, DODDEL −42,583 s, TABHUE −24,900 s; full 19 in the
JSON); DJECIN is the no-match override; every violent "collapse" so far walked is in-play tennis leaking
into a mis-set window.

## ② The pre-bell re-cut (per leg: floor · close · fill validity)

Effective pre-bell edge per leg = min(`w1_right`, actual bell). Across 1,536 scored legs: **69 legs' floors
vanish entirely** (no pre-bell print at any price at or below the old floor era — the old floor was wholly
in-play) and **85 legs' floors rise**; closes re-cut to the last strictly-pre-bell true print. Fill
validity: **93 credited fills across 63 games are POST-BELL** (fill after the resolved bell) — **44
completed pairs rest on ≥1 post-bell fill, carrying 178¢ of the exam's locked margin** (exemplars: DODDEL
16¢ · VILRAH 16¢ · RAFAGU 12¢; the collapse-class completes are the bulk). Unresolved-bell games' fills are
flagged `BELL_UNRESOLVED`, not judged.

## ③ Post-formation opens — the spread-settle rule (measured on DELXIL, as ordered)

Books open placeholder-wide (DELXIL: DEL 4/94, XIL 5/94 — spread ≈90¢) and collapse in a **single
repricing wave** (+153 s) to ≤6¢, never re-widening. **Rule used everywhere: post-formation open = the mid
of the first book row with spread ≤ 10¢ that holds ≤ 20¢ for the next 30 minutes** (DEL 82.0¢, XIL 17.5¢).
Never the onset-adapter price.

## ④ Census deltas vs `22441e05` + the corrected 30-game table

Print-grain pair floors (post-onset), old ruler: **612 games offered (≤99 joint) — exactly the frozen
census count @ `22441e05`**, margin pool 4,603¢. Re-cut strictly pre-bell: **offered 612 → 564 (−48
games); margin pool 4,603¢ → 2,258¢ (−2,345¢, −51%)**. 63 games' pair floor sums rise; 36 games become
unmeasurable pre-bell (a leg with no pre-bell prints). **Half the offer census's apparent money was
in-play money.**

Corrected 30-game table (V52i-cohort sample; per leg **open** = spread-settle · **floor** = pre-bell ·
**fill** = dev-804 V52e entry, `!PB` = post-bell fill · **last** = pre-bell close; `—` = does not exist
pre-bell; full table with epochs in the JSON):

| game | bell src | leg: open / floor(old) / fill / last | leg: open / floor(old) / fill / last |
|---|---|---|---|
| 26JUL12BALHUA | TAPE | BAL 20.0 / **—**(1) / 17`!PB` / — | HUA 82.5 / **—**(66) / 78`!PB` / — |
| 26JUL12DAHBAE | MACHINE | BAE 89.5 / 92(92) / 94 / 95 | DAH 9.0 / 4(4) / 4 / 6 |
| 26JUL12GUEGOM | TAPE | GOM 39.5 / **—**(42) / – / — | GUE 58.0 / **—**(1) / 58`!PB` / — |
| 26JUL12KUMTUR | TAPE | KUM 69.5 / **—**(69) / 72`!PB` / — | TUR 29.5 / **—**(1) / 20`!PB` / — |
| 26JUL12MORNEP | TAPE | MOR 71.0 / 71(70) / 71 / 78 | NEP 24.0 / **24**(1) / **24** / 24 |
| 26JUL12PANYOR | TAPE | PAN 82.0 / **—**(80) / 96`!PB` / — | YOR 18.0 / **—**(1) / 3`!PB` / — |
| 26JUL12POLKUH | MACHINE | KUH 21.0 / 15(15) / 18 / 20 | POL 79.0 / 80(80) / – / 85 |
| 26JUL12PRIBAL | TAPE | BAL 9.0 / **—**(1) / 1`!PB` / — | PRI 90.5 / **—**(98) / – / — |
| 26JUL13BLISAS | TAPE | BLI 43.5 / 42(42) / 43 / 43 | SAS 55.5 / 55(55) / – / 59 |
| 26JUL13JONSPI | TAPE | JON 48.5 / 89(89) / – / 89 | SPI 11.5 / 12(12) / – / 12 |
| 26JUL13SANDAN | MACHINE | DAN 63.0 / 75(75) / 77 / 76 | SAN 36.0 / 22(22) / – / 25 |
| 26JUL13VANLEE | TAPE | LEE 46.0 / 45(45) / – / 46 | VAN 54.0 / 55(55) / – / 57 |
| 26JUL14DELXIL | TAPE | DEL 82.0 / 83(83) / – / 84 | XIL 17.5 / 15(15) / 17 / 17 |
| 26JUL14PUTJEA | UNRESOLVED | JEA – / —(—) / – / — | PUT 50.0 / —(—) / – / — |
| 26JUL14SALIBR | TAPE | IBR 43.0 / 44(44) / – / 44 | SAL 57.0 / 56(56) / – / 57 |
| 26JUL14WOLVAN | MACHINE | VAN 78.0 / 79(79) / 79 / 80 | WOL 22.0 / 20(20) / 20 / 22 |
| 26JUL15PRIMOL | TAPE | MOL 29.0 / 28(28) / 29 / 28 | PRI 70.0 / 68(68) / 69 / 73 |
| 26JUL15ROMGAL | TAPE | GAL 67.0 / 67(66) / – / 67 | ROM 32.5 / 33(30) / – / 33 |
| 26JUL15TABMID | TAPE | MID 27.0 / 23(23) / 23 / 24 | TAB 73.0 / 74(74) / 76 / 76 |
| 26JUL15WESCOP | TAPE | COP 80.5 / 83(83) / – / 83 | WES 19.0 / 17(17) / – / 17 |
| 26JUL16MERDRO | MACHINE | DRO 49.0 / 39(39) / 49 / 40 | MER 54.0 / 48(48) / – / 61 |
| 26JUL17BURMER | TAPE | BUR 44.0 / 37(37) / 42 / 38 | MER 57.0 / 55(55) / 57 / 62 |
| 26JUL17HOLBOU | TAPE | BOU 34.0 / 33(33) / 33 / 34 | HOL 66.5 / 66(66) / 66 / 67 |
| 26JUL18BADZID | MACHINE | BAD 75.0 / 74(74) / 74 / 77 | ZID 28.0 / 23(23) / 25 / 24 |
| 26JUL18CASGEA | MACHINE | CAS 36.5 / 29(29) / – / 29 | GEA 63.0 / 65(65) / 69 / 72 |
| 26JUL19ARSMAR | MACHINE | ARS 34.0 / 35(35) / – / 40 | MAR 66.0 / 59(59) / 60 / 62 |
| 26JUL20ARSRIC | TAPE | ARS 36.0 / 36(36) / – / 36 | RIC 61.5 / 62(62) / – / 66 |
| 26JUL20KYMCLA | TAPE | CLA 24.5 / 23(23) / 24 / 24 | KYM 74.5 / 75(75) / – / 79 |
| 26JUL20QUEKAL | MACHINE | KAL 65.0 / 68(68) / 69 / 69 | QUE 35.0 / 30(30) / 30 / 32 |
| 26JUL20TROISO | TAPE | ISO 24.0 / 21(21) / 21 / 22 | TRO 76.0 / 77(77) / – / 79 |

The
re-read of the oracle map falls out directly: **the five fat shallow-win games' single-digit "floors" have
no pre-bell existence at all** — BALHUA, GUEGOM, KUMTUR, PANYOR, PRIBAL show `—` where the old ruler saw
1¢ — while **MORNEP survives re-cut intact** (NEP's true pre-bell floor is 24¢, and the V52e fill at 24¢
pre-bell sits exactly on it). Fills column is the dev-804 V52e machine (`MARKET_EVENT_LEDGER_804`), not
V52h.

## ⑤ The review packs

Pushed as built @ `76f82dd8`: **ARSMAR** (machine-exact bell = `w1_right`; zero post-bell rows) and the
four violent sample games **KUMTUR · BALHUA · MORNEP · PANYOR**, each with `tminus_bell_s` to the resolved
actual bell, post-bell-in-window trade counts, and pre-bell closes beside the old W1 closes (KUMTUR: 458
of 461 KUM window trades are post-bell; BALHUA: 595/596). GUEGOM @ `03e38798`, DELXIL @ `5c5bf82c`
complete the review set. Disclosure: the ARSMAR pack regenerates the four `c09bde99`-format CSVs in
GUEGOM format (added `tminus_bell_s`); the originals remain at their pin; the two `restpath.csv` files are
untouched.

## Conservation

804 games = 192 MACHINE_RECEIPT + 591 TAPE_SIGNATURE + 1 SETTLEMENT_NO_MATCH + 20 BELL_UNRESOLVED. 1,608
legs = 1,536 scored + 51 no-onset/no-tape + 21 onset-but-empty-window. Floors: 69 vanish + 85 rise
pre-bell. Census: old offered 612 (= frozen census exactly) → 564; margins 4,603¢ → 2,258¢. Post-bell
fills 93 legs / 63 games / 44 completed pairs / 178¢. No score, policy, or ledger byte modified — counts
and receipts; the operator rules the consequence. ANALYTICAL_ESTIMATE.
