# CAUSAL AUDIT — every graded game, both directions (2026-07-04 night)

Population: the 16 A–F morning-ledger events + tonight's 5 (HERPDA, ZANSIE, WATSHI,
LEGWIN, ZAMBRI). Chains from both log files; results from the **fills/settlements API
(exchange truth), not the bot log**. Raw: `causal_audit.json` / `audit_rows.json` (scripts committed).

## (2) EXCHANGE TRUTH vs LEDGER — three discrepancies, one reversal

| game | ledger | exchange truth | mechanism of the hole |
|---|---|---|---|
| **MELCAS** | **F, −$2.60** "half-arm STARVATION" | **+$3.65, completed WINNING pair (52+41=93)** | **TWO unbooked fills during the crash window**: MEL's 66c exit FILLED (log then booked "settled LOSS −$2.60" against shares no longer held) and CAS's 41c entry FILLED unbooked (log's settle shows "WIN pnl 0.0" — zero booked qty). The F grade was a booking artifact, not a trading outcome. |
| TIABUB | D, $0.00 (open) | +$0.65 | exit filled post-window (booked; window cutoff, benign) |
| ANIKEY | D, $0.00 (open) | +$0.80 | same |

Also decomposed: LEGWIN event −$11.65 = operator's **manual 500-lot round-trip −$12.40**
(505 bought @48, 500 sold @46, 1 taker print) + bot LEG +$0.75; the bot's 5-sh WIN remains
open with the sweep's 49c LEG re-arm resting. WATSHI: WAT open 5 @65 (unrealized, market
`inactive` — which is also why discovery can't yet re-include SHI; the boot-repost sweep
retries every 60s and is correctly waiting). Unbooked-exit fills found tonight: LEG +$0.75
(20:05), PDA +$0.80 (15:51) — same class as MELCAS, smaller stakes.

**All 18 other games: exchange truth == ledger to the cent.** The grader wasn't sloppy —
the LOG was blind where check_fills was starved (crash) or the position was link-path
invisible (restart). Standing rule vaulted as F36: exchange truth is the only result-side
source across restarts.

## (1)+(3) THE CODE CHAINS — sub-B guilty steps (all KNOWN classes, no NEW)

Every sub-B chain traces to a named, already-diagnosed step; full per-game chains in
`audit_rows.json`:

- **GIUFEL F**: staircase post → walk (2× `premarket_walk_capped` held 80 vs 92 ✓) → latch
  09:15 → FEL grace-cancel ON TIME → GIU 7c dog cancel 26min late = **the _sibling_ticker
  crash starving on_bbo manage** (KNOWN, fixed 775dac33).
- **HEICEC F**: last_traded staircase post 70c → filled 19min AFTER gun at emfb **+21 over
  burst-FV** on an unmanaged stale bid = crash-starved cancel (KNOWN). Worst leg of the day.
- **MELCAS "F"** → **reversed by exchange truth** (see above); its actual chain — MEL
  staircase walk-down 55→50→52 fill, CAS staircase 41 dog fill on the dip, combined 93 —
  is a **working pair** the ledger couldn't see.
- **BENAHO/EALSWI/KASPIR/RINDIA/DESVA/TIABUB/ANIKEY/PAOSAK D/F half-arms**: all
  crash-manufactured PAIRING/STARVATION (KNOWN; the dog-leg TypeError). The fix table's
  three tonight-shipped mechanisms (reaim-on-arrival, boot-repost, reshuffle-no-bucket)
  did not exist during the window — none could have bitten.
- **MERRYB C**: grace cancels 9.5min late (crash) + FUCKUP-3 exit-harvest asymmetry
  (KNOWN, pre-existing).
