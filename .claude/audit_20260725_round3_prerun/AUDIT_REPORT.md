# INDEPENDENT ROUND-3 PRE-RUN AUDIT @ 14e0e846 — NO SCORING, NO EXECUTION

**Status: AUDIT COMPLETE. ALL SEVEN GATES PASS. EXECUTION NOT AUTHORIZED — nothing executable exists yet by design; an additions-only execution package is the required next step.**
Date: 2026-07-25 · Branch: `audit/window1-independent` · Auditor: independent CC session
Method: detached read-only worktree at the PRE-RUN; every number recomputed from committed artifacts and git blobs; synthetic-free verification (frozen streams only); zero scorer/instrument scoring invocations; holdout untouched; no live/production access.

**Identity flag:** the tasking's PRE-RUN SHA (`14e0e846e892cda98f656aeef1f43d2c48da96ee7`) is 41 hex characters — malformed. The actual commit is **`14e0e846e8922da98f656aef1f43d2c48da96ee7`** ("Freeze Round-3 Window-1 forensic PRE-RUN"), resolved unambiguously: sole child of `10ac6dbc`, remote tip of `codex/window1-definition`, matching subject. All findings refer to that commit.

## 0. Prior art (C45 gate)

Prior art: `807e2c86` (controlling final-results audit — all 8 Round-2 candidates PC=0, 82 single-leg fills, partner-starvation hypothesis), `c94d4e50` (Round-2 execution authorization), `2ac4a2f4` (grid1 forensic), memory `project_window1_osfamily_audit` (Round-1: miss = instrument ceiling). Delta: first audit of the Round-3 forensic + score-free PRE-RUN.

## Gate 1 — Ancestry and scope: PASS

- `14e0e846` parent is exactly `10ac6dbc` (the audited Round-2 results commit); children-scan across all refs shows it is the **sole child**; it is the remote branch tip.
- The diff is **exactly the 20 claimed additive files** (7 forensic, 7 PRE-RUN, 4 analysis sources, 1 candidates contract, 1 test suite); zero modifications or deletions — all Round-2 artifacts and frozen surfaces are byte-identical by construction.
- Manifest: D=804, target_PC=603, metric contract `unchanged_from_round2: true` (C = dual exact-five in guarded W1; PC/S/IC definitions verbatim; 60s official / 900s proxy guards), dev dates 07-12…20, sealed holdout 07-24…26, `prohibited_surface_changes: false`, `holdout_opened/queried: false`, `live_or_production_access: false`. It binds the Round-2 results commit, my controlling audit `807e2c86` **and its report blob OID `9bb51a3d…` (verified against git)**.

## Gate 2 — Root-cause forensic: PASS — the starvation forensic is trustworthy

Recomputed entirely from the committed Round-2 grid2 ledgers (not the forensic's own numbers):

- **82 lawful Window-1 fills** — exact match.
- **60 stranded candidate-event rows** — exact match; all 60 (candidate_id, event_id) keys, filled-leg identity, quantity, VWAP, first-fill timestamp, receipt count, and sibling-leg identity match grid2's naked_single_leg rows **field-for-field with zero mismatches**.
- **Categories: mutually exclusive** (single scalar category per row), **exhaustive** (sum 60, no `other` rows used), and aggregate exactly to the claimed census: **16 sibling-never-called, 16 reaim-armed-without-later-trigger, 16 eligibility-began-after-cutoff, 4 partial-fill-response-not-armed, 8 cutoff/policy-horizon** (composite of 4 sub-causes, 2 each).
- **Causal receipts**: every row carries eligibility/boundary/horizon timestamps, place/divot/reaim counters, and reach evidence; category-specific invariants (e.g. eligibility ≥ cutoff for the after-cutoff class; zero divots and zero placements for never-called; armed>0 with zero triggers for reaim-without-trigger; 0<qty<5 for the partial class) hold on **all 60 rows with zero violations**.
- The four Round-2 reaim candidates changed real orders on **327 events** (91+85+87+64 — matches both the grid2 comparison and the 327-row difference ledger) and completed **zero** pairs.
- **No arithmetic, classification, or causality disagreement found.**

## Gate 3 — Full-OS reconciliation: PASS

`OS_LINEAGE_RECONCILIATION.md` (hash-bound) adjudicates every lineage mechanic against the Living Vault, whose exact committed blob (plus LIFECYCLE, DAILY_STANDARD, OPERATOR_CONSTRAINTS, MODEL_REGISTRY) is pinned in the manifest — I verified the pinned blob OIDs are exactly the branch's committed docs (the recorded sha256s are CRLF disk-basis over those same blobs; equivalence proven). Cross-checks against the Vault text:

- **Pair law / asynchronous per-leg timing / first-fill sibling response / touch-join-park / walk-park / divot lineage / drift-cohort-orientation steering / dynamic recut cells / true-print + BBO/top-five / queue preservation / content-bound own-order receipts** — all present in the instrument as real order-affecting machinery (action vocabulary and code verified; see Gate 4). The Vault's JOIN/IMPROVE law ("join it or improve by EXACTLY 1¢") is now implemented (Round-2's join was adjudicated nominal/miswired — named, and repaired). The Vault's queue law ("the bid HOLDS its queue position — never a cancel/repost cycle") is the instrument's `causal_book_updates_cell_queue_held` / `reprice_refused_current_queue_preserved` behavior. The Vault's dip/aim doctrine (aim = size-backed dip, FV-gate refuted and superseded by the Vault itself) is the divot-targeting lineage; FV-anchor omission is Vault-*compliant*, not a gap.
- **Disclosed unavailable surfaces, censoring only their dependents:** cohort (all cells n<30 → `NO_CALL_UNAVAILABLE`, 5,884 named no-calls), Pinnacle, proved full depth, independent shape mapping, schedule-revision chain, and — the one Vault-authorized *decision-changing* component not bound — the **sealed dual-divot pair-policy object (`state/pair_policies_sealed_v1.json`)**, which the spec names explicitly and refuses to proxy ("Older entry-surface tables are not substituted for it"). That is a disclosed limitation, **not a silent omission or proxy**. No silently omitted, proxied, or merely nominal decision-changing component was found.

