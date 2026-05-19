# Exit-Optimized Bounce v1 Spec -- E32 Locked Exit Model, Dual Conservative-Fill Frame

**Status:** v0.1 -- initial draft 2026-05-18 ET. The Phase-2 strategy-actionable deliverable: exit-optimized realized bounce per price band under the LESSONS E32 locked cell/exit model, computed under BOTH conservative-fill entry frames with cross-frame robustness as the headline output. Layer-B-equivalent per LESSONS B16, built on the validated Layer-A descriptive surface (inmatch_bounce_surface_v1, registered 6f1d4bde).

**Every model decision in this spec is resolved -- not assumed (C38). The resolution authority for each:**
- Exit logic, ranking metric, no-stop, two-exit-windows, settlement-as-answer-key: LESSONS E32 (the locked cell/exit model, re-derived from first principles 2026-05-14).
- T-20m is a conservative FV-anchored *fill assumption* for analytical honesty, NOT a structural axiom forbidding in-match entry (operator clarification 2026-05-18: "we only did T-20 for analysis because it's a conservative period to fill bids and when it's aligned with the FV anchor for the most part"). E32(f)'s "in-match is an exit venue, never an entry venue" describes that analytical frame's fill conservatism, not an immutable model law.
- Therefore both conservative-fill frames are emitted side-by-side; the edge's survival across BOTH is the deliverable (operator decision 2026-05-18, option 3): an edge robust under both conservative frames is real; an edge surviving only one indicates the fill frame is doing the work, not the strategy -- decision-critical to know BEFORE capital deployment.
- A39 dual-metric, A38 firewall, F35 cohort, B14/G17 premarket/in-match decomposition: carried forward as locked constraints from the validated Layer-A.

**Anchored to:**
- LESSONS E32 (the locked cell/exit model -- exit logic, no-stop, two exit windows, settlement=answer-key, average-bounce-per-band ranking; the resolution authority for all exit-model decisions)
- LESSONS B16 (Layer A/B/C; this is Layer-B-equivalent, built on the validated Layer-A inmatch_bounce_surface_v1, NOT replacing it)
- LESSONS B14 / G17 (premarket vs in-match are separate cell classes; the two exit windows are decomposed, never conflated -- the legacy NEEDS-RECOMPUTATION cluster came from this conflation)
- LESSONS A38 (peak-through-settlement saturates; the exit must be a finite real exit -- E32(d) settlement-as-answer-key structurally satisfies this: settlement is the ground-truth scoring key, never the optimized objective)
- LESSONS A39 (cents AND ROI both emitted every row -- structurally mandatory; the Layer-A cents<->ROI inversion carries into the exit-optimized result)
- LESSONS C38 (probe/authority-don't-assume; every model decision here is resolved by E32 or explicit operator decision, none assumed)
- LESSONS E31 (pre-game vs in-game economic distinction -- the two fill frames are economically distinct; the comparison is the point)
- LESSONS B20 (report the curve/shape, not a reductive label -- exit-optimized bounce vs band is a curve; characterize it, no brittle classifier)
- LESSONS B22 (fill is a distribution -- within each frame the entry mark is characterized as a distribution, not a single assumed point)
- LESSONS F35 (tier-1/2 reliable cohort -- same screen as the validated Layer-A)
- per_minute_universe_spec.md Sec 2.8 (forward-label columns), Sec 7 (phase_state / regime / premarket_phase classifier), Sec 2.6 (match_start_ts signal hierarchy)
- inmatch_bounce_surface_v1_spec.md (the validated Layer-A this is built on; lineage 6f1d4bde, surface sha 14241db0)
- TAXONOMY 2.5 (GRAIN/VECTOR/OBJECTIVE), TAXONOMY line 196 (exit-optimized = the locked objective)

**Foundation pointers:**
- Bounce/tape source: `data/durable/per_minute_universe/per_minute_features.parquet` (FOUNDATION-TIER, sha256 9fde4b5d, T37 ckpt-3) -- read fresh; supplies both the T-20m premarket mark AND the in-match entry minutes AND the full forward tape (premarket + in-match exit windows) AND the settlement answer key.
- Cohort screen: `data/durable/n_profile_v1/n_profile.parquet` (sha256 a7ed1155, lineage c76eee5 / MANIFEST c9a0f3e) -- F35-reliable tier-1/2 live-era, the same validated screen as Layer-A.
- Descriptive reference (interpreted against, NOT queried as the entry source): `data/durable/inmatch_bounce_surface_v1/surface.parquet` (sha256 14241db0, lineage 6f1d4bde) -- the validated Layer-A the in-match frame's result is interpreted in light of (B16 staging: "built on" = interpreted against a validated layer, not literally querying its aggregated rows; spec Sec 6 of the Layer-A spec said "vectorized query over v1" before probe evidence showed v1's surface is in-match-entry -- that sentence is superseded here by the B16 *intent*, recorded honestly per the G23/4f55339 discipline).

