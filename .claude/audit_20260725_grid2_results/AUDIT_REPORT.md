# INDEPENDENT FINAL RESULTS AUDIT — grid2-stdoutsafe EXECUTION @ 10ac6dbc

**Status: AUDIT COMPLETE. RESULTS ADMISSIBLE. NO CANDIDATE REACHED PC ≥ 603 — highest observed PC = 0.**
Date: 2026-07-25 · Branch: `audit/window1-independent` · Auditor: independent CC session
Method: read-only detached worktree at `10ac6dbc`; every hash verified against git blobs (LF-authoritative); all metrics independently recomputed from the per-event ledgers; zero scoring reruns; holdout untouched; no production/live surface accessed.

## 0. Prior art (C45 gate)

`git log audit/window1-independent` + grep of prior audit directories. Prior art: `c94d4e50` (my PRE-RUN authorization of `47bfbd43`, defining the exact one-attempt scope), `2ac4a2f4` (grid1 failure forensic), `9868bf48`/`dd6fc308` (Round-2 packaging/PRE-RUN audits), and memory `project_window1_osfamily_audit` (07-24: Round-1 miss = instrument ceiling, not market). Delta: first audit of the completed grid2-stdoutsafe execution results.

## 1. Ancestry — PASS

`10ac6dbc` ("Record authorized Round-2 development execution") has parent exactly `47bfbd43`; a children-scan across all refs shows it is the **sole child**; it is the remote tip of `codex/window1-definition`. The diff `47bfbd43 → 10ac6dbc` is **purely additive**: the 20-file results directory plus one sanitized top-level execution receipt (`.claude/window1_round2_grid2_execution_receipt_20260725.json`). No modification or deletion of any file — results-only.

## 2. Frozen surfaces — PASS (byte-identical by construction)

Because the results commit contains zero M/D entries, every authorized artifact — bundle (`e0e088e3…`), runner (`b8c02d16…`), scorer (`b41e6915…`), scorer contract (`6684ee34…`), guard/metric/candidate contracts, 6,432 candidate streams, D=804 ledger, and all frozen July 12–20 inputs — is byte-identical at `10ac6dbc` to the package I verified blob-by-blob in the `c94d4e50` authorization audit. The start receipt and execution manifest pin the identical bundle/scorer/contract hashes, git SHA `47bfbd43`, and forensic binding (`2ac4a2f4` / blob `b587b241…`). The top-level receipt additionally binds my authorization commit and its report blob (`4f7910e8…` — verified against `c94d4e50`).

## 3. Single lawful execution — PASS

- Start 2026-07-25T06:34:15.770158Z → end 07:06:51.173253Z (32.6 min), `exit_code: 0`.
- `candidate_scorer_invocations_completed: 8`; execution manifest records exactly **1 scorer invocation per candidate, total 8**, in the frozen dispatch order.
- No `EXECUTION_FAILURE.json` exists; top-level receipt: `execution_attempt_count: 1`, `retry_or_resume_count: 0`. The runner refuses pre-existing result directories, and only one results directory exists in the tree.
- PROGRESS.log: exactly 18 one-line events, complete and correctly ordered (execution_id, git_sha, then start/complete for candidates 1–8, no gaps, no duplicates). STDOUT.log is **byte-identical** to PROGRESS.log; STDERR.log is empty (SHA-256 = empty-string hash). Console-echo receipt: stdout and stderr remained enabled the whole run — **no stdout loss occurred**; the stdout-safe machinery was armed but never needed.
- No partial-artifact contamination: the retired grid1 directory is bound as excluded (`retired_execution_consumed: false` in receipts) and its 6 files remain byte-identical to the forensic record (re-verified this session).

## 4. Output hashes — PASS (18/18)

