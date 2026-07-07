# DOCTRINE-VS-BOT CONFORMANCE — the Living Vault marched against the live process (2026-07-07 ~14:15 ET)

**Method:** read-only vs the bot (PID 704299, blob `01d8dec` lineage, LIVE all day). Referee = today's jsonl (`logs/live_v3_20260707.jsonl`, ~14:00 ET cut) + exchange truth + live config (`deploy_v5_live.json` as loaded). Every actionable claim in LIVING_VAULT.md + LESSONS A–G + `.claude/rulings/` gets three columns and no fourth option: **claim | code cite | LIVE PROOF from today's tape** — or it goes to UNPROVEN-LIVE with a trigger/detector. Every grave gets a tripwire or a named gap. **Re-verification cadence: this audit re-runs POST-ANY-DEPLOY (the tape section, ~10 min) and WEEKLY in full (with the archaic sweep).** Producers: `/root/conformance_tape_pull.py` (event census).

## 1 · LAWS & INVARIANTS — claim | cite | live proof (today)

| # | claim (law / invariant / ratified behavior) | code cite | LIVE PROOF (today's jsonl) |
|---|---|---|---|
| 1 | Buy chokepoint: committed exposure = exchange held + resting buys, ≥lot → refuse; fail-closed on API miss (C47 family) | live_v4.py:3086-3140 | `buy_blocked_position_full` ×57 (01:24:53 KHOSAM-KHO current_qty 5 → refused) + `buy_qty_reduced` ×4 (07:33 MABROS 4 held → reduced to 1) |
| 2 | Conception halt: failed book audit stops ALL buys, exits keep working (C49) | :3079-3084 | `buy_blocked_conception_halt` ×33 (12:35:51 SOTTEO-SOT) while `v4_exit_posted` continued through the halt window |
| 3 | Post-boot book audit within 5 min, assert-and-halt, jsonl-verified (C49) | :8622-8760, boot :9304, re-audit :9556 | `post_boot_audit` ×15: boot FAIL 12:35:29 (19 failures) → `conception_halt_cleared` 12:59:36 → v1.2 boot PASS 13:13:34 — the full arm→clean→clear cycle on one day's tape |
| 4 | EXIT QTY = POSITION QTY (booking + reconcile top-up + consolidation) | :5508 (`open_qty = ex_open`), :8918 (top-up), qty-gap path | `reconcile_exit_topup` ×13 (BUEXAV 1→5 @86) + `reconcile_exit_posted` qty_gap ×22 (02:06 CHOCHE position_qty 7) + audit PASS table exit-qty==held on every held leg |
| 5 | Reconcile reads exchange truth PAGINATED (C47) | reconcile() cursor walks (:8640s); audit same | `post_boot_audit` n_resting_orders=234 (>2 pages) in one read; boot sweep `sibling_bid_alive` skips ×11 — guards seeing past page 1 |
| 6 | Completion cross bounded ≤100 par (C-BOUND-RULING 4I) | cross_bounds_ok:192, _try_complete_cross:7472 | `complete_cross` ×1 (10:38 AUGDJO basis **exactly 100** admitted) + `complete_cross_skip` ×30 (01:16 TAGSUZ basis 119 REFUSED, cap named in the event) |
| 7 | leg2_reshuffle: faller re-aim to min(aim, 97−basis), re-derived per walk (goal law) | _reshuffle_leg2_target:2301 | `leg2_reshuffle_reaim` ×22,389 (MATKOM →7 vs basis 90, goal 97) |
| 8 | Re-aim on ANY sibling basis arrival, no bucket exempt (C42) | _reaim_sibling_on_arrival:3947 | `reaim_sibling_arrival` ×78 (03:05 MARDEV 5→3 after leg1 94) |
| 9 | Sibling repost on boot from exchange truth, once/event, live-exempt, dup-guarded (C-REPOST-SIBLING) | _repost_missing_siblings:4033 | `sibling_repost_placed` ×355; `sibling_repost_scan` ×309 with skip reasons (`sibling_bid_alive`/`sibling_position`/`event_live`) |
| 10 | TRUE basis from fills VWAP, never pos_map avg (A54 / C-TRUE-BASIS) | _true_entry_basis:4013 | `adoption_true_basis` ×107 (01:07 TIAZHO mark_avg 39 vs true_basis 44) + `reconcile_price_mismatch` ×2,112 logged-never-corrected (the A54 artifact metric) |
| 11 | Honest clock windows (per_match_clock, Ratification #20) | flag TRUE; window machinery :1526s | `window_open_set` ×633 (SIMROU 10:23 exhibit earlier today) |
| 12 | Tape latch + grace 300s (match_live_grace_kill) | :3675-3690, :1411-1412 | `match_live_detected` ×100 (volume_burst) + `match_live_grace_armed` ×49 |
| 13 | latch_tape_override: quiet counter-evidence unlatches a lying latch | :1653-1659, :4540 | `match_live_unlatched` ×5 (03:29 NAKIDO reason counter_evidence_quiet, 300s) |
| 14 | premarket_walk_cap per-cat ceiling above conception cell | :2322-2325, enforcement :4927 | `premarket_walk_capped` ×2 (07:38 SOUJED proposed 94 vs ceiling 76, cap 4 ITF_M) |
| 15 | Same-price repost hold (churn fix, C-CHURN) | flag + hold event | `v4_repost_hold_same_price` ×425 |
| 16 | Ex-self CARRY live: every shadow line answers posture vs the NON-SELF chain (expression ruling, observe half) | _book_ex_self:5082, _aim_shadow_log:2219-2283 | **1,787 `bid_ex_self` lines today** (aim_shadow ×1,988 with postures + shadow aims + dip_admissible) |
| 17 | Expression CLAMP gated OFF by ruling (arm awaits evidence) | _express_target:5107; `expression_invariant` ABSENT→False | `expression_clamped` = **0** — proof of the OFF state as ruled (not a fire) |
| 18 | Aim = dip, FV = yardstick (aim-table doctrine); shadow carries aim25/50 | :2219s + aim table dispatch | aim_shadow fields `shadow_aim25/50`, `dip_admissible` on 1,988 lines; `would_skip_walled_post` ×300 (wall observe A49 lineage) |
| 19 | maker_only_entry: the only taker is the bounded completion cross | flag TRUE; chokepoint :3061 | today's sole taker entry = the `complete_cross` in row 6; every other entry resting maker |
| 20 | Completion V1-V4 + engagement E1-E3 tripwires armed each boot | :2642-2650 + boot arms | `completion_tripwire_armed` / `engagement_tripwire_armed` at each of today's 4 boots; zero violation fires |
| 21 | Exit bands from the sealed surface, band levels untouched (0A + Vault seal) | _v4_apply_exit:5442+ | `v4_exit_posted` ×678, every one carrying band_x/cell_id from the gated-optima surface |
| 22 | Gate laws C40/C45/C46 (lint+smoke+prior-art+outcome-proof) | deploy/deploy_gate.sh [0-3] | THREE gated deploys ran today (10:21, 12:34, 13:13) — console records `DEPLOY GATE: PASS` each, outcome proofs cited (PROOF_PASS ccf8fa8f, PROOF_AUDIT ee8b108d lineage) |
| 23 | Copilot/manual frame: manual legs adopted attributed, bot defers (operator_manual_mode) | flag TRUE; adoption attribution | `reconcile_v4_adopted` ×437 with attribution field; SIMROU `manual_first` skips this morning |

## 2 · UNPROVEN-LIVE (no tape event today — trigger or stamp, no silent passes)

| claim | cite | status + detector |
|---|---|---|
| Never-marketable clamp (maker buy ≥ ask → clamp to ask−1) | :3067-3077 | **AWAITING NATURAL OCCURRENCE** (0 today — book conditions never crossed a maker target). Fired on prior tapes. Detector: `never_marketable_clamped` event key; weekly cadence checks the counter. No smoke trigger — deliberately posting a crossing maker buy is a real order; not worth it. |
| Hold-to-settle rule (band rule "hold" → NO exit by config) | :5495s (rule=="hold") | **AWAITING NATURAL OCCURRENCE** (0 `hold_to_settle` today — no hold-cell fills). Detector: event key + C47 audit `hold_rule` exemption column (present in every audit table today, value false on all — consistent). |
| C50 two-file close-out gate | deploy_gate.sh [4/4] | **BOOTSTRAP PENDING** — law shipped after today's last deploy; no deploy has run through it. Trigger: the NEXT deploy (first = warn-pass + records `state/last_deploy_sha`, then strict). Detector: gate console line `two-file law OK` / `CLOSE-OUT REFUSED`. |
| v1.2 float guard on fractional-residue legs | :3103-3110 | **AWAITING NATURAL OCCURRENCE** (no buy attempt on a fractional leg since 13:13 boot). Detector: `buy_qty_reduced` with non-integer committed; C47 audit `conception_on_owned` (EVAGOW was the v1.1-era catch). |
| C-ERROR-TRIPWIRE (≥20 errors/600s → CRITICAL + /tmp file) | live_v4 tripwire block | **NOT FIRED today** (order_error ×131 spread across 13h; no `/tmp/live_v4_TRIPWIRE.json` check ran in this audit — stamped as the gap). Detector: the tripwire file + CRITICAL log line; weekly cadence adds the file check. |
| C-KALSHI-OCC coarse-start guard (real-future-≤36h) | _kalshi_occ_start:1220 | observe-mode (`kalshi_occ_observe`=True); no schedule_gap ITF-W case today. Detector: its observe log key. |

## 3 · CLOSED DEFECT CLASSES — tripwire per grave (exhibits: race counter, CLAHER counter, cycle-119 grace forensic)

| grave / defect class | recurrence signal | live tripwire TODAY? |
|---|---|---|
| Dup-buy storm (class a) | >1 same-side buy order / committed > lot | ✅ chokepoint guard (57 fires) + C47 audit `buy_stack`/`conception_on_owned` every boot + monitor `reaim_sibling_race` counter |
| Naked-surplus exits (class b) | held > resting sells | ✅ C47 audit `exit_qty_mismatch`/`no_exit` (caught 12 real at 12:35) + reconcile top-up/consolidation events |
| Post-only-cross exit hole (OPEN, queued build) | sell 400 "post only cross"; ITM leg exitless | ✅ `order_error` 400 counter (131 today, class within) + C47 `exit_unpostable_itm` flag (CLAHER live counter) |
| Grace breach (fills past latch+300) | fill ts > latch+grace | ✅ monitor ZT `grace_breach` (cycle-119 forensic = the exhibit) |
| Combined pair > 97 goal | pair basis over goal | ✅ monitor ZT `combined_over_goal` |
| Walk-cap breach | buy above conception ceiling | ✅ monitor ZT `walk_cap_breach` + `premarket_walk_capped` events |
| Handler errors / ENOSPC class | handler_error events | ✅ monitor ZT `handler_error` (its first catch WAS the disk-full) |
| Same-tick booking races | pre-basis fills, dup adoption | ✅ monitor race counter (`reaim_sibling_race` source stamps) |
| Duplicate same-scope defs (C39) | later def silently wins | ✅ lint_gate AST at every deploy (gate-time, 3× today) |
| Schedule-lie clock (ALCCLA) | latch vs quiet tape divergence | ✅ `match_live_unlatched` counter-evidence (5 today) + honest clock |
| pos_map-avg basis fabrication (A54) | adopted basis ≠ fills VWAP | ✅ `adoption_true_basis` delta + `reconcile_price_mismatch` (2,112 today, logged-only by design) |
| Unbooked fills / link-path invisibility (F39) | exchange fill with no book event | ✅ C47 audit diff-vs-banked + SLATE continuity cuts (ledger-time) |
| Cancel-410 / v1-endpoint rot | 410 deprecated on order ops | ✅ `order_error` status counter (any 410 = instant class signal) |
| Sub-1 fractional residues accumulating | positions 0<q<1 with no exit | ⚠ **NO-TRIPWIRE**: C47 audit deliberately skips h<1.0 (tolerance) — residues are invisible to it. **GAP → BOARD: add a residue-count/Σ column to the audit event.** |
| Console-truncation measurement (C47 second half) | key-presence read on console | ⚠ **PARTIAL**: deploy script now greps the jsonl; no guard against a future ad-hoc console grep — process law only. Cadence item, not runtime. |
| FV-gate-on-A regression (doctrine grave) | an A-grade gated on FV anywhere | ⚠ **NO-TRIPWIRE** (doctrine-only): detector = this audit's weekly grep of grading code for FV gates. |
| Directional-entry resurrection (06-15 grave) | any directional entry branch armed | ⚠ **NO-TRIPWIRE** runtime; config inventory in this audit is the detector (no such flag exists today). |

## 4 · ARCHAIC SWEEP — retired views vs code paths

| item | state in code/config | verdict |
|---|---|---|
| `pair_governor_scoot` | config **False**; code path gated | dead-as-configured ✅ (grave: dup-buy; lineage closed into reaim) |
| `riser_post_revision` | config **False** (pre-registered disarm executed) | dead-as-configured ✅; code retained for the Plex bounce re-arm |
| `freeze_at_gun` | config ABSENT→False; :1640-1646 docstring says CONTRADICTS gun+300 doctrine, DO NOT arm | shelved-in-code, correctly self-labeled ✅ |
| `expression_invariant` | ABSENT→False | STAGED-BY-RULING (not archaic — arm awaits shadow evidence + four-bar gate) ✅ |
| `fv_anchor_scenarios_enabled` | **False**; legacy FV routing branch | dead legacy branch, gated ✅ |
| `round5_detector_enabled` | **False**; stubbed | dead ✅ |
| marketable_taker / t20m fallback | gated off under `maker_only_entry`=True (boot line confirms) | dead-as-configured ✅ |
| DCA legacy paths (DCA-A cells) | reachable only via legacy cell configs; staircase tables live | dormant ✅ |
| **`join_trial_mode` = TRUE** | trial ABORTED 06-18; flag still true — gates the trial-abort machinery (:5130-5139) + stamps `join_is_trial` (:7031) | ⚠ **FINDING: archaic-armed flag.** Inert to placement but mislabels live legs as trial and keeps a dead abort armed. → BOARD: config flip to False through the gate. |
| `kalshi_schedule_primary` = TRUE alongside `per_match_clock` = TRUE | schedule-SOURCE swap (:3541) vs window CLOCK (flip) — different layers | coexistence appears intended (4I: LATCH-CAL canonical for aims; occurrence as schedule source) — ⚠ VERIFY item on BOARD (one line in the next clock pass). |
| ≤2¢ branch inventory (the INTERIM-ARCHAIC adjacency) | :3978 `goal_level<=2` → noise-skip (sibling repost, logged `noise_level`); :4095 `level<=2` skip; reaim `<=2c → cancel` (C42-ruled); :2380 spread≤2 book branch | all three RULED or observe-class, none a hard price offset — the INTERIM-ARCHAIC grave (hard offsets) has **no surviving implementation**; aims come from tables ✅ |
| `completion_all_cells` = TRUE | was gated OFF 06-24; armed in the 06-30 ceiling arm lineage | CURRENT (not archaic); noted because memory of 06-24 says OFF — the arm superseded it ✅ |
| tennis_v5.py / live_v3 lineage files | on disk, not executed (tmux runs live_v4 only) | archive ✅ |
| ROADMAP / SESSION_HANDOFF / JUNE_VAULT | tombstoned FROZEN (yesterday's Phase 2) | ✅ |

## 5 · FOLLOW-UP QUEUES (ready-made for BOARD)

1. **join_trial_mode → False** (config-only flip through the gate; archaic-armed flag). 
2. **Sub-1 residue tripwire**: add residue count/Σ to `post_boot_audit` event (closes the one audit blind spot).
3. **kalshi_schedule_primary coexistence check** — one-line verification in the next clock pass.
4. **C50 bootstrap** — confirm warn-pass + SHA recording at the next deploy, then strict.
5. **Never-marketable + hold-to-settle** — natural-occurrence watches (event-key counters, weekly).
6. **Tripwire-file check** (`/tmp/live_v4_TRIPWIRE.json`) added to the weekly cadence checklist.

**Cadence: §1's tape columns re-run POST-ANY-DEPLOY (producer: `/root/conformance_tape_pull.py`); full audit incl. §4 archaic sweep WEEKLY (next: 2026-07-14).**