**Output:** `data/durable/exit_optimized_bounce_v1/` (parquet + meta.json + validation_report.md)

**GRAIN / VECTOR / OBJECTIVE (TAXONOMY 2.5):** Grain = per-(price-band x fill-frame x exit-window-resolution) aggregate. Vector = vector-agnostic. Objective = **exit-optimized** (the locked objective, TAXONOMY 196 -- realized bounce from fill to optimized exit, no stop, two exit windows).

---

## 1. Scope

### 1.1 In scope

v1 produces **exit-optimized realized bounce per price band**, under the E32 locked exit model, computed under BOTH conservative-fill entry frames:

- **Frame P (premarket-T-20m):** entry mark = the N's price at the T-20m premarket mark (the minute where `time_to_match_start_min` ~ +20, the conservative FV-anchored fill mark per the original analysis rationale). Forward tape = premarket exit window (T-20m -> match_start) PLUS in-match exit window (match_start -> settlement-300).
- **Frame I (in-match price-level):** entry mark = in-match minutes on the validated Layer-A price-level axis (the conservative fill frame the validated descriptive surface established; bilateral near-efficient/87%-within-1c confirms in-match price is also largely FV-aligned). Forward tape = in-match exit window only (the Layer-A regime).

For EACH frame, per price band, E32's locked exit model:
- **Cell** = price band (one axis: price; E32(a)). Band-free continuous price-level binning as in Layer-A (>=40 quantile bins, display device not model band).
- **Exit target** = derived per band from the band itself (E32(e): "every band gets its own exit target derived from the band"). The exit-target derivation rule is specified in Sec 2.3.
- **No stop** (E32(c)): two outcomes only -- reach the band-derived exit target (record realized bounce to that exit), or ride to settlement (record the settlement answer-key outcome). Non-winners are NOT cut.
- **Two exit windows** (E32(f)): a position can hit its target in the earlier window OR ride into the later window and hit it there. Frame P: premarket-exit OR in-match-exit. Frame I: in-match-exit only (single window -- the Layer-A regime; the "two windows" structure is Frame-P-specific by construction, recorded explicitly).
- **Settlement = answer key, not objective** (E32(d)): first touch of 99c/1c (`settlement_value`) is the ground-truth that scores the hindsight-optimal exit; it is NEVER the optimized quantity.
- **Ranking metric** = highest average bounce per cell band (E32(e) -- NOT hit rate, which is gameable with tiny targets; average bounce rewards both reaching the exit and the exit being large, misses drag it down). A39: emitted in BOTH cents AND ROI.

**Headline output:** the cross-frame robustness table -- exit-optimized average bounce per band under Frame P vs Frame I, with explicit per-band agreement/divergence. An edge present in both frames is robust; an edge present in only one is frame-dependent (flagged, not hidden).

### 1.2 Out of scope (v1)

- NO fees / slippage / fill-probability modeling (Layer-C-equivalent -- deferred entirely).
- NO new entry venues beyond the two specified conservative-fill frames.
- NO stop-loss / position-cutting logic (E32(c) -- no stop, by locked model).
- NO hit-rate as a ranking metric (E32(e) -- explicitly rejected as gameable; emitted only as a reported secondary diagnostic, never the ranking).
- NO settlement-scored objective (TAXONOMY 195/196 -- settlement is the answer key; a settlement-scored number measured the wrong objective).
- NO re-derivation of the Layer-A descriptive surface (it is validated; this is built on it per B16, not replacing it).

### 1.3 Relationship to existing artifacts

- Built on the validated Layer-A (inmatch_bounce_surface_v1, 6f1d4bde) per B16 -- the in-match frame's descriptive foundation and the reference both frames' exit-optimized results are interpreted against.
- Reads per_minute_features fresh (not a query over the Layer-A aggregated surface) because E32's exit model needs the per-minute forward tape and the T-20m mark, which the aggregated surface does not carry. This is the spec Sec 6-of-Layer-A *intent* (B16 layered build) honored over its now-superseded literal "vectorized query over v1" wording -- recorded honestly.
- This is the first **exit-optimized** (TAXONOMY 196 locked objective) deliverable post foundation-rebuild. Legacy settlement-scored findings in ANALYSIS_LIBRARY tagged NEEDS RECOMPUTATION are recomputed conceptually by this model (not silently reclassified).

