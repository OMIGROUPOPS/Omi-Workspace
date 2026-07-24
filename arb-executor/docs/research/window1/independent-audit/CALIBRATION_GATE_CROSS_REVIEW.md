# Independent cross-review — Window-1 execution calibration gate

Reviewed commit: `34ba125e77f5d66609fec1b4f44fdccf6ddeb90b` ("Add Window-1 execution calibration gate", codex/window1-definition, 2026-07-23 19:21:04 -0400).
Review date: 2026-07-23. Read-only; no Codex files modified; no scoring, tuning, or candidate work performed.
Method: four independent verification passes recomputing every gate claim from the committed JSONL ledgers and the immutable evidence (prints.jsonl, ws_depth archives, private-export hash receipts), full — not sampled — where feasible.

## Verdict: GATE PASS is justified. All four subgates PASS.

| Subgate | Verdict | Basis |
|---|---|---|
| historical_execution_replay | **PASS** | 258/12/870/468 partition recomputed exactly from the 1,608-row ledger; mutually exclusive, exhaustive; 0 duplicate leg identities; 2 legs per each of 804 events; repost collapse verified at both grains (order→lineage, lineage→leg); 0 replay mismatches; mismatch ledger genuinely empty (empty-file sha256). |
| real_start | **PASS** | 29+79+625+71 = 804 recomputed; boundary-censored = 775 = 804−29; zero schedule-only promotions verified three independent ways (null exact_start on all 71; no schedule-only-evidence row classed higher; no schedule-only row holding accepted non-schedule evidence); field-level identical to the frozen prior ledger (0 mismatches over 804 rows). |
| causal_market_data | **PASS** | Full recompute: 4,836,462 rows / 4,836,462 positive-size / 4,836,462 distinct trade_ids / 1,606 tickers; file sha256 reproduced (`e9b5a765…fabb55`). All 215 WS archives re-read (282,398,961 physical rows): 3,322,756 required trade rows, 3,322,756 unique identities, 3,322,756 exact public-tape matches, 0 mismatches of any type; the 2 zero-trade tickers re-derived independently (`…26JUL19KRUCAS-CAS`, `…26JUL19SALVRB-VRB`); 28 corrupt archives byte-identical to the named censoring list and MD5-verified against the Spaces manifest (corrupt at origin, not in transit). No full-depth claim anywhere; kernel consumes no ladders; gate hard-requires `raw_ws_full_depth == unavailable`. |
| full_os_research_adapter | **PASS** (with caveats C1–C2 below) | All 20 components present; status counts 5/13/1/1 as claimed; all 47 source receipts sha256-verified against disk, 0 mismatches; every classification honest against the Living Vault and disk ground truth (Pinnacle unavailable, bookmaker partial at 844/6,432 rows and 128/804 events, full depth unavailable, top-5 "partial" is the conservative feature-row-grain call); AIM_V2 actuator exclusion code-asserted. |

Artifact integrity: all 9 hashes in `CALIBRATION_GATE_SUMMARY.json.artifact_hashes` match disk. `CAUSAL_TAPE_RECONCILIATION.json` is pinned via `CALIBRATION_EVIDENCE_MANIFEST.json` (chain intact).

Tests: the claimed **34 targeted passes reproduce exactly** (the 5-file suite in EXECUTION_CALIBRATION_CONTRACT.md: 34 collected, 34 passed; the 3 new test files alone contain 8 of them). The **2 broader pre-existing failures reproduce** and both provably predate this commit (`git diff 101742e4 34ba125e` empty over the implicated files): (1) `test_window1_policy_runner` ablation-family rename crash — deprecated scorer, fails loudly, cannot mask calibration; (2) `test_window1_recovery_manifest` stale hash receipt for `POST_SAMPLE_MICMAY_FORENSIC.json` (manifest frozen at 95a02afd, file republished at 5f8dfb6f) — unrelated to calibration inputs, but a live instance of receipt drift that should be fixed, not skipped.

## Resolved question: 47 vs 42 unattributed private-fill lineages

Both numbers are true at different grains and both appear in `LIFECYCLE_VALIDATION_SUMMARY.json`: **47 unattributed private buy-fill rows collapse onto 42 order lineages** (37 lineages × 1 fill + 5 × 2). The gate report's 42 is the lineage grain. All 42 map 1:1 into the 468 censored legs (`private_fill_lacks_entry_lineage`). Unchanged since commit 0cf2f7bd.

