# OMQS — M-α1: PAIR-ECONOMICS REPLAY of don't-pull (2026-07-01)

**Question:** simulate the premarket bid NOT being pulled — replay the fill at each dedupped opportunity, hold both legs to settle (pair completion), and measure the recovery vs the −$43.97 naked baseline. **Ship-gate: NET recovers ≥ +$25 after the contamination filter.**

**Coverage correction (important):** including `.csv.gz` (the archive cron gzips tapes >1 day old), **all 91 stranded legs are tape-covered** — the earlier β/α (16-40 legs) were gzip-blind partial subsets. This replay is on the full 91.

## Result
Method: dedup consecutive same-level `taker_side="no"` prints into fill opportunities (cap 5 lots/pair, first-opportunity fill); pair NET = (100 − kept_entry − fill)/100·lots − taker-fee, **winner-independent** (a completed pair pays 100¢ whichever leg wins).

| framing | NET (all 91) | recovery vs −$43.97 | completions | ≤97 | 98-100 | >100 |
|---|--:|--:|--:|--:|--:|--:|
| WITHOUT contamination filter | −$11.94 | **+$32.03** | 66 | 27 | 36 | 3 |
| WITH filter (PRE-PEAK only) | −$11.94 | **+$32.03** | 66 | 27 | 36 | 3 |

**Contamination filter has no effect** — pair completion pays 100¢ regardless of which leg wins, so POST-PEAK "collapse" fills don't hurt pair economics (they buy the cheap loser leg while the held sibling wins). The filter matters only in the naked frame.

## The decomposition that matters (recovery by error-class)
| class | n | recovery | lever |
|---|--:|--:|---|
| **NEVER_LAID** | 48 | **+$26.02** | **always-lay both legs** (the money) |
| PULLED | 13 | **+$3.10** | don't-pull (small) |
| TOO_DEEP | 2 | +$2.70 | — |
| BEHIND_WALL | 3 | +$0.21 | — |
| NO_OPP | 25 | +$0.00 | no catchable dip |

**This revises the earlier print-level "95% PULLED" headline.** That was an artifact of gzip-blind partial coverage dominated by two legs. With full coverage, dedup, and per-event accounting, the dominant recoverable class is **NEVER_LAID** — the catchable winner-dip arrived *before we had any bid resting*. **Don't-pull's own recovery is only +$3.10 — it does NOT clear the +$25 gate.** Always-lay-both (+$26) does.

**And it only stanches the bleed, not turns profit:** even fully applied the cohort is **net −$11.94** (from −$43.97). Only **41% of completions clear the ≤97 good-price bar**; most (36/66) complete near par (98-100). The fix stops the naked-loser-ride; it does not make the stranded cohort +EV.

## SIEBON + DALTRA forensic (88.7% of the raw print evidence — walked individually)
Both **CLEAN — `determined` outcomes, real matches, not voids or data anomalies.**
- **SIEBON** (`KXWTAMATCH-26JUN29SIEBON-BON`, WTA_MAIN): last_trade trajectory **38→99→1** — a genuine in-play swing (BON led to near-certain, then lost). 1,571 taker-no prints → **19 dedupped opportunities**. First-opp fill 36¢ + kept 63¢ = **combined 99¢** (marginal). Both legs `determined`; SIE (kept) won → pair pays 100.
- **DALTRA** (`KXATPCHALLENGERMATCH-26JUN30DALTRA-TRA`, ATP_CHALL): trajectory **53→79→1** (TRA led then lost). 294 taker-no → **14 opportunities**. First-opp fill 51¢ + kept 45¢ = **combined 96¢** (≤97, good). Missed leg `determined`; DAL (kept) won → pair pays 100.
Neither is a retirement-void or a frozen-book artifact; the wild swings are real favorite-collapse matches. The dedup (19/14 opps, not 1,571/294 prints) is the honest opportunity count.

## Dollar magnitude = HELD-PENDING (per Plex gate)
The +$32 recovery is **directionally solid but the absolute figure is not Vault-ready:** 45/91 have full settle-pnl, 79/91 are `determined` (pair=100 valid), **12 unknown**; and the naked baseline uses *logged realized* (≈0 for unsettled kept legs), which likely **understates** the true naked loss — making +$32 if anything conservative on the baseline side. One-config-era, Jun24-30 only.

## Ship read
- **Don't-pull → SHADOW** (its own recovery +$3.10 < $25; Plex pre-set it to shadow regardless).
- **Always-lay-both → SHIPPABLE-ORTHOGONAL** (+$26, clears the bar on its own; the real lever).
- Gated further by M-α2 (does completing pairs neutralize the M2 protective-cancel cost?).

Method: `malpha1.py`.
