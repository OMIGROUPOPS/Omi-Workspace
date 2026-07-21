# OUTCOME PROOF — THE RE-BUY-AFTER-CASH DEFECT (live, operator's catch)
Candidate: this push. C46 two-lane. **Urgent live-money fix.**

## THE DEFECT, from the box (ICHYAM-YAM, 2026-07-20)
- 09:12–09:34 PM: leg accumulates 5 shares @51 basis; exits posted @64.
- The exits **FILL** — the leg CASHES (the operator's "selling live at
  exits"). `check_fills` has not booked it (per-order poll starvation,
  the named unbooked-fill root).
- 10:18:48 / 10:29:19 PM: **my phantom tooth** (shipped hours earlier)
  reads engine-holds-5 vs exchange-holds-0 on a live market and, at 2
  consecutive cycles, **DROPS the engine's position record**.
- 10:29:26 PM: with the record — and with it the cycle count and the
  tombstone — erased, the router re-conceives the leg as fresh:
  `entry_dossier placed:path_aim` → **buy 5@37 (10:29:31), re-priced
  5@45 (10:29:38)** → fills 5@48 (10:33:23), new exit @59.
  **A re-buy on a leg that had just cashed, at a worse basis.**
- Same window: `naked_leg_defect` + `unbooked_fill_defect` fire on the
  same leg — the tooth's own siblings naming the true class while the
  drop branch acted on the wrong one.

## THE FIX (two holes, both closed)
1. **THE DROP IS DEAD.** An engine position the exchange no longer
   holds is a cashed exit, not a phantom. The branch now routes the
   cash through `_reconcile_exit_fill_from_truth`: confirm the sell
   against exchange truth (exit order status first, fills feed second),
   then book it — pnl, `_session_exited` stamp, **cycle increment**,
   tombstone, position closed. **Without confirmation the record
   STANDS** (`phantom_cash_unconfirmed`) — state is never erased on
   exchange-empty again. Detection (flag, red, every cycle) unchanged.
2. **`reentry_cycle_cap: 2 → 1`** (operator's law: after selling at
   exits, no re-buy). Enforced at the `place_order` chokepoint
   (`cycle_cap_refused`, covers every conception path), at the router
   skip, and asserted by the book audit (`cycle_cap_breach`).

## LANE 1 — MECHANISM
Replay of tonight's own sequence under the fix: at 10:29:19 the branch
books YAM's cash (exit order executed → `exit_filled`, cycle 1→1
counted), the position closes cleanly and is tombstoned; at 10:29:26
the router's re-conception hits `cycle_cap_refused` at the chokepoint
(cycle 1 ≥ cap 1) — **the 5@37/5@45 buys are never placed, the 5@48
fill never happens.** The construction delta is exactly the defect:
one erased position record and one unlawful re-entry per occurrence.
Legs that have not cashed are untouched (guard requires exchange-empty
+ live market + 2 cycles + confirmed sell).

## LANE 2 — SETTLEMENT P&L
The instance cost is real but small-n: the re-buy filled 5@48 with an
exit resting @59 (open at write time). No P&L claim is made; the fix
is judged on Lane 1 (C46).

## Verdict
Lane 1: the defect's own replay shows both the erase and the re-buy
prevented. DEPLOY IMMEDIATELY.
