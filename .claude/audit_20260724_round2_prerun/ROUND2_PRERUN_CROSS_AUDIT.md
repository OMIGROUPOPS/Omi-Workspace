# Independent PRE-RUN audit — Codex Round-2 Window-1 instrument

- Audited object: `origin/codex/window1-definition` PRE-RUN commit `6eecbd1d9adc7c41af28526d0cabe1038f3ae18b` ("Freeze lawful Window-1 Round-2 instrument"), sole child of Round-1 results `f7cd4209`, and the branch tip at audit time.
- Controlling prior audit: `audit/window1-independent` @ `024f03bb` (bound inside the PRE-RUN manifest by git blob OID and SHA-256 — binding verified).
- Method: detached read-only worktree pinned at 6eecbd1d; full code reading of `window1_round2_instrument.py` (1,308 lines), the prerun/capability/correction scripts, and all five Round-2 contract JSONs; re-execution of the 17 committed tests (pass) and the capability proof (reproduces byte-identically); and an **independently authored adversarial fixture campaign** (`adversarial_fixtures.py`, receipt `ADVERSARIAL_FIXTURE_RECEIPT.json`) that never touches the D=804 population, never scores, and never opens the holdout.

## Gate verdicts

| Gate | Verdict |
|---|---|
| PRE-RUN AUTHENTICITY | **PASS** |
| ROUND-1 CORRECTION | **PASS** |
| T8/T6 LOOKAHEAD REMOVAL | **PASS** |
| PER-LEG ASYNCHRONY | **PASS** (mechanism; one anchor ruling owed — see F4) |
| POSTURE/RECUT/SIBLING EXECUTABILITY | **PASS** |
| CAUSAL MARKET INPUTS | **FAIL** (F2: zero-size evidence defect; F4: realized-start eligibility anchor) |
| MISSINGNESS/CENSORING CONTRACT | **PASS** (law correct; F1 population consequence named) |
| METRIC AND DENOMINATOR FREEZE | **PASS** |
| HOLDOUT SEAL | **PASS** |
| **ROUND-2 DEVELOPMENT EXECUTION AUTHORIZED** | **NO** — blocked by F1, F2, F3 (F4 needs a ruling) |

## Frozen-receipt reproduction (all verified)

1. PRE-RUN SHA 6eecbd1d, parent f7cd4209, single commit, equals branch tip; `frozen_at` 2026-07-24 14:02 ET.
2. Exactly 10 candidate IDs (3 profiles × declared posture-pairs × hold/reaim) and exactly 9 predeclared ablations; results candidates match the freeze; `free_numeric_parameters: []`; no scoring/tuning performed flags all false.
3. No post-freeze additions: the commit is the freeze; nothing on the branch follows it.
4. **All 45 receipts verify against committed git blob bytes** (`hash_basis: staged_git_blob_lf`), including byte counts and git blob OIDs. The Round-1 CRLF wart is fixed.
5. Round-1 corrected conservation reproduced against my controlling audit: D=804, C=10, PC=9, S=9, IC=4; failure census 582 genuine zero-fill + 84 naked single-leg + 12 zero-length-window (per-date decomposition sums exactly; the 12 zero-length events verified all on 2026-07-19 from the f7cd4209 ledger); censored 102 = 85 start-boundary + 11 missing-feature/no-birth-book + 6 queue-ambiguous; missing features censored, never nonfill.
6. The 26 optimistic bound is scoped to the selected candidate and the frozen 24-candidate Round-1 grid, with `market_ceiling: false` and `data_ceiling: false` stated in the receipt.
7. The four `pair_divot_core` rows are struck by ID with the defect named and `replacement_scores_asserted: false` (struck, not silently repaired — correct).

## Independent adversarial results (own fixtures, frozen surfaces)

