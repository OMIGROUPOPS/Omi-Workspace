# INDEPENDENT WINDOW-1 RANGE-MASTERY ATTACK SIMULATOR AUDIT @ 66b50db3 — RULING: BLOCKED

**BLOCKED — measurement censoring, one demonstrated semantic defect.** The simulator's mechanical substrate is the cleanest of the series — lineage, price-at-X print law, exact-touch semantics, chronology, headroom arithmetic, D=804 preservation, mechanism honesty (including explicit RETRACTION of every previously-blocked mechanic), 70/70 tests — but the frozen contract **records certain executable strict-ask evidence as a diagnostic and discards it as unfilled while maker-safety moves the order away at the very book that proves the fill**: 13 exposed intervals per candidate (26 total), on 13 distinct legs/events each, with 20 of 26 censored fills being what would have been the event's *first* credited fill — so headroom for those events was never armed or armed on the wrong leg/timestamp.

Date: 2026-07-25 · Branch: `audit/window1-independent` (child of `ffa41255`) · Auditor: independent CC session
Method: detached clean worktree at `66b50db35e9dcec756ce6366bed1fe44147f8e29`; no implementation, scoring, C/PC/IC/S calculation, ranking, tuning, or holdout/live access; every reported number reproduced from the frozen artifacts and raw pinned inputs.

## 1. Lineage and isolation — PASS

- Parent exactly `84959172`; all-refs children scan: sole child; remote tip of `codex/window1-definition` verified (audit tip `ffa41255` verified). **31 additions, zero modifications/deletions.**
- **The BLOCKED parent's mechanics are not inherited.** The instrument imports exactly four symbols from the blocked file — `normalize_event`, `preserve_last_trade`, `VERIFIED_PRINT`, `CARRIED_UNKNOWN` — the normalizer/last-trade preservation path that my macro×micro audit independently PASSED (item 2 there). All other imports come from the Round-2 mechanical module. Grep-verified absent: `bid − edge` targeting, the universal climb/decay split as posture law, `composed_macro_micro` annotation, and the taker-side/pressure direction confirm gates — and the MECHANISM_RECOVERY_TABLE explicitly lists all five as **RETRACTED**.
- All 24 ARTIFACT_HASH_MANIFEST rows reproduce (sha256; CRLF-equivalent accepted only where blob-equal). Deterministic regeneration relaunched fresh-directory; running at ruling time (see addendum policy below) — immaterial to this BLOCK.

## 2. Price-at-X law — PASS (independently reproduced)

From all 38,311 committed interval rows plus code (`_first_price_reach`, `evaluate_interval`): a positive-size, receipt-identified, non-self public print **at or below X** during the exposed interval is `PRICE_REACHED` and assigns exactly **five simulated shares at X** (`accounting_quantity_if_later_scored: 5`); printed quantity, cumulative-five, single-five-print, displayed-depth-five, and queue-clearance are all explicitly not required (per-row negative flags; queue/taker-reach appear only in `depth_volume_stress` with `decision_gate: false`). The reported **38 cumulative-five false negatives per candidate reproduce exactly** (`primary=true ∧ cumulative volume through cutoff < 5`).

## 3. Strict-ask censor — **BLOCK (measurement censoring, fully demonstrated)**

Code chronology (`_on_book` → maker-safety → `_apply_liveaim`; `_on_print` → `_first_price_reach`): when a lawful external ask moves to or below the resting order's X, `_on_book` **cancel+reprices the order down to ask−1** (`maker_safety_external_ask_move`) — before any crediting path exists, because **the only crediting path is print-based** `PRICE_REACHED`. `evaluate_interval` then computes `CERTAIN_FILL = strict_print ∨ strict_ask` as a **diagnostic only**; accounting is `5 if PRICE_REACHED else 0`. A strict print below X is definitionally also `PRICE_REACHED`, so the entire divergence class is strict-ask-only. Census (reproduced; full detail in `PRICE_AT_X_CENSUS.json`):

| | macro_hold | macro_micro |
|---|--:|--:|
| intervals | 9,177 | 29,134 |
| CERTAIN_FILL ∧ ¬PRICE_REACHED | **13** | **13** |
| … all strict-ask-only | 13 | 13 |
| distinct legs / events affected | 13 / 13 | 13 / 13 |
| maker-safety moved the order **at the evidence timestamp** | 13/13 | 13/13 |
| censored fill = would-be event **first fill** | (of 26 total: **20**) | |

