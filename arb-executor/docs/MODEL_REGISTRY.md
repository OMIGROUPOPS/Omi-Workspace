# MODEL REGISTRY — every fitted model we own (2026-07-10; clock-era admissibility per the 07-10 census: ITF = live-era only · CHALL = archive ±30 min COARSE · mains = CONVICTED)

| # | model | lifecycle step | artifact path | categories | validation status | clock-era admissibility |
|---|---|---|---|---|---|---|
| M1 | Sequential-floor recut (edge_p50, cell-keyed) | L4 aim / L5 place | `.claude/seqfloor_20260708/recut_cells.json` | all 6 (90-cell grid) | RATIFIED (RULING_DYNAMIC_S_CELL_AIM) | fitted on June–July live tape → ADMISSIBLE all cats incl. ITF |
| M2 | Aim table (dip depth per cat/bucket) | L4 aim / L5 place | `aim_table.json` (deployed ba08243) | all 6 | DEPLOYED, armed (per_cat_depth) | live-era fit → ADMISSIBLE |
| M3 | Volume ledger recut (fill-rate vs volume bands; never-wake floor) | L2 qualify / L4 | `.claude/volume_20260709/recut_cells_volume.json` + VOLUME_LEDGER.md | all 6 | evidence FILED (floor ruling: EXECUTED as early-unlock 2,500) | live-era → ADMISSIBLE |
| M4 | Fill-rate REDO (spread-relative depths; the traverse) | L4/L5 | `.claude/fillredo_20260709/` | all 6 | study DONE; mains-JOIN thesis vindicated | live-era → ADMISSIBLE |
| M5 | Entry tables (per_regime_offsets_v2 / entry_table_cell) | L5 place | in config/live_v4 | active cats | LIVE (legacy fit) | pre-census fit — era-mixed: COARSE ONLY; refit queued (aim-surface refit) |
| M6 | Exit band table (cell → band_x) | L7 exit | live_v4 exit tables | active cats | LIVE; **FV-blind BY DESIGN (−0g ruling pending)** | era-mixed: legacy — graded, not trusted as conviction |
| M7 | AIM_V2 operational (latch-calibrated) | L4 | `data/shape_corpus/aim_v2_operational_LATCHCAL.json` | per-tier | GATED OFF (honest n 0/500 — BLOCKED-ON-DATA) | corpus era-mixed; honest-weight ruling pending (−1c) |
| M8 | Shape corpus + bell recovery | L3 window / L4 | `data/shape_corpus/` (+349 recovered bells) | all | TRAINING-GRADE ONLY (33.9% ±5min) — **FORBIDDEN as certification truth** | training only, never a clock |
| M9 | match_facts_v3 mid-jump clocks | L3 (archive T-relative) | `data/match_facts_v3.csv` | ATP/WTA main+CHALL — **NO ITF ROWS** | census 07-10: CHALL jump-slice ±30m coarse; fallback 76 + no_bbo 444 EXCLUDED | mains CONVICTED · CHALL coarse · **ITF: NOTHING — live era is ITF's only clock** |
| M10 | Fused-gun sources + fallback bell | L3 match-live | live_v4 `_gun_poll`/`_gun_stamp` | all | certification PENDING (±3-min bar; truth-join fixed 07-09; night-3 blocked by −0e halts) | live-era by construction |
| M11 | Hold-gate dual readings (quiet/floor) | L6 hold | `oslayer/holdgate.py` | all | SHADOW (T4 clock started 07-09 9:23:59 pm; threshold = Plex's) | live-era shadow |
| M12 | OS decision core (regime/timing/posture) | L4–L6 | `oslayer/decision_core.py` | all | SHADOW (os_active dormant, 4 conditions open) | cites M1/M2 — inherits their eras |
| M13 | Flow-state gauge thresholds | L2/L3 | monitor + fallback bell constants | ITF/CHALL (mains excluded) | PROVISIONAL (early-canvas fit; bell fires self-graded nightly) | live-era |
| M14 | Stranded-winner β / entry-blend arcs | L5 posture | `analysis/stranded/`, entry-blend arc docs | studied cats | NO-SHIP verdicts (graves with lessons) | historical studies — context only |
| M16 | **ITF_M fitted refuse margin (8¢)** | L5 grade | `.claude/book_replay/BOOK_REPLAY_V2.json` refits.refuse_margins | ITF_M ONLY (category law: the other five cats' fits LOST held-out and were REFUSED entry; ITF_W's evidence favors the decreed 2¢) | SHADOW (nightly REFUSE-MARGIN line; held-out +1170¢ vs −85¢; caveat NAMED: train-window sign flip — small-sample caution) | live-era corpus (2,953 legs, walk-forward split) |
| M-corpus | Back-adjudicated book (every settled leg Jun 26→Jul 10, composer-graded at its recorded tick, ids per era) | all | `.claude/book_replay/BOOK_REPLAY_V2.json` corpus | all 6 | THE refit substrate; completion-params + participation tables ride as evidence feeds | live-era |
| M15 | **Three-price range layer** (WINDOW_MAP_3WAY axes: fill−runmid bucket × price cell × W1/COR/W2, per cat per side; reach/win/cash/knife) | L4–L7 anchor | `.claude/range_layer/RANGE_LAYER_3WAY.json` (builder `analysis/range_layer_build.py`) | all 6 (2,783 era-admissible legs, 204 cells, 112 at n≥5) | composer-wired (range_prior; gate test iv PASS); archive-CHALL coarse addendum pending | live-era book Jun 26→today; census law in header; ITF live-only by construction |

**NAMED GAPS (no admissible anchor — the composer must return NO-OPINION here, never a guess):**
- **G1: W1 direction prior, mains** — mains clocks convicted + mains excluded from gauge fits → no admissible discovery-time direction model for ATP_MAIN/WTA_MAIN.
- **G2: ~~per-category W1 volatility map~~ — FILLED 07-10 by M15** (the June WINDOW_MAP_3WAY framework era-stamped, not a new invention); residual: archive-CHALL coarse addendum + thin cells (92/204 under n=5) stay NO-OPINION.
- **G3: in-play price model** — beyond the tape itself, nothing fitted for in-play dynamics (by §0A design: exits solved on foundation; entries premarket). Posterior in-play = tape-weighted only.
- **G4: ITF archive T-relative ranges** — do not exist (M9 has no ITF); anything T-relative for ITF must come from live-era artifacts (M1–M4, M13).
- **G5: cash-convention** — dollar-precise conviction grading blocked pending −1a000.

**INDEXED STUDIES (June; cited by RULING_PAIR_ECONOMICS — evidence, not live anchors):**
- **COMPLETION_FUNNEL (Jun 24–30):** 406 pairable · 72% completed · 93 strands · −$50.65 realized.
- **ADVERSE_SELECTION_STRANDED:** kept leg loses 65%; maker bid on the winning sibling structurally starved; verdict: cross to complete, or never hold the kept leg naked.
- **HELD_IF_NOT_CANCELLED:** 43% win · −$653 counterfactual under band-asymmetric exits; the pre-start cancel is protective and stays.

> **COMPOSER LIVE-SIDE (07-11, C-COMPOSER-G1 v1):** M12's composer twin now runs in-process (`conviction_shadow` at every decision site; O(1) incremental posterior; purity lint-asserted). G1 distance: 371 settled mains legs + 20,332 mains tape samples banked — fit at honest n, never before.


**EV3 TRIAL NOTE (07-13, C-EV3-BACKTEST):** the three-term frame graded on 264 held-out legs (Jul 11-13 vs M15 trained through Jul 10, leash floor applied): EV3 +$7.70 vs actual +$2.35 vs two-term +$5.75; EV3-minus-actual +$5.35 with 95% CI [-20.20, +29.10] -> FLAT-AT-INSUFFICIENT-N (n<300 pre-agreed bar). Leash stays; posterior-proxy variant grades below cell-only (1/264 flattens) -> posterior wiring not earned. Re-read at accrued n>=300.

**GUIDEBOOK V1 NOTE (07-13, C-GUIDEBOOK-AIM):** M1+fillredo+M6 composition (538 pages) REFUSED by the held-out week replay (-$9.90 vs -$0.62 actual; 114 fills on 247 aims). Built, gated OFF. v2 direction: condition depth on dip TIMING (t_deep page, unexploited) + the three-price shape axis.

**GUIDEBOOK V2 NOTE (07-14, C-GUIDEBOOK-V2):** timing-conditioned recut on G9 (48 pages, tour only -- NO admissible ITF corpus exists, named). Held-out week: -$10.70 vs -$9.30 actual -> THIRD REFUSAL, dark. Partition check PASSED (8/4 vs v1 collapse-skew): the timing axis fixes WHO fills. Windows diffuse ([13,508]/[91,996] min) -- the discount is not a clock moment; v3 = flow-signature conditioning after ITF tape accrual.

**LIVE-AIM NOTE (07-14, C-LIVE-AIM v1):** fourth aim design, SHADOW: prior (GUIDEBOOK_V1 page) x live state (flow_ratio vs M3/M13 curve, depth_trend, spread, print_sig); lib_conf = banked-tape confidence per cat (accrual-aware); nightly LIVE-AIM SHADOW line; forward cutover bar n>=300 + CI clear of zero + operator word.

**LIVEAIM-BACKTEST NOTE (07-14):** discovery-instant replay N=741 era-clean: engine +9.50 vs actual +11.20 (CI [-34,+34]); AIM_DEEP fired 1x -- the moment-forming mechanism is a re-aim-time phenomenon, unmeasurable at discovery instants. Acceleration refused; forward bar unchanged.

**REACH LAW (07-14, C-TAKER-REACH v1) — THE FILL JUDGE:** P(fill at depth X over residency R) = 1-exp(-rate_X*R); rates per cat|flow from G9 taker-sell sweeps (< Jul 10, walk-forward) + live-era ITF (branded). Week re-grade: E$+39.61 vs actual +$11.20, yield 15.4-16.0% vs 8% bar incl. pessimistic x0.5; N=244 (underpowered, CI [-3.05,+58]); doors closed on the letter; forward clock stands. THE HARVESTABLE MAP: the harvest lives in OPEN flow (ITF_W|open 68 five-cent-reach sweeps/hr; quiet ~0). .claude/takerreach/LAW.json
