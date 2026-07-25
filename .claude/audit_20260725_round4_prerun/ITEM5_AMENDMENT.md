# AMENDMENT — ROUND-4 AUDIT ITEM 5 ONLY (supersedes the Item-5 correction in AUDIT_REPORT.md)

Date: 2026-07-25 · Amends: `84cdf87a12f3b0c4986ba3133c84711bce4e74c7` · Target PRE-RUN: `4f65344672430adc51fe0a5a7e8c9279b2b354ed`
Scope: Item 5 exclusively. No implementation, scoring, tuning, ranking, holdout, or live access occurred. Every other finding of the prior audit — including the Item-6 requirement to remove/deprecate the two inert 100¢ fields, and the overall BLOCKED status pending the corrected PRE-RUN — remains in force unchanged.

## Independent evidence reproduction — MATCHES THE IMPLEMENTATION LANE EXACTLY

From the frozen private market caches and the frozen normalization path at `4f653446` (policy windows from the frozen normalizer):

| Event | Leg | Raw prints | In-window prints | Raw book snapshots | In-window lawful BBO snapshots |
|---|---|--:|--:|--:|--:|
| KXATPCHALLENGERMATCH-26JUL19KRUCAS | CAS / KRU | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 |
| KXWTAMATCH-26JUL13TAUTOM | TAU / TOM | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 |
| KXWTAMATCH-26JUL14PUTJEA | JEA / PUT | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 |
| KXWTAMATCH-26JUL20KUDKOR | KOR / KUD | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 |
| KXATPCHALLENGERMATCH-26JUL20CREMAT | CRE / MAT | 116 / 65 | **7 / 4** | 2,303 / 3,044 | **0 / 0** |

- Four events have no market evidence of any kind on either leg.
- CREMAT has thousands of book snapshots — every one **outside** the lawful Window-1 policy corridor — and exactly 7 (CRE) and 4 (MAT) lawful in-window prints. Prints are executions, not resting-book best-bid authority.
- **All ten legs have zero lawful positive-size external BBO snapshots inside the policy window.** The never-marketable maker price (external-bid-anchored, ≤ ask−1) cannot be instantiated on any leg without either fabricating a price or substituting a print for a BBO — both forbidden.

## Semantic ruling — CONFIRMED

The prior Item-5 correction conflated two distinct laws. The censor finding was and remains correct: `causal_role` absence must never terminally censor a D event. But the prior *required invariants* (ii)/(iii) — both-leg placement on the five named events and placement on all 804 — demanded maker presence where **no lawful price authority exists**, which is impossible under never-marketable / no-fabrication law. The lawful semantics are:

- **D = 804 is the immutable metric denominator.** D membership does not require an executable placement when lawful price authority is unavailable.
- `causal_role` absence → named steering NO_CALL; never a terminal censor.
- Role-agnostic neutral presence may occur **only when a lawful external BBO exists**.
- Without a lawful BBO: the correct result is a named market-evidence **NO_CALL_UNAVAILABLE**, zero placement, and **continued D membership** — not a fabricated price, not print-as-BBO substitution, not denominator removal.
- If these events are later scored, they remain in D and fail C; they are never excluded from the denominator.

(The instrument already implements exactly this pattern elsewhere: `contemporaneous_R1_external_bid_unavailable → NO_CALL_UNAVAILABLE` in the headroom armer, and `positive_size_external_bbo_unavailable` presence handling.)

## Superseding authorized repair — exactly this, nothing more

1. `causal_role` becomes optional steering input: absence produces a named NO_CALL (role-specific posture steering disabled), never `feature_censor`/terminal censoring.
2. Missing lawful in-window positive-size external BBO produces a named market-evidence NO_CALL (`NO_CALL_UNAVAILABLE` class); presence is attempted only where a lawful BBO exists.
3. Every one of the five events remains eligible inside D = 804 (denominator and actionable stream population; `event_terminal` must no longer be `censored_feature`).
4. **No order is created without a lawful BBO** — zero placements on all ten legs given the evidence above; no fabricated or print-derived prices.
5. Both candidate streams change for **exactly these five events**; the other 799 event streams per candidate remain byte-identical (proven by regeneration diff).
6. No scorer, no metrics: all performance fields remain null; no C/PC/S/IC population.
7. All other audit findings of `84cdf87a` remain untouched — including the Item-6 100¢ removal/deprecation requirement and the requirement that the corrected PRE-RUN arrive as a new additions-only commit on this lineage and pass a fresh independent audit before any execution package is considered.

Amended required invariants/tests for the corrected PRE-RUN (replacing the prior (i)–(v)):
(i) zero `censored_feature` terminals attributable to `causal_role` anywhere;
(ii) the five named events carry named causal_role NO_CALL and named market-evidence NO_CALL rows, zero placements, and non-censored terminals in both candidates;
(iii) eligible-event count = 804 in both candidates' actionable populations;
(iv) all 799 previously-eligible streams byte-identical under regeneration;
(v) a test pinning that absent lawful BBO yields NO_CALL + zero orders (no fabricated price path exists);
(vi) the existing 52 tests still pass.

**Status after this amendment: still BLOCKED pending the corrected PRE-RUN — but the repair above is the authorized specification for it.**
