# MORNING DOSSIER — 2026-07-08 (the entry dossier + the naked-exit recurrence)

One document, exchange truth, per-category everywhere. Times ET unless stamped Z.
Prior art (C45): this extends the 07-07 sweep/conviction lineage (LIVING_VAULT 07-07 late entry, `.claude/sweep_20260707/`), the disk-full graves (06-25, 07-01 — `project_disk_full_incident` class), C47-CONTINUOUS, and the POST_FILL classifier (`POST_FILL_MOVE_20260708.md`). Delta: the recurrence is convicted as a *liveness* class, not an exit class; the entry read below carries every mechanical leg flagged so the bugs don't pollute it.

---

# PART 0 — NAKED-EXIT RECURRENCE: CONTAINED, THEN CONVICTED

## 0a. THE SWEEP (paginated exchange truth; before → after)

**BEFORE (15:27:32Z / 11:27 ET): 27 unsettled positions — 8 NAKED (40 sh), 19 covered, 0 partial.**

| leg | cat | pos | resting sell | basis¢ | filled (ET Jul-8) | status at sweep |
|---|---|---|---|---|---|---|
| KXITFWMATCH-26JUL08MILMIS-MIS | ITF_W | 5 | 0 | 92 | 04:37:45 | NAKED |
| KXWTACHALLENGERMATCH-26JUL08VANSEL-VAN | WTA_CHALL | 5 | 0 | 38 | 04:44:01 | NAKED |
| KXITFWMATCH-26JUL08MILMIS-MIL | ITF_W | 5 | 0 | 6 | 05:32:27 | NAKED |
| KXWTACHALLENGERMATCH-26JUL08JONJEA-JON | WTA_CHALL | 5 | 0 | 50 | 06:16:06 | NAKED |
| KXITFWMATCH-26JUL08LUENAT-LUE | ITF_W | 5 | 0 | 53 | 06:45–06:51 | NAKED |
| KXITFWMATCH-26JUL08LUENAT-NAT | ITF_W | 5 | 0 | 41 | 06:59:47 | NAKED |
| KXWTACHALLENGERMATCH-26JUL08JONJEA-JEA | WTA_CHALL | 5 | 0 | 47 | 09:30:40 | NAKED |
| KXATPCHALLENGERMATCH-26JUL07TOMSHI-TOM | ATP_CHALL | 5 | 0 | 63 | 11:18:57 | NAKED |
| (19 further legs, all Jul-6/7 fills) | — | 5 ea | 5 ea | — | pre-crash | COVERED |

**Containment executed:** disk freed 100%→82% (see 0b root cause) → the `<90%` respawn cron fired **15:30:02Z**; boot reconcile posted all 8 exits within 36 seconds at the standing bands (adoption at fills-VWAP true basis, A54/C-TRUE-BASIS path):

| leg | exit posted | band_x | result |
|---|---|---|---|
| TOMSHI-TOM | 82¢ | 19 | resting |
| JONJEA-JON | 61¢ | 11 | resting |
| JONJEA-JEA | 56¢ | 9 | resting |
| LUENAT-LUE | 65¢ | 12 | **ITM (bid 81) → taker path: SOLD 5 @ 85¢** (basis 53, is_taker=true 15:30:35Z) |
| LUENAT-NAT | 49¢ | 8 | resting |
| MILMIS-MIL | 9¢ | 3 | **ITM (bid 13) → taker path: SOLD 5 @ 13¢** (basis 6, is_taker=true 15:30:37Z) |
| MILMIS-MIS | 98¢ (capped) | 7 | resting |
| VANSEL-VAN | 45¢ | 7 | resting |

