# SESSION HANDOFF — current

**Convention:** This file is ALWAYS the current handoff — overwrite in place at end of each session. Numbered SESSION{N}_HANDOFF.md files in `docs/handoffs/` are frozen historical snapshots; do not edit them.

**Last updated:** 2026-06-05 UTC (BBO-threshold settlement-cancel SAFETY fix LIVE on top of RUN-7).
**Repo state:** HEAD `d05d0e6e` (BBO-settlement gate; RUN-7 strategy unchanged — config `b40b863c` / code lineage `104feeaa`). Atlas + foundation chain canonical on origin/main.

## BBO-THRESHOLD SETTLEMENT-CANCEL SAFETY FIX — LIVE (restart 2026-06-05T04:51:11Z)

**Deployed:** commit `d05d0e6e` (FF on VPS from `313c7c93`) + config flag flipped. **Blob-verified RUNNING:** on-disk `live_v4.py` == `418b4ecb`; PID **2904327**; `disable_bbo_threshold_settlement=true` loaded; 0 tracebacks; reconcile clean (0/0, flat at restart).

**The bug (SAFETY):** `check_settlements()` treated a price touching `best_bid>=98` / `best_ask<=2` as settlement → `process_settlement()` → cancelled the resting exit (`settlement_cleanup`, :2782). Prices ROUND-TRIP to extremes mid-match — that is NOT settlement. Blast radius (RUN-7 cohort): bbo_threshold was the settlement source for **4 of 5** settlements (**ws_lifecycle fired 0×**, rest_poll 1×); **all 4 fired 7m-1h52m before real settlement; 1 wrong-direction** (MARPAL-PAL settled LOSS via bbo at 18:35:14Z, cancelled its 17c exit, market settled YES at 20:27:34Z — won by luck). Every resting exit was pulled early on a false price signal.

**The fix (gated `disable_bbo_threshold_settlement`, default False = byte-identical):** early-return in `check_settlements` so the BBO heuristic is NEVER a settlement source — never closes a position, never cancels an exit. The inherited-verbatim Bug-4 path (line 16-18 "DO NOT modify") is GATED not rewritten. After the fix, a resting exit cancels ONLY by: (a) its own fill, (b) `process_settlement` from `ws_lifecycle`/`rest_poll` (real exchange settlement, unchanged), (c) `v4_exit_reset`/`exit_consolidate` (cancel-AND-repost, never naked). Test: `tests/test_bbo_settlement_gate.py` drives the REAL `check_settlements` (gate ON → no (bid,ask) over the full 0..100² grid triggers settlement) + full 12-file suite green.

**Cohort:** RUN-7 strategy baseline CONTINUES (safety fix). Restart `2026-06-05T04:51:11Z`; pre-stop snapshot cutoff `2026-06-05T04:50:34Z` (flat). Prior log archived VPS `/tmp/live_v4_c55c4819_pre-d05d0e6e.log`.

**OPEN (read-only, do NOT conflate with deploy):** (1) is the bot actually trading vs legitimately flat between waves — discovery=72 tickers at restart, WS_SUBSCRIBED 72. (2) **ws_lifecycle settlement fired 0× all cohort** — primary WS settlement path appears dead; bbo+rest_poll covered. With bbo now off, settlement leans on rest_poll. Investigate WS feed health (does it affect discovery/book/position too).

## MARKETABLE-CLAMP (3RD CROSS SITE) — LIVE (restart 2026-06-05T03:47:23Z)

## MARKETABLE-CLAMP (3RD CROSS SITE) — LIVE (restart 2026-06-05T03:47:23Z)

**Deployed:** commit `313c7c93` (FF on VPS from `e4fd9f7`) + config flag flipped. **Blob-verified RUNNING:** on-disk `live_v4.py` == `c55c4819`; PID **2862656**; `marketable_clamp_placement=true` loaded; run7 table + deploy_v5_live.json; 0 tracebacks; reconcile clean (0 pos / 0 resting at restart — bot was flat).

**The fix (correctness on top of RUN-7, not a strategy change):** the entry placement had a THIRD taker cross site never fixed by RUN-7 — the initial-placement branch crossed taker whenever `target_bid >= current_ask` (`marketable_taker`). RUN-7 had already clamped the reprice path (`_reprice_target`) and the T-20m fallback (`_fallback_order`) to ask-1 maker, but not this one. Live forensics (RUN-7 cohort, 6 takers): **5/6 crossed here with fillable taker-sell flow within 0-4c of our bid** (two AT/BELOW it) — premature crosses, not firming legs. Now gated by **`marketable_clamp_placement=true`**: when `target_bid >= ask` and NOT `force_cross`, clamp to `max(1, ask-1)` post_only maker (`entry_mode=marketable_clamp`) and rest, instead of lifting. Same clamp already proven on the other two sites.

**Preserved / untouched:** round5 `force_cross` still crosses (gate is `and not force_cross`); the late `miss_fallback` cross (`time_to_start <= V4_T20M_SEC`, buffer-futility) is unchanged (that is the RUN-8 buffer question). Manage-side: cancel-on-marketable exemption + T-20m re-fallback exclusion extended to `marketable_clamp` so the ask-1 bid rests like `fallback_maker` to T-15m/fill (both gated — dead when flag off).

**Cohort:** RUN-7 strategy baseline **CONTINUES** (correctness fix — stops premature placement-path taker crosses; not a new strategy). New **correctness boundary = restart `2026-06-05T03:47:23Z`**: from here, marketable placements rest ask-1 maker instead of crossing. Pre-stop snapshot cutoff `2026-06-05T03:46:25Z` (bot flat: 0 pos / 0 resting). RUN-7 ask-1-maker-era log archived to VPS `/tmp/live_v4_8961e5a6_pre-313c7c93.log`. Test: `tests/test_marketable_clamp_placement.py` (source-pins + placement-mode truth-table) + full 11-file suite green.

**Verify next is_taker pass:** taker entry rate should drop further (was ~45-55% maker-fill cohort; these premature crosses convert to `marketable_clamp` maker rests). Watch `marketable_clamp` play_type fills behave like clean maker fills (88-90% exit-reach), not a hidden adverse cohort.

## LOCKED-BOOK GUARD FIX — LIVE (restart 2026-06-04T18:21:49Z)

**Deployed:** commit `e4fd9f7f` (FF on VPS from `64ae2ce3`). **Blob-verified RUNNING:** on-disk `live_v4.py` == `8961e5a6` (file hash, not logs); PID **2524137**; guard line now `book.best_bid > book.best_ask`; run7 table + deploy_v5_live.json loaded; 0 tracebacks.

**The fix (one char, correctness — NOT a strategy change):** the universal anti-degenerate entry guard used `best_bid >= best_ask`, which collapsed **LOCKED** books (bid==ask, a tight fully-priced two-sided market) into the `degenerate_book_skip` and silently discarded ~**22 investable entries/day** across all 4 categories — including the one Roland Garros main-draw market seen (`KXWTAMATCH-26JUN04KOSAND`, 43/43). Changed to `>`: only genuinely **CROSSED** books (bid>ask, a real book artifact) skip; locked books now place. Untouched real fences: `best_bid<=0`, `best_ask>=100`, `side_skip_stale_book` (BOOK_STALENESS_SEC=900). Byte-identical on every non-locked book (proven in test). Plex + apply_delta(L1671)/apply_snapshot 100-flip source-verified — no book-collapse source.

**Verification hook (telemetry only, NOT a gate):** `v4_place` now logs `book_bid`/`book_ask`/`book_spread`/`locked_book` on the entry_resting placement. Next is_taker-truth pass: confirm locked-book (`locked_book=true`) fills behave like normal tight-market fills, not a hidden adverse cohort.

**Cohort:** RUN-7 strategy baseline **CONTINUES** from `2026-06-03T18:56:26Z` (this is a correctness fix on top of RUN-7, not a new strategy — the maker-fill cohort keeps growing N). The locked-book **correctness boundary = restart `2026-06-04T18:21:49Z`**: markets that would previously have been degenerate-skipped now place from here on. JUN-date stale exclusion (`-26JUN01-`/`-26JUN02-`) still holds.

**Deploy snapshot:** pre-stop reconcile cutoff `2026-06-04T18:18:56Z` → 2 positions / 2 resting / 0 orphans. Stopped SIGINT-graceful (state continuously persisted via `_save_v4_resting` + exchange reconcile on boot). Post-restart reconcile: **2 positions / 2 resting / 0 orphans / 0 unmanaged** — clean carryover, no naked positions. RUN-7 cohort log archived to VPS `/tmp/live_v4_RUN7_3335727d_pre-e4fd9f7.log`. Test: `tests/test_run7_locked_book.py` (source-pins `>` + truth-table) + full 10-file suite green.

