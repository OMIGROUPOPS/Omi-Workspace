# PAIR-STORY HOURLY APPENDIX — the floor by hour, two conventions (2026-07-07)

Same 2,457-pair universe and honest axis as `PAIR_STORY_20260707.md`; one tick re-pass (producer `analysis/floor_by_hour_20260707.py`, detached+watcher; per-pair rows `/root/pair_story_20260707/results_hourly.jsonl`; aggregates `hourly.json`, plot `hourly_floors.png`). Per (cat, hour-bin T-8h→bell): **(a) prints-only joint floor** (ratified conservative: min joint fillable, trailing-15min print convention) vs **(b) QUOTE-TOUCH joint floor** (min joint mid-sum the books actually quoted — NON-CONSERVATIVE, labeled; a mid is not a fill). The (a)−(b) gap per bin is the wide-spread-no-prints regime, measured not assumed.

## 1 · COVERAGE FIRST — the thin-early caveat, quantified

| cat | T-8..T-7 cov% (tick-min med) | T-5..T-4 | T-2..T-1 | T-1..bell |
|---|---|---|---|---|
| ITF_M | 64.2% (15) | 76.2% (23) | 92.8% (32) | 99.4% (50) |
| ITF_W | 63.0% (14) | 78.6% (23) | 91.8% (28) | 98.7% (48) |
| ATP_CHALL | 79.2% (13) | 85.2% (15) | 97.9% (25) | 99.5% (44) |
| WTA_CHALL | 100% (10) | 86.7% (11) | 96.7% (20) | 100% (40) |
| ATP_MAIN | 93.6% (34) | 93.6% (35) | 98.4% (38) | 99.5% (44) |
| WTA_MAIN | 94.2% (28) | 96.9% (28) | 99.6% (35) | 99.6% (45) |

Early ITF bins rest on ~2/3 of pairs at ~15 quoted-minutes/hour — thin, stated. The early-bin verdicts below are nonetheless unambiguous in DIRECTION (quotes at par + zero prints); they are not fragile to the missing third.

## 2 · THE FLOOR PER BIN, (a) vs (b) — full per-cat tables

(jf_any% = share of covered pairs with ANY joint print-fillable moment in the bin; jf/jm = median floors; gap = (a)−(b) med.)

**ITF_M** — prints/min are LITERALLY ZERO until T-3h:

| bin | jf_any% | (a) jf med | (b) jm med | gap | spread | prints/min |
|---|---|---|---|---|---|---|
| T-8..T-7 | 6.7 | 99 | 98.5 | +2.0 | 5.5 | 0.00 |
| T-7..T-6 | 10.2 | 101 | 99.0 | +2.0 | 5.0 | 0.00 |
| T-6..T-5 | 12.7 | 100 | 99.0 | +2.5 | 4.5 | 0.00 |
| T-5..T-4 | 13.1 | 101 | 99.0 | +2.0 | 4.0 | 0.00 |
| T-4..T-3 | 18.4 | 101 | 99.0 | +2.5 | 4.0 | 0.00 |
| T-3..T-2 | 26.7 | 101 | 99.0 | +2.5 | 4.0 | 0.02 |
| T-2..T-1 | 58.5 | **97** | 98.0 | 0.0 | 3.5 | 3.13 |
| T-1..bell | 97.6 | **84** | 94.5 | **−9.0** | 1.5 | 82.9 |

**ITF_W** — same shape: jf_any 5→98%, (a) 100→**86**, (b) 99→95.5, gap +2.5→**−8.0**, spread 5→1.5, ppm 0→78.9.

**ATP_CHALL** — jf_any 15→96%, (a) 101→**93**, (b) 99.5 flat→98.0, gap +1.5→**−4.0**, spread 2→1, ppm 0.1→64.7.

**WTA_CHALL** (n=29-30/bin, LUCK-POLLUTED) — same: (a) reaches 90 only in the last hour; (b) 99.5-100 until then.

**ATP_MAIN** — the hypothesis bins, stated in full:

| bin | jf_any% | (a) jf med | (b) jm med | gap | spread | prints/min |
|---|---|---|---|---|---|---|
| T-8..T-7 | 72.6 | 101 | **100.0** | +1.0 | 1.0 | 5.7 |
| T-7..T-6 | 75.0 | 101 | 100.0 | +1.0 | 1.0 | 6.7 |
| T-6..T-5 | 76.8 | 100 | 100.0 | +0.5 | 1.0 | 7.1 |
| T-5..T-4 | 74.3 | 100 | 100.0 | +1.0 | 1.0 | 8.2 |
| T-4..T-3 | 84.6 | 101 | 100.0 | +1.0 | 1.0 | 8.6 |
| T-3..T-2 | 83.0 | 101 | 100.0 | +0.5 | 1.0 | 15.0 |
| T-2..T-1 | 88.6 | 100 | 100.0 | 0.0 | 1.0 | 19.7 |
| T-1..bell | 96.2 | 100 | 100.0 | 0.0 | 1.0 | 46.0 |

**WTA_MAIN** — (b) med **100.0 in every bin** until 99.5 in the last hour; (a) 101→99; spread 1¢ flat.

## 3 · SPREAD + PRINT-RATE CURVES (the stability/liquidity story)

- **ITF**: spread walks 5.5→4→3.5→1.5¢ across the window while prints/min sit at **0.00 until T-3h**, 3/min at T-2..1, ~80/min in the last hour. The early ITF book is a wide, silent quote lattice — it trades essentially never.
- **CHALL**: spread ~1.5-2¢ all day; prints wake at T-3h (ATP) — liquidity arrives with the slate, not the match, until the final convergence.
- **MAINS**: spread 1¢ and prints flowing (3-9/min) from T-8h — the mains are LIQUID all day; they are simply liquid AT PAR.

## 4 · VERDICT LINES (feeding the pre-T-4h posting spec + the mains go/no-go)

- **ITF_M / ITF_W: the early canvas does NOT offer what the late one does — under EITHER convention.** Early (a) is empty (jf_any 5-13%, and the rare early prints are at par+ — anti-selection, someone crossing a wide book); early (b) quotes ~99 mid behind 4-5¢ spreads, so even lifting the early book at midline buys par. The wide-spread-no-prints regime hides NOTHING here. **The whole ITF floor (84/86) is a T-2h→bell phenomenon, overwhelmingly T-1h.** Pre-T-4h spec implication: early posting buys POSITION (queue, lifecycle, being present when the window opens) — it cannot buy early FILLS at discount, because there are no prints to fill against. The "≤97 achievable 90-96% pre-T-4h" thesis line should be read as *achievable by bids resting from pre-T-4h*, not *fillable pre-T-4h*.
- **ATP_CHALL: same shape, milder** — (a) floor reaches 93 only in the last hour; nothing early under either convention (gap +1 to +1.5). Early posting = position only.
- **WTA_CHALL: same, n<30 provisional.**
- **MAINS GO/NO-GO: NO-GO.** The mains-early hypothesis is **REFUTED**: ATP_MAIN's quote-touch floor is **100.0 flat in every bin T-8→T-1** (WTA_MAIN identical to 99.5 last-hour) — the early mains canvas offers nothing below par even in quote space, with 1¢ spreads and steady prints, i.e., a liquid book that has simply priced the pair at par all day. (a) does not "stay empty while (b) improves" — (b) never improves. No convention rescues a sub-97 mains pair pre-bell; the PAIR_STORY S-line for mains (≤93, top-decile tail) stands as a rarity-hunt, not a window.

*Re-verification: rides the PAIR_STORY cadence (re-run as observed_starts coverage grows).*
