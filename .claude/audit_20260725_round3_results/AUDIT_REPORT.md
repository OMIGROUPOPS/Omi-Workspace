# INDEPENDENT ROUND-3 RESULTS AUDIT @ 754415bb — READ-ONLY, NOT SCORED, NOT RERUN

**Status: EXECUTION AND RESULTS ADMISSIBLE. Best candidate independently reproduced: PC = 6/804 (target 603). The dominant failure has MOVED: it is no longer partner-leg starvation — it is lawful maker orders that do not fill.**
Date: 2026-07-25 · Branch: `audit/window1-independent` · Auditor: independent CC session
Method: detached read-only worktree at `754415bb`; all hashes verified against git blobs; every metric recomputed from the raw per-event ledgers; decision streams joined to outcomes for causal decomposition; zero scoring/rerun/tuning; holdout untouched; no production access; no Round-4 built.

## 0. Prior art (C45 gate)

`f09c9ae7` (my execution authorization of package `6daab089`), `b415a98e` (Round-3 PRE-RUN audit: 1,160 reaim proofs, starvation forensic 16/16/16/4/8), `807e2c86` (Round-2 results: all PC=0, 82 single-leg fills). Delta: first audit of executed Round-3 results; adjudicates whether the starvation repair changed the outcome and why the miss persists.

## 1. Legality of the execution — PASS on every check

- `754415bb` ("record Round-3 development execution") is the **sole child** of the authorized package `6daab089` and the remote tip of `codex/window1-definition`; the diff is **purely additive and is exactly the frozen 19-artifact output inventory** — nothing else, so every frozen surface is byte-identical by construction.
- All 18 OUTPUT_HASH_MANIFEST entries reproduce from git blobs (sizes included). PROGRESS.log equals the frozen 20-line contract byte-for-byte (with the real `git_sha=6daab089…` substituted); STDOUT.log == PROGRESS.log; STDERR empty; console echo never failed.
- One attempt: start 16:37:54Z → end 17:13:59Z (36 min), exit 0, `candidate_scorer_invocations_completed: 8`, exactly one scorer invocation per candidate in frozen order, no failure artifact, no retry/resume, results directory created once.
- Bundle binding: `input_bundle_sha256 = 7dec1673…` exact; execution ID exact; controlling identities (Round-2 results + audit, Round-3 PRE-RUN + audit, both report blob OIDs) embedded in the receipts.
- Non-access proof: holdout unopened/unqueried, 0 network calls, 0 live-exchange calls, empty production/config/order/position/Window-2/exit/settlement/DCA path lists; independently corroborated — every ledger row's date lies in July 12–20 and the commit touches nothing outside the results directory.

## 2. Independently reproduced metrics (from raw ledgers; report totals matched EXACTLY on every candidate — zero mismatched keys)

| Candidate | C | PC | S | IC | C/D | PC/D | PC/C | exact5 | partial | naked | nonfill | zero-len | contra | censored | Σ |
|---|--:|--:|--:|--:|--|--|--|--:|--:|--:|--:|--:|--:|--:|--:|
| pair_presence·park_join·hold | 3 | 3 | 3 | 2 | .0037 | .0037 | 1.00 | 3 | 0 | 281 | 332 | 13 | 14 | 161 | 804 |
| **pair_presence·park_join·reaim** | **6** | **6** | **5** | **3** | .0075 | **.0075** | 1.00 | 6 | 0 | 278 | 332 | 13 | 14 | 161 | 804 |
| pair_presence·touch_park·hold | 3 | 3 | 1 | 0 | .0037 | .0037 | 1.00 | 3 | 2 | 165 | 446 | 13 | 14 | 161 | 804 |
| pair_presence·touch_park·reaim | 3 | 3 | 0 | 0 | .0037 | .0037 | 1.00 | 3 | 2 | 165 | 446 | 13 | 14 | 161 | 804 |
| causal_steer·park_join·hold | 3 | 2 | 2 | 1 | .0037 | .0025 | 0.67 | 3 | 2 | 264 | 347 | 13 | 14 | 161 | 804 |
| causal_steer·park_join·reaim | 4 | 3 | 2 | 2 | .0050 | .0037 | 0.75 | 4 | 2 | 263 | 347 | 13 | 14 | 161 | 804 |
| full_os·walk_park·hold | 1 | 1 | 1 | 1 | .0012 | .0012 | 1.00 | 1 | 0 | 38 | 577 | 13 | 14 | 161 | 804 |
| full_os·walk_park·reaim | 1 | 1 | 1 | 1 | .0012 | .0012 | 1.00 | 1 | 0 | 38 | 577 | 13 | 14 | 161 | 804 |

