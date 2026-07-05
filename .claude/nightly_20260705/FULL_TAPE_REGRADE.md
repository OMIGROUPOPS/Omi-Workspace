# FULL-TAPE REGRADE — the current box, time as a first-class dimension

**Window:** aba83af boot Jul 4 21:32:50 ET → Jul 5 17:03 ET (both bot logs; the 733341f
10:39 restart is inside the window). **Population: 144 games / 251 filled legs / 107
completed pairs.** Exchange truth refreshed off the fills API (531 fill rows reconcile to
the 251 ledger legs) + market results for all 251 tickers. 71 games had outcomes land
AFTER the morning pass; only 4 games still carry an open leg (VILPER, SEKMAL, VANTRO,
ARSOSU). Read-only throughout — no config, no restarts; the box holds.

Artifacts: `ftr_report.txt` (one row per game, every tracked metric), `ftr_dump.json`
(full per-leg/per-fader detail), `full_tape_regrade.py` (the pass, rerunnable).

---

## (1) FINAL RESULTS — the regrade

**Exchange truth (mandatory format):** cash **$902.75** + portfolio **$11.21** (balance
API ts 1783285543; positions endpoint shows the 4 open games as the only exposure). Vs
the morning pass ($842.73 + $76.96): cash +$60.02 as day settlements returned collateral
and realized. **Box realized: +$2.23 across 144 games** — the whole night+day nets to
noise; the grade ledger below says where it bled and where it earned.

**Final grades (144 games):**

| cat | A | B | C | D | F | tot |
|---|---|---|---|---|---|---|
| ATP_CHALL | 20 | 11 | 37 | 8 | 11 | 87 |
| ATP_MAIN | 2 | 0 | 1 | 1 | 0 | 4 |
| ITF_M | 5 | 1 | 5 | 2 | 6 | 19 |
| ITF_W | 3 | 2 | 4 | 2 | 7 | 18 |
| WTA_CHALL | 6 | 2 | 4 | 0 | 0 | 12 |
| WTA_MAIN | 2 | 0 | 1 | 1 | 0 | 4 |
| **TOTAL** | **38** | **16** | **52** | **14** | **24** | **144** |

