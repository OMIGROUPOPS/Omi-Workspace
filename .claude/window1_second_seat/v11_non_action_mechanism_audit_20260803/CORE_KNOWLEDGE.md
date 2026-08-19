# CORE_KNOWLEDGE — the deduplicated substance of the Window-1 vault [ANALYTICAL_ESTIMATE · CONSOLIDATION]

**Dispatch license (L18): LAW_INDEX read at `ae731326`; laws consulted: L7 · L18.** Consolidation only —
every claim carries its source SHA; contradictions are flagged in `VAULT_MAP.md` (10 named), never
silently resolved here. Companion: `VAULT_MAP.md` (367 documents, one line each).

## ① THE MARKET — what the record knows about W1 premarket prices

**The object.** Kalshi tennis match markets (four series: KX{ATP,WTA}{,CHALLENGER}MATCH), two YES legs per
match summing structurally to ~100¢. Window 1 = the pre-match span; the dev corpus is the 804 floor-passing
Jul 12–20 games, 1,608 legs, with the full true-print tape (4,836,462 prints, all exchange-verified by
trade_id, phantom rate 0.0 — `db470ec8`, `3f4b0046`).

**The window's true geometry** (`c0056976`, the sole source — L11): recorder open → **formation** (books
open placeholder-wide ~90¢ spread and settle in a single repricing wave, median ~minutes; open =
spread-settle mid, `3c7bc577`) → the verified pre-match span → **the bell** (verified per game:
192 machine-exact · 571 tape-inferred ±30 min · 20 upper-bound · 20 UNKNOWN · 1 no-match; the machine-exact
bells match the post-hoc honest clock 192/192 at zero error, `620fe4c1`). **142 games' bells ring >60 s
before the recorded window edge** — the old "collapse games" were in-play tennis inside a mis-set window
(`3c7bc577`); vocabulary: *decided-early pair*, and motion words are leg-only (`8ab4f2d9` fold 7).

**How prices move pre-match** (`ec88f8e3` old-ruler journeys; re-based `e269779b`): movement is **steps,
not gradients** — the median leg does 81% of its whole travel in its top-3 hours (`ec88f8e3`). On verified
ground the pre-match world is majority-still: **FLAT_BOTH 440 / MIRRORED 298 / other 38** of 776 clean
spans (`e269779b`). The 13-family shape taxonomy (`e269779b`) with per-family floor-timing law: up-shapes
floor at 0.05–0.23 of the span (their floor ≈ the open), down-shapes at 0.78–0.99 (floor arrives late),
stills mid; mirror complements are real (EARLY_SET pairs, DRIFT pairs, LATE_BREAK pairs). Down-shapes
carry ~8–9¢ median depth below open with opposite early-callability (EARLY_SET_DOWN declares by f=0.25
100%, LATE_BREAK_DOWN 11% — `8ab4f2d9`).

**Where the value is.** The pair's value = both legs bought under par: offered-under-par exists on **680
of 804 games, 3,123¢ of total pre-match margin** (`96597c98` binding `c0056976`). The margin ladder is
thin-heavy: 58 games ≥10¢ (817¢), 265 ≥5¢, 435 ≥3¢, 245 at 1–2¢ (`96597c98`). Depth-of-fill is nearly
rule-insensitive (fill−floor median 2¢, `ab609761`); the binding question is *whether* a stand kisses and
how many pairs strand. The **running session low beats every static depth aggregate** (`ab609761`), and
the shortfall on the current lane is **mostly one cent of standing distance** (58% of too-deep floor
moments exactly 1¢ — `d211505b`). Roles are readable from drift alone at 95.1% once ripe, but ripeness is
five numbers, not one (UP 0.023 → WTA_CHALL 0.964 of span — `41c1f724`); early down-calls reverse (62.5%
at f=0.05). Recognition coverage is a pure function of the clock (`41c1f724`).

**Settlement truth** (`3f4b0046`, Kalshi's own rules verbatim): resolves Yes only "after a ball has been
played"; pre-match walkover → **fair-price scalar settlement, not void** (observed once: complementary
0.65+0.35 = 1.00, DJECIN); in-match retirement → that side No. A completed under-par pair's margin
survived every resolution mode observed; two collapse legs (RAF, SHE) resolved YES — the tape is not
destiny.

