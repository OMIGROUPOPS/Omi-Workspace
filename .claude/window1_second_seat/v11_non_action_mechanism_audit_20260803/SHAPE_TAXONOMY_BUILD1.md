# THE SHAPE TAXONOMY — build 1, on verified ground [ANALYTICAL_ESTIMATE · UNVALIDATED-CANDIDATE]

Analysis seat only. No wiring, no mechanisms — the catalog and the benchmark. Corpus: **only the verified
pre-match spans of `W1_GROUND_TRUTH_TABLE` @ `c0056976`** — 776 clean-span games; the 28 others excluded
and named in the JSON (20 UNKNOWN-bell, 3 EMPTY, 5 NO_FORMATION). Full rows:
`SHAPE_TAXONOMY_BUILD1.csv` (1,552 legs) + `.json`.

## ① The signature (method stated)

Per leg, on the T-minus axis normalized to its verified span [formation end → bell]: the forward-filled
last-true-print path sampled at 17 points (leading value = the post-formation open), with features
net · travel · biggest single step share · first-quarter net · last-quarter net · reversal count.
Families assigned by stated rules (order: SLEEPER → ROUND_TRIP/QUIET_WOBBLE when |net|<5¢ → LATE_BREAK
when ≥70% of the net is in the last quarter → EARLY_SET when ≥70% is in the first quarter and flat after →
ONE_STEP when one inter-sample step carries ≥60% → GRIND_WOBBLE → DRIFT).

## ② The families [CANDIDATE] — 1,552 legs

| family (plain English) | legs | floor-timing (median position) |
|---|--:|--:|
| QUIET_WOBBLE — never leaves a 5¢ band | 615 | 0.54 |
| ROUND_TRIP — travels ≥10¢, comes back | 274 | 0.47 |
| SLEEPER — almost no prints | 141 | 0.59 |
| ONE_STEP_UP — one repricing step carries the climb | 105 | 0.23 |
| DRIFT_UP — steady climb | 95 | **0.07** |
| EARLY_SET_UP — climbs in the first quarter, then done | 80 | **0.05** |
| EARLY_SET_DOWN — falls early, then done | 62 | 0.61 |
| ONE_STEP_DOWN — one step carries the fall | 53 | 0.78 |
| DRIFT_DOWN — steady fall | 44 | **0.96** |
| LATE_BREAK_UP — the whole move is the last quarter | 39 | 0.49 |
| LATE_BREAK_DOWN — falls only at the end | 37 | **0.99** |
| GRIND_WOBBLE_UP / _DOWN | 4 / 3 | 0.12 / 0.86 |

Pair view on verified ground: **FLAT_BOTH 440 · MIRRORED 298 · OPPOSED_UNBALANCED 20 · DECOUPLED 18**
(the old-ruler world was 547 mirrored of 801 — most of that motion was in-play; the verified pre-match
world is majority-still). Mirror pairings are real complements: EARLY_SET_DOWN+EARLY_SET_UP 33 ·
DRIFT_DOWN+DRIFT_UP 26 · LATE_BREAK_DOWN+LATE_BREAK_UP 19 · ONE_STEP_DOWN+ONE_STEP_UP 17. **The
floor-timing law by shape, not assumption: up-shapes floor at the start (0.05–0.23), down-shapes floor at
the end (0.78–0.99), still-shapes floor mid.**

## ③ THE BENCHMARK — same receipts, verified truth

At each leg's actual first-post receipt (census @ `336f42bf` / `FIRST_POST_LEDGER` @ `4716657a`), the
early-window signature alone: **drift = last in-span print before the receipt − post-formation open;
≥+2¢ → CLIMBER, ≤−2¢ → FALLER, else ABSTAIN.** Truth = verified-ground roles (298 mirrored pairs,
CANDIDATE). 483 role-legs posted; 236 pairs with both legs posted. The census baselines (63.5% / 51.9% /
25%) were scored on old-ruler truth; the machine is re-scored here on the identical receipts and verified
truth for like-for-like.

| | leg accuracy | pair both-right | full inversion |
|---|--:|--:|--:|
| **signature, called (84% coverage)** | **95.1%** (385/405) | **72.5%** (171/236) | **1.7%** (4) |
| signature, forced (all 483) | 87.2% | — | — |
| machine read-at-post, same receipts/truth | 73.3% (354/483) | 63.1% (149/236) | **16.9%** (40) |

Signature accuracy by time-into-window: Q1 88% · Q2 97% · Q3 97% · Q4 97% — it *improves* with the
window (the machine's declined). By cell (n≥15): every cell 87–100%; ATP_CHALL|26_50 98%. By family:
DRIFT 100% · EARLY_SET 98% · ONE_STEP 90–95% · LATE_BREAK 81–90% (the weakest called family, as its
construction predicts).

## ④ The honest split

**Callable early:** DRIFT_*, EARLY_SET_*, ONE_STEP_* — the drift has declared by the posting moment
(90–100% called accuracy). **Indistinguishable early:** LATE_BREAK_* by construction (the move IS the
last quarter) plus the abstain set (72 of 483 posted role-legs, mostly QUIET_WOBBLE / ROUND_TRIP ties).
**Priced:** mirrored offered games carrying a LATE_BREAK leg — **47 games / 368¢** of pre-match margin
(ALVVAN 27¢ · ARIZHA 18¢ · RAQKUM 17¢) — against **233 games / 1,358¢** on callable families (FETPIE
22¢ · SAKKOR 17¢ · BORDIM 16¢). The residual is named, priced, and not claimed.

## ⑤ The MORNEP standard — the target row

`26JUL12MORNEP` @ `c0056976`: verified span OK · library floors MOR 71¢ / NEP 24¢ · fills **71 and 24 —
at the floors, both PRE_BELL_VALID** · locked delta 5¢ on valid fills. Reads matching roles, targets at
library floors, fills pre-bell. **The taxonomy's job is making that row reproducible on purpose.**

## Conservation

804 = 776 corpus + 28 excluded-and-named; 1,552 legs signed; pairs 298+440+20+18 = 776; 483 role-legs
posted, 236 pairs both-posted (171+4+61); benchmark denominators exact; families sum to 1,552. All role
and family tables UNVALIDATED-CANDIDATE — priors, not gates; no decision-input claims; no wiring.
ANALYTICAL_ESTIMATE.
