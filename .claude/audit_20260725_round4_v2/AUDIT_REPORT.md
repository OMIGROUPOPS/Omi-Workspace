# INDEPENDENT ROUND-4 PRE-RUN V2 AUDIT @ 781b6d6f — PASS (mechanical V2 correction closed; scoring NOT authorized)

**RULING: PASS.** The V2 overlay implements exactly the Item-5 amendment (`abe543e3`) and the 100¢ removal, and nothing else. This PASS closes only the mechanical censor/100-cent correction. **It does not authorize scoring or any execution package**: the separately identified last-trade/chain and macro×micro composition omissions remain outside this audit and require their own PRE-RUN reconciliation before any benchmark is considered.

Date: 2026-07-25 · Branch: `audit/window1-independent` · Auditor: independent CC session
Method: detached clean worktree at `781b6d6fac65381a67f74a177478947bfd804dc8`; no implementation, tuning, scoring, benchmarking, ranking, holdout, or live/production access; all comparisons against git blobs; regeneration into a fresh temp directory.

## 0. Prior art (C45)

`84cdf87a` (Round-4 V1 audit — BLOCKED on the five causal_role-censored events + inert 100¢ fields), `abe543e3` (Item-5 amendment — presence on the five events proven impossible; authorized repair = named NO_CALLs + zero placement + D membership). Delta: first audit of the V2 PRE-RUN implementing that exact repair.

## 1. Git lineage and scope — PASS

`781b6d6f` ("freeze amended Window-1 Round-4 pre-run v2") has parent exactly `4f653446`; all-refs children scan: **sole child**; remote tip of `codex/window1-definition` verified. The commit is **additions-only: exactly 26 added paths, zero modifications/deletions** — no inherited V1 source byte changed. The overlay (`window1_round4_instrument_v2.py`, 201 lines) subclasses the V1 instrument and overrides only: `_new_state` (causal_role censor → named NO_CALL), `_posture`/`_target_price` (neutral join-external-best-bid fallback, lawful-BBO-required), `_terminalize` (market-evidence NO_CALL terminal), and the spec loader/policy (100¢-field rejection). `headroom_b2_max`/`strict_pair_budget` are re-exported from V1 unchanged. The V2 spec changes only availability contracts and parameter removal; candidate IDs, profiles, fill contract, and headroom contract are unchanged (`fill_or_headroom_law_changed: false`, `candidate_ids_changed: false` in the supersession receipt — corroborated by code diff and stream identity below). **No unrelated macro/micro strategy change entered this commit.**

## 2. Item-5 semantics — PASS

Evidence census independently reproduced (this same day, against the identical pinned caches — aggregate `aad8d055…`, byte-identical at this commit by additions-only lineage): **all ten legs lack any lawful positive-size external BBO inside the policy window**; KRUCAS/TAUTOM/PUTJEA/KUDKOR have zero prints and zero snapshots entirely; CREMAT's 2,303/3,044 snapshots all fall outside the window and its **7/4 in-window prints are executions, not BBO authority**. In the V2 streams for all ten changed candidate-events:

- No print is substituted for a BBO and no price is fabricated (explicit per-row flags `print_substituted_for_BBO: false`, `fabricated_price: false`).
- No never-marketable claim without an ask: `_target_price` raises unless **both** a lawful external bid and ask exist (maker ceiling = ask−1).
- causal_role absence produces the named steering NO_CALL `causal_role_unavailable_role_specific_steering_disabled` (`NO_CALL_UNAVAILABLE`, steering disabled, role not inferred) — on both legs of all ten streams.
- Missing BBO produces the named market-evidence NO_CALL `lawful_positive_size_external_bbo_unavailable_no_order` with `placement_created: false` and `D_membership_continues: true` — on both legs of all ten streams.
- **Zero placements on all ten legs** (no place/reprice actions anywhere).
- All five events remain members of D=804 (`actionable_event_count_by_candidate = 804` for both candidates), and their terminals are **non-censored `complete_counterfactual_stream`** with per-leg terminal `market_evidence_unavailable_no_call`. The committed FIVE_EVENT_PROOF matches (2 role NO_CALLs + 2 market NO_CALLs + 0 placements per stream).

## 3. Stream identity — PASS

Exactly **1,608** candidate-event streams; key set identical to V1. Full-row comparison against the V1 frozen streams: **exactly 10 changed** — the five named events × two candidates, no others — and **exactly 1,598 byte-identical** (**799 unaffected per candidate**). Stream hashes independently recomputed over all 1,608: `sha256(canonical(order_stream))` matches every embedded `stream_sha256` (0 mismatches); all 1,608 stream receipts match (0 mismatches). The committed V1↔V2 identity receipt's claims (10 changed / 1,598 identical, amendment-bound, `scored: false`, `metrics: null`) match my recomputation exactly.

## 4. D and metrics — PASS

