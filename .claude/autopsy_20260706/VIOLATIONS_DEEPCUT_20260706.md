# VIOLATIONS DEEP-CUT + TRIPLE CROSS-CHECK — 2026-07-06 post-flip session

**Prior art (C45 gate):** JUNE_VAULT §4I C-BOUND-RULING (21eaad4, 07-05) · §0A PRIORITY-1=PAIR (88e254e5, 07-02) · aim-table doctrine §4-§5 (07-03, named the simultaneous-fill residual + STATIC/CHASED census) · C42 C-REAIM-ON-ARRIVAL (3691ff5, 07-04) · premarket_walk_cap arm (ba08243, 07-03) · pair_governor grave (f4a766d, 06-29, SUMTAK duplicate-buy: "serialization one-post-per-leg-per-tick NEVER built") · paired_cap BANNED lineage (06-12) · A54 mark-to-market note (in-code, `_repost_missing_siblings`) · riser pre-registration SCOREBOARD_20260706.md (07-05, bar (e) = the walk-cap follow-up tripwire) · PART1_SPEC :96 (07-05, completion conception deliberately legacy-clock) · PLEX flip ruling conds 3/5/6 (07-06). Newer trumps older throughout; dates cited inline.

Session: boot 2026-07-05 23:50:39 ET (`per_match_clock:true`, armed 297a7086). 36 zero-tolerance violations in the monitor stream at pull time (board showed 33 at 10:54, 34 at 11:03; 3 more landed by cycle 143 — same two classes). Every count below is per-violation-record, dedup by monitor key, ts ≥ boot.

---

## CLASS 1 — walk_cap_breach ×19 (all ITF_M/ITF_W, all ref=join_bid)

**Proven mechanism (ordering proof, not hypothesis):** every one of the 19 violating buys executed **hours BEFORE `window_open_set` fired** for its ticker (violations 23:50–09:18; conception stamps 04:00–11:05, every one at legacy-clock ttm≈240min). The bot-side cap (`premarket_walk_cap`, live_v4.py:7770-7779) keys on `self._window_open[tk]` — **empty at decision time → silent no-op**. `premarket_walk_capped` fired **0 times all session**. Conception (`_maybe_set_window_open`, :2620) is stamped at legacy T-240 by design (PART1_SPEC:96, 07-05); the flip opened honest ITF windows 6–10h before that stamp exists. **The cap is structurally inert in exactly the window the flip created** — the honest-window question, answered.

Sub-split (per-violation chain match, `vio_contexts.json`):
- **W-a ×10 — monitor-semantics false positives**: the graded buy is a **fresh `v4_place`** at the entry-table target (e.g. LUKNOE-LUK 56c from cell 74, `anchor_src=last_traded`), graded against a conception stamped hours LATER (ceiling 18 from a 06:30 stamp applied to a 00:30 buy). ZT3 assumes conception precedes all buys — true pre-flip, false post-flip. Retroactive grading; no walk occurred at the graded moment.
- **W-b ×9 — real uncapped walks**: `v4_move_repost` join_bid chains with no ceiling (VLADIL 27→38 = +11c; LUKNOE 56→59→66→67 = +11c across the chain; HIEGUT 37→41; TSIAND/TEXCAR/LENTHE/HOSGAT +1 steps of longer chains). Session-wide chase census (riser fills, CHALL/ITF): **60% walked up before filling, median +6c, max +57c** — the ALCCLA disease (07-03) at population scale.
- Damage attribution: walk-chased fills that went naked settled the F-track losses — WONIBR −$3.25, BOIBOY −$3.85, LENTHE −$3.25 (one-sided, chase-priced).

**Category-scoped verdict: ITF-only, honest-window-only. Bot defect (W-b) = cap anchor void; monitor defect (W-a) = conception-ordering assumption.**

## CLASS 2 — combined_over_goal ×16

Split by proven lifecycle (`stale_order_forensics.json`, exchange order_id joins; `bound_coverage.json` site map):

