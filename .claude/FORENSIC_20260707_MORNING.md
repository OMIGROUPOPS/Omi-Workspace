# FORENSIC 2026-07-07 MORNING — overnight dup-buy storm + naked-surplus exits

**Status: EMERGENCY CONTAINMENT. Exchange truth throughout (fills / positions / resting-orders APIs pulled read-only 09:38–09:55 ET; artifacts `/root/forensic_20260707.json`, `/root/forensic_analysis2_20260707.json`; producers committed at `arb-executor/analysis/forensic_20260707/`).**

---

## 0. PRIOR ART (C45 gate)

Greps: `LESSONS.md` (`dup`, `paginat|cursor`, `exit.*qty|consolidat`, `position guard`), `.claude/PRIOR_ART_INDEX.md`, gated-flags inventory (`grep "self.config.get(" live_v4.py`), code-resident staged builds.

- **F39 (LESSONS.md:489)** — verbatim: *"link-path position invisibility (after a restart, filled legs with live exits never re-materialize as Position objects)"*. The buy-guard blindness mechanism was ALREADY DOCUMENTED as a result-side hole; tonight it fired on the ORDER side. Delta: this build closes the placement-side consequence (exchange-truth guard at the chokepoint).
- **C-DUP-GUARD 07-06 (live_v4.py:4026, staged in-code)** — placement-side skip for same-pass dup conception in `_repost_missing_siblings` ("12 same-pass dups on the 07-06 tape", POTFEL). Delta: that guard reads `ord_map` — which tonight was a TRUNCATED first-page snapshot — and `self.positions` — empty after boot. It was structurally blind to cross-boot dups; this build fixes the snapshot itself (pagination) and adds the chokepoint guard it presupposed.
- **`reconcile` qty-gap consolidation (live_v4.py:8691-8711)** — prior art for exit-qty repair, but it only runs for UNTRACKED legs (the `sells and not existing` branch); the tracked-leg LINK path (8669-8674) bumps `entry_qty` and never resizes the exit. Delta: same-band top-up added to the LINK path.
- **PRIOR_ART_INDEX: `pair_governor_scoot` DISARMED (duplicate-buy)** — the one prior duplicate-buy incident; its lineage closed into reaim (C43). Tonight's storm is a different mechanism (reconcile blindness, not scoot).
- **⛔ Vault 0A "exits are SOLVED" standing order** — respected by construction: this build changes exit QUANTITY mechanics only (deployed-exit mechanical correctness). Band levels, cells, exit targets, hold rules: UNTOUCHED. No exit-policy work here.
- **Pagination prior art: NONE** (`grep -in "paginat\|cursor" LESSONS.md` → 0 hits). New defect class.
- C39–C41/C45/C46 gate laws apply; this deploy goes through `deploy/deploy_live_v4.sh` with `OUTCOME_PROOF` (see `.claude/proof_20260707/PROOF_PASS.md`).

---

## 1. QUANTIFY (exchange truth)

### 1a. Dup/multi-buys since 00:00 ET

**119 tickers** bought past the 5-share standard lot (or >5 held) since 00:00 ET. Over the full 48h tape: **163 tickers, 902.82 surplus shares, $413.18 committed** that a position-guard would have refused (per-ticker replay in `.claude/proof_20260707/`). Full per-ticker fills with order-ids: `/root/forensic_analysis2_20260707.json` → `dup`.

**VANBOO (the known 2:34am case) — raw chain (log ET / fills UTC):**
```
BUY 2026-07-07T03:01:48Z px=62 qty=5 oid=5db4fe9e   (23:01 ET, normal entry; window boot@19:26)
[02:06:59 AM] ORDER_PLACED buy 63x5 oid=469b534a  via SIBLING_REPOST_PLACED   (boot 02:07 reconcile)
[02:20:04 AM] ORDER_CANCELLED oid=469b534a label=match_live_cancel            (match went LIVE)
[02:34:19 AM] ORDER_PLACED buy 63x5 oid=159fb665  via SIBLING_REPOST_PLACED   (boot 02:34 reconcile — fresh
                                                    _events_live latch, fresh _sibling_repost_done, blind ord_map)
BUY 2026-07-07T06:41:35Z px=63 qty=5 oid=4b829ea2   (02:41 ET — UNTRACKED prior-boot orphan, no log lifecycle)
BUY 2026-07-07T06:41:35Z px=63 qty=5 oid=159fb665   (02:41 ET — same tick)
```
→ 15 bought on a leg whose lot is 5, on a match already in play, minutes after the 02:34 restart.

