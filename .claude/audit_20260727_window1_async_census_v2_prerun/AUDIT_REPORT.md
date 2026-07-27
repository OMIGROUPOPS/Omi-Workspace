# INDEPENDENT AUDIT — WINDOW-1 ASYNCHRONOUS OPPORTUNITY-VS-POLICY CENSUS V2 PRE-RUN @ e60f6af4 — RULING: PASS

**PASS. A fully independent raw-input reconstruction — a fresh driver built only from the frozen laws, never importing the V2 module — reproduced every one of the 1,608 event rows, 6,501 qualifying episodes, 473 first-leg references, 10,733 exposure attributions, and 1,352 orientation rows with ZERO row-level differences. All controlling 0350c081 fixtures reproduce exactly; zero BBO-selection mismatches; zero older/favorable selections; 25/25 tests; two fresh clean regenerations byte-identical to each other and to the committed package; every hash verifies; no forbidden surface touched.**

Date: 2026-07-27 · Branch: `audit/window1-independent` · Additions-only sole child of `0350c081a26e06216a34f58eed8a13e72ef5e236` · Auditor: independent CC session
Under audit: `e60f6af4f6db5bab5b8a30704a0cb1fc98c774a7` ("Freeze Window-1 asynchronous opportunity census V2") on `codex/window1-definition`.

## 1. Lineage and containment — PASS

Parent is exactly `9220eba26b00a5b94e86d9c644adef16382942a0`; e60f6af4 is the **sole child** of 9220eba2 across all refs; remote `codex/window1-definition` tip = e60f6af4. The local branch ref reads `6daab089` — a **stale deep ancestor** (the pre-V1 Round-3 freeze), not a divergence: no divergent commits exist, and the implementation worktree is checked out detached at e60f6af4. Diff 9220eba2→e60f6af4: **24 additions, 0 modifications, 0 deletions**; full `ls-tree -r` comparison proves every inherited candidate, instrument, scorer, result, and artifact blob is **byte-identical** (V1 census, strict-ask, and results packages included; inherited test tree untouched, 131→132 files by pure addition). The package contains only the score-free census (implementation + spec + tests + 21 receipts/artifacts).

## 2. Controlling-law binding — PASS

The frozen builder binds `0350c081` as its acceptance authority (all five amendment blob OIDs verified against the audit branch), and its acceptance runs **only after independent construction** (code-verified; construction never reads audit data). Every committed figure equals the final amended law; none of the retracted fixtures (170/173, 49/52, 46/49, 3,229/3,278, 18/25, 81/84, 559-union) appears in any acceptance path.

## 3. Independent raw-input reconstruction — PASS, zero differences

My driver rebuilt, from the pinned frozen inputs only (frozen result ledgers, V1 X-evidence ledger, unscored candidate streams, raw guarded-cache-v3): credited first legs, evidence receipts/timestamps, authoritative X1/bid0, d1, b2_max, sibling identities, every lawful raw book and print, every strictly-later lawful episode with contemporaneous BBO (timestamp-then-preserved-ordinal), X and d2, strict combined budget, evidence provenance, capacity status, earliest lawful recovery, episode counts, terminal classes, both no-fill counterfactual orientations, and the deduplicated union — then compared **every field of every row** against the committed package:

| comparison | rows | differences |
|---|--:|--:|
| event-level census (804 × 2 candidates) | 1,608 | 0 |
| qualifying episodes (all fields incl. policy, capacity, depth, provenance) | 6,501 | 0 |
| raw contemporaneous BBO receipts | 6,501 | 0 |
| authoritative first-leg references (incl. bid0, d1, b2_max, boundary, x_evidence_id) | 473 | 0 |
| bounded exposure attributions | 10,733 | 0 |
| counterfactual orientation rows (incl. witnesses) | 1,352 | 0 |

Reproduced aggregates (both candidates): **D=804/804; 1,608 rows; recovered naked 22/237 and 25/240; residual 215/215; episodes 3,226 and 3,275 (Σ 6,501); splits 16+6 and 19+6; no-fill union 65/336 and 68/340; both 52/54; one 13/14; neither 271/272; VUKBRO exactly 1 lawful episode per candidate.** Event-census classes conserve exactly (22 = 14 never-exposed + 7 moved-away + 1 capacity-unproved; 25 = 14 + 10 + 1; residual 215 = 213 no-lawful + 2 evidence-unavailable).

## 4–5. First-leg reference and contemporaneous sibling-BBO law — PASS

bid0 comes solely from `FROZEN_X_EVIDENCE_LEDGER.book_and_chain_at_first_observation.nonself_best_bid_cents` of the credited (event, leg, X1) — re-derived independently for all 473 rows, with d1 and b2_max reproduced for every recovered naked event; no merged/thinned stream, same-second neighbor, later book, carried last trade, sibling evidence, or favorable receipt selection exists in code or data (events with bid0 null — NEUPRA, BUBHAL — surface as named `evidence_unavailable`, never substituted). All **6,501** episodes audited (no sampling): strict-ask bid/ask always from the same lawful snapshot with X=ask+1; print BBO always the latest lawful positive-size raw-cache row at or before the full-precision print timestamp with **preserved source-list ordinal controlling same-timestamp order (later ordinal wins)**; d2 = X − contemporaneous bid and d1+d2+0 < 0 verified row-by-row; **0 BBO-selection mismatches, 0 older/favorable selections**; exact conservation to 3,226/3,275. Ask is never bid; carried last-trade is never BBO authority (provenance labels verified); no thinned-stream bid exists (`thinned_stream_used: false` on all 6,501 receipts, and construction reads only guarded-cache-v3).

