# PART 3 — CLEAN 3-DAY COMPARISON (Jul 6 / Jul 7 / Jul 8, GROSS vs CLEAN)

**Prior art (C45):** `.claude/live_20260705/SLATE_LEDGER_20260706.md` (evening refresh 07-07 23:15 ET, mech ⚑ flags per leg), `.claude/BLEED_ATTRIBUTION_20260707.md` (flag machinery, classes a/b/c), `.claude/autopsy_20260706/VIOLATIONS_DEEPCUT_20260706.md` (Jul-6 defect classes), `.claude/sweep_20260707/POST_FILL_MOVE_20260708.md` + `post_fill_move.py` (divot convention), `.claude/sweep_20260707/SWEEP_TABLE.txt` (07-07 naked sweep), `/root/naked_sweep_20260708/` (07-08 sweep + exchange truth), `arb-executor/audit/w1_grading.py` (grade rubric). **Delta:** first per-day × per-cat GROSS-vs-CLEAN split of the four entry metrics with the mechanical legs stripped.

**Producers (this pass, read-only, nothing written on the VPS):** `part3_day67_metrics.py` → `part3_day67_out.json` (per-leg from `/tmp/slate_ledger_v2.json` + `/root/post_fill_move.json`); `part3_day8_metrics.py` → `part3_day8_out.json` (per-leg from `/root/naked_sweep_20260708/fills_recent.json` + `orders_resting.json` + premarket_ticks + Kalshi trades tape + `state/schedule.json`). All four files live next to this doc.

## 0 · CONVENTIONS + COVERAGE (read before the tables)

- **Day attribution:** metrics 1–3 by **fill-day ET**; grade mix by **conception-day** (ledger convention). Jul-8 is a **PARTIAL day** (data to ~12:07 ET; bot DEAD 02:52→11:30 ET, disk full — see PROOF_LOG_ENOSPC).
- **Sources per day:** Jul 6 + Jul 7 = the evening exchange-truth ledger (`/tmp/slate_ledger_v2.json`, built 07-07 23:15 ET) + `post_fill_move.json` divot classes. Jul 8 = `fills_recent.json` (exchange fills, snapshot 12:07 ET).
- **`fills_recent.json` coverage check (mandated):** it is a **rolling last-3000-fills pull** (refreshed by cron; at 11:45 pull it reached back to 2026-07-06 04:00 ET, at 12:07 to 08:22 ET). It does **NOT** cover Jul-6 from midnight — the gap is noted and irrelevant here: Jul 6/7 are computed from the ledger, which is a full exchange-truth pull.
- **Metric 1 — entry-vs-own-low:** ledger `vw − w1_low` (own cheapest fillable W1 print, gold-census field), **W1-filled legs with a clock only**. Jul-8: recomputed prints-based (min trade print, window fill−24h → honest start, W1 fills only). Conservative: wider window can only enlarge the gap. Jul-6 n is tiny because the honest-clock census covered few Jul-6 legs (`w1 = no-clock` dominates) — stated, not smoothed.
- **Metric 2 — divot share:** `post_fill_move.py` classifier verbatim; share = DIVOT / (DIVOT+REPRICE+NO_UNDERCUT), AMBIG excluded, W1 fills only.
- **Metric 3 — band-reach:** pregame = exit filled W1/corridor OR band touched W1/corridor; any = same over all windows incl. W2. Denominator = filled legs with a band on record.
- **Metric 4 — grade mix:** ledger event grades (A/B/C/D/F; B-family aggregated in the ledger JSON row field). CLEAN = events with **no** mech-flagged leg. **S-tier: 0 events all three days** (EVENING_CUT §2 honest-era regrade; the S tier is empty era-wide). The renderer's **leg-level** S count (6 era legs, SLATE §0) is not reproducible per-cat/per-day from the ledger JSON fields (a field-level approximation over-counts ~10×) → per-cat S rows are **UNAVAILABLE, not approximated**.
- Mains (ATP_MAIN/WTA_MAIN) are n≤8 everywhere — LUCK-POLLUTED per C46, shown for completeness, no trend claimed.

## 1 · MECHANICAL-STRIP MANIFEST (exactly what was stripped, and why)