Every census is mutually exclusive (single classification field, closed 8-bucket vocabulary incl. `other_quantity`=0 everywhere) and sums to 804. Zero duplicate event/leg/fill/receipt identities; zero fills after any leg's boundary; per-leg fill-receipt quantities cross-foot to inside-window quantities everywhere; C/PC/S/IC row flags match my derivations on all 6,432 rows. Combined-cost ranges (completed pairs): best candidate 90.64–100.0¢ (median 98); combined-delta ranges all negative for pair_presence candidates (best: −18.36…−2.0); individual-leg delta signs over all 24 completed duals: **34 negative, 5 zero, 9 positive**. The claimed best-candidate profile (C=6, PC=6, S=5, IC=3; 332/278/13/14/161) **reproduces exactly**. Best PC truly equals **6/804**.

## 3. Every claimed completed dual, individually audited — 24 candidate-duals over 11 unique events, ALL VALID

All 24: both legs exactly 5.0, receipt-identified causal fills (receipt IDs unique), every fill timestamp ≤ that leg's independently lawful guarded boundary, boundary status positive on both legs, entry VWAPs and W1-close references present, combined cost = sum of leg VWAPs, combined delta = sum of individual deltas (exact cross-foots). No schedule substitution, proxy fills, synthetic transitions, duplicate receipts, or post-boundary fills anywhere. Unique completing events (sanitized IDs) and completing candidates:

- `…26JUL19BOHBOU` — all 8 candidates (e.g. best: cost 90.64, deltas −10.0/−8.36, Δ −18.36 → C/PC/S/IC)
- `…26JUL15CERKEC` — both park_join families ×(hold, reaim)
- `…26JUL19VUKGEA` — pair_presence·park_join ×2 · `…26JUL19MCKOUA` — causal_steer ×2 · `…26JUL16RICGEA` — touch_park ×2
- Reaim-only conversions: `…26JUL15COLSON`, `…26JUL17TABTIR`, `…26JUL18SHETSI` (park_join), `…26JUL14GOMMCD` (touch_park), `…26JUL15WOLJOH` (causal_steer)
- Hold-only: `…26JUL20SURKUZ` (touch_park hold completed; reaim **lost** this dual)

## 4. Anatomy of the miss — the failure class has CHANGED

Joining the frozen decision streams to ledger outcomes, for **every** candidate:

- **Every naked-single event had the sibling order POSTED before its cutoff and simply unfilled** — `sibling_posted_but_unfilled` = 281/278/165/165/264/263/38/38; **`sibling_never_placed` = 0 across all eight candidates.**
- **Every genuine-nonfill event had BOTH legs posted with zero fills** — `both_legs_posted_no_fill` = 332/332/446/446/347/347/577/577; one-leg-only or never-posted = 0.
- Round 2's starvation categories (sibling never called: 16; eligibility after cutoff: 16; reaim without trigger: 16; partial-response not armed: 4) are **eliminated** — the Round-3 repair (first-lawful-BBO presence, advisory t_deep, partial-fill arming) did exactly what it froze. Price/size/identity rejections: none recorded as fill-preventing states; missing-feature censor is its own bucket (161, identical across candidates — no candidate newly censored anything); contradictory (14) and zero-length (13) are boundary states, unchanged. **No unexplained state remains: 804 = duals + posted-but-unfilled naked + both-posted nonfill + censored + contradictory + zero-length + partial (touch/steer 2) for every candidate.**
- For the best candidate specifically: 278 games stranded one filled leg because the partner's lawful maker order rested unfilled to the cutoff; 332 produced no pair because both lawful maker orders rested unfilled. The binding constraint is **fill-through probability at the frozen posture prices**, not eligibility, wiring, or arming.

## 5. NO_CALL units — NOT game counts

Ledger sums equal frozen stream action-row counts exactly. **cohort_NO_CALL (0,0,0,0,1471,1471,1471,1471)** counts **per-leg cohort-consultation decision rows** in the order stream — 1,471 rows spread over 777 events (≈1.9/event; max 2 per event) for each steer/full_os candidate; pair_presence never consults cohort. **reaim_NO_CALL (0,324,0,347,0,354,0,288)** counts **armed-sibling evaluations that found no lawful later trigger** — e.g. 324 rows over 319 events (up to 2/event). Both are repeated stream-decision evaluations, and presenting either as a game count would be wrong; the game denominators are 777 and 319/345/348/280 respectively.

## 6. The eight frozen candidates — causal comparison

**hold vs reaim** (pre-registered changed-order events → outcomes): park_join 322 changed → **+3 duals** (all three singles→duals: COLSON, TABTIR, SHETSI; +1¢ cost on each; improvement_class "both"); causal_steer 291 → **+1** (WOLJOH); touch_park 269 → **+1 gained, 1 LOST** (GOMMCD gained, SURKUZ lost — net C 0, S −1: the +1 repost surrendered queue position on an order that would have filled); full_os 278 → **0**. Everything else was moved/reposted orders that still never filled. **Why hundreds of changed orders yield ≤6 pairs:** the reaim change is a +1-cent improvement to an already-resting unfilled maker order; it converts only when the tape trades through the improved price before the guarded cutoff — 3/322, 1/269, 1/291, 0/278 events. It also carries a real cost (one lost dual, S degradation at the 100¢ boundary: touch_park reaim S=0 because improved costs crossed 100¢).

