# VANISHED-EXIT LIFECYCLE TRACE — 2026-07-20 (the owed trace; read-only, exchange-truth)

**Prior art (C45):** founded in the P0 naked sweep entry (truth/OPEN_LEDGER.md IN-MOTION top, commits fff3ba51 + a401fa56): GNI/HAN exits "posted 09:09–09:13, gone from the exchange by 09:39 — cause unnamed"; candidates listed were drain-cancel, post-boot cancel cycle, exchange-side rejection after ack. This trace answers with the Kalshi order lifecycle (GET /portfolio/orders/{id} + fills + per-ticker order history) joined to the engine log. Delta vs prior art: the class as founded **dissolves — no exit ever vanished**. Two known mechanisms + one NEW defect class named below.

All exchange times UTC (13:xx Z = 09:xx ET). Engine log = logs/live_v3_20260720.jsonl. Boot of record: 09:01:15 post_boot_audit context=boot (PASS, 5 pos / 80 resting). No boot occurred near 09:22 — the morning's third boot was 09:01:15; everything below happened inside ONE running process.

## HAN (KXITFWMATCH-26JUL20BRUHAN-HAN) — determination-cancel, lawful, not ours

- 09:07:47 entry placed (cfddc5d0…) → executed 09:09:09, 5sh @19.
- 09:09:42 exit posted @24 (c5e0a3c5…, engine v4_exit_posted 09:09:45).
- **Exchange order status: `canceled`, last_update 13:37:03Z = 09:37:03 ET** — ~66s before the settlement stamp (ws_lifecycle settled_ts 1784554689 ≈ 09:38:09 ET). No engine cancel line exists; nothing in-process touched it.
- **Verdict: Kalshi's own market-determination cancel** — match ended, the exchange pulled the resting sell, position rode to settlement LOSS (−95¢, lawful; the operator's sweep at ~09:40 saw the one-minute post-determination gap and correctly could not repost). Class instance DISSOLVED.

## GNI (KXITFWMATCH-26JUL20SKOGNI-GNI) — two positions, one unbooked fill; the real defect

**Cycle 1 (clean):** entry d410f8e9 placed 09:09:31 → cancel raced its own fill (cancel_fill_race 09:13:07) → booked 5sh @11. `itm_exit_taken` @14 posted 09:13:08 (cc22362e) — **executed AT CREATION as a taker (fill 13:13:08.495Z, is_taker=true)**: the ITM-exit-take is deliberately marketable; nothing vanished. Engine booked it 09:15:40 (checker lag only), trade T-20260720-0074 complete, +15¢ gross.

**Cycle 2 (the naked window):** 09:22:31 `sibling_repost_placed` — a **5¢ bid** (pair97_bound vs SKO leg-1 basis 92; goal_level 5), order ce5f9c76, trade T-20260720-0078, tracked as entry_resting by the live process. **Executed 13:28:41Z = 09:28:41 ET (maker, 5sh @5). The engine never booked the fill** — no entry_filled, no exit; check_fills ran the whole time (steady audits 09:22:34 / 09:41:59 PASS). Naked from 09:28:41.
- 09:39:31 the operator-sweep's restored exit (`p0naked2-GNI-1784554771`) — **executed 09:39:54 ET @14**. This is the "restored exit FILLED" of the 10:05 amendment; exchange-truth basis of those shares was 5¢ (cycle-2), not 11¢ (cycle-1) — the amendment conflated the two cycles; actual cycle-2 realized ≈ +45¢ (5sh, 5→14), not +15¢.
- **10:21:40 the engine, still blind, cancels ce5f9c76 as `v4_cancel_degenerate` (success=false — order was executed)** → the cancel-resolve path finally discovers the fill: `entry_cancel_partial {filled_qty: 5, kept_position: true}` — booking a 5-share position whose shares the sweep had sold 42 minutes earlier. **Last GNI engine line ever; no exit posted, no settled line.** Steady audits since (10:33→11:49) PASS with no GNI flag and state/live_v4_resting.json holds no GNI position — the phantom did not persist to disk; in-memory fate unverified (named residual).

## The named classes (feed the naked-tooth code gate; bot untouched today)

1. **UNBOOKED-FILL ON A TRACKED RESTING ORDER (new, the real defect):** a live, tracked, entry_resting order filled at 09:28:41 and check_fills booked nothing for 53 minutes — booking finally arrived via the cancel-race resolver, not the poll. Field-schema drift is EXCLUDED (raw order carries `fill_count_fp: "5.00"`; the parse handles it). Root candidate to read at the gate: per-order GET poll starvation/cadence under an 80+-order book (rate-limiter budget), or a skip branch in the entry_resting scan. The 07-19 exit_qty_mismatch tooth cannot see this; **the owed audit tooth (filled-leg-without-resting-exit, every steady cycle) would have flagged it at ~09:29 — eleven minutes before the operator's eyes did.**
2. **SWEEP×ENGINE DOUBLE-OWNERSHIP:** the out-of-band restored exit sold shares the engine later self-booked (10:21:40 kept_position on already-sold shares). Any out-of-band remediation order needs an engine-visible stamp (audit-exempt/adoption path), or the next unbooked fill turns containment into a phantom position.
3. **HAN's lesson (no defect):** exchange determination-cancel of resting exits ~1min before settlement visibility is normal; a naked-sweep running in that gap will see "exit gone" on a determined market. The naked-tooth should treat markets inside the determination window as settlement_pending, not naked.

**Ledger correction owed with the next C50:** amendment's "GNI +3/sh over engine basis 11" → exchange truth is cycle-1 +15¢ (11→14 taker) AND cycle-2 +45¢ (5→14 via the sweep's exit); JAG/HAN unchanged.
