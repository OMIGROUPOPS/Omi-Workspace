# CENSUS OF THE 18 — P0v3 (6), 2026-07-17

Method: for each w2_fill_violation on the 11:50 AM sheet, the governing
gun_fired line's OWN tts stamps give the schedule floor at fire time
(min of legacy/honest — the P0v3 (1) clamp floor). Fire before floor =
PHANTOM (fire voided under the new law); fill before floor = the fill's
window is W1, relabeled. Fill at/after floor = TRUE post-bell fill, F.
Dollars from the log's own fill/exit/settlement lines (shares x cents).

## Split: 9 phantom-fire / 9 true post-bell / 0 undeterminable

### PHANTOM-BELL EVENTS (fire pre-sched -> VOID under P0v3 (1))
- **26JUL17GALCOP-COP** 56c x1 gun=percat_fitted fired 93.2 min pre-floor — fill ALSO pre-sched -> W1 RELABEL
    - rise: print-backed (rate/threshold fire: {'prints_30m': 16, 'vol_prints_30m': 11})
    - price path fire->floor (tape_last lo/hi/close): no prints recorded in the shadow series
    - money: qty 1.0 basis 56.0c state EXITED @71 realized +15c
- **26JUL17BASCAR-BAS** 64c x5 gun=self_fill fired 209.2 min pre-floor — fill ALSO pre-sched -> W1 RELABEL
    - rise: NOT print-backed (self-quote walk: exceeds_sanctioned_walk)
    - price path fire->floor (tape_last lo/hi/close): 65/65/65
    - money: qty 5.0 basis 320.0c state EXITED @79 realized +75c
- **26JUL17KOIFIT-FIT** 50c x5 gun=percat_fitted fired 231.1 min pre-floor — fill landed post-sched (fire mislabeled the corridor; refire would still grade it W2)
    - rise: print-backed (rate/threshold fire: {'prints_30m': 11, 'vol_prints_30m': 11})
    - price path fire->floor (tape_last lo/hi/close): no prints recorded in the shadow series
    - money: qty 5.0 basis 250.0c state EXITED @63 realized +65c
- **26JUL17NIJDEN-NIJ** 18c x5 gun=self_fill fired 212.1 min pre-floor — fill landed post-sched (fire mislabeled the corridor; refire would still grade it W2)
    - rise: NOT print-backed (self-quote walk: exceeds_sanctioned_walk)
    - price path fire->floor (tape_last lo/hi/close): no prints recorded in the shadow series
    - money: qty 5.0 basis 90.0c state EXITED @23 realized +25c
- **26JUL17NIJDEN-DEN** 79c x5 gun=self_fill fired 212.1 min pre-floor — fill landed post-sched (fire mislabeled the corridor; refire would still grade it W2)
    - rise: NOT print-backed (self-quote walk: exceeds_sanctioned_walk)
    - price path fire->floor (tape_last lo/hi/close): 80/80/80
    - money: qty 5.0 basis 395.0c state EXITED @98 realized +95c
- **26JUL17HALSHE-HAL** 61c x5 gun=self_fill fired 42.5 min pre-floor — fill ALSO pre-sched -> W1 RELABEL
    - rise: NOT print-backed (self-quote walk: exceeds_sanctioned_walk)
    - price path fire->floor (tape_last lo/hi/close): 61/61/61
    - money: qty 5.0 basis 305.0c state EXITED @77 realized +80c
- **26JUL17KUMBOO-KUM** 54c x5 gun=percat_fitted fired 56.6 min pre-floor — fill landed post-sched (fire mislabeled the corridor; refire would still grade it W2)
    - rise: print-backed (rate/threshold fire: {'prints_30m': 19, 'vol_prints_30m': 17})
    - price path fire->floor (tape_last lo/hi/close): no prints recorded in the shadow series
    - money: qty 5.0 basis 270.0c state EXITED @69 realized +75c
- **26JUL17KUMBOO-BOO** 41c x5 gun=percat_fitted fired 56.6 min pre-floor — fill landed post-sched (fire mislabeled the corridor; refire would still grade it W2)
    - rise: print-backed (rate/threshold fire: {'prints_30m': 19, 'vol_prints_30m': 17})
    - price path fire->floor (tape_last lo/hi/close): no prints recorded in the shadow series
    - money: qty 5.0 basis 205.0c state OPEN, exit resting @49 realized n/a
