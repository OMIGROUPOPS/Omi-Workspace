# Independent cross-audit — Codex Window-1 OS-family development result

- Audited object: `origin/codex/window1-definition` results commit `f7cd420951f074104dbc602b84137c5eed7455da` ("Record corrected Window-1 development result"), declared PRE-RUN parent `bb7f994305334fcc95a57ce261f5e90385458798` (v3 freeze).
- Audit lane: `audit/window1-independent`. This audit read committed artifacts and code at f7cd4209 in a detached worktree; it ran no new strategy search, built no competing simulator, opened no holdout, and touched no live surface.
- Method: independent re-implementation of the classification/metric laws from the written contract, applied to the committed per-event ledger (`WINDOW1_OS_FAMILY_SELECTED_EVENTS.jsonl`, 804 rows) and results JSON; full code reading of `window1_os_family_search.py`, `window1_fit_benchmark.py` (pricing/action/outcome path), `window1_execution_kernel.py` (fill law), `window1_start_guard.py`; hash verification of all 30 PRE-RUN repository receipts against git blobs; execution of the 15 committed tests (all pass).

## Headline verdicts

| Gate | Verdict |
|---|---|
| PRE-RUN FREEZE | **PASS** |
| EXECUTION REPRODUCIBILITY | **PASS** (ledger-level; see scope bound) |
| FULL-OS-FAMILY CLAIM | **FAIL** (execution real; the "all families executed and affected decisions" reading is not supported) |

Independently reproduced from the committed ledger, all matching Codex exactly:

- **D = 804** (unique event ids; conservation 10 + 0 + 0 + 678 + 14 + 102 = 804)
- **C = 10**, **PC = 9**, **S = 9**, **IC = 4**
- exact-five 10, partial 0, other-quantity 0, nonfill 678, contradictory 14, censored 102
- PC/D = 1.12%, C/D = 1.24%, PC/C = 90%, S/C = 90%, IC/D = 0.50%
- optimistic-queue completions = 26 (reproduced)
- by-date, by-tournament-class, by-start-source-class tables all reproduce the report exactly (receipt: `REPRODUCTION_RECEIPT.json`)
- zero flag mismatches: every PC event has exactly 5.0 shares on both legs, both completions at or before the strict positive cutoff, and strictly negative combined delta; every IC event has both individual leg deltas strictly negative; the one non-PC completion (JACTRU, cost 101, pair delta 0) is correctly excluded under the strictly-negative law.

**Is C=10 / PC=9 trustworthy?** Yes, for the selected policy `drift_cohort_orientation__walk__reaim` under the frozen instrument: the numbers reproduce exactly, the fill law is causal and size-aware, the selected family's decision clock is causal (T-6h delay enforced before any order), no schedule-only or live-by-only event produced a positive, no holdout date appears anywhere, and the guard object is printed beside all 718 verdict-capable events. The caveats below concern non-selected candidate rows and labeling, not the headline.

## Q1 — Counterfactual generation vs replay: COUNTERFACTUAL (genuine)

`build_actions` generates maker orders from the policy law (price = best_bid − max(enabled frozen surface depths), clamped to ask−1, never marketable) at snapshots from the frozen 804-event market cache. Fills are simulated by `simulate_candidate_actions` against public true prints only: sell-flow prints (`taker_side=="no"`) strictly below the order price fill it outright; same-price prints fill it after debiting `queue_ahead` (book size at the level at posting time) in the lower case, or with zero queue in the upper case. Nothing in the search path calls `replay_historical_execution` or reads private fills; grep confirms zero usage. This is not a reclassification of historically logged placements.

Two fidelity caveats:
- The candidate spec (`WINDOW1_OS_FAMILY_CANDIDATES_V1.json` v2) promises walk advances via a "verified **non-self** true-print chain" advancing "one cent"; the implementation gates walk moves on any sell-flow print at/below the current price (no self-print exclusion exists anywhere in the cache or runner) and jumps directly to `min(best_bid, ask−1)` rather than one cent. Bounded impact (the walk ablation moves C by 1), but the spec text over-promises what the code does.
- Own historical resting size is included in `queue_ahead` (conservative) and own historical prints count as fill evidence (standard replay assumption); acceptable, but "own-order fingerprints" were never used to separate the two.

