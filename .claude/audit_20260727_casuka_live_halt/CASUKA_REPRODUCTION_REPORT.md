# CASUKA LIVE-HALT — INDEPENDENT READ-ONLY REPRODUCTION

Controlling halt: `058282b99cfb4da702ad85528750232f07f2c1b4` · `.claude/audit_halt/AUDIT_HALT_20260727_133309.md` (steady_cadence, 13:33:09 ET, FAIL exit_qty_mismatch CASUKA-CAS held 5 / resting exits 8; flags FARRIU, VEGKAW).
Reproduced read-only from `/tmp/live_v4.log` on the VPS (engine PID 2241929, single boot **Sat Jul 25 00:12:01 EDT**, tmux `live_v4`). **No orders cancelled, no positions modified, no halt state touched, no code changed, T2 worktree untouched.** All times ET Jul 27; log line numbers cited.

## 1. CASUKA-CAS — exact reproduction

Entry walk (organ `v4_move_repost`, all count 5 buys): `44529e20…` @36 (13:10:47, L2493209; cancelled 13:10:48) → `19bbca8a…` @63 (13:10:49; cancelled 13:15:29) → `9415a999…` @78 (13:15:31; cancelled 13:17:28) → **`b48c5fd4-a8fa-4d19-82d0-b42cce5ed332` @87×5** (13:17:29, L2495115, resting).

Fill discovery was **reconcile-side, not engine-side**: 13:28:27 `NAKED_LEG_DEFECT` held 2.0 / resting exits 0 + `UNBOOKED_FILL_DEFECT` exchange 2 vs engine 0 on `b48c5fd4` (consecutive_cycles 1, L2497102-3) → `RECONCILE_V4_ADOPTED` 2@87 (`steady_state_reconcile`) → **exit #1 `b1833bce-47e4-471d-bd6b-568beabfdb51` SELL 98×2** (13:28:33, L2497109).

The remaining 3 of the buy filled by 13:33. Then the defect second:

- **13:33:07** `NAKED_LEG_DEFECT` held 5.0 / resting exit 2 / uncovered 3 → organ `v4_exit_reset_stray` **cancelled `b1833bce`** (success true, L2498062) and posted **exit #2 `6f99f47a-389f-472a-b734-43b27ddeb8a1` SELL 98×5** (EXIT-QTY=POSITION-QTY law, `NAKED_TOOTH_HEAL`, L2498063-65).
- **13:33:08** organ `RECONCILE_EXIT_TOPUP` posted **exit #3 `f623b057-c2d5-4a42-9b47-6037511d9779` SELL 98×3**, computed from `{"position_qty": 5, "resting_sell_qty": 2}` (L2498066-67) — a **stale resting-exit snapshot** taken before the same cycle's heal had cancelled the 2-lot and posted the 5-lot.
- **13:33:09** steady_cadence audit read held 5 / resting exits 8 → FAIL → halt commit `058282b9`.

**Root cause: engine logic — a same-cycle duplicate-post race between two exit organs (`v4_exit_reset_stray` heal and `RECONCILE_EXIT_TOPUP`) acting on one stale resting-sell snapshot.** Not exchange, not the position ledger (both reads were individually correct at their instants), not reporting (the audit correctly measured 8 vs 5). Zero API retries involved; adoption `consecutive_cycles: 1`.

**The three excess contracts live in ONE order: `f623b057…` (count 3).** The three exit-order IDs of the incident: `b1833bce…` (cancelled by heal), `6f99f47a…` (5-lot), `f623b057…` (3-lot surplus).

Aftermath (receipts): 14:27:25 `EXIT_RECEIPTS_BOOKED` per_order `6f99f47a: 5` (98¢, +55¢) — and the surplus 3-lot **also executed**, leaving exchange qty **−3** (`CASH_CLEANUP_RACED_HOLDING` / `QUARANTINE_UNKNOWN`, L2506889-90, kalshi_qty −3): the engine **oversold 3 unowned contracts** (short-yes). Quarantine held it read-only until `SETTLED WIN @100` 15:02:36 (L2511338) closed the market; the −3 settled against it (≈−6¢ on the surplus; net event P&L +55¢ booked). **14:27:13 `CONCEPTION_HALT_CLEARED` (halted_reaudit PASS, L2506880) — the halt is no longer active**; the engine has been conceiving normally since (fresh ORDER_PLACED at 21:43-44 ET).

## 2. FARRIU and VEGKAW flags — reconciled

- **FARRIU** (`FAR absent / RIU filled`): RIU's only entry was a resting bid @41 (V4_PLACE 06:35:26, L1899192) that **never filled** — every status row through settlement reads `entry=41c exit=0c entry_resting`; it `SETTLED` 10:03:27 at 50 with **pnl 0, qty 0** and `SETTLEMENT_UNEXPECTED_PHASE entry_resting` (L1961291-92). The 13:33 audit still classified RIU **"filled"** — the classifier maps `tk in self.positions` → "filled" (live_v4.py ~L14432), and a settled-while-entry-resting leg left a stale positions entry 3.5h after settlement. **Reporting/stale-state artifact; zero market exposure.**
- **VEGKAW** (`VEG filled / KAW absent`): VEG's only entry was a resting bid @48 (V4_PLACE 13:18:12, L2495310) that **never filled** (perpetual `entry_resting`, market `determined` 16:17:56). Same classifier artifact labels it "filled". KAW was "absent" at 13:33 (no priced bid, no named refusal within the cycle); its completion buy @38×5 was then itself blocked by the halt (`BUY_BLOCKED_CONCEPTION_HALT` 13:45:44, L2499585) and later wall-skipped. **Flag-only; no unpaired position ever existed** (neither leg filled).

## 3. Verdict

- CASUKA failure: **real defect, engine race** (stale-snapshot double-post), self-healed financially by fills+settlement; halt self-cleared 14:27:13.
- Secondary real defect exposed: **no sell-side clamp to exchange position** — the surplus exit executed as an oversell (−3).
- FARRIU/VEGKAW: **classifier artifact** (`positions`-membership ≠ booked fill), flag-only.
- No live mutation is required now; the repair is code-side for Cursor Codex (see EXECUTION_REPAIR_PACKET.json).
