# Overnight Validation — 2026-07-03

**Window:** live boot **22:09:10 ET Jul 2** → 13:36 ET Jul 3 (6 restarts on the Jul-2 evening; final live boot on HEAD `9afd572`, config `deploy_v5_live.json`).
**Flags armed this window:** `tape_gated_abandon=T`, `per_side_placement=T`, `inside_buffer_off=F` (held), completion trio (`all_cells`/`combined_ceiling`/`reprice`)=T, `kalshi_occ_observe=T` (observe-only).
**Bot untouched** — all reads via Kalshi API + bot log `logs/live_v3_20260702.jsonl`. Harness: `overnight_ledger.py` + `grade.py`.

**Headline:** net realized **−$7.30** (exit-sells **+$50.70**, settlement-on-held **−$58.00**; 128 resolved legs, **8 still open** all carrying exits above fill). FV-capture **+1.3¢ mean / 61% bought under fair value**. The night's two dollar-bleeders are **both pre-existing structural classes, not the newly-armed participation flags**.

---

## (1) PARTICIPATION SWEEP

| cat | tracked | rested | ≥1 fill | pair-fill |
|-----|--------:|-------:|--------:|----------:|
| ATP_CHALL | 20 | 20 | 19 | 14 |
| ATP_MAIN | 16 | 8 | 7 | 7 |
| WTA_MAIN | 16 | 8 | 8 | 7 |
| ITF_M | 78 | 29 | 28 | 17 |
| ITF_W | 63 | 17 | 17 | 12 |
| **TOTAL** | **193** | **82** | **79** | **57** |

**Trajectory: 1.5/8 → 19 → tonight 79 games with ≥1 fill / 57 pairs filled.** A 3–4× step over the "19" baseline. (No persisted artifact for "last night's count" — anchored to the operator-stated trajectory.)

- **ATP_CHALL is the engine:** 20/20 tracked→rested, 14 clean pairs. **Full participation.**
- **Main tour is deliberately selective:** ATP_MAIN & WTA_MAIN each rested 8 of 16 tracked (half). Not a failure — main-tour markets are thinner/richer; the bot correctly declines the ones it can't get maker edge on.
- **ITF is where volume AND the fragile tail both live:** ITF_M rested 29/78, ITF_W 17/63. The marginal games participation *added* are disproportionately the ITF fragile/over-par shapes (see §4).

**Net read:** the participation objective is decisively met. The cost is that the added volume is tail-heavy in ITF.

---

## (2) A–F LEDGER — grade distribution (79 games)

| cat | A | B | C | D | F | total |
|-----|--:|--:|--:|--:|--:|------:|
| ATP_CHALL | 8 | 1 | 4 | 3 | 3 | 19 |
| ATP_MAIN | 2 | 1 | 4 | 0 | 0 | 7 |
| ITF_M | 2 | 3 | 9 | 8 | 6 | 28 |
| ITF_W | 1 | 2 | 6 | 3 | 5 | 17 |
| WTA_MAIN | 4 | 1 | 2 | 1 | 0 | 8 |
| **TOTAL** | **17** | **8** | **25** | **15** | **14** | **79** |

**Entry timing vs both clocks:** 136/136 filled legs were **placed before scheduled start** (100% disciplined premarket posting — zero entry-chasing). Of the fills, **59 printed before the tape gun, 77 at/after it** — i.e. 57% filled on the in-play dip after the resting premarket bid survived to the gun. FV-capture on those is net-positive, so the "hold-to-tape, fill the dip" thesis is behaving as designed.

Full per-game table with FV_CAPTURE (per leg), forfeited-¢, and named error → `graded_full.txt`. Per-leg TSV → `on_ledger.tsv`.

**Calibration note:** grade C is strict — it includes marginal **combined-101–103¢** pairs (fee-level over-par) alongside genuine fragile shapes. The D-band "structurally doomed" pairs are the real blowups (combined 109–153¢).

---

## (3) FIX SCORECARD — did each flag's error class shrink?

| flag / class | metric this window | verdict |
|---|---|---|
| **tape_gated_abandon** (schedule-killed markets) | `match_live_cancel = 0`; `schedule_abandon_deferred = 9384` (all `tape_not_live`); 6 `match_live_resting_cancel` that **correctly fired on real tape** | **PASS.** Zero pre-tape premature kills (the FERCER class). Bids held through schedule-T0 and were cancelled only when tape actually went live. |
| **per_side_placement** (zero-discount fills) | dog/sub-50 fills **78** → **53 PAID by a dip (FV>0, 68%)**, 25 zero-discount (FV≤0). ATP_CHALL/ATP_MAIN **79% bought under FV**; ITF_W **negative** mean FV | **PARTIAL PASS.** The deepened dog bids are paid by dips for ATP. **Fails in ITF_W** (fills land above tape onset). |
| **never-rested games** | 82/193 rested; residual "sibling never rested" = **10 games, −$1.00** (all penny-longshot partners) | **LARGELY ADDRESSED.** No tracked ATP/WTA pair went entirely un-bid; residual is tiny-dollar ITF longshots. |
| **half-armed pairs** | **22 events** single-leg-filled = 12 STARVATION (sib rested, walled out) + 10 PAIRING (sib never rested) | **NOT shrunk by these flags.** The STARVATION half (−$13.60) is the wall-queue problem, outside the participation-flag domain. |

