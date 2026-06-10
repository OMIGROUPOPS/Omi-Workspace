# PART-2: completion_reprice mechanism — COMMIT 1 (code, dormant)

Single-concern diff to `live_v4.py`, flag `completion_reprice` **default OFF** (key absent
from `config/deploy_v5_live.json` — verified). Commit 1 = this code, dormant. Commit 2 =
activation, ONLY after the dormant gate clears and on separate instruction.

**NOT touched (verified):** exit surface, `_v4_apply_exit`, mid-based repost reference,
taker-cross entry bug, T-15 buffer for fresh entries, `placement_minute` bound, FD limits,
Bug-4 settlement paths, `deploy_v5_live.json`.

## Mechanism

At each of the THREE entry-fill booking sites (check_fills entry poll; placement
instant-fill `_book_placement_cross_fill`; T-20m instant-fill), the existing sibling call
`_cancel_sibling_if_paired_over_cap` is extended into ONE handler, mutually exclusive by
cap arithmetic:

- `leg1_basis + sibling_bid > 99` → **T50 cancel (UNCHANGED, byte-identical)**
- `elif completion_reprice AND (category, leg1.window_open_cell) ∈ completion_cells AND
  sibling.phase == entry_resting` → reprice sibling to
  `s1 = min(s0 + X_cell, sibling_ask − 1, 99 − leg1_basis)` via `_reprice_target`
  (post_only always), qty = **leg-1 FILLED qty**; no-op if `s1 ≤ s0`.

`s0` = SIBLING's window-open price; lookup cell = LEG-1's window-open cell (replay frame,
1944b250, parquet sha `7883f5c8…`). The completion handler NEVER computes a cell from
current_price — the only book-time inputs are the ask clamp and the cap term (CC-confirmed:
no `cell_lookup`/`regime_lookup` call exists anywhere in the completion paths).

**Window-open cell** (`_maybe_set_window_open`): set by the tick loop (apply_trade on each
print + the 60s routing sweep for the T-240 boundary), first time-t-available LAST-TRADE
reference at-or-after T-240. Never mid; never at placement. Lifecycle: (a) set as above,
set-once; (b) bot-level `self._window_open` dict — survives phase transitions AND
position deletion/re-entry; (c) serialized in `_save_v4_resting` (v2 file shape, flag-ON
only) and persisted immediately on set; (d) restored on boot (`_load_v4_resting`,
legacy-shape back-compat kept). Leg-1 fill with the frame unset (pre-T-240 fill) → NO
attempt — designed conservative edge.

**Freshness (item 4):** `V4_COMPLETION_FRESHNESS_SEC = 600` (ships at 10 min, not tuned;
evidence logged as `completion_freshness`). Re-evaluates s1 vs current book (s0/X/leg-1
basis frozen), re-places if changed, refreshes qty to leg-1's current filled qty,
cancel-and-revert when cap headroom gone (`s1 ≤ s0` or `s1 < 1`).

**Buffer exemption (item 5):** `_completion_buffer_exempt` — completion bids ONLY are
exempt from the T-15 `match_start_buffer`; they ride to T-0 under freshness re-evaluation
and are cancelled at T-0 (`t0_reached`, ≤120s latency via the validate backstop; sooner on
BBO updates) or the moment T51 flags the match live. Void/halt = exchange-counterparty
risk: a voided market cancels the resting order exchange-side; NO assumption about void
settlement price exists anywhere in the code.

## Config table

`docs/policy/completion_cells_v1.csv` — 12 rows (one X per cell), columns
`category,cell,X,provenance_sha`, from the 1944b250 SHIP_FIRST set
(sha256 verified `7883f5c8d99200a5dc9c468c381e39ea20441ff93e1c664ac98a0a334ba911e4`):
ATP_CHALL {25,27,35,53,54,56,58}→X=1; ATP_MAIN 35→3, 37→3, 39→2, 41→2, 42→1.
Loaded at boot alongside the entry table (flag-ON only; missing file fails boot loudly).
Absent cell = never attempt.

## Item 6 — CAP-INVARIANT VERIFICATION (code-path enumeration, not example)

Question: can `_paired_basis_ok`'s `sib_cost` ever derive from a completion-repriced
sibling's RESTING bid? Every call site enumerated:

