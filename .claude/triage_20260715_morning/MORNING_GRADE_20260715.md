# THE MORNING GRADE — 2026-07-15, every placement and fill since the 2:36:35 AM boot
(C-MORNING-TRIAGE v1 Part 5 · graded ~1:20 PM ET · full per-leg table: `GRADE_TABLE.md` (520 rows, one per leg) · raw JSON `/root/morning_grade_20260715.json` on the box)

## PRIOR ART (C45)
- Window ledger machinery: C-WINDOW-LAW 07-14 (`_window_phase`, W1/CORRIDOR/W2 stamps on every decision — this grade's phase columns read those stamps; ADJUDICATION_20260714 §WINDOW LEDGER is the nightly form). Delta: this grade splits **placement-phase and fill-phase as separate columns** (operator APPEND 07-15) — the nightly ledger does not.
- Fill grading rubric: POSITION_GRADE / S-A rubric (BOARD §S/A) grades positions; this grade adds a mechanical tape grade per FILL (below).
- E-vs-A: C-FLOW-REST-SEED 07-15 seeded the dossier gauge; the nightly REACH E-vs-A line grades integration windows. Delta: this grade holds the gauge to its placement-instant p_fill.

## THE HEADLINE NUMBERS (all with n)
- **653 buy placements** across **520 legs** since boot; **104 fills booked** (53 fresh-path, 51 reconcile adoptions/re-bookings).
- **Placement-phase vs fill-phase (the operator's window question):** placements landed overwhelmingly W1; fills landed **W2 75 / W1 24 / CORRIDOR 5 of 104** — the book is built early, the fills arrive at/after the gun.
- **Corridor-placed buys, flagged by name (9, ALL MAINS, zero ITF):** SHEQUE-QUE, TRANAV-TRA, BUBHAL-BUB, KYMTSI-KYM, KYMTSI-TSI, TABMID-TAB, BASTIR-TIR, AVAMAR-AVA, AVAMAR-MAR. Under the operator's window word these are exactly the dispreferred late buys — the W1-PREFERENCE rule (priced below) would have refused all 9.
- **Fill grades (mechanical rubric, stated):** TIGHT = tape's 30-min post-fill low stayed within 1¢ of fill; EARLY = tape printed ≥2¢ below fill within 30 min; UNDER-THE-WALL = join-queue depth_at_post ≥500 and still filled (dip-through). Result: **EARLY 79 / TIGHT 25 of 104** — 76% of fills saw the tape go ≥2¢ lower within 30 minutes. The aim-vs-dip gap is measurable leg by leg in the table. (Named caveat: the 51 adoption bookings grade off booking ts, not exchange-fill ts — their windows are shifted late; the 53 fresh fills carry the clean grades.)
- **Exit same-second: 104/104 fills had the band exit posted ≤60s, order-id cited in the table** (typ. +0.2–3s). Exit discipline is clean — no naked windows this morning outside the two audit races below.
- **Expected-vs-actual under the seeded gauge (dossier p_fill_1h at placement, n=314 consultations):**
  - quiet bucket: n=289, E[fills]=1.82 → **actual 59** (~32× under-prediction — fills come at flow onset, the placement-instant gauge reads quiet; the −0k/onset-lag class at slate scale)
  - open bucket: n=17, E[fills]=17.0 → **actual 0** (placements INTO flow never filled — cancelled by match_live or never reached)
  - warm: n=8, E=0.43 → 0
  - gauge_src: rest_seeded 307 / ws_only 7 (the R1 seed is live and feeding)
  - **Reading: the gauge is anti-predictive at the placement instant on this slate — the harvest is rest-early-fill-late; placement-time "open" is too late. This is the numeric spine under the operator's word: "late buys are not preferable."**
- **Tail-vs-path billing (realized since boot):** settles TAIL n=15 −280¢ | settles PATH n=39 **−3,159¢** (TRANAV −415, LEOTSI −315, ALHVUX −385 pre-boot conception, MASDUT −155, SEMALE −120, POPMIC −90, KAMTIM −90, MATRIV −90…) | band exits cashed n=60 **+2,509¢** | flattens n=6 (incl. RINTAB −10 TAIL). Net realized ≈ **−$9.3** before fees. The morning's shape: W1 exits cash +$25.1 while W2 rides bleed −$31.6 — the ride-to-zero side is the leak, not the entry lane.
- **Scalar-retirement settles (new tape fact): 3 this morning** (MASDUT 50¢ WIN −155, POCMIS −55, GUZPAR −70) — retirements settle at 50 and turn >50-basis "winners" into losses; these are ungovernable by exits (book empties at determination).

## VIOLATION CENSUS — monitor cycles 100–117 (9:36–11:47 AM), chatter vs real
| class | lines since boot | distinct subjects | chatter share | real signal |
|---|---|---|---|---|
| bell_missing | 199 | 192 events | coverage-sweep chatter (each unbelled slate event lines once per sweep) | the scorecard's named **BELLS-MISSING=71** with honesty windows (AUNALV + the 2:36 restart gap) — coverage item, not new defect |
| completion_taker_capped | 32 | 21 legs | re-evaluation chatter after cap 3/3 hit | the DECREED 3/day taker cap bound at 3 actions by ~3:11 AM; **21 further taker verdicts refused-named** — leash working as decreed, but 21 wanted completions is a real economics number for the cap's n≥30 sunset review |
| completion_flatten_deferred | 40 | 26 legs | EV-within-noise guard lines (design) | 0 defects |
| completion_flatten_capped | 17 | 13 legs | cap 8/day binding (design) | 0 defects |
**Real defects in the window: the two audit-race halts below (both rooted today). Everything else is guard chatter — the leashes printing their names.**

## THE TWO HALTS, ROOTED
- **9:58:07 AM (MASDUT-DUT, band 98, bid 0): AUDIT-vs-SETTLEMENT race.** The match retired → market determined 9:58:36 → the exchange emptied the book (bid 0) and shed the resting 98¢ exit (order d7413b69, posted 6:24:47 same-second with the fill) moments before the audit read "held 5, no sell resting". Settlement booked 10:02:30 (scalar 50, −155¢); halt cleared on re-audit. The leg was never naked-by-defect.
- **11:24:29 AM (JONURG-JON, band 0, bid 67): AUDIT-vs-FILL-DISCOVERY race — the band-0 class, instance 2** (TOPGEN 07-14 08:40:51 was instance 1; DARCRI 12:15:56 PM printed instance 3 same family post-window, self-cleared 12:18). Exchange fill 11:24:16 → audit 11:24:29 (13s gap, `pos_obj` unbooked → `band = 0` at live_v4.py:12167) → cancel-race discovery 11:24:40 → exit 5@87 posted 11:24:43 (order a1a3f307, band_x 18 on entry 69). **The C-BOOK-THE-FILL healer silently skipped both times: its basis input (exchange `market_exposure_dollars` on a seconds-fresh position) resolves falsy and the code falls through to the halt with no `fill_book_error` line. REMEDY PRICED (not deployed): (a) log the skip reason at the fall-through; (b) fall back to the order-fingerprint's posted price as booking basis; (c) treat determined/empty-book markets as settlement-pending FLAG not FAIL.** Both halt classes are conservative (halt conceptions, exits keep working) and self-healed inside 8 minutes.

## GUN SCORECARD — the verdict for the 6:10 word
**DELETION GATE: OPEN — all four proofs PRESENT** (clean-regrade numbers · percat-vs-legacy priority reconciliation 199 rows · MAINS-OFF denominator split · percat-vs-self-fill table 206 events/1 overlap). Fires 187/453 tracked (41%; non-mains denominator 184/417 = 44%), MULTI-SOURCE 112, SELF-FILL 1 (0 unconfirmed). BELLS-MISSING=71 named — the word inherits the AUNALV bell_missing and the 2:36 restart-gap honesty windows per the standing order. The legacy-trigger deletion word is the operator's to give on this OPEN gate.

## W1-PREFERENCE RULE — PRICED (follow-on, awaits the operator's word after this grade is read)
Operator word (verbatim, vaulted this push): *"late buys are not preferable; corridor should only be happening as a fallback when vol is low with ITF."*
- **Rule as priced:** mains/CHALL CORRIDOR-phase entry placements = REFUSED, named (`corridor_refused_w1_preference`). ITF CORRIDOR entry placement permitted ONLY as fallback: discovered ≥1,500 (the armed floor) AND volume-quiet at placement AND named on the dossier. Resting-early-fills-late explicitly NOT penalized (fills in CORRIDOR/W2 on W1-placed bids stay lawful) pending the operator's confirmation of the placement-time reading.
- **Costed on this morning's tape:** would have refused the 9 named mains corridor buys (of which BASTIR-BAS/TABMID-MID/SHEQUE-SHE/BUBHAL-HAL/IBRBAD-IBR later filled W2 with exits resting — their outcomes are open; the rule's bill lands when they settle). ITF corridor placements this morning: 0 — the ITF fallback clause costs nothing on today's tape.
- Not armed. One flag, one gate, on the word.

## PART 2 CROSS-REFERENCE
The ≥1,500 discovery floor (corridor + stale-dated conceptions) is ARMED via the full gate this push — proof `.claude/proof_20260715/PROOF_DISCOVERY_FLOOR.md` (VU exhibit ALHVUX: 60-share conception, never-traded sibling, −385¢; replay 9 events → 4 refuse net +300¢, KOAYAZ's +85¢ forgone named honestly).