- **LEGWIN ZT (tonight)**: adoption-blind pair checks (KNOWN as of tonight, C42, patched
  3691ff5 + boot sweep 87271a2 — the sweep's first live act re-armed LEG at 49 = 97−48 ✓).

**No NEW failure class was found by the audit.** The new classes of the day are result-side:
unbooked fills (F36) and link-path position invisibility (memory + C-REPOST v2 docstring).

## (4) A/B INVERTED — EARNED vs GIFT, and the riser-side answer

**The riser test, evidenced (15 riser legs vs 9 faller legs, bot fills only):**

- **Faller legs: mean +8.7c below window-open, 7/9 with real discount** (ZANSIE +29,
  GIUFEL +18, ORLPOP +16, BENAHO +7, CLALAM +6…). The aim-depth mechanism demonstrably
  pays: the dip comes to the resting level. **EARNED class exists and lives on the faller
  side.**
- **Riser legs: mean +1.6c below window-open — 13/15 within the 1–2c placement offset.**
  That is not dip capture; it is the table's own token offset. And burst-FV says the fills
  are **adversely selected**: of 11 risers with emfb, **8 paid ABOVE burst-FV** (HEI +21,
  MEL +15.5, DIA +15.5, LAM +13, PIR +12.5, HEM +8.5, RYB +5…) — a riser bid fills
  precisely when its leg fades toward it. **Said plainly: with riser_post≈0, half the book
  is zero-discount BY DESIGN, and its fills carry negative selection. Every green riser
  outcome in this ledger is the tape recovering, not the mechanism earning. This is the
  aim table's next revision, evidenced: the riser side needs either a real offset or an
  explicit accept-the-concession annotation with the adverse-selection cost priced in.**

**Stamps (per game, green outcomes):**

| game | grade | stamp | why |
|---|---|---|---|
| HEMMOE +1.20 | A | **MIXED** | MOE faller EARNED (emfb −9.5, bought under FV); HEM riser conceded (+8.5 over FV, token +2 disc) — the pair's earned cent is the faller's |
| ORLPOP +1.25 | B | **MIXED** | ORL dip-capture EARNED (+16 vs open); POP completion-repriced 13c ABOVE its open (completion path, ceiling-legal) |
| CLALAM +4.65 | C | **EARNED entry / GIFT size** | CLA bought **19c under burst-FV** (the board's best entry — the morning's "fragile" verdict used the ambiguous candle gun and is corrected); the +$4.65 size is dog-settle luck |
| MERRYB +0.10 | C | **GIFT** | both mechanisms failed (late cancels, unfilled exits); survived by WIN1 symmetry |
| KASPIR/RINDIA/DESVA/PAOSAK/TIABUB/ANIKEY (+0.65…+0.95) | D | **GIFT ×6** | naked singles, 4/6 filled above burst-FV, all rescued by tape direction |
| MELCAS +3.65 | F→(A-class) | **EARNED** | completed 93-pair, both legs mechanism-priced; the only pair on the board where both sides worked |
| ZANSIE +1.90 / ZAMBRI +1.90 / HERPDA +1.05 (tonight) | n/a | **EARNED-leaning** | faller discounts +29/+1/+0 with real exits landed |

## (5) THE VERDICT TABLE — causal-step distribution per grade

| grade | games | EARNED | MIXED | GIFT | note |
|---|---|---|---|---|---|
| A | 1 | 0 | 1 | 0 | **the A is HALF-earned: its earned cent is the faller leg; the riser leg conceded by design** |
| B | 1 | 0 | 1 | 0 | same shape |
| C | 2 | 1 (entry) | 0 | 1 | CLALAM's entry is the day's best mechanism print |
| D green | 6 | 0 | 0 | **6** | **every positive D is a GIFT — say it loudly: the tape, not the code, paid them** |
| F | 5 | 1 (MELCAS, reversed) | 0 | 0 | the other 4 F's are honest mechanism-failure losses |

The clean split: **everything EARNED on this board came from a faller leg filled below its
open/FV. Nothing EARNED came from a riser leg. The doctrine's money-making mechanism is
the faller dip; the riser side currently contributes exposure, not edge.**

## (6) STANDING

Every future ledger row now carries `stamp` (EARNED / GIFT_CLASS / MIXED / PENDING),
`side`, `disc_vs_open`, and `chain` — implemented in the live monitor's fill grading and
rendered as the LIVE_STATUS stamp column. Future overnight ledgers use `causal_audit.py`
(chains + exchange truth) as the standing result-side pass; the RUNBOOK inherits it.

## POSTSCRIPT (21:15 ET) — live wart found while closing the audit: RESHUFFLE-WALK CHURN

The LEG 49c re-arm survived 13 minutes. The chain (21:55-21:07 log): every ~70-130s the
walk proposed moving LEG up toward the touch (50-55c), `leg2_reshuffle_reaim` capped it
back to 49 (**the bound HELD on every single cycle — the mechanism works**), but the
repost path executed a cancel+repost AT THE SAME 49c — ~10 round-trips, queue priority
burned each time — until `v4_cancel_bid_marketable_stale` killed the bid entirely at
21:07:44. No repost since (the boot sweep's once-per-event guard, by design). Net: WIN
5-sh sits single again, and the pair's passive completion path is gone until the next
restart or manual re-arm.

NEW class, named: **reshuffle-walk churn** — when the re-aim resolves to the CURRENT
resting price, the repost must be suppressed (hold FIFO), and a reshuffle-pinned bid
should be exempt from the marketable-stale kill (its price is doctrine-pinned, not
stale). Next dispatch's patch candidate; zero doctrine risk meanwhile (bound never
breached; the cost is queue priority + a lost completion bid).