**park_join vs touch_park vs walk_park:** touch postures fill single legs less often overall (165 naked vs 281) but complete the same 3 duals at worse cost (99–102¢ vs 89.6–98¢, S collapses); walk_park (full_os) fills almost nothing (38 naked, 1 dual, 577 nonfill) — its deeper parked prices almost never get reached. park_join is the most productive posture on both fills and cost.

**pair_presence vs causal_steer vs full_os:** the steering families really ran their machinery (per-candidate stream rows: drift 1,596, orientation 1,608, top-5 1,207–2,792, cohort all-NO_CALL n<30) and produced 1,720–4,095 reprices vs pair_presence's 785–977 — yet completed **fewer or equal** duals (3–4 vs 3–6) with one PC-losing positive-delta dual (causal_steer hold: Δ +4). Extra steering movement did not convert to fills; it mostly reshuffled resting orders and occasionally degraded outcomes.

## 7. System coverage vs the Living Vault / OS lineage

Faithfully used and genuinely exercised (real order effects in the streams): pair law, per-leg asynchronous timing, park/join/touch/walk postures, divot recognition + latent recut cells (queue-preserving; 198,617 latent updates, 27,896 micro-divots per candidate), positive-print receipt-identified recuts, first-fill sibling response (591/554/586/518 armings; 325/271/292/287 applications), true prints with duplicate exclusion, BBO/top-five pressure (where bound), content-bound own-order receipts. Reduced to no-decision by *evidence*, not by wiring: cohort steering (every consultation NO_CALL at n<30 — named, correct per Vault law). Declared unavailable and NOT proxied (Vault-compliant): the sealed dual-divot pair-policy object, Pinnacle/FV bookmaker surface, proved full depth, independent shape mapping, schedule-revision chain. FV-anchor omission is Vault-mandated (superseded doctrine). **`full_os` is NOT the complete historical OS** — it is the fullest lawful research binding of it: the walk/park + steering family minus the five declared-unavailable surfaces. No component was silently omitted, bookkeeping-only, or proxied; every gap is named and evidence-blocked. I verify the *executed* streams match this claim (the run scored the exact streams audited at `b415a98e`).

## 8. Final ruling

1. **Admissible.** Lawful single execution of the authorized package; all receipts, hashes, and contracts reproduce; no selection/tuning/holdout/production contact.
2. **Reproduced metrics:** table in §2 — matches the report exactly on every number.
3. **Best PC = 6/804 confirmed** (pair_presence·park_join·reaim; PC/D = 0.75%; target 603 missed by 597).
4. **Round 3 proves:** the Round-2 partner-starvation chain is *fixed* — every leg now establishes lawful presence and every stranded partner had a resting order; reaim's later +1 response is real and net-positive for park_join (+3 duals at +1¢); the instrument is deterministic and the full mechanics run without wiring defects.
5. **Round 3 does not prove:** a market ceiling; that no OS policy family can reach 603 (only these eight frozen candidates were tested, minus five declared-unavailable evidence surfaces); anything about July 24–26; anything about live performance; and 6/804 does not validate PC as attainable at target under passive maker posting.
6. **Dominant failure: unfilled lawful maker orders** — posted-but-unfilled partner legs (278 best-candidate) and both-posted-no-fill events (332). Not starvation, not eligibility/NO_CALL restriction (units clarified in §5), not censoring (161 fixed), not omitted machinery.
7. **This is a frozen candidate-family ceiling** — specifically a *passive-maker fill-probability* ceiling of these posture/price laws on this slate. It supports no broader claim about the market or about all OS policies.
8. **Discrepancies/defects: none material.** Notes: (a) touch_park·hold contains a completed dual at combined cost 101¢ and touch_park·reaim at 100–102¢ — lawful (S correctly excludes them; the ≤100¢ pair-order guard applies to maker *prices at post time*, and reaim's +1 improvements crossed the S threshold), (b) causal_steer·hold contains a PC-failing dual with Δ = +4 (correctly not PC), (c) NO_CALL counts must never be quoted as game counts (§5), (d) the Round-2 preserved grid1 evidence remains untouched in the old worktree (execution correctly ran from a clean checkout).
9. **Smallest lawful Round-4 correction (named only — NOT built, NOT scored, NOT authorized):** attack fill-through, not presence. One new pre-registered posture axis on the existing pair law: cutoff-aware price laddering — the resting maker order may take a bounded number of lawful +1 steps toward the executable side as the guarded cutoff approaches (walk-cap-bounded, print-triggered, queue-preserving between steps, maker-only, pair-cost-guarded), replacing the single one-shot +1 reaim. Everything else — D=804, metric contract, guards, dates, scorer, candidate-freeze discipline, one-attempt law — unchanged. It must arrive as a frozen PRE-RUN with its own independent audit before any execution.