- **C-a ×7 — FABRICATED at booking (monitor artifact + real booking defect)**: TODSAG, VAJRAM, HERNAG, POTFEL, TEUHAS, PACLOV, KULVOG. The leg-2 orders were priced **exactly AT the bound** (97−basis) by the re-aim/goal machinery — which worked. The fills were booked via reconcile adoption at `market_exposure_dollars/qty` = **mark-to-market, not cost** (:8290-8291 → `_v4_reconcile_naked` :8356/:8447), fabricating +1..+9c. Exchange-VWAP combined: PACLOV 106→**97.0**, TEUHAS 105→**97.0**, VAJRAM/POTFEL 101→**97.0**, KULVOG 102→**95.5**, TODSAG 98→**95.5**, HERNAG 98→**85.8**. The code documents this exact trap in-code (A54, :3847) and the sibling-repost path already fetches true basis — the adoption sites don't. Booking price also selects the exit cell → **exit-cell poisoning** on every adopted fill (144 adoptions this session).
  - **Underneath 4 of these: the real orphan defect** — three unserialized writers of `pos.entry_order_id` (`_reaim_sibling_on_arrival` :3814-3829, `_repost_missing_siblings` :3911-3919 off a pass-start ord_map snapshot :8299, `_v4_move_repost` overwrite :7791) clobber each other → bound-priced orders left live and untracked. POTFEL stacked a duplicate 5-lot (double-filled to 10); TEUHAS/HERNAG twins double-filled; **KEYNOS (Class 3) is the same defect filling 23min in-play**.
- **C-b ×6 — pre-basis same-tick races (design residual, accepted 07-03)**: DZJMCK, HERNGU, ERHSIN, HESPAL, DUHCAR, BASBAD. Both legs resting, filled <1s apart, re-aim cancel raced and lost. Overs +1..+5. The aim-doctrine (07-03) named this verbatim: "simultaneous independent entry fills at rich prices are a race neither fully closes." The only known closer is a pre-fill combined veto = **paired_cap, BANNED lineage** (06-12; residue struck 3×). **Named unsolved — by doctrine choice, bounded ~+1..+5c on 5-lots.**
- **C-c ×2 — bound-enforcement holes (real bot defects, law breaches of 21eaad4)**:
  - TSIAND +4 REAL: `_v4_move_repost` bound computed in the pre-await decision slice while leg-1's fill was 3s from booking; no post-await re-check; the arrival hook fired in the cancel→place gap and judged the stale 69c order clean. (:7684-7711 clamp is pre-await only; :7734-7789 awaits.)
  - SILDIG +10 REAL: **fresh `v4_place` path carries no pair bound at all** (site-4 structural hole; riser branch posts at best_bid unconditionally :2302-2313; the only basis-aware placement guard is T50, dormant under `paired_cap_enforced=false`). Posted 98c vs bound 88, filled → 107.
  - Near-miss census (whole session): post-basis over-bound orders = **5 total** (VULCOU rescued, TEXCAR rescued, TSIAND filled, SILDIG filled, LAPCIO rounding-compliant). These two mechanisms are the ENTIRE post-basis exposure surface.
- **C-d ×1 — honest cancel-fill race**: GARCIO +1 (cancel success 1.7s after the fill; leg-1 booking latency ~16s). Race residual, bounded.

## CLASS 3 — grace_breach ×1 (WTA_MAIN KEYNOS)

Order e71a32af placed 08:12:34 by `reaim_sibling_arrival`; 15s later `sibling_repost_placed` stacked a second order and overwrote `entry_order_id` → e71a32af **orphaned live**. Latch 10:50:26, grace-cancel 10:56:01 killed only the tracked order. The orphan filled 54c at 11:12:42 — 23min past latch. Same orphan family as C-a; the grace machinery itself worked. (Pair completed at 97 combined; position open.)

---

# TRIPLE CROSS-CHECK (per candidate; a fix failing any prong does not ship)

## Candidates
| id | fix | class addressed |
|---|---|---|
| P1 | **C-TRUE-BASIS**: `_v4_reconcile_naked` books fills-API buy-VWAP (new `_true_entry_basis`, the :3874 A54 pattern), not pos_map mark-to-market | C-a (all 7) + exit-cell poisoning on all adoptions |
| P2 | **C-BOUND-RECHECK**: re-derive goal−basis clamp AFTER the poll/cancel awaits in `_v4_move_repost`, before place | C-c TSIAND (+ VULCOU-class) |
| P2b | **ownership-abort**: `_v4_move_repost` aborts placement if `entry_order_id` was re-keyed across its awaits (log-only residual for the place-await micro-window — no cancel added) | orphan mechanism A |
| P3 | **C-BOUND-SITE4**: fresh-place clamp `target_bid ≤ max(1, goal − sibling booked basis)` at the entry scan | C-c SILDIG (+ TEXCAR-class) |
| P4 | **dup-guard**: `_repost_missing_siblings` also honors the in-memory in-flight entry (`phase==entry_resting` + `entry_order_id`), fresher than the pass-start ord_map snapshot | orphan mechanism B (POTFEL dup, KEYNOS) |
| S1 | walk-cap position-anchored fallback (cap walks at first-post + per-cat cents when `_window_open` unset) | W-b — **STAGED GATED-OFF, not shipped** (see verdicts) |
| S2 | full order-ownership serialization + orphan sweeper | orphan class root — **NOT SHIPPED** (see verdicts) |
| M1/M2 | monitor: ZT2 grades combined off exchange fills API; ZT3 skips buys that predate the conception stamp | W-a + C-a false-positive halves (tooling, read-only) |
| R1 | riser_post_revision disarm | pre-registered rule — **DEFERRED TO PLEX** (see verdicts) |