## Receipt reconciliation (verified)

3,360 accepted orders across 1,041 lifecycles − 42 receipt-less unattributed = **3,318 attributable placements**; +14 failed attempts = **3,332 validated**. **338 official fill receipts** = 291 on the 270 filled legs (partial fills: 250×1, 19×2, 1×3) + 47 on the 42 censored unattributed lineages — so 338 does not divide into 270 directly. **3,574 cancellation receipts** = 3,371 successful + 203 unsuccessful attempt receipts; per-attempt counting and multi-receipt orders (one 180-repost lifecycle carries 358 successful cancel receipts) explain cancels > placements. **308 causal nonplacement receipts** confirmed (`EXECUTION_REPLAY_SUMMARY.json`, 308 unique decision_ids), covering 284 zero-lifecycle exact-nonfill legs. Note: only the 3,371 successful-cancel count is recomputable from committed artifacts; 3,574/203 rest on the private inputs' hash receipts.

## The 31 duals / 27 under par (verified, with the material negative stated)

31 events with both legs exact-five recomputed; 27 strictly under 100¢ (3 at exactly 100, 1 at 101). All 62 legs: quantity exactly 5, non-null VWAP, zero mismatch flags. Correctly labeled historical witnesses: `metrics_not_evaluated` covers C/PC/NC/IC/X and no candidate fields exist in any ledger row. Dates: 07-13 ×2, 07-14 ×12, 07-15 ×6, 07-17 ×7, 07-19 ×2, 07-20 ×2; none on 07-12/16/18.

**D1 (must accompany the number): all 31 sit on `causal_live_by_bound` events.** Window-1 timing is provable for none of them; the prior boundary instrument ruled all 62 legs start-boundary-censored (proven-W1 C = 0). The gate report correctly avoids claiming W1 capture but does not print this negative beside the 31/27. Any downstream citation of "31 duals, 27 under par" must carry the qualifier "W1 timing unproven."

Nine banked duals: a different population by construction — the 07-16 pair-law census over an 80-game slate (9 pair-complete, only 8/9 at 5-lot both legs, identities private, slate includes non-D games). Overlap with the 31 is not computable from committed artifacts; notably the replay shows zero duals dated 07-16. No contradiction; do not merge the populations.

## Exact disagreements with Codex (none gate-breaking)