1. **Placement guard (`_route_event` side loop).** The caller leg has no Position
   (`if tk in self.positions: continue`). While a completion bid rests, BOTH legs hold
   Positions (leg-1 active; sibling entry_resting) → neither can be the caller → the
   guard is unreachable with a completion-repriced sibling. After a completion bid is
   cancelled + untombstoned, a fresh placement on that leg calls the guard with sibling =
   leg-1, whose `entry_price` is its genuine FILL basis (filled, `entry_qty>0`) — not a
   resting completion bid.
2. **T-20m fallback guard (`_v4_manage_resting_inner`).** Completion bids branch to
   `_v4_manage_completion` at the TOP of `_inner` and never reach the fallback guard.
   Leg-1 is phase=active and never enters `_inner` (requires entry_resting). So while a
   completion bid rests, no leg reaches this call site; after revert, the sibling seen by
   a reverted caller is leg-1 with its genuine fill basis.
3. **`_cancel_sibling_if_paired_over_cap` T50 arm** (uses `sp.entry_price` as `sib_bid`,
   not via `_paired_basis_ok`). Reachable with a completion-repriced sibling only when
   leg-1 books ADDITIONAL partial fills. There the completion bid IS the sibling's true
   cost-if-filled — the correct quantity for the cap check — and `s1 ≤ 99 − leg1_basis`
   makes the arm fire only if the new average basis exceeds the frozen attempt basis, in
   which case it protectively CANCELS (fail-safe direction). The completion arm then
   no-ops on `entry_mode == "completion_reprice"` (idempotence guard) — no re-reprice.

**Conclusion: no path derives `sib_cost` from a completion-repriced sibling's resting
bid. Option A (original_entry_price field) not required.** (`completion_prev_price` is
nevertheless stored on the Position for revert, so Option A is one field-read away if a
future path appears.)

## Logging (item 7) — wave-gate computable from day one

- `completion_attempt` — s0, s1, X, cap_headroom, trigger_fill_id (leg-1 entry order),
  cell_at_completion_lookup, leg1_basis, qty, sib_ask, prev_bid, order_id.
- `completion_no_attempt` — reasons: leg1_window_open_unset / sibling_window_open_unset /
  cell_not_eligible / no_headroom / already_at_s1 (the no-attempt arm).
- `completion_fill` — SEPARATE from the leg `entry_filled` event; exchange `is_taker`
  from `/portfolio/fills` (never placement intent; feedback rule).
- `completion_freshness` — every 10-min re-evaluation (unchanged or re-placed), the
  evidence stream for post-hoc tuning of the 10-min constant.
- `completion_reverted` (+ time_since_reprice) — reasons: cap_headroom_gone / match_live /
  t0_reached / flag_off / place_failed.
- `orphan_outcome` — terminal no-completion snapshot: BOTH legs' BBO + last-trade +
  ages + time_to_start, s0/s1/X, leg-1 basis/qty → T-20-frame valuation computable
  offline by joining `completion_attempt` ↔ (`completion_fill` | `orphan_outcome`) and
  the existing settlement events. Paired events are separate from leg fills throughout.
- `window_open_set` / `window_open_restored` / `completion_cells_loaded` — telemetry.

## EXECUTION-TIME SPEC PATCHES (flagged for retroactive ratification — all vacuities, verified inert or conservative; no defects found)

1. **X selection.** SHIP_FIRST carries all three X per cell (36 rows / 12 cells); the
   runtime needs one. Selected per-cell `argmax(blended_lift_pp_0p5x)` (the frozen
   deployed-conservative-end objective), tie → smallest X. Every candidate in the
   feasible set is itself SHIP_FIRST-eligible → choice affects edge magnitude only,
   never eligibility.
2. **Sibling frame requirement.** s0 = sibling window-open price (replay `s0 =
   r2["wopen"]`) → sibling frame unset ⇒ NO attempt (same conservative edge as the
   leg-1 rule; logged `sibling_window_open_unset`).
3. **`already_at_s1` inert skip.** If the sibling already rests exactly at s1, a
   cancel/re-place would only forfeit queue priority → skip, logged.
4. **"Ride to T-0" terminalized.** Cancel at T-0 (`t0_reached`) via the manage path;
   T51 match-live still cancels a completion bid (never fill into live play). Latency
   bound: ≤120s after T-0 (validate backstop) or first BBO update.