1. **Leg-A timing independence:** changing only Leg A's birth anchor moved its eligibility (1,020,160 → 1,000,000) and its stream; Leg B's stream byte-invariant. 2. Symmetric for Leg B. Eligibility confirmed numerically as `cutoff + t_deep_p50×60` per leg (t_deep_p50 is negative; e.g. ATP_MAIN cell 57 → −144 min).
3. **Posture:** park_join vs touch_park on identical data → different executable orders (park at 55 = bid−depth on a divot trigger; touch at 57 = at-bid on flow alone).
4. **Sibling response:** first full fill (earlier leg) emits a timestamped `sibling_hold` / `sibling_reaim_decision` at the fill instant; the reaim is exactly +1¢ and executes only at the sibling's **own** later eligibility+divot trigger (hold: 55; reaim: 56; same trigger timestamp) — causal, bounded, no shared clock.
5. **Missingness:** `true_prints=False` on one leg → named `feature_censor` action, zero orders, `censored_feature` terminal — never nonfill.
6. **Schedule-only:** no cutoff → `censored_start_boundary`, zero orders; a schedule-only event carrying a positive cutoff is **refused with an error**.
7. **T8/T6:** my own two-bundle fixture (only the frozen drift-recognition mapping mutated) → pre-T6 action streams identical, post-T6 differ. Code-path inspection: `recognition_depth`/`current_band` are written only inside `_on_recognition` (fired only at left+7200 within the window); `eligible_ts` reads only the birth recut cell; no pricing path accepts a recognition band before T6.
8. **Flow/evidence hygiene:** own-fingerprint prints are excluded from fills, flow, divot, and walk (logged as `contributed_volume_excluded`); own resting size is subtracted from the external book and can only remove evidence. Zero-size prints do not count toward flow minimums and cannot fill. **But see F2.**
9. **Top-five pressure:** ask/external-bid ratio from the current causal snapshot only; ≥1.5 adds exactly the frozen 1¢ (depth 2.0→3.0, price 55→54); `top5` unavailability censors by name.
10. **Exclusions:** no code path in the instrument references Pinnacle, AIM, shape, full depth, the uncommitted sealed-pair object, or the riser (string-absence verified); `SURFACE_PATHS` loads only the six frozen research surfaces.
11. **Per-leg recut:** a causal book-cell change on one leg (57→44, edge 1→2) produced `pair_recut` + cancel + reprice (55→42) on that leg only; the sibling stream untouched.
12. **Holdout/date fence:** events dated Jul 24/25/26 refused ("sealed holdout event refused"); Jul 22 and Jul 11 refused ("outside frozen development dates").
13. **Counterfactual streams:** both legs emit `leg_open → … → terminal` with generated placements; `scored: false`, `metrics: null`; nothing replays a historical order. Zero-length windows yield the distinct `zero_length_window1_opportunity` class.

## Findings that block authorization

**F1 — The cohort-steering floor is structurally unattainable in the development population (six of ten candidates are dead on arrival).** The frozen `cohort.json` has, with `cell_edge` present: ATP_MAIN **0 rows**, WTA_MAIN ≤1/zone, WTA_CHALL ≤3/zone, ATP_CHALL ≤15/zone — against the frozen `cohort_minimum_n: 30`. D=804 contains only these four categories. `_initialize_birth` **censors the leg** whenever the cohort zone is below n=30 and `cohort_steering` is enabled, so `r2_causal_steer` (×2) and `r2_full_os` (×4) will emit `censored_feature` for every leg of all 804 events. Consequently the entire steering repair (orientation, drift recognition, pressure) and the **only walk-capable profile** can never act in the real run; the grid degenerates to the four `r2_async_pair` candidates. The PRE-RUN capability gate ("every advertised family changed at least one eligible order decision") was proven **only on synthetic surfaces** built inside the proof script — it does not hold on the frozen surfaces over the development categories. It is also in tension with the spec's own language ("callable only at n≥30"), which reads as no-call, not leg-censoring.

**F2 — Zero-size prints confirm divot and walk evidence, violating the frozen evidence law.** Spec and adapter both state zero-size/synthetic activity "never confirms flow, divot, walk, or fill." Fixtures prove: a zero-size print **can** emit `micro_divot` (which gates park/walk placement), and a zero-size print **can** serve as a verified walk-chain link (advance executed). Root cause: `_detect_divot` and the `_maybe_walk` chain filter check `taker_side` but not `size > 0`. Fill and flow paths are correct. Latent on size-validated caches, but Round-2's data is not yet bound (F3), so the law is not enforced anywhere.