**Crediting law** (L0, `e073c606`): kiss=credit — any identified positive-size true trade at-or-below a
lawful standing rest, strictly after it stood; quote touch never credits; strict channel is
build-verification only. Kalshi serves full trade history but **no historical depth** — the recorder's
dual-book store is the sole standing-state source (L8, `db470ec8`).

## ② THE OS — organs, inputs → outputs, status

The judgment gate (V52 era, born `1d5564b5`) runs per receipt, clauses in order; the decision web at
decision grain is `2af60dfc` (standing reference):

| organ | consumes → produces | status · receipt |
|---|---|---|
| **Clause ① onset (wake)** | receipt stream → causal stability onset (A spread-collapse / B trade-cadence, sequential-prefix, no right edge) | LIVE — V52l ADOPTED (`6678fd0c`, L12) |
| **Clause ② read** | post-onset print+book history, causal-rank weighted → read state (RISING/FALLING/SETTLED), evidence sufficiency | LIVE (`08ce27c0`) |
| **Clause ③ level** | read + role instrument + policy → target cents | LIVE as V52l default; role lane = drift instrument (anchor = spread-settle mid, series floored at formation — L16, `a059264d` parity 139,430/139,430) |
| **Clause ④ referee** | pair disagreement → adjudication (market-proof precondition REMOVED at V52h, `b43d7cde`) | LIVE (`893ee4c6`) |
| **Clause ⑤ pair-entry conservation** | credited sibling entry → max lawful target | LIVE (`c235363e`→`ab841995`) |
| **Clause ⑥ joint-target conservation** | both targets → order-free joint ≤ par | LIVE (`ab841995`); slack-at-receipt shown non-commuting with a moving counterpart (`f30ea3eb`) |
| **N9 palantír** | dossier store → priors that inform, never gate | LIVE (`b09aa22b`, `9929e918`) |
| **Shape/role instrument** | drift vs anchor → CLIMBER/FALLER call | HIRED-CANDIDATE (`e269779b`); faithful — 100% ungated reproduction (`620fe4c1`) |
| **Ripeness gates** | live coordinates (trades/travel/minutes) → bind license | measured only: TRD5/TRV6 knee (`71de534a`); span-fraction gates not-live-realizable in the tail (L15) |
| **The live clock** | min(catalog schedule, in-play tape guard ≥5 prints/15 min both legs) → span end | measured (`620fe4c1`): late-by->30 min 70.3%→1.9%; guard latency median +233 s |
| **Crediting** | prints vs standing rests → valid fills on truth-table spans | LIVE (L0 + `fc17d0d3` grading binding) |

Exam protocol: THE FULL-804 EXAM on the truth table exclusively; four-state {COMPLETE_AT_DELTA, PARTIAL,
NEITHER, UNKNOWN_BELL(own class)} with valid fills only (`2aa454af` method, `96597c98` current).

## ③ THE LAWS

`LAW_INDEX.md` @ `ae731326` — L0–L18, one line each, SHA-cited; L18 (dispatch license) is seat-enforced.
This document consulted L7 and L18.

## ④ THE NUMBERS — the operator's measurements, current basis

- **Both-sides-under-par (offered) rate: 680/804 = 84.6%** of games; 3,123¢ total margin (`96597c98`).
- **The lane (L17 baseline): V52l lineage 311 completes / 714¢ = 45.7% of offered games, 22.9% of offered
  cents** (`96597c98`). V52r's own census: 300/662¢; V52s closed-loop: 310/581¢, bar FAIL (`16895d3f`).
- **Average locked delta on completes: 714/311 ≈ 2.3¢** (lineage) · 662/300 ≈ 2.2¢ (V52r); the honest-
  scoreboard standing baseline was 350¢/214 with **139 of 214 completes at exactly 1¢** (`2aa454af`).