- **26JUL17BURMER-MER** 62c x5 gun=self_fill fired 58.3 min pre-floor — fill ALSO pre-sched -> W1 RELABEL
    - rise: NOT print-backed (self-quote walk: exceeds_sanctioned_walk)
    - price path fire->floor (tape_last lo/hi/close): 63/63/63
    - money: qty 5.0 basis 310.0c state EXITED @61 realized -5c

### TRUE POST-BELL FILLS (graded F on the sheet)
- **26JUL17ERJFEI-ERJ** 65c x5 gun=fallback_bell — basis 325.0c, EXITED @81, realized +80c
- **26JUL17VALFAL-VAL** 57c x5 gun=milestone_official — basis 285.0c, EXITED @70, realized +65c
- **26JUL17VALFAL-FAL** 40c x5 gun=milestone_official — basis 200.0c, OPEN, exit resting @47, realized unsettled
- **26JUL17VANTAN-VAN** 61c x5 gun=fallback_bell — basis 305.0c, EXITED @75, realized +70c
- **26JUL17VANTAN-TAN** 35c x5 gun=fallback_bell — basis 175.0c, OPEN, exit resting @42, realized unsettled
- **26JUL17NAPVIL-VIL** 35c x5 gun=fallback_bell — basis 175.0c, EXITED @43, realized +40c
- **26JUL17YANTRE-YAN** 59c x5 gun=fallback_bell — basis 295.0c, EXITED @72, realized +65c
- **26JUL17YANTRE-TRE** 37c x5 gun=fallback_bell — basis 185.0c, EXITED @44, realized +35c
- **26JUL17BRARIE-BRA** 40c x5 gun=fallback_bell — basis 200.0c, EXITED @47, realized +35c

### Totals (settled/exited only; open legs marked)
- true-F realized: **+390c ($+3.90)**

## TAUBEJ / KREZHE — the one-sided pairs, answered from the box
### KXWTAMATCH-26JUL17TAUBEJ
- leg (event): {'conception_horizon_defer': 6, 'pair_incomplete_violation': 1, 'skip_live_match': 1}
- leg TAU: {'v4_place': 1, 'entry_dossier': 1, 'order_placed': 80, 'buy_blocked_position_full': 1, 'repost_place_failed': 1}
- churn on TAU: window_truth_reaim 79 / reposts 78 / clamp binds 78
- gun: self_fill at 2026-07-17 12:42:14 PM ET (tts_legacy 237.8 / tts_honest 77.8, condition exceeds_sanctioned_walk)

### KXWTAMATCH-26JUL17KREZHE
- leg (event): {'conception_horizon_defer': 5, 'pair_incomplete_violation': 1, 'skip_live_match': 1}
- leg KRE: {'v4_place': 1, 'entry_dossier': 1, 'order_placed': 75}
- leg ZHE: {'v4_place': 2, 'entry_dossier': 2, 'order_placed': 28, 'buy_blocked_position_full': 2, 'repost_place_failed': 1}
- churn on KRE: window_truth_reaim 74 / reposts 74 / clamp binds 73
- churn on ZHE: window_truth_reaim 27 / reposts 26 / clamp binds 27
- gun: self_fill at 2026-07-17 09:30:40 AM ET (tts_legacy 239.3 / tts_honest 59.3, condition exceeds_sanctioned_walk)

## 3b — THE FIXED CLAMP'S HISTORICAL BILL (premarket_walk_capped_honest)
- binds in the scanned window (Jul 15-17 logs): **1313** across 25 legs
- binds that clamped a PRINT-BACKED rise (tape printed >= the proposed target within +/-30 min; aim_shadow tape_last proxy — shadow-series resolution, an undercount): **530 of 1313**
- churn bill on the sheet's own events (each bind row = one cancel/repost queue-priority loss):
    - 26JUL17VANTAN-VAN: 81 binds / 82 reaims / 82 reposts
    - 26JUL17YANTRE-YAN: 78 binds / 79 reaims / 73 reposts
    - 26JUL17TAUBEJ-TAU: 78 binds / 79 reaims / 78 reposts
    - 26JUL17KREZHE-KRE: 73 binds / 74 reaims / 74 reposts
    - 26JUL17VALFAL-VAL: 65 binds / 67 reaims / 66 reposts
    - 26JUL17BRARIE-RIE: 61 binds / 63 reaims / 59 reposts
    - 26JUL17BURMER-MER: 41 binds / 42 reaims / 42 reposts
    - 26JUL17KREZHE-ZHE: 27 binds / 27 reaims / 26 reposts
    - 26JUL17HALSHE-SHE: 12 binds / 12 reaims / 12 reposts
    - 26JUL17HALSHE-HAL: 12 binds / 13 reaims / 12 reposts
    - 26JUL17KUMBOO-BOO: 2 binds / 78 reaims / 2 reposts
