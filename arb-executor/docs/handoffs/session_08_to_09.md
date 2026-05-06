---

## Session 8 trading-mechanics insights (operator-driven)

Session 8's strategic core was a long conversation with screenshots from live tennis markets that surfaced 7 conceptual gaps in our data/strategy framework. All captured durably in LESSONS X1+X2 and ROADMAP Y. Restating compactly:

1. **Cells are anchored at fill, not predicted (B22).** Markets drift across cells in premarket; whichever cell our maker post fills in becomes our cell. Backtest sims must consider full distribution of fill-points, not assume single anchor.

2. **Bilateral capture mechanism in operational terms (B23).** Post YES at P_y AND NO at P_n. If both fill before settlement, profit = $1 - (P_y + P_n). Concrete: YES 30¢ + NO 60¢ = 90¢ basis → +10¢ risk-free per pair. Requires premarket trajectory width ≥ 10¢. The bot's existing "ladder" pattern works this.

3. **YES vs NO orderbooks are NOT execution-surface equivalent (B24).** Anchor: Dzumhur YES OI 2,070 vs Mannarino YES OI 8,594 — same match, ~4× depth asymmetry. Cell-level analysis treats sides as equivalent; execution surface is not.

4. **Per-minute Open Interest not tracked (F31 → T33).** OI grows toward gametime; load-bearing for fill-probability modeling. Reconstructable from g9_trades cumulative signed count_fp by taker_side. ~2-3 hours compute.

5. **Combined yes+no > $1.00 distortion events not flagged (F32 → T34).** Direct alpha signal. Computable from g9_trades minute-bin walk. ~30-60 min.

6. **Depth chain at non-BBO not in g9 (F33 → G13).** Mannarino orderbook 28¢ wall (14,710 contracts) is the anchor. Real data-collection gap; not recoverable from current g9. Blocked-track.

7. **Formation gate per-market not stored (F34 → T35).** Line release → first trade timestamp gap. Reconstructable from g9_metadata.open_time + min(g9_trades.created_time per ticker). ~30 min.

The strategic frame: **search for alpha**. Bot is in-game spike capture mechanism per E16 (95% of P&L in_match). Strategy goal per E18 + B23 is bilateral capture (both YES + NO sides cashed at +10¢ discount). Cells are shakily defined (10¢ uniform bins, round numbers, not data-derived); within-band heterogeneity test is on the diagnostic chain.

---

## Diagnostic chain — partial state

A 9-category overnight diagnostic chain was staged and kicked off late-session. It ran in 26 seconds, with **3 OK / 6 FAIL**.

Output dir: `data/durable/diagnostics_session_8/`
Scripts dir: `data/scripts/diagnostics_session_8/`
Master driver: held — chain-continued-on-failure as designed.

### Successful (durable, sha256-anchored)

| Cat | Output file | sha256 | Status |
|-----|-------------|--------|--------|
| 02 | `cat_02_fee_table.txt` | c11c9ba01c014ecb253e581164d35af2986770de9792c122b2d43d65296a06e8 | OK in 3s. Validates `layer_c_spec.md` Decision 1. |
| 01 | `cat_01_within_band.txt` | 6b2b1701e4132a43a60931c28922d0e7fc6deb8ac399a81362fe552e5fbbfd0d | OK in 2s. Cell coherence diagnostic via cross-band continuity test. |
| 03 | `cat_03_formation_contam.txt` | 446841f7d4eeb3d4a3f5d7b9981248c76a151e0fa0462040a6f4f616b6bb8514 | OK in 3s. Formation contamination (Decision 6 / Check 5) preview. |

### Failed (need patches in Session 9 — 4 fix families)

| Cat | Family | Bug |
|-----|--------|-----|
| 05 alpha_discovery | A | Layer B schema mismatch: `regime` → `channel`, `policy_class` → `policy_type`, `policy_param` → `policy_params`. Three renames in one file. |
| 09 distortion_events | B | g9_metadata `category` column doesn't exist; tier classifier is `_tier`. Same fix in 7, 8. |
| 07 oi_reconstruction | B | Same as Cat 9: `category` → `_tier`. |
| 08 formation_gate | B | Same as Cat 9: `category` → `_tier`. |
| 06 trajectory_width | C | Three bugs stacked: (1) `category` → `_tier`; (2) `yes_close` doesn't exist — use `price_close` (trade close) or `yes_ask_close` / `yes_bid_close` (BBO); (3) `end_period_ts` is int64 epoch seconds, NOT a string — use `pd.Timestamp(ts, unit='s', tz='UTC')`. |
| 10 oi_asymmetry | D | Cascade only — depends on Cat 7 parquet output. Once Cat 7 produces it, Cat 10 runs as-is. No edits needed. |