Every censored row carries the original exposed X, the ask book receipt and timestamp, the actions taken at that timestamp (`maker_safety_external_ask_move_cancel` + reprice), and the resulting accounting state (credited 0, diagnostic true). Same-timestamp ordering: books are processed before prints at equal ts, so a same-ts qualifying print would credit at the *new lower* limit after the maker-safety move — the credited-limit change is subsumed in the 26. **A resting buy at X confronted by a lawful external ask below X is certain executable evidence; recording it as a diagnostic and discarding it as unfilled is measurement censoring.** Headroom consequence measured: in 20 of 26 cases the censored fill precedes the event's actual first credited fill (or the event has none) — those headroom paths were never armed or armed on the wrong leg/timestamp. Not repaired here, per scope.

## 4. Exact-touch decomposition — PASS (labels are honest, but see item 3)

Reproduced exactly: macro_hold PRICE_REACHED 495 / CERTAIN_FILL 50 / EXACT_TOUCH 715; macro_micro 486 / 49 / 706. Decomposition (per candidate, macro_hold / macro_micro): print-only touches 474/465; **ask-only touches 240/240**; both 1/1; touches followed by later print reach 475/466; **ask touches that never become certain fills 240/240**. Ask == X remains contextual/queue-sensitive (stress diagnostic with fitted taker-reach probability, `decision_gate: false`) and is never auto-credited; a positive print exactly at X is `PRICE_REACHED` (`reached = price ≤ target`). **EXACT_TOUCH exceeds PRICE_REACHED because it is an event-level boolean union of exact-print and exact-ask touches — dominated by the 240 ask-only touches that never credit — and the three labels are overlapping booleans, not disjoint counts or completed fills.**

## 5. Interval and chronology integrity — PASS

Exposure begins only at a lawful order (intervals open on place with lawful BBO); evidence filtered to `[opened_ts, min(closed_ts, guarded_cutoff)]`; Window-1 guard respected (`positive_window1_provable` gating; cutoff clamp); one leg receives only its earliest lawful assignment (`_first_price_reach` sets quantity to LOT once and nulls the order); repricing does not retroactively erase prior-interval evidence (each interval evaluated over its own bounds from the immutable observation stream); future ladder outcomes are confined to the counterfactual diagnostic fields and never enter policy (`range_outcome_separate_from_decision_receipt: true`; no policy path reads `evaluate_interval` output).

## 6. Combined first-leg headroom — PASS mechanically, with disclosures

