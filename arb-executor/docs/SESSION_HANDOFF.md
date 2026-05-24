# SESSION HANDOFF — current

**Convention:** This file is ALWAYS the current handoff — overwrite in place at end of each session. Numbered SESSION{N}_HANDOFF.md files in `docs/handoffs/` are frozen historical snapshots; do not edit them.

**Last updated:** 2026-05-21 ET (post-atlas-lock Stage 0 reconcile).
**Repo state:** HEAD `d99c6e9` (atlas lock). Atlas + foundation chain canonical on origin/main.

**Read order for a fresh chat or CC instance:** README → this file → LESSONS Section 1 → TAXONOMY Section 2.5 → ANALYSIS_LIBRARY → ROADMAP → SIMONS_MODE. On-demand: spec docs in `docs/` and atlas LOCKED_DOWN files in `data/durable/spike_volatility_map/`.

`CHAT_HANDOFF.md` was consolidated into this doc in this same Stage 0 reconcile; the stub there points back here.

---

## ORIENTATION (read first)

### Current state, in one sentence

The strategy phase is locked. The bot is paused. Next is execution-lock: surface bugs in paper mode before deploying.

### What just landed (the 2026-05-15 → 2026-05-20 arc)

Five canonical analytical artifacts landed in dependency order between CHAT_HANDOFF's last touch (2026-05-15) and HEAD:

1. **per_minute_features.parquet** (T37 ckpt-3, sha256 `9fde4b5d`) — FOUNDATION-TIER per TAXONOMY. 9.33M ticker-minute rows, 88 cols. The canonical observation grain. Pre-existing at start of arc; foundation for everything below.

2. **n_profile_v1** (T40, sha256 `a7ed1155`, producer `a28840e`) — per-N rollup, 19,614 rows × 45 cols, 0 dropouts, 7/7 gates PASS at Phase-3 full corpus 2026-05-18. The per-N projection of the foundation.

3. **inmatch_bounce_surface_v1** (T41, sha256 `14241db0`, register commit `6f1d4bd`) — Layer-A-equivalent band-free in-match bounce surface. 800 rows, 7/7 gates PASS at full cohort 2026-05-18. First analytical deliverable on n_profile_v1.

4. **Spike volatility map atlas** (T42, six commits `481de7f` → `d99c6e9`) — four-category descriptive lock-down. 14,033 N's across ATP_MAIN / WTA_MAIN / ATP_CHALL / WTA_CHALL. 4 spike per-N parquets + 12 descriptive parquets + 4 LOCKED_DOWN.md + PAIRING_DIAGNOSTIC.md + canonical producer `data/scripts/build_spike_perN.py` (`c5e377f`).

5. **(superseded subtrees, preserved not deprecated)** — Rung 1 strategy_evaluation producer (T39.1, commit `5fc6d40`, spec v0.3.2) committed code but never ran; exit_optimized_bounce_v1 (T39.2, spec/producer v0.4 `d23fff5`) Phase-1 PASS, Phase-2 halted-then-gate-fix. Both ate by the atlas. Code preserved; available if future work wants the rung-framing or dual-conservative-fill-frame approach.

### What's next (execution-lock)

The atlas measured strategy. The bot's job is to turn measured edge into realized edge. Sequence (locked this session, B-then-A):

1. **Bug 4 first** (T11a/T11b) — settlement state detection in paper mode per `docs/bug4_brief.md`. 500+ line spec exists. Operationally: phantom positions hold resting exit orders past settlement. Closes the paper-mode reliability gap.
2. **Layer B v2 second** (T36) — tick-level fill semantics replacing minute-cadence simulator (which overstates fills 2.4×). Spec at `docs/layer_b_v2_spec.md`. Spec must be revised against T37 foundation before producer build (per ROADMAP T36 amendment 2026-05-14).
3. **Hot-reload mechanism** — operator-stated requirement: weed out bugs without shutdown/reboot. `docs/bot_v5_shell_architecture.md` may address; v5 vs v3 decision pending.
4. **Paper-mode integration test suite** — B4-T8 through B4-T11 unit tests plus broader coverage (match-cycle, fill detection, settlement, position state, P&L, scanner-executor, restart-and-resume).
5. **Paper-mode run against live tape** — continuous; compare paper P&L against atlas hindsight rules.
6. **Capital deployment with safety rails** — start small, scale via G22 cts/N axis as depth is characterized.

**Deployment philosophy:** Trade all 90 cells per category, do not cherry-pick to high-ROI cells. Volume is the operational constraint. Execution work resolves marginal cells; cell selection does not.

---

## DURABLE CONTEXT

### Operator

Druid, co-founder OMI Group Holdings (trading division OMQS). Algorithmic prediction-market trading on Kalshi tennis binary markets. Direct, technically precise, high-urgency. Pushes back on premature conclusions; consistently correct when he does. Treat operator pushback as probe-trigger per A32, not defend-trigger.

### Agent topology — four agents, operator is routing layer

