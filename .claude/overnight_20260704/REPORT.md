# Morning Validation — 2026-07-04 (window: ba08243 boot 18:32:05 ET Jul 3 → hotfix shutdown 12:58:55 ET Jul 4)

**HEADLINE, NO SOFTENING: one of the five new flags shipped a crash.** `leg2_reshuffle`'s
entry-side branch calls a 1-arg `_sibling_ticker(tk)` helper that is **shadowed by the
pre-existing 2-arg `_sibling_ticker(tk, et)`** defined later in the class body (duplicate
method name, introduced in 5b924f10, armed by ba08243). Every evaluation of a dog leg
(anchor < 50) in the reshuffle branch threw `TypeError`. First fire **05:00:39 AM ET Jul 4**
— the moment the July-4 slate's first dog window opened (patient zero: KXATPMATCH-26JUL04DIMBER,
DIM leg at 44c). From then until shutdown:

- **5,022** run-loop errors = the 5s backstop routing sweep died **every ~5.7s for 7.97h**
  at the first poisoned event — every event after it in the sweep got no backstop routing.
- **817** `on_bbo_update` aborts = BBO-driven placement/management for poisoned events died,
  and because `_route_event` runs BEFORE `_v4_manage_resting` in that handler, **resting-bid
  management (incl. grace-kill cancels) was starved too**.
- 05:00:39 is exactly when the daily placement engine ramps (prior night: 242 buys/121 fills
  04:00→13:00; last night: 34 buys/19 fills in the same hours).

**Hotfix deployed:** 775dac33 (`_sibling_ticker_any` rename), pushed, pulled on VPS,
bot restarted 13:00:02 ET (tmux live_v4, ulimit 262144, PID 2790287). Post-restart:
6 entry fills, 3 maker exit fills, **0 errors**.

---

## (1) HARNESS RESULTS

### Metric A — fills past gun+300s on latch-detected matches: **3 (TARGET 0) — FAIL, all crash-mediated**

| violation | timeline |
|---|---|
| KXWTAMATCH-26JUL04MERRYB-MER (+14.4m) | latch 08:35:51 (tts 24.1m) → grace armed both legs → grace expired 08:40:51 → cancel attempted only **08:50:17 (9.5 min late)** → `success:false`, bid already swept in-play → fill 19c booked via `match_live_cancel_race` |
| KXWTAMATCH-26JUL04MERRYB-RYB (+14.5m) | same event, same mechanism, fill 79c at 08:50:19 |
| KXATPCHALLENGERMATCH-26JUL04GIUFEL-GIU (+31.5m) | latch 09:15:12 (override, tts 104.8m) → favorite leg FEL cancelled ON TIME 09:20:49 (`graced:true`) → dog leg GIU (7c) cancel only **09:46:42 (26 min late)**, already filled. The dog leg is exactly the ticker class the TypeError poisons. |

Verdict: grace_kill **logic** did its job wherever routing was alive (FEL cancel at
grace+37s; 5 grace_armed, 2 resting_cancels, 17 unlatch resets). The violations are the
crash starving the cancel path, not a grace_kill design failure. Metric A must be re-run
clean tonight on 775dac33 before grace_kill gets a PASS.

### Metric B — latch behaviour: **PASS (directionally)**

- Latches: **36 vs 22** baseline. **25 via TTS-override** (tts>30m at latch = the old TTS
  floor would have been blind to them; the floor was sitting on a lying
  `kalshi_schedule_primary` clock — the ALCCLA root cause).
- False-fire spot-check on 5 override latches with the wildest tts (173–238 min "before start"):
  **5/5 were real matches** — all finalized within hours of latch (MAXBRO 02:25Z, GUOSNI 06:10Z,
  BITTUR 09:35Z, PANDER 10:15Z, NAVKOS 12:00Z). Zero false-fires found.

## (2) LEDGER RE-RUN (A–F, all six categories, since ba08243 restart)

20 legs filled / 16 events / 103 tracked. Full per-game ledger in `graded2_full.txt`,
per-leg TSV in `on2_ledger.tsv`.

### Grade distribution (last night vs night before)