| day | legs stripped / total fills | flag breakdown | flag source |
|---|---|---|---|
| **Jul 6** | **79 / 391** (20%) | ⚑a dup-surplus 49 · ⚑a+b 6 · ⚑a+c 3 · ⚑a+b+c 2 · ⚑b naked-band-touch 13 · ⚑b+c 1 · ⚑c fractional 5 · +1 manual (KEYNOS-KEY, footnote) | leg `mech` field in `slate_ledger_v2.json`, assigned by BLEED_ATTRIBUTION_20260707 (producer `bleed_attribution_20260707.py`, guard-replay + naked-window machinery) |
| **Jul 7** | **126 / 655** (19%) | ⚑a 72 · ⚑a+b 18 · ⚑a+c 4 · ⚑a+b+c 1 · ⚑b 19 · ⚑b+c 4 · ⚑c 4 · **naked-sweep 4** (ISOTOM-TOM, KUSTAG-TAG, NASLEE-LEE, TIKCHO-CHO) | same ledger flags (dup-buy-storm surplus = class a, the 07-07 dominant defect, fix ccf8fa8f); naked-sweep names from `sweep_20260707/SWEEP_TABLE.txt` (exchange truth 22:51 ET) |
| **Jul 8** | **218 / 292** (75%) | **13 named naked-class** (MILMIS-MIS/MIL, VANSEL-VAN, JONJEA-JON/JEA, LUENAT-LUE/NAT, TOMSHI-TOM, DAMARN-ARN/DAM, PDARIB-RIB, MAXABA-MAX, ISHCRO-CRO — all located in the fills) + **205 dead-window legs** (every leg whose buys landed 02:52–11:30 ET: bot dead → every such fill is an orphaned, unmanaged bid; superset of the named class by construction) | named list = today's naked-class brief + `naked_sweep_20260708/sweep_before.json`; dead window = last write of `logs/live_v3_20260707.jsonl` (02:52) → restart (11:30) |

Jul-6 footnotes: (i) the **adoption mark-to-market fabrications** (7 events: TODSAG, VAJRAM, HERNAG, POTFEL, TEUHAS, PACLOV, KULVOG — VIOLATIONS_DEEPCUT C-a) fabricated **booking prices**, not exchange fills; every metric here is computed from exchange VWAP, so that defect cannot contaminate these tables — and the *fill-level* residue of the same incident (orphan **dup double-fills**) is already caught: all 7 events carry ⚑a on the dup leg (verified by name). (ii) **KEYNOS-KEY** (the Class-3 in-play orphan fill, 54¢ at 11:12:42, rode to settlement) carries **no** a/b/c flag — stripped manually here (WTA_MAIN Jul-6 clean n 6→5; it sits in no gap/band/divot cohort, so only the fill count moves; its event, grade B, also belongs out of the clean grade cell — WTA_MAIN n is no-read anyway).

Full per-leg strip lists are machine-readable in `part3_day67_out.json` (`mech_legs` per cat/day) and `part3_day8_out.json` (`mech` per leg).

## 2 · METRIC 1 — ENTRY vs OWN W1 LOW (median ¢ above own cheapest fillable W1 point; n in parens)

| cat | Jul6 gross | Jul6 clean | Jul7 gross | Jul7 clean | Jul8 gross | Jul8 clean |
|---|---|---|---|---|---|---|
| ATP_MAIN | 2.0 (3)‼ | 2.0 (3)‼ | 2.0 (3)‼ | 2.0 (3)‼ | no fills | no fills |
| WTA_MAIN | 1.75 (4)‼ | 2.0 (3)‼ | 3.0 (2)‼ | 3.0 (2)‼ | no fills | no fills |
| ATP_CHALL | 4.0 (6)‼ | 5.0 (5)‼ | 1.0 (70) | 1.7 (61) | 1.5 (8)‼ | 40.0 (1)‼† |
| WTA_CHALL | 1.0 (6)‼ | 1.0 (6)‼ | 1.0 (18) | 1.0 (17) | 1.0 (8)‼ | 0.0 (1)‼ |
| ITF_M | 3.5 (10) | 6.0 (6)‼ | 1.0 (79) | 1.0 (73) | 1.0 (25) | 0.5 (8)‼ |
| ITF_W | 10.0 (5)‼ | 10.0 (3)‼ | 2.0 (67) | 3.0 (53) | 1.0 (35) | 1.0 (14) |

‼ = n<30, luck-polluted per C46. † single leg DEMGIU-GIU (filled 66¢ 02:18 ET vs a 26¢ print in the prior-day window) — n=1, likely a thin-tape window artifact; no read.
Jul-6 caveat: the census only exists for clocked legs (5–10 per cat) — medians unstable. Jul-8 gross rows include dead-window pre-gun fills; their *entry* prices look fine — the damage of the outage is in exits, which this metric cannot see.

