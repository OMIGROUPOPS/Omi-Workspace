# BLEED ATTRIBUTION 2026-07-07 (STEP 1) — mechanical vs strategic, honest era

**Era: 2026-07-05 10:39:54 ET boot → 2026-07-07 ~11:00 ET. Exchange truth only** (fills + settlements + order-history + public tape + live marks; producer `arb-executor/analysis/forensic_20260707/bleed_attribution_20260707.py`, raw JSON `/root/bleed_attribution_20260707.json`).

## 0. PRIOR ART (C45)

- `.claude/FORENSIC_20260707_MORNING.md` (same day) — the defect classes being dollar-realized here; containment `ccf8fa8f` LIVE since 10:21 ET, so the bleed windows CLOSE at deploy.
- **C46 Lane-2 discipline** — the per-class dollar figures below are settlement-involved and small-n; they attribute damage, they do not grade strategy. The gross/mechanical/strategic split is the deliverable; Step 2's restatement consumes it.
- **F39 / A55** — result-side only from exchange records; sells priced by action (never raw outcome_side); settlement value computed from `market_result` × net position, not the settlements `revenue` field (observed 0 on fp accounts).
- **A54** — basis from fills VWAP, never pos_map avg.
- Delta: first dollar-attribution of the defect family, and the bid_ex_self emission diagnosis (verdict reversal, §4).

## 1. METHOD (assumptions stated)

- **(a) dup/multi-buy surplus:** guard replay over era fills per ticker (identical admission logic to the deployed chokepoint guard): buys admitted past a committed 5-lot are SURPLUS. Ticker P&L (sells − fees − basis + settlement of net) attributed **pro-rata** to the surplus share fraction; realized (settled/sold) reported separately from open mark risk.
- **(b) naked base-lot band-touch (the KHRYOU class):** per leg, sell-order lifecycle intervals (alive qty = initial_count — slightly over-covers, conservative) vs held-qty timeline → naked windows > 60s on the FIRST lot only (surplus shares live in (a); no double count). Band = the leg's standing sell price on record. "Touched" = any public print STRICTLY above band inside a window, or prints AT band totalling ≥ 2× the naked qty (queue conservatism). Foregone = naked_qty × (band − outcome), outcome = settlement value or current bid. Legs with no sell order ever in era (hold-rule by config, or never-exited) carry no band on record and are excluded — listed count in §2.
- **(c) fractional residues:** sub-1-share position fractions (int-floor invisible to exit sizing) × (outcome − basis).
- Daily gross = realized-on-the-day (sell fills at era-avg basis + settlements of net at era-avg basis), ET days. Pre-era opening shares carry era-average basis (noted; small).

## 2. THE MECHANICAL BLEED (per class / per day; per-ticker tables in the Appendix)

Era universe: **2,374 fills / 1,025 tickers / 936 settled**. Producer stats: 458 legs showed ≥1 naked base-lot window >60s; 73 survived the band-touch + settled/mark delta filters.

| class | 07-05 | 07-06 | 07-07 | TOTAL | n |
|---|---|---|---|---|---|
| (a) dup surplus, realized $ | −2.88 | −8.71 | −37.76 | **−49.35** | 161 tickers, 892.9 surplus sh (10.0 / 310.4 / 572.5 by day) |
| (a) open mark risk $ | | | −0.38 | −0.38 | (backfill closed the rest) |
| (b) naked band-touch foregone $ | −6.20 | −33.60 | −70.92 | **−110.72** | 73 legs (4 / 20 / 49); settled portion −103.72, open −7.00 |
| (c) fractional residues $ | −0.09 | +0.08 | +0.69 | **+0.67** | 25 legs |
| **MECHANICAL TOTAL $** | **−9.17** | **−42.23** | **−108.01** | **−159.40** | |

Readings:
- **(b) > (a): the exits that weren't there cost 2.2× more than the surplus shares themselves.** The KHREYOU-class exhibit generalizes: 73 legs where the tape printed at/above the leg's own standing band while no exit rested, then settlement took it (all but 2 settled at 0). Named: TIMJEF-JEF band 91 touched → settled 0 → $4.55 foregone; BARSIM-BAR 94 → 0 → $4.70; KHRYOU-KHR band 52 touched, 2 sh, $1.04.
- Class (a) per-share damage is mild (−5.5c/sh avg — dups roughly coin-flipped) but it carried **$413 of unintended capital** and manufactured the (b) windows (exit churn/resize on multi-lot legs is what left bands uncovered).
- The bleed **accelerated day-over-day** (−9 → −42 → −108): each restart layer compounded, and 07-07's three overnight restarts (01:07/02:07/02:34 ET) were the worst. Containment `ccf8fa8f` (10:21 ET) closes all three classes going forward: chokepoint refuses the surplus, EXIT QTY = POSITION QTY keeps bands covered, pagination restores guard sight.

## 3. RE-ATTRIBUTION — gross / mechanical / strategic (the Step-2 restatement input)

My exchange-truth daily gross (realized-on-the-day: sell fills at era-avg basis + settlements of net, ET days):

| ET day | gross realized $ | mechanical $ | **strategic residual $** |
|---|---|---|---|
| 07-05 (from 10:39 boot) | −3.66 | −9.17 | **+5.51** |
| 07-06 | +17.22 | −42.23 | **+59.45** |
| 07-07 (to ~11:20) | −86.37 | −102.71 | **+16.34** |
| **era total** | **−72.81** | **−154.11 (settled-realized)** | **+81.30** |

