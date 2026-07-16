# C-PROVE-THE-DAY v1 — the would-have day (2026-07-15, midnight → ~5 PM ET, one integrated pass)

## PRIOR ART (C45)
- The 5 PM stack this proves, deployed today in sequence: C-DISCOVERY-FLOOR (`ea0544c8`) · C-TAPE-BELL + W2 zero-tolerance + W1-PREFERENCE + cross cap + healer (`23a097ac`) · C-DAILY-STANDARD Part 0 per-source grace + Layer 3 stamps (`f5ef2864`). Their individual replays: PROOF_DISCOVERY_FLOOR.md (9 events), tapebell acceptance (77 rows), PROOF_DAILY_STANDARD.md (grace conversion). **Delta: this is the INTEGRATED pass — one machine, fates composed across guards, one dollar verdict.**
- liveaim_backtest / fullwindow replay: the replay-harness law (fills judged on the real tape). Inherited.

## THE ACCOUNTING RULES (stated, binding on every number below)
1. **Subtractive by construction.** The new chain only ADDS refusals (floor, preference, clamp) and sweeps (tape-bell + 60s grace). No bid exists in the would-have day that did not exist in the actual day — so no fills are invented, no market-impact claims are needed, and every counterfactual is a REAL fill removed size-aware at its booked price.
2. Counterfactual fill deaths are scored only where the guard's predicate is MEASURED (exchange tape at the decision instant for the floor; the recorded corridor stamps for preference; the tape would-fire + 60s for the sweep) — never assumed.
3. Exits and settles are the existing machinery's booked outcomes against the real tape; open legs are marked at the current exchange bid vs basis.
4. Aims are unchanged both days (path aims; the seeded gauge feeds the record, not the aims — behavior isolation 201/201, proven at the R1 deploy). The 5–95 clamp ran live BOTH days (no delta; refusal counts cited).

## PART 2 — SIDE-BY-SIDE (per-fill fates: `prove_the_day.json`, 135 rows)
| measure | ACTUAL day | WOULD-HAVE day |
|---|---|---|
| entry fills booked (midnight → ~5 PM) | 135 | 59 (76 die lawfully) |
| — killed at conception (discovery floor, measured tape) | — | 2 (ALHVUX −385¢ avoided · KOAYAZ +85¢ forgone — both cited) |
| — killed at placement (W1-PREFERENCE, corridor mains) | — | 1 filled leg dies (+80¢ forgone); 11 corridor mains placements refused in all (10 never filled — placements die harmless, named by ticker in the JSON) |
| — swept by the tape-bell + 60s grace (death timestamp per row) | — | **73** (removed net −333¢: 47 winners +2,257¢ vs losers −2,590¢ — the bell kills both sides; the losers dominate) |
| W2-stamped fills (the violation class) | **92** | **18** (14 fire-but-margin<60s · 1 no-fire GUTSHA · 3 post-3:37 live-bell era) |
| 5–95 leg clamp refusals | 54,673 dossier lines | identical (live both days — no delta by construction) |
| pair-seesaw refusals | 71 | identical |
| realized P&L | **−538¢** | **+15¢** |
| marked P&L (open legs, snapshot) | 0¢ measurable | 0¢ measurable |
| **THE HEADLINE DELTA** | | **+553¢ = +$5.53** |

The 92 W2 fills' fates individually (the operator's 75 + the day's growth to 92): every row in `prove_the_day.json` carries fill time, price, fate, why (with the bell's death timestamp where swept), realized P&L, and open/closed state.