---

## 2. Schema

One row per (price_band x fill_frame x exit_window_resolution x category), with pooled (category=ALL) as headline and per-category as the reported covariate stratum (carrying the Layer-A probe-2 finding: pooled with category as level-covariate, not separate shape fits).

### 2.1 Column families

**Identity:**
- `fill_frame` (string) -- `P_premarket_t20` / `I_inmatch_pricelevel`.
- `price_band_lo`, `price_band_hi`, `price_band_mid` (float64) -- continuous-axis quantile-bin bounds (>=40 bins; display device, band-free preserved).
- `exit_window_resolution` (string) -- how the position resolved: `hit_target_window1` / `hit_target_window2` / `rode_to_settlement`. (Frame I has only `window1`=in-match; `window2` rows are null/absent for Frame I and that asymmetry is documented, not papered over.)
- `category` (string) -- `ALL` / `ATP_MAIN` / `ATP_CHALL` / `WTA_MAIN` / `WTA_CHALL`.

**Exit-optimized bounce -- the locked objective, A39 dual (mandatory):**
- `exit_bounce_c_mean`, `_median`, `_p25`, `_p75`, `_p90` (float64) -- realized bounce in cents from fill to the resolved exit (band-derived target if hit, settlement answer-key outcome if rode). The E32(e) headline ranking metric (in cents).
- `exit_bounce_roi_mean`, `_median`, `_p25`, `_p75`, `_p90` (float64) -- same in ROI (= bounce / entry_price). A39: both emitted every row; neither proxies the other (the Layer-A inversion carries through).
- `avg_bounce_rank_metric` (float64) -- the E32(e) ranking value: average realized bounce per band (cents), the headline by which bands are ranked. Explicitly the average over ALL positions in the band (winners reaching target AND riders to settlement) -- misses drag it down by construction (E32(e)).

**Exit-target provenance (per band):**
- `exit_target_c` (float64) -- the band-derived exit target (cents), per Sec 2.3.
- `exit_target_rule` (string) -- the derivation rule applied (audit trail; Sec 2.3).

**Settlement answer-key (E32(d) -- ground truth, NOT objective):**
- `settlement_outcome_frac_yes` (float64) -- fraction of band's N's settling YES (`settlement_value`->1). Diagnostic context for interpreting riders; NEVER the optimized quantity. Flagged answer-key-only.
- `rode_to_settlement_frac` (float64) -- fraction of band's positions that did NOT hit target and rode to settlement (the E32(c) non-winners-not-cut population).

**Secondary diagnostics (reported, NEVER ranking):**
- `hit_rate` (float64) -- fraction reaching the band-derived target. Reported per E32(e) as a diagnostic ONLY; explicitly NOT the ranking metric (gameable with tiny targets -- gate G4 asserts ranking uses avg_bounce, not this).
- `n_positions` (int64), `n_tickers` (int64), `low_support` (bool).
- `entry_mark_ttms_median`, `_p25`, `_p75` (float64) -- B22 fill-distribution descriptor: the `time_to_match_start_min` distribution of the entry mark within this frame/band (Frame P clusters ~ +20; Frame I is negative/in-match -- characterized, not assumed a point).

**Cross-frame robustness (the headline):**
- Emitted as a derived companion table `robustness.parquet`: per (price_band x category), Frame-P avg_bounce vs Frame-I avg_bounce, the sign-agreement flag, and the magnitude ratio. An edge is `robust` iff present (same sign, both materially > 0) in BOTH frames; `frame_dependent` otherwise (flagged, the decision-critical finding).

### 2.2 Derived-quantity definitions (exact -- prevents A38/A39/E32 contamination)