## (a) PRIOR ART — chronological
- **P1**: A54 (in-code, 07-04 era) documents the exact trap; `_repost_missing_siblings` (fc6191b6, 07-04) already ships the true-basis fetch — P1 extends the SAME pattern to the adoption sites. C44 (07-04): exchange truth over bot bookkeeping. No grave contradicts; maker/taker-truth law (06-xx, memory) is the same principle. **PASS.**
- **P2/P3**: C-BOUND-RULING (21eaad4, **07-05**) is deployed LAW: "every resting/reprice/completion path bounds combined ≤97." Site-4 and the post-await window are implementation gaps of that law — P2/P3 complete it. §0A (07-02): "the combined cap binds the SECOND leg's target after the first fills — a walk constraint, never a participation filter" — P3 clamps price, never skips (max(1,·)). C42 (07-04) closed the same gap-class at three other sites. paired_cap grave (06-12) bans pre-fill VETOES — P2/P3 are post-basis clamps, not vetoes; T50's dormancy untouched. **PASS.**
- **P2b/P4**: pair_governor grave (06-29 SUMTAK): duplicate-buy collision root = unserialized writers; "re-arming re-adds the collision" — P2b/P4 are the first serialization steps, placement-side only. §4H standing lock "no cancel rework" (07-01/02): respected — neither adds/changes a cancel; both ABORT placements. **PASS.**
- **S1 (walk-cap fallback)**: erosion bar (e) pre-registered the follow-up build (07-05). BUT the per-cat cap sizes (ITF 4c) came from the **07-03 card-clock census**; no honest-window census exists (the population is one night old, and books legitimately drift tens of cents over 7h windows). Prior art also warns: freeze_at_gun SHELVED (07-03) for over-freezing. **PASS with census precondition.**
- **S2**: grave says the serialization was "NEVER built"; building it fully touches cancel/resolve machinery → §4H lock. **FAIL (a) for tonight — staged as design only.**
- **R1**: pre-registration (07-05) fires the disarm rule mechanically ((a) median −1¢ < +1¢). BUT the baseline was the card-clock box and the flip changed the population 64min after the riser deploy; the non-eroded median is +1¢ and the failure mechanism is (e) erosion (60%), which the pre-registration routes to the walk-cap follow-up, not disarm. Riser is a Plex-adjacent armed build (bde7c958 gate). **Verdict: report rule-fired; disarm decision to Plex/operator — not flipped unilaterally under the week hold.**