**F3 — The Round-2 data diet is unbound.** The 45 receipts cover code, contracts, surfaces, the V5 start ledger, and reports — but **no receipt binds the 804-event export, the per-leg observation streams (books/prints), or the feature-availability flags**. Round-1's freeze bound events, normalized prints, and a validated 804-file market cache by hash; Round-2 has no equivalent yet. Until a data-binding supersession freeze exists, "no undeclared numeric search surfaces" cannot be extended to the inputs, and the F2 size>0 guarantee has no enforcement point.

**F4 — The per-leg eligibility clock is anchored to the realized start.** `eligible_ts = cutoff + t_deep_p50×60`, and the cutoff derives from the realized (post-hoc-detected) official/proxy start. A live policy cannot know the realized start in premarket; using it as a timing input gives every candidate a start-time oracle that legitimately-schedulable policies lack (the Vault's pre-T-4h posting spec anchors on the exchange schedule). This is declared in the spec ("clamped to the guarded Window-1 interval") but sits in tension with `future_information_prohibited`. Either re-anchor to the schedule (`scheduled_start − t_deep`) or publish an explicit lawfulness ruling that the guarded cutoff is part of the frozen evaluation frame and print that concession beside every Round-2 result.

## Named inert, duplicated, unavailable, or misleading families

- `cohort_steering` — **unavailable** in all four development categories under the frozen surface and floor; implemented as leg-censoring, making it **misleading** in the capability matrix (fixture-true, population-false).
- `r2_causal_steer__*` (2) and `r2_full_os__*` (4) — **dead-on-arrival candidates** as frozen (F1).
- `nonself_one_cent_walk` — executable and exactly-one-cent (proven), but lives only in `r2_full_os`, so it is unreachable in-run under F1; its chain verification accepts zero-size links (F2).
- `causal_orientation` — executable; frozen ORIENT_V1 has callable cells for ATP_MAIN (2), WTA_MAIN (2), ATP_CHALL (3) and **zero for WTA_CHALL** — it can never call in WTA_CHALL (coverage fact to disclose, not a defect).
- `bookmaker_fv` — declared conditionally lawful, used by no v1 candidate (deliberate, disclosed — acceptable).
- Undeclared-but-hash-bound numeric constants not listed in `parameter_surface`: orientation call thresholds 0.65/0.35 and min-n 10, recognition purity 0.5, divot-signal fallback max age 300 s, 3-print orientation minimum. Not free parameters (frozen in code), but the "zero free numeric parameters" disclosure should enumerate them.
- Cosmetic: the posture branch `external_bid + 1` is unreachable from macro pricing alone (macro target never exceeds the bid); it is reachable only via the sibling reaim bias.

## Smallest correction (do not run the search before it)

One supersession commit on Codex's branch, then a fresh independent PRE-RUN audit pass:
1. Add `size > 0` filters to `_detect_divot` (triggering print and trailing-median population) and to the `_maybe_walk` chain candidates (F2).
2. Resolve the cohort law per its own spec text: below-floor cohort → **no cohort call**, not leg censoring — or remove `cohort_steering` from the `r2_causal_steer`/`r2_full_os` required families, or justify an attainable per-category floor with prior art (F1). Re-run the capability proof **against the frozen surfaces with development categories** so the gate is population-true.
3. Bind the data diet by hash exactly as Round-1 v3 did: the 804-event export, per-leg observation streams (books and prints, with a size>0 and monotone-timestamp validation receipt), and feature-availability flags (F3).
4. Rule on the eligibility anchor: re-anchor to the exchange schedule, or commit an explicit ruling that cutoff-anchored timing is part of the frozen evaluation frame, disclosed beside every result (F4).

No repair was made to Codex's branch. No Round-2 scoring, tuning, ablation evaluation, or holdout access occurred. This audit touched no production, live, order, position, configuration, Window-2, exit, settlement, or DCA surface.
