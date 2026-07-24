# Final independent audit — superseding Round-2 Window-1 PRE-RUN

- Audited object: `origin/codex/window1-definition` @ `7667157fa7cb4dce32974025d41ba661a656a354` ("Supersede Round-2 Window-1 PRE-RUN freeze"), sole child of the rejected PRE-RUN `6eecbd1d` and the branch tip at audit time.
- Controlling audit: `audit/window1-independent` @ `fb17a98f` — bound inside the new manifest by path, bytes, SHA-256, and git blob OID (`bd0fdefa…`); OID re-derived on the audit branch and confirmed identical.
- Method: detached read-only worktree pinned at 7667157f; git-blob verification of every receipt; full reading of the v2 instrument (clock partition, admission gate, NO_CALL, evaluator) and the data-binding/freeze scripts; independent recomputation of every headline claim from the per-event receipt rows (not the summary integers); re-execution of the 28 committed tests (pass); and an auditor-authored adversarial fixture campaign (`adversarial_fixtures_v2.py`; receipts committed). No D=804 execution, no scoring, no holdout access, no edits to Codex's branch.

## Gate verdicts

| Gate | Verdict |
|---|---|
| PRE-RUN AUTHENTICITY | **PASS** |
| DATA-BINDING FREEZE | **PASS** |
| COHORT NO_CALL SEMANTICS | **PASS** |
| ZERO-SIZE EXCLUSION | **PASS** |
| POLICY/EVALUATION CLOCK SEPARATION | **PASS** |
| REAL-FAMILY EXECUTABILITY | **PASS** — with the independent order-affecting family count reduced to **8** (see finding R1) |
| CANDIDATE DISTINCTNESS/COMPLETENESS | **FAIL** — retained candidates pass every test; the removal of the four reaim variants fails the duplicate-or-inert requirement (R1) |
| MISSINGNESS/CENSORING CONTRACT | **PASS** |
| METRIC/DENOMINATOR/HOLDOUT FREEZE | **PASS** |
| **ROUND-2 DEVELOPMENT EXECUTION AUTHORIZED** | **NO** — two items (R1, R2), both small |

## 1. Ancestry and immutable freeze — verified

- 7667157f is the **sole** commit after 6eecbd1d and equals the branch tip; parent chain 7667157f → 6eecbd1d → f7cd4209 confirmed.
- All **11** artifact hashes in the v2 `ARTIFACT_MANIFEST.json` and all **24** manifest receipts verify against committed git blob bytes with matching byte counts and blob OIDs (`hash_basis: staged_git_blob_lf` — the CRLF class is closed).
- The data-binding manifest's own receipt (332,562 bytes, SHA-256 `5b97aab2…`, OID `b616c3a7…`) verifies; its `binding_bundle_sha256` is carried into the PRE-RUN manifest.
- The binding covers 16 input records: committed surfaces by blob OID, and the private inputs by content hash — the 804-event ledger (`1f150cf0…`), the normalized public print archive (`e9b5a765…`), the guarded market cache (`aad8d055…`, 804 per-event file receipts, cache key `b85371c8…`), feature flags, own-order lifecycle receipts, and the V5 start ledger — all identical to the hashes frozen in Round-1's v3 manifest, so the data diet is continuous and pre-existing, not rebuilt.
- The runtime validator (`window1_round2_data_binding.py`) hard-refuses: missing/uncommitted repository inputs, changed digests, changed 804-identity or date fence, changed 1,608-leg contract, changed cache file set or bundle hash, and **bound caches containing invalid print sizes** (0 invalid rows found). The instrument itself refuses holdout dates and any non-development date (fixture-proved for 07-24/25/26/23/11).
- D=804, target PC=603, lot 5, and the metric contract are byte-identical to the frozen definitions (C dual exact-five; PC strictly negative combined; S strictly < 100; IC both legs strictly negative).

## 2. Cohort NO_CALL — verified, with the true number

- Every candidate: 694 eligible + 110 censored = **804**, recomputed from the 804 per-event stream receipts (unique event IDs, terminals only `complete_counterfactual_stream`/`censored_feature`).
- All 110 censor reasons are named and lawful: `causal_role` 10 legs (the 5 events with no usable feature row — the same 5 events missing BBO/top-five), `dynamic_recut_cell_unavailable` 127 legs, `top5` 10 legs (censoring only where the profile requires it).
- **The committed NO_CALL count is 1,471, not the relayed 1,741** (and the committed print universe is **2,249,391**, not the relayed 2,240,391 — both relay figures are digit transpositions; the committed artifacts are internally consistent everywhere).
- Grain of 1,471: **per-leg cohort-binding actions**. Exactly 1,608 legs − 127 recut-unavailable legs − 10 role-missing legs = 1,471 legs reach the cohort binding step; each emits exactly one `NO_CALL_UNAVAILABLE` (unique event-leg pairs verified; 777 events touched; max cohort n seen = 15 < 30). It exceeds 804 because events have two legs; no double-counting reaches event classification — eligible/censored counts are byte-identical between cohort-aware and cohort-free candidates.
- Continuation proven two ways: on the real frozen surfaces (fixture: ATP_MAIN leg emits `cohort_no_call` with `underlying_policy_continues: true`, no `feature_censor`, and **still places its order**), and at population level (identical 694/110 across all four candidates).
- NO_CALL never becomes nonfill, censor, zero signal, or rejection — the status is carried in the evidence census only.