## (b) INTERACTION SWEEP — every armed flag × each shipped fix (P1, P2, P2b, P3, P4)
- **per_match_clock / _shadow**: none of the five touch window construction, liveness, latch, or abandon (flip ruling cond 6 respected — grep-provable: no `_is_match_live`/`latch`/`abandon` in the diffs).
- **leg2_reshuffle (97)**: P2 re-runs the reshuffle's own bound post-await (same formula, lower-only); P3 applies the identical bound at placement. Both only LOWER targets → reshuffle semantics preserved; `reshuffle_pinned` stamped so churn-fix (repost_hold/stale-pin) exemptions apply to clamped bids.
- **reaim_on_sibling_arrival**: P1 gives it a TRUE basis (its bound was computed off inflated adopted avgs — now correct, strictly tighter-or-equal never looser... note: true basis ≤ mark avg on these cases, so bounds LOOSEN toward correct, +1..+9c less aggressive cancels — this is the intended correction). P2b prevents move_repost from orphaning reaim's orders. P4 prevents sibling-repost from stacking on reaim's orders.
- **premarket_walk_cap**: untouched (still window-open-anchored; its honest-window void is S1's job, staged).
- **riser_post_revision**: P2/P3 do not touch the conception-site riser post (bounds only bind once a sibling basis exists — a riser leg-1 by definition has no filled sibling... when leg-2 fills first the "riser" becomes the bound target, which is the LEGWIN-class protection working as law). Erosion measurement unaffected.
- **repost_hold_same_price / marketable_stale_pin_exempt**: P2's clamp runs BEFORE `_projected_repost_price`? — No: the hold check (:7717) precedes the awaits; P2 runs after. A P2-clamped target equal to the resting price re-posts once (one extra churn round-trip in the rare clamp case) — accepted, logged, bounded by the clamp's rarity (5 post-basis cases/session).
- **repost_sibling_on_boot**: P4 adds one skip-reason to its scan; its once-per-event guard and bounded pricing unchanged.
- **fallback_pair_bound / completion / complete_cross**: untouched (P1 changes the INPUT price of adoption booking, which completion re-aim hooks read — they become correct; `_completion_target` formula untouched, REANCHOR scope-confinement respected: no completion/exit/meter/routing logic edited).
- **match_live_grace_kill / latch_tape_override**: untouched; P2b/P4 REDUCE the orphan population the grace-cancel cannot see (KEYNOS class) without touching the cancel itself.
- **per_cat_depth / depth_aware_join / staircase***: placement targets flow through unchanged except the final min() clamp (P3) — depth/staircase reference_sources unaffected (`staircase_hold` early-returns before the walk path; P2 sits in the join/regime walk only).
- **kalshi_occ_observe / scale_gun_shadow / pm_clock_shadow**: observe-only, untouched.
- **The honest-window question (what breaks that was calibrated for card windows):** P1–P4 are clock-independent corrections (true prices, law bounds, write-ownership). The only candidate whose CALIBRATION is card-clock-derived is S1 (ITF 4c cap) — which is exactly why S1 does NOT ship tonight.

## (c) OUTCOME REPLAY — two-lane, last night's own tape (`outcome_replay.py`)
Lane 1 (mechanism): per violation, apply each fix to the recorded chain — does it block/re-aim/correct it? Lane 2 (P&L): delta on the night, n flagged.
Results (see script output in this dir, run on the pulled session data):
- P1: all 7 C-a violations dissolve at the source (booked = exchange, bound-compliant); 144 adoptions re-book at true basis; **zero order flow altered → every clean fill survives by construction; participation identical**. Lane 2: $0 direct (booking correctness); grading/exit-cell placement corrected (9 exit cells shift; see script).
- P2: TSIAND repost 77→73 (blocks the +4 over; the 73 bid may or may not fill — Lane-2 range −$0.20..+$1.15 on that pair, n=1 flagged luck). VULCOU-class already-rescued unchanged. No clean fill touched (clamp fires only on the 5 post-basis cases, all violations/near-misses).
- P2b: KEYNOS-class orphan at move_repost prevented (0 occurrences tonight took this exact path — the guard is prophylactic for mechanism A; TODSAG/VAJRAM orphans predate any move_repost interleave and are P1/P4 territory).
- P3: SILDIG 98→88 (blocks +10; 88 was the standing bound bid that had already been placed twice — participation retained at the bound). TEXCAR fresh 37→30 (rescue no longer needed). No other fresh place all session had a filled sibling + over-bound target → zero clean-fill impact.
- P4: POTFEL duplicate 5-lot never placed (−$2.85 exposure, half the double-fill); KEYNOS second order never placed → the ORIGINAL stays tracked → grace-cancel reaches it → no in-play fill. TODSAG/TEUHAS/HERNAG/PACLOV duplicates similarly blocked (4 events). Clean-fill check: all 114 sibling_repost placements scanned — only those with a live in-memory in-flight entry are skipped (the dup set); legitimate WATSHI-heal reposts (no in-flight order) unaffected.
- Lane 2 total (all five): violations blocked/corrected worth ≈ +$8–12 of the −$16.96 violation-game damage (dominated by orphan double-fills and the SILDIG/TSIAND overs); n=26 settled violation games — **flagged: single night, luck-polluted below n≈30.**

## VERDICTS
- **SHIP (bundle C-TRUE-BASIS+BOUND-LAW, one deploy):** P1, P2, P2b, P3, P4 — all three prongs PASS. These complete the deployed 07-05 law + fix write-ownership at the two placement sites, with zero participation loss on replay.
- **STAGE GATED-OFF:** S1 (walk-cap honest fallback) — fails (b) tonight: cap size has no honest-window census (card-clock calibration; the exact failure mode this job was told to hunt). Staging spec: anchor = position's first-post; per-cat cents TBD from ≥3 nights of honest-window walk census; arm via Plex.
- **DO NOT BUILD NOW:** S2 full serialization — §4H lock (cancel rework); P2b+P4 take the two proven placement-side entries into the defect instead.
- **NAMED UNSOLVED:** C-b same-tick pre-basis races (6 tonight, +1..+5c) — closable only by the banned pre-fill veto; carried openly, not half-fixed. Monitor artifact halves (W-a) get M1/M2 tooling fixes, not bot changes.
- **DEFER TO PLEX:** R1 riser disarm (rule fired; population caveat; erosion routes to S1).