**The PENDING→final migration (morning box only, all legs filled pre-10:39, n=90):**
23A / 10B / 35C / **7D** / **15F** vs the morning report's 27A/12B/31C/**16D**/12F. The
story is the D column: the morning's 16 "half-armed, open/held" naked singles resolved —
the lucky ones exited green and stayed D, **the rest settled as losses and became F**
(12→15 F on a smaller n). Every "PENDING" grade is now final. (Small A/C migrations also
reflect this pass's uniform fv-onset convention — last pre-gun print — not just outcomes.)

**Grade-vs-money monotonicity (settled/exited-only, n=140): NOT MONOTONE.**
A $0.70 / B $0.95 / C −$0.30 / D $0.43 / F −$1.24 mean per game. Two inversions:
- **D > C**: D is naked singles that got luck-directional green exits (+$0.43 mean);
  C absorbs the pairs whose held leg settled to zero. The rubric grades structure, the
  money follows the coin — on this box the coin paid D and punished C.
- **B > A** (small): several A pairs earned pennies while B pairs caught bigger exits.
- The endpoints hold: A/B positive, F clearly worst. The middle is scrambled by one
  named class: **directional-hold bleed inside completed pairs — 10 pairs, −$23.70**
  (FUCKUP-3 shape: capped winner sold, loser held to settle). Named for money
  attribution only — exits are OUT OF SCOPE per the standing order; this is not a
  proposal to touch them.

**The pair scoreboard (107 completed):** 85 ≤97 (**79%**), 63 at exactly 97 (the bound
stack pins), 17 at 98–100, 5 over par (MUCKRE 110 = the patched fallback defect;
IEMBER 102, ILAPLU 101, KAMVAN 100, SABOSA 100, DALARI 100 — the cross-cap/ceiling
adjudication class from the morning board, unchanged).

---

## (2) THE CLOCK FINDING — the tape starts long before the schedule says

Per-game true tape onset (volume gun) vs the scheduled clock, median minutes:

| cat | gun vs sched | n |
|---|---|---|
| ATP_CHALL | **−99m** | 87 |
| ATP_MAIN | −64m | 4 |
| WTA_MAIN | −79m | 4 |
| WTA_CHALL | **−103m** | 12 |
| ITF_M | **−235m** | 19 |
| ITF_W | **−242m** | 18 |

The scheduled clock (kalshi_schedule_primary — the known liar) runs ~1.5h late on
challengers and **~4 hours late on ITF**. Consequence, read directly off the time map:
the bot opens windows at T-4h *scheduled*, which for ITF is **at or after true onset** —
the ITF "premarket" it believes it is trading barely exists. ITF fills land post-gun
(in-play, Window-2, the knife) while the bot's clock says T-3h30m. This is the
structural driver of the ITF half_timing leak below, it is why the fader's divot keeps
passing before leg-1 can set a bound, and it is the live confirmation that deliverable
(c) — the pre-T-4h posting window — is where the ITF opportunity actually lives: on the
true clock, "pre-T-4h scheduled" IS the real ITF premarket.

## THE TIME MAP — when the money lives vs when we act (true-tape clock)

BEST = best fillable sell-flow moment per leg; POST = our first rest; FILL = our fill.

**ATP_CHALL** (134 legs with tape):
```
bucket   BEST POST FILL      reading
>8h-3h      3   36    1      we post here (96% of first-posts are >1h pre-gun)...
3-1h       13  108   18
1h-30m     23    3   27      ...the money starts here:
30-0m      38    2   44      88% of BEST moments are <1h pre-gun or post-gun,
post       57    6   64      and our fills simply mirror them — the bids rest
                             at stale levels until the gun-adjacent dip reaches down.
```
**ITF_M / ITF_W** (54 legs): BEST post-gun 35, 0–60m pre-gun 14, earlier 5. Posts land
near/inside the gun because the scheduled clock lies ~4h late. ITF is being traded
in-play while labeled premarket.
**WTA_CHALL** (23 legs): BEST 10 at 20m-0 + 11 post-gun; posts 2–4h early. Same shape.

**The overlap verdict:** our engagement window overlaps the opportunity window only
because resting bids survive into it. WHERE we post (2–4h pre-gun) and WHEN the money
prints (last 30min pre-gun through the first hour post-gun) are two different regimes;
the level conceived at window-open is what the gun-adjacent dip has to reach down to.
Full histograms on both clocks are in `ftr_report.txt`.

---

## (3) MONEY LEFT ON THE TABLE — ranked, with dollars

| $ | n | flaw class |
|---|---|---|
| −$29.65 realized | 24 F games | half-armed naked single settled LOSS (37 half-arms in box, net −$26.22) |
| −$23.70 realized | 10 pairs | directional hold inside completed pair (exit-domain; named, not actioned) |
| $12.68 forfeited | 14 games | **forfeited completion** — the fader's tape offered ≤bound, no fill (locked-margin value) |
| $8.45 forfeited | 35 legs | **fill above a catchable dip** (dip lasted ≥90s or ≥3 prints, we paid more) |

Worst catchable-dip misses: LEGWIN LEG filled 80c vs a 46c print 56min earlier;
ELIAZO ELI 18c vs 3c (62s dip, 19min earlier); RECDUB REC 59c vs 48c (105s dip, 26min
earlier); MONFER MON 20c vs 6c.

**Leak decomposition, full-box regrade (half-pairs):** the bimodal reading holds and
sharpens —
- **half_timing** (fader dip ≤bound passed BEFORE leg-1 filled): **ITF_W 7 events/147¢ +
  ITF_M 4/66¢** vs ATP_CHALL 3/1¢. The timing leak is an ITF phenomenon, and per §(2) it
  is the lying clock wearing a leak costume.
- **half_no_dip** (tape never offered the bound): ATP_CHALL 12 events — deep bounds off
  cheap leg-1 fills; structural, not timing.
- Sibling starvation is NOT a mass phenomenon this box: **one** real case —
  LEGWIN, bid rested 89min while **41,022 shares** printed at/below our level (the
  queue-wall exhibit, same class as ALTMED-ALT).

---

## (4) THE FLAW IN ENGLISH — one line per sub-A game (times in every line)

Notes for reading: "T-X vs gun" = minutes before true tape onset; "sched" = the
scheduled clock. "before_dip" = our bid was already at/above the dip level when it
printed (we were there; the print filled us or the queue). "never_reached_level" = our
bid never got to the dip's price. Lines quoting a cheaper print name only prints
distinct from our own fills. Pairs graded C on shape ("deep-neg FV fragile",
"zero-discount", "directional hold") carry the money number instead of a tape moment.
Exemplars first, the full 106-line board verbatim below.

**The ones the operator should read first:**
- **[D] WTA MUCKRE (comb 110 — the patched fallback's tape story):** MUC's dip printed
  **62c at T-1h06m before the gun** (sz 279); our bid sat pinned at 59 and never reached
  it; the T-20m fallback then paid **72c, 225 minutes after the moment** — the defect
  C-FALLBACK-BOUND now clamps.
- **[C] WTA SABOSA (comb 100):** SAB's 68c moment printed at **T-2h12m vs gun** (sz 442);
  we filled 69c **170 minutes later**, after the window had inverted.
- **[F] ITF_W DEKCAK:** the fader DEK printed **11c at 09:05:34, 8 minutes BEFORE leg-1
  filled and set the bound 72** — the divot existed, the bound didn't yet; nothing was
  aimed at it.
- **[F] ITF_W BROKOI:** KOI's dip held **20c for 6.9 minutes** (sz 389) at T+58m past the
  gun — catchable at any reaction speed — we caught it (leg-2 21c) but fader BRO's 40c
  moment had passed 30min before leg-1; the pair never completed and the naked leg
  settled −$2.10.
- **[D] ATP_CHALL LEGWIN (the starvation exhibit):** LEG's best print 46c at T+5m; we
  filled 80c **56 minutes later**, and the sibling bid starved 89 minutes while 41k
  shares printed at/below our level; fader WIN's 16c print came 8m before the bound
  existed.

**The full board (machine lines, verbatim from the pass):**

```
[B] ATPCHALLENGER POTANG (comb 97, $1.15): ANG's best print was 46c for 7s (sz 26) at T-6h24m vs gun / T-1h03m sched; we filled 47c 0m later (before_dip)
[B] ATPCHALLENGER JANRYA (comb 99, $0.40): JAN's best print was 90c for 175s (sz 325) at T-3m vs gun / T-2h41m sched; we filled 94c 36m later (never_reached_level)
[B] ATPCHALLENGER KAMVAN (comb 100, $0.64): KAM's best print was 11c (sz 1) at T-12m vs gun / T+15m sched; we filled 13c 1m later (before_dip)
[B] ATPCHALLENGER MORMAR (comb 97, $1.25): MAR's best print was 37c (sz 100) at T+30m vs gun / T-1h09m sched; we filled 38c 0m later (before_dip)
[B] ITFW COHTSE (comb 97, $0.80): COH's best print was 8c (sz 5) at T-1m vs gun / T-3h57m sched; we filled 12c 11m later (before_dip)
[B] ITFW TUBSOB (comb 99, $1.20): TUB's best print was 71c for 102s (sz 50) at T+58m vs gun / T-3h59m sched; we filled 72c 2m later (during_dip)
[B] WTACHALLENGER BARPOP (comb 97, $1.15): POP's best print was 63c (sz 28) at T-0m vs gun / T-1h51m sched; we filled 65c 0m later (before_dip)
[B] SCIORA, ALBZOR, UTADEV, SZYSTR, PDACAS, MARJUN, POPCAS, MORHAU, MONGIM: no tape-visible flaw (filled at/inside the best print the tape offered)
[C] ATPCHALLENGER CRIRUB (comb 97, -$3.25): directional hold settled -$3.60
[C] ATPCHALLENGER PRIROT (comb 97, -$0.40): 1 leg deep-neg FV fragile
[C] ATPCHALLENGER SEIMOL (comb 95, $0.90): zero-discount pair
[C] ATPCHALLENGER SCHDE (comb 99, $1.30): DE's best print was 73c (sz 2) at T-40m vs gun; we filled 75c; SCH's best print was 23c (sz 100) at T-39m vs gun; we filled 24c
[C] ATPCHALLENGER SMIPIR (comb 97, -$0.35): 1 leg deep-neg FV fragile
[C] ATPCHALLENGER BERBOC (comb 97, -$0.15): directional hold settled -$1.10
[C] ATPCHALLENGER RATRAH (comb 97, $1.20): 1 leg deep-neg FV fragile
[C] ATPCHALLENGER MARDUR (comb 97, -$2.75): directional hold settled -$3.15
[C] ATPCHALLENGER MELWAL (comb 97, -$0.75): 1 leg deep-neg FV fragile
[C] ATPCHALLENGER NIJBER (comb 97, $1.25): 1 leg deep-neg FV fragile
[C] ATPCHALLENGER IEMBER (comb 102, $0.05): combined 102c >100 over-par (complete_cross, adjudication pending)
[C] ATPCHALLENGER LUZSAN (comb 97, -$3.60): 1 leg deep-neg FV fragile
[C] ATPCHALLENGER INGFEL (comb 97, -$0.30): 1 leg deep-neg FV fragile
[C] ATPCHALLENGER COVDEL (comb 99, $1.35): 1 leg deep-neg FV fragile
[C] ATPCHALLENGER VALREJ (comb 96, $1.25): 2 legs deep-neg FV fragile
[C] ATPCHALLENGER FELMOE (comb 97, -$3.50): FEL's best print was 75c for 3s (sz 837) at T+0m vs gun / T-2h50m sched; we filled 76c 0m later (before_dip)
[C] ATPCHALLENGER WEIHOE (comb 96, $1.20): 1 leg deep-neg FV fragile
[C] ATPCHALLENGER DESYEV (comb 97, $3.55): 1 leg deep-neg FV fragile
[C] ATPCHALLENGER BASRIB (comb 96, $1.30): RIB's best print was 51c (sz 1) at T+0m vs gun / T-59m sched; we filled 61c 0m later (before_dip)
[C] ATPCHALLENGER SLABAS (comb 97, -$1.20): 1 leg deep-neg FV fragile
[C] ATPCHALLENGER STEDIN (comb 97, $1.30): STE's best print was 23c at T+29m vs gun / T-53m sched; we filled 26c 0m later (before_dip)
[C] ATPCHALLENGER RAMNEU (comb 97, $1.30): 1 leg deep-neg FV fragile
[C] ATPCHALLENGER ILAPLU (comb 101, -$0.52): combined 101c >100 over-par (both legs same second — fallback-class print, now clamped)
[C] ATPCHALLENGER DALARI (comb 100, -$0.10): ARI's best print was 4c (sz 1) at T-0m vs gun / T+189m sched; we filled 6c 0m later (before_dip)
[C] ATPCHALLENGER CIZCAZ (comb 97, $1.25): 1 leg deep-neg FV fragile
[C] ATPCHALLENGER PEROPI (comb 98, -$3.30): directional hold settled -$3.65
[C] ATPCHALLENGER TENBER (comb 99, $1.25): 1 leg deep-neg FV fragile
[C] ATPCHALLENGER SUNBAR (comb 97, -$1.20): directional hold settled -$2.00
[C] ATPCHALLENGER PRICOU (comb 97, $1.15): 1 leg deep-neg FV fragile
[C] ATPCHALLENGER HUANOC (comb 98, -$3.10): 2 legs deep-neg FV fragile
[C] ATPCHALLENGER HIGZHU (comb 96, $1.20): ZHU's best print was 53c (sz 14) at T+10m vs gun / T-46m sched; we filled 58c 0m later (before_dip)
[C] ATPCHALLENGER BINPOL (comb 97, $1.25): BIN's best 58c for 33s (sz 338) at T+1m vs gun, we filled 59c; POL's best 37c for 28s (sz 1005) at T+30m, we filled 38c
[C] ATPCHALLENGER GANZIN (comb 97, -$0.45): 1 leg deep-neg FV fragile
[C] ATPCHALLENGER ELLJOH (comb 97, -$2.80): ELL's best print was 61c (sz 50) at T-8m vs gun / T-1h36m sched; we filled 64c 0m later (before_dip)
[C] ATPCHALLENGER IMAMIL (comb 97, $1.20): MIL's best print was 57c for 1s (sz 50) at T-15m vs gun / T-1h21m sched; we filled 58c 0m later (before_dip)
[C] ATPCHALLENGER PAPMBI (comb 97, -$2.80): directional hold settled -$3.20
[C] ATPCHALLENGER FARMAT (comb 96, $1.20): FAR's best print was 38c (sz 1) at T-47m vs gun / T-1h08m sched; we filled 39c 41m later (before_dip)
[C] ATP HURSTR (comb 97, -$3.20): HUR's best print was 65c for 6s (sz 2437) at T+322m vs gun (deep in-play); we filled 71c 0m later (before_dip); the pair completed but the held leg settled -$3.55
[C] ITF BOUDOU (comb 97, $1.25): DOU's best 74c for 58s (sz 103) at T+58m vs gun / T-3h50m sched, we filled 75c 1m later (during_dip); BOU's best 17c for 178s (sz 89) at T+56m, we filled 22c 21m later (never_reached_level)
[C] ITF DELNIC (comb 101, -$3.40): DEL's best print was 21c (sz 367) at T-34m vs gun / T-3h58m sched; we filled 23c 0m later (before_dip)
[C] ITF LENJON (comb 97, $1.25): 1 leg deep-neg FV fragile
[C] ITF SALCON (comb 102, $0.90): CON's best print was 11c for 17s (sz 1064) at T+52m vs gun / T-2h15m sched; we filled 13c 4m later (never_reached_level)
[C] ITF FARBRO (comb 96, -$2.80): zero-discount pair
[C] ITFW MONFER (comb 94, $1.15): FER's best 66c for 5s at T+28m vs gun / T-3h42m sched, we filled 74c 13m later (never_reached_level); MON's best 6c (sz 44) at T+28m, we filled 20c 17m later (never_reached_level)
[C] ITFW KUHEBE (comb 93, -$1.15): 1 leg deep-neg FV fragile
[C] ITFW TRAABB (comb 98, $1.10): ABB's best print was 57c (sz 25) at T-0m vs gun / T-3h59m sched; we filled 67c 6m later (never_reached_level)
[C] ITFW MUNGAD (comb 97, -$2.35): 1 leg deep-neg FV fragile
[C] WTACHALLENGER MORKOT (comb 97, $0.50): 1 leg deep-neg FV fragile
[C] WTACHALLENGER BAYMAR (comb 99, -$0.50): BAY's best print was 27c (sz 162) at T+44m vs gun / T-50m sched; we filled 28c 0m later (before_dip)
[C] WTACHALLENGER DITLEW (comb 97, $1.15): DIT's best print was 30c (sz 10) at T-21m vs gun / T-55m sched; we filled 31c 0m later (before_dip)
[C] WTACHALLENGER ARSOSU (comb 97, $0.35): ARS's best print was 61c (sz 44) at T+10m vs gun / T-3m sched; we filled 62c 0m later (before_dip)
[C] WTA SABOSA (comb 100, -$3.05): SAB's best print was 68c (sz 442) at T-2h12m vs gun / T-3h00m sched; we filled 69c 170m later (never_reached_level)
[D] ATPCHALLENGER LEGWIN ($0.90): LEG's best print was 46c for 18s (sz 3) at T+5m vs gun / T-1h15m sched; we filled 80c 56m later; fader WIN printed 16c at 21:32:19, 8m BEFORE leg-1 set the bound 17c — nothing was aimed at it; sibling starved 89m while 41,022 shares printed at/below our level
[D] ATPCHALLENGER MARZAN ($0.20): half-armed naked single (exited green, luck-directional)
[D] ATPCHALLENGER VILPUR ($0.85): PUR's best print was 70c (sz 48) at T-0m vs gun / T-1h45m sched; we filled 81c 0m later (before_dip)
[D] ATPCHALLENGER HUEMAR ($0.07): half-armed naked single (exited green, luck-directional)
[D] ATPCHALLENGER URRMEL ($0.20): half-armed naked single (exited green, luck-directional)
[D] ATPCHALLENGER VILPER ($0.00): half-armed naked single (open/held)
[D] ATPCHALLENGER SEKMAL ($0.00): half-armed naked single (open/held)
[D] ATPCHALLENGER VANTRO ($0.00): fader TRO printed 51c at 12:39:08, 192m BEFORE leg-1 set the bound 51c — nothing was aimed at it
[D] ATP AUGDAV ($0.85): half-armed naked single (exited green, luck-directional)
[D] ITF THUGRE ($0.00): half-armed naked single (exited green, luck-directional)
[D] ITF MCKBER ($0.10): BER's best print was 94c for 13s (sz 75) at T+13m vs gun / T-3h59m sched; we filled 96c 0m later (before_dip)
[D] ITFW BUYCOH ($0.20): COH's best print was 12c (sz 4) at T-52m vs gun / T-3h55m sched; we filled 15c 20m later (never_reached_level); fader BUY printed 81c at 09:17:22, 6m BEFORE leg-1 set the bound 82c
[D] ITFW VARGRO ($0.06): half-armed naked single (exited green, luck-directional)
[D] WTA MUCKRE (comb 110, $1.35): MUC's best print was 62c (sz 279) at T-1h06m vs gun / T-3h55m sched; we filled 72c 225m later (never_reached_level) — the patched fallback defect's tape story
[F] ATPCHALLENGER MARNVS (-$0.25): NVS's best print was 4c for 1s (sz 525) at T-24m vs gun / T-3h10m sched; we filled 5c 0m later (before_dip); naked single settled LOSS
[F] ATPCHALLENGER SEYMAJ (-$0.20): half-armed naked single -> settled LOSS
[F] ATPCHALLENGER FRUSIN (-$0.25): half-armed naked single -> settled LOSS
[F] ATPCHALLENGER DONGRE (-$0.95): fader DON printed 78c at 04:14:27, 206m BEFORE leg-1 set the bound 78c — nothing was aimed at it; naked single settled LOSS
[F] ATPCHALLENGER CHESPE (-$1.95): half-armed naked single -> settled LOSS
[F] ATPCHALLENGER BLIPET (-$0.30): half-armed naked single -> settled LOSS
[F] ATPCHALLENGER WALVAR (-$0.15): half-armed naked single -> settled LOSS
[F] ATPCHALLENGER RYBTUN (-$3.65): TUN's best print was 72c for 46s (sz 162) at T-21m vs gun / T-2h15m sched; we filled 73c 1m later; naked single settled LOSS
[F] ATPCHALLENGER GOIAND (-$1.55): half-armed naked single -> settled LOSS
[F] ATPCHALLENGER SANROD (-$4.10): half-armed naked single -> settled LOSS
[F] ATPCHALLENGER MONHUR (-$0.20): HUR's best print was 3c (sz 1778) at T+6m vs gun / T-2h50m sched; we filled 4c 0m later; naked single settled LOSS
[F] ITF SHVFAU (-$0.40): SHV's best print was 1c (sz 3721) at T+25m vs gun / T-3h56m sched; we filled 8c 0m later; naked single settled LOSS
[F] ITF BONBRA (-$0.65): BRA's best print was 10c (sz 1) at T+2m vs gun / T-2h26m sched; we filled 13c 0m later; naked single settled LOSS
[F] ITF SABMIS (-$4.05): SAB's best print was 75c (sz 1) at T+2m vs gun / T-2h15m sched; we filled 81c 3m later (never_reached_level); fader MIS printed 14c at 11:44:20, 3m BEFORE leg-1 set the bound 16c
[F] ITF XUXCHE (-$0.10): CHE's best print was 1c for 55s (sz 1061) at T+60m vs gun / T-3h58m sched; we filled 2c; fader XUX printed 64c at 11:09:17, 52m BEFORE leg-1 set the bound 95c
[F] ITF SLOKHR (-$1.95): fader SLO printed 50c at 12:44:14, 17m BEFORE leg-1 set the bound 58c — nothing was aimed at it; naked single settled LOSS
[F] ITF IONDAO (-$0.50): DAO's best 9c for 154s (sz 196) at T+26m vs gun / T-3h59m sched, we filled 10c 3m later (during_dip); fader ION printed 62c at 13:47:50, 45m BEFORE leg-1 set the bound 87c
[F] ITFW MAXSTE (-$0.70): MAX's best 12c for 158s (sz 146) at T+52m vs gun / T-3h34m sched, we filled 14c 8m later (never_reached_level); fader STE printed 54c at 21:03:18, 30m BEFORE leg-1 set the bound 83c
[F] ITFW BROKOI (-$2.10): KOI's best 20c held 415s (sz 389) at T+58m vs gun / T-3h25m sched, we filled 21c (during_dip); fader BRO printed 40c at 21:04:58, 30m BEFORE leg-1 set the bound 76c
[F] ITFW SPIGAR (-$0.05): fader SPI printed 92c at 06:10:30, 51m BEFORE leg-1 set the bound 96c — nothing was aimed at it
[F] ITFW KARMAT (-$0.05): fader KAR printed 85c at 07:08:08, 64m BEFORE leg-1 set the bound 96c — nothing was aimed at it
[F] ITFW ALVJOH (-$3.65): half-armed naked single -> settled LOSS
[F] ITFW LIMHAG (-$0.65): HAG's best print was 11c (sz 4) at T+60m vs gun / T-3h59m sched; we filled 13c 1m later; fader LIM printed 79c at 08:10:06, 51m BEFORE leg-1 set the bound 84c
[F] ITFW DEKCAK (-$1.25): CAK's best print was 21c (sz 1) at T+30m vs gun / T-3h54m sched; we filled 25c 8m later (never_reached_level); fader DEK printed 11c at 09:05:34, 8m BEFORE leg-1 set the bound 72c
```

---

## (5) Method + caveats (so nothing here gets over-read)

- **Tape** = `analysis/trades/*.csv` (live-updated, sub-minute, taker_side). Best
  fillable moment = cheapest **sell-flow** print (taker_side==no — the flow that fills a
  resting maker bid) between window-open and the entry-window close (latch/gun). Dip
  duration = contiguous prints ≤best+1 with ≤5min gaps; "catchable" = ≥90s or ≥3 prints.
- **The tape contains our own fills.** A row whose best print equals our fill at fill
  time is self-referential — those score "no tape-visible flaw," and every flaw line
  above quotes only prints distinct from ours.
- **Both clocks**: sched = kalshi_schedule_primary (the known liar — §(2) is the
  measurement of the lie); gun = volume burst in the fill-anchored window (night-pass
  convention, fill−1h→fill+6h), ambiguous-flagged when thin.
- fv-onset = last pre-gun print, uniformly — a slight convention shift vs the morning
  ledger; small A/C migrations are convention, not news.
- Pre-bound fader prints with 300–600min leaks are overnight thin prints (context); the
  actionable timing leaks are the ITF cluster at 3–64min pre-bound.
- 4 games still open; their grades are structural (D naked-single) and can only migrate
  D→F on a bad settle.

**Where this points (analysis only — the box holds):** the week's central question now
has a two-part evidenced answer. (1) The ITF timing leak is the scheduled clock lying by
~4h — the fader's divot isn't "early," our bound is late because Window 1 is opened
after the war started; the pre-T-4h posting spec (deliverable c) is the fix-shaped
question. (2) The ATP_CHALL leak is structural no-dip on deep bounds — the tape simply
never offers 97−leg1 when leg1 filled rich; that's a leg-1 concession question, and the
riser fv_observe stream (452 graded, gate exceeded) is already queued for the Plex
bounce at full n.