## Gate 4 — Causality and execution mechanics: PASS

Code-verified in the frozen instrument, each backed by a dedicated test (suite: **20/20 pass**, 0.22s, zero scoring):

- Maker presence begins at each leg's **own first lawful positive-size causal BBO** after policy activation (`first_positive_size_bbo_independent_presence`); legs are independent.
- **t_deep is advisory only** — it appears solely as `advisory_tdeep_ts` receipt fields with `advisory_tdeep_is_hard_gate: False`; no eligibility path reads it.
- **No lookahead**: decisions consume only data at or before the decision timestamp; policy code cannot read realized-start truth (`test_policy_truth_and_holdout_are_hard_refused`); streams are byte-deterministic and never scored.
- **Recuts require receipt-identifiable positive-size prints**; zero/null/malformed/synthetic/duplicate/receipt-less transitions contribute zero to every surface (dedicated tests, incl. zero-size walk chains).
- **Queue preserved** unless new causal evidence permits a change: book updates refresh latent cells but hold queue; reprices refused when only bookkeeping changed.
- **Any first positive fill — including partial — arms exactly one later sibling +1 response**, activated only at that sibling's own strictly-later lawful print trigger and subject to maker/band/positive-price/par/pair-cost/max-cost guards; missing evidence is a named NO_CALL (1,313 `sibling_reaim_no_call` rows), never a censor of the underlying leg.
- **Content-bound book receipts with duplicate exclusion** enforced (219,832 `book_excluded` rows for missing/duplicate identities; same-timestamp distinct-content books get distinct receipts).
- **NO_CALL and censoring never become nonfills or fabricated orders**: censored events are named with per-leg missing features; **zero legs contain any real decision after their censor timestamp** (verified over all 880 censored streams); pre-censor lawful decisions are preserved, not retroactively erased.

## Gate 5 — Candidate distinctness on real inputs: PASS

All recomputed from the frozen streams (git blob), not the summary files:

- **Eligibility: exactly 694 eligible + 110 censored for every candidate**; the 110 censored events are the identical named set across all eight (and are the same 110 feature-unavailable events known from Round 2).
- **All 28 candidate pairs are behaviorally distinct on real order decisions** (place/reprice/cancel signatures): minimum 269, maximum 777 differing events per pair; zero identical pairs; the 4,183 committed first-difference witnesses all show real decision differences.
- **Reaim later-sibling order changes recomputed: 322 / 269 / 291 / 278** (pair_presence-park_join, pair_presence-touch_park, causal_steer, full_os) — event sets exactly equal the committed proof ledger; total **1,160**.
- **All 1,160 +1 proofs independently re-derived with zero problems**: earlier real decisions byte-identical between hold and reaim (recomputed lists AND recomputed SHA-256s match), an actual `reprice` action exists at the sibling's later lawful trigger (strictly after the first-leg fill), priced at **exactly base + 1 cent**.
- **These are actual order-changing differences, not bookkeeping**: on the 804−N non-applied events of each pair, real-decision signatures are **identical** (all differences there are annotation rows only), and no synthetic fixtures or renamed duplicates exist — every stream is bound to the real frozen market caches and the D=804 identity.

## Gate 6 — Data binding and freeze: PASS