**NEXT (unchanged, held):** T51 hardening → RUN-8 buffer relaxation (ATP_CHALL #1 candidate — confirmed: all 19 ATP_CHALL ask-1 clamp bids T-15 buffer-cancelled, 0 filled; the flow they need lives in T-15→T-0).

## RUN-7 LIVE — ATP_CHALL trade-floor offsets + ask-1 maker fallback (restart 2026-06-03T18:56:26Z)

**Deployed:** `b40b863c` (config) / `104feeaa` (code). **Blob-verified RUNNING:** on-disk `live_v4.py` == `3335727d` (file hash, not logs); PID 2178215; `_fallback_order` present; run7 table loaded.

**The two safe levers (one regime change, config-gated, ENTRY_BUFFER_SEC untouched):**
- **Lever A — ATP_CHALL trade-floor offsets:** `entry_table_cell_path → entry_table_percell_run7.csv` (HYBRID: ATP_CHALL recalibrated to the actual trade-print floor [PMU price_low, reach60 on the reachable T-15..T-180 window], 62 cells; WTA_CHALL + both mains KEEP `_minrule`). Print-truth walk: ATP_CHALL fill **54→68% (+14pp)** at ROC 14.6→12.1 (volume-for-edge). Mains NOT recalibrated — print-truth showed it hurts them (−1/−2pp; candle-vs-print gap is a thin-Challenger artifact).
- **Lever B — ask-1 maker fallback:** `fallback_maker_clamp=true`, `fallback_min_before_start=20`. The T-20m fallback now re-posts an **ask-1 MAKER** (`post_only=True` via `_fallback_order`/`_reprice_target`) instead of crossing taker — no premium/fee, forfeits the (net-negative-live, −$0.16/leg per RUN-5) certainty floor. Fires at T-20m for the T-20→T-15 window. `entry_mode=fallback_maker` fires it once + scopes a cancel-on-marketable EXEMPTION to that bid only (normal drifted bids still cancel; degenerate still cancels). Tests: t60 (12) + full 9-file suite green.

**Cohort: NEW RUN-7 baseline cutoff = restart `2026-06-03T18:56:26Z`.** The RUN-6/RUN-7 boundary is this restart ts; JUN-date exclusion still holds for stale (`-26JUN01-`). RUN-7 is the clean control baseline for the RUN-8 buffer experiment (ATP_CHALL is the #1 relaxation candidate).

**RUN-7 baseline snapshot (at stop):** cash **$2,724.08**, **3 open positions**, 8 resting, settlements 24h net **+$6.45** (gross $95.00 / cost $87.30 / fees $1.25). NOT-FLAT; proceeded (entry-only config-gated change, operator-authorized). Flipped 3 keys: `entry_table_cell_path→entry_table_percell_run7.csv`, `fallback_min_before_start 1→20`, `fallback_maker_clamp→true`.

**NEXT (held):** T51 hardening (spec `T51_HARDENING_SPEC.md`) → implement+test → RUN-8 buffer relaxation (ATP_CHALL → WTA_CHALL → WTA_MAIN → ATP_MAIN), per-category gated on final-window net P&L clearing this RUN-7 baseline.

---

## RUN-6 LIVE — fix-3 reprice-maker-only (restart 2026-06-03T06:27:57Z)

**Deployed commit:** `ede406ab` (FF from `e5ac0fbf`). **Blob-verified RUNNING:** on-disk `live_v4.py` hash `6ce95fda` == `HEAD:live_v4.py` (file hash, NOT logs); PID 1984688; `_reprice_target` present; levers active (minrule + cancel_on_marketable=true + fallback_min_before_start=1).

**RUN-6 stack:** live levers (min-rule offsets + T-1 fallback + cancel-on-marketable, flags-on) **+ D18 placement-instant-fill booking + fix-3 reprice-maker-only**. The **T-20m fallback is the ONLY sanctioned taker entry** — the significant-move reprice now clamps a marketable target to `max(1, ask-1)` and re-rests maker (no `cross_on_move` cross). Fix-1 delivered by lever-3 (confirmed); **fix-2 DROPPED** (forensic: the paired-basis cap is not over-blocking — T50 verdict zero fair legs blocked; parked-contested, do not change). Tests: 8 files all pass.

**Cohort cutoff UNCHANGED — still `02:35:46Z` (three-lever line below).** Fix-3 + D18 are correctness fixes, NOT a strategy change, so the entry strategy under test (levers) is continuous from the three-lever deploy; a fresh RUN-6 line would needlessly fragment the maker-fill cohort we're growing N on. JUN-date exclusion still holds for stale (`-26JUN01-`).

**RUN-6 baseline snapshot (at stop, pre-restart):** cash **$2,703.19**, **9 open positions** (incl. the first new-cohort fill `26JUN03 MAYPAN-PAN` + 5 JUN01 stale + JUN02 RUN-5), 12 resting (8 exits + new 26JUN03 entries LAZSAM/TOPNAV). settlements 24h net **−$12.35**. NOT-FLAT at deploy; proceeded (entry-only correctness change, operator-authorized).

**Pre-committed RUN-6 read (LOCKED — measure post-wave, do not move the goalposts):**
- **Read A — genuine-maker fill-rate** (`is_taker=FALSE` from /fills, NOT entry_mode) vs the corrected **open→T-15m** targets: ATP_MAIN **74%** / WTA_MAIN **72%** / ATP_CHALL **54%** / WTA_CHALL **60%**. Tests whether the levers deliver maker fills (RUN-5 was ~6%). Near target ⇒ lever-3 landed; well below ⇒ cancel-churn still failing.
- **Read B — reprice-taker-leak → ZERO** (`cross_on_move` count = 0; only T-20m fallbacks remain as takers). Direct test of fix-3.
- **Held out:** absolute ROC (validated object is the DELTA, not absolute — live below walk by adverse-selection margin); maker-edge P&L verdict (N too small after one run — next read); the ENTRY_BUFFER→T-2m change (separate, only after RUN-6 confirms).
- **Caveats throughout:** delta-not-absolute · is_taker-not-entry_mode · blob-not-logs · JUN-date cohort · fix-2 parked-contested.

---


**Read order for a fresh chat or CC instance:** README → this file → LESSONS Section 1 → TAXONOMY Section 2.5 → ANALYSIS_LIBRARY → ROADMAP → SIMONS_MODE. On-demand: spec docs in `docs/` and atlas LOCKED_DOWN files in `data/durable/spike_volatility_map/`.

`CHAT_HANDOFF.md` was consolidated into this doc in this same Stage 0 reconcile; the stub there points back here.

---

## D18 DEPLOY — placement-instant-fill NO_EXIT fix (2026-06-03T05:24:33Z restart)

**Deployed commit:** `fde1ecf7` (FF from `69b906c6`). **Verified RUNNING by blob-diff:** on-disk `live_v4.py` blob `c2bc515d` == `HEAD:live_v4.py`; `_book_placement_cross_fill` present; PID 1967778; minrule table + three lever flags still loaded. **NOT a new cohort** — D18 is a pure correctness fix (books a fill that already happened + posts the exit that should always exist), ungated. The three-lever cohort cutoff (`02:35:46Z`, below) is UNCHANGED; entries before and after this restart are all three-lever cohort.

**The fix:** a `post_only=False` placement cross (miss_fallback / marketable_taker) can fill ON PLACEMENT; the placement path stored the position `phase="entry_resting"` with no instant-fill handler → the fill was never booked → the `match_start_buffer` cleanup cancelled the already-filled order and its `phase=="active"` guard skipped the exit → **naked-held, uncapped downside** (SHEBRA-SHE 2026-06-01, the one genuinely-silent leg of the D18 forensic; the other 4 flagged legs were reconcile-handled via `reconcile_v4_hold`/`reconcile_v4_exit_posted` — a forensic detection miss, corrected). New `_book_placement_cross_fill()` mirrors the T-20m fallback path's existing instant-fill handler. Fallback path left byte-identical. Tests `test_d18_placement_exit.py` (14) + T58/T52/T50 regress green.

**At deploy:** cash unchanged, 8 open old-cohort positions (NOT-FLAT; proceeded — entry-only + pure-correctness change, exits/state untouched). Untracked forensic scripts backed up to VPS `/tmp/predeploy_d18_backup.tar`. New-cohort premarket wave (26JUN03) began landing at restart under the fixed binary (first: MAYPAN-MAY @72 / -PAN @24).

**⚠ OPEN FINDING — lever-2 fill-window vs the T-15m match_start_buffer (NOT fixed; flagged for decision):** `ENTRY_BUFFER_SEC=900` (line ~2367) cancels ANY unfilled `entry_resting` bid at T-15m. Under the deployed lever-2 (`fallback_min_before_start=1` → manage-side fallback at T-60s), the T-60s fallback-cross is effectively **dead code** — the T-15m buffer cancels the bid first. So lever-2's realized behavior is **"maker rest → skip(cancel) at T-15m"** (which IS maker-or-skip), but the live fill window is **open→T-15m**, whereas the combined walk modelled **open→T-2m**. Per A50 (late-window dips dominate), the walk may **overstate** the fill-rate lift to the extent first-dips cluster in the final 15m. **Consequence for the lever-3 confirmation watch:** if live first-wave fill undershoots the walk's 69-81%, it could be this window-truncation, NOT cancel-churn failing — a confound to separate. This is why the placement-side fallback was DELIBERATELY left at T-20m (resting a fresh sub-20m placement to T-1 is futile — the buffer cancels it). QUANTIFIED (analysis/exit_charts/window_truncation.py, deployed minrule offsets, same per-minute data the walk used): the live open→T-15m window vs the walk's open→T-2m loses **ATP_MAIN 81→74%, WTA_MAIN 81→72%, ATP_CHALL 69→54%, WTA_CHALL 74→60%** (ALL 76→65%; truncation = 9-21% of walk fills, WORST on Challenger). **Read the first-wave fill-rate against the LIVE column (54-74% cat-specific), NOT the 69-81% headline.** CRITICAL: **ROC is window-neutral** (e.g. ATP_CHALL 14.59→14.58%) — the truncation costs FILL-RATE (volume/deployment), NOT per-capital edge. So it's a throughput question, not an edge question. First-wave read: fill near 54-74% ⇒ lever-3 LANDED (gap is just truncation, recoverable via path a); fill well below ⇒ cancel-churn still failing (code-level). Path (a) lower ENTRY_BUFFER_SEC for v4 = pure volume recovery at the validated edge (~18-21% more Challenger fills), worth it for Challenger but as a SEPARATE gated+validated change (lower toward T-2m, leaning on T51 live-detection + the now-fixed D18 instant-fill guard), only after the first wave confirms lever-3. Path (b) accept open→T-15m: no code, standing expectation = 54-74%.

---

## T58 THREE-LEVER ENTRY-FIX DEPLOY — cohort cutoff (2026-06-03T02:35:46Z / 2026-06-02 22:35 ET)

**Deployed commit:** `c156b6a8` (FF from RUN-5 `83e08395`, +18 commits). **Verified RUNNING, not just logged:** on-disk `live_v4.py` blob == `HEAD:live_v4.py` (`41d988b7…`), live config blob == committed, PID 1925320 `python3 -u live_v4.py` started at the restart, and the three lever flags resolved ON in the loaded config (`v4_fallback_sec=60`, `cancel_on_marketable=True`, `cancel_marketable_buffer=1`, `entry_table_cell_path → entry_table_percell_minrule.csv`).

**The three levers (all config-gated; flags-off = pre-fix byte-identical, clean rollback):**
- **Lever 1 — min-rule offsets:** `entry_table_cell_path → entry_table_percell_minrule.csv` — deep 7–18¢ cells shallowed to 3–8¢ at envelope reach60; shallow 1–2¢ untouched.
- **Lever 2 — T-1 fallback:** `fallback_min_before_start=1` (was T-20). Maker rests through the convergence window; T51/T52 skip-on-live/fat retained = maker-or-skip on thin/wide, premarket-safe.
- **Lever 3 — cancel-on-marketable (A):** `cancel_on_marketable=true`, `cancel_marketable_buffer=1`. Resting entry bid cancels only on degenerate OR bid-gone-marketable (`target ≥ ask − 1¢`), not wide-spread-alone — kills the 1,585-cancel churn, keeps the pick-off protection.

**Validation:** fresh per-match walk green all 4 cats. Fill **+10..+24pp**, ROC **DELTA +1.40..+4.94pp** (ATP_MAIN +1.56, WTA_MAIN +1.40, ATP_CHALL +4.94, WTA_CHALL +4.11). **Caveats held in all attribution:** (1) the validated quantity is the **DELTA**, not the absolute walk ROC — live realized sits below the walk by the adverse-selection margin (the walk assumes stable rest). (2) Lever-3's confirmation is the **LIVE fill-rate vs the walk's 69–81% projection, measured post-deploy** (the walk cannot price the cancel-churn fix). Live fill climbing off ~6% toward projection = churn fixed; staying near 6% = it did not land, diagnose. **Watch the first premarket wave under `c156b6a8`.**

**Cutoff key = the restart timestamp `2026-06-03T02:35:46Z`.** Every entry PLACED after it = three-lever cohort (clean). Pre-cutoff positions = old-entry-config cohort, frozen, managed by UNCHANGED exit logic (the `live_v4.py` delta is provably entry-only — exit/sell/DCA/state code byte-identical):
- **8 open positions at cutoff** (qty 5 each, all with resting exits): JUN01 stale — MARELL-MAR, MARELL-ELL, BICMON-MON, SEAKRU-KRU, NAEING-NAE (5); JUN02 RUN-5 — KRUSAK-KRU, MARFRU-MAR (WTA_CHALL), BLAGIL-GIL (ATP_CHALL) (3).
- **1 pre-cutoff resting BUY entry:** `KXATPMATCH-26JUN03BERARN-ARN` — placed under RUN-5 config before restart. NOTE: 26JUN03 ticker-date but PRE-three-lever — **exclude from the three-lever cohort by the timestamp key** (date alone would mis-tag it clean).

**T57 reconcile at deploy:** cash **$2,704.39**, 8 open, settlements 24h net **−$12.35** (gross $206.00, cost $214.62, fees $3.73). Guard fired NOT-FLAT; proceeded because the change is entry-only and the cohort cutoff freezes open positions by design (operator-authorized). Untracked analysis outputs backed up to VPS `/tmp/predeploy_untracked_backup.tar` before the FF; `session_reconcile.py` restored from git. No `state/`, `logs/`, `kalshi.pem`, or `.bak` touched.

---

## RUN-5 / RUN-6 COHORT CUTOFF — P&L attribution lock (2026-06-02 ET)

**Boundary (by ticker date, the unambiguous cohort key):**
- **`-26JUN01-` = STALE cohort** — entered in the morning RUN 0–2 (old/pre-finalization config; RUN 0 even ran `deploy_v5.json` size 10 — the CONFIG_PATH footgun, fixed `d585d0da`) and adopted across the evening restarts. **EXCLUDED from RUN-6 (and current-strategy) P&L attribution.**
- **`-26JUN02-` and later = CLEAN** — entered under the validated deploy (RUN 5, `83e08395`, `deploy_v5_live.json`, exit surface `gated_optima_validated_2026-06-01`, T58 entry, size 5). The current-strategy P&L.

**Passive cutoff — DO NOT FLATTEN the stale legs.** As of 2026-06-02 ~13:40 ET, 7 stale JUN01 legs (5 events) remain open, **each with a resting exit sell** — managed, not naked; they will exit-fill or settle on their own. Flattening was rejected: the $6.15 forfeited-exit counterfactual (the 6 RUN-2 naked-ride legs) proved closing early forfeits the in-play bounce these exits are positioned to catch. They ride. Attribution is locked by the date key above, so no execution is needed to keep RUN-6 clean.

**Stale legs still riding (JUN01, RUN 2):** NAEING-NAE/ING (Inglis/Naef), WONTAR-TAR (Wong/Tarvet), SEAKRU-KRU (Searle/Krueger), BICMON-MON (Bicknell/Monday), MARELL-ELL/MAR (Martin/Ellis) — 7 legs, qty 5 each, all with resting exits.

**Old-config cap-failure artifact (flagged, no action):** two stale pairs sit at combined ≥100 — **NAEING 65+36 = 101**, **MARELL 36+64 = 100** — residual of the morning over-100 entries (the T50/T52 fat-spread cross failure the current config structurally prevents). They ride to settle; excluded from RUN-6.

**Already resolved:** the 6 RUN-2 naked-ride legs (GALPOL-GAL/POL, STRMOE-STR, CECSIM-CEC, KESMAR-MAR, SHEBRA-SHE) have all settled out.

**RUN-6 = the next restart.** It will FF past `d585d0da` (CONFIG_PATH footgun fix) and start on a book whose only RUN-6-attributable positions are `-26JUN02+`. Account at cutoff: cash $2,697.44 + mark $30.35 = **$2,727.79**; 13 open (7 stale + 6 current), 13 resting exits (7 stale + 6 current). Read-only — no positions touched.

---

## ORIENTATION (read first)

### Current state, in one sentence

The strategy phase is locked. The bot is paused. Next is execution-lock: surface bugs in paper mode before deploying.

### What just landed (the 2026-05-15 → 2026-05-20 arc)

Five canonical analytical artifacts landed in dependency order between CHAT_HANDOFF's last touch (2026-05-15) and HEAD:

1. **per_minute_features.parquet** (T37 ckpt-3, sha256 `9fde4b5d`) — FOUNDATION-TIER per TAXONOMY. 9.33M ticker-minute rows, 88 cols. The canonical observation grain. Pre-existing at start of arc; foundation for everything below.

2. **n_profile_v1** (T40, sha256 `a7ed1155`, producer `a28840e`) — per-N rollup, 19,614 rows × 45 cols, 0 dropouts, 7/7 gates PASS at Phase-3 full corpus 2026-05-18. The per-N projection of the foundation.

3. **inmatch_bounce_surface_v1** (T41, sha256 `14241db0`, register commit `6f1d4bd`) — Layer-A-equivalent band-free in-match bounce surface. 800 rows, 7/7 gates PASS at full cohort 2026-05-18. First analytical deliverable on n_profile_v1.

4. **Spike volatility map atlas** (T42, six commits `481de7f` → `d99c6e9`) — four-category descriptive lock-down. 14,033 N's across ATP_MAIN / WTA_MAIN / ATP_CHALL / WTA_CHALL. 4 spike per-N parquets + 12 descriptive parquets + 4 LOCKED_DOWN.md + PAIRING_DIAGNOSTIC.md + canonical producer `data/scripts/build_spike_perN.py` (`c5e377f`).

5. **(superseded subtrees, preserved not deprecated)** — Rung 1 strategy_evaluation producer (T39.1, commit `5fc6d40`, spec v0.3.2) committed code but never ran; exit_optimized_bounce_v1 (T39.2, spec/producer v0.4 `d23fff5`) Phase-1 PASS, Phase-2 halted-then-gate-fix. Both ate by the atlas. Code preserved; available if future work wants the rung-framing or dual-conservative-fill-frame approach.

### What's next (execution-lock)

The atlas measured strategy. The bot's job is to turn measured edge into realized edge. Sequence (locked this session, B-then-A):

1. **Bug 4 first** (T11a/T11b) — settlement state detection in paper mode per `docs/bug4_brief.md`. 500+ line spec exists. Operationally: phantom positions hold resting exit orders past settlement. Closes the paper-mode reliability gap.
2. **Layer B v2 second** (T36) — tick-level fill semantics replacing minute-cadence simulator (which overstates fills 2.4×). Spec at `docs/layer_b_v2_spec.md`. Spec must be revised against T37 foundation before producer build (per ROADMAP T36 amendment 2026-05-14).
3. **Hot-reload mechanism** — operator-stated requirement: weed out bugs without shutdown/reboot. `docs/bot_v5_shell_architecture.md` may address; v5 vs v3 decision pending.
4. **Paper-mode integration test suite** — B4-T8 through B4-T11 unit tests plus broader coverage (match-cycle, fill detection, settlement, position state, P&L, scanner-executor, restart-and-resume).
5. **Paper-mode run against live tape** — continuous; compare paper P&L against atlas hindsight rules.
6. **Capital deployment with safety rails** — start small, scale via G22 cts/N axis as depth is characterized.

**Deployment philosophy:** Trade all 90 cells per category, do not cherry-pick to high-ROI cells. Volume is the operational constraint. Execution work resolves marginal cells; cell selection does not.

---

## DURABLE CONTEXT

### Operator

Druid, co-founder OMI Group Holdings (trading division OMQS). Algorithmic prediction-market trading on Kalshi tennis binary markets. Direct, technically precise, high-urgency. Pushes back on premature conclusions; consistently correct when he does. Treat operator pushback as probe-trigger per A32, not defend-trigger.

### Agent topology — four agents, operator is routing layer

No direct agent-to-agent pipes. Operator copy-pastes between them. All git commits have author `Druid <Osullivan Omigroup.ops@outlook.com>` (operator's local git config) and Co-Authored-By `Claude Opus 4.7 (1M context)`. Executor-of-record for VPS-side runs is named explicitly in commit messages ("App-authored", "App-verified", "via App", etc.).

- **Opus (chat-side Claude on claude.ai)** — strategy, spec drafting, verification, coordination. Web/mobile chat interface. Has `web_fetch` + `bash_tool` sandbox at `/tmp/omi_check/` for byte-verification reads only. Cannot SSH to VPS, cannot commit. Drafts prompts that operator pastes to App or CC. Co-Authored-By on every recent commit.
- **App (VPS-side executor)** — runs on the VPS at `root@104.131.191.95`, workspace `/root/Omi-Workspace`. Full shell, file read/write, runs producer scripts directly against the heavy parquets that live there (g9_trades 1.5GB, per_minute_features 388MB, n_profile.parquet, etc.). The agent of record for spike producer runs, n_profile_v1 Phase-3 build, inmatch_bounce_surface_v1 Phase-2 build, Layer A v1 / Layer B v1 / Rung 0 producer runs, forensic replay runs. Evidence: commit messages `5fc6d40`, `8e8f46e`, `19fdd5a`, `0fcf474`, `c9a0f3e`/`c76eee5`, `4c100f7` all attribute the on-VPS work explicitly to App.
- **CC (Claude Code in Cursor IDE)** — runs in Cursor on operator's Windows machine with the operation's codebase loaded as working context (local clone at `C:\Users\omigr\OMI-Workspace\arb-executor`). Drafts/edits code, helps operator construct commits from the local clone, can push to origin/main. Where code-level changes get authored before being either committed locally or shipped to App for VPS execution.
- **Plex (Perplexity Comet)** — external research/synthesis. Browser-based; read-only on public web URLs incl. the public GitHub repo. No shell, no write. Methodology synthesis only (e.g., this session arc's stability framework rounds, adaptive-binning consult).

### Systems access

- **App's working context:** VPS shell at `ssh root@104.131.191.95`, workspace `/root/Omi-Workspace`, primary subdir `arb-executor/`. Heavy parquets (g9_trades, per_minute_features, n_profile, Rung 0 cell_economics) live here.
- **CC's working context:** local Windows clone at `C:\Users\omigr\OMI-Workspace`, target subdir `arb-executor/`. Commit-authoring happens here; pushed to origin/main.
- **GitHub:** `github.com/OMIGROUPOPS/Omi-Workspace` (public). Source of truth.
- **VPS-vs-origin sync:** the VPS git tree runs behind origin/main by design — App pulls only when re-running producer code (explicit operator decision per turn).
- **Opus sandbox:** clone the public repo to `/tmp/omi_check/Omi-Workspace` for byte-verification reads; ephemeral per chat session, read-only.

### Foundation chain (canonical, with sha256s)

```
G9 corpus                  per_minute_features        n_profile_v1                inmatch_bounce_surface_v1
(T28 ea84e74)              T37 ckpt-3 9fde4b5d        T40 a7ed1155                T41 14241db0
g9_candles 9.5M rows       9.33M ticker-min rows      19,614 rows × 45 cols       800 rows
g9_trades 33.7M rows  -->  88 cols          -->       7/7 gates PASS       -->    7/7 gates PASS
g9_metadata 20,110 rows    FOUNDATION-TIER            per-N rollup                Layer-A-equiv per B16
                                                                                  |
                                                                                  v
                                                              Spike volatility map atlas (T42)
                                                              4 cat × {1c, 2c, 3c} descriptive
                                                              + spike per-N parquets
                                                              + canonical producer build_spike_perN.py
                                                              HEAD d99c6e9
```

Parallel superseded subtrees:
- Rung 1 producer (T39.1, commit `5fc6d40`): committed-but-never-run, lane eaten by atlas.
- exit_optimized_bounce_v1 (T39.2, commit `d23fff5` v0.4): Phase-1 PASS, Phase-2 halted then gate-fixed, never re-run.

### Working norms (battle-tested, carry forward verbatim)

1. **Single-concern commits**, dependency-ordered. Never bundle.
2. **One executor prompt per turn** (App or CC), never bundled. Multi-step workflows sequence across turns.
3. **Probe-validate-probe-validate** before expensive compute. Five failure modes per D11: provenance, grain, unit, coverage, upstream-filter.
4. **Corpus mutations require C37 pre-replace validation gate**. Compute `.new`, run hard gates against `.new` bytes, `os.replace` only on all-pass. Gate failures adjudicated with disk evidence, not narrative.
5. **Streaming discipline on VPS** (~1.9 GB RAM). >3-4 full columns into pandas risks OOM. Use iter_batches / per-ticker pyarrow pushdown.
6. **Web-fetch / verify every commit against origin** via `/tmp/omi_check` clone or equivalent. Don't trust executor summary uncritically.
7. **State recommendations with conviction, not options.** When the right answer is clear, name it and let operator countermand. Operator-flagged: "stop with the subjective questions."
8. **When you background a job, you own the follow-through.** Poll it, surface results when they land — don't wait to be asked.
9. **All operator-facing timestamps ET per G21.** UTC stays at raw-bytes layer only.
10. **Full player names always.** Never abbreviations or 3-letter Kalshi codes.
11. **Treat operator pushback as probe trigger per A32**, not as noise.
12. **External synthesis (Plex, etc.) gets committed to `docs/external_synthesis/<source>_<topic>_<date>.md` immediately**, not held in chat-side context only.
13. **Critical review uses disk evidence, not inference.** Pull the actual repo and verify column names, doctrine claims, corpus assumptions against committed source. Inference about what the spec "probably says" produces partially-wrong corrections.
14. **The "ct" unit is one contract, integer-indivisible.** Pays $1 (effectively 99¢ per E32 first-touch). Operator-facing economics in ct terms always; per G22 keep N (per-binary-market unit-of-observation) and ct (unit-of-position-size) distinct.
15. **Codify principles when operator surfaces them.** A39 (cents-vs-ROI), G22 (N-vs-ct), B25 (minute-cadence undercount), C38 (zero-large-fraction = scoping bug not sample artifact) all came from this discipline.
16. **The repo is the shared brain.** Anything that would otherwise be copy-pasted between agents gets committed and read from origin/main.
17. **CC prompts use repo-root-relative paths.** CC operates from `C:\Users\omigr\OMI-Workspace` (the actual repo root, not the arb-executor subdir). Always pre-flight `git rev-parse --show-toplevel` before any path-dependent operation. Chat-side path assumptions are inference, not evidence.

### What NOT to do (lessons paid for this session arc)

- **Don't collapse the three axes into one realizable-PnL number.** Headline × exit-fill-fraction × entry-improvement × sizing-scale stays decomposed. Never present a deployable dollar figure without the three-axis caveat attached.
- **Don't run OOS tests as if the descriptive measurement is a predictive claim.** The atlas measures what the corpus paid under per-cell hindsight-optimal rules. That is well-posed without OOS. Predictive generalization is a separate question downstream of execution work. Confusing the two produced an hour of OOS rabbit-hole work this arc.
- **Don't pool adjacent cells without preserving real heterogeneity.** The 2¢ probe diagnostic showed pooling cells 37 + 38 destroyed $37.50 of edge that was real cell-by-cell variance, not overfitting. 1c/2c/3c reported side-by-side per Plex round-2 recommendation.
- **Don't apologize when corrections are needed.** Operator pushback is signal; absorb the correction, recompute, move on. Don't self-flagellate or relitigate.
- **Don't conflate Rung 0 (cell economics primitive) with Rung 1 (strategy evaluation).** They answer different questions at different aggregation levels. T39 (the recomputation ladder) and T42 (the atlas) ARE different things even though both touch cell economics.
- **Don't lose the foundation chain.** per_minute_features → n_profile_v1 → inmatch_bounce_surface_v1 → atlas is the actual provenance. Treating the atlas as if it sits directly on G9 trades misses the load-bearing intermediates.
- **Don't run code in the Opus sandbox that ought to run via App or CC.** `/tmp/omi_check` is read-only verification only — clone fresh, read, never write. Producer execution and corpus mutations against the heavy parquets run via App (on the VPS). Code authoring and local commits run via CC (Cursor IDE). Operator routes per task.
- **Don't reframe what the operator said into safer versions.** When operator says "execution lock," draft toward execution lock, not toward an adjacent thing that feels more familiar.
- **Don't conflate "foundation broken" with "everything pre-atlas is suspect."** Foundation = data/strategy layer only. Executor-side institutional knowledge from prior deploys is durable and the execution-lock arc explicitly uses it (see "Bot status: PAUSED" below).

---

## CURRENT OPERATIONAL STATE

### Bot status: PAUSED

All prior bot versions (v1, v2, v3, V4.2c) traded on a foundation now known to be broken at the data/strategy layer. Capital is unused. The entire 2026-04-30 → 2026-05-20 arc was foundation rebuild. Now atlas is locked; execution-lock arc is next.

**Executor learnings carry forward.** "Foundation broken" means the data/strategy layer — spike measurement methodology, truncation handling, cell definition. Executor-side institutional knowledge from prior deploys is durable and the execution-lock arc explicitly uses it:

- **F4** — silent fill-detection failure class (Apr 17-23: 0 entry_filled events over 6 days despite 763 cell_match events). The category of bug Bug 4 implementation has to defeat.
- **Bug 4 (T11a/T11b)** — paper-mode settlement state handling, 500+ line brief at `docs/bug4_brief.md`, OPEN. First task in the execution-lock arc.
- **B25** — minute-cadence simulator undercount (2.4× overstatement of fills for limit policies vs tick-level reality). Mechanism that Layer B v2 (T36) has to fix.
- **C19** — Kalshi lifecycle timestamps don't track actual match start; use BBO volatility-jump detection or external scrape.
- **C37** — corpus mutations require pre-replace validation gate. Compute `.new`, run hard gates against `.new` bytes, `os.replace` only on all-pass.
- **Paper-mode infrastructure already exists in `live_v3.py`** — `_PAPER_API` flag, `PaperFillSimulator`, `PaperPosition` dataclass. Paper-mode unit tests specified B4-T8 through B4-T11. Paper mode does NOT poll REST settlements (would falsely close paper positions using real-account history); settlement detection in paper mode is via WS lifecycle + BBO threshold.
- **Kalshi auth pattern** — always copy from `swing_ladder.py`'s `_kalshi_headers()`. Never reimplement. RSA-PSS SHA256 signing `"{timestamp_ms}{method}{path_with_prefix}"`.
- **Kalshi API quirk** — `dict.get("taker_fill_count", 0)` returns `None` not `0` when the key exists with null value. Always use `(status.get("taker_fill_count") or 0)` pattern. Fill detection uses `remaining_count == 0` and `status == "executed"` as primary signals.
- **Rate-limit budget separation** — heavy backfill must not share rate-limit bucket with live trading (per L2 lesson when added). Operational requirement for execution-phase deployment.

The execution-lock arc inherits all of this. Strategy was rebuilt; execution is not being rebuilt — it's being debugged and hardened.

### Atlas headline (T42, four-category spike volatility map)

Taker-floor, hindsight-optimal per-cell exit-or-hold rules, 10ct sizing:

| Category   | N      | Trading days | 1c Total $   | 1c ROI  | Cheap regime ROI | Daily $  | Daily ROI |
|------------|--------|--------------|--------------|---------|------------------|----------|-----------|
| ATP_MAIN   | 4,137  | 252          | +$1,658.80   | +7.90%  | +36.13%          | $6.58    | +7.90%    |
| WTA_MAIN   | 3,683  | 248          | +$1,824.90   | +9.84%  | +43.22%          | $7.36    | +9.84%    |
| ATP_CHALL  | 5,326  | 109          | +$2,029.20   | +7.57%  | +36.83%          | $18.62   | +7.57%    |
| WTA_CHALL  | 887    | 80           | +$645.30     | +14.52% | +57.58%          | $8.07    | +14.52%   |

**Corpus totals:** 14,033 N's, +$6,158.20, $70,813.20 capital deployed, blended +8.70% per-trade ROI. **Pairing rate (event-level):** 79.3% paired (6,208 paired / 7,825 total events); 88.5% of N's in paired events. **Combined max-overlap operational picture:** ~91 N/day, ~$460 capital/day, ~$40.62 earnings/day, +8.70% blended daily ROI on cycling capital at 10ct.

### Three-axis caveat (verbatim, load-bearing for every headline)

Every atlas number is the strategy's opportunity floor on the corrected foundation. Three axes between this and realized PnL:

**AXIS 1 — EXIT-side fill realism (pushes DOWN).** Every simulated +X exit in the atlas assumes qualified-size taker print at that level = guaranteed maker fill. B25/Cat-11 evidence: 2.4× simulator overstatement of fill rates for limit policies in minute-cadence simulators against tick-level reality. The ≥250ct size-qualification floor and Main-tour deep mid-match liquidity mitigate somewhat; realization fraction unmeasured for this corpus. Expected realized capture: **0.4–0.8× of simulated**, pending dedicated Layer C fill-realism work.

**AXIS 2 — ENTRY-side maker improvement (pushes UP).** Every anchor in the atlas is a real T-20m TAKER trade — someone who paid up to cross the spread. A resting maker buy at the bid (or better) fills at a BETTER price than the taker print. On typical 1-2¢-spread markets, ~1¢ per ct cheaper entry per trade, compounding across larger captures on hits, higher ROI per hit, smaller carry losses on misses. Expected improvement: **~+10–30% on the headline**. Aligns with the bot's existing edge thesis (LESSONS line 48: "anchor-relative discount capture, 97% of fills are Scenario C_discount"). Tier 3 marginal cells (~35 cells where best_X is small) most levered to entry-side improvement.

**AXIS 3 — ARRIVAL FREQUENCY (G22).** Deployable economics need N's/day × ct/N sizing. Frequency observable from corpus (16.4 / 14.9 / 48.9 / 11.1 N/day per category at 10ct). Sizing depends on depth (F33). G22 axes are never collapsed: per-N edge × N's/day × cts/N.

**Combined:** realizable PnL = (headline) × (exit-fill-fraction 0.4–0.8) × (entry-improvement-multiplier ~1.1–1.3) × (sizing scale once depth is characterized).

Operator stated privately: "we can also assume privately that we'll be saving a cent or 2 once we figure execution out." Axis 2 in operational form. Headline stays conservative; operational hand reads ~+25–50% better than headline. Execution work will measure per cell.

**Do NOT** treat headline as deployable dollars. **Do NOT** treat headline as pure upper bound (entry-side correction is in the operation's favor).

### Structural patterns observed in the atlas (preserved as doctrine)

- Cheap regime (anchor 5–30¢) deploys ~8–9% of capital and generates 30–40% of dollar profit across all four categories. A39 cent-sensitivity geometry confirmed empirically.
- **Highest-ROI single cell across the corpus:** ATP_MAIN anchor=9¢, hold-to-settlement rule, +242% ROI on $20.70 capital (N=23, 30% YES-settle rate). Cheap-cell A39 asymmetry in extremis.
- WTA outperforms ATP at same draw level (WTA_MAIN +9.84% > ATP_MAIN +7.90%; WTA_CHALL +14.52% > ATP_CHALL +7.57%). Codebase hint that ATP/WTA need structurally different strategies does NOT show up in the spike-volatility-map dimension — both tours produce the same shape, WTA ~2pp hotter.
- Challenger tours: denser per active day, shorter-season. ATP_CHALL 48.86 N/day in 109 days vs ATP_MAIN 16.42 N/day in 252 days.
- High regime (anchor ≥66¢) barely positive everywhere (+3.11% / +3.52% / +3.46% / +5.50%). Favorite-side trades are marginal contribution.
- Cheap-regime unpaired N's outperform cheap-regime paired N's on ROI (+45.5% vs +38.9% aggregate). Asymmetric-information pattern flagged at corpus scale.

### Capital position

Operator stated: plenty of capital to scale up. Sizing is not the binding constraint. Binding constraints are (a) execution mechanics and (b) market depth (F33).

---

## OPEN UNCERTAINTIES (do not underweight)

1. **Bot architecture v5 vs v3** — operator wants hot-reload (weed out bugs without shutdown/reboot). `docs/bot_v5_shell_architecture.md` exists; whether v5 addresses modularity/hot-reload requires read. Pending.
2. **Deployable rule shape** — atlas measured perfect hindsight per cell. The deployable rule isn't perfect hindsight. Open question: what's the deployable rule shape? Per-cell argmax overfits within-sample. Possible shapes include global X, global r%, per-regime r%, or per-cell-with-pre-specified-smoothness. Resolution comes from paper-mode validation against atlas hindsight rules, not from further hindsight analysis.
3. **Bilateral capture mechanism (B23)** — pairing diagnostic showed 79.3% upstream feasibility. Atlas didn't run bilateral economics. When does it get layered in? Likely after paper-mode validates single-leg execution.
4. **FV-anchor workstream** — operator-flagged: "im obviously going to be attacking this next. this is very very important." Atlas measured taker-floor entries (conservative). FV-anchor work measures actual edge from "Kalshi mid is X¢ below FV" entries. Big. Likely sequenced after execution-lock but before live capital, or threaded into paper-mode validation alongside execution debugging.
5. **Adaptive cell-width binning** — Plex round-4 deferred. Defensible as Layer A smoothing with pre-specified threshold grid; run AFTER atlas to compare emergent band patterns across categories. Future enhancement.
6. **Depth-chain data collection (F33 / G13)** — prospective Kalshi `/orderbook` polling, required for fill-probability modeling at non-BBO maker-post depths. Currently a blocked-track gap.
7. **Rung 1 / exit_optimized_bounce_v1 disposition** — both have committed code on origin/main, neither was run to completion, both ate by the atlas. Preserved not deprecated. Open question: do we ever want to run them retroactively for cross-validation? Or formally retire? Operator call.
8. **Whether 6-27% stable-window coverage means one of three attack vectors must shoulder most of operation's coverage** — open from prior session, possibly addressed by atlas regime breakdown but not formally closed.
9. **Daily-overlap assumption** — the ~$40/day combined operational picture assumes max-overlap days across all four categories. Tour calendars don't always align; actual daily realization will vary. Corpus mean is planning baseline, not daily expectation.

---

## KEY FILE PATHS

**Doctrine docs (`arb-executor/docs/`):**
- `LESSONS.md` (558 lines, A–G categories) — durable principles. Critical: A21 (CIs), A22 (measurement universe), A24 (variable inventory), A32 (operator pushback as probe-trigger), A37 (strict-entry coverage cost), A38 (dual-peak vs settlement), A39 (cents-vs-ROI), A39 amendment, B6 (small-N CIs), B13 (skew-relative thresholds), B14/G17 (premarket vs in-match decomposition), B15 (unit-of-decision per-minute), B16 (Layer A/B/C separation), B23 (bilateral mechanism), B25 (minute-cadence fire_rate undercount), C17 (credential redaction), C19 (lifecycle timestamps), C27 (foundation-pointer discipline), C28 (streaming), C37 (pre-replace gate), C38 (zero-large-fraction = scoping bug), D10 (dynamic lesson numbering), D18 (consult git universe FIRST), E12 (premarket phases), E18 (bilateral capture rate anchor), E32 (locked cell/exit model — load-bearing), E32(e) (every band gets its own exit target), F4 (Apr 17-23 silent fill-detection), F28 (/tmp ephemerality), F33 (depth-chain gap), F34 (formation gate), F35 (recoverable 6.4% tier-3 calibration defect), G19 (candle sparse minute population), G21 (ET on operator surfaces), G22 (three-axis deployment math), G23 (honest provenance discipline).
- `ROADMAP.md` (T/F/U/G/D categories). Read T11a/T11b (Bug 4), T26 (Live trading deployment), T32 (Layer C, demoted), T36 (Layer B v2, open with pre-build revision), T37 (foundation, COMPLETE), T39 (recomputation ladder), T39.1 (Rung 1 superseded-not-deprecated), T39.2 (exit_optimized_bounce_v1 Phase-2-halted-superseded), T40 (n_profile_v1 COMPLETE), T41 (inmatch_bounce_surface_v1 COMPLETE), T42 (atlas COMPLETE).
- `SIMONS_MODE.md` — axiomatic framing. Axiom 2: "The price is not trying to be fair value." Axiom 3: "Mispricing is the default state." Sections 4–6 load-bearing for cell-selection vs execution problem split.
- `TAXONOMY.md` — data tier definitions (A/B/C, G, FOUNDATION-TIER), analysis depth levels 0–6, Section 2.5 GRAIN/VECTOR/OBJECTIVE classification axes.
- `ANALYSIS_LIBRARY.md` — indexed findings catalog with disposition.

**Atlas files (`arb-executor/data/durable/spike_volatility_map/`):**
- 4 LOCKED_DOWN.md files (one per category), PAIRING_DIAGNOSTIC.md, CROSS_CATEGORY_MAP.md (stale; will be deprecated in this Stage 0).
- 4 spike per-N parquets + 12 descriptive parquets (4 categories × 3 widths).

**Producer & bot code:**
- `data/scripts/build_spike_perN.py` (`c5e377f`) — canonical reproducible atlas producer. Takes `--category {ATP_MAIN,WTA_MAIN,ATP_CHALL,WTA_CHALL} --output /path.parquet`.
- `live_v3.py` — current bot (paused). Has `_PAPER_API`, `PaperFillSimulator`, `PaperPosition` dataclass. Bug 4 OPEN.
- `swing_ladder.py` — Kalshi auth pattern reference. Per memory: "Always copy from `swing_ladder.py`'s `_kalshi_headers()` — never reimplement."
- `data/scripts/build_n_profile_v1.py` (`a28840e`) — n_profile_v1 producer.
- `data/scripts/build_inmatch_bounce_surface_v1.py` (`85118d4`) — inmatch_bounce_surface_v1 producer.
- `data/scripts/build_rung1_strategy_evaluation.py` (`5fc6d40`) — Rung 1 producer, **committed not run**.

**Spec docs (`arb-executor/docs/`):**
- `bug4_brief.md` (500+ lines) — Bug 4 spec, OPEN per T11a/T11b. **CRITICAL for execution-lock arc.**
- `bot_v5_shell_architecture.md` — next-gen bot spec. Read for hot-reload questions.
- `layer_b_v2_spec.md` (52 KB) — tick-level exit-policy simulator spec. OPEN per T36; pre-build revision required against T37 foundation.
- `layer_c_spec.md` — realized economics with fees. OPEN per T32, gated on Layer B v2 PASS, demoted by B25.
- `forensic_replay_v1_spec.md` — replay that surfaced B25.
- `per_minute_universe_spec.md` — foundation corpus spec.
- `n_profile_v1_spec.md` — n_profile_v1 spec.
- `inmatch_bounce_surface_v1_spec.md` — inmatch surface spec.
- `rung0_cell_economics_spec.md` — Rung 0 spec v1.1.
- `rung1_strategy_evaluation_spec.md` — Rung 1 spec v0.3.2 (build-ready, producer committed, not run).
- `exit_optimized_bounce_v1_spec.md` — exit-opt v0.4 spec (Phase-1 PASS, Phase-2 halted then gate-fixed, not re-run).
- `recomputation_ladder.json` — 6-rung dependency map for 22 settlement-scored audit entries.

**Data sources (NOT git-tracked, VPS-only by size; sha256 in MANIFEST):**
- `data/durable/g9_trades.parquet` — 33.7M-row tick-level trade tape.
- `data/durable/g9_candles.parquet` — 9.5M-row per-minute candles.
- `data/durable/g9_metadata.parquet` — 20,110-row market metadata.
- `data/durable/per_minute_universe/per_minute_features.parquet` (sha256 `9fde4b5d`) — FOUNDATION-TIER.
- `data/durable/n_profile_v1/n_profile.parquet` (sha256 `a7ed1155`) — per-N foundation.
- `data/durable/inmatch_bounce_surface_v1/surface.parquet` (sha256 `14241db0`).
- `data/durable/rung0_cell_economics/cell_economics.parquet` (sha256 `6fdd019d`) — Rung 0 output.
- `data/durable/kalshi_fills_history.json` — Tier-A fill fact source (7,489 fills Mar 1 – Apr 29).

**Atlas parquets ARE git-tracked** (small enough): `data/durable/spike_volatility_map/*.parquet`.

---

## RECENT COMMIT TRAIL

Most recent first.

Premarket-dynamics arc (2026-05-22 → 2026-05-23, most recent):

- `701ccc8` (+ `9fc0319` ROADMAP T48 / `4abe792` ANALYSIS_LIBRARY / this SESSION_HANDOFF; LESSONS A43 commit follows) — **Path C arc wrap-up (T48): feature-conditioned entry refinement — NEGATIVE, arc CLOSED.** Commits the held Phase 2 (offset modulation) + corrected Phase 3 (execution-mode) negatives as one unified writeup framed against v4's positive. **Phase 2: best variant +0.089pp gross (noise; per-cell dominance 22/36).** **Phase 3 corrected: best drift-threshold ≥4¢ nets −0.248pp** (8 favorite cells −$191.1; cross cohort enters ~1¢ cheaper, eaten by the 1¢ fee + the exit cap; drift within 0.19¢ of Scope A T4). Both not promoted. **Unified mechanism (LESSONS A43): the locked atlas fixed-profit exit (+X regardless of entry) caps entry-side feature conditioning** — a working predictor (T46 AUC 0.73) has no entry-side channel to monetize; the productive lever is the static per-cell offset on the net-PnL objective (T47 v4, +1.024pp). Synthesis: `path_c_arc_findings.md`; 4 parquets promoted on-disk. **Closes the empirical premarket-dynamics strategy arc.**
- `c90985b` (+ `eb272c8`/`7f80b74`/`f55b689` docs; policy update `60dd43f`) — **Path B v4 (T47): per-cell offset re-optimization on net-PnL — DEPLOYABLE.** Re-sweeps placement×offset per cell on net realized PnL (vs v1's entry-capture): **net ROI 11.73% vs v3 10.70% (+1.024pp; +1.22pp vs canonical v3)** on lower capital, gate 6 material. **Net-PnL-optimal offsets are SHALLOW (1-3¢, 27/36 cells), opposite v1's deep favorites** — the atlas exit cap binds, so deep offsets just miss; shallow bids fill reliably. The positive complement to the Path C negative arc (the lever was the offset itself, mis-set by v1). v4 supersedes v3 as the deployable table (`per_regime_offsets_v2.csv`).
- `22f3221` (+ `a4f3cc5`/`0f696f2` docs) — **Path C Phase 1 (T46): 3-feature drift predictor (Plex Round 7 Tier 1).** Real out-of-sample signal: **holdout AUC 0.7298** (>0.62 bar; CPCV 0.6625). paired_arb_gap strongest single feature (within-cell fill lift to 3.5×); taker_imbalance dominant in the model (negative sign). **Key finding: binary skip-gates UNDERPERFORM place-everywhere** (Rule A 9.17% / Rule B 9.36% vs v3 12.11%) — a fill predictor's value is offset modulation, not on/off placement when the fallback is safe (LESSONS A42). Recommend Path C Phase 2 as offset modulation. Outputs on-disk only.
- `648b8db` (+ `ff86121`/`95216b4` docs) — **Path B v3 (T45): per-regime offsets + atlas exit replay (deployable).** Per-(cat×regime) offsets from v1 replace the universal 15¢: **$8,098.50 vs atlas $6,158.20 (+31.5%)** on lower capital ($66,902) → blended ROI **12.11% vs 8.70% (+3.41pp)**, beating T44's +2.93pp by only **+0.48pp (+$269)** — diminishing returns (the incremental is the underdog harvest the universal rule clamped away). Fill 28.4% (vs 15%); baseline exact; gate-4 v3-fill==v1-fill (0.0pp). Outputs on-disk only.
- `a61830c` (+ `5470754`/`23e6898` docs) — **Path B v2 (T44): marketable-vs-resting split + atlas exit replay.** Maker placement realizes **$7,829.30 vs atlas $6,158.20 (+27.1%)** on lower capital → blended ROI **11.63% vs 8.70% (+2.93pp), pre-realism**; baseline reproduced exactly; favorite-driven (universal 15¢ clamps underdog bids to 1¢). Outputs on-disk only.
- `8d2f259` / `41eb0f2` (842d213) / `5e37400` — Path B worked-example charts v3 / v2 / v1 (one paired event each; v3 added the marketable-vs-resting honesty + atlas exit overlay that drove Path B v2's execution split).
- `5bd88b6` / `4f07e5a` — Path B v1 doc-system commits (ROADMAP T43; ANALYSIS_LIBRARY registration).
- `1e00818` — Path B premarket maker-bid fill mechanics (T43). 14,033 N × 42 placement×offset cells; entry-side fill rates only (no PnL, no exit logic). Corpus hindsight entry-improvement ceiling 2.46¢/N; monotonic favorite>underdog gradient (r85_94 ~6.5¢ via 15¢ offsets, r05_14 ~1.1¢ via 2-3¢). Outputs on-disk only; producer `884e951`.
- `7c15776` — Walkover/retirement sanity check. T4 mid-drift gradient NOT robust: removing reversal-prone events (17.7-25% of N by duration proxy) ~halves the extreme-band drift (±11¢ → ±5-6¢).
- `2ca8890` — Scope A corpus premarket map (per_minute_distributions_v1 + per_event_fingerprint_v1, 14,033 N). Headline: monotonic ~±11¢ anchor-regime mid-drift gradient (T4), near-identical across categories.
- `a0bc5e6` — fv_overlap_join_v1 substrate + v3 example chart. Cross-book consensus FV layered on premarket_tape (~3.5% of atlas events have FV coverage; WTA_CHALL 0% per betexplorer scraper gap).
- `7d98e74` — book_prices → durable fv_history archive + daily 02:30 UTC cron (stops the rolling-32-day FV-poll leak).
- `30a47b6` — premarket_tape_v1 substrate (T-4h→T-20m per-minute tape, 2.06M rows, foundation scope).

Atlas arc:

- `d99c6e9` — Pairing diagnostic: 79.3% events have both N's anchored. ATP_MAIN 85.5% / WTA_MAIN 81.2% / Challengers ~74%. Empirical upstream feasibility for B23.
- `d038cb3` — WTA_CHALL descriptive locked. 887 N, 1c +$645/+14.52% across 80 days. ALL FOUR CATEGORIES LOCKED.
- `ec1f593` — ATP_CHALL descriptive locked. 5,326 N, 1c +$2,029/+7.57% across 109 days. 48.86 N/day.
- `c5e377f` — Canonical reproducible producer `build_spike_perN.py`. Reproduces committed ATP_MAIN+WTA_MAIN parquets byte-identical.
- `75603f4` — WTA_MAIN descriptive locked. 1c +$1,825/+9.84% across 3,683 N's, 248 days.
- `481de7f` — ATP_MAIN descriptive locked. 1c +$1,659/+7.90% across 4,137 N's, 252 days. Plex-confirmed methodology.

Plus archived chat-bridge handoff at `docs/handoffs/EXECUTION_PHASE_HANDOFF.md` (commit [hash, filled in post-archive-commit]) covering 2026-05-19→2026-05-20 chat-bridge methodology arc with documented gaps.

Pre-atlas analytical arc (2026-05-15 → 2026-05-19):

- `9912660` — Spike volatility map ATP_MAIN + WTA_MAIN per-N parquets (corrected untruncated size-qualified spike).
- `b5c837c` — LESSONS D18 (chat-side failure mode: reason from data not from priors; consult git universe FIRST).
- `5fc6d40` — Rung 1 producer (build to spec v0.3.2). **Committed not run.**
- `3bbac37`, `c916c50`, `ba09107`, `59c3f14` — Rung 1 spec v0.3.2 / v0.3.1 / v0.3 / v0.2 patches.
- `6f1d4bd` — Register `inmatch_bounce_surface_v1` CANONICAL. 7/7 gates PASS full cohort, sha256 `14241db0`.
- `0e94959`, `85118d4`, `11dce1c` — inmatch_bounce_surface_v1 v0.3 / v0.2 / spec.
- `de62d7f`, `d23fff5`, `5020f10`, `8e8f46e` — exit_optimized_bounce_v1 spec v0.1 + producer v0.2/v0.3/v0.4. Phase-1 PASS, Phase-2 halted then gate-fixed. **Not re-run.**
- `c9a0f3e`, `c76eee5` — n_profile_v1 MANIFEST + ANALYSIS_LIBRARY register. sha256 `a7ed1155`.
- `a28840e` — n_profile_v1 Pass-1 OOM remediation (Phase-3 validated at full corpus). **The producer commit of record.**

Pre-arc context: `7911478` CHAT_HANDOFF post-Rung-0 landing (2026-05-15); `44c9ec6` SESSION_HANDOFF stale-path fix (2026-05-14); `19fdd5a` F35 / T37-RECAL canonicalization.

---

## IMMEDIATE NEXT ACTIONS (post-Stage-0)

0. **Premarket-dynamics arc landed (2026-05-22 → 2026-05-23).** Chain: premarket_tape_v1 (`30a47b6`) → fv_history archive + cron (`7d98e74`) → fv_overlap_join_v1 (`a0bc5e6`) → Scope A corpus map (`2ca8890`) → walkover/retirement check (`7c15776`) → **Path B fill mechanics (T43, `1e00818`)**. Net empirical picture: the atlas T-20m taker anchor (T42, locked exit) can be entered earlier as a maker for a per-regime expected entry-improvement of up to ~2.46¢/N (hindsight ceiling), strongly favorite-skewed (Scope A T4 drift gradient is the mechanism; walkover check shows ~half the extreme drift is reversal-driven so the deployable signal is the completed-match ~±5-6¢ gradient). **Next:** the bid-laying policy spec can now be drafted from Path B's per-regime fill rates (entry side) layered on the locked atlas exit — it is its own T-item, not yet opened.
1. **This Stage 0 reconcile completes first** — eight commits land before any new execution-phase work:
   1. SESSION_HANDOFF.md rewrite (this doc)
   2. CHAT_HANDOFF.md → pointer stub
   3. ANALYSIS_LIBRARY.md (T40/T41/T39.1/T39.2/T42 entries)
   4. ROADMAP.md (T40/T41/T39.1/T39.2/T42 added; T36/T11/T32 statuses confirmed; execution-phase sequence noted)
   5. MANIFEST.md (atlas entry with sha256s and producer commit)
   6. CROSS_CATEGORY_MAP.md (deprecation header pointing to LOCKED_DOWN + PAIRING_DIAGNOSTIC)
   7. README.md (current-state + next-major-step updates)
   8. docs/handoffs/EXECUTION_PHASE_HANDOFF.md (archive with prefix note flagging known gaps)
2. **Read `bot_v5_shell_architecture.md`** — operator-pending recommendation on v5 vs v3 for hot-reload.
3. **Bug 4 implementation** — operator review of `bug4_brief.md` is required before CC prompt drafting. 500+ lines, settlement-state-mechanics-dense; mandatory operator eyeball before any CC prompt.
4. **Layer B v2 spec revision** — per T36 amendment, spec must be revised against T37 foundation before producer build.
5. **Paper-mode integration test suite** — design after Bug 4 lands.
6. **Capital deployment plan** — after paper-mode validation against live tape. Far-future tracking per T26.

---

---

Latest landed analysis: **Path C arc wrap-up — feature-conditioned entry refinement (T48), NEGATIVE; the empirical strategy arc is CLOSED**, analytical commit `701ccc8` (2026-05-23). Commits the held Phase 2 (offset modulation, best +0.089pp gross = noise) + corrected Phase 3 (execution-mode, best −0.248pp net) negatives as one unified writeup framed against v4's positive. **Unified mechanism (LESSONS A43): the locked atlas fixed-profit exit (+X regardless of entry) caps entry-side feature conditioning** — a fill predictor with genuine signal (T46 holdout AUC 0.73) has no entry-side channel to monetize, because the entry discount only moves the hold-to-settlement minority + capital, not the dominant triggered-exit payoff. The productive lever is the **static per-cell offset re-optimized on net-PnL (T47 Path B v4, +1.024pp, DEPLOYED)**, not per-event variation. Synthesis: `docs/analysis/premarket_dynamics_v1/path_c_arc_findings.md`; both run_summaries + MANIFEST + 4 promoted parquets. Doc commits `9fc0319` (ROADMAP T48) + `4abe792` (ANALYSIS_LIBRARY T48) + this update; **commit 5 (LESSONS A43) follows**. Preceding: Path B v4 (T47, `c90985b`, DEPLOYABLE); Path C Phase 1 (T46, `22f3221`); Path B v3/v2/v1 (T45/T44/T43).

**Empirical premarket-dynamics strategy work is CLOSED.** The deployable spec is `bid_laying_policy_v1.md` v4 + `per_regime_offsets_v2.csv` (shallow per-cell offsets, net-PnL-optimal). The Path C arc proved the architecture's ceiling: locked fixed-profit exit + static per-cell maker placement on the correct objective is the empirical limit on this strategy; per-event feature conditioning adds nothing through the tested channels (offset modulation, execution-mode switching, skip-gating). **Next work is execution-lock, not strategy: Bug 4 settlement mechanics → Layer B v2 (tick-level fill realism, T36) → paper-mode integration → paper-mode live → capital deployment.** Remaining strategy-side ideas with a credible mechanism are exit-side (not entry-side) — re-optimizing the atlas X per cell on net-PnL, or an exit-outcome predictor — see `path_c_arc_findings.md` Section 7.

End of handoff.