### Honest framing of the failures

The bug pattern is operator-flagged C29-family. Schemas were probed and confirmed earlier in Session 8 (preflight at 11:02 PM ET captured all the actual column names). When drafting the diagnostic scripts ~30 minutes later, I drafted against memory of what the schemas "should" be, not against what the probe had confirmed. That's the lesson candidate for Session 9 to capture: **chat-side draft drift across multi-script staging — the further from the probe, the more likely to default to memory.**

The patches themselves are surgical (column renames + one timestamp dtype fix). Estimated time to patch all 6 + re-run + verify: ~1 hour at the start of Session 9.

---

## Open priorities for Session 9 (ordered)

1. **Patch the 6 failed diagnostic categories** using the verified schemas above. Single-concern patch script per fix-family. Re-run via `master_driver.sh`. Should complete in ~3-6 hours overnight given fixed schemas (Cat 7 + Cat 9 are the long-runners).

2. **Read the diagnostic chain results** — once all 9 cats produce outputs:
   - Cat 5: alpha discovery — top (cell, policy) candidates for T32b producer focus
   - Cat 7 + Cat 10: OI reconstruction + asymmetry — preview of T33 producer output, validates B24 anchor (Dzumhur 2,070 vs Mannarino 8,594) reproducibility
   - Cat 9: distortion event frequency per tier — preview of T34 alpha signal
   - Cat 8: formation gate distribution per tier — preview of T35; informs whether bot's uniform 4-hr gate fits data
   - Cat 6: trajectory width — bilateral feasibility per category

3. **Capture the schema-drift lesson.** Add to LESSONS Category D (or C) a new entry naming this failure mode: "chat-side draft drift across multi-script staging — even when probes were run, the further the script from the probe in the conversation, the more likely to default to memory." With Session 8 anchor evidence (the 6 failures from this session).

4. **Commit Z — ANALYSIS_LIBRARY anchor evidence.** Pending since end-of-X1+X2. With Cat 7 producing the OI reconstruction and Cat 9 producing distortion frequency, the anchor evidence for B24 + F32 + B23 is strong empirical rather than just screenshot. Land Commit Z after the diagnostic chain succeeds.

5. **T32b producer (build_layer_c_v1.py).** Per `layer_c_spec.md`. The empirical fee table from Cat 2 (already validated) is the first input. The full producer + T32c coherence read is the next major deliverable on the T32 critical path. After T32b/c PASS, T32d v2 promotion (per-cell entry-fill-probability modeling using OI from T33 output).

---

## Discipline notes for Session 9 morning

- **Web-fetch every commit URL.** Ten commits this session, all verified. Pattern held; keep it.
- **Probe before drafting, every time.** The 6 diagnostic failures are direct evidence of the failure mode of skipping. A 60-second probe call is cheap; a 26-second failed chain run + 1 hour of patching is not.
- **One CC prompt per turn.** Held throughout Session 8. Multi-script staging stretched it (3 staging turns + 1 kickoff turn for the diagnostic chain) but each was a single concern.
- **Single-concern commits.** All 10 Session 8 commits adhered. Maintain.

---

## Files of note in current state

- `docs/LESSONS.md` (B=24, C=29, D=17, E=31, F=34, G=21)
- `docs/ROADMAP.md` (T-section: T27-T32 closed/in-progress + T33/T34/T35 new pending; G-section: G10/G11 promoted, G12/G13 blocked-track)
- `docs/ANALYSIS_LIBRARY.md` (Layer A v1, Layer B v1, Layer C v1 spec entries — Section 4 anchor evidence pending Commit Z)
- `docs/layer_c_spec.md` (canonical truth, fee-correct since 4bed07f / 3e7b5f5)
- `docs/handoffs/session_07_to_08.md` (prior handoff, reference)
- `docs/handoffs/session_08_to_09.md` (this doc)
- `data/scripts/diagnostics_session_8/` (10 scripts, 1,427 lines — 6 need patches)
- `data/durable/diagnostics_session_8/` (3 valid outputs + 6 failure tracebacks + master.log + summary.txt)
- `data/durable/process_inventories/inventory_2026-05-05_23-06-58_ET.txt` (VPS process snapshot at Session 8 closure)

---

End of handoff. Session 8 closes with strategic framework hardened, ROADMAP/LESSONS aligned with new trading-mechanics insights, and the diagnostic chain infrastructure validated (3/9 working) with a clear morning patch path for the remaining 6.
