# INDEPENDENT AUDIT — WINDOW-1 T1 SCORING EXECUTION RESULTS @ d710ba06 — RULING: PASS

**PASS. All 6,432 event rows across the eight frozen T1 result ledgers reproduce exactly through an independent driver (0 row-level differences); every reported C/PC/IC/S count and PC/D rate is exact; execution integrity holds (one attempt, zero retries, eight scorer invocations, correct authorization bindings, only the named results directory added); metric law verified with zero violations and zero silent PC→IC tightening. The causal reconciliation below is receipt-backed, including the decisive finding that response-only is a behavioral no-op whose PC deficit vs the parents is an admission-law surface difference, while persistence — lawful on every receipt — measurably destroyed 20–28 PC per candidate.**

Date: 2026-07-27 · Branch: `audit/window1-independent` · Additions-only child of `07ec71e7aecc643750a2deb618ff06a029f263fb` · Auditor: independent CC session
Under audit: `d710ba0606084f67625e255e87ebad1cd016bf6a` on `codex/window1-definition`.

## 1. Lineage, execution, containment — PASS

d710ba06 is the **sole child** of package `bbf6f632`; remote tip equals it; the diff is **15 additions, all inside `.claude/window1_t1_results_w1-t1-dev-20260712-20260720-grid1-scorepkg-v1/`, zero modifications/deletions**. The execution manifest binds the branch-recovery authorization `07ec71e7` and its report path, the exact execution ID, the exact input-bundle SHA `67a9166a…`, and the frozen command with correct substitutions; **one wrapper attempt, retry_count 0, exactly 8 scorer invocations, exit 0, no failure artifact**. The Round-2 evidence directory in the stale worktree is present, untracked, and verifies against its **own creation-time OUTPUT_HASH_MANIFEST (5 entries, 0 drift)**; the externally claimed manifest SHA `56e47204…` uses an unspecified hashing law not reproducible from audited materials — byte-integrity is proven by the stronger internal check. No holdout/live/network access; no candidate mutation, ranking, or rerun.

## 2. Independent row-level reproduction — PASS, zero differences

My own orchestration (never invoking execute mode, writing no results directory) loaded the frozen package inputs, adapted the 3,840-row unique fill ledger through the byte-identical audited adapter, derived all 1,608 references through the byte-identical audited reference adapter, and scored all eight candidates. **All 8 × 804 event rows are identical to the committed ledgers; all eight summaries identical; all 14 output hashes verify.** Every reported aggregate reproduces exactly:

| candidate | C | PC | IC | S | PC/D | PC-not-IC |
|---|--:|--:|--:|--:|--:|--:|
| hold response-only | 131 | 115 | 37 | 100 | 14.3035% | 78 |
| hold target-completeness | 134 | 114 | 36 | 101 | 14.1791% | 78 |
| hold persistence-only | 102 | 93 | 34 | 79 | 11.5672% | 59 |
| hold full-stack | 94 | 88 | 32 | 77 | 10.9453% | 56 |
| micro response-only | 123 | 109 | 34 | 94 | 13.5572% | 75 |
| micro target-completeness | 128 | 109 | 35 | 95 | 13.5572% | 74 |
| micro persistence-only | 98 | 91 | 32 | 77 | 11.3184% | 59 |
| micro full-stack | 94 | 88 | 33 | 77 | 10.9453% | 55 |

## 3. Metric law — PASS

Verified on every completed row: PC ⇔ combined pair delta strictly < 0 (never both-legs-negative; PC-but-not-IC = 55–78 per candidate proves no tightening); combined-zero rejected; IC diagnostic only; S = cost < 100, independent of PC; fee frozen at 0; reference-missing/ambiguous completions retain C and S with PC/IC unavailable; D = 804 conserved on all eight; **zero silent PC→IC tightening rows** (no completed pair with combined < 0 scored non-PC). Positive-d2 fills were eligible whenever the strict combined budget allowed — none occurred (see §6).

## 4. Parent-vs-T1 census — receipted (PARENT_VS_T1_EVENT_DIFF_CENSUS.json)

Every T1 candidate compared against its correct frozen parent ledger, with exact event-ID sets, transition matrices, and per-event first causal divergences (candidate-normalized action streams):

- **response-only:** hold PC 115 = 116 retained − 1 lost; micro 109 = 111 − 2. Zero gains, zero other class changes beyond the lost events → naked.
- **target-completeness:** hold C +7/−5 (134), PC +3/−5 (114); micro C +8/−5 (128), PC +3/−5 (109); 2–3 completed-non-PC gained.
- **persistence-only:** hold C −30, PC −23 (93); micro C −27, PC −20 (91); all losses → naked-gained.
- **full-stack:** hold C −38, PC −28 (88); micro C −31, PC −23 (88).

## 5. Mechanism-specific causal findings — receipted (MECHANISM_OUTCOME_CENSUS.json)

