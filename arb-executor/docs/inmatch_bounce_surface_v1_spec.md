# In-Match Bounce Surface v1 Spec — Band-Free Price-Level Bounce Characterization

**Status:** v0.1 — initial draft 2026-05-18 ET. The first analytical deliverable built on the n_profile_v1 foundation. Layer-A-equivalent per LESSONS B16: this spec characterizes a *property of the market* (the band-free in-match forward-bounce surface as a function of price-level), with NO exit policy, NO fees, NO fill model. Exit-optimization (the locked E32 objective) is defined here as a Phase-2 interface but explicitly NOT implemented in v1.

**Every structural decision in this spec is evidence-grounded from two read-only probes (not assumed structure — C38 discipline):**
- Probe-1 (2026-05-18, /tmp/bounce_probe.log): organizing axis = band-free continuous price-level `|mid_close − 0.50|`. The bilateral axis (`|partner_sum − 1.00|`, B23/E18) is near-degenerate (87% of minutes at dislocation ≤0.01, ~2c bounce span vs price-level's ~15c) — measured negative, NOT the organizing dimension. The load-bearing structure is the A39 cents↔ROI inversion: absolute-cents bounce is monotone-DOWN (max at coin-flip mid≈0.50), ROI is monotone-UP (max at the cheap-longshot extreme) — they invert on the same axis. A38 saturation confirmed (to-settlement ~1.9× the finite-30min mean). SCALP-window asymmetry holds and strengthens 5→60min.
- Probe-2 (2026-05-18, /tmp/bounce_probe2.log): the cents↔ROI inversion is category-UNIVERSAL in shape and sign across ATP_MAIN / ATP_CHALL / WTA_MAIN / WTA_CHALL (all power-adequate, THIN list empty). The operation's prior ("ATP_CHALL tracks WTA, diverges from ATP_MAIN") does NOT transfer to this axis — ATP_MAIN sits mid-pack between the WTAs; no ATP/WTA or main/challenger clustering. Stratification = pooled with category as a level-covariate only (mild ~+0.01c WTA shift on a shared shape), NOT separate per-category shape fits.

**Anchored to:**
- LESSONS B16 (Layer A/B/C separation; this is Layer-A-equivalent — property of market, not strategy)
- LESSONS B14 / G17 (in-match strictly decomposed from premarket; never conflate the two windows)
- LESSONS B20 (spec the curve SHAPE, not just direction; second-order shapes are characterized not assumed)
- LESSONS B22 (fill is a distribution across in-match minutes, not a single anchor point — retrospective-conditional)
- LESSONS A38 (peak-through-settlement saturates on the post-resolution 99c pin — finite-horizon forward labels are the operational metric; to-settlement is diagnostic-only)
- LESSONS A39 (absolute cents and ROI are structurally different ranking metrics that must BOTH be emitted — here the inversion makes this structurally mandatory, not cosmetic)
- LESSONS B23 / E18 (bilateral structure — measured near-degenerate on this axis by probe-1; recorded as a negative result, not the organizing dimension)
- LESSONS C38 (probe-don't-assume; every structural choice here is probe-resolved)
- LESSONS E32 (the locked cell/exit model — the Phase-2 exit-optimization interface, defined not implemented)
- LESSONS F35 (tier-3 match_start_method boundary-unreliable; cohort screens to tier-1/2)
- LESSONS G23 (both_sides_active_minutes corpus-scoped — the n_profile_v1 column the cohort screen uses)
- TAXONOMY Section 2.5 (GRAIN / VECTOR / OBJECTIVE classification triple)
- n_profile_v1_spec.md (the per-N foundation this analysis screens the cohort from)
- per_minute_universe_spec.md Section 2.8 (the forward-looking label columns this analysis aggregates)

**Foundation pointers:**
- Cohort screen: `data/durable/n_profile_v1/n_profile.parquet` (sha256 a7ed1155…, producer commit a28840e, ANALYSIS_LIBRARY lineage c76eee5, MANIFEST c9a0f3e)
- Bounce source: `data/durable/per_minute_universe/per_minute_features.parquet` (FOUNDATION-TIER, sha256 9fde4b5d…, T37 ckpt-3)

**Output:** `data/durable/inmatch_bounce_surface_v1/` (parquet + meta.json + validation_report.md)

**GRAIN / VECTOR / OBJECTIVE (TAXONOMY 2.5):** Grain = per-(price-level-bin × horizon) aggregate over in-match minutes (the surface). Vector = vector-agnostic (descriptive market property). Objective = objective-agnostic in v1 (descriptive); Phase-2 interface carries the exit-optimized objective.

---

## 1. Scope

### 1.1 In scope

v1 produces the **band-free in-match forward-bounce surface**: how realized forward bounce (in BOTH absolute cents and ROI) varies as a continuous function of price-level dislocation `|mid_close − 0.50|`, over in-match minutes of the F35-reliable tier-1/2 live-era cohort, at finite forward horizons (5/15/30/60min, 30min headline).

The artifact answers: **"for an in-match minute at a given price-level, what forward bounce was achievable — in cents and in ROI — and what is the shape of that relationship across the price-level axis?"**

- Band-free: price-level is a continuous axis. No inherited `entry_band` / `spread_band` / `volume_intensity` pre-bucketing. Binning exists ONLY as a reporting/display device (fine-grained, ≥40 quantile bins) over the continuous axis, never as a model structure.
- Pooled across categories; category emitted as a reported covariate column for the measured ~+0.01c WTA level shift, NOT as a separate-shape stratification (probe-2).
- Dual-metric: every bounce figure emitted in BOTH absolute cents AND ROI (= bounce / entry_price). Structurally mandatory — the metrics invert on this axis (probe-1+2).
- Finite-horizon: 5/15/30/60min forward labels. 30min is the operational headline. `_to_settlement` carried as the A38 diagnostic comparator ONLY.
- In-match only: `regime == "in_match"` (B14/G17).
- Fill as a distribution: characterized across the `time_to_match_start_min` distribution of in-match minutes, NOT a single assumed entry point (B22).

### 1.2 Out of scope (v1 — Layer-A-equivalent per B16)

- NO exit policy / exit-target optimization (that is the Phase-2 interface, §6 — defined, not implemented).
- NO fees, slippage, or fill-probability modeling (Layer-C-equivalent — out of scope entirely for v1).
- NO bilateral-axis modeling (probe-1 measured it near-degenerate; recorded as a negative result in §5, not modeled).
- NO premarket window (B14/G17 — in-match strictly decomposed).
- NO per-category separate shape fits (probe-2 — pooled with category covariate).
- NO settlement-anchored bounce as an operational metric (A38 — diagnostic-only).

### 1.3 Relationship to existing artifacts

- Reads cohort screen from n_profile_v1 (per-N foundation), bounce data from per_minute_features (per-minute foundation). It is the join: select cohort N's via n_profile_v1, aggregate their in-match forward labels from per_minute_features.
- Layer-A-equivalent per B16. Distinct from the legacy Layer A v1 (`cell_stats.parquet`, SUPERSEDED) — that was band-bucketed and pre-rebuild; this is band-free on the FOUNDATION-TIER corpus.
- Supersedes nothing; it is the first post-rebuild bounce-surface deliverable.

---

## 2. Schema

One row per (price_level_bin × horizon × category) — the surface, with pooled rows (category = "ALL") as the headline and per-category rows as the reported covariate stratum.

### 2.1 Column families

**Identity / axis:**
- `price_level_bin_lo`, `price_level_bin_hi` (float64) — the continuous-axis quantile-bin bounds on `|mid_close − 0.50|`. Bins are a display device over the continuous axis (≥40 quantile bins; see §3.2).
- `price_level_bin_mid` (float64) — bin midpoint, the plotting x-coordinate.
- `horizon` (string) — one of `5min` / `15min` / `30min` / `60min`. `30min` is the headline.
- `category` (string) — `ALL` (pooled headline) / `ATP_MAIN` / `ATP_CHALL` / `WTA_MAIN` / `WTA_CHALL`. Pooled is primary; per-category rows are the reported level-covariate stratum (probe-2), NOT separate models.

**Bounce — absolute cents (A39, mandatory):**
- `bounce_c_mean`, `bounce_c_median`, `bounce_c_p25`, `bounce_c_p75`, `bounce_c_p90` (float64) — realized forward bounce in cents = `max_yes_bid_forward_{horizon} − entry_price`, aggregated over the bin's in-match minutes.
- `bounce_c_frac_positive` (float64) — fraction of minutes in bin with bounce_c > 0 (the SCALP-capture signal).

**Bounce — ROI (A39, mandatory):**
- `bounce_roi_mean`, `bounce_roi_median`, `bounce_roi_p25`, `bounce_roi_p75`, `bounce_roi_p90` (float64) — `(max_yes_bid_forward_{horizon} − entry_price) / entry_price`.
- The cents and ROI families are BOTH emitted for every row. Consumers pick by decision type (cents = capital-deployment / per-contract throughput; ROI = percent-return / cross-band comparison). Per A39 + probe-1+2: these invert on the price-level axis — neither may proxy the other.

**Diagnostic (A38 — comparator ONLY, never operational):**
- `bounce_c_to_settlement_mean`, `bounce_c_to_settlement_median` (float64) — `max_yes_bid_forward_to_settlement − entry_price`. Emitted SOLELY to demonstrate the A38 saturation (expected ~1.9× the finite-30min figure per probe-1). Flagged in-column-comment and in validation_report as diagnostic-only. Any downstream consumer using this as an operational bounce is in error.

**Cell support / honesty:**
- `n_minutes` (int64) — in-match minutes aggregated into this bin (the support).
- `n_tickers` (int64) — distinct N's contributing.
- `time_to_match_start_min_median`, `_p25`, `_p75` (float64) — the B22 fill-distribution descriptor for this bin (so consumers see WHEN in the match these fills concentrate, not assume a point).

### 2.2 Derived-quantity definitions (exact, to prevent A38/A39 contamination)

- `entry_price` := `yes_ask_close` (a maker buying YES fills at the ask; bounce is realized on the forward `yes_bid`). Minutes with `entry_price ≤ 0.01` or `≥ 0.99` are excluded (degenerate / already-resolved).
- `price_level_dislocation` := `abs(mid_close − 0.50)` where `mid_close = (yes_bid_close + yes_ask_close)/2`. Continuous. The organizing axis (probe-1).
- Forward bounce uses ONLY the finite-horizon labels `max_yes_bid_forward_{5,15,30,60}min` from per_minute_features §2.8. `max_yes_bid_forward_to_settlement` is used ONLY for the diagnostic columns. This is the A38 firewall, in the schema.
- In-match := `regime == "in_match"` (the per_minute_features derived column: `minute_ts ≥ match_start_ts AND minute_ts < settlement_ts − 300`). B14/G17.

---

## 3. Producer architecture

### 3.1 Input artifacts (read-only)

- `data/durable/n_profile_v1/n_profile.parquet` — cohort screen (per-N). Columns used: `ticker`, `category`, `match_start_method`, `tier`, `total_volume_in_match`.
- `data/durable/per_minute_universe/per_minute_features.parquet` — bounce source (per-minute). Columns used: `ticker`, `minute_ts`, `category`, `regime`, `yes_bid_close`, `yes_ask_close`, `mid_close`, `time_to_match_start_min`, `max_yes_bid_forward_{5,15,30,60}min`, `max_yes_bid_forward_to_settlement`.

### 3.2 Pipeline

1. **Cohort screen** from n_profile_v1: `match_start_method ∈ {both_sides_price_discovery, both_sides_trade_density}` AND `tier == "live"` AND `total_volume_in_match > 0`. Expected ~7,383 N's (probe-validated; gate-checked, §4). This is the F35-reliable tier-1/2 live-era cohort.
2. **Per-ticker pushdown** of in-match minutes from per_minute_features (the proven bounded-memory pattern — per-ticker `pq.read_table(..., filters=[('ticker','=',t)])`, filter `regime=="in_match"`, accumulate; explicit `del` per iteration; NEVER whole-frame load). Memory must stay bounded (the n_profile_v1 OOM lesson — gate-checked, §4).
3. **Derive** `entry_price`, `price_level_dislocation`, and the per-minute cents + ROI bounce at each finite horizon (§2.2). Exclude degenerate entry prices.
4. **Bin the continuous axis for display**: ≥40 quantile bins on `price_level_dislocation` (fine enough that the bin is a display device, not a model band — the band-free property is preserved; the surface is the continuous relationship, bins only render it). Quantile (not fixed-width) so each bin has comparable support.
5. **Aggregate** per (price_level_bin × horizon × category) AND per (price_level_bin × horizon × category="ALL" pooled). Emit the full cents + ROI + diagnostic + support families (§2.1).
6. **Shape characterization** (B20 — measured, not assumed): for the pooled headline (category="ALL", horizon=30min), compute and log the monotonicity/shape of the cents curve and the ROI curve and confirm the inversion. The ROI mid-trough-before-cheap-peak (probe noted as a second-order shape) is CHARACTERIZED here (logged in validation_report), explicitly NOT assumed.

### 3.3 Phased rollout

- **Phase 1**: 1000-ticker stratified subsample (category × price-level), <30min, equivalence-style sanity (shape direction matches probe-1+2). Memory-bounded check.
- **Phase 2 (re-validation)**: full cohort, all gates (§4).
- **Phase 3**: not applicable (this is an aggregate, not a per-N rebuild — the cohort is fixed at ~7,383). Full run IS Phase 2.

### 3.4 Output

`data/durable/inmatch_bounce_surface_v1/surface.parquet` + `meta.json` (producer_commit, inputs_sha256 for BOTH foundations, cohort_n, gate results) + `validation_report.md` (gate table, the pooled 30min cents+ROI curves, the inversion confirmation, the A38 saturation demonstration, the B20 second-order ROI-shape characterization, per-category level-shift table).

---

## 4. Validation gates

### 4.1 Hard gates (block on failure; quarantine-don't-delete; C37 re-validate vs on-disk bytes pre-replace)

- **G1 cohort parity**: cohort N count from n_profile_v1 screen == distinct tickers contributing in-match minutes + an accounted dropout list (N's with zero in-match minutes are logged with reason, not silently dropped). Expected cohort ~7,383 (probe-validated).
- **G2 in-match purity**: 100% of aggregated minutes have `regime == "in_match"` (B14/G17 — zero premarket contamination). NOTE (v0.2 correction, evidence /tmp/g2_probe.log): v0.1 also asserted `time_to_match_start_min < 0`; that was a spec OVER-SPECIFICATION inconsistent with the foundation. per_minute_universe_spec defines `in_match := minute_ts >= match_start_ts` — INCLUSIVE of the match-start boundary minute, which the foundation tags `regime=="in_match"` with `time_to_match_start_min == 0`. Probe: of regime==in_match rows, ZERO have ttms>0; the only non-negative are exactly the ttms==0 boundary minute (~1/ticker). regime-purity alone is the correct invariant (already perfect — non_in_match=0); the ttms<0 clause was redundant and contradicted the foundation contract the analysis relies on. Honest-provenance per the G23 / 4f55339 discipline: the committed v0.1 G2 was wrong; this is the corrected definition with its probe evidence, not a silent patch.
- **G3 A38 firewall**: the operational bounce columns are computed ONLY from finite-horizon labels; assert no operational column references `max_yes_bid_forward_to_settlement`. The diagnostic column must show mean ≥ 1.3× the finite-30min mean (the A38 saturation must be VISIBLE — if it is not, the finite/settlement wiring is suspect).
- **G4 A39 dual completeness**: every emitted surface row has BOTH a non-null cents family AND a non-null ROI family. No row may carry one without the other.
- **G5 dislocation domain**: `price_level_dislocation ∈ [0, 0.49]` for all aggregated minutes (sanity on the axis; 0.49 = entry-price-exclusion boundary).
- **G6 bin support**: every emitted (bin × horizon × category="ALL") row has `n_minutes ≥ 200` (B20 — no shape claim on a thin cell; per-category rows below threshold are emitted with a `low_support=true` flag, not suppressed, not used for shape claims).
- **G7 memory bound**: peak producer RSS stays under a recorded envelope through the per-ticker pushdown (the n_profile_v1 OOM lesson — explicit watch; the cohort is ~7,383 tickers, probe runs peaked ~780MB bounded — a sustained climb toward 1.9GB is a hard failure).

### 4.2 Informative measurements (logged, not blocking)

- Pooled 30min cents-curve and ROI-curve monotonicity + the inversion (expected from probe-1+2: cents monotone-DOWN, ROI rising-to-cheap-extreme, inverted — but MEASURED and reported, per B20, not asserted).
- Per-category level shifts vs pooled (expected ~+0.01c WTA per probe-2 — reported as covariate, not modeled as shape).
- The B22 fill-distribution (`time_to_match_start_min`) per bin.
- SCALP-window sensitivity table (5/15/30/60min — expected to strengthen with horizon per probe-1; the A38-drift toward longer horizons noted).

---

## 5. Recorded negative result (bilateral axis — measured, not assumed)

Probe-1 measured the bilateral-mispricing axis (`|partner_sum − 1.00|`, the B23/E18 mechanism that n_profile_v1's corpus-scoped `both_sides_active_minutes` was built to enable): **near-degenerate.** 87% of in-match minutes sit at bilateral dislocation ≤0.01 (the bilateral market is highly efficient), with only ~2c bounce span across the entire bilateral range vs ~15c on the price-level axis. This is a *measured negative*, recorded honestly (per the 4f55339 / G23 honest-provenance discipline): the bilateral axis is NOT the bounce-organizing dimension on this cohort/structure, despite its theoretical centrality (B23/E18) and despite the foundation work (G23) that made it analyzable. v1 does NOT model the bilateral axis. Recording WHY it was excluded prevents a future session re-deriving it as an open question.

---

## 6. Phase-2 interface — exit-optimization (DEFINED, NOT IMPLEMENTED in v1)

Per B16 layered-realism staging: v1 is Layer-A-equivalent (property of market). The locked exit-optimized objective (LESSONS E32 / TAXONOMY line 196: "realized bounce from fill to an optimized exit target — average bounce per cell band, no stop, two exit windows") is the Layer-B-equivalent next stage. v1 is specified so that stage plugs in WITHOUT rework:

- v1 emits the cohort definition, the per-minute `entry_price`, the price-level axis, and the finite-horizon forward-label-derived bounce — i.e. the raw observation + realized-outcome surface. The exit-optimization layer becomes a vectorized query over these (mirroring how legacy Layer B became a vectorized operation over Layer A's forward labels per per_minute_universe_spec §1).
- The Phase-2 spec will: (a) read v1's surface + the per-minute forward labels, (b) apply the E32 locked cell/exit model (no stop, two exit windows) as a policy grid over the finite-horizon labels, (c) emit exit-optimized realized bounce per price-level bin — strategy-actionable, built ON the validated v1 descriptive surface, NOT replacing it.
- v1 explicitly does NOT implement any exit policy. The interface contract is: v1's output is the validated descriptive foundation; Phase-2 consumes it. This is the B16 discipline (each layer built on the validated one below), and it prevents the Layer-A/B conflation that produced the legacy NEEDS-RECOMPUTATION cluster.

---

## 7. Cross-references

- LESSONS B16 (Layer A/B/C; this is Layer-A-equivalent), B14/G17 (in-match decomposition), B20 (spec the curve; second-order shapes characterized), B22 (fill-as-distribution), A38 (finite-horizon firewall), A39 (dual-metric mandatory), B23/E18 (bilateral — measured negative §5), C38 (probe-don't-assume — every structural choice probe-resolved), E32 (Phase-2 exit interface), F35 (tier-1/2 cohort), G23 (corpus-scoped both_sides_active_minutes — the cohort screen column)
- n_profile_v1_spec.md (cohort foundation), per_minute_universe_spec.md §2.8 (forward-label source), TAXONOMY 2.5 (GRAIN/VECTOR/OBJECTIVE)
- Probe evidence: /tmp/bounce_probe.log (probe-1: axis + A38 + A39 inversion + SCALP sensitivity), /tmp/bounce_probe2.log (probe-2: category-universality, prior does-not-transfer, pooled-with-covariate)
- Foundations: n_profile.parquet sha256 a7ed1155 (ANALYSIS_LIBRARY c76eee5, MANIFEST c9a0f3e); per_minute_features.parquet sha256 9fde4b5d (T37 ckpt-3)

## 8. Resolution log (v0.1 — 2026-05-18)

- Organizing axis = band-free continuous price-level. RESOLVED by probe-1 (bilateral near-degenerate, recorded §5). Not assumed.
- Stratification = pooled, category as level-covariate. RESOLVED by probe-2 (inversion category-universal; operation's ATP_CHALL-tracks-WTA prior does NOT transfer to this axis). Not assumed.
- Dual-metric (A39) = structurally mandatory. RESOLVED by probe-1+2 (cents↔ROI inversion is the load-bearing, category-universal structure — single-metric ranking is wrong by construction here).
- Operational metric = finite-horizon, 30min headline. RESOLVED by probe-1 (A38 saturation ~1.9× confirmed; to-settlement diagnostic-only, firewalled in G3).
- Objective = descriptive-first (Layer-A-equivalent), Phase-2 exit-optimization interface defined not implemented. Operator decision 2026-05-18 (B16 layered-realism staging).
- Second-order ROI mid-trough shape: flagged CHARACTERIZE-don't-assume (B20), measured in §3.2 step 6 / logged §4.2 — not baked into the spec as structure.
- 2026-05-18 ET (v0.2): G2 corrected — v0.1 `time_to_match_start_min < 0` was a spec over-specification inconsistent with the foundation's inclusive `>=` match-start boundary (probe /tmp/g2_probe.log: 0 rows ttms>0; boundary minute regime==in_match ttms==0 by foundation design). G2 now regime-purity only. G1 made phase-aware in the producer (parity vs attempted ticker set, not hardcoded full cohort). Science wiring unchanged + confirmed correct (Phase-1 shape matched probe-1). Probe-confirmed, not assumed.
- 2026-05-18 ET (v0.3): brittle shape-classifier in validation_report fixed (commit 0e94959) — the v0.2 rigid argmin≤1 positional heuristic false-labeled roi-curve NON-MONOTONE / inversion=False because the characterized ROI mid-trough is at bin 14/39; replaced with Spearman rank-correlation sign (the correct monotone-direction measure), inversion judged by opposite ρ signs. Same C38/B20 brittle-classifier pattern as the probe-2 classifier. Surface.parquet UNCHANGED (sha 14241db0 byte-identical proven); report-only fix, regenerated from the frozen validated surface.
- 2026-05-18 ET (LANDED): Phase-2 full-cohort run gate-validated (all 7 gates PASS, surface sha 14241db0, 800 rows, 7369+14==7383, 692,034 in-match minutes; science reproduces probe-1/2: Spearman cents −0.995 / roi +0.722, inversion present). Registered CANONICAL in ANALYSIS_LIBRARY + MANIFEST (this commit). Two-commit provenance recorded: surface built v0.2 85118d4, report classifier-corrected v0.3 0e94959 (surface byte-unchanged). First analytical deliverable on the n_profile_v1 foundation. Phase-2 exit-optimization (§6, E32) is the defined-not-implemented next stage.