**ZHAISH-ZHA — three 5-lots swept in ONE tick (06:17:04Z = 02:17 ET):** oids `0b6ea350`, `4116439d`, `d4f1b5f1` — three boots' completion bids stacked in the book; the process only knew about one (`4116439d`, placed 02:07:00). It booked 5, posted a 5-share exit. (Reconcile later consolidated this one: `reconcile_consolidate` cancel + 15@84 repost, 02:33:58 — the consolidation path CAN do it, when it can see.)

**GOMDAL-DAL:** 4 buy orders filled (1×5@71 04:13 ET booked via adoption; 3×5@69 04:45 ET same tick — no `ORDER_PLACED` lifecycle in the current boot's log for the three; prior-boot orphans).

**Conception windows:** overnight boots at **01:07:21, 02:07:01, 02:34:20 ET** (`STARTUP_VALIDATION` lines 1036311/1065291/1072776 of `/tmp/live_v4.log`) — the ex-self deploy-refire restarts. Every boot ran a blind reconcile and conceived a fresh completion-bid layer on top of the orphans it couldn't see. The current process (PID 388331) is the 02:34 boot. Dup buys continued all morning (MARDEV second 5-lot at 09:11 ET).

### 1b. Exit coverage audit (whole live book, positions API = referee)

**88 open positions; 28 naked legs; 104.49 naked shares; $39.58 at bid.** Full table in `/root/forensic_analysis2_20260707.json` → `coverage`. Named exhibits:

| ticker | held | resting sell | naked | band px |
|---|---|---|---|---|
| KXITFWMATCH-26JUL07SIMROU-**SIM** (in play) | 10 | 5 | **5** | 40 |
| KXITFWMATCH-26JUL07SIMROU-**ROU** (sibling) | 5 | 5 | 0 | 79 |
| KXITFMATCH-26JUL07ECHADD-**ADD** | 15 | 5 | **10** | — |
| KXITFWMATCH-26JUL07KHRYOU-YOU | 10 | 5 | 5 | — |
| KXITFWMATCH-26JUL07LEKVLA-VLA | 10 | 5 | 5 | — |

(27 more in the JSON; several are fractional-share residues 0.24–5.68 from partial exits — same defect class, exits sized to the tracked order, not the position.)

### 1c. Attribution — the mechanism, with cited lines

Four defects compounding; raw order-id lifecycles above.

1. **Reconcile reads only page 1 of exchange truth** — `live_v4.py:8581` (positions) and `:8598` (orders) fetch WITHOUT cursor pagination. Kalshi pages at 100; the book carried **277 resting orders** this morning (empirically: default call returns exactly 100 + `cursor`). Every reconcile guard — `sibling_position` (:4022), `sibling_bid_alive` (:4024), link/consolidation — evaluated a snapshot blind to ~2/3 of the book.
2. **Each boot re-conceives what it can't see** — `_repost_missing_siblings` (:3991) keys its once-per-event guard on the in-memory, per-session `_sibling_repost_done` (:4005) and the per-session `_events_live` latch (:4017). Three restarts = three fresh sessions = up to three stacked completion bids per event, none canceling its predecessors (placement-side-only by design, :4032).
3. **The buy guard was scoped to bot memory, fills-not-positions** — `place_order` guard (:3074-3090, pre-fix) counted `self.positions[tk].entry_qty` (booked fills of the tracked order, phase=="active") only. After a restart the LINK path never re-materializes filled legs (F39), so `current_qty = 0`; resting buy orders were never counted at all. **This is why `buy_blocked_position_full` logged 0 occurrences all night: the guard consulted a memory that was structurally empty at exactly the moments the dups were conceived.** Same story for the C-DUP-GUARD skip counter — it reads the truncated `ord_map` and the empty boot memory.
4. **Exits size to the tracked order, clamp only downward** — `_v4_apply_exit`: `open_qty = filled - pos.exit_filled_qty` (:5450, order-scoped: one lot) then `open_qty = min(open_qty, ex_open)` (pre-fix :5459 — prevents overselling, never sizes UP). The LINK path (:8669-8674) bumps `entry_qty` to exchange qty but never resizes the resting exit. **Answer to the amendment's question: the 5-lot sell is not a literal hardcoded constant — `sizing.exit_contracts=5` exists (:1295) but `_v4_apply_exit` doesn't read it; the effective 5 is the tracked order's own fill count. Functionally identical to a standard-lot assumption, and the fix replaces it with position-qty sizing permanently.**

**Ex-self re-fire (the 1c suspect question): the code landed, the feature never fired.** `d3aa99b0` IS an ancestor of the VPS HEAD and the running blob (PID 388331, booted 02:33:30, after the commit); `live_v4.py` contains `bid_ex_self` at 5 sites; **`grep -c bid_ex_self /tmp/live_v4.log` = 0** — the field has never been emitted by any process. The 01:07/02:07/02:34 restarts are that deploy's refire trail, and they are what conceived the dup layers.

---

## 2. CONTAIN (smallest diffs, through the gate)

All four in `live_v4.py`, one commit, one restart:

- **[C-EXIT-QTY-IS-POSITION-QTY] (fix for 1b/2a)**
  - `_v4_apply_exit`: exchange lookup now SETS `open_qty = ex_open` (position qty; strays are canceled two lines above) instead of `min()`-clamping. Ledger fallback unchanged on API miss. Band computation untouched.
  - reconcile LINK path: if exchange qty > total resting sell qty on a tracked non-hold leg → **top up the gap at the resting exit's own price** (`reconcile_exit_topup` log event). No cancels, no new levels — the existing exit keeps its queue position.
- **[C-BUY-POSITION-GUARD] (fix for 2b)** — `place_order` buy branch now checks exchange truth: per-ticker positions API + per-ticker resting orders API; `committed = max(memory_qty, exchange_held) + open_resting_buys`; `committed >= 5` → refuse (`buy_blocked_position_full` with `source: exchange_truth`); partial headroom → reduce. **Fail-closed**: API miss → refuse the buy (`buy_guard_api_fail`), retry next tick.
- **[C-RECONCILE-PAGINATION] (root cause)** — both reconcile fetches walk the cursor to exhaustion. The guards of defect #2 (`sibling_position`, `sibling_bid_alive`) now see the whole book, which is what makes them enforceable at all.

**Explicitly NOT touched:** exit band levels/cells/hold rules (Vault 0A), aim tables, config values, any entry-policy surface.

## 3. BACKFILL (2a amendment: FULL OPEN-BOOK RECONCILE)

Executed by the deployed code's own boot reconcile (positions API = referee, now paginated): untracked legs with resting sells → existing `qty_gap_consolidated` path at the same band px; tracked legs → new same-band top-up; legs with no exit at all → existing auto-post path at the standing band per deployed config (hold-rule legs stay exitless BY CONFIG and are listed as such). Before/after table appended below after the restart (§4).

## 4. VERIFICATION (key-presence; appended post-deploy 10:35 ET)

**Deploy: GATE PASS → booted `910dd13` (code `ccf8fa8f`), PID 617743, 10:21:10 ET, ONE restart, 0 error-events post-boot.** Smoke: 551 order_placed / 76 exits / 265,033 dog-leg book states. Outcome proof accepted (`no code delta to HEAD`).

### (a) Surplus exits — raw

Boot reconcile (paginated) consolidated the book itself, 10:21:38–10:23:59 ET:
```
[10:21:48 AM] RECONCILE_EXIT_POSTED KXITFMATCH-26JUL07ECHADD-ADD {"reason": "qty_gap_consolidated", "exit_price": 64, "position_qty": 15, ...}
[10:21:48 AM] RECONCILE_EXIT_POSTED KXATPCHALLENGERMATCH-26JUL06BARZIN-BAR {"reason": "qty_gap_consolidated", "exit_price": 66, "position_qty": 10, "order_id": "332c9be4-..."}
[10:23:59 AM] RECONCILE_EXIT_TOPUP KXITFWMATCH-26JUL07BUEXAV-XAV {"exit_price": 86, "qty": 4, "position_qty": 5, "resting_sell_qty": 1, "order_id": "3d9ef409-..."}  <- NEW link-path top-up, first live fire
```
Stragglers posted directly (`/root/backfill_post_20260707.py`, scp'd, band prices preserved):
```
KXITFWMATCH-26JUL07SIMROU-SIM held=5 resting=0 gap=5 band=40
  POST 5@40 -> HTTP 201 {"average_fill_price":"0.6300","fill_count":"5.00","order_id":"2fb7e18b-6970-41c4-9fa8-dcb2e80a2d45",...}   <- band-40 exit FILLED at 63 (+23c over band)
KXITFMATCH-26JUL07URSPOU-POU  POST 0.68@63 -> HTTP 201 resting (826993fe)
KXATPCHALLENGERMATCH-26JUL07HERAMB-AMB POST 0.48@98 -> HTTP 201 resting (fe32426d)
KXITFWMATCH-26JUL07GIADIA-DIA POST 0.46@65 -> HTTP 201 resting (018ed242)
KXITFWMATCH-26JUL07MELROD-ROD POST 0.20@26 -> HTTP 201 resting (5e5e8364)
```
Named exhibits, final exchange state: SIMROU-**SIM 0 naked** (surplus realized 63 vs band 40); SIMROU-**ROU 5 held / 5-lot @79 resting** (`de6c0036`); ECHADD/KHRYOU/LEKVLA settled or fully exited (held 0).

**Before/after: 104.49 naked shares / 28 legs → 0.87 / 1** (`/root/after_audit_final_20260707.md` has the full ticker|held|before|after|band table). The residual = WALVAL-WAL 0.87 fractional shares (bid 1c): ghost adoption qty=0, no standing band on record, and the bot's int-floor arithmetic cannot see sub-1 fractions — flagged, ~$0.01 exposure. (RODAND/BROGAR appeared naked in one snapshot: they were fills 1s old; exits posted at 10:29:59/10:29:58 — pipeline racing the audit, not gaps.)

### (b) Would-be dup buy blocked — raw (jsonl, full event)

```
{"ts": "2026-07-07 10:25:31 AM ET", "event": "buy_blocked_position_full", "ticker": "KXITFWMATCH-26JUL07MALKOM-KOM",
 "details": {"current_qty": 9, "exchange_qty": 0, "open_buy_qty": 0, "committed": 9, "target_max": 5,
             "attempted_count": 5, "price": 6, "source": "exchange_truth"}}
```
A 6th-share-onward buy on the 9-held MALKOM leg, refused at the chokepoint. Upstream, the paginated sibling sweep now also SEES the book: first boot pass logged `sibling_bid_alive: 11` skips (11 would-be re-conceptions prevented before reaching the chokepoint at all).

### (c) Ex-self re-fire

**NO — it never landed as behavior.** `d3aa99b0` is an ancestor of the running blob (booted 02:33:30, after the commit; `bid_ex_self` present at 5 code sites) but `grep -c bid_ex_self /tmp/live_v4.log` = **0** across all processes ever. The deploy re-fire produced a process, not the feature. Its restarts (01:07/02:07/02:34 ET) are what layered the dup bids.

### Follow-ups (flagged, NOT in this diff)

1. **post-only-cross exit hole**: an exit whose band is at/below the bid 400-rejects (`"details":"post only cross"` — GUEDON-DON 10:23:53, ECHADD first attempt) and the leg stays naked until the next reconcile. In-the-money exits should be allowed to take. Needs its own gated change.
2. **int-floor fractional blindness**: `ex_open = sum(int(float(position_fp)))` and `str(int(count))` in the order payload floor fractional shares; sub-1 residues are invisible to sizing (WALVAL 0.87). Kalshi accepts fractional counts (proven by the four 201s above).
3. **exchange_qty=0 on the MALKOM block** while memory said 9 — memory caught it (max() of both is the design), but the per-ticker positions read deserves a look (settled-filter timing).
4. VPS `origin` URL still leaks a GitHub PAT (standing item, unrelated).