Second wave (fills landing DURING containment on still-orphaned bids, adopted by the live bot's steady-state reconcile ≤8 min): DAMARN-ARN exit 80¢ 11:37:38 · DAMARN-DAM 45¢ 11:37:43 · PDARIB-RIB 26¢ 11:37:58 · MAXABA-MAX 84¢ 11:39:34 · ISHCRO-CRO 72¢ 11:43:11.

**AFTER (15:44:59Z): 32 positions — 32 COVERED, 0 NAKED, 0 partial.** (Raw dumps: VPS `/root/naked_sweep_20260708/{positions,orders_resting,fills_recent}.json`.)

## 0b. THE CONVICTION — the watchdog, per leg, with the rows

**The defect is a LIVENESS class, not an assertion class. Named: C-LOG-ENOSPC.**

Root chain (console log `logs/live_v4_crash_20260708.log.gz`, tail):
1. Disk hit 100% overnight (16G tennis.db + 11G durable + **9.0G uncompressed per-ticker tick CSVs** + 243MB console log — the bot fills its own disk).
2. **02:52:04–02:52:22 ET:** WS handlers logged `WS_ERROR [Errno 28] No space left on device` and *survived* (reconnect swallows). Then `routing_tick → _route_event → _log("skipped") → self.log_file.flush()` raised **uncaught OSError ENOSPC**; `run()`'s catch-all called `self._log("error", …)` which **died in the same flush** → process exit. The logger killed the loop.
3. The `*/2min` respawn cron is gated `disk<90%` — **correct gate, but an absorbing state**: nothing frees disk, nothing escalates. Bot down 02:52→11:30 ET (12.6h).
4. The dead bot's **316 resting orders** (02:50:37 audit count) stayed on the exchange and kept filling: **every naked fill is post-crash (04:37–11:18 ET); every pre-crash fill had its exit resting.** 100% separation — see 0c.

**Did an audit PASS while a leg was naked? NO — there was no audit alive to pass.** Per audit surface:

| audit surface | overnight record | verdict |
|---|---|---|
| In-process 15-min `steady_cadence` (C47-CONTINUOUS) | 23:57 boot → PASS every ~15 min; **00:44:43 FAIL `STERAD-RAD:no_exit`** → conception halt → exit posted @42 **one second later** (the fill was booking as the audit read — a 9-second race, not a defect) → `halted_reaudit` **PASS 00:46:16** (93s heal). Last PASS **02:50:37** (55 pos / 316 orders). Then the process died; the auditor died with it. | Assertions SOUND while alive; **blast radius = the process**. The operator's "PASS all night" window ends 02:50. |
| External `position_audit.py` (cron */30) | **Has NEVER run from cron.** The line `set -a && . .env && set +a && …` dies under dash: POSIX `.` searches PATH only → `.: .env: not found`, rc=2 before python launches; stderr went to a nonexistent MTA. `audit_cron.log` never existed; `audit_log.json` frozen **Feb 28**. | DEAD SINCE FEBRUARY. One-char fix `. ./.env` applied (crontab backup `crontab.bak_enospc_20260708_115230`); first successful cron-path run verified today. |
| nightwatch / watchdog.sh (1-min) | Detected BOT_DOWN within 60s of the crash and appended **~758 minutely alerts** to local files (58,573 lifetime BOT_DOWN lines) — no channel out (no MTA, no push). nightwatch itself started erroring ENOSPC at 11:18 when the disk filled completely. | Detection worked; **escalation layer does not exist** → BOARD item. |
| cash_ledger snapshot (cron hourly) | Crashing since **Feb 26** — `balance_snapshots.json` contains git merge-conflict markers (`<<<<<<< Updated upstream`). Same era as the position_audit freeze: the whole out-of-process layer rotted in late Feb while in-process machinery grew. | Repaired (corrupt file archived `.bak_conflictmarkers_feb26`, reinitialized; snapshot verified live). |
| shape_accumulator (cron 04:45) | Jul-8 run died mid-write on the same ENOSPC (0-byte `samples_20260708.jsonl`). | Re-run post-recovery: folded 632 legs / 6,553 samples. |

**Per-leg conviction rows** (fill vs audit timeline — all 8 + wave-2 legs share one row class):
every leg filled ≥1h45m AFTER the last audit of any kind (02:50:37); no exit was ever posted-then-died (the jsonl shows zero exit-post attempts for these tickers before 11:30 — nothing was alive to attempt one); the fills happened via orphaned maker bids resting on the exchange book. **Defect class per leg: DEAD-PROCESS-ORPHAN-FILL (naked-class), MECHANICAL.** The one pre-crash naked window (STERAD-RAD 00:44:43, 9 seconds) was booking-race noise the audit correctly flagged and the machinery healed unaided.

## 0c. THE PATTERN — covered vs naked, one table

| cohort | n legs | fill window | resting exit? | what distinguishes |
|---|---|---|---|---|
| COVERED (Jul-6/7 fills) | 19 | all **before 02:52 ET** | yes, every one | fill booked by a LIVE bot → `_v4_apply_exit`/sweep-era machinery posted the band exit at fill time |
| NAKED wave 1 | 8 | **04:37–11:18 ET, all after 02:52** | none until 11:30 | fill landed on an orphaned bid of a DEAD process |
| NAKED wave 2 | 5 | 11:20–11:44 ET (containment window) | ≤8 min (steady-state adoption) | fills on still-orphaned pre-crash bids; live bot's check_fills doesn't poll orders it isn't tracking — reconcile adopts on cadence |

Fill path, category, ITM-at-post, the 23:57 boot window — none of them split the cohort. **The single separator is fill-time vs process-death (02:52 ET), 100% clean.** (The 23:57 boot is simply the last preflight deploy — the band-clamp deploy — and is innocent; its process is the one that died at 02:52.)

## 0d. THE FIX — shipped in the same gated deploy (the class is one line)

- **Code (`9a74b061` C-LOG-ENOSPC):** `_log` / `_log_tick` / `_log_trade` write+flush wrapped `try/except OSError` — drop the line, never the bot; `_log_write_errors` counter. With this, 02:52 becomes a 5-second hiccup (run():9690 sleeps and continues). Proof: `.claude/proof_20260708/PROOF_LOG_ENOSPC.md` (Lane 1 unchanged by construction; Lane 2 $0 claimed).
- **DEPLOYED through the full gate: `bfd2814`, PID 1383620, 11:58 ET** — lint PASS, smoke PASS (216,875 book states), outcome-proof OK, C50 two-file OK, post-boot audit PASS, 0 errors.
- **Ops, same pass:** disk 100%→82% (2,205 idle tick CSVs gzipped lossless — readers already handle `.csv.gz`; crash console log archived); crontab repairs with backup — position_audit `. ./.env` (external audit alive for the first time since Feb), daily disk-hygiene jobs (gzip idle ticks >4h @06:17, truncate console log >500MB @06:27, gzip jsonls >2d @06:37); cash_ledger snapshot file repaired.
- **NOT improvised tonight (BOARD):** BOT_DOWN escalation channel (operator decision needed: push/SMS/dashboard-red); an out-of-process 15-min naked-leg audit twin (position_audit asserts trades.json lineage, not the v4 band contract — extend it or write a thin exchange-truth checker).

---

# P&L RECONCILIATION (mandatory format: cash + portfolio + Kalshi API)

| lens | number | source |
|---|---|---|
| Kalshi cash | **$757.26** | API /portfolio/balance (12:00 ET; $755.86 at 11:59 — a settlement landed between reads) |
| Kalshi portfolio value | **$77.10** (API `portfolio_value` 7710¢; 31–32 unsettled positions, exposure sum $80.05) | API /portfolio/positions |
| PM | $80.00 (cash, idle) | SDK |
| **Total** | **$912.61** | cash_ledger snapshot (repaired, first clean run since Feb 26) |
| vs 07-07 evening cut | cash $747.43 → $757.26 (**+$9.83 cash overnight**, incl. settlements + the two containment taker-sells: LUE +$1.60 realized over basis, MIL +$0.35) | EVENING_CUT_20260707 |

---

# STANDING BOARD ITEMS (nothing dropped)

1. **Jul-8 checkpoint (week-order midpoint):**
   - **Config-hold: CONFIRMED.** Every config commit since the aba83af baseline is a sanctioned gated flip already ledgered (riser arm→disarm, Flip #20, shadow arms, join-trial retire, walk-cap staging OFF). Today's deploy is code-only (defect exemption); zero config/table delta.
   - **ITF_W crossing: NOT CROSSED.** Accumulator re-run post-recovery: **coverage 0/500 target cells at n_honest≥30 (0.0%), trigger=False** (corpus: +632 legs / 6,553 samples folded today). The aim median re-derivation stays BLOCKED-ON-DATA per the Plex regression ruling; **the 14k-claims-vs-live holdout harness read is therefore not yet triggered** (walk-forward runs when coverage floors are met — coverage is the trigger, not vibes).
   - Leak-decomposition cumulative table: **rides tonight** — last night is not a valid leak night (bot dead 02:52→11:30; the leak channels measure a LIVE bot's timing). Flagged, not smoothed.
2. **Post-gun forensic** — NEXT in lane (unchanged).
3. **Price-band clamp live-verify** — see Part 1 side-answer (a) below (overnight jsonl scan).
4. **8 latch-only bids' overnight outcome** — see Part 1 side-answer (b) below.
5. **Fractional/MALKOM/PAT queue** — intact on BOARD (items 6/7/8), untouched.
6. **Plex reanchor slot** — still open (`0a17ce03`), still owed by relay.
7. **Re-entry doctrine** — awaiting operator ruling (carried).
8. **NEW (this incident):** BOT_DOWN escalation channel + out-of-process audit twin — BOARD IN-FLIGHT.

## 0e. FOOTPRINT AMENDMENT (post-census — the 8 open legs were the survivors, not the incident)

The full-cohort census (Part 1, exchange fills) puts the dead-window footprint at **203 crash-orphan fills + 8 wave-2 adoptions = 211 MECHANICAL legs of 293 total** (Part 3's independent strip: 218/292 under its slightly wider convention). Most settled before the 11:27 sweep — the 8 naked open positions were the tail still alive. 77% of the night's fills landed after tape-inferred match start (Part 2): a dead bot cannot cancel at match-live, so the orphaned bids provided **in-play** liquidity all morning. Settlement of the mechanical cohort: 95 winners / 121 losers (rode to 0) — the B/F grade mass in Part 1 is *unmanaged pair-ride*, not entry quality. The collectors (tick/trade recorders) died with the disk 02:46–11:30 ET, so Parts 1–2 bridge the hole with the Kalshi public trade tape (starred trades-only classifications).

---

# PART 1 — LAST NIGHT'S COHORT, PER LEG (293 rows)

**Full table: `PART1_COHORT.md`** (this directory; raw JSON `dossier_part1_out.json`). Headline:
- **n=293 filled legs** (ITF_W 127, ITF_M 124, WTA_CHALL 22, ATP_CHALL 20, mains 0); 211 MECHANICAL.
- **Median gap to own fillable W1 low: +0¢** (W1?-fills +3, W2~-fills −2) — the fills sit ON their own lows; the naked fills were the move's leading edge (the POST_FILL 07-08 finding reproduced on a 10× larger, bug-polluted night).
- **Class mix: REPRICE 131 (45%) / DIVOT 77 / NO_UNDERCUT 40 / AMBIG 32 / NO_TAPE 13** — 210 rows are starred trades-only proxies (order-book tape unrecoverable in the dead window).
- **Grade mix: S 9 / A 41 / B 110 / C 4 / D 7 / F 122** — B and F are overwhelmingly rode-to-settlement shapes (nobody home to exit), MECHANICAL-flagged so they don't read as entry verdicts.
- Windows: honest clock had NO observed_start all night; latches only pre-crash → most rows carry `W1?`/`W2~` (tape-onset anchors) or window-uncertain flags, per the honest-flag convention.

Side answers (standing items #3 and #4):
- **(a) Band-clamp live-verify: FIRED but NOT AIRTIGHT.** 51 `band_refused` events post-boot; resurrection boot-audit `bid_outside_5_95`=0. BUT **29/639 post-boot buys were placed outside [5,95) via the walk/repost path** — a second chokepoint the clamp does not cover — and one filled: HARMAI-HAR 5sh @4¢. Enforcement half-done; see Part 4 shortlist.
- **(b) The 8 LOUD tape-latch-only bids: all 8 filled; 7/8 cashed exits** (several on exits that rested straight through the crash); **1 casualty: MIXKRU-MIX @39 rode to 0.**

# PART 2 — THE UNISON COUNTERFACTUAL (174 pairs)

**Full table: `PART2_UNISON.md`.** Conservative prints-only convention (a counterfactual fill is claimed only where sell-flow actually printed at/below the claimed level while claimable); sim-flattery flags carried per row.
- **Median delta (achieved − unison-achievable): ITF_M 0¢ · ITF_W +1¢ · ATP_CHALL 0¢ · WTA_CHALL 0¢.** Where both legs are claimable (28/174 pairs), unison buys ~nothing — the fills were already on their divot-qualified claimable lows.
- **Unison-≤97 claimable: 14/174 pairs.** (The 80/119 both-filled pairs that ACTUALLY made ≤97 are dominated by uncompensated in-play mechanical fills a live bot would have cancelled — not an entry achievement; MECHANICAL discipline holds.) Unison ≤ cat S-line: **exactly 1 pair** (JONJEA 46+44=90, WTA_CHALL — itself naked-class).
- **The binding constraint is print scarcity, not conditioning: 224/348 legs printed ZERO W1 sell-flow** — FLOOR-BY-HOUR's silent lattice reproduced live. Divot-conditioned floors ≈ unconditioned floors on this tape.
- **Doctrine-level finding:** the S-line's habitat (the T-20m→bell burst, where pair-story's floor lives) **is exactly what the built latch clock refuses to trade** — the bell clock and the engine's latch clock disagree by the premature-latch margin, and the achievable floor sits inside that gap. Caveat: 171/174 starts are tape-inferred (premature-biased → the replay under-claims, honestly).

# PART 3 — CLEAN 3-DAY COMPARISON (MECHANICAL stripped)

**Full tables: `PART3_CLEAN3DAY.md`** (+ reproducible scripts/JSON beside it). Strip manifest: Jul-6 79/391 legs (dup/adoption classes per BLEED_ATTRIBUTION), Jul-7 126/655 (dup-storm + 4 naked-sweep), Jul-8 218/292 (naked-class + dead window). CLEAN columns per cat:

| cat | entry-vs-own-low (6→7→8) | divot share | band-reach pregame | read |
|---|---|---|---|---|
| ITF_M | 6.0¢ → 1.0¢ → 0.5¢ | ~25% flat | 7% → 38% | **genuinely improving** |
| ITF_W | 10¢ → 3¢ → 1¢ | ~18% (0/7 decisive Jul-8 sliver) | 10% → 48% | improving on price, **still reprice-dominated** |
| ATP_CHALL | → 1.7¢ | — | ~23% | flat-to-slightly-better |
| WTA_CHALL | 1¢ / 1¢ | 1 divot in 11 decisive | — | flat |
| mains | n≤8 all days | — | — | NO-READ |

Distortions named: Jul-8 gross is 75% mechanical (describes unmanaged orders — band/divot metrics UNAVAILABLE for those legs, not just skewed); Jul-6 gross FLATTERED entry quality (dup fills bought the dips: ITF_M 3.5¢ gross vs 6.0¢ clean) and band-reach (+4pts); grade-mix gross flattered B-share both ledger days (clean F-share rises, ITF_M Jul-7 29→38%). **The clean columns look worse and are truer.**

# PART 4 — THE VERDICT, PER CAT (findings first, then the shortlist)

- **ITF_W: (a) waiting-on-the-brain.** The clean entry price is closing on its own low (10→3→1¢) while the fill CLASS stays reprice-heavy — exactly the POST_FILL diagnosis: depth alone buys reprices cheaper; the selector is ask-hold + sibling-chain state. **Cells qualified at today's checkpoint: NONE** — honest corpus coverage 0/500 cells at n≥30 (trigger=False, accumulator re-run post-recovery). No tuning available that isn't guessing ahead of the data.
- **ITF_M: (a), stay the course.** The only cat with a monotone clean improvement on both price and band-reach. Nothing to change now; the aim build inherits it.
- **ATP_CHALL / WTA_CHALL: (a)** — flat at small clean n; no code-shaped defect in the entry path surfaced.
- **Mains: no-read** (three straight days n≤8; zero mains legs in tonight's cohort).
- **(b) — code/analysis changes available NOW (the shortlist, defects only, config untouched):**
  1. **Walk/repost band-clamp bypass** (Part 1 side-answer): C-BAND-CLAMP enforces [5,95) at the placement chokepoint only; the walk/repost path placed 29 buys outside it post-boot, 1 filled @4¢. Same flag class as the preflight deploy — extend the clamp to the walk chokepoint. One-line class, gate-eligible next deploy.
  2. **BOT_DOWN escalation channel + out-of-process audit twin** (Part 0) — ops build, operator decision on channel.
  3. **Latch-vs-bell forfeit window** (Part 2 doctrine finding) — NOT a change tonight; it is the named question the post-gun forensic (NEXT in lane) must answer with honest-clock data: how much of the T-20m→bell floor do premature latch-cancels forfeit, per cat. Analysis, then ruling; touching latch behavior is config and the week order holds.
- **No proposal is dressed as a finding above**; items 1–2 are defect classes with live exhibits, item 3 is a question routed to the lane that owns it.

# PART 5 — CROSS-REFERENCE vs LIVING_VAULT (chronology law; flags, not smoothing)

1. **FLAG — the 07-08 preflight entry** ("C-BAND-CLAMP … no maker buy outside [5,95) at the chokepoint"): TRUE at that chokepoint, **incomplete as a book-wide guarantee** — the walk/repost path is a second conception site (29 placements, 1 fill). The standing entry stays; the gap is named on the BOARD shortlist.
2. **TENSION (not contradiction) — the latch lineage** (C-RIDE-LIVE-OFF, latch_tape_override, LATCH-CAL): Part 2's finding that the achievable floor lives inside the latch-vs-bell gap does not overturn any standing entry (pair-story already placed the floor in the last ~20min), but it sharpens the cost of premature latching from "missed bounce" (FERCER) to "the S-line habitat is systematically unreachable." Routed to post-gun forensic.
3. **CONSISTENT — POST_FILL_MOVE (07-08):** Part 1's median gap +0¢ / fills-as-leading-edge reproduces the finding on a 10× night; REPRICE 45% cohort-wide matches the ITF_W diagnosis.
4. **CONSISTENT — dup-storm/BLEED lineage:** Part 3's Jul-6/7 gross-vs-clean distortions land exactly where those entries said the bugs were; clean columns adopted for all trend claims here.
5. **FLAG — ledger vs exchange on adopted exits** (A52/A54 family): the bot ledger recorded LUENAT-LUE's exit at 65 while the exchange printed the taker sweep at 85; every adopted-exit price in tonight's ledger must be read from /fills, not the bot's exit_price field. (Part 1 graded from exchange prints.)
6. **CONSISTENT — 0A exits-out-of-scope:** nothing in this dossier proposes exit-policy change; the band levels were used as-found throughout.

# CODA — what last night was, in one paragraph

Last night was not an entry-quality night; it was a liveness incident wearing an entry ledger. The bot traded honestly for 3h40m (23:12→02:52), died full-disk, and its 316 orphaned bids spent 8.6 hours filling into live matches with nobody home — 211 mechanical legs whose B/F settlement mass says nothing about placement. Inside the clean 70-leg sliver and the 3-day clean trend, the entry program is doing what the doctrine asked: ITF fills now land 0–1¢ off their own fillable lows (ITF_M monotone-improving on band-reach too), and the remaining gap is not price but *class* (reprice-dominated fills) and *habitat* (the floor lives in a window the latch clock forfeits) — both already owned by named lanes (AIM_V2 blocked-on-coverage; post-gun forensic NEXT). The machine's real lesson this morning is the one shipped: the logger can no longer kill the loop, the disk can no longer strand the respawn, and the audits that "passed all night" now have a heartbeat that doesn't share the patient's.