## 3 · METRIC 2 — DIVOT SHARE (of decisive fills: DIVOT / (D+R+N); D/R/N counts in parens)

| cat | Jul6 gross | Jul6 clean | Jul7 gross | Jul7 clean | Jul8 gross | Jul8 clean |
|---|---|---|---|---|---|---|
| ATP_MAIN | 100% (1/0/0)‼ | 100% (1/0/0)‼ | 100% (1/0/0)‼ | 100% (1/0/0)‼ | no fills | no fills |
| WTA_MAIN | 100% (1/0/0)‼ | 0/0/0 UNAVAIL | 0/0/0 UNAVAIL | 0/0/0 UNAVAIL | no fills | no fills |
| ATP_CHALL | 50% (2/2/0)‼ | 33% (1/2/0)‼ | 19.5% (8/25/8) | 21.6% (8/22/7) | 0% (0/0/1)‼ | 0% (0/0/1)‼ |
| WTA_CHALL | 33% (1/1/1)‼ | 33% (1/1/1)‼ | 0% (0/2/7)‼ | 0% (0/2/6)‼ | 0% (0/0/1)‼ | 0% (0/0/1)‼ |
| ITF_M | 29% (2/2/3)‼ | 25% (1/1/2)‼ | 25.6% (11/22/10) | 25.6% (10/20/9) | 67% (2/1/0)‼ | 67% (2/1/0)‼ |
| ITF_W | 0% (0/2/0)‼ | 0% (0/2/0)‼ | 18.2% (8/29/7) | 17.6% (6/24/4) | 0% (0/5/2)‼ | 0% (0/5/2)‼ |

Jul-6 is effectively **UNAVAILABLE at cat level** (decisive n ≤ 4 everywhere): the classifier cohort is W1-filled legs, and Jul-6 barely produced W1 fills under the honest clock. Jul-8 gross adds nothing over clean because **197 of 218 mechanical legs are NO_TAPE** — the tick recorder died with the bot; the outage-window fills are *unclassifiable*, not unclassified.

## 4 · METRIC 3 — BAND-REACH RATE (pregame W1/corridor %, with any-window % in parens; denominator = filled legs with a band on record)

| cat | Jul6 gross | Jul6 clean | Jul7 gross | Jul7 clean | Jul8 gross | Jul8 clean |
|---|---|---|---|---|---|---|
| ATP_MAIN | 33% (83%) 6 | 40% (100%) 5‼ | 0% (100%) 4‼ | 0% (100%) 4‼ | no fills | no fills |
| WTA_MAIN | 0% (86%) 7‼ | 0% (100%) 5‼ | 0% (100%) 4‼ | 0% (100%) 4‼ | no fills | no fills |
| ATP_CHALL | 19% (87%) 91 | 21% (86%) 71 | 25% (83%) 133 | 23% (83%) 115 | UNAVAIL (0/5) | UNAVAIL (0/2) |
| WTA_CHALL | 20% (83%) 35 | 19% (81%) 32 | 24% (78%) 41 | 18% (73%) 33 | UNAVAIL (0/5) | UNAVAIL (0/2) |
| ITF_M | 11% (85%) 102 | 7% (84%) 81 | 40% (79%) 250 | 38% (76%) 208 | UNAVAIL (0/4) | UNAVAIL (0/4) |
| ITF_W | 13% (88%) 142 | 10% (87%) 112 | 48% (86%) 223 | 48% (84%) 165 | UNAVAIL (2/7) | UNAVAIL (0/4) |

**Jul-8 = UNAVAILABLE, honestly:** a band exists on record only for the 7 legs that had a resting sell at the 12:07 snapshot. The dead-window fills had **no exit order at all** — the absence of a band IS the day's defect; a band-reach rate cannot be computed for them without inventing bands. Recompute at tonight's ledger refresh once exits/settlements exist.

## 5 · METRIC 4 — GRADE MIX (ledger event grades A/B/C/D/F; conception-day, settled events as of 07-07 23:15 ET; CLEAN = events with zero mech-flagged legs)