**Supersession note (chronology law):** the committed tape-bell acceptance (77 rows: 76 fires / 54 before-fill / 37 catches) ran with gun anchors poisoned by a substring-match bug (window stamps' `gun_fired: false` matched the gun-line filter, first-wins) — its catch counts were FLOORS. This pass parses event fields exactly; its fates supersede the acceptance's per-row fates. Direction of the error was conservative, as an acceptance should be.

## PART 3 — THE FUNCTIONAL VERDICT (per guard: fired everywhere it should, zero misfires on lawful behavior — cited, or the miss named)
| guard | fired where it should? | misfires on lawful behavior? |
|---|---|---|
| ≥1,500 discovery floor | YES — 2/2 measured under-floor conceptions killed (ALHVUX 60 sh, KOAYAZ 9 sh); live instance post-deploy: VUKARS (stale-dated JUL14, refused, cited in the log) | ZERO — every fresh-dated W1 conception passed (predicate scope holds; the smoke replay showed the same) |
| W1-PREFERENCE | YES — all 11 corridor mains placements refuse (by ticker) | ZERO — 0 ITF corridor placements today, so the fallback clause cost nothing; no W1 placement touched |
| 5–95 leg clamp | live BOTH days, 54,673 refusal lines — no delta by construction | ZERO new (pre-existing guard, unchanged) |
| seeded-gauge aims | aims unchanged both days (gauge feeds the record, not the aims — isolation 201/201 at the R1 deploy) | ZERO |
| tape-bell + 60s grace | fires on 91/92 pre-deploy-cohort W2 events; sweeps 73 before their fills (death timestamps cited per row) | **the FERCER watch stands**: the rise-escape can fire early on drifting premarket tape — nightly scorecard grades every fire; no lawful W1 bid was swept in this replay (sweeps key on fires past honest start or 5¢ rises on sustained tape) |
| W2 zero-tolerance | 92 violations actual → 18 would-have; **target 0 named and missed honestly**: 14 sub-60s margins (onset-adjacent) + 1 no-fire + 3 live-bell era | ZERO false violations (every flagged fill genuinely booked in W2) |
| IOC cross cap | no over-par cross existed today to refuse (0 instances; DELXIL was 07-14's tape — the cap's founding replay) | ZERO |
| band-0 healer | would have flagged, not halted, all 3 audit-race halts (JONURG + DARCRI fill-race, MASDUT settlement-race) — conception uptime saved ≈ 11 halt-minutes | ZERO (flag paths only) |

## PART 3b — THE DRESS REHEARSAL (tonight's 12:20 machinery, run early — `ADJUDICATION_20260715.md`, regenerated in full by the real 12:20 cron)
**THE STANDARD CENSUS: all four keys RAN.** L1_three_bucket: 135 fills / 700 placements graded · L2_game_reports: **405 reports** generated · L3_cash_window: 162 dossiers stamped · P0_grace_census: 3 sources graced.
**The three-bucket grade rendered per the operator's frame** — and independently confirms the day's diagnosis: ITF_M SETTLED 53 with **36 graded F(W2-entry)**, Σ−1,303¢; ITF_W 33 of 44 F(W2-entry); the F(W2-entry) class IS the bleed the would-have day removes. (Grades and dollars per cat in the artifact.)
**The grace census printing per-source:** tape_flow 4 graced windows @60s · percat_fitted 4 @300s · **finding: 494 graced windows stamped `unstamped`** (the volume-burst latch arms grace before any gun stamp exists — a naming gap in the latch path, filed to census intake; behavior unchanged, the 300s default applies).
The reporting stack is proven end-to-end before its first real night.

## PART 5 — THE EARNING REPLAY (the story; no threshold verdict)
Full doctrine expressed over the day's 394 considered events: selector TRADE/DROP (fitted, as-is) → path aims per page → role-timed postures (fav rests from consultation; dog joins at the late floor, anchor−2h) → guards on top (tape-bell sweep at would-fire+60s) → baby sizing. Fill law: real prints crossing the hypothetical bid, size-aware (cum size at-or-below bid ≥5); exits by the band machinery on the real tape; settles by market result.

**THE STORY (dollars first; yield WITH participation, every row):**
| cat | window | offered | taken | wagered | earned | yield w/ participation | DROP left on table |
|---|---|---|---|---|---|---|---|
| ATP_CHALL | W1 | 1 | 1 | $2.50 | +$0.65 | +26.0% w/ 100% (1/1) | $0 |
| ATP_CHALL | CORRIDOR | 6 | 5 | $11.00 | +$2.20 | +20.0% w/ 83.3% (5/6) | +$0.40 on 1 |
| ATP_MAIN | CORRIDOR | 1 | 1 | $1.40 | +$0.30 | +21.4% w/ 100% (1/1) | $0 |
| ITF_M | W1 | 10 | 8 | $20.10 | +$2.30 | +11.4% w/ 80.0% (8/10) | −$2.90 on 2 |
| ITF_M | CORRIDOR | 16 | 16 | $31.00 | +$0.75 | +2.4% w/ 100% (16/16) | $0 |
| ITF_W | W1 | 4 | 4 | $9.35 | +$2.40 | +25.7% w/ 100% (4/4) | $0 |
| ITF_W | CORRIDOR | 21 | 21 | $37.15 | +$0.60 | +1.6% w/ 100% (21/21) | $0 |
| WTA_CHALL | W1 | 1 | 1 | $1.40 | +$0.30 | +21.4% w/ 100% (1/1) | $0 |
| WTA_CHALL | CORRIDOR | 6 | 5 | $12.90 | +$2.80 | +21.7% w/ 83.3% (5/6) | +$0.20 on 1 |
| WTA_MAIN | W1 | 1 | 1 | $0.70 | +$0.00 | 0.0% w/ 100% (1/1) | $0 |
| **TOTAL** | | **68** | **64** | **$127.50** | **+$12.30** | **+9.6% w/ 94.1% (64/68)** | −$2.30 net |

**THE ROLE SPLIT (the standing number, first print):** favs positive in every lane (ITF_M corridor fav +6.7% / W1 fav +10.4%; ITF_W corridor fav +10.9% / W1 fav +25.9%; CHALL favs +22–26%). **The leak has a name: ITF dog-side CORRIDOR** — ITF_M dog corridor −8.9% (7/7 taken, $8.45 wagered, −$0.75) and ITF_W dog corridor **−21.7%** (11/11, $10.60, −$2.30) — at FULL participation, so no ratio flattery. Dogs in W1: tiny n, positive (+23.8%/+31.6% on 1-leg samples). The recut conversation starts from this row: the dog-side corridor posture (join-at-late-floor) is where the story's dollars leak; W1 lanes and fav-side postures carry the earning.

The 8% figure above is the operator's standing scaling reference — his decision line, never a target; today's story runs +9.6% at 94.1% participation on $127.50 wagered.

**The number pairing law (permanent, this dispatch):** yield and participation print together above, per row, with the dollars — no component shrank participation to flatter a ratio. The 8% figure is the operator's standing scaling reference — his decision line, never a target.

**Baseline reconciliation (the number law):** the operator's exchange-truth read **$751.81 (his window, as stated)**; the API cash balance at the earning replay's generation instant (~6:05 PM ET) printed **$736.01** — the gap is the afternoon's realized settles and fees between the two windows, both figures exchange-sourced, windows stated beside each. From tonight the equity recorder (C-FUND-TRACKER, 60s cadence) owns this number continuously — cash + marked = fund equity, one ledger, and this reconciliation question stops existing by construction.

**The AM outage window, marked:** the deploy-stop-window incident's dead gap (02:28:35→02:36:35 AM ET, 8 minutes, healed by manual restart at the gated SHA — vault −0l) sits inside today's timeline; no fills or opportunities inside it are claimed by either day.

## HONEST LIMITS
1. The would-have day's surviving W2 fills are not zero — the onset-is-the-fill class (fill print rides the opening burst) is structurally uncatchable by flow evidence, and sub-60s margins remain; each is named in the fates table. The target is named and missed honestly where it is missed.
2. Pre-deploy W2 fills are judged by the replay's would-fire; post-3:37 PM fills are the LIVE bell's account and are marked as such.
3. Marks move; the marked column is a snapshot at generation time, stamped.