## 6. Three disputed X=17 receipts — PASS

`06a93c92…`, `8f0d3c80…` (CERKOL), `3e4c49d6…` (FRUKRE) appear in **zero** qualifying sets (mine and the package's). Reproduced: X=17, d1=0, controlling same-second bid=17, d2=0, combined 0, unlawful. The implementation selects CERKOL ordinal **218181** (refusing older favorable 218159) and FRUKRE ordinal **58380** (refusing 58363) — frozen in its self-consistency receipt and re-derived by my driver; the receipts are also hard-coded frozen exclusions with a validator that fails the build if any ever qualifies.

## 7. VUKBRO — PASS

Both candidates: credited BRO, X1=58, fill ts 1783949040.451872, bid0=58, d1=0, b2_max=−1, sibling VUK, **exactly one lawful print episode** at X=41 / contemporaneous bid 42 / d2=−1 / ts 1783979002.679826, cutoff 1783992600.0. The seven later bid=41/d2=0 prints are excluded (my reconstruction finds exactly 1 qualifying episode).

## 8. Window and chronology — PASS

All boundaries carry `positive_window1_provable=true` (473-event boundary receipt matches my ledger extraction row-for-row); every episode lies inside the authoritative inclusive [policy_left_ts, guarded_cutoff_ts] corridor (0 violations across 6,501) with the inherited **inclusive right endpoint** (fixture-tested); sibling evidence strictly later than the causal first fill (0 violations; same-timestamp sibling evidence excluded by law and test); no post-boundary evidence contributes; **AVEFOR remains excluded** (0 qualifying episodes, asserted by the builder and reproduced).

## 9–10. Separation and combined-headroom law — PASS

Price reach, five-contract capacity, policy exposure, execution proof, and policy credit stay distinct fields on every row; no cumulative-five requirement censors reach (1 capacity-unproved recovered event per candidate proves the class lives); prints never substitute for BBO; unavailable evidence surfaces as named classes, never fabricated (five no-BBO events — KRUCAS, CREMAT, TAUTOM, PUTJEA, KUDKOR — remain in D=804 with zero fabricated placement; CREMAT's orientation path rests on real raw-cache evidence and reproduces independently). Macro direction appears only as category context — no direction veto exists in any law path. `b2_max = floor(−d1 − fee − 1)` and strict combined negativity verified on all rows; **6,310 of 6,501 episodes have positive d2 inside combined headroom** (min d1 = −15) — no IC/both-negative gate, no simultaneous-fill gate, no S/cost-100 gate; IC untouched.

## 11. Policy-exposure attribution — PASS

All **10,733** rows audited and reproduced exactly, covering precisely the 473 first-leg-available naked pairs. `policy_exposed_without_execution_proof` (533 / 2,302 rows) requires all five proven requirements on the same interval; every other row is the named class `policy_exposure_evidence_unavailable_or_indeterminate` with its exact unproven requirements enumerated (corridor overlap 7,210; headroom 1,686; post-first-fill 598; no lawful BBO 28). The V1 unbounded class is gone; every attribution reconciles to event-level totals.

## 12. Recurring-X classes — PASS

Per-(event, leg, X) classification rebuilt independently: **27/34** V1-ledger-observed X-levels rejected by global-first admission with a later lawful recurrence; **16/16** raw lawful recurrences with no V1 X-ledger observation at all. Classes are disjoint (verified per event), published separately (never blended into an unlabeled total), every member carries receipt-level proof, and **X=17 belongs to neither class** for CERKOL or FRUKRE (no independently lawful X=17 recurrence exists).

## 13–14. Presentation, population, nulls — PASS

Naked primary results use only the realized credited-first-leg orientation; no-fill retains both counterfactual orientations with the deduplicated either-orientation union as primary; orientation rows carry `orientation_rows_are_not_event_counts=true` and `realized_policy_miss_claim=false` throughout. D=804 per candidate, all 804 represented, `D_member=true` on all 1,608 rows; every metrics/performance field null, `scored=false`, no C/PC/IC/S computed anywhere; no scorer import/invocation, no benchmark/result directory, no ranking or selection.

## 15. Integrity, tests, determinism — PASS

All 19 artifact-manifest rows, 20 determinism-inventory rows, 16 source-manifest rows (bytes + sha256 + git blob OID), 5 controlling-audit blobs, and all 9 gzip payloads verify; the 804-file guarded-cache name+content set hash and the controlling VUKBRO cache SHA (`fbacf0ab…16a07`) match. **25/25 focused tests pass**; no inherited test weakened (inherited test tree byte-identical). **Two fresh clean regenerations** from frozen inputs (detached worktree at 9220eba2; the three frozen V2 source files placed untracked, since the builder hashes them from the working tree — the one operational note of this audit) were byte-identical to each other and **all 21 package files byte-identical to the committed package**; the self-consistency receipt was recomputed live by the regeneration, not trusted.

## 16. Forbidden access — PASS

Code, imports, receipts, paths, and execution traces confirm: no scorer, benchmark, tuning/ranking/selection, holdout (sealed dates enforced as rejections only), live/production/network, order/position mutation, Window-2, exit, settlement, or DCA surface accessed or invoked. Builder git usage is read-only (`rev-parse`, `show`); writes go only to the package directory and temp dirs.

## RULING

**PASS.** The V2 pre-run is a faithful, deterministic, score-free implementation of the final controlling law at 0350c081, independently reproduced from raw inputs with zero row-level and zero aggregate differences. This PASS authorizes **only** operator use of this score-free census for Window-1 opportunity-versus-policy diagnosis. It does **not** authorize scoring, strategy tuning, ranking, deployment, holdout access, or any benchmark.