- **Frame P entry mark:** for each N, the minute where `time_to_match_start_min` is closest to +20 within the premarket regime (`regime=="premarket"`), with a tolerance window (+/-2 min) -- characterized as a distribution (B22), not assumed exact. `entry_price` at that minute = `yes_ask_close` (maker-buy fills at the ask, conservative). The "FV-anchored" property is reported (the bilateral pair-sum proximity at that mark) but is descriptive context, not a filter.
- **Frame I entry mark:** in-match minutes (`regime=="in_match"`), `entry_price = yes_ask_close`, on the Layer-A price-level axis -- identical to the validated Layer-A entry model (this frame IS the validated surface's entry model, carried into the exit-optimized objective).
- **Exit realization (E32 locked, both frames):** from the entry mark, walk the forward tape. If the band-derived `exit_target_c` (Sec 2.3) is reached within the frame's exit window(s), realized bounce = (target - entry_price) [the exit is the target, by construction of "hit target"]. If NOT reached, the position rides to settlement: realized bounce = (settlement-determined terminal value - entry_price) using `settlement_value` as the answer key (E32(d)). NO STOP -- there is no third "cut" outcome (E32(c)).
- **A38 firewall:** the exit is a FINITE real exit (the band-derived target) or the settlement answer-key terminal. The optimized quantity is NEVER "max bid through settlement" (that is the A38 saturation). Gate G3 asserts no exit-bounce column is computed from `*_forward_to_settlement` max-bid labels; settlement enters ONLY as the answer-key terminal for riders, via `settlement_value`, not via a forward-max label.
- **Forward tape source:** Frame P uses `*_forward_to_match_start` (premarket window) THEN the in-match forward labels (in-match window) -- the two exit windows, decomposed (B14/G17), resolved in order (window1 premarket, window2 in-match). Frame I uses the in-match forward labels only (single window).

### 2.3 Band-derived exit target (E32(e) -- "every band gets its own exit target derived from the band")

E32(e) mandates each band has its own exit target derived from the band, and notes extremes fail for opposite reasons (~95c band: risking 95c for <=4c; ~5c band: never enough traction). The target derivation rule (v1):

- The exit target is the band's entry price plus a band-proportionate move, where the move is **characterized from the validated Layer-A bounce surface for that band** (the Layer-A surface IS the realized-bounce distribution per band -- B16: Layer-B's target is derived from Layer-A's measured property). v1 rule: `exit_target_c = entry_price + f(band)` where `f(band)` = the Layer-A pooled median realized 30min bounce for that price band (a conservative, measured, per-band move -- NOT a flat target, NOT hit-rate-gamed).
- This makes the exit target **measured, per-band, derived from the validated descriptive layer** -- the literal B16 "Layer-B built on validated Layer-A" relationship. The rule is recorded in `exit_target_rule` per row for audit.
- **B20 / characterize-don't-assume:** the per-band target shape (does the median-bounce-derived target produce the E32(e)-predicted extreme failures?) is CHARACTERIZED in the validation report (logged), explicitly NOT assumed. The extreme-band behavior E32(e) predicts (95c/5c failing for opposite reasons) is a measured output to confirm, not a baked assumption.

---

## 3. Producer architecture

### 3.1 Inputs (read-only)

- `per_minute_features.parquet` (sha 9fde4b5d) -- fresh per-ticker pushdown. Columns: `ticker, minute_ts, category, regime, premarket_phase, yes_bid_close, yes_ask_close, mid_close, time_to_match_start_min, time_to_settlement_min, settlement_value` + forward-label family (`max_yes_bid_forward_{5,15,30,60}min`, `max_yes_bid_forward_to_match_start`) + partner pair-sum columns (for the FV-anchor descriptive context).
- `n_profile.parquet` (sha a7ed1155) -- cohort screen (F35-reliable tier-1/2 live-era; same as Layer-A).
- `inmatch_bounce_surface_v1/surface.parquet` (sha 14241db0) -- read for the per-band `f(band)` exit-target derivation (Sec 2.3); the B16 Layer-A->Layer-B dependency.

### 3.2 Pipeline

1. Cohort screen from n_profile_v1 (identical to Layer-A: match_start_method in {both_sides_*}, tier==live, total_volume_in_match>0; ~7,383 expected).
2. Per-ticker pushdown of per_minute_features (the proven bounded-memory pattern: per-ticker filter, explicit del, gc-every-200 -- the n_profile/Layer-A OOM lesson; gate G8).
3. For each N, extract BOTH entry marks: Frame P (the T-20m+/-2 premarket minute) and Frame I (all in-match minutes, Layer-A model).
4. Load per-band `f(band)` from the validated Layer-A surface; derive `exit_target_c` per band (Sec 2.3).
5. For each (N, frame, entry mark): walk the frame's forward tape, resolve exit (hit target in window -> realized bounce to target; else ride to settlement -> answer-key terminal via settlement_value). E32 no-stop.
6. Aggregate per (price_band x fill_frame x exit_window_resolution x category) AND pooled (category=ALL). Emit A39 dual (cents AND ROI), the E32(e) avg_bounce ranking metric, secondary diagnostics.
7. Build the cross-frame `robustness.parquet`: per band/category, Frame-P vs Frame-I avg_bounce, sign-agreement, magnitude ratio, robust/frame_dependent flag.
8. Shape characterization (B20, Spearman-based -- reuse the v0.3 Layer-A classifier discipline, NOT a brittle argmin heuristic): log the exit-optimized-bounce-vs-band curve shape per frame, and the cross-frame agreement, MEASURED.

### 3.3 Phased rollout

- **Phase 1:** 1000-ticker stratified sanity (<40min), all gates, both frames produced, robustness table populated, memory bounded. Direction sanity: Frame-I exit-optimized bounce should relate sensibly to the validated Layer-A (it's the same entry model + an exit policy on top -- the exit-optimized average must be <= the unconditional forward-max by construction; a violation = wiring bug -> STOP).
- **Phase 2:** full cohort, all gates. Full run IS Phase 2 (aggregate, not per-N rebuild).

### 3.4 Output

`data/durable/exit_optimized_bounce_v1/surface.parquet` + `robustness.parquet` + `meta.json` (producer_commit, ALL THREE input shas: per_minute_features 9fde4b5d, n_profile a7ed1155, layer-A surface 14241db0; cohort_n; gate results) + `validation_report.md` (gate table, per-frame exit-optimized cents+ROI curves, the cross-frame robustness table as the headline, the E32(e) extreme-band-failure characterization, B22 entry-mark distributions per frame, A38-firewall confirmation).

---

## 4. Validation gates

### 4.1 Hard gates (block; quarantine-don't-delete; C37 reload-from-disk-then-gate-then-replace)

- **G1 cohort parity:** cohort N from screen == contributing + accounted dropouts (phase-aware: parity vs the ATTEMPTED ticker set -- the Layer-A G1 lesson; never hardcode full cohort against a subsample).
- **G2 frame purity:** Frame P entry marks are 100% `regime=="premarket"` with `time_to_match_start_min` in [+18,+22] (the T-20m+/-2 window); Frame I entry marks are 100% `regime=="in_match"`. Zero cross-frame leakage (B14/G17 -- the two frames are economically distinct, never conflated; this is the gate that prevents the legacy NEEDS-RECOMPUTATION conflation).
- **G3 A38 firewall:** assert NO exit-bounce column derives from a `*_forward_to_settlement` max-bid label. Settlement enters ONLY as the rider answer-key terminal via `settlement_value` (E32(d)). The exit-optimized mean must be materially BELOW the unconditional forward-max-to-settlement (if it is not, the exit policy is not actually capping -- A38 contamination; STOP).
- **G4 ranking-metric integrity:** the ranking/headline column is `avg_bounce_rank_metric` (average realized bounce, ALL positions incl. settlement-riders). Assert `hit_rate` is present but NOT used as the ranking (E32(e) -- hit-rate is gameable; gate fails if the ranking is computed from hit_rate).
- **G5 no-stop integrity:** every position resolves to exactly one of {hit_target_window1, hit_target_window2, rode_to_settlement}. Assert ZERO positions in any "cut/stopped" state (E32(c) -- no stop; a stopped position = model violation).
- **G6 A39 dual completeness:** every row has BOTH a non-null cents family AND a non-null ROI family. No row carries one without the other.
- **G7 band support:** every pooled (band x frame) row has `n_positions >= 200` (B20 -- no shape claim on a thin cell; per-category below-threshold flagged low_support, not suppressed).
- **G8 memory bound:** peak producer RSS under recorded envelope (the n_profile/Layer-A OOM lesson; ~7,383-ticker fresh pushdown + the Layer-A surface join -- expect bounded ~1.2-1.5GB by analogy to Layer-A's 1184MB; sustained climb toward 1.9GB = hard fail).
- **G9 robustness-table completeness:** `robustness.parquet` has one row per (populated band x category) with the robust/frame_dependent flag set; no band silently absent (the headline output must be complete or the deliverable's central question is unanswered).

### 4.2 Informative measurements (logged, not blocking)

- Per-frame exit-optimized bounce-vs-band curve shape (Spearman-based per the v0.3 discipline -- NOT a brittle classifier; cents AND ROI, the inversion expected to carry from Layer-A).
- The cross-frame robustness summary: how many bands robust vs frame_dependent (the decision-critical headline).
- E32(e) extreme-band characterization: do the ~95c and ~5c bands fail for the opposite reasons E32(e) predicts (risk-reward geometry vs traction)? -- MEASURED, not assumed.
- B22 entry-mark `ttms` distributions per frame (Frame P should cluster tightly ~+20; Frame I spread across in-match).
- Per-category level shifts vs pooled (the Layer-A probe-2 covariate finding -- reported, not modeled as shape).

---

## 5. The B16 layering contract (explicit -- prevents the conflation that caused the legacy NEEDS-RECOMPUTATION cluster)

This is Layer-B-equivalent. The contract:
- Layer-A (inmatch_bounce_surface_v1, validated 6f1d4bde) is the property-of-market descriptive surface. It is NOT replaced.
- Layer-B (this) applies the E32 locked EXIT POLICY on top -- the band-derived exit target (Sec 2.3) is itself derived from Layer-A's measured per-band bounce (the literal "built on the validated layer below" relationship).
- Frame I's entry model IS Layer-A's entry model (in-match price-level) -- so Frame I is the direct Layer-B-over-Layer-A: same entries, plus the E32 exit policy. Frame P is the conservative-premarket-fill comparator that tests whether the edge is fill-frame-robust.
- Layer-C (fees/slippage/fills) is explicitly deferred. This spec does NOT model them. A future Layer-C-equivalent consumes THIS validated Layer-B.
- The honest record (G23/4f55339 discipline): Layer-A spec Sec 6 said the exit layer would be "a vectorized query over v1's surface." Probe evidence later showed v1's surface is in-match-ENTRY by construction; E32's model needs the per-minute forward tape + the T-20m mark, which the aggregated surface does not carry. This spec honors spec-Sec 6's B16 *intent* (Layer-B built on a validated Layer-A) while superseding its literal "query over v1" wording -- recorded here, not silently changed.

---

## 6. Cross-references

- LESSONS E32 (locked cell/exit model -- the resolution authority), B16 (layering), B14/G17 (premarket/in-match decomposition), A38 (finite-exit firewall), A39 (dual-metric), C38 (resolve-don't-assume), E31 (pre/in-game economic distinction), B20 (characterize the curve), B22 (fill-as-distribution), F35 (tier-1/2 cohort), G23/4f55339 (honest-provenance for the superseded spec-Sec 6 wording)
- per_minute_universe_spec.md Sec 2.8 / Sec 7 / Sec 2.6; inmatch_bounce_surface_v1_spec.md (validated Layer-A, lineage 6f1d4bde); TAXONOMY 2.5 / line 196 (exit-optimized = locked objective)
- Foundations: per_minute_features 9fde4b5d (T37 ckpt-3), n_profile a7ed1155 (c76eee5/c9a0f3e), inmatch_bounce_surface_v1 surface 14241db0 (6f1d4bde)

## 7. Resolution log (v0.1 -- 2026-05-18)

- Exit logic / no-stop / two-exit-windows / settlement=answer-key / avg-bounce-per-band ranking: RESOLVED by LESSONS E32 (the locked model). Not assumed.
- T-20m = conservative FV-anchored fill ASSUMPTION, not a structural axiom forbidding in-match entry: RESOLVED by operator clarification 2026-05-18 ("we only did T-20 for analysis because it's a conservative period to fill bids and when it's aligned with the FV anchor"). E32(f)'s "never an entry venue" reinterpreted as that frame's fill conservatism, not an immutable law. Not assumed -- operator-resolved.
- Both conservative-fill frames emitted side-by-side, cross-frame robustness as the headline: RESOLVED by operator decision 2026-05-18 (option 3). An edge robust under both conservative frames is real; surviving only one = frame-dependent, decision-critical pre-deployment. Not assumed -- operator-resolved.
- Band-derived exit target = per-band measured move from the validated Layer-A surface (Sec 2.3): the literal B16 Layer-B-built-on-validated-Layer-A relationship. The extreme-band-failure behavior E32(e) predicts is a MEASURED output (B20 characterize-don't-assume), not baked.
- A38 firewall: settlement enters ONLY as the rider answer-key terminal (E32(d)), never as a forward-max label -- structurally satisfies A38 by the locked model itself. Gate G3.
- Spec-Sec 6-of-Layer-A "vectorized query over v1" wording superseded by B16 intent (E32 needs the per-minute tape + T-20m mark the aggregated surface lacks): recorded honestly Sec 5, not silently changed (G23/4f55339 discipline).