Reproduced from the 95,727 headroom receipts: activations **691 / 690** exact; d1 = X − contemporaneous first-leg external bid with book receipt; `b2_max = floor(−d1 − fee − 1)` — **zero mismatches**; strict `d1+d2+fee < 0` and exact `+1` per qualifying strictly-later sibling print on **all accepted decisions (5,280 / 16,722 exact)** — zero violations; no action at the first-fill timestamp (`sibling_action_same_timestamp: false`; trigger requires `ts > first_fill_ts`); expression law enforced (`proposed == prior+1`, `< ask`); no IC or S gate anywhere. Opportunity reconciliation: **24,822 / 39,248** = per-event sums of `sibling_opportunity_inside_remaining_budget_count` in the pairwise ledger; total headroom decisions 41,227 / 54,500. **Disclosure required by this audit:** the accepted upward reprices are cancel+replace operations — each surrenders queue; "macro hold" must always be qualified as *hold except headroom +1 steps and maker-safety down-moves* (the stream reasons make this explicit; the PRE-RUN report's "hold" language must carry that qualification). **Headroom impact of the item-3 censor: 20 of 26 censored fills were first-fill-position — those events' arming is wrong or missing by construction.**

## 7. Macrostructure binding — PASS

Native Atlas use verified against `.claude/trendpath/ATLAS_V1.json` (pages natively keyed by leader/underdog and price buckets — `atlas_native_side`/`path_price_bucket` match the source's own conventions; the ≥50 keying here is the atlas's native page key, not the retracted posture split); causal first-print + 60-minute discovery with frozen median; discovery − native bottom `depth_p50`; category coverage with named NO_CALL when a page is unavailable; mains par-lock behavior present; **no moving-bid-minus-edge target** (RETRACTED and absent from code); no close-keyed future leakage (close-keyed recut cells PROXIED, unused for targets); no evaluation-start access.

## 8. Microstructure binding — PASS

LIVE-AIM mapping (`liveaim_mapping`) uses category flow thresholds (ITF 6 / CHALL 16 / mains gauge-off — the CLIMBSIDE_SPEC's "ITF OPEN ≥6 prints/30m" lineage), print-count ratio, print signature, depth trend, spread — all computed from receipted evidence, with verdicts (AIM_DEEP/SHALLOW/PRIOR, NO_BID_CHASE_GUARD, GAUGE_OFF) that hold or select among already-authorized targets; divot logic holds a selected target rather than fabricating one; carried last trade never becomes print volume or BBO authority (inherited PASSED preservation path; provenance fields carried through); chain depth/volume/cadence/flow-count/signature/spread/depth-trend are consumed where classified BOUND and only stored where PROXIED; **no invented direction gates** — the previously invented last-trade/pressure/taker-side direction rules are RETRACTED and absent.

## 9. Mechanism status — PASS

MECHANISM_RECOVERY_TABLE (9 BOUND / 10 PROXIED / 4 ABSENT / 5 RETRACTED) validated against the executable: every BOUND row corresponds to a real production-path decision effect (print fill law, BBO chain, Atlas discovery macro, LIVE-AIM, guidebook deep tier, microdivot, pair headroom, schedule clock, external-ask maker-safety); volume/cadence and carried last-trade are now honestly **PROXIED** (the macro×micro over-claim corrected); ABSENT rows match unavailable evidence; RETRACTED rows are the five blocked mechanics. One pointed note: the BOUND `external_ask_maker_safety` mechanism is real and decision-changing — and is precisely the mechanism that consumes the strict-ask evidence as evasion instead of credit (item 3).

## 10. Population and no-evidence events — PASS

D = **804 per candidate** (recounted from stream shards). The five no-BBO events reproduce in both candidates with zero placements, zero fabricated prices, no print-for-BBO substitution, named `feature_no_call` rows (steering + market evidence), null metrics, D membership retained.

## 11. Score-free and forbidden access — PASS

All C/PC/IC/S and performance fields null across streams, fillability rows (`C: null…`, `metrics: null`, `scored: false`), and receipts; no scorer/benchmark imported or executed; no ranking/selection; forbidden-access receipt corroborated (no holdout, live, production, exit, Window-2, settlement, DCA, network paths); **70/70 tests pass** (18 range-attack + 12 macro×micro + 8 V2 + 22 R4 instrument + 10 R4 diagnostics).

## RULING

**BLOCKED — measurement censoring (item 3).** One demonstrated semantic defect: strict-ask-below-X certain-fill evidence is diagnostically recorded, never credited, and actively evaded by maker-safety at the evidence timestamp — 26 exposed intervals (13 per candidate), 13 legs / 13 events per candidate, 20/26 at first-fill position with headroom consequently never armed or mis-armed. Everything else in this PRE-RUN independently reproduces, including the honest retraction of every previously blocked mechanic.

The narrow correction (not implemented here) is a frozen accounting rule for strict-ask evidence during an exposed interval — credit-then-(optionally)-reprice rather than evade-then-discard — with the 26 affected intervals as the acceptance fixture, a re-derived headroom arming census, and a fresh independent audit. No scoring package may be constructed against `66b50db3`.

## Determinism addendum policy

Fresh-directory regeneration was running at ruling time; its result will be recorded in a follow-up receipt when complete. It cannot affect this BLOCK.

## Determinism addendum (final)

The fresh-directory regeneration was launched twice and terminated by the execution environment both times before producing output (the range-attack builder is the heaviest in the series: 13.5M-snapshot normalization plus 38,311 ladder-interval evaluations). **The committed DETERMINISTIC_REGENERATION_RECEIPT therefore remains unconfirmed by this audit.** This is immaterial to the BLOCKED ruling, which rests on the demonstrated strict-ask measurement censoring; but deterministic regeneration MUST be independently confirmed as part of the corrected PRE-RUN's audit before any scoring package is considered. All 24 artifact hashes were verified against the committed blobs; what remains unproven is only the regenerate-from-frozen-inputs byte-identity claim.