5. **Revert semantics.** "Cancel-and-revert" = restore the pre-completion bid
   (prev price, entry_size, prev mode; maker-clamped), EXCEPT match_live / t0_reached /
   inside-T-15 → cancel-only (a re-placed bid would be instantly buffer-cancelled or
   would enter live play). Order-place failure → cancel + free the leg (untombstone).
6. **Freshness qty refresh.** Re-evaluation refreshes completion qty to leg-1's CURRENT
   filled qty (later partial leg-1 fills); the initial attempt is idempotent (no
   re-reprice on subsequent leg-1 fill events).
7. **is_taker scope.** Fetched on completion fills only (no API load on non-completion
   paths); the trigger fill's is_taker is joinable offline via trigger_fill_id + /fills.
8. **Window-open persistence vehicle.** Piggybacked on `state/live_v4_resting.json` as a
   v2 shape `{"_shape":"v2","legs":{…},"window_open":{…}}` — written ONLY when the flag
   is ON; flag OFF writes the legacy bare-legs shape byte-identically (regression-tested
   on the exact key set). Loader accepts both shapes. Paper mode does not persist frames
   across restarts (same as resting bids today).
9. **Test-fixture touch.** `tests/test_t50_paired_basis.py` stub gained
   `completion_reprice=False` (the handler's new dependency). Pre-existing failures in
   `test_t60_run7_fallback.py` / `test_marketable_clamp_placement.py` reproduce
   IDENTICALLY on pristine HEAD (stale stubs from earlier Stage-1 features) — not
   touched, out of this diff's concern.

## Tests

`tests/test_completion_reprice.py` — 57 checks, ALL PASS (test_t58 style): reprice clamp;
cap-headroom sweep (`leg1_basis + s1 ≤ 99` for all combos); never-cross sweep; qty
matching (leg-1 FILLED qty incl. partial); buffer-exemption scoping (completion only, all
legacy modes unaffected); freshness re-evaluation (no-op <10min, re-place on ask move,
ts-refresh when unchanged, revert on headroom-gone, t0 cancel-only, flag-off revert,
fill-race); window_open set-at/after-T-240 + never-mid + set-once + stale-reject +
pre-T-240-fill no-attempt + serialization round-trip (v2 + legacy back-compat); flag-OFF
byte-identical (T50 verbatim, completion unreachable, legacy state shape exact-key-set,
no window-open tracking). Full suite at HEAD parity.

## DORMANT-DEPLOY CHECKLIST (commit 1 — flag OFF; STOP after this)

1. Push this commit; on VPS `cd /root/Omi-Workspace && git pull`; verify
   `git rev-parse HEAD` == remote tip (VC discipline — production never runs
   uncommitted code).
2. Verify `config/deploy_v5_live.json` has NO `completion_reprice` key (it doesn't;
   zero config edits in this deploy) and `graceful_shutdown: true` (it is).
3. Run tests on VPS: `python3 tests/test_completion_reprice.py` and
   `python3 tests/test_t50_paired_basis.py` → ALL PASS.
4. **Quiet-hours restart** (no entry windows near opening): SIGTERM the process; capture
   the **duration_sec four-number readout** from `shutdown_drain_begin`/`done`:
   resting_entry_bids pre-count, attempted, cancelled, duration_sec. Exit code from the
   wrapper.
5. FD limit: auto-applied at boot (`_raise_fd_limit`) — verify the
   `[BOOT] RLIMIT_NOFILE soft …` line in the new boot log.
6. Post-boot: reconcile report → 0 orphans; boot log contains NO
   `completion_cells_loaded` (flag OFF); `state/live_v4_resting.json` stays legacy shape
   (no `"_shape"` key).
7. **One full card flag-OFF, zero behavioral delta:** diff the day's log event-type
   histogram vs the prior comparable day — expect ZERO new event types (no
   `window_open_set`, no `completion_*`), unchanged placement/cancel/fill flow.
8. **STOP.** No activation, no flag flip. Commit 2 (activation) on separate instruction,
   additionally blocked on the queued replay micro-addendum (per-cell attempt-arm and
   no-attempt-arm outcome SDs — C3(iii) predicted-SE inputs; recommit artifact with
   updated sha).