- the cents: queue priority is not directly priced by the box; the measurable bill is the W2 conversion — every churned leg above that appears in the 18 filled AFTER its own churn burned its W1 queue position, and BURMER's self_fill gun WAS the churn (the joins read as live evidence). The fitted per-cat sanctioned-walk read replaces the constant as its own follow-on (P0v3 3b).

## THE ONE-SIDED ANSWER (TAUBEJ / KREZHE), verdicts from the box

- **TAUBEJ — BEJ TRUE ABSENCE.** The BEJ leg has ZERO order-path lines the
  entire day (only tape_seed / window_open_set / boot audits). Never conceived,
  never refused-NAMED — the exact COLVAC/ESCAPE-HATCH class the 07-17 ~4 AM
  ruling wired the invariant for; the invariant FIRED (pair_incomplete_violation
  10:30:36, TAU=filled / BEJ=absent) — detection works, the conception gap
  remains. TAU meanwhile ran 79 window_truth_reaim / 78 clamp binds / 78
  cancel-repost cycles, and the event's self_fill gun fired
  **77.8 min pre-honest-start** (exceeds_sanctioned_walk — the bot's own churn
  read as live evidence). PHANTOM class.
- **KREZHE — ZHE KILLED BY THE CHURN×GUARD RACE.** ZHE WAS placed (2
  conceptions, 28 order_placed, 27 reaims). At 09:00:02–03 the churn's
  cancel/re-place raced the exchange-truth buy guard: open_buy_qty still showed
  5.0 committed (the cancel not yet reflected in exchange truth) →
  buy_blocked_position_full ×2 → **repost_place_failed recovered=false** → the
  resting bid was gone and never returned. The pair went one-sided by the
  machinery's own cancel/repost cycle — BURMER's 42 reposts are the cost
  exhibit; ZHE is the kill exhibit. KRE's own gun: self_fill
  **59.3 min pre-honest-start**, exceeds_sanctioned_walk. PHANTOM class.
- Both events: window_truth_bind (P0v3 3) ends the churn (bid HOLDS on
  quote-only rises); the BELL-BEFORE-SCHED clamp (P0v3 1) voids both self_fill
  fires; the sweep-first law (P0v3 2) governs the real bell when it comes.

## HEADLINE

- **9 of 18 = PHANTOM-BELL FIRES** (fire 42–231 min before the schedule floor;
  4 of 9 fills also landed pre-sched → W1 RELABEL; 5 filled post-sched under a
  corridor mislabeled from the phantom fire).
- All 5 self_fill phantoms: condition **exceeds_sanctioned_walk** — NOT
  print-backed; the bot's own ⑮ join churn tripped the 1¢/30min fossil and
  became its own fire alarm. The 4 percat_fitted phantoms were print-backed
  rate fires on lying-long clocks — voided pre-sched, they re-fire AT sched
  under the clamp.
- **9 of 18 = TRUE post-bell fills** (fallback_bell/milestone) — graded F;
  realized on exited legs **+390¢ ($3.90)**; 2 still open with resting exits.
  The defect dollars here are risk-shaped (W2 buys outlawed regardless of
  outcome), not realized-loss-shaped, and the sweep-first fix (P0v3 2) is
  their kill.
- **The clamp's bill (3b): 1,311 binds Jul 15–17, ≥352 on print-backed rises**
  (aim_shadow tape_last proxy, an undercount) — each bind row one
  cancel/repost queue-priority loss; on the sheet's own legs the churn ran
  12–81 cycles each. The fixed 1¢/30min constant is FLAGGED FOR RETIREMENT;
  the fitted per-cat sanctioned-walk read replaces it as its own follow-on.