**Response-only finished below the parents for a non-behavioral reason.** All three deficits (PASKRU both regimes; FEAWAL micro) have **T1 stream fill facts byte-identical to the parent stream facts**, both landing after the guarded cutoff (KRU X=30 @ 1783934608.97 vs cutoff 1783932900.0; FEA X=46 @ 1783883078.08 vs cutoff 1783882200.0). The T1 scoring package admits only in-window frozen simulated fills; the parent results package credited guarded FILLABLE_AT_X within the window (KRU@36, FEA@48). Response-only produced **zero true behavioral C/PC changes** — its 476,710 explicit decisions were all HOLDs on already-active exposure.

**Target-completeness raised C but not PC** because its genuine gains (+4C/+3PC hold, +5C/+3PC micro — new in-window fills at complete headroom targets) were offset by 5+5 previously-PC events whose modified exposure sequence shifted the eventual fill fact past the cutoff, and because 2–3 of the gained completions are completed-non-PC.

**Persistence sharply reduced C and PC through lawful HOLDs.** Every lost event carries `t1_persistence_hold` receipts on the lost leg. Refined per-leg taxonomy: hold-persistence 30 C losses = 24 behavioral shifted-fill-landed-post-right + 5 true never-filled + 1 admission artifact; micro 27 = 18 + 7 + 2. Lawful queue preservation measurably missed the later reprice path that filled the parent in-window — **lawful is not good: −23/−20 PC**.

**Both full stacks converged to C=94/PC=88 because their C event sets are IDENTICAL (94 shared events).** Persistence dominates the stack and pins sibling exposure to the same held prices in both regimes, erasing the macro-context gap that separates the parents (C 132 vs 125); only IC differs (32 vs 33).

## 6. Positive-d2 attrition funnel — receipted (POSITIVE_D2_HEADROOM_ATTRITION.json)

All 82 pre-run selected positive-d2 targets traced: **82 constructed = 82 selected → 10 suppressed by persistence HOLD retaining the prior price → 72 exposed at the selected X → 72 with no lawful fill evidence ever appearing at that price → 0 filled → 0 completed → 0 PC.** The zero is **10 persistence retention + 72 genuine observed non-execution at the exposed maker price** — not target supersession beyond the 10, not scorer exclusion, not first-leg/reference arithmetic, and not tightening (explicitly tested: zero). Headroom was computed and consumed (exposed); the market never printed or asked through those +1-cent targets inside the window.

## 7. Prior-defect migration outcomes — receipted

- **48 response rows:** 48 streams changed, 0 credited fills changed, 0 C, 0 PC — **48 outcome-neutral** (explicit decisions replaced silence; no executions changed).
- **8 target-completeness rows:** 8 streams changed, 2 credited fills changed, 2 C, 2 PC — **2 improved, 6 neutral**.
- **34 persistence rows:** 34 streams changed, 0 credited fills/C/PC changed on the fixture events themselves — **34 neutral** (the persistence damage occurred on *other* events).
- **2 capacity rows:** diagnostic-only, no conversion claim, unchanged.

## 8. Ruling and scope

**PASS.** Execution integrity, independent reproduction, metric law, and every reported aggregate reproduce exactly. This validates **these eight frozen results only** — it is not a market ceiling, an opportunity rate, a full-OS verdict, or proof that Window-1 drift is absent.

## Causal findings for the coordinating Codex tuning task (findings only; no strategy proposed)

1. **Response-keyed decisions changed nothing that executes.** Every applicable decision point already carried active sibling exposure; the 24-row defect was informational silence, not missing exposure. The apparent −1/−2 PC is an admission-surface artifact (in-window simulated-fill law vs parent FILLABLE_AT_X law) on exactly three events whose fills sit just past the guarded cutoff.
2. **PC creation on this tape came only from target completeness** (+3 PC per regime, from new in-window fills at complete headroom targets), and its cost was fill-timing displacement on 5 previously-PC events per regime (shifted fill facts landing post-right). Net −2 PC as frozen.
3. **Persistence, as specified, is strictly PC-destructive on this tape** (−23/−20 alone; dominant in full-stack −28/−23): holding lawful maker exposure forfeits the reprice-path fills that produced the parent's completions, converting them to post-right fill facts (24/18) or no fill at all (5/7). Any retained persistence needs a receipt-backed exit trigger tied to fill-probability decay, not price-lawfulness alone.
4. **The 82 positive-d2 headroom targets are exposure-complete but execution-dry:** 72 were exposed and never crossed; 10 were held away by persistence. Positive-d2 PC requires the market to trade through bid+1 inside the window — which never happened once in 82 exposures on this tape.
5. **Full-stack convergence shows persistence erases the macro-regime distinction entirely** (identical 94-event C sets); regime-level tuning cannot act through a persistence-dominated stack.
6. **Scoring-surface note:** parent-vs-T1 comparisons mix two audited fill-admission laws on boundary-straddling fills (3 events). Any future comparison intending behavioral attribution should hold the admission law fixed across both sides.