1. **D2 — the 79 "causal interval" class is heterogeneous and the summary hides it:** 32 of 79 intervals are contradictory (lower bound after upper bound) with no safe pre-start cutoff. Definitely-prestart-scorable events = **76** (29 exact + 47 clean intervals), not 108. The next replay's provable-C universe is 76 events (prior possible-C ceiling 240).
2. **C1 — AIM_V2 tension:** the actuator exclusion is genuine and code-asserted, but the pinned fit instrument's shape prior (`aim_v2_operational_LATCHCAL.json`, sha `6183ddec…`) is byte-identical to the file receipted under the adapter's *excluded* aim_v2 component, and it drives per-cell resting aims in `window1_fit_benchmark.py` (`shape_context`/`shape_cell_offset`). Disclosed in WINDOW1_SPEC/REPRODUCTION; invisible from the adapter alone. State it wherever "AIM_V2 excluded" is claimed.
3. **C2 — proxy-substitution protection is contractual, not mechanical:** the shared execution kernel is enforced in code (the fit runner's inline simulator was deleted and delegated), but `window1_fit_benchmark.py` contains no adapter-version binding and no policy allowlist; `walk_law`/`touch` remain executable rules, and the only guard is an incidental crash if the causal policy is absent from the spec — it forces presence, not selection. `silent_proxy_substitution_allowed: false` is a stamped constant.
4. `schedule_fields_consumed: false` is a hardcoded constant in the kernel — true (the replay path references no schedule field) but tautological as a receipt.
5. `classify_leg` (window1_boundary_validation.py) defaults a filled-five leg with a missing completion clock on a safe-cutoff event to `exact_post_start_noncompletion` — a proven negative from absent evidence. The next instrument must assert non-null clocks before emitting that ruling.
6. Bookkeeping: `CAUSAL_TAPE_RECONCILIATION.json` absent from `artifact_hashes` (pinned only via the evidence manifest); evidence-manifest entries carry `path_included: false` (hash-only lookup); corrupt-archive `error_class` recorded as the literal string "error". Normalize, non-blocking.
7. One `exact_filled_other_quantity` leg has quantity 10.0 (overfill) — correctly classed, but "other quantity" includes overfills, not only partials.

## Blocking defects before the deterministic 804-event replay

**None.** The gate is sound for its declared scope. Four conditions attach to the next run (from the findings above): (i) bind the adapter version and an explicit policy allowlist mechanically in the fit runner, or predeclare the candidate-spec sha256 in the run's freeze receipt before execution; (ii) fix or explicitly assert around the missing-clock default in `classify_leg` (D5-class rulings must require non-null clocks); (iii) print the D2 decomposition (29 exact + 47 clean-interval = 76 provable-C events; 32 contradictory intervals censored) in the replay report; (iv) the replay must consume the private exchange fill clocks (they exist and reconcile at mismatch 0; published ledgers null them).

## Frozen input pins and metric contract for the next run

Inputs (from `CALIBRATION_EVIDENCE_MANIFEST.json` / `CAUSAL_TAPE_RECONCILIATION.json`, all verified this review):

- events: `1f150cf0e4e4a5809617c2b9303d5f1cf64b22d182d996ff893de255e6e48b46` (336,694 B)
- public true-print tape: `e9b5a765b51ddbf0d65364c4f38744ad949ca3c675e5b3a0e472392fbcfabb55` (4,836,462 rows; manifest `d2a3bd4b156f312fce3bbb8a8875114904ac39f2ed5b36801799d9a905e4d575`)
- ws summary: `b512360d1082354b61af5a9c3daa9c6968643940d2f0f185b53bc193ec265fa2`; tape reconciliation: `bb42302887ebdd3b8391cab631edc62ffb90dcb42a10223e698d2133b683f35a`
- real-start ledger: `90a943b598baa8debe1acd08fa4b664d3661cd3762c2e5ab54e54d781819b947`; summary: `de47ef5200d98772212e05fd8b81be9a2a5c0df13cdb32d5eb8c38610940d6cc`
- expected legs: `52dfe9dfbb8a414b16ccd93ae0b136c7f980df0109d3cefa1167204d97121f5e`; expected execution summary: `bfec8d5063a90052ccd46d0ef6207df11b7851f725c22d67fd8ff2f2e6e09ea0`
- decisions: `38cf05ee2649c628299577f5d793bf541b9813973f3094efc25d4f1b7ee6ac1f`; feature coverage: `ad733270a5c3f4222370816fcb57391efba36f233ec6201fa69c1ebe561ca040`; source coverage: `231a6ae056d232c7e203cc8c7e7614a0ab6892b38b12d10fdb58f3a0122772df`; os contract: `02c58d259442b7c35798a68c30acb7ee0debb61e91184b30c6ba772872650396`
- private (hash-receipted, outside git): fills `76e7830f…32f335`, orders `707375e7…d19912`, lifecycles `897195b5…de3356`
- code: kernel `cd921003f68f993bd8185d5e2413cde9983167be50b7ae8c0dd148b1a9e18893`, calibration runner `e6ac696b46db6d4284fd1b3d92642cb721afaa8b2b3509b4efbc70bc313635ed`, ws reconciler `3b6c6b24dad36bdc25b77c5f312e2684f397feaade3a434cf59b7d178ff26ee9`, fit runner `c587ea02055aced7b3b72f1c7eeea62dd9b6f03f38ceea66355ab7c57939c34d`
- adapter: `cc137a5ed4b0218587e64c43da0572a2fa9a4ca1c4e32e02e36ec992d79cf3fe` (WINDOW1_OS_RESEARCH_ADAPTER.json)

Metric contract (per the gate's own stop law plus this review's conditions): one deterministic, predeclared corrected-instrument replay over all 804 development events, one fixed adapter version, one fixed execution kernel; report C, PC, NC, IC, X, the dynamic-floor gap, and per-leg dip/catch separately; decompose C-eligibility as 76 provable / 728 boundary-censored; no tuning, no ablation, no holdout inspection, no shrinking of D; censored counts carried, never dropped. The Jul 24–26 forward holdout remains unopened and untouched by this review.

— Independent cross-review (Fable seat), read-only; scratch recomputation artifacts retained outside git.