| cat | Jul6 gross A/B/C/D/F (n) | Jul6 clean | Jul7 gross | Jul7 clean | Jul8 |
|---|---|---|---|---|---|
| ATP_MAIN | 0/2/0/2/0 (4)‼ | 0/1/0/2/0 (3)‼ | 0/1/1/0/0 (2)‼ | 0/1/1/0/0 (2)‼ | UNAVAILABLE |
| WTA_MAIN | 0/4/0/0/0 (4)‼ | 0/2/0/0/0 (2)‼ | 0/2/0/0/0 (2)‼ | 0/2/0/0/0 (2)‼ | UNAVAILABLE |
| ATP_CHALL | 0/39/2/5/10 (56) | 0/20/1/5/10 (36) | 0/33/25/2/8 (68) | 0/27/13/2/8 (50) | UNAVAILABLE |
| WTA_CHALL | 0/13/3/2/0 (18)‼ | 0/10/3/2/0 (15)‼ | 0/6/10/0/2 (18)‼ | 0/5/4/0/2 (11)‼ | UNAVAILABLE |
| ITF_M | 1/45/6/10/9 (71) | 0/19/3/9/9 (40) | 0/66/15/1/33 (115) | 0/42/11/1/33 (87) | UNAVAILABLE |
| ITF_W | 2/69/7/10/12 (100) | 0/38/3/8/12 (61) | 0/68/6/2/14 (90) | 0/36/4/2/14 (56) | UNAVAILABLE |

S = 0 events every day (era-wide; §0 note). **Jul-8 grade mix UNAVAILABLE:** the day's events are largely unsettled, the W1 regrade machinery (`full_tape_regrade` → `w1_grading.py`) has not run for the day, and the outage killed the tick tape its windows need — grading it today would be fiction.

**Read the distortion, not just the totals:** stripping mech events *raises* the F-share (ITF_M Jul-7: F 29% gross → 38% clean; ITF_W Jul-6: 12% → 20%) because the dup-surplus events disproportionately got exited (B-family) — the gross B-share was **flattered by defect volume**. The clean columns are the honest machine, and they are worse-looking but truer.

## 6 · TREND READ (plain words, CLEAN columns; Jul-8 = partial-day sliver, 74 clean legs total)

- **ITF_M — improving where measurable.** Entry-vs-own-low clean: 6.0¢ (tiny n) → 1.0¢ → 0.5¢ (n=8). Band-reach pregame 7% → 38%. Divot share flat ~25%, reprice-dominated. The gross Jul-6 number (3.5¢) was **flattered by the dup storm** — the surplus fills bought the dips, so the defect made entry timing look better than the honest machine's 6¢.
- **ITF_W — improving, but still the reprice cat.** Clean gap 10¢ (n=3, unstable) → 3¢ → 1¢. Band-reach 10% → 48%. Divot share 18% Jul-7 and 0/7 decisive on the Jul-8 sliver — two-thirds-plus of decisive fills are still the market moving through us (POST_FILL doctrine confirmed across all three days). Entry px is getting closer to the low; the *class* of fill has not improved.
- **ATP_CHALL — flat-to-slightly-better.** Clean gap 5¢ (tiny n) → 1.7¢; band-reach ~21% → 23% (no jump like ITF); divot ~22% Jul-7. The Jul-8 clean column is n=1–3 and carries one 40¢ outlier — no read.
- **WTA_CHALL — flat.** Gap 1¢ → 1¢; band-reach 19% → 18%; 1 divot in 11 clean decisive fills across Jul-6/7 — small but consistently reprice/no-undercut.
- **Mains — no read all three days** (n ≤ 8, luck-polluted).
- **Where gross lies:** (1) **Jul-8 gross is 75% mechanical** — any headline built on it (fill counts, entry gaps) describes orphaned bids, not the strategy; band/divot metrics for the day are not merely distorted, they are *unmeasurable* (no exits existed, no tape was recorded). (2) **Jul-6 gross flattered entry quality** (dup fills at the lows: ITF_M 3.5¢ gross vs 6.0¢ clean) **and inflated band-reach** (⚑b legs are by definition band-touchers: ITF_M 11% gross vs 7% clean). (3) **Grade mix gross flattered the B-share** on both ledger days (mech events exited more often than honest ones). (4) Jul-7's dup storm barely moved the per-cat medians (gross≈clean within 1¢) because the surplus was *volume*, not different prices — the Jul-7 damage was dollars (−$108 mechanical, BLEED_ATTRIBUTION), not entry-metric distortion.

*Recompute Jul-8 properly at tonight's ledger refresh (settlements + regrade); this doc's Jul-8 columns are the 12:07 ET partial cut. C50 close-out is the session owner's, not this part-file's.*
