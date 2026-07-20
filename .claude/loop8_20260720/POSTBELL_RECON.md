# POST-BELL FILL RECONCILIATION — morning blind windows, 2026-07-20 (~12:40 PM ET; read-only, no orders placed)

**Prior art (C45):** owed thread from the P0 naked-sweep entry (truth/OPEN_LEDGER.md IN-MOTION; commits fff3ba51/a401fa56/7aadbcdc — the morning arc: log-gzip defect → three gate boots → boot of record 09:01:15). Instrument: exchange fills (paged /portfolio/fills, all 78 fills ≥ 00:00 ET today) joined against today's engine log bookings + `schedule_match` clocks. Delta vs prior art: the owed reconciliation delivered; verdict below.

## Verdict: CLEAN — zero unreconciled blind-window fills, zero true W2 fills, zero naked legs at close of check

| class | n | disposition |
|---|---|---|
| BOOKED (W1) | 48 | normal path |
| Pre-boot orphans, 04:17–08:36 ET | 26 | the known blind-window class (engine down / gzip era) — all ITF, all contained by the 09:01:15 boot's 44-order fingerprint re-adoption + the operator-eyes P0 sweep; buys carry matching same-morning sells on the tape (MARBIT, GIUHER, PETTAB, VALGOM, POLBRU, VASSIN, MARROS, MONNES, PALLEO…) |
| POST-SCHED buy (OLISCH-SCH 11:53:29) | 1 | **NOT a W2 fill** — the engine's own `clock_liar` line (12:30:46) shows kalshi_start 7:00 AM today vs te_honest start 10:00 AM TOMORROW (07-21); the fill is T−21h by the honest clock. Sched-clock error class, instance on the record |
| Fresh fills, booking-lag | 2 | KOZPAS-PAS 12:24:47 (5sh @30) + WINARS-ARS 12:27:04 (5sh @18): unbooked at check time (~12:30) → **engine self-healed by 12:39** — ARS booked AND its exit filled +25¢ (18→23, in-play, fallback_bell source); PAS booked (completion_shadow basis 30) with its band-7 exit resting @37. Lag ≈ 12–15 min — a mild instance of the UNBOOKED-FILL class (GNI's 53-min case stays the outlier); feeds the same naked-tooth gate |

## Containment discipline receipt (for the record)
A `p0naked3` exit-restore was staged for PAS/ARS when both read naked at ~12:30. The **pre-act re-verify guard** (position + resting-sell recount immediately before posting) found PAS already covered and ARS already flat — **no orders were placed**. Honest instrument note: my read of `atp_chall_adaptive_exit_bands.parquet` (band_exit_X 66/72 → exits 96/90) DISAGREES with the engine's live band answer (PAS band 7 → exit 37) — the parquet column is not entry+offset as assumed; any future out-of-band restore must take the band answer from the engine's own emitted lines (completion_shadow/v4_exit_posted), never a raw parquet read. Filed as a containment-protocol note.

## Feeds forward
- The naked-tooth code gate (owed) now carries three instance shapes: GNI 53-min (outlier), PAS/ARS 12–15-min (cadence-normal), determination-window false-naked (HAN).
- `clock_liar` OLISCH = fresh evidence for the corpus indictment's session-clock class; no action, already the engine's own read.