(mechanical column = classes (a) realized + (b) foregone + (c), settled portions on the day they settled; strategic residual = what the day would have shown absent the defect family. Open-position mark components excluded from both sides — reported separately: (a) mark −0.38, (b) open −7.00.)

**The verdict: the era's strategy was net POSITIVE (+$81.30 realized) absent the defect family. The entire era loss and more is mechanical.** No band-unreachability signal survives attribution — the "strategic" column is positive on all three days. Step 2's restatement: gross −$72.81 = strategy +$81.30 + defects −$154.11 (+ fees inside).

### Reconciliation vs the stated figures (mandatory P&L format)

- **Stated: Jul 6 "RODE" −$189.50, today −$54 (24h). My calendar-day views reproduce NEITHER individually — but the two-day aggregate matches: cash view Jul-6 −$50.63 + Jul-7 −$199.11 = −$249.74 vs stated −$243.50 (Δ 2.6%).** The stated split uses a different day boundary (their "Jul 6" evidently captures the Jul-6 slate's overnight settlements that my calendar view books on 07-07 morning — where the −$199.11/−$86.37 sits). Slate-tagged realized (26JULxx in ticker): JUL05 −4.14, JUL06 −1.05, JUL07 −70.02-and-open.
- **Cash + portfolio + API reconciliation:** cash flow by ET day (buys/sells/settle-revenue/fees): 07-05 +50.63, 07-06 −50.63, 07-07 −199.11. Account now: **balance $672.52** (Kalshi API), **portfolio_value $167.20** (Kalshi's mark) vs my bid-marked open book $152.51 across 79 legs (Δ $14.69 = bid-vs-mid marking). Fees era-total $1.13 (included).
- Of the stated −$243.50 two-day bleed, **−$154.11 (63%) is mechanically attributed** to this defect family with per-leg evidence; the remainder is open-position mark movement + window convention, not band-unreachability.

## 4. WHY `bid_ex_self` READ AS 0 — DIAGNOSIS ONLY (no deploy)

**The feature fired; the measurement lied. Verdict of the 02:30 verify and the morning forensic §4(c) REVERSED.**

- **Emission site 1 — `_aim_shadow_log` (live_v4.py:2265→2281):** gated on `aim_shadow` (config **True**) + the LATCHCAL table existing (`data/shape_corpus/aim_v2_operational_LATCHCAL.json`, present since Jul 6 20:50, 1,470 cells) → emits `aim_shadow` events through `self._log`, `bid_ex_self` included unconditionally. **jsonl truth: 1,668 occurrences in `logs/live_v3_20260707.jsonl`, first at 02:34:33 AM ET** — nine seconds after the 02:34:20 boot finished validation. The re-fire landed. Jul 6 jsonl: 0, correct — the code arrived with that boot.
- **Why every grep said 0:** the checks ran on `/tmp/live_v4.log` — the CONSOLE stream, whose writer truncates event payloads at ~190 chars. `aim_shadow` records are long; `bid_ex_self` sits past the cut on every line. Key-presence checks MUST run on the jsonl (vaulted, C47).
- **Emission site 2 — `expression_clamped` (live_v4.py:5110):** correctly silent BY CONFIG: `expression_invariant` is ABSENT from `deploy_v5_live.json` → `bool(config.get(..., False))` = OFF (live_v4.py:1619) → `_express_target` is a pass-through and can never log. The ex-self CARRY (observe fields) is live; the ex-self CLAMP (behavior) is gated off, as designed at d3aa99b0.
- **Boot-flag state at 02:34:** `aim_shadow=True`, `expression_invariant=OFF`, LATCHCAL present → exactly the observed emission pattern. No code defect; no deploy needed. The only defect was forensic method.

## APPENDIX — producer output (full per-ticker tables)

```
STATS fills=2374 tickers=1025 settled=936 b_candidates=458

## CLASS (a) dup/multi-buy surplus
| ticker | day | surplus sh | realized $ | mark risk $ | settled |
|---|---|---|---|---|---|
| KXATPCHALLENGERMATCH-26JUL07GOMDAL-DAL | 07-07 | 15 | -10.43 | +0.00 | Y |
| KXITFMATCH-26JUL06LUEVAN-LUE | 07-06 | 10 | -7.40 | +0.00 | Y |
| KXATPCHALLENGERMATCH-26JUL07BURSCH-BUR | 07-07 | 10 | -6.53 | +0.00 | Y |
| KXITFMATCH-26JUL06ZHAISH-ZHA | 07-07 | 10 | -6.50 | +0.00 | Y |
| KXITFMATCH-26JUL07ECHADD-ADD | 07-07 | 10 | -5.10 | +0.00 | Y |
| KXITFMATCH-26JUL06NAKIDO-NAK | 07-07 | 5 | -4.05 | +0.00 | Y |
| KXATPCHALLENGERMATCH-26JUL07GADSTA-GAD | 07-07 | 5 | -3.77 | +0.00 | Y |
| KXATPMATCH-26JUL06DECOB-DE | 07-06 | 5 | -3.72 | +0.00 | Y |
| KXITFWMATCH-26JUL07SEIKUL-SEI | 07-07 | 5 | -3.65 | +0.00 | Y |
| KXATPCHALLENGERMATCH-26JUL07JUSKRA-KRA | 07-07 | 15 | -3.52 | +0.00 | Y |
| KXITFWMATCH-26JUL06URREVA-URR | 07-06 | 5 | -3.00 | +0.00 | Y |
| KXWTAMATCH-26JUL06PAOEAL-EAL | 07-06 | 5 | -2.92 | +0.00 | Y |
| KXATPCHALLENGERMATCH-26JUL06ZORDEV-ZOR | 07-06 | 5 | -2.75 | +0.00 | Y |
| KXATPCHALLENGERMATCH-26JUL06MAXGHI-GHI | 07-06 | 5 | -2.70 | +0.00 | Y |
| KXITFWMATCH-26JUL07MILSAK-MIL | 07-07 | 5 | -2.65 | +0.00 | Y |
| KXITFWMATCH-26JUL06PACLOV-PAC | 07-06 | 5 | -2.60 | +0.00 | Y |
| KXITFWMATCH-26JUL07ZARNEW-ZAR | 07-07 | 5 | -2.45 | +0.00 | Y |
| KXITFWMATCH-26JUL07GANSAM-SAM | 07-07 | 5 | -2.38 | +0.00 | Y |
| KXATPCHALLENGERMATCH-26JUL06BASHOE-BAS | 07-06 | 5 | -2.30 | +0.00 | Y |
| KXITFMATCH-26JUL07BROVAN-VAN | 07-07 | 5 | -2.27 | +0.00 | Y |
| KXITFWMATCH-26JUL07HAVHIB-HAV | 07-07 | 5 | -2.23 | +0.00 | Y |
| KXITFMATCH-26JUL07STRHAR-HAR | 07-07 | 5 | -2.20 | +0.00 | Y |
| KXITFWMATCH-26JUL06MCAENC-MCA | 07-06 | 5 | -2.10 | +0.00 | Y |
| KXITFWMATCH-26JUL07ARYKRO-ARY | 07-07 | 15 | -2.10 | +0.00 | Y |
| KXATPCHALLENGERMATCH-26JUL06RAQRIB-RIB | 07-06 | 5 | -1.80 | +0.00 | Y |
| KXITFMATCH-26JUL06VANBOO-BOO | 07-07 | 5 | -1.80 | +0.00 | Y |
| KXITFWMATCH-26JUL07LANDEN-LAN | 07-07 | 5 | -1.75 | +0.00 | Y |
| KXITFWMATCH-26JUL07ABEJOR-ABE | 07-07 | 5 | -1.70 | +0.00 | Y |
| KXITFMATCH-26JUL05MASCIO-MAS | 07-05 | 5 | -1.65 | +0.00 | Y |
| KXITFMATCH-26JUL06TEUHAS-TEU | 07-06 | 5 | -1.50 | +0.00 | Y |
| KXITFWMATCH-26JUL07OLIALL-OLI | 07-07 | 5 | -1.50 | +0.00 | Y |
| KXITFMATCH-26JUL07JIMKUM-JIM | 07-07 | 5 | -1.48 | +0.00 | Y |
| KXATPCHALLENGERMATCH-26JUL07BARSIM-BAR | 07-07 | 5 | -1.43 | +0.00 | Y |
| KXITFWMATCH-26JUL06BOSTOP-TOP | 07-06 | 5 | -1.38 | +0.00 | Y |
| KXWTACHALLENGERMATCH-26JUL07CARPIG-PIG | 07-07 | 5 | -1.35 | +0.00 | Y |
| KXITFMATCH-26JUL06TIMJEF-JEF | 07-06 | 5 | -1.30 | +0.00 | Y |
| KXATPCHALLENGERMATCH-26JUL07FORLOG-FOR | 07-07 | 5 | -1.27 | +0.00 | Y |
| KXATPCHALLENGERMATCH-26JUL05LEGSHI-LEG | 07-05 | 5 | -1.23 | +0.00 | Y |
| KXITFWMATCH-26JUL07PROMAE-MAE | 07-07 | 5 | -1.21 | +0.00 | Y |
| KXITFWMATCH-26JUL06ZRNLUE-ZRN | 07-06 | 5 | -1.15 | +0.00 | Y |
| KXATPCHALLENGERMATCH-26JUL06VILBOC-BOC | 07-06 | 5 | -1.10 | +0.00 | Y |
| KXITFMATCH-26JUL07WISVRT-WIS | 07-07 | 5 | -1.07 | +0.00 | Y |
| KXITFWMATCH-26JUL07DAPTEI-DAP | 07-07 | 5 | -1.05 | +0.00 | Y |
| KXITFMATCH-26JUL07BRAJAD-BRA | 07-07 | 5 | -1.02 | +0.00 | Y |
| KXITFMATCH-26JUL07REYMAL-REY | 07-07 | 5 | -1.00 | +0.00 | Y |
| KXITFMATCH-26JUL07PEDRAD-PED | 07-07 | 5 | -0.93 | +0.00 | Y |
| KXITFMATCH-26JUL07BREBEN-BEN | 07-07 | 5 | -0.88 | +0.00 | Y |
| KXITFWMATCH-26JUL07POCINI-POC | 07-07 | 5 | -0.85 | +0.00 | Y |
| KXATPCHALLENGERMATCH-26JUL06BARDAL-DAL | 07-06 | 5 | -0.80 | +0.00 | Y |
| KXATPCHALLENGERMATCH-26JUL07LEOCAS-LEO | 07-07 | 5 | -0.75 | +0.00 | Y |
| KXITFMATCH-26JUL07AGWZIC-ZIC | 07-07 | 5 | -0.68 | +0.00 | Y |
| KXITFWMATCH-26JUL07PODSMI-POD | 07-07 | 5 | -0.65 | +0.00 | Y |
| KXITFWMATCH-26JUL06GANPUI-PUI | 07-06 | 5 | -0.63 | +0.00 | Y |
| KXITFMATCH-26JUL07MELVAR-VAR | 07-07 | 5 | -0.62 | +0.00 | Y |
| KXITFWMATCH-26JUL07MARAVA-AVA | 07-07 | 5 | -0.62 | +0.00 | Y |
| KXWTACHALLENGERMATCH-26JUL07VANMAR-MAR | 07-07 | 5 | -0.62 | +0.00 | Y |
| KXITFWMATCH-26JUL06GAONON-GAO | 07-06 | 5 | -0.56 | +0.00 | Y |
| KXATPCHALLENGERMATCH-26JUL07CHOKUZ-KUZ | 07-07 | 5 | -0.50 | +0.00 | Y |
| KXITFMATCH-26JUL07COCAZA-AZA | 07-07 | 5 | -0.47 | +0.00 | Y |
| KXITFWMATCH-26JUL06PODLUK-POD | 07-06 | 5 | -0.45 | +0.00 | Y |
| KXATPCHALLENGERMATCH-26JUL06MAGROD-ROD | 07-06 | 5 | -0.43 | +0.00 | Y |
| KXITFWMATCH-26JUL07TODSTR-TOD | 07-07 | 5 | -0.40 | +0.00 | Y |
| KXITFWMATCH-26JUL06VAJRAM-RAM | 07-06 | 5 | -0.35 | +0.00 | Y |
| KXITFWMATCH-26JUL07SCHTRI-SCH | 07-07 | 5 | -0.32 | +0.00 | Y |
| KXITFMATCH-26JUL06HERNAG-NAG | 07-06 | 5.37 | -0.29 | +0.00 | Y |
| KXITFWMATCH-26JUL07MANLUK-MAN | 07-07 | 5 | -0.27 | +0.00 | Y |
| KXATPCHALLENGERMATCH-26JUL07ZHOCAT-CAT | 07-07 | 5 | -0.23 | +0.00 | Y |
| KXITFMATCH-26JUL06ALIMIS-MIS | 07-06 | 5 | -0.23 | +0.00 | Y |
| KXITFMATCH-26JUL07COSBLO-COS | 07-07 | 5 | -0.20 | +0.00 | Y |
| KXWTACHALLENGERMATCH-26JUL07LABBER-BER | 07-07 | 5 | -0.20 | +0.00 | Y |
| KXITFWMATCH-26JUL07SENKEN-SEN | 07-07 | 5 | -0.12 | +0.00 | Y |
| KXATPCHALLENGERMATCH-26JUL06BARZIN-BAR | 07-06 | 5 | +0.00 | -0.38 | open |
| KXITFWMATCH-26JUL06VARMUN-MUN | 07-06 | 5 | +0.15 | +0.00 | Y |
| KXITFWMATCH-26JUL07KAKJAN-KAK | 07-07 | 5 | +0.15 | +0.00 | Y |
| KXITFWMATCH-26JUL07MALKOM-KOM | 07-07 | 5 | +0.15 | -0.00 | open |
| KXITFWMATCH-26JUL07HERBAL-BAL | 07-07 | 5 | +0.17 | +0.00 | Y |
| KXITFMATCH-26JUL07TAINIK-TAI | 07-07 | 5 | +0.20 | +0.00 | Y |
| KXITFMATCH-26JUL06MATKOM-KOM | 07-07 | 5 | +0.22 | +0.00 | Y |
| KXITFWMATCH-26JUL07LEKVLA-VLA | 07-07 | 5 | +0.28 | -0.00 | open |
| KXWTACHALLENGERMATCH-26JUL06GRAMAS-GRA | 07-06 | 5 | +0.28 | +0.00 | Y |
| KXATPCHALLENGERMATCH-26JUL06PALKOL-PAL | 07-06 | 5 | +0.30 | +0.00 | Y |
| KXITFWMATCH-26JUL06MARGLU-MAR | 07-06 | 5 | +0.30 | +0.00 | Y |
| KXITFWMATCH-26JUL07PATMAK-MAK | 07-07 | 5 | +0.33 | +0.00 | Y |
| KXITFMATCH-26JUL06BONFAU-FAU | 07-06 | 5 | +0.35 | +0.00 | Y |
| KXITFMATCH-26JUL06OKITAN-TAN | 07-07 | 5 | +0.35 | +0.00 | Y |
| KXITFWMATCH-26JUL06WAGYOU-WAG | 07-06 | 5 | +0.35 | +0.00 | Y |
| KXATPCHALLENGERMATCH-26JUL06PRIORA-ORA | 07-06 | 5 | +0.38 | +0.00 | Y |
| KXATPCHALLENGERMATCH-26JUL07CORBLA-BLA | 07-07 | 5 | +0.38 | +0.00 | Y |
| KXITFWMATCH-26JUL07EVAENC-EVA | 07-07 | 5 | +0.38 | +0.00 | Y |
| KXITFWMATCH-26JUL07RICMAD-MAD | 07-07 | 5 | +0.38 | +0.00 | Y |
| KXATPCHALLENGERMATCH-26JUL07ROMBAS-BAS | 07-07 | 5 | +0.40 | +0.00 | Y |
| KXITFWMATCH-26JUL07KHRBEL-KHR | 07-07 | 5 | +0.40 | +0.00 | Y |
| KXITFMATCH-26JUL06CUNLIM-LIM | 07-06 | 5 | +0.40 | +0.00 | Y |
| KXATPCHALLENGERMATCH-26JUL06FOMDHA-FOM | 07-06 | 5 | +0.42 | +0.00 | Y |
| KXITFWMATCH-26JUL06TODSAG-SAG | 07-06 | 5 | +0.42 | +0.00 | Y |
| KXITFMATCH-26JUL06VANHOR-HOR | 07-06 | 5 | +0.50 | +0.00 | Y |
| KXITFMATCH-26JUL07CHOCHE-CHO | 07-07 | 2.45 | +0.52 | +0.00 | Y |
| KXITFMATCH-26JUL07STECHA-STE | 07-07 | 5 | +0.58 | +0.00 | Y |
| KXITFWMATCH-26JUL07YESFET-YES | 07-07 | 5 | +0.60 | +0.00 | Y |
| KXWTACHALLENGERMATCH-26JUL06LEWMAR-LEW | 07-06 | 5 | +0.60 | +0.00 | Y |
| KXITFMATCH-26JUL07URSPOU-POU | 07-07 | 5 | +0.60 | -0.00 | open |
| KXITFWMATCH-26JUL06VIRKOV-VIR | 07-06 | 5 | +0.65 | +0.00 | Y |
| KXITFWMATCH-26JUL07SOZNIS-NIS | 07-07 | 5 | +0.65 | +0.00 | Y |
| KXITFWMATCH-26JUL06IVAKUH-IVA | 07-06 | 5 | +0.70 | +0.00 | Y |
| KXITFWMATCH-26JUL06POPSOL-SOL | 07-06 | 5 | +0.70 | +0.00 | Y |
| KXITFWMATCH-26JUL07INOBUY-INO | 07-07 | 5 | +0.70 | +0.00 | Y |
| KXATPCHALLENGERMATCH-26JUL07DEDTAB-DED | 07-07 | 5 | +0.72 | +0.00 | Y |
| KXATPCHALLENGERMATCH-26JUL07SEYSVR-SVR | 07-07 | 5 | +0.72 | +0.00 | Y |
| KXITFMATCH-26JUL07SCHMUR-MUR | 07-07 | 5 | +0.75 | +0.00 | Y |
| KXITFWMATCH-26JUL07KOTOZE-OZE | 07-07 | 15 | +0.75 | +0.00 | Y |
| KXWTACHALLENGERMATCH-26JUL07KABSHE-SHE | 07-07 | 5 | +0.78 | +0.00 | Y |
| KXITFMATCH-26JUL06HOSGAT-HOS | 07-06 | 5 | +0.78 | +0.00 | Y |
| KXITFMATCH-26JUL07FAUVEL-FAU | 07-07 | 5 | +0.80 | +0.00 | Y |
| KXATPCHALLENGERMATCH-26JUL06CAMDE-CAM | 07-06 | 5 | +0.80 | +0.00 | Y |
| KXATPCHALLENGERMATCH-26JUL06CHEYEV-CHE | 07-06 | 5 | +0.82 | +0.00 | Y |
| KXITFMATCH-26JUL07MCDMUB-MCD | 07-07 | 5 | +0.82 | +0.00 | Y |
| KXWTACHALLENGERMATCH-26JUL07BARRAD-RAD | 07-07 | 5 | +0.82 | +0.00 | Y |
| KXITFMATCH-26JUL06FUKTAK-FUK | 07-07 | 10 | +0.83 | +0.00 | Y |
| KXITFWMATCH-26JUL06SIMCIR-SIM | 07-06 | 5 | +0.85 | +0.00 | Y |
| KXATPCHALLENGERMATCH-26JUL06HUAPUR-PUR | 07-06 | 5 | +0.88 | +0.00 | Y |
| KXITFMATCH-26JUL07HAUMIE-HAU | 07-07 | 5 | +0.88 | +0.00 | Y |
| KXITFWMATCH-26JUL07SIMROU-SIM | 07-07 | 5 | +0.88 | +0.00 | Y |
| KXITFWMATCH-26JUL07BEHBAR-BAR | 07-07 | 5 | +0.90 | +0.00 | Y |
| KXITFWMATCH-26JUL07PODLEO-POD | 07-07 | 5 | +0.90 | +0.00 | Y |
| KXITFMATCH-26JUL07MECOVC-OVC | 07-07 | 5 | +0.93 | +0.00 | Y |
| KXWTACHALLENGERMATCH-26JUL07TUBREN-TUB | 07-07 | 5 | +0.93 | +0.00 | Y |
| KXITFWMATCH-26JUL07PROMAE-PRO | 07-07 | 5 | +0.95 | +0.00 | Y |
| KXATPCHALLENGERMATCH-26JUL06CLAPAP-CLA | 07-06 | 5 | +0.95 | +0.00 | Y |
| KXATPCHALLENGERMATCH-26JUL06IVADIN-IVA | 07-06 | 5 | +0.95 | +0.00 | Y |
| KXATPCHALLENGERMATCH-26JUL06KUZSTR-KUZ | 07-06 | 5 | +0.95 | +0.00 | Y |
| KXATPCHALLENGERMATCH-26JUL06WALNEU-WAL | 07-06 | 5 | +0.95 | +0.00 | Y |
| KXATPCHALLENGERMATCH-26JUL07FELPAS-PAS | 07-07 | 5 | +0.95 | +0.00 | Y |
| KXITFMATCH-26JUL06BEASCO-BEA | 07-06 | 5 | +0.95 | +0.00 | Y |
| KXITFWMATCH-26JUL06POHSTU-STU | 07-06 | 5 | +0.95 | +0.00 | Y |
| KXITFWMATCH-26JUL07COPBRE-BRE | 07-07 | 5 | +0.95 | +0.00 | Y |
| KXITFWMATCH-26JUL07KRYDYU-DYU | 07-07 | 5 | +0.95 | +0.00 | Y |
| KXITFWMATCH-26JUL06MILHER-MIL | 07-06 | 5 | +0.97 | +0.00 | Y |
| KXITFWMATCH-26JUL07PETFRI-FRI | 07-07 | 5 | +1.05 | +0.00 | Y |
| KXITFWMATCH-26JUL06KULVOG-KUL | 07-06 | 5 | +1.07 | +0.00 | Y |
| KXITFMATCH-26JUL07BADZEU-BAD | 07-07 | 5 | +1.10 | +0.00 | Y |
| KXATPCHALLENGERMATCH-26JUL06DONCIZ-DON | 07-06 | 5 | +1.15 | +0.00 | Y |
| KXATPCHALLENGERMATCH-26JUL06HUETEN-HUE | 07-06 | 5 | +1.18 | +0.00 | Y |
| KXITFWMATCH-26JUL06KARBAS-KAR | 07-06 | 5 | +1.25 | +0.00 | Y |
| KXATPCHALLENGERMATCH-26JUL06POLHAI-HAI | 07-06 | 5 | +1.32 | +0.00 | Y |
| KXITFWMATCH-26JUL07TAHHUR-HUR | 07-07 | 5 | +1.34 | +0.00 | Y |
| KXITFMATCH-26JUL06HAZSHI-SHI | 07-07 | 5 | +1.38 | +0.00 | Y |
| KXITFWMATCH-26JUL07CENGLU-CEN | 07-07 | 5 | +1.40 | +0.00 | Y |
| KXATPCHALLENGERMATCH-26JUL06POTFEL-FEL | 07-06 | 5 | +1.42 | +0.00 | Y |
| KXITFMATCH-26JUL07BELALU-ALU | 07-07 | 5 | +1.43 | +0.00 | Y |
| KXITFWMATCH-26JUL07KHRYOU-YOU | 07-07 | 5 | +1.48 | +0.00 | Y |
| KXWTACHALLENGERMATCH-26JUL06MONPOP-MON | 07-06 | 5 | +1.62 | +0.00 | Y |
| KXITFWMATCH-26JUL07HIETSY-TSY | 07-07 | 5 | +1.68 | +0.00 | Y |
| KXITFWMATCH-26JUL07PANZHO-PAN | 07-07 | 10 | +1.80 | +0.00 | Y |
| KXATPCHALLENGERMATCH-26JUL07BARKOP-KOP | 07-07 | 5 | +1.82 | +0.00 | Y |
| KXITFMATCH-26JUL06ELDHAU-HAU | 07-06 | 5 | +1.90 | +0.00 | Y |
| KXITFWMATCH-26JUL07YARHAY-HAY | 07-07 | 10 | +1.90 | +0.00 | Y |
| KXITFWMATCH-26JUL07REVHER-REV | 07-07 | 5 | +1.95 | +0.00 | Y |
| KXITFMATCH-26JUL06MEHCOU-MEH | 07-06 | 5 | +1.98 | +0.00 | Y |
| KXITFWMATCH-26JUL06DIANIK-DIA | 07-06 | 5 | +2.54 | +0.00 | Y |
| KXWTACHALLENGERMATCH-26JUL07MONJEA-JEA | 07-07 | 15 | +3.00 | +0.00 | Y |
| KXITFMATCH-26JUL07WYGMAS-WYG | 07-07 | 10 | +4.07 | +0.00 | Y |
(a) TOTAL: 161 tickers | realized -49.35 | mark risk -0.38

## CLASS (b) naked base-lot, band touched
| ticker | day | naked sh | band | outcome | foregone $ | settled |
|---|---|---|---|---|---|---|
| KXATPCHALLENGERMATCH-26JUL07BARSIM-BAR | 07-07 | 5 | 94 | 0 | 4.70 | Y |
| KXITFMATCH-26JUL06TIMJEF-JEF | 07-06 | 5 | 91 | 0 | 4.55 | Y |
| KXITFMATCH-26JUL07MECOVC-OVC | 07-07 | 5 | 86 | 0 | 4.30 | Y |
| KXITFWMATCH-26JUL07INOBUY-INO | 07-07 | 5 | 76 | 0 | 3.80 | Y |
| KXITFWMATCH-26JUL07VRARUG-RUG | 07-07 | 5 | 75 | 0 | 3.75 | Y |
| KXITFMATCH-26JUL07BRAJAD-BRA | 07-07 | 5 | 73 | 0 | 3.65 | Y |
| KXATPCHALLENGERMATCH-26JUL06MAGROD-ROD | 07-06 | 5 | 66 | 0 | 3.30 | Y |
| KXITFMATCH-26JUL07PEDRAD-PED | 07-07 | 5 | 59 | 0 | 2.95 | Y |
| KXITFWMATCH-26JUL07DAPTEI-DAP | 07-07 | 5 | 59 | 0 | 2.95 | Y |
| KXWTAMATCH-26JUL06BOUMER-BOU | 07-06 | 5 | 57 | 0 | 2.85 | Y |
| KXITFMATCH-26JUL05GELBRE-GEL | 07-05 | 5 | 53 | 0 | 2.65 | Y |
| KXATPCHALLENGERMATCH-26JUL05LEGSHI-LEG | 07-05 | 5 | 51 | 0 | 2.55 | Y |
| KXITFWMATCH-26JUL06VLADIL-VLA | 07-06 | 5 | 49 | 0 | 2.45 | Y |
| KXATPCHALLENGERMATCH-26JUL07LEOCAS-LEO | 07-07 | 5 | 44 | 0 | 2.20 | Y |
| KXITFMATCH-26JUL06HANKUN-HAN | 07-07 | 5 | 44 | 0 | 2.20 | Y |
| KXATPCHALLENGERMATCH-26JUL07JUSKRA-KRA | 07-07 | 5 | 43 | 0 | 2.15 | Y |
| KXITFMATCH-26JUL07AGWZIC-ZIC | 07-07 | 5 | 43 | 0 | 2.15 | Y |
| KXITFWMATCH-26JUL07SADSTA-SAD | 07-07 | 5 | 43 | 0 | 2.15 | Y |
| KXITFMATCH-26JUL06VANHOR-HOR | 07-06 | 5 | 42 | 0 | 2.10 | Y |
| KXITFWMATCH-26JUL06BRESAF-SAF | 07-06 | 5 | 41 | 0 | 2.05 | Y |
| KXITFWMATCH-26JUL06WAGYOU-WAG | 07-06 | 5 | 41 | 0 | 2.05 | Y |
| KXATPCHALLENGERMATCH-26JUL06MONCOU-COU | 07-06 | 5 | 40 | 0 | 2.00 | Y |
| KXITFMATCH-26JUL07MINMIL-MIL | 07-07 | 5 | 40 | 0 | 2.00 | Y |
| KXITFMATCH-26JUL06KASLIL-LIL | 07-06 | 5 | 38 | 0 | 1.90 | Y |
| KXITFWMATCH-26JUL07PODSMI-POD | 07-07 | 5 | 37 | 0 | 1.85 | Y |
| KXATPCHALLENGERMATCH-26JUL07GUEDON-DON | 07-07 | 5 | 36 | 0 | 1.80 | open |
| KXITFMATCH-26JUL06OKITAN-TAN | 07-07 | 5 | 36 | 0 | 1.80 | Y |
| KXITFWMATCH-26JUL07EVAENC-EVA | 07-07 | 5 | 36 | 0 | 1.80 | Y |
| KXITFWMATCH-26JUL07LEKVLA-VLA | 07-07 | 5 | 34 | 0 | 1.70 | open |
| KXITFWMATCH-26JUL06PODLUK-POD | 07-06 | 5 | 33 | 0 | 1.65 | Y |
| KXITFWMATCH-26JUL07PROMAE-MAE | 07-07 | 5 | 33 | 0 | 1.65 | Y |
| KXATPMATCH-26JUL06LEHZVE-LEH | 07-07 | 5 | 31 | 0 | 1.55 | open |
| KXITFMATCH-26JUL06DONDEV-DEV | 07-06 | 5 | 31 | 0 | 1.55 | Y |
| KXITFMATCH-26JUL06OCHMUT-MUT | 07-07 | 5 | 31 | 0 | 1.55 | Y |
| KXITFMATCH-26JUL06PHATOM-PHA | 07-07 | 5 | 28 | 0 | 1.40 | Y |
| KXITFMATCH-26JUL06TAGSUZ-SUZ | 07-07 | 5 | 27 | 0 | 1.35 | Y |
| KXITFMATCH-26JUL07BELALU-BEL | 07-07 | 3 | 44 | 0 | 1.32 | Y |
| KXITFMATCH-26JUL06DEDYUN-YUN | 07-06 | 5 | 26 | 0 | 1.30 | Y |
| KXITFWMATCH-26JUL06GAONON-GAO | 07-07 | 5 | 25 | 0 | 1.25 | Y |
| KXITFWMATCH-26JUL06SACLAZ-LAZ | 07-06 | 5 | 24 | 0 | 1.20 | Y |
| KXITFWMATCH-26JUL06VAJRAM-RAM | 07-06 | 5 | 24 | 0 | 1.20 | Y |
| KXITFWMATCH-26JUL07BATBEL-BAT | 07-07 | 5 | 24 | 0 | 1.20 | Y |
| KXITFMATCH-26JUL07LAVTOR-LAV | 07-07 | 5 | 23 | 0 | 1.15 | Y |
| KXITFWMATCH-26JUL06TODSAG-SAG | 07-06 | 3 | 36 | 0 | 1.08 | Y |
| KXITFWMATCH-26JUL07KHRYOU-KHR | 07-07 | 2 | 52 | 0 | 1.04 | Y |
| KXITFWMATCH-26JUL06SIMCIR-CIR | 07-06 | 5 | 20 | 0 | 1.00 | Y |
| KXITFWMATCH-26JUL07MANLUK-MAN | 07-07 | 5 | 20 | 0 | 1.00 | Y |
| KXITFWMATCH-26JUL07SENKEN-SEN | 07-07 | 5 | 20 | 0 | 1.00 | Y |
| KXITFMATCH-26JUL06SAKLIX-LIX | 07-07 | 4 | 23 | 0 | 0.92 | Y |
| KXITFWMATCH-26JUL07BUEXAV-XAV | 07-07 | 1 | 86 | 0 | 0.86 | open |
| KXATPCHALLENGERMATCH-26JUL07ZHOCAT-CAT | 07-07 | 5 | 16 | 0 | 0.80 | Y |
| KXITFMATCH-26JUL07TEXCRA-TEX | 07-07 | 5 | 15 | 0 | 0.75 | Y |
| KXITFWMATCH-26JUL07YARHAY-YAR | 07-07 | 3 | 25 | 0 | 0.75 | Y |
| KXWTACHALLENGERMATCH-26JUL05KOBLEW-LEW | 07-05 | 5 | 13 | 0 | 0.65 | Y |
| KXITFWMATCH-26JUL06VARMUN-MUN | 07-06 | 4 | 15 | 0 | 0.60 | Y |
| KXWTACHALLENGERMATCH-26JUL07KABSHE-KAB | 07-07 | 3 | 19 | 0 | 0.57 | Y |
| KXITFWMATCH-26JUL07PUSMAY-MAY | 07-07 | 5 | 10 | 0 | 0.50 | Y |
| KXITFMATCH-26JUL07BELKOS-KOS | 07-07 | 5 | 9 | 0 | 0.45 | Y |
| KXITFMATCH-26JUL07MOUMON-MOU | 07-07 | 5 | 42 | 33 | 0.45 | open |
| KXITFMATCH-26JUL07URSPOU-POU | 07-07 | 0.68 | 63 | 0 | 0.43 | open |
| KXATPCHALLENGERMATCH-26JUL06ERHSIN-SIN | 07-06 | 5 | 8 | 0 | 0.40 | Y |
| KXATPCHALLENGERMATCH-26JUL05MARHAI-MAR | 07-05 | 5 | 7 | 0 | 0.35 | Y |
| KXATPCHALLENGERMATCH-26JUL07WALVAL-WAL | 07-07 | 0.87 | 40 | 0 | 0.35 | Y |
| KXITFWMATCH-26JUL06BUYALV-ALV | 07-06 | 1 | 34 | 0 | 0.34 | Y |
| KXITFMATCH-26JUL07STECHA-CHA | 07-07 | 3 | 9 | 0 | 0.27 | Y |
| KXITFWMATCH-26JUL07GUESAN-SAN | 07-07 | 1 | 11 | 0 | 0.11 | Y |
| KXITFWMATCH-26JUL07SCHTRI-SCH | 07-07 | 0.29 | 37 | 0 | 0.11 | Y |
| KXITFWMATCH-26JUL07GIADIA-DIA | 07-07 | 0.46 | 65 | 45 | 0.09 | open |
| KXITFWMATCH-26JUL07EVAGOW-GOW | 07-07 | 0.72 | 18 | 7 | 0.08 | open |
| KXITFWMATCH-26JUL07PATMAK-PAT | 07-07 | 1 | 4 | 0 | 0.04 | Y |
| KXITFWMATCH-26JUL06PEEPAH-PEE | 07-06 | 0.06 | 45 | 0 | 0.03 | Y |
| KXITFWMATCH-26JUL07MELROD-ROD | 07-07 | 0.2 | 26 | 13 | 0.03 | open |
| KXITFWMATCH-26JUL07MALKOM-KOM | 07-07 | 0.1 | 13 | 0 | 0.01 | open |
(b) TOTAL: 73 legs | foregone 110.72 (settled portion 103.72)

## CLASS (c) fractional residues: 25 legs | net +0.67
| KXATPCHALLENGERMATCH-26JUL07WALVAL-WAL | 07-07 | 0.87 | -0.28 |
| KXITFMATCH-26JUL06LUEVAN-LUE | 07-06 | 0.34 | -0.25 |
| KXITFMATCH-26JUL06GARCIO-CIO | 07-06 | 0.59 | -0.24 |
| KXITFWMATCH-26JUL07PROMAE-MAE | 07-07 | 0.62 | -0.18 |
| KXITFWMATCH-26JUL06ZRNLUE-ZRN | 07-06 | 0.72 | -0.17 |
| KXITFWMATCH-26JUL06VAJRAM-RAM | 07-06 | 0.97 | -0.15 |
| KXITFWMATCH-26JUL06GAONON-GAO | 07-07 | 0.52 | -0.10 |
| KXITFMATCH-26JUL05MASCIO-MAS | 07-05 | 0.27 | -0.09 |
| KXITFWMATCH-26JUL07EVAGOW-GOW | 07-07 | 0.72 | -0.05 |
| KXITFMATCH-26JUL06HERNAG-NAG | 07-06 | 0.29 | -0.05 |
| KXITFWMATCH-26JUL07GIADIA-DIA | 07-07 | 0.46 | -0.04 |
| KXITFWMATCH-26JUL06PEEPAH-PEE | 07-06 | 0.06 | -0.02 |
| KXITFWMATCH-26JUL07MELROD-ROD | 07-07 | 0.20 | -0.02 |
| KXATPCHALLENGERMATCH-26JUL07HAMWAL-HAM | 07-07 | 0.01 | +0.00 |
| KXITFWMATCH-26JUL07EVAGOW-EVA | 07-07 | 0.28 | +0.01 |
| KXITFMATCH-26JUL07STECHA-STE | 07-07 | 0.78 | +0.10 |
| KXITFWMATCH-26JUL06GAONON-NON | 07-07 | 0.55 | +0.14 |
| KXITFMATCH-26JUL07CHOCHE-CHO | 07-07 | 0.45 | +0.15 |
| KXITFWMATCH-26JUL07POCINI-INI | 07-07 | 0.67 | +0.16 |
| KXITFMATCH-26JUL07MABROS-MAB | 07-07 | 0.98 | +0.22 |
| KXITFWMATCH-26JUL06LABTSY-TSY | 07-06 | 0.59 | +0.22 |
| KXITFMATCH-26JUL06LENTHE-LEN | 07-06 | 0.34 | +0.23 |
| KXITFWMATCH-26JUL07PROMAE-PRO | 07-07 | 0.86 | +0.28 |
| KXITFWMATCH-26JUL07TAHHUR-HUR | 07-07 | 0.72 | +0.29 |
| KXATPCHALLENGERMATCH-26JUL06HUETEN-TEN | 07-06 | 0.71 | +0.50 |

## DAILY GROSS (realized) | fees total 1.13
| day | gross $ | mechanical $ | strategic residual $ |
|---|---|---|---|
| 07-05 | -3.66 | -9.17 | +5.51 |
| 07-06 | +17.22 | -42.23 | +59.45 |
| 07-07 | -86.37 | -102.71 | +16.34 |
```