All 18 entries in OUTPUT_HASH_MANIFEST.json reproduce exactly against git-blob bytes, byte counts included; `stdout_sha256`/`stderr_sha256` in the manifest reproduce; the manifest's own hash matches the top-level receipt's claim. (A first pass against my worktree files "failed" 17/18 — that is my checkout's CRLF conversion, not the artifacts; blob bytes are authoritative and all match.)

**Determinism bonus:** grid2's candidate-1 ledger is **byte-identical** (`3619e26d…`) to grid1's preserved candidate-1 ledger from the failed attempt — the frozen instrument reproduced the identical result on a fresh run, confirming both determinism and the grid1 forensic's "ledger closed sound" verdict.

## 5. Conservation and identity — PASS

Per candidate (all 8): exactly 804 rows; 804 distinct event_ids **set-identical to the frozen D=804 event ledger**; 1,608 leg tickers, all unique; zero duplicate fill receipts (receipt_id + ticker basis); all event dates within 2026-07-12…20; single `classification` per row from the closed vocabulary {genuine_nonfill, censored, contradictory, zero_length_window, naked_single_leg} — mutually exclusive by construction; census sums to 804 for every candidate (matches METRIC_CONSERVATION_REPORT).

## 6. Independent metric recompute — PASS (matches reported; see AUDIT_RECOMPUTE_RECEIPTS.json)

Recomputed from raw ledger rows, not report totals. Definitions applied: C = both legs `inside_window_quantity == 5` (dual exact-five); PC = C ∧ combined W1-close delta < 0; S = C ∧ combined entry cost < 100¢; IC = C ∧ both individual leg deltas < 0. Row-level C/PC/S/IC flags match my derivations on all 8 × 804 rows (zero mismatches); cost/delta cross-foots (combined = sum of legs) had zero failures (vacuous — no completions).

### Complete candidate table (D = 804, target PC = 603)

| # | Candidate | C | PC | S | IC | C/D | PC/D | S/C | IC/C | genuine_nonfill | censored | contradictory | zero_length | naked_single_leg |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | r2_async_pair__park_join__hold | 0 | 0 | 0 | 0 | 0.0 | 0.0 | — | — | 615 | 161 | 14 | 13 | 1 |
| 2 | r2_async_pair__park_join__reaim | 0 | 0 | 0 | 0 | 0.0 | 0.0 | — | — | 615 | 161 | 14 | 13 | 1 |
| 3 | r2_async_pair__touch_park__hold | 0 | 0 | 0 | 0 | 0.0 | 0.0 | — | — | 587 | 161 | 14 | 13 | 29 |
| 4 | r2_async_pair__touch_park__reaim | 0 | 0 | 0 | 0 | 0.0 | 0.0 | — | — | 587 | 161 | 14 | 13 | 29 |
| 5 | r2_causal_steer__park_join__hold | 0 | 0 | 0 | 0 | 0.0 | 0.0 | — | — | 616 | 161 | 14 | 13 | 0 |
| 6 | r2_causal_steer__park_join__reaim | 0 | 0 | 0 | 0 | 0.0 | 0.0 | — | — | 616 | 161 | 14 | 13 | 0 |
| 7 | r2_full_os__walk_park__hold | 0 | 0 | 0 | 0 | 0.0 | 0.0 | — | — | 616 | 161 | 14 | 13 | 0 |
| 8 | r2_full_os__walk_park__reaim | 0 | 0 | 0 | 0 | 0.0 | 0.0 | — | — | 616 | 161 | 14 | 13 | 0 |

Combined cost/delta distributions: **empty for every candidate** (no completions exist to distribute). Partial (both-legs-touched, not exact-five): 0 everywhere. Inside-window fills across all 8 candidates: **82 total, every one single-leg** (patterns: one leg 5.0 / other 0; or fractional 0.55–1.7 / other 0). No-call counters: cohort_NO_CALL = 0 everywhere; reaim_NO_CALL = 0 on hold ledgers, 185/251/182/168 on the four reaim ledgers.

## 7. Frozen behavior applied as authorized — PASS

- **Real-start guards**: every leg's boundary block carries a lawful guard (`te-calibration-central-93pct-asymmetric-v1`, `causal-interval-strict-60s-v1`, `official-point-strict-60s-v1`; guard absent only on censored/contradictory boundaries); boundary status census: 11,280 positive / 1,360 censored / 224 contradictory legs; source classes are the frozen vocabulary (official_exact, quantized_late_detection_proxy, live_by_only, schedule_only, clean_causal_interval, contradictory). **All 82 inside-window fills have timestamps ≤ the leg's boundary timestamp — zero cutoff violations.**
- **Per-leg asynchronous timing / pair behavior**: per-leg boundaries and per-leg fill accounting are present and independent per leg (asynchronous by construction); no cross-leg contamination found (leg identities unique; fills attach to single legs).
- **Reaim behavior / first-fill sibling response**: hold-vs-reaim ledgers differ **only** in `reaim_NO_CALL_count` — zero outcome differences (classification, flags, costs, deltas all identical). BASE_REAIM_COMPARISON's changed-order event lists match the **frozen, pre-registered** `base_reaim_changed_order_event_ids` in the bundle exactly (91/85/87/64 events per pair); fills gained/lost = 0, singles→duals = 0, metric changes = 0, improvement_class "neither", `ranking_or_selection_applied: false`.

## 8. No post-hoc selection — PASS

The results commit is additive-only (no code, config, or package change after observing results); `selection_status: UNRANKED_FROZEN_SELECTION_RULE_ABSENT`; `selected_candidate_receipt_emitted: false`; `ranking_performed`/`tuning_performed`/`ablation_performed` false throughout; all eight candidates remain unranked (and are in fact tied). **Audit fact only: the highest observed PC is 0, shared by all eight candidates.** This is not a selection.

## 9. Holdout and surface isolation — PASS

Non-access proof: `holdout_opened/queried: false`, `input_manifest_holdout_rows: 0`, `holdout_paths_opened: []`, `network_calls: 0`, `live_exchange_calls: 0`, and empty lists for production, live_v4, configuration, and orders/positions/Window-2/exits/settlement/DCA paths; only the grid2 results directory was written. Independently corroborated: every ledger row's event_date lies in July 12–20 (zero July 24–26 rows); the commit diff touches nothing outside `.claude/` results + receipt; the frozen cache census (verified at authorization) contains zero holdout dates. This audit itself opened no holdout path.

## 10. Verdicts

**Admissibility: ADMISSIBLE.** The execution is the single authorized attempt, at the authorized SHA, under the authorized bundle and command, with complete receipts, reproducing hashes, conserved D=804, and no selection, tuning, retry, holdout, or production contact. Grid1 remains inadmissible and untouched.

**PC ≥ 603: NO.** No candidate reached it; no candidate recorded even one dual completion (PC = 0, distance 603 for all eight).

**What the run proves:**
- The frozen Round-2 instrument executes deterministically end-to-end (grid1's candidate-1 ledger reproduced byte-for-byte on a fresh run) and the stdout-safe repair is sound (armed, unneeded, zero interference).
- On the July 12–20 development slate, under the frozen real-start guards and Window-1 cutoff law, **none of the eight frozen OS-family policies produces a single dual exact-five completion in D=804**. Entry activity exists (82 single-leg inside-window fills) but the paired leg never completes — the zero is a pairing/completion failure, not a total absence of fills. Reaim, as frozen, changed orders on the pre-registered events but changed no outcome.

**What the run does not prove:** a market ceiling (`market_ceiling_claimed: false`); that all possible OS policies fail (`all_possible_OS_policies_claimed: false` — only these eight frozen candidates were tested); anything about July 24–26 (sealed); anything about live trading performance; and it provides no basis for ranking or selecting among candidates (all tied at zero).

**Discrepancies/defects: none material.** Three definitional notes, all resolved: (a) report `partial` counts both-legs-touched-not-exact-five (0 everywhere), while single-leg activity of any size is `naked_single_leg`; (b) report `feature_unavailable` counts entries (110/115), not rows (110) — candidates 5–8 carry an extra unavailable `top5` feature on 5 events; (c) 17/18 apparent hash mismatches in a working-tree pass were my checkout's CRLF conversion — git-blob bytes all verify.

**Smallest lawful next action:** no execution. Take these admissible zero-completion results to the standing analysis/ruling process as the development answer for Round 2: diagnose *why* dual completion never occurs (82 single-leg fills vs 0 duals — partner-leg starvation is the standing hypothesis, consistent with the 07-24 finding that the miss is instrument ceiling, not market), and only then design a Round-3 instrument as a new pre-registered PRE-RUN with its own independent audit before any execution. No retry or re-run of grid2; the holdout stays sealed; no candidate is selected or deployed.
