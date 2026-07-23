# Window-1 Independent Gap-Closure (CC) — continues ff0f336f

Read-only, on `audit/window1-independent` only. No production/config/order/live changes,
no Kalshi contact, no scoring/tuning. Raw identities/credentials stay out of Git; Spaces
queried read-only (creds from `.env`, never printed). The retracted 4.9–17% figure is not
reused as a ceiling.

## Part 1 — Print-gap classification (39 legs without normalized prints)

Method per leg: trades-object existence, ticks `last_trade` variation, private fills,
sibling-leg trades, and the demonstrated lossiness of the trades archive.

**Decisive proof the trades archive is lossy:** 4 of the 39 legs carry **private fills**
(the bot's own executions = real trades) yet have **no trades object** in Spaces. A missing
trades object therefore cannot prove "zero-trade" for any leg.

| Class | Count | Basis |
|---|---:|---|
| missing-ingestion (PROVEN) | **4** | private fill present ⇒ a trade occurred ⇒ archive gap |
| proven zero-trade | **0** | none have all-zero `last_trade`; and the archive is provably lossy |
| unresolved / CENSORED | **35** | `last_trade` nonzero (31/39) but carryover-ambiguous; missing object ≠ zero volume |

All 39 have a ticks CSV. `last_trade` distinct-nonzero=1 uniformly (even on 276k-row markets)
⇒ it is a carryover value, not per-trade evidence, so it is **not** used to claim trades.
Recovery path for the 35: the **ws_depth archive contains `trade` messages** (1,222 in a single
sampled hour) — the authoritative tape that can reclassify these individually. Not reinterpreted
as zero volume. (Leg list: `PRINT_GAP_LEDGER.tsv`.)

## Part 2 — Real-start ledger (honest status: mostly CENSORED)

I could **not** independently reconstruct reliable real starts for all 804 from ingested/log
signals, and I will not ship a misleading ledger:
- The bot's **detector is invalid as a real-start source.** `window_open_set` is a pre-start
  entry-window signal (misaligned with schedule by hours in extraction), and `gun_fired` is
  demonstrably unreliable — in the MICMAY forensic it latched at the **false 22:00 ET schedule,
  ~3h after the real ~19:00 ET start.**
- Valid real-start sources **exist but need extraction not completed at 804-scale:**
  `observed_starts.first_inplay_at` (provider observed — only 14 in-window, ends Jul 14);
  `live_scores` score onset (417 in-window, leg-code-keyed → needs mapping);
  **`market_lifecycle_v2` transitions in the ws_depth archive** (exchange lifecycle, precedence #3);
  and tape-regime reconstruction from recovered ticks (premarket excluded, precedence #4).

**Quantified:** the benchmark established a verified start for only **40/804**; independent
real start is confirmable today for a **minority** (14 provider + partial score), so the
remaining games are **CENSORED** for real-start truth pending ws_depth-lifecycle / score-onset
extraction. The gap is closeable from recovered data but is not a trivial ingest.

## Part 3 — Mayo/Michelsen forensic (COMPLETE) — see `MAYO_MICHELSEN_FORENSIC.md`

Lifecycle recovered from byte-pinned logs (order/client IDs sanitized there):
- **Real match start ≈ 2026-07-21 19:00 ET** (P0-established; the fill at 19:37 ET confirms in-play).
- **Mayo (MICMAY-MAY) placement:** 2026-07-21 **19:36:19 ET** (23:36:19Z), resting.
- **Michelsen sibling (MICMAY-MIC) placement:** **19:36:21 ET** (23:36:21Z), resting.
- **Mayo FILL:** **19:37:30 ET** (23:37:30Z), 5 @ 85¢ — **~37 min AFTER real start** (post-start fill).
- **Sibling cancellation:** **22:01:12 ET** (Jul-22 02:01:12Z) `gun_fire_sweep` → then `match_live_cancel` success=false (already gone) — i.e., swept at the **false 22:00 schedule**, ~3h after real start.
- **Schedule value the bot used:** **22:00 ET** (from `expected_expiration_time` — the false late schedule).
- **Detector latch:** gun fired ~**22:01 ET**, ~3h late, because `phantom_bell_void` suppressed the real bell.
- **Survived/filled after real start:** **YES** — Mayo filled 37 min post-start; a Mayo re-post rested until `settlement_cleanup` (Jul-22 18:54Z).
- **Responsible source/code path:** `event_kalshi_occ` derived from `expected_expiration_time` + `phantom_bell_void` suppressing the real bell → the start-gate used the false 22:00 schedule, permitting post-real-start entry. This is exactly the P0 real-start-entry-guard defect (fix candidate `a4996dd0`: `event_kalshi_occ` from `occurrence_datetime` only, strong-evidence override, entry-start-gate). **Evidence only — no live fix applied.**

## Part 4 — Depth integrity (Jul 12–20)

From a downloaded ws_depth hour object (`ws_20260720_18`, 31 MB, 84,150 msgs):
- **Types:** `orderbook_delta` 80,192, `market_lifecycle_v2` 2,260, **`trade` 1,222**, **`orderbook_snapshot` 444**, `ok`/`subscribed`.
- **Five-level snapshots vs full depth:** the `ticks/` CSVs are **top-5 snapshots (bounded depth)** — directly usable for BBO / 5-level imbalance / executable-5-depth / depletion. The `ws_depth/` stream is **full-book deltas WITH snapshot ancestors present (444/hr)** — so full depth is **reconstructable in principle**; `seq` is carried per message. **Per the rule, I do NOT call the delta stream "full depth" yet** — gapless seq-continuity after each snapshot is **not yet validated** (my sample tracked the wrong seq field). Full-depth microstructure (pressure/persistence/add-cancel/replenishment) is causally measurable **only after** snapshot-anchored gapless reconstruction is proven; five-level pressure is measurable now from ticks.
- ws_depth also carries the authoritative **tape** (feeds Part 1 recovery) and **exchange lifecycle** (feeds Part 2 real start).

## Net
- Print gap: **4 proven ingestion, 0 zero-trade, 35 censored** — never called zero volume.
- Real start: reliably reconstructable for a minority today; bulk **CENSORED**; bot detector proven invalid (Mayo).
- Mayo/Michelsen: fully reconstructed — a **post-real-start fill** caused by schedule substitution + phantom-bell suppression.
- Depth: five-level snapshots usable now; full-depth reconstruction feasible (snapshots exist) but **not yet proven** — not asserted.