## 3. Positive-size causal evidence — verified

- The admission gate (`positive_public_print`) requires receipt identity, `size_verified: true`, finite parsed size > 0, a proved public source class, and no `synthetic_transition`, **before** any fill, divot, flow, orientation, walk, or posture surface. Adversarial fixtures: zero, None, malformed, synthetic, unverified, identity-less, and unproved-source rows are all logged `print_excluded` and trigger nothing, while the lawful control row fires the divot; a zero-size walk-chain link no longer advances the walk (the prior F2 defect is fixed at the code layer, and the bound cache independently reports 0 invalid-size rows).
- Book levels pass a positive-finite-size sanitizer; own resting size subtracts only.
- Deduplication/ordering are enforced at the cache layer (unique trade identity, monotone timestamps — carried from Round-1 v3 validation) and fills consume only prints inside each order's active interval, causally.
- The identical 2,249,391 per candidate is the **shared admitted print universe** (prints are appended to leg state regardless of decisions); it is not forced consumption. Decision volume is far smaller and differs per candidate: place 590/592/590/418, reprice 9,531/5,416/10,388/8,278, cancel 9,734/5,545/10,598/8,375. A per-print attribution of "changed at least one decision" is not recorded in the committed receipts and cannot be derived without re-executing candidates over the bound population (forbidden here); the honest statement is: at most ~20k order actions per candidate are print- or book-triggered against the 2.25M-print universe, and the receipts name per-event action counts. R2 (the scorer supersession) should emit the exact per-print trigger census if the operator wants it.

## 4. BBO/top-five — verified

- Coverage: 799/804 events for every candidate; the 5 uncovered events are the `causal_role`/`top5`-missing censored events — never imputed as zero and never eligible.
- Book observations are causal snapshots; own orders are subtracted (or, when absent, the receipts record zero attributable own volume across all 1,608 legs); own volume cannot confirm any surface (fixture: own-fingerprint print at a fillable price is excluded and never fills).
- Pressure is computed from the top-five levels of the contemporaneous snapshot only and is never described as full depth (`raw_ws_full_depth` remains declared unavailable; no code path reads it).
- Book changes alter real decisions: the recut family witness (BINGIL-class events; `pair_recut` → cancel → reprice) and the pressure witness (AZKLEO, hash-distinct streams with pressure disabled) are on real bound events.

## 5. Policy clock vs evaluation clock — verified