## Q2 — Did six families / 24 policies / nine surfaces execute and affect decisions?

All 24 policies ran over all 804 events (D enforced per candidate); all nine parameter surfaces (band_map, sealed, divot, drift, cohort, orient, recut, atlas, reach) were loaded, hash-verified, and evaluated per leg. But by tier:

| Tier | Finding |
|---|---|
| Present in metadata | All 16 feature families, 6 OS families, 9 surfaces. |
| Loaded by adapter | All 9 surfaces (hash-bound). |
| Evaluated | 8 of 9 surfaces feed depth candidates or quantile calls; shape corpus never evaluable (no independent causal cell mapping — correctly not imputed). |
| Capable of changing an order | divot, sealed, drift-recognition, cohort, orient, recut, atlas — yes in principle. **reach (takerreach LAW) is structurally incapable**: `reach_rate` is computed and stored but never read by any pricing or action path; it only gates the `atlas_and_reach` coverage flag. |
| Actually changed ≥1 event | divot (price base, all families); recut+atlas (define the recut family's prices — its C=2 differs); t6 recognition delay (drift/mirror vs pair differ); walk (drift walk_hold C=6 vs park_hold C=4; ablation C 10→9); first-fill reaim (largest lever: ablation C 10→6); top-five pressure and bookmaker FV (alter causal_micro/full prices — those families' counts differ). **Zero observable effect anywhere: drift recognition, cohort steering, orientation prior, and (for the selected candidate) sealed bands** — the four `drift_cohort_orientation` candidates are deep-equal to the four `mirror_deceleration` candidates at every committed reporting granularity (full summary objects identical including group tables and distributions), and the without_drift_recognition / without_cohort_steering / without_orientation_prior / without_sealed_bands ablations are identical to the unablated selected result. |

Consequence: the six declared families collapse to at most four distinct decision behaviors (pair-divot, drift≡mirror, recut-atlas, causal-micro, full-stack — with drift and mirror identical). "Six OS families executed" is true only nominally.

## Q3 — Missing features were NOT converted to nonfill; the collapse claim is refuted

- No event required all 16 families: completions occurred in coverage classes 7, 8, and 9 of 16; zero events had all 16 (reproduced).
- When no surface produced a depth (no lawful bid expressible), the runner emitted no order → `missing_placement_evidence` → **censored**, not nonfill. Exactly 11 such events (10 missing-placement + 1 no-causal-birth-book) sit inside the 102 censored.
- Censored decomposition (reproduced): 85 start-boundary (99 no-cutoff minus 14 contradictory) + 11 missing-placement/no-book + 6 queue-ambiguous (upper-complete but lower-incomplete).

## Q4 — What the "26 optimistic-queue completions" bounds

The 26 is computed from causal, size-aware public prints applied to **counterfactually generated candidate orders** — not historical placements. But it is candidate-specific: per-candidate values across the frozen grid range from 1 (dynamic_recut park hold) to 26 (the drift/mirror reaim twins); pair reaim = 17, causal_micro reaim = 10–11. So 26 bounds **the selected candidate's (and its decision-identical twins') order stream under a zero-queue assumption** — which is also the grid maximum, so it lawfully bounds *the frozen 24-candidate grid*. It does **not** bound the market, or any policy that prices differently (e.g., at the touch, or with per-leg timing). The report's phrasing "only 26 events complete under the optimistic same-price queue bound" under a "Data/start ceiling" heading invites the broader reading and should be scoped to the grid.

## Q5–Q7 — Reproduction: PASS (details above; receipt committed)

## Q8 — The 678 nonfills decompose; two labeling defects

- **582** events: both legs posted counterfactual orders, zero fills under both queue cases — genuine candidate decisions (deep passive bids at bid−depth) with full causal tape evidence.
- **84** events: **exactly one leg filled 5.0 and the partner never completed** — naked singles. Genuine decisions, but the report nowhere discloses that 84 of the "nonfills" are half-filled pairs (an economically material risk shape; in live trading these are the starved-partner exposures the Vault documents).
- **12** events: the guarded start precedes T-8h, so lawful Window 1 has zero length; `empty_outcome` deliberately marks these non-censored and they classify as **nonfill despite no order ever being possible**. These are unavailable opportunities, not policy nonfills; nonfill is overstated by 12 (should be 666 genuine + a separate no-window class).