| cat | A | B | C | D | F | total | (prior night A/B/C/D/F, tot) |
|---|---|---|---|---|---|---|---|
| ATP_CHALL | 1 | 0 | 0 | 2 | 3 | 6 | 8/1/4/3/3, 19 |
| ATP_MAIN | 0 | 0 | 0 | 2 | 0 | 2 | 2/1/4/0/0, 7 |
| ITF_M | 0 | 1 | 0 | 1 | 1 | 3 | 2/3/9/8/6, 28 |
| ITF_W | 0 | 0 | 1 | 0 | 0 | 1 | 1/2/6/3/5, 17 |
| WTA_MAIN | 0 | 0 | 1 | 2 | 1 | 4 | 4/1/2/1/0, 8 |
| **TOTAL** | **1** | **1** | **2** | **7** | **5** | **16** | 17/8/25/15/14, 79 |

### Grade-vs-result monotonicity (realized $/game)

A +1.20 · B +1.25 · C +2.38 avg (CLALAM dog-luck +4.65, MERRYB +0.10) ·
D +3.50 avg excluding the +$190 manual-adoption outlier · **F −11.55 total, every F negative.**
Monotone at the tails; C/D noisy at N this small.

### Named-class counts (last night vs night before)

| class | last night | night before | read |
|---|---|---|---|
| over-par completions (comb>100) | **0** | 15 | all 4 completed pairs ≤100 (99/99/93/98) — ceiling+walk_cap consistent, sample tiny |
| par-zero-lock (zero-discount pair) | **0** | 1 | — |
| deep-negative-FV fills (fragile games) | **1** | 8 | but per-leg FV mean −5.0c / 35% pos vs +1.3c / 61% prior — the fills that DID land during the crash were disproportionately stale bids swept in-play |
| in-play chases (fill at/after gun) | **17/20 (85%)** | 77/136 (57%) | crash artifact: unmanaged bids couldn't be cancelled |
| half-arms | **12/16 (75%)** | 22/79 (28%) | 8 PAIRING + 3 STARVATION + 1 manual-orphan; see below |

**The half-arm explosion is manufactured by the crash**: the TypeError fires on the DOG
leg's anchor evaluation, so favorites placed and dogs never did → "sib never rested"
PAIRING half-arms (8 of them; prior full night had 10 in 5× the games). This is a NEW root
cause wearing a KNOWN class's jersey.

## (3) REGRESSION SWEEP — did the five new flags break an existing function?

**YES. One catastrophic, one open secondary, rest clean.**

| check | verdict |
|---|---|
| fills/day | **149 → 20** (−87%). Hourly attribution: crash landed at the exact hour the placement engine ramps. Not slate-driven. |
| pairs completed | **57 → 4** |
| events rested | 82 → 18 |
| new error classes | **2 new event types (`error`, `on_bbo_update_error`), 5,839 rows, 100% the one TypeError.** No other new error class. Singletons: `settlement_unexpected_phase` ×1, `orphan_outcome` ×1 (not seen prior night; low priority). |
| reshuffle vs ceiling | no interaction observed — `leg2_reshuffle_reaim` fired **0 times all night** (its subjects, dog legs, crashed at entry-anchor before any walk could re-aim). Reshuffle is **not validated**, it is **unexercised + guilty of the crash** (its entry branch is the crash site). |
| walk_cap vs liquid-repost | `premarket_walk_capped` ×3 (all GIUFEL-FEL: correctly clamped a 92c proposed walk to 80 = conception 77 + cap 3); `liquid_repost_at_touch` ×0 → no interaction possible. Behavior-correct where it fired. |
| grace_kill vs freeze remnants | `freeze_at_gun_hold` ×0 — freeze stayed shelved, zero remnant fires. grace armed ×5 / resting_cancel ×2 / unlatch ×17, all coherent. |
| latch_override false-fires | 0 found (5/5 spot-checked override latches were real matches). |
| per_cat_depth | no dedicated event; feeds offsets silently. Dog/sub-50 fills: 6, paid-by-dip 2, zero-discount 4 — worse than prior 68%, crash-confounded, re-measure tonight. |

**Secondary anomaly (open, pre-existing? unclear):** the late-morning July-4 ITF slate sat
with 1–2h-stale books and got `event_skip_stale_book`-skipped every sweep (27k skips
11AM–1PM, 1,237/event; prior-night per-event max 300). `ws_subscribed` 23 vs 77. Suspect
WS-subscription starvation during the crash window; not proven. Watch tonight on the fixed
build — if books stay stale on a healthy loop, this is its own incident.

Also noted: `staircase_hold_place` 83 → 938 is DIMBER's favorite leg computing a placement
target every surviving sweep pass and dying with the event before ordering — crash artifact,
not a staircase change.

## (4) NET P&L (realized, settled/exited legs in window) — mandatory format