- Candidate code **cannot** read realized-start truth: all eight forbidden fields (`evaluation_real_start_ts`, `strict_positive_cutoff_ts`, `proxy_clock_utc`, etc.) are hard-refused at event validation (fixture-proved field by field); the corridor declaration and anchor-observation ordering are also enforced (mismatches refused).
- Eligibility is `policy_anchor_ts + t_deep_p50×60` — anchored to the timestamped exchange schedule observed before the window (fixture-verified numerically); placement, repricing, cancellation, posture, recut, and sibling timing use only that anchor plus contemporaneous evidence; terminal cancels occur at the declared policy horizon.
- Byte-identical policy streams under different futures: same causal history evaluated twice → identical `stream_sha256`; the ex-post evaluator classifies the same stream `no_inside_window_fill` under an early realized start and `has_inside_window_fill` under a late one.
- Schedule-only truth cannot prove a positive: the evaluator returns `censored_start_boundary` with `positive_window1_proved: false`, and refuses a schedule-only truth that carries a realized start.
- No recognition band leaks backward (T8/T6 proof re-verified in this commit's artifacts; the recognition checkpoint is the only consumer).
- One binding note for the scorer (folded into R2): the committed `evaluate_order_stream` helper classifies against the **raw** realized start; the deterministic scorer must classify lawful Window-1 fills against the **guarded strict cutoff** from the V5 ledger (official−60 s / proxy−900 s / interval−60 s), which is where the mandated metric law lives. The helper is explicitly score-free, so this is a requirement, not a defect.

## 6. Real-family capability — verified, count reduced to 8

All nine claimed witnesses are on real July-12 development events inside the bound 804 universe (ALVVAN, AZKLEO, TABHUE, BINGIL), each an isolated-family-disable contrast on identical causal history with differing decision hashes, `scored: false` everywhere. Asynchronous timing (eligibility change), leg posture (price 55 vs touch), one-cent walk (reprice +1¢), pair recut (cancel/reprice on cell change), orientation (depth change), drift recognition (T6 repricing), true-print flow (placement gating), and BBO/top-five pressure (depth +1¢) are all **order-affecting** on real inputs.

**R1 — the ninth family, `first_fill_sibling_response`, is order-inert in the retained grid.** The capability harness counts `sibling_hold` in `DECISION_ACTIONS`, and the witness (AZKLEO, 28 vs 27 decisions) is exactly the presence of the sibling-hold bookkeeping record — no order price, time, cancellation, or eligibility changes. With every `reaim` variant removed, **no retained candidate can change any sibling order after a first fill**. The independent order-affecting family count is therefore **8**, and the dedup rationale "hold retains executable first-fill sibling response" is misleading as written. Honest non-coverage declarations (cohort NO_CALL, own-subtraction inert with zero attributable volume, start boundary evaluation-only) are correctly not counted.

## 7. Candidate completeness and the removal test

- The four retained candidates emit complete two-leg counterfactual streams (leg_open → terminal on all 804 events each), independently timed per leg, generated — never reclassified history (no historical-order path exists in the v2 instrument).
- Pairwise distinctness verified from committed per-event decision hashes: all six pairs differ on 324–486 **real** events; no candidate exists only on synthetic fixtures; `duplicate_candidate_groups: []` confirmed.
- Exclusions upheld: Pinnacle, full depth, shape (no independent non-AIM mapping), the uncommitted sealed-pair object, and the riser are declared unavailable and have no code path; no undeclared parameter search (free numeric parameters: zero; the handful of in-code constants — orientation 0.65/0.35/n≥10, purity 0.5, divot fallback age — remain hash-bound and unchanged from the rejected freeze).
- Removals: the two `r2_full_os__park_join__*` removals are **genuinely structural duplicates** (walk is unreachable under park_join; capability data confirms walk actions occur only under walk_park). **The four `__reaim` removals fail the mandated duplicate-or-inert test**: reaim variants are neither — the v1 capability proof and my prior fixtures showed reaim changes the sibling's order by exactly +1¢ at its own trigger, and Round-1's ablation showed the sibling response was the largest completion lever (C 10→6). No committed evidence shows the removal was outcome-informed (the campaign computed no costs or deltas, and fills were equally visible for retained candidates), but the stated rationale is not true of orders, and the mandate requires removed candidates to be duplicates or inert. This is R1's other half.

## 8. The capability campaign itself — verified clean

Bound July 12–20 categories only (all nine dates observed, no others); zero holdout presence in any input; witnesses replayed from the real bound population, not proof-script fixtures (the synthetic-surface capability proof of the rejected freeze was replaced by `window1_round2_actual_family_proof.py` over real events); `metrics: null`, `candidate_scoring_performed: false`, `performance_ablation_performed: false`, `tuning_performed: false` throughout; selection (dedup) used decision-stream hashes, not fills or outcomes.

## Authorization: NO — two items, both small

**R1 — restore the sibling-response actuator or re-rule its removal.** Smallest exact correction: one supersession commit restoring the four `__reaim` candidates to the frozen allowlist (an 8-candidate grid; the campaign machinery regenerates their capability rows mechanically), and correcting the family matrix to mark `first_fill_sibling_response` order-affecting via reaim (8 order-affecting families under hold-only grids). If Codex instead insists on a 4-candidate grid, it must commit an explicit ruling that names the removal as a pre-scoring design law, concedes the family count is 8, and accepts that the grid cannot express the Vault's completion response.

**R2 — commit the deterministic scorer before execution.** `scoring_implemented: false`: no scoring runner is frozen, so a compliant execution would require post-freeze code — an open surface. The same supersession commit must add the scorer, hash-bound in the manifest, implementing the frozen metric contract verbatim with lawful Window 1 = the V5 guarded strict cutoff (not the evaluator helper's raw start), the corrected Round-1 census classes (genuine_zero_fill / naked_single_leg / zero_length_window / censored / contradictory), and conservation to exactly 804.

Everything else — ancestry, receipts, data binding, NO_CALL semantics, positive-size gating, clock separation, missingness, metric/denominator/holdout freeze, campaign hygiene — **passes**, and all four blockers from the controlling audit (F1 cohort, F2 zero-size, F3 unbound data, F4 realized-start anchor) are **verified fixed**. After the single R1+R2 supersession commit and a short delta audit (ancestry + new receipts + scorer review), Round-2 execution can be authorized at that new SHA.

Relay corrections for the record: the true committed figures are **1,471** cohort NO_CALLs per cohort-aware candidate (not 1,741) and **2,249,391** positive-size prints per candidate (not 2,240,391); the committed artifacts are internally consistent.

No edits were made to Codex's branch. No scoring, tuning, performance ablation, D=804 execution, or holdout access occurred. No production, live, order, position, configuration, Window-2, exit, settlement, or DCA surface was touched.