No direct agent-to-agent pipes. Operator copy-pastes between them. All git commits have author `Druid <Osullivan Omigroup.ops@outlook.com>` (operator's local git config) and Co-Authored-By `Claude Opus 4.7 (1M context)`. Executor-of-record for VPS-side runs is named explicitly in commit messages ("App-authored", "App-verified", "via App", etc.).

- **Opus (chat-side Claude on claude.ai)** — strategy, spec drafting, verification, coordination. Web/mobile chat interface. Has `web_fetch` + `bash_tool` sandbox at `/tmp/omi_check/` for byte-verification reads only. Cannot SSH to VPS, cannot commit. Drafts prompts that operator pastes to App or CC. Co-Authored-By on every recent commit.
- **App (VPS-side executor)** — runs on the VPS at `root@104.131.191.95`, workspace `/root/Omi-Workspace`. Full shell, file read/write, runs producer scripts directly against the heavy parquets that live there (g9_trades 1.5GB, per_minute_features 388MB, n_profile.parquet, etc.). The agent of record for spike producer runs, n_profile_v1 Phase-3 build, inmatch_bounce_surface_v1 Phase-2 build, Layer A v1 / Layer B v1 / Rung 0 producer runs, forensic replay runs. Evidence: commit messages `5fc6d40`, `8e8f46e`, `19fdd5a`, `0fcf474`, `c9a0f3e`/`c76eee5`, `4c100f7` all attribute the on-VPS work explicitly to App.
- **CC (Claude Code in Cursor IDE)** — runs in Cursor on operator's Windows machine with the operation's codebase loaded as working context (local clone at `C:\Users\omigr\OMI-Workspace\arb-executor`). Drafts/edits code, helps operator construct commits from the local clone, can push to origin/main. Where code-level changes get authored before being either committed locally or shipped to App for VPS execution.
- **Plex (Perplexity Comet)** — external research/synthesis. Browser-based; read-only on public web URLs incl. the public GitHub repo. No shell, no write. Methodology synthesis only (e.g., this session arc's stability framework rounds, adaptive-binning consult).

### Systems access

- **App's working context:** VPS shell at `ssh root@104.131.191.95`, workspace `/root/Omi-Workspace`, primary subdir `arb-executor/`. Heavy parquets (g9_trades, per_minute_features, n_profile, Rung 0 cell_economics) live here.
- **CC's working context:** local Windows clone at `C:\Users\omigr\OMI-Workspace`, target subdir `arb-executor/`. Commit-authoring happens here; pushed to origin/main.
- **GitHub:** `github.com/OMIGROUPOPS/Omi-Workspace` (public). Source of truth.
- **VPS-vs-origin sync:** the VPS git tree runs behind origin/main by design — App pulls only when re-running producer code (explicit operator decision per turn).
- **Opus sandbox:** clone the public repo to `/tmp/omi_check/Omi-Workspace` for byte-verification reads; ephemeral per chat session, read-only.

### Foundation chain (canonical, with sha256s)

```
G9 corpus                  per_minute_features        n_profile_v1                inmatch_bounce_surface_v1
(T28 ea84e74)              T37 ckpt-3 9fde4b5d        T40 a7ed1155                T41 14241db0
g9_candles 9.5M rows       9.33M ticker-min rows      19,614 rows × 45 cols       800 rows
g9_trades 33.7M rows  -->  88 cols          -->       7/7 gates PASS       -->    7/7 gates PASS
g9_metadata 20,110 rows    FOUNDATION-TIER            per-N rollup                Layer-A-equiv per B16
                                                                                  |
                                                                                  v
                                                              Spike volatility map atlas (T42)
                                                              4 cat × {1c, 2c, 3c} descriptive
                                                              + spike per-N parquets
                                                              + canonical producer build_spike_perN.py
                                                              HEAD d99c6e9
```

Parallel superseded subtrees:
- Rung 1 producer (T39.1, commit `5fc6d40`): committed-but-never-run, lane eaten by atlas.
- exit_optimized_bounce_v1 (T39.2, commit `d23fff5` v0.4): Phase-1 PASS, Phase-2 halted then gate-fixed, never re-run.

### Working norms (battle-tested, carry forward verbatim)

1. **Single-concern commits**, dependency-ordered. Never bundle.
2. **One executor prompt per turn** (App or CC), never bundled. Multi-step workflows sequence across turns.
3. **Probe-validate-probe-validate** before expensive compute. Five failure modes per D11: provenance, grain, unit, coverage, upstream-filter.
4. **Corpus mutations require C37 pre-replace validation gate**. Compute `.new`, run hard gates against `.new` bytes, `os.replace` only on all-pass. Gate failures adjudicated with disk evidence, not narrative.
5. **Streaming discipline on VPS** (~1.9 GB RAM). >3-4 full columns into pandas risks OOM. Use iter_batches / per-ticker pyarrow pushdown.
6. **Web-fetch / verify every commit against origin** via `/tmp/omi_check` clone or equivalent. Don't trust executor summary uncritically.
7. **State recommendations with conviction, not options.** When the right answer is clear, name it and let operator countermand. Operator-flagged: "stop with the subjective questions."
8. **When you background a job, you own the follow-through.** Poll it, surface results when they land — don't wait to be asked.
9. **All operator-facing timestamps ET per G21.** UTC stays at raw-bytes layer only.
10. **Full player names always.** Never abbreviations or 3-letter Kalshi codes.
11. **Treat operator pushback as probe trigger per A32**, not as noise.
12. **External synthesis (Plex, etc.) gets committed to `docs/external_synthesis/<source>_<topic>_<date>.md` immediately**, not held in chat-side context only.
13. **Critical review uses disk evidence, not inference.** Pull the actual repo and verify column names, doctrine claims, corpus assumptions against committed source. Inference about what the spec "probably says" produces partially-wrong corrections.
14. **The "ct" unit is one contract, integer-indivisible.** Pays $1 (effectively 99¢ per E32 first-touch). Operator-facing economics in ct terms always; per G22 keep N (per-binary-market unit-of-observation) and ct (unit-of-position-size) distinct.
15. **Codify principles when operator surfaces them.** A39 (cents-vs-ROI), G22 (N-vs-ct), B25 (minute-cadence undercount), C38 (zero-large-fraction = scoping bug not sample artifact) all came from this discipline.
16. **The repo is the shared brain.** Anything that would otherwise be copy-pasted between agents gets committed and read from origin/main.
17. **CC prompts use repo-root-relative paths.** CC operates from `C:\Users\omigr\OMI-Workspace` (the actual repo root, not the arb-executor subdir). Always pre-flight `git rev-parse --show-toplevel` before any path-dependent operation. Chat-side path assumptions are inference, not evidence.

### What NOT to do (lessons paid for this session arc)

- **Don't collapse the three axes into one realizable-PnL number.** Headline × exit-fill-fraction × entry-improvement × sizing-scale stays decomposed. Never present a deployable dollar figure without the three-axis caveat attached.
- **Don't run OOS tests as if the descriptive measurement is a predictive claim.** The atlas measures what the corpus paid under per-cell hindsight-optimal rules. That is well-posed without OOS. Predictive generalization is a separate question downstream of execution work. Confusing the two produced an hour of OOS rabbit-hole work this arc.
- **Don't pool adjacent cells without preserving real heterogeneity.** The 2¢ probe diagnostic showed pooling cells 37 + 38 destroyed $37.50 of edge that was real cell-by-cell variance, not overfitting. 1c/2c/3c reported side-by-side per Plex round-2 recommendation.
- **Don't apologize when corrections are needed.** Operator pushback is signal; absorb the correction, recompute, move on. Don't self-flagellate or relitigate.
- **Don't conflate Rung 0 (cell economics primitive) with Rung 1 (strategy evaluation).** They answer different questions at different aggregation levels. T39 (the recomputation ladder) and T42 (the atlas) ARE different things even though both touch cell economics.
- **Don't lose the foundation chain.** per_minute_features → n_profile_v1 → inmatch_bounce_surface_v1 → atlas is the actual provenance. Treating the atlas as if it sits directly on G9 trades misses the load-bearing intermediates.
- **Don't run code in the Opus sandbox that ought to run via App or CC.** `/tmp/omi_check` is read-only verification only — clone fresh, read, never write. Producer execution and corpus mutations against the heavy parquets run via App (on the VPS). Code authoring and local commits run via CC (Cursor IDE). Operator routes per task.
- **Don't reframe what the operator said into safer versions.** When operator says "execution lock," draft toward execution lock, not toward an adjacent thing that feels more familiar.
- **Don't conflate "foundation broken" with "everything pre-atlas is suspect."** Foundation = data/strategy layer only. Executor-side institutional knowledge from prior deploys is durable and the execution-lock arc explicitly uses it (see "Bot status: PAUSED" below).

---

## CURRENT OPERATIONAL STATE

### Bot status: PAUSED

All prior bot versions (v1, v2, v3, V4.2c) traded on a foundation now known to be broken at the data/strategy layer. Capital is unused. The entire 2026-04-30 → 2026-05-20 arc was foundation rebuild. Now atlas is locked; execution-lock arc is next.

**Executor learnings carry forward.** "Foundation broken" means the data/strategy layer — spike measurement methodology, truncation handling, cell definition. Executor-side institutional knowledge from prior deploys is durable and the execution-lock arc explicitly uses it:

- **F4** — silent fill-detection failure class (Apr 17-23: 0 entry_filled events over 6 days despite 763 cell_match events). The category of bug Bug 4 implementation has to defeat.
- **Bug 4 (T11a/T11b)** — paper-mode settlement state handling, 500+ line brief at `docs/bug4_brief.md`, OPEN. First task in the execution-lock arc.
- **B25** — minute-cadence simulator undercount (2.4× overstatement of fills for limit policies vs tick-level reality). Mechanism that Layer B v2 (T36) has to fix.
- **C19** — Kalshi lifecycle timestamps don't track actual match start; use BBO volatility-jump detection or external scrape.
- **C37** — corpus mutations require pre-replace validation gate. Compute `.new`, run hard gates against `.new` bytes, `os.replace` only on all-pass.
- **Paper-mode infrastructure already exists in `live_v3.py`** — `_PAPER_API` flag, `PaperFillSimulator`, `PaperPosition` dataclass. Paper-mode unit tests specified B4-T8 through B4-T11. Paper mode does NOT poll REST settlements (would falsely close paper positions using real-account history); settlement detection in paper mode is via WS lifecycle + BBO threshold.
- **Kalshi auth pattern** — always copy from `swing_ladder.py`'s `_kalshi_headers()`. Never reimplement. RSA-PSS SHA256 signing `"{timestamp_ms}{method}{path_with_prefix}"`.
- **Kalshi API quirk** — `dict.get("taker_fill_count", 0)` returns `None` not `0` when the key exists with null value. Always use `(status.get("taker_fill_count") or 0)` pattern. Fill detection uses `remaining_count == 0` and `status == "executed"` as primary signals.
- **Rate-limit budget separation** — heavy backfill must not share rate-limit bucket with live trading (per L2 lesson when added). Operational requirement for execution-phase deployment.

The execution-lock arc inherits all of this. Strategy was rebuilt; execution is not being rebuilt — it's being debugged and hardened.

### Atlas headline (T42, four-category spike volatility map)

Taker-floor, hindsight-optimal per-cell exit-or-hold rules, 10ct sizing:

| Category   | N      | Trading days | 1c Total $   | 1c ROI  | Cheap regime ROI | Daily $  | Daily ROI |
|------------|--------|--------------|--------------|---------|------------------|----------|-----------|
| ATP_MAIN   | 4,137  | 252          | +$1,658.80   | +7.90%  | +36.13%          | $6.58    | +7.90%    |
| WTA_MAIN   | 3,683  | 248          | +$1,824.90   | +9.84%  | +43.22%          | $7.36    | +9.84%    |
| ATP_CHALL  | 5,326  | 109          | +$2,029.20   | +7.57%  | +36.83%          | $18.62   | +7.57%    |
| WTA_CHALL  | 887    | 80           | +$645.30     | +14.52% | +57.58%          | $8.07    | +14.52%   |

**Corpus totals:** 14,033 N's, +$6,158.20, $70,813.20 capital deployed, blended +8.70% per-trade ROI. **Pairing rate (event-level):** 79.3% paired (6,208 paired / 7,825 total events); 88.5% of N's in paired events. **Combined max-overlap operational picture:** ~91 N/day, ~$460 capital/day, ~$40.62 earnings/day, +8.70% blended daily ROI on cycling capital at 10ct.

### Three-axis caveat (verbatim, load-bearing for every headline)

Every atlas number is the strategy's opportunity floor on the corrected foundation. Three axes between this and realized PnL:

**AXIS 1 — EXIT-side fill realism (pushes DOWN).** Every simulated +X exit in the atlas assumes qualified-size taker print at that level = guaranteed maker fill. B25/Cat-11 evidence: 2.4× simulator overstatement of fill rates for limit policies in minute-cadence simulators against tick-level reality. The ≥250ct size-qualification floor and Main-tour deep mid-match liquidity mitigate somewhat; realization fraction unmeasured for this corpus. Expected realized capture: **0.4–0.8× of simulated**, pending dedicated Layer C fill-realism work.

**AXIS 2 — ENTRY-side maker improvement (pushes UP).** Every anchor in the atlas is a real T-20m TAKER trade — someone who paid up to cross the spread. A resting maker buy at the bid (or better) fills at a BETTER price than the taker print. On typical 1-2¢-spread markets, ~1¢ per ct cheaper entry per trade, compounding across larger captures on hits, higher ROI per hit, smaller carry losses on misses. Expected improvement: **~+10–30% on the headline**. Aligns with the bot's existing edge thesis (LESSONS line 48: "anchor-relative discount capture, 97% of fills are Scenario C_discount"). Tier 3 marginal cells (~35 cells where best_X is small) most levered to entry-side improvement.

**AXIS 3 — ARRIVAL FREQUENCY (G22).** Deployable economics need N's/day × ct/N sizing. Frequency observable from corpus (16.4 / 14.9 / 48.9 / 11.1 N/day per category at 10ct). Sizing depends on depth (F33). G22 axes are never collapsed: per-N edge × N's/day × cts/N.

**Combined:** realizable PnL = (headline) × (exit-fill-fraction 0.4–0.8) × (entry-improvement-multiplier ~1.1–1.3) × (sizing scale once depth is characterized).

Operator stated privately: "we can also assume privately that we'll be saving a cent or 2 once we figure execution out." Axis 2 in operational form. Headline stays conservative; operational hand reads ~+25–50% better than headline. Execution work will measure per cell.

**Do NOT** treat headline as deployable dollars. **Do NOT** treat headline as pure upper bound (entry-side correction is in the operation's favor).

### Structural patterns observed in the atlas (preserved as doctrine)

- Cheap regime (anchor 5–30¢) deploys ~8–9% of capital and generates 30–40% of dollar profit across all four categories. A39 cent-sensitivity geometry confirmed empirically.
- **Highest-ROI single cell across the corpus:** ATP_MAIN anchor=9¢, hold-to-settlement rule, +242% ROI on $20.70 capital (N=23, 30% YES-settle rate). Cheap-cell A39 asymmetry in extremis.
- WTA outperforms ATP at same draw level (WTA_MAIN +9.84% > ATP_MAIN +7.90%; WTA_CHALL +14.52% > ATP_CHALL +7.57%). Codebase hint that ATP/WTA need structurally different strategies does NOT show up in the spike-volatility-map dimension — both tours produce the same shape, WTA ~2pp hotter.
- Challenger tours: denser per active day, shorter-season. ATP_CHALL 48.86 N/day in 109 days vs ATP_MAIN 16.42 N/day in 252 days.
- High regime (anchor ≥66¢) barely positive everywhere (+3.11% / +3.52% / +3.46% / +5.50%). Favorite-side trades are marginal contribution.
- Cheap-regime unpaired N's outperform cheap-regime paired N's on ROI (+45.5% vs +38.9% aggregate). Asymmetric-information pattern flagged at corpus scale.

### Capital position

Operator stated: plenty of capital to scale up. Sizing is not the binding constraint. Binding constraints are (a) execution mechanics and (b) market depth (F33).

---

## OPEN UNCERTAINTIES (do not underweight)

1. **Bot architecture v5 vs v3** — operator wants hot-reload (weed out bugs without shutdown/reboot). `docs/bot_v5_shell_architecture.md` exists; whether v5 addresses modularity/hot-reload requires read. Pending.
2. **Deployable rule shape** — atlas measured perfect hindsight per cell. The deployable rule isn't perfect hindsight. Open question: what's the deployable rule shape? Per-cell argmax overfits within-sample. Possible shapes include global X, global r%, per-regime r%, or per-cell-with-pre-specified-smoothness. Resolution comes from paper-mode validation against atlas hindsight rules, not from further hindsight analysis.
3. **Bilateral capture mechanism (B23)** — pairing diagnostic showed 79.3% upstream feasibility. Atlas didn't run bilateral economics. When does it get layered in? Likely after paper-mode validates single-leg execution.
4. **FV-anchor workstream** — operator-flagged: "im obviously going to be attacking this next. this is very very important." Atlas measured taker-floor entries (conservative). FV-anchor work measures actual edge from "Kalshi mid is X¢ below FV" entries. Big. Likely sequenced after execution-lock but before live capital, or threaded into paper-mode validation alongside execution debugging.
5. **Adaptive cell-width binning** — Plex round-4 deferred. Defensible as Layer A smoothing with pre-specified threshold grid; run AFTER atlas to compare emergent band patterns across categories. Future enhancement.
6. **Depth-chain data collection (F33 / G13)** — prospective Kalshi `/orderbook` polling, required for fill-probability modeling at non-BBO maker-post depths. Currently a blocked-track gap.
7. **Rung 1 / exit_optimized_bounce_v1 disposition** — both have committed code on origin/main, neither was run to completion, both ate by the atlas. Preserved not deprecated. Open question: do we ever want to run them retroactively for cross-validation? Or formally retire? Operator call.
8. **Whether 6-27% stable-window coverage means one of three attack vectors must shoulder most of operation's coverage** — open from prior session, possibly addressed by atlas regime breakdown but not formally closed.
9. **Daily-overlap assumption** — the ~$40/day combined operational picture assumes max-overlap days across all four categories. Tour calendars don't always align; actual daily realization will vary. Corpus mean is planning baseline, not daily expectation.

---

## KEY FILE PATHS

**Doctrine docs (`arb-executor/docs/`):**
- `LESSONS.md` (558 lines, A–G categories) — durable principles. Critical: A21 (CIs), A22 (measurement universe), A24 (variable inventory), A32 (operator pushback as probe-trigger), A37 (strict-entry coverage cost), A38 (dual-peak vs settlement), A39 (cents-vs-ROI), A39 amendment, B6 (small-N CIs), B13 (skew-relative thresholds), B14/G17 (premarket vs in-match decomposition), B15 (unit-of-decision per-minute), B16 (Layer A/B/C separation), B23 (bilateral mechanism), B25 (minute-cadence fire_rate undercount), C17 (credential redaction), C19 (lifecycle timestamps), C27 (foundation-pointer discipline), C28 (streaming), C37 (pre-replace gate), C38 (zero-large-fraction = scoping bug), D10 (dynamic lesson numbering), D18 (consult git universe FIRST), E12 (premarket phases), E18 (bilateral capture rate anchor), E32 (locked cell/exit model — load-bearing), E32(e) (every band gets its own exit target), F4 (Apr 17-23 silent fill-detection), F28 (/tmp ephemerality), F33 (depth-chain gap), F34 (formation gate), F35 (recoverable 6.4% tier-3 calibration defect), G19 (candle sparse minute population), G21 (ET on operator surfaces), G22 (three-axis deployment math), G23 (honest provenance discipline).
- `ROADMAP.md` (T/F/U/G/D categories). Read T11a/T11b (Bug 4), T26 (Live trading deployment), T32 (Layer C, demoted), T36 (Layer B v2, open with pre-build revision), T37 (foundation, COMPLETE), T39 (recomputation ladder), T39.1 (Rung 1 superseded-not-deprecated), T39.2 (exit_optimized_bounce_v1 Phase-2-halted-superseded), T40 (n_profile_v1 COMPLETE), T41 (inmatch_bounce_surface_v1 COMPLETE), T42 (atlas COMPLETE).
- `SIMONS_MODE.md` — axiomatic framing. Axiom 2: "The price is not trying to be fair value." Axiom 3: "Mispricing is the default state." Sections 4–6 load-bearing for cell-selection vs execution problem split.
- `TAXONOMY.md` — data tier definitions (A/B/C, G, FOUNDATION-TIER), analysis depth levels 0–6, Section 2.5 GRAIN/VECTOR/OBJECTIVE classification axes.
- `ANALYSIS_LIBRARY.md` — indexed findings catalog with disposition.

**Atlas files (`arb-executor/data/durable/spike_volatility_map/`):**
- 4 LOCKED_DOWN.md files (one per category), PAIRING_DIAGNOSTIC.md, CROSS_CATEGORY_MAP.md (stale; will be deprecated in this Stage 0).
- 4 spike per-N parquets + 12 descriptive parquets (4 categories × 3 widths).

**Producer & bot code:**
- `data/scripts/build_spike_perN.py` (`c5e377f`) — canonical reproducible atlas producer. Takes `--category {ATP_MAIN,WTA_MAIN,ATP_CHALL,WTA_CHALL} --output /path.parquet`.
- `live_v3.py` — current bot (paused). Has `_PAPER_API`, `PaperFillSimulator`, `PaperPosition` dataclass. Bug 4 OPEN.
- `swing_ladder.py` — Kalshi auth pattern reference. Per memory: "Always copy from `swing_ladder.py`'s `_kalshi_headers()` — never reimplement."
- `data/scripts/build_n_profile_v1.py` (`a28840e`) — n_profile_v1 producer.
- `data/scripts/build_inmatch_bounce_surface_v1.py` (`85118d4`) — inmatch_bounce_surface_v1 producer.
- `data/scripts/build_rung1_strategy_evaluation.py` (`5fc6d40`) — Rung 1 producer, **committed not run**.

**Spec docs (`arb-executor/docs/`):**
- `bug4_brief.md` (500+ lines) — Bug 4 spec, OPEN per T11a/T11b. **CRITICAL for execution-lock arc.**
- `bot_v5_shell_architecture.md` — next-gen bot spec. Read for hot-reload questions.
- `layer_b_v2_spec.md` (52 KB) — tick-level exit-policy simulator spec. OPEN per T36; pre-build revision required against T37 foundation.
- `layer_c_spec.md` — realized economics with fees. OPEN per T32, gated on Layer B v2 PASS, demoted by B25.
- `forensic_replay_v1_spec.md` — replay that surfaced B25.
- `per_minute_universe_spec.md` — foundation corpus spec.
- `n_profile_v1_spec.md` — n_profile_v1 spec.
- `inmatch_bounce_surface_v1_spec.md` — inmatch surface spec.
- `rung0_cell_economics_spec.md` — Rung 0 spec v1.1.
- `rung1_strategy_evaluation_spec.md` — Rung 1 spec v0.3.2 (build-ready, producer committed, not run).
- `exit_optimized_bounce_v1_spec.md` — exit-opt v0.4 spec (Phase-1 PASS, Phase-2 halted then gate-fixed, not re-run).
- `recomputation_ladder.json` — 6-rung dependency map for 22 settlement-scored audit entries.

**Data sources (NOT git-tracked, VPS-only by size; sha256 in MANIFEST):**
- `data/durable/g9_trades.parquet` — 33.7M-row tick-level trade tape.
- `data/durable/g9_candles.parquet` — 9.5M-row per-minute candles.
- `data/durable/g9_metadata.parquet` — 20,110-row market metadata.
- `data/durable/per_minute_universe/per_minute_features.parquet` (sha256 `9fde4b5d`) — FOUNDATION-TIER.
- `data/durable/n_profile_v1/n_profile.parquet` (sha256 `a7ed1155`) — per-N foundation.
- `data/durable/inmatch_bounce_surface_v1/surface.parquet` (sha256 `14241db0`).
- `data/durable/rung0_cell_economics/cell_economics.parquet` (sha256 `6fdd019d`) — Rung 0 output.
- `data/durable/kalshi_fills_history.json` — Tier-A fill fact source (7,489 fills Mar 1 – Apr 29).

**Atlas parquets ARE git-tracked** (small enough): `data/durable/spike_volatility_map/*.parquet`.

---

## RECENT COMMIT TRAIL

Most recent first.

Premarket-dynamics arc (2026-05-22 → 2026-05-23, most recent):

- `22f3221` (+ `a4f3cc5`/`0f696f2` docs) — **Path C Phase 1 (T46): 3-feature drift predictor (Plex Round 7 Tier 1).** Real out-of-sample signal: **holdout AUC 0.7298** (>0.62 bar; CPCV 0.6625). paired_arb_gap strongest single feature (within-cell fill lift to 3.5×); taker_imbalance dominant in the model (negative sign). **Key finding: binary skip-gates UNDERPERFORM place-everywhere** (Rule A 9.17% / Rule B 9.36% vs v3 12.11%) — a fill predictor's value is offset modulation, not on/off placement when the fallback is safe (LESSONS A42). Recommend Path C Phase 2 as offset modulation. Outputs on-disk only.
- `648b8db` (+ `ff86121`/`95216b4` docs) — **Path B v3 (T45): per-regime offsets + atlas exit replay (deployable).** Per-(cat×regime) offsets from v1 replace the universal 15¢: **$8,098.50 vs atlas $6,158.20 (+31.5%)** on lower capital ($66,902) → blended ROI **12.11% vs 8.70% (+3.41pp)**, beating T44's +2.93pp by only **+0.48pp (+$269)** — diminishing returns (the incremental is the underdog harvest the universal rule clamped away). Fill 28.4% (vs 15%); baseline exact; gate-4 v3-fill==v1-fill (0.0pp). Outputs on-disk only.
- `a61830c` (+ `5470754`/`23e6898` docs) — **Path B v2 (T44): marketable-vs-resting split + atlas exit replay.** Maker placement realizes **$7,829.30 vs atlas $6,158.20 (+27.1%)** on lower capital → blended ROI **11.63% vs 8.70% (+2.93pp), pre-realism**; baseline reproduced exactly; favorite-driven (universal 15¢ clamps underdog bids to 1¢). Outputs on-disk only.
- `8d2f259` / `41eb0f2` (842d213) / `5e37400` — Path B worked-example charts v3 / v2 / v1 (one paired event each; v3 added the marketable-vs-resting honesty + atlas exit overlay that drove Path B v2's execution split).
- `5bd88b6` / `4f07e5a` — Path B v1 doc-system commits (ROADMAP T43; ANALYSIS_LIBRARY registration).
- `1e00818` — Path B premarket maker-bid fill mechanics (T43). 14,033 N × 42 placement×offset cells; entry-side fill rates only (no PnL, no exit logic). Corpus hindsight entry-improvement ceiling 2.46¢/N; monotonic favorite>underdog gradient (r85_94 ~6.5¢ via 15¢ offsets, r05_14 ~1.1¢ via 2-3¢). Outputs on-disk only; producer `884e951`.
- `7c15776` — Walkover/retirement sanity check. T4 mid-drift gradient NOT robust: removing reversal-prone events (17.7-25% of N by duration proxy) ~halves the extreme-band drift (±11¢ → ±5-6¢).
- `2ca8890` — Scope A corpus premarket map (per_minute_distributions_v1 + per_event_fingerprint_v1, 14,033 N). Headline: monotonic ~±11¢ anchor-regime mid-drift gradient (T4), near-identical across categories.
- `a0bc5e6` — fv_overlap_join_v1 substrate + v3 example chart. Cross-book consensus FV layered on premarket_tape (~3.5% of atlas events have FV coverage; WTA_CHALL 0% per betexplorer scraper gap).
- `7d98e74` — book_prices → durable fv_history archive + daily 02:30 UTC cron (stops the rolling-32-day FV-poll leak).
- `30a47b6` — premarket_tape_v1 substrate (T-4h→T-20m per-minute tape, 2.06M rows, foundation scope).

Atlas arc:

- `d99c6e9` — Pairing diagnostic: 79.3% events have both N's anchored. ATP_MAIN 85.5% / WTA_MAIN 81.2% / Challengers ~74%. Empirical upstream feasibility for B23.
- `d038cb3` — WTA_CHALL descriptive locked. 887 N, 1c +$645/+14.52% across 80 days. ALL FOUR CATEGORIES LOCKED.
- `ec1f593` — ATP_CHALL descriptive locked. 5,326 N, 1c +$2,029/+7.57% across 109 days. 48.86 N/day.
- `c5e377f` — Canonical reproducible producer `build_spike_perN.py`. Reproduces committed ATP_MAIN+WTA_MAIN parquets byte-identical.
- `75603f4` — WTA_MAIN descriptive locked. 1c +$1,825/+9.84% across 3,683 N's, 248 days.
- `481de7f` — ATP_MAIN descriptive locked. 1c +$1,659/+7.90% across 4,137 N's, 252 days. Plex-confirmed methodology.

Plus archived chat-bridge handoff at `docs/handoffs/EXECUTION_PHASE_HANDOFF.md` (commit [hash, filled in post-archive-commit]) covering 2026-05-19→2026-05-20 chat-bridge methodology arc with documented gaps.

Pre-atlas analytical arc (2026-05-15 → 2026-05-19):

- `9912660` — Spike volatility map ATP_MAIN + WTA_MAIN per-N parquets (corrected untruncated size-qualified spike).
- `b5c837c` — LESSONS D18 (chat-side failure mode: reason from data not from priors; consult git universe FIRST).
- `5fc6d40` — Rung 1 producer (build to spec v0.3.2). **Committed not run.**
- `3bbac37`, `c916c50`, `ba09107`, `59c3f14` — Rung 1 spec v0.3.2 / v0.3.1 / v0.3 / v0.2 patches.
- `6f1d4bd` — Register `inmatch_bounce_surface_v1` CANONICAL. 7/7 gates PASS full cohort, sha256 `14241db0`.
- `0e94959`, `85118d4`, `11dce1c` — inmatch_bounce_surface_v1 v0.3 / v0.2 / spec.
- `de62d7f`, `d23fff5`, `5020f10`, `8e8f46e` — exit_optimized_bounce_v1 spec v0.1 + producer v0.2/v0.3/v0.4. Phase-1 PASS, Phase-2 halted then gate-fixed. **Not re-run.**
- `c9a0f3e`, `c76eee5` — n_profile_v1 MANIFEST + ANALYSIS_LIBRARY register. sha256 `a7ed1155`.
- `a28840e` — n_profile_v1 Pass-1 OOM remediation (Phase-3 validated at full corpus). **The producer commit of record.**

Pre-arc context: `7911478` CHAT_HANDOFF post-Rung-0 landing (2026-05-15); `44c9ec6` SESSION_HANDOFF stale-path fix (2026-05-14); `19fdd5a` F35 / T37-RECAL canonicalization.

---

## IMMEDIATE NEXT ACTIONS (post-Stage-0)

0. **Premarket-dynamics arc landed (2026-05-22 → 2026-05-23).** Chain: premarket_tape_v1 (`30a47b6`) → fv_history archive + cron (`7d98e74`) → fv_overlap_join_v1 (`a0bc5e6`) → Scope A corpus map (`2ca8890`) → walkover/retirement check (`7c15776`) → **Path B fill mechanics (T43, `1e00818`)**. Net empirical picture: the atlas T-20m taker anchor (T42, locked exit) can be entered earlier as a maker for a per-regime expected entry-improvement of up to ~2.46¢/N (hindsight ceiling), strongly favorite-skewed (Scope A T4 drift gradient is the mechanism; walkover check shows ~half the extreme drift is reversal-driven so the deployable signal is the completed-match ~±5-6¢ gradient). **Next:** the bid-laying policy spec can now be drafted from Path B's per-regime fill rates (entry side) layered on the locked atlas exit — it is its own T-item, not yet opened.
1. **This Stage 0 reconcile completes first** — eight commits land before any new execution-phase work:
   1. SESSION_HANDOFF.md rewrite (this doc)
   2. CHAT_HANDOFF.md → pointer stub
   3. ANALYSIS_LIBRARY.md (T40/T41/T39.1/T39.2/T42 entries)
   4. ROADMAP.md (T40/T41/T39.1/T39.2/T42 added; T36/T11/T32 statuses confirmed; execution-phase sequence noted)
   5. MANIFEST.md (atlas entry with sha256s and producer commit)
   6. CROSS_CATEGORY_MAP.md (deprecation header pointing to LOCKED_DOWN + PAIRING_DIAGNOSTIC)
   7. README.md (current-state + next-major-step updates)
   8. docs/handoffs/EXECUTION_PHASE_HANDOFF.md (archive with prefix note flagging known gaps)
2. **Read `bot_v5_shell_architecture.md`** — operator-pending recommendation on v5 vs v3 for hot-reload.
3. **Bug 4 implementation** — operator review of `bug4_brief.md` is required before CC prompt drafting. 500+ lines, settlement-state-mechanics-dense; mandatory operator eyeball before any CC prompt.
4. **Layer B v2 spec revision** — per T36 amendment, spec must be revised against T37 foundation before producer build.
5. **Paper-mode integration test suite** — design after Bug 4 lands.
6. **Capital deployment plan** — after paper-mode validation against live tape. Far-future tracking per T26.

---

---

Latest landed analysis: **Path C Phase 1 — 3-feature drift predictor (T46)**, analytical commit `22f3221` (2026-05-23). Tests whether T-4h features predict whether a maker bid's fill level is reached: **holdout AUC 0.7298 (>0.62 bar; CPCV 0.6625)** — real out-of-sample signal. paired_arb_gap is the strongest single feature; taker_imbalance dominates the model (negative sign). Key finding: binary skip-gating underperforms place-everywhere (Rule A/B 9.17%/9.36% vs v3 12.11%) — the predictor's value is offset modulation, not on/off placement (LESSONS A42). Doc commits `a4f3cc5` (ROADMAP T46) + `0f696f2` (ANALYSIS_LIBRARY) + this update + LESSONS A42. Preceding: Path B v3 (T45, `648b8db`), v2 (T44), v1 (T43), worked-example charts v1/v2/v3.

**The bid-laying policy spec is the open downstream T-item.** Empirical inputs now in hand: (a) deployable shape = per-regime offsets (T45), marketable→taker / resting→maker branch (A41), atlas exit from entry (T44/T45); (b) pre-realism ceiling +3.41pp blended over the +8.70% atlas floor → ×B25 realism (0.5-0.7×) for the deployable estimate; (c) per-regime conditioning is a +0.48pp refinement over a universal favorite offset (diminishing returns — don't over-engineer the offset table); (d) a T-4h drift predictor has real signal (holdout AUC 0.73, T46) but must be deployed as offset modulation, not skip-gating (A42) — Path C Phase 2 is the open item that would test whether modulated offsets beat v3's +3.41pp.

End of handoff.