- **Cash (Kalshi API):** $2,691.74. Portfolio value (API): $416.45.
- **Bot-log realized in window: +$189.15** = exits +$196.00 (9 legs) + settles −$6.85 (9 legs), 2 legs open at window close (both settled after).
  - **Of which $190.00 is NOT bot alpha**: KXITFMATCH-26JUL03HARNAS-NAS was an operator
    MANUAL position (7 taker fills, ~1000 sh @74c), boot-adopted, auto-exited @93c by the
    bot's exit machinery. **Bot-native realized: −$0.85** (exits +$6.00, settles −$6.85).
- **Kalshi-API reconciliation:** every ledger ticker appears in the window's API fills; the
  window settlements list matches the ledger's settled legs 1:1. Account also carries manual
  non-tennis trades (MLB, 2× WC spreads, CS2, Nathan's) — excluded. Maker fills show
  `fee_cost 0.000000`; HARNAS's 7 fills are the only tennis taker prints in the window.
- Open now (API `position_fp`): ZAMBRI-BRI 5 sh (post-restart pair, sibling exited +$0.30),
  HERPDA-PDA 5 sh (exit resting 98c), KXNATHANSHDOU-26MEN-CLEG12 250 sh (manual orphan, no
  cell config — operator's).
- Shutdown-drain note: both 12:58:55 cancels returned `success:false` — both orders were
  already filled (ZANSIE 65c booked at reboot via boot_reconcile; HERPDA already held).
  Not a cancel-410-class failure.

## (5) EVERY SUB-B GAME (one line, mechanical cause, KNOWN vs NEW)

| gr | game | mechanical cause | class |
|---|---|---|---|
| C | ITFW CLALAM | CLA engagement-join filled 25c vs onset 10c (FV −15) — fragile; got lucky, dog WON +$4.65 | KNOWN (fragile deep-neg) |
| C | WTA MERRYB | pair 98 comb settled WIN1: winner held, loser held to 0 (−$3.95) — exit-harvest asymmetry | KNOWN (FUCKUP-3, pre-existing) |
| D | ATPCH KASPIR | favorite filled, dog never rested | KNOWN symptom, **NEW root: crash-manufactured PAIRING** |
| D | ATPCH RINDIA | same | same |
| D | ATP DESVA | same | same |
| D | ATP TIABUB | same | same |
| D | WTA ANIKEY | same | same |
| D | WTA PAOSAK | same | same |
| D | ITF HARNAS | manual adoption, no sibling ever — not a bot decision | N/A (manual) |
| F | ATPCH GIUFEL | dog filled 7c, favorite grace-cancelled; **dog's own late cancel = crash** → naked, LOSS −$0.35 | KNOWN symptom (STARVATION), crash-mediated |
| F | ATPCH HEICEC | filled 70c at FV −37 **19 min after gun** on an unmanaged stale bid → naked, LOSS −$3.50; worst leg of the night | KNOWN class (deep-neg chase), crash-mediated |
| F | ATPCH MELCAS | filled 52c gun+3m, sibling starved → naked LOSS −$2.60 | KNOWN (STARVATION), crash-mediated |
| F | ITF BENAHO | dog 28c filled, sibling rested-unfilled → naked LOSS −$1.40 | KNOWN (STARVATION) |
| F | WTA EALSWI | Swiatek 74c filled, dog never rested → naked LOSS −$3.70 | crash-manufactured PAIRING |

**No new loss-class was invented by the flags themselves.** The new class of the night is
operational: *duplicate-method shadowing crash* — caught by zero tests because both defs
parse fine; the aim-dispatch tests exercised the helper directly (bound at class level the
later def wins only at instance-call time on the earlier-def call sites).

## Disposition

- 775dac33 LIVE since 13:00:02 ET. All five flags remain armed — four are either validated-
  where-fired or inert-as-designed; `leg2_reshuffle` is now actually live for the first time.
- Tonight's validation must treat 775dac33 as the flags' TRUE first night: Metric A target 0,
  reshuffle/per_cat_depth first-fire counts, FV distribution, half-arm rate vs the 28% baseline.
- Open watches: ITF stale-book anomaly; `settlement_unexpected_phase`/`orphan_outcome` singletons;
  KXNATHANSHDOU 250-sh manual orphan sitting in the account.

Artifacts: `on2_ledger.tsv` `on2_participation.tsv` `on2_agg.txt` `graded2_full.txt`
`metricAB_20260704.txt` `hourly_new.txt` `hourly_old.txt` `regress_census.txt`
`pnl_reconcile.txt` + the scripts that produced them.
