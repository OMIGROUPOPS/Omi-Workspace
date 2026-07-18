# PHASE B — THE RANGE SPECTRUM, population census v2 (ITF folded in)

pairs are ONE object; per-cat HARD partition; tick_src stamped per pair (snapshots poll-cadence for mains/CHALL; premarket_ticks for ITF — RECENT-ERA ONLY, the pre-Jul-11 ITF archive died in the disk-hygiene pruning, counted never padded).

- ATP_CHALL: pairs 3038 · complete-pairs 2994 · legs ranged 6008
- ATP_MAIN: pairs 1097 · complete-pairs 1055 · legs ranged 2111
- ITF_M: pairs 154 · complete-pairs 122 · legs ranged 266
- ITF_W: pairs 138 · complete-pairs 117 · legs ranged 253
- WTA_CHALL: pairs 721 · complete-pairs 709 · legs ranged 1423
- WTA_MAIN: pairs 1104 · complete-pairs 1054 · legs ranged 2109
- **TOTAL legs ranged: 12170**

## RE-CUT ON UPGRADED EDGES (post milestone promotion, 07-17 night)
- 104 events promoted to `official_actual_milestone`; full re-cut: **12,170
  legs ranged / 6,051 pairs** (ATP_CHALL 6,008 · mains 4,220 · WTA_CHALL
  1,423 · ITF 519 recent-era).
- SOURCE CAVEAT, named: volume texture is per-source — snapshots count
  traded-poll density (mains/CHALL), premarket_ticks count book-row density
  with last_trade set (ITF). The HARD per-cat partition means no cross-source
  pooling can occur by construction.

## ACCEPTANCE WALK — KXITFWMATCH-26JUL17BUCKRU (today, from the spectrum)
One pair, one object, the seesaw signature intact:
- **KRU (fav)**: anchor 88 (`last_before_t8`) → **GRIND** +4 to close 92;
  low 86 @T−6.4h; spread_med 3¢; woke T−7.8h.
- **BUC (dog)**: anchor 17 → **LATE-COLLAPSE** −11 to close 6; low AT the
  right edge (T−0); same wake.
- seesaw corr **−0.212** on overlapping prints; right edge = tick-onset
  28 seconds after the honest sched (`onset_ticks_est`, estimate-grade,
  clamped ≥ sched). The pair reads as one story: the favorite ground up
  while the dog bled out into the bell — never two orphans.

## THE COHORT SURFACE (Phase C seed, built from this spectrum)
- 42 cells (per-cat × side × anchor bucket), 16 thin (<30) — thin says
  thin. **FITTED WALK RATES (P0v3-3b fulfilled): ATP_MAIN 1.07 ·
  WTA_MAIN 1.16 · ATP_CHALL 1.10 · WTA_CHALL 1.00 · ITF_M 0.81 · ITF_W
  0.56 ¢/30min (p75, grind-up legs)** — the 1¢/30min constant dies by
  evidence and is largely VINDICATED for mains/CHALL; the ITF honest-anchor
  caps (14–20¢) were the real fiction. **KINSHIP: NO-BORROW, both ITF cats**
  (tolerance failed on floor-passing cells — the receipt rules; no ceremony).