- **Offer distribution:** 58 games ≥10¢ (817¢) · 265 ≥5¢ (2,157¢) · 435 ≥3¢ (2,743¢) · 245 thin 1–2¢
  (380¢) (`96597c98`).
- **Organ breakdown of the misses** (380 offered-not-completed, `1c9419a0`): **STOOD_TOO_DEEP 240 games /
  1,201¢ / 341 of 415 unbought legs (76% of the money — gap median 1¢, `d211505b`)** · authority-not-earned
  37 g / 152¢ · STOOD_ELSEWHERE (post-bell kisses) 16 g / 179¢ · onset-blocked 6 g / 37¢ · thin ≤1¢
  abstentions 79 g / 79¢ (banded apart). Pair-lows blocks: **zero moments** (removed at V52h and stayed
  removed).

## ⑤ THE GRAVEYARD — with causes

- **The reflex lanes** (Jul 21–29 rounds, t1/t2, range-attack, OS-family): retired — the reflex census
  found honest completes 0/393; all pre-gate fills were policy-born posts (`1d5564b5`).
- **The theta/hourly-median table** (`2d48e4ee`): scope-defective — journeys are steps (`ec88f8e3`).
- **The A/B onset binary**: replaced by the PRIMED ruling; "the bell" as a word: retired (fold 6).
- **The crediting illusion** (`AT_OR_ABOVE_UNCREDITED_TIMING`): dissolved — all 2,093 moments were
  post-credit export echo (`7a123d87`, `8b4483fb`).
- **The averages-can't-aim-depth line**: V52i/j/k triple-flatline (`576c705f`, `604ab3e7`, `de266f2e`),
  V52m/n (`da4fd13b`, `74a702c8`), the percentile target rules (`ab609761`) — every static depth aggregate
  lost to the session low; cause: depth is a per-moment market fact, not a population constant (L14).
- **V52o** (`fe9387b2`): the benchmark rule at the causal-onset clock — killed by the clock, not the rule
  (26.7% coverage; `41c1f724`).
- **V52p** (`020b775c`): killed by the anchor-binding defect, not the instrument (`620fe4c1`).
- **Uniform lane-wide shifts** (`d211505b`): DEF+1 loses 211 completes to par-crossing to rescue 51.
- **Slack-at-the-receipt** (`f30ea3eb`): count survives, identity doesn't — 68 knife-edge completes lost;
  the counterpart moves after the check.
- **Span-fraction gates live** (L15, `620fe4c1`): tail distortion ×1.6–×6.9.

## ⑥ OPEN QUESTIONS THE RECORD ITSELF NAMES

1. **V52s disposition** — closed-loop yield-priority preserved the invariant (0 violations) but banked
   −133¢ vs L17 and failed its mechanism bar; adoption/hold is operator-reserved (`16895d3f`).
2. **The conditional repair** — the narrow frontier ends where design begins: what conditioning closes the
   1¢ standing gap without re-pricing the knife edge (`d211505b`, `f30ea3eb`)?
3. **The 20 UNKNOWN-bell games** — permanently ungradeable or recoverable (`c0056976`)?
4. **"Fair price" settlement generality** — complementary-sum-100 observed at n=1 (DJECIN); Kalshi's
   discretion, not a proven invariant (`3f4b0046`).
5. **The live premium** — queue plausibility prices it (§6 of the synthesis); replay cannot; unmeasured.
6. **Live-clock coverage cost** — the composite clock costs 12–31 points of gate coverage
   (`71de534a`); whether an earlier independent bell feed (the prevention trio's observed edge, fold 7)
   recovers it is unbuilt.
7. **WTA_CHALL** — never ripens before the bell (0.964, `41c1f724`) and is the thinnest library cell
   (n=19, `8ab4f2d9`); the record has no working answer for the category.
8. **The 8-game grading-edge mismatch** — spans OK 776 vs lane-gradeable 784 (EMPTY/NO_FORMATION handling,
   `1c9419a0` conservation note): a seam awaiting a ruling.

*Conservation: companion map = 367 lines = 256 HEAD + 85 branch + 26 packages, exactly. Every § claim
above carries a SHA; the 10 standing contradictions live in the map header, unresolved by design.*