D = 804 and actionable population = **804 per candidate** (membership no longer conflated with maker placement — the five no-evidence events are members with zero orders). `all_metrics_null: true`, `C_PC_S_IC_populated: false`, every stream `scored: false` / `metrics: null`; no scorer or benchmark imported or invoked (grep across all four V2 modules: zero scorer imports; diagnostic receipt `scorer_invoked: false`); no ranking or selection (`benchmark_execution_authorized: false`, execution inventory `execution_id/command: null`).

## 5. Stale 100-cent fields — PASS

`first_fill_sibling_max_combined_cost_cents` and `maximum_pair_order_cost_cents` are **absent from the entire V2 candidate spec** (string search over the full JSON: zero occurrences) and absent from runtime policy parameters. The only code occurrences are the `FORBIDDEN_INERT_PARAMETERS` assertions in `load_candidate_spec` and `candidate_policy`, which **raise** if either field appears — occurrences that prove rejection, as required. Combined with the V1 audit's perturbation/removal proof (byte-identical streams), neither value can affect any decision. `pair_cost_gate_enabled` is a spec declaration consistent with the V1 diagnostic-only `_pair_cost_passes`.

## 6. Inherited execution law — PASS

The V2 overlay overrides none of the fill or headroom machinery: cumulative positive-size executed-print primary fills at limit-or-better; queue/depth strictly a labeled diagnostic (`alters_primary_fill: false`); no queue or five-displayed gate; no strict trade-through; no IC gate; no S/combined-cost gate; exact-five first-leg headroom; integer-cent `b2_max = floor(−b1 − fee − 1)`; strict `b1 + b2 + fee < 0`; movement only on lawful strictly-later receipt-identified evidence. Proven three ways: (a) code — the overlay touches only availability semantics; (b) the V2 headroom receipts file is **decompressed-byte-identical to V1's** (167,501 rows — the five events had no headroom activity); (c) independent re-verification over all **167,501** receipts: **zero b2_max mismatches** against the frozen function, **zero strict-budget violations**, and the accepted-action count reconciles exactly (21,838 one-cent improvements + 5,721 budget-reducing corrections = 27,559 = the committed invariant receipt).

## 7. Deterministic reproduction and receipts — PASS

- **Tests:** `test_window1_round4_v2.py` → **8 passed**; inherited relevant suites (`test_window1_round4_instrument.py`, `test_window1_round4_diagnostics.py`, `test_window1_round3_instrument.py`) → **52 passed**. Total relevant: **60/60**.
- **Regeneration:** `python -B arb-executor/analysis/window1_round4_prerun_builder_v2.py --repo . --events <private>/joined/events.jsonl --market-cache <private>/fit-local/guarded-cache-v3 --output-dir <fresh temp> --workers 6` → all regenerable V2 artifacts **byte-identical to the committed git blobs** (streams gz decompressed content, headroom receipts gz, candidate order differences, capability) — zero nondeterminism. *(Result recorded below.)*
- **Receipts:** all 16 artifact receipts and 6 code receipts verify (sha256 + staged blob OIDs; the familiar CRLF disk-basis accepted where blob-equivalent); the controlling amendment blob OID pinned in the manifest **matches `abe543e3`'s committed ITEM5_AMENDMENT.md exactly**; inherited-source receipts declared byte-identical (additions-only commit proves it); opportunity-ledger V2 manifest shard hashes verify; supersession receipt retracts V1 from execution (`V2_execution_binding_required: true`) while preserving V1 files.
- **Isolation:** no holdout, live, production, order, position, exit, settlement, DCA, Window-2, or oracle-field access anywhere in the V2 modules or artifacts; policy imports no diagnostics; forbidden oracle fields inherited and enforced from V1.

## Regeneration result (measured)

All **five** regenerable artifacts byte-identical to the committed git blobs (gz compared on decompressed content): FROZEN_CANDIDATE_EVENT_STREAMS_V2.jsonl.gz (1,608 streams), ROUND4_V2_HEADROOM_DECISION_RECEIPTS.jsonl.gz (167,501 receipts), ROUND4_V2_CANDIDATE_ORDER_DIFFERENCES.jsonl (707 rows), ROUND4_V2_REAL_CAPABILITY.json, and ROUND4_V1_V2_STREAM_IDENTITY_RECEIPT.json. **Zero nondeterminism.**

## RULING

**PASS.** The V2 PRE-RUN at `781b6d6f` correctly and minimally implements the amended availability law and the 100¢ removal; the five events are restored to D=804 as lawful NO_CALL members with zero fabricated orders; everything else is byte-identical to the audited V1.

**Scope of this PASS:** it closes the mechanical V2 censor/100-cent correction only. It does **not** authorize scoring, benchmarking, or an execution package. The separately identified **last-trade/chain** and **macro×micro composition** omissions remain open and must be reconciled in their own PRE-RUN with independent audit before any Round-4 execution is considered.