- **All 13 artifact receipts** (forensic + PRE-RUN files) reproduce: sha256, byte count, and git blob OID each verified against the commit.
- **All 19 source/contract receipts** verified (the 5 governance docs bind the exact committed HEAD blobs; their recorded sha256/bytes are over CRLF disk reads of those same blobs — equivalence proven, noted as a receipt-basis quirk, not a defect).
- **All 6,432 stream receipts** verified three ways: manifest receipt = embedded stream hash = my recomputation of `sha256(canonical(order_stream))`; receipts-list canonical hash matches `candidate_event_stream_receipts_sha256`; zero truth leaks (`scored:false`, `metrics:null`, `holdout_queried:false`, `evaluation_truth_present:false` on every stream).
- Frozen inputs: event ledger `1f150cf0…` (unchanged from Round 2, D=804, 1,608 legs), market cache aggregate `aad8d055…` (804 files, unchanged), leg-identity hash bound. The frozen inputs contain everything the retained policies require; unavailable surfaces (Pinnacle, full depth, shape, schedule revisions, cohort coverage, dual-seal object) censor or NO_CALL **only their dependent feature** — required-feature absence censors the event for the dependent candidate *from the censor point only* (zero post-censor decisions), and optional-module abstention (cohort 5,884, feature 40, pair-cost 16, reaim 1,313) never touches the underlying pair orders.
- **July 24–26 sealed**: zero holdout rows in any input census, streams span 07-12…20 only, `holdout_opened/queried: false` throughout. No Window-2, exit, DCA, settlement, live, or production surface appears anywhere in the 20 files (all paths are `.claude/window1_round3_*` + analysis/tests/docs-research).

## Gate 7 — Execution readiness: PASS as a PRE-RUN; NOT yet executable — separate package required

- The **candidate surface is complete and hash-bound**: 8 candidates in frozen order, closed numeric surface (`free_numeric_parameters` empty), 6,432 frozen streams with receipts, candidates contract + spec + capability censuses committed. The spec forbids adding candidates after this PRE-RUN, and the frozen stream receipts make any post-hoc alteration detectable — **no candidate can be added, removed, or altered after seeing results**.
- Progress/failure handling and one-attempt refusal laws exist as proven Round-2 machinery (stdout-safe runner), **but no Round-3 execution instrument exists yet**: the manifest deliberately records `benchmark_execution_authorized: false`, `execution_id: null`, `benchmark_execution_command: null`; there is no Round-3 grid runner, no scorer binding to the r3 streams, no execution package, and no validation receipt.
- **Determination: a separate additions-only execution package is still required** — a Round-2-style deterministic runner bound to these frozen streams and the unchanged scorer/metric contract, a scoring input bundle with a new execution ID and result directory, a validate-only receipt, and a superseding PRE-RUN commit.

## Plain answers

- **Gates:** 1 PASS · 2 PASS · 3 PASS · 4 PASS · 5 PASS · 6 PASS · 7 PASS (as a score-free PRE-RUN; execution package outstanding by design).
- **Is the starvation forensic trustworthy?** Yes — every number recomputes from the admitted Round-2 ledgers, the 60 rows match field-for-field, the five categories are mutually exclusive, exhaustive, and invariant-clean, and the 327-changed-events/zero-pairs claim reproduces.
- **Does Round 3 actually repair the demonstrated partner-leg chain?** Yes, mechanically and category-by-category: independent first-BBO pair presence addresses the 16 never-called and 16 eligibility-after-cutoff strandings (presence no longer waits for a divot or a fitted t_deep gate); partial-fill arming addresses the 4 partial-not-armed; the advisory-only t_deep plus presence-at-activation address the horizon strandings; and the reaim later-trigger response is retained as a real, guarded, exactly-+1 order change with 1,160 byte-identical-prefix proofs. Whether the repair *fills* is exactly what one deterministic execution must measure.
- **Remaining proxy/wiring/evidence/candidate-distinctness blockers:** none found. One disclosed, non-proxied gap (sealed dual-divot pair-policy object unavailable in this research checkout) and one receipt-basis quirk (CRLF sha256 basis on the 5 governance-doc receipts; blob OIDs exact) — both named, neither blocking.
- **Is execution authorized?** **No — NOT AUTHORIZED**, because there is nothing to execute: this PRE-RUN intentionally freezes the candidate surface without an execution instrument. No scoring may run against these streams until an execution package exists and passes independent audit.
- **Smallest exact correction (next step):** construct the **additions-only Round-3 execution package** on top of `14e0e846` — deterministic stdout-safe runner bound to the frozen r3 streams, unchanged scorer + metric contract, new execution ID and result directory, validation-only receipt, one-attempt/overwrite-refusal laws — then submit that superseding PRE-RUN for independent audit before any execution.

The malformed SHA in the tasking should be corrected in the record to `14e0e846e8922da98f656aef1f43d2c48da96ee7`.
