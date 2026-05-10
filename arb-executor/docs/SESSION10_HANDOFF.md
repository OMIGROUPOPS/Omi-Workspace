# Session 10 Handoff: Forensic Replay v1 → Layer B v2

**Audience:** Claude Code (CC), starting fresh with this doc as the briefing entry point.
**Authored:** 2026-05-10 ET, end of Session 9 chat-side work.
**Repo state at handoff:** commit `fb3f976` on `main` (final commit of Cat 11 / B25 canonicalization sweep, immediately preceding this handoff doc commit).

## What just happened (Session 9 strategic finding)

Forensic replay v1 was authored, built, run end-to-end across three phases, and produced a strategically load-bearing FAIL verdict against Layer B v1's simulator. The FAIL is structural, not a code bug — Layer B's simulator and tick-level reality diverge because the simulator detects threshold crosses at minute-boundary `yes_bid_close` candle prints, and tick reality has sub-minute bid spikes that hit hypothetical resting sells without trace in the minute close. The mechanism is named in **LESSONS B25 (commit `033fb8a`): minute-cadence fire_rate undercount.**

Phase 3 corrected (commit `73de3a6`) measured Spearman ρ=0.136 between simulated `capture_mean` and realized `capture_A_net_mean` across 80 candidates (FAIL on the spec's 0.75 threshold; p=0.23, no significant correlation). 76.2% of candidates have realized > simulated. By policy class: limit policies (n=39, 49% of corpus) realize +$0.072 over simulated (2.4× understatement); time_stop calibrated within $0.008; trailing under-realize by $0.005.

A deployable cohort exists empirically: 40 of 80 candidates meet `replay_fill_rate ≥ 0.40 AND cell_drift_at_fill ≤ 0.50`. Top deployable by Scenario B is **ATP_MAIN 50-60 tight low / limit_c=30** (B=$0.261/moment, fill 76%, drift 9%, win 94%, n=2914). Production execution should use Scenario B (fill-time exit anchor) — B > A in 78.8% of candidates, mean delta $0.0158/moment.

## Cat 11 / B25 canonicalization sweep (7 commits, all landed)

| Commit | Doc | Concern |
|---|---|---|
| `73de3a6` | `data/durable/forensic_replay_v1/` | Phase 3 corrected outputs persisted |
| `4e36f30` | `docs/ANALYSIS_LIBRARY.md` | Cat 11 anchor + Cat 5 closure |
| `033fb8a` | `docs/LESSONS.md` | B25 mechanism + changelog |
| `c87e797` | `docs/SIMONS_MODE.md` | Section 6 forward-reference closure |
| `827fc22` | `docs/forensic_replay_v1_spec.md` | Section 10 verdict + footer |
| `c1cdcea` | `docs/SIMONS_MODE.md` | Section 5 line-24 closure |
| `fb3f976` | `docs/ROADMAP.md` + `docs/SIMONS_MODE.md` | T32 demotion + T36 + Section 8 |

The doc set is in coherent harmony state. Forward-references closed: SIMONS_MODE Section 5 + Section 6 + Section 8 (3 of 3). Empirical anchor: Cat 11. Mechanism: B25. Spec verdict: Section 10. ROADMAP: T32 demoted, T36 (Layer B v2) introduced as the new highest-priority deliverable.

## What's next: T36 — Layer B v2 spec authoring + producer build + corpus rollout

T36 is the new T-item authored in commit `fb3f976`. Read `docs/ROADMAP.md` T36 entry for full scope. Briefly:

**Goal:** Author Layer B v2 spec, build a producer, roll out across all 12,455 non-settle premarket cells (Phase 3 evaluated only top-20-per-category = 80). v2 folds forensic replay's tick-level mechanism back into the simulator at the source. v2's output supersedes Layer B v1's `exit_policy_per_cell.parquet` as the deployment ranking source.

**Calibration target:** v2 must produce capture mean within ±$0.01 of forensic replay v1's $0.261/moment realized at rank-1 cell (ATP_MAIN 50-60 tight low / limit_c=30). Anchored in `data/durable/forensic_replay_v1/phase3/candidate_summary.parquet`.

**Mechanism reference:** B25 (commit `033fb8a`) names the structural defect v2 fixes.

**Out of scope (deferred to v3 or separate variants):**
- Settle-horizon time_stop policies (Cat 5's predicted top cell WTA_MAIN 40-50 tight low / time_stop "settle" remains forensic-replay-unvalidated; separate forensic replay v2 settle-horizon variant pending)
- In-match channel (v2 stays premarket-only)
- Fees integration (Cat 2's fee table; T32 scope, demoted to v3)
- Production deployment decisions (which cells, sizing, queue management)

**Phased rollout discipline (carry over from forensic replay v1):**
- Phase 1: single candidate × 100 moments calibration probe (smoke test, ~5 min budget). Phase 1 candidate: ATP_MAIN 50-60 tight low / limit_c=30. v2 must produce capture mean within ±$0.01 of $0.261. If v2 ≈ forensic replay v1 on this cell, mechanism is validated.
- Phase 2: single candidate × all moments (validate runtime + memory)
- Phase 3: full corpus (or sampled subset)

**Runtime budget concern (load-bearing for spec Section 5):**
12,455 cells × ~330 moments/cell × ~0.3s/moment = ~1000 hours single-threaded. Way too slow. v2 needs to be either:
- Sampled (top-N per cell-key feature combination, similar to Layer A's manifest), OR
- Parallelized across cells

Decide and document in spec Section 5. **This decision commits the architecture for several sessions; chat-side sign-off matters at this gate (Coordination Point 2 below).**

## Coordination Points (mandatory STOP markers — do not push past without operator sign-off)

### COORDINATION POINT 1 — STOP after Layer B v2 spec lands

After authoring Layer B v2 spec (sibling shape to `forensic_replay_v1_spec.md` and `layer_b_spec.md` — Sections 1-9 + footer), commit it as a single-concern commit. Then surface:
- Commit URL
- Architecture decision in Section 5 (sampled vs parallelized)
- Any deviations from the briefing or open architectural questions

Operator brings to chat-side for spec review. v2 spec choices commit the architecture for several sessions; chat-side sign-off matters here. **Do NOT proceed to producer build without sign-off.**

### COORDINATION POINT 2 — STOP after Phase 1 calibration probe lands clean

After implementing v2 producer and running Phase 1 (single candidate × 100 moments smoke test), surface:
- Commit URL for producer
- Phase 1 results (capture mean, fill rate, runtime, memory)
- Whether v2 hits the calibration target (±$0.01 of $0.261 on ATP_MAIN 50-60 tight low / limit_c=30)

Operator brings to chat-side for review. v2 Phase 1 PASS is the gate for committing to v2 as deployment ranking source. **Do NOT launch Phase 2 or Phase 3 without sign-off.**

### COORDINATION POINT 3 — STOP after Phase 3 lands

Surface validation gate verdicts (analogous to forensic replay v1's Phase 3 gate). If v2 PASSES, the corpus-wide ranking source is now real and forensic replay v1's deployable cohort can be expanded.

## Operating norms (carry over from Session 9)

1. **Single-concern commits.** Never bundle. Seven commits in the Cat 11 sweep kept the discipline clean.
2. **scp-pattern for large file edits.** Heredoc fails on multi-line triple-quoted Python. Always draft locally, scp to `/tmp`, verify-compile + grep-anchors, then `mv` into place.
3. **Pre-flight gates before every edit.** `grep -q` for distinctive anchors, `&& exit 1` for things that shouldn't already exist, `|| true` on `grep -c` to avoid C29 set-e brittleness, fail loud on missing anchors.
4. **Web-fetch verify each commit URL.** Don't assume reported diff matches what landed. Fetch the commit page and read the diff.
5. **One ssh prompt per turn, never bundled.** If a workflow is multi-step, sequence them; don't try to fit Phase 1 + commit + Phase 2 launch in one ssh invocation.
6. **Probe before assume.** Format probes before drafting (Cat 11 anchor caught a stylistic-drift risk this way; B25 caught actual lesson-format on probe; T32 amendment caught the existing T33 amendment shape on probe).
7. **Recommendation posture.** State a clear recommendation with reasoning; don't present a/b/c menus when the right answer is clear.
8. **Resolve uncertainty through probes, not open-ended operator questions.**
9. **Suspicion and uncertainty get resolved through probes, not surfaced as open questions to the operator.**

## What's out of scope (deferred)

- Settle-horizon time_stop policies in forensic replay
- In-match channel forensic replay
- Fees integration (Cat 2 fee table) into forensic replay v1 or Layer B v2
- Production deployment decisions
- Layer C v1 (T32, demoted by Cat 11 / B25)
- Forensic replay v2 settle-horizon variant
- VPS PAT migration to SSH-based auth (operator-acknowledged tracked item; not blocking T36 work)

## Key file paths

- VPS working dir: `~/Omi-Workspace/arb-executor`
- Spec docs: `docs/{forensic_replay_v1_spec.md, layer_b_spec.md, SIMONS_MODE.md, ANALYSIS_LIBRARY.md, LESSONS.md, ROADMAP.md}`
- Producer scripts: `data/scripts/{build_layer_a_v1.py, build_layer_b_v1.py, build_forensic_replay_v1.py, cell_key_helpers.py}`
- Output parquets: `data/durable/{layer_a_v1/, layer_b_v1/, forensic_replay_v1/, g9_trades.parquet, g9_candles.parquet, g9_metadata.parquet}`
- Live bot: `data/scripts/live_v3.py` with `deploy_v4.json`
- Phase 3 corrected outputs (canonical truth): `data/durable/forensic_replay_v1/phase3/`

## How to coordinate with chat-side after a STOP

When you hit a coordination point:
1. Surface a brief summary of what landed (commit URLs, key metrics, any deviations from the briefing)
2. Note any open questions for chat-side
3. Stop. Don't anticipate next moves; let chat-side direct.

Operator brings your output back to chat. Chat-side Claude reviews, drafts the next single-concern, operator hands it to you. Same pattern as Session 9 worked, just with you operating between coordination points.