## Q9 — Start law: PASS

- All 453 TennisExplorer clocks remain `quantized_late_detection_proxy` in the V5 ledger (453 counted; five-minute grid enforced by code; `exact_start_utc` nulled; never promoted).
- The asymmetric guard (−900/+600, `te-calibration-central-93pct-asymmetric-v1`) was frozen at a673ac2d (12:14) with a blindness declaration (no candidate results/fills/deltas/prices/holdout read), derived from the 234-official population (222 comparable crosswalks, median +300 s, 207/222 = 93.2% within 15 min, 15-event tail) — before any scoring (results 12:59).
- One-sided conflict law (`retain-stronger-causal-bounds-v1`) implemented and tested: proxy may never overwrite an earlier live_by; 13 named proxy conflicts censored by name with reasons; positive-capable 705 = 234 + 440 + 31 (the 718→705 shrink is named and evidence-backed, disclosed).
- No schedule-only or live-by-only event has a cutoff or a positive (reproduced: zero).
- Every verdict-capable event (718) carries its guard object; witness rows carry per-leg guard IDs, cutoffs, margins under BOTH laws. Witness recomputation confirmed: strict-60s = **5 strict / 3 under par** (matching the mandated correction), frozen guard = 1 strict / 0 under par. The four post→strict reversals (TOPUGO, COLVAC, GRABER, YEVCAM), the 106→82 shrink, and the 45→146 W1-leg expansion are disclosed in the correction record.

## Q10 — Freeze integrity: PASS with two warts

- PRE-RUN chain a673ac2d → 004f9d40 → bb7f9943 is lawful: both supersessions occurred before any candidate result existed (v2 failed closed loading its first event; v3 rebuilt 119 cache horizons with no policy evaluation), each documented.
- All 30 repository receipts verify. **Wart 1:** 8 of 30 receipt hashes were computed over CRLF working-tree bytes rather than git blob bytes (all 8 verify exactly after LF→CRLF re-encoding; the other 22 verify as blobs). No content drift — but receipts should hash committed blob bytes for portability.
- Candidate set in results == the 24 frozen PRE-RUN ids; ablations == the 13 predeclared; no post-result additions. D=804 in every candidate (code-enforced). Delta/reference law matches the frozen contract (leg VWAP − last true print at/before cutoff within [T-8h, cutoff]; PAR=100 strict; negative = strictly < 0). No holdout date appears in any artifact; the events input is date-fenced in code.
- **Wart 2 / genuine defect:** the invariant `future_information_used: false` is **not true for the four `pair_divot_core` candidates**. Their sealed-band depth term is `sealed_depth(called_band)` where `called_band` is the recognition band computed from the bid path through T-6h (`net`, `dip` measured over [birth, T-6h]) — but pair_divot_core is not in the delayed-family set and posts at T-8h. Its published rows (C=10/PC=9/S=8 twice, C=4 twice) therefore embed up to two hours of lookahead. The selected drift candidate and the other delayed families are causal (orders cannot precede T-6h); causal_micro and recut families don't use the sealed term. The headline is unaffected; the pair-family comparison rows are contaminated and must not be cited.
- Simplified-walk-law substitution: the runner is not the old simplified replay (it consumes the committed chronological surfaces), but see Q11 — several Vault instruments are name-only.

## Q11 — Vault-authorized instruments: absent / inert / simplified

Compared against the chronological LIVING_VAULT and deployed Window-1 lineage:

**Absent (not expressible by any candidate):**
- **Per-leg asynchronous divot timing** — the Vault's central entry doctrine ("fill the two legs AT DIFFERENT TIMES, each at ITS OWN divot"; inter-divot gap p50 41–62 min; the pre-T-4h posting-window spec). Every candidate posts both legs simultaneously at T-8h (or T-6h delayed) and waits; the only asynchronous element is the post-first-fill reaim. Dip-timing priors (recut per-cell timing priors) were never wired.
- Walking-staircase / join-improve-by-1¢ expression law as deployed (the grid's walk jumps to the touch, max 2 moves, no non-self chain).
- Riser/Plex bounce actuator (lawfully disarmed per Vault), FV-anchor placement, premarket walk cap, latch/grace-kill (exit-side, lawfully out of scope), sealed **pair-policy** object of 07-20 (`pair_policies_sealed_v1.json` — not a committed source; correctly declared unavailable, not reconstructed).
- Shape corpus (no independent non-AIM causal cell mapping — correctly absent, not imputed). AIM_V2 and Pinnacle correctly prohibited and unused.

**Inert (loaded/evaluated, zero decisions changed):**
- Drift recognition, cohort steering, orientation prior (drift≡mirror deep-equality + identical ablations); sealed bands for the selected candidate; takerreach LAW (structurally never wired to any decision); own-order fingerprints (coverage flag only).

**Simplified / name-only:**
- `mirror_deceleration` is not the Vault's mirror/seesaw instrument — it is pair-divot + sealed + a T-6h delay; the Vault's riser/deceleration/mirror/seesaw surfaces exist in the grid only as a coverage flag (|net| ≥ 5). Note the Vault itself REFUSED mirror-class steering on 07-20 (0/66 sub-par), so this absence costs nothing proven, but the family label overstates.
- "Dual-divot steering and catch" is reduced to a static divot-depth lookup; the catch (timing) half is absent.
- Dynamic floor is expressed as bid-relative depth, not the Vault's Σ(own W1-close − edge_p50) value-relative floor.

## Development miss, family ceiling, or something broader?

**A development miss under an under-expressive frozen instrument — not a proven market ceiling, and not even a proven frozen-family ceiling beyond this grid.** Three lines of evidence:
1. The optimistic zero-queue bound (26/804) caps only deep-passive simultaneous T-8h/T-6h posting at bid−depth prices; candidates that price nearer the touch systematically fill more (walk > park, reaim > hold everywhere in the grid), and the grid never tests touch/join postures or per-leg timing.
2. The Vault's own 07-20 re-score recorded 16 sub-par duals per 200 slate pairs (8.0%) achieved by the deployed system — several times the grid's C/D = 1.24%. The market demonstrably completes more sub-par duals than this instrument can express.
3. The PC-failure census is dominated by nonfill (678), not by adverse deltas (only 1 completion failed the delta test): when the instrument completes, it prices well (PC/C = 90%). Fill expression, not selection, is the binding constraint.

The 75% target (603) remains unproven in either direction; nothing in this run establishes a ceiling at 26.

## Every disagreement with Codex

1. Nonfill=678 overstates genuine policy nonfills: 12 zero-length-window events (no order possible) are inside it; honest split = 582 zero-fill + 84 single-leg + 12 no-window.
2. 84 naked-single events (one leg filled 5.0, partner never) are undisclosed inside "nonfill" — material risk shape.
3. `future_information_used: false` is false for the four pair_divot_core rows (T-6h recognition band inside a T-8h price via the sealed term). Headline unaffected.
4. The 26-completion sentence should be scoped to the frozen grid's best candidate, not left readable as a data/market ceiling.
5. "Six OS families" executed only nominally: drift ≡ mirror (deep-equal), so at most 4–5 distinct behaviors; recognition/cohort/orientation/sealed contributed zero observable decisions; reach is structurally unwired.
6. Candidate-spec text vs code: "non-self chain" not implemented; "advance one cent" is actually jump-to-touch.
7. Receipt hashes for 8 files taken over CRLF working-tree bytes (no drift; portability wart).
8. No disagreement on: D, C, PC, S, IC, all census counts, all group tables, witness recomputation (5/3 and 1/0), start-law implementation, freeze ordering, holdout integrity.

## Smallest lawful next action

Two steps, in order, both development-only, no deployment:
1. **Report correction (no new search):** re-emit the classification census splitting nonfill into 582 genuine / 84 single-leg / 12 no-window, disclose the naked-single shape, scope the 26 bound to the frozen grid, and strike the pair_divot_core rows (or annotate their lookahead).
2. **Round-2 PRE-RUN (new freeze, same D=804, same guards, same delta law):** extend the candidate grid to express the one Vault instrument the census says is binding — per-leg asynchronous divot timing (recut per-cell timing priors / pre-T-4h posting spec) plus touch/join postures under the deployed one-cent expression law with a real non-self chain — then rerun. Only after that grid also misses would a frozen-family ceiling claim be evaluable.

— Audit executed read-only against f7cd4209; reproduction code and receipt committed alongside this report. No production, live, order, position, settlement, exit, DCA, Window-2, holdout, or configuration surface was touched.