**`kalshi_occ_observe`:** observe-only, 730 `kalshi_occ_delta` + 57 observe fires logged, **0 behavior change** (as staged). Ready to measure/arm as a separate step.

---

## (4) EVERY GAME BELOW B — mechanical chains

Full one-line chains per game in `graded_full.txt`. **Rolled up by named-error domain (54 below-B games):**

| games | net $ | domain | owner |
|------:|------:|--------|-------|
| 15 | −2.00 | **combined>100 over-par** (both maker bids filled rich, sum > par) | entry-pricing / per_side leak |
| 12 | **−13.60** | **half-armed STARVATION** — partner bid rested but sat behind a wall, orphan rode naked to settle | wall-queue (pre-existing) |
| 10 | −1.00 | half-armed PAIRING — sibling never rested (penny longshots) | pairing (small) |
| 8 | **−13.75** | **exit-harvest FUCKUP-3** — combined-≤100 pair, exit-band sold the winner and **held the loser to 0** | exit logic (pre-existing) |
| 8 | +2.20 | fragile leg (bought above tape onset, but recovered via band exit) | per_side / ITF |
| 1 | +1.30 | zero-discount pair | per_side |

**The two things that actually cost money tonight are NOT the newly-armed flags:**
1. **Exit-harvest directional bleed (FUCKUP-3), −$13.75 / 8 games.** Combined-≤100 pairs where holding *both* to settle nets ~0, but the exit-band cashed the rising winner at +band and left the falling loser to settle at zero. Examples: JODMOC (−$3.40 net, held JOD to −$3.75), STRMED (−$3.80), BASCEC/JUSWAL/KENWAT (each ~−$0.85). Remedy is the known one: hold-both-to-settle / stop-loss the loser on directional reads — **not** an entry change.
2. **Half-armed STARVATION, −$13.60 / 12 games.** NEDSMI (−$6.70) is the worst: leader filled 67¢, partner rested but never cleared the wall, single rode to settle-loss. Same queue-starvation as the join-trial nights. Untouched by tonight's flags.

**The over-par class (15 games, combined>100)** is the one adjacent to `per_side_placement`: two independent maker bids both fill at prices summing over par (SLAMUN 153¢, KABNGU 127¢, LOPCLA 126¢ — all ITF). Net only −$2.00 because band exits recover most, but it's real tail risk and worth a combined-cap on the *entry* side (the ceiling today only governs completions).

---

## FV_CAPTURE distribution (per category)

FV_CAPTURE = (leg price at tape onset − our fill); + = bought under fair value. Onset = gun latch, fallback last-trade-before-scheduled.

| cat | N | min | p50 | mean | max | %pos |
|-----|--:|----:|----:|-----:|----:|-----:|
| ATP_CHALL | 33 | −13 | 2 | **+2.1** | 19 | **79%** |
| ATP_MAIN | 14 | −1 | 1 | **+2.8** | 27 | **79%** |
| ITF_M | 45 | −56 | 2 | +3.3 | 74 | 56% |
| ITF_W | 29 | −48 | 0 | **−3.7** | 21 | 48% |
| WTA_MAIN | 15 | −2 | 0 | +1.7 | 23 | 47% |
| **ALL** | **136** | −56 | 1 | **+1.3** | 74 | **61%** |

**Synergy (pairs both-filled): 19 STRONG (both legs +FV, combined ≤100) · 20 FRAGILE (≥1 leg deep-negative) · 18 mixed.**
- STRONG shape is an **ATP phenomenon** — nearly every ATP_CHALL/ATP_MAIN pair (COMRIN, COUHEM, GIUMAR, HURPAU…).
- FRAGILE shape is an **ITF phenomenon** — nearly every deep-negative pair is ITF_M/ITF_W (ZIEHER −56, SLAMUN −48/−39, VANBUC −26, KABNGU −28). This is the same population as the over-par and starvation classes: **ITF is structurally where the deepened per-side bids fill above the tape and the pairs go over par.**

> The FV column is reported alongside grades but does **not** move the A–F letters this run, per instruction.

---

## Bottom line
- Participation flags did their job: **schedule-kill class → ~0**, **per-side dip-capture 68%** (79% in ATP), participation **3–4× the baseline**.
- The residual loss is **old structure** — exit-harvest (FUCKUP-3) and wall-starvation — surfaced *more* only because participation is up.
- **The lever for next step is ITF-specific:** ITF is where fragile / over-par / starvation all concentrate. Options: an entry-side combined-cap (kills over-par), hold-both-to-settle on directional pairs (kills FUCKUP-3 bleed), and a walled-queue skip for ITF (kills starvation singles). None require touching the ATP book, which is clean.
