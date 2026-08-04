# Executable ceiling — time-overlap intersection of the residency-maker windows

Analysis seat only. Descriptive. Read-only on every input. Reachable windows read
directly from the per-leg quote tapes; window edges and floors from the committed
dual-floor ledger; closes from the independent audit (`INDEPENDENT_CLOSE_AUDIT_1608.csv`).
Per-event rows in `EXECUTABLE_CEILING_EVENTS.csv`; all numbers in
`EXECUTABLE_CEILING_SUMMARY.json`.

## Headline

The price ceiling of **390** events (both maker floors below own close, sum < 100)
collapses to **31** once you require the two legs to be reachable **at the same
time**. **359 of 390 (92%) are sequential-only.** The simultaneously-lockable
executable ceiling is **31 / 804 ≈ 3.9%** of games; at par (≤ 97) only **10**.

## Method and acceptance

For each of the 390 price-ceiling events, each leg's residency-maker reachable
window is the union of the contiguous tape intervals where `best_ask ≤ maker_floor`
(an offer at or below our resting maker bid is fillable) with the seller-aggressed
print instant at ≤ maker_floor. Two legs **OVERLAP** if their reachable sets
intersect in time (both rests fillable at once); **DISJOINT** if they never do.

Reachability is `best_ask ≤ maker_floor` and deliberately does **not** re-impose
the pricer's 10-second signing dwell or 5-lot capacity gate — those are signing
gates, not physical fill conditions, and `maker_floor` is already capacity-qualified
upstream (the qualifying ask carried ≥ 5 cap; the seller-aggressed print carried
real size). Re-imposing the 5-lot gate here wrongly drops legs whose offer sits at
the floor with a thin instantaneous display (e.g. HEM: ask resting at 27 ≤ its
maker floor 28 for the entire window, displayed size < 5 — plainly fillable).

**Acceptance (enforced before commit): PASS.** every leg has ≥ 1 reachable
interval (0 empty); OVERLAP + DISJOINT = 390; every DISJOINT gap > 0.

## Overlap vs disjoint

| | events | share |
|---|---:|---:|
| OVERLAP (simultaneous rests fillable) | **31** | 7.9% |
| DISJOINT (sequential-only) | **359** | 92.1% |

### By frontier tier (cumulative)

| pair sum | price-ceiling events | OVERLAP | DISJOINT |
|---|---:|---:|---:|
| ≤ 93 | 59 | 2 | 57 |
| ≤ 95 | 104 | 2 | 102 |
| ≤ 97 (par) | 217 | **10** | 207 |
| < 100 | 390 | **31** | 359 |

### By category × region

OVERLAP:

| category | le25 | 26_50 | 51_75 | ge76 | total |
|---|---:|---:|---:|---:|---:|
| ATP_CHALL | 3 | 6 | 8 | 0 | 17 |
| ATP_MAIN | 0 | 0 | 2 | 1 | 3 |
| WTA_MAIN | 2 | 2 | 0 | 3 | 7 |
| WTA_CHALL | 1 | 1 | 1 | 1 | 4 |

DISJOINT:

| category | le25 | 26_50 | 51_75 | ge76 | total |
|---|---:|---:|---:|---:|---:|
| ATP_CHALL | 28 | 61 | 60 | 18 | 167 |
| ATP_MAIN | 8 | 40 | 32 | 9 | 89 |
| WTA_MAIN | 18 | 22 | 18 | 10 | 68 |
| WTA_CHALL | 6 | 10 | 13 | 6 | 35 |

## The 359 sequential-only events — ordering and gap

**Ordering.** The **dearer** leg (higher maker floor) reaches its floor first on
**219** events; the cheaper leg first on 139 (tie 1). The common posture is
therefore the worse one: you are lifted on the expensive side and must then carry
it while chasing the cheap side.

**Gap** (time between the two reachable windows = the carry you hold, single-legged):

| bucket | events |
|---|---:|
| ≤ 15 min | 35 |
| 15-60 min | 71 |
| 1-4 h | 141 |
| 4-12 h | 76 |
| > 12 h | 36 |

Median gap **8,088 s (2.25 h)**, p25 44 min, p75 5.3 h. **253 of 359 gaps exceed
an hour; 112 exceed four hours.** The handful above 12 h include legs with
anomalous window bounds (e.g. a post-match seller-aggressed print), so the median
and the 1-4 h mode are the representative figures.

## Reading

The residency ruling makes the maker floor an honest *price* ceiling (390 events,
48.5% of the book). But an arb requires both legs *at once*, and on 92% of those
events the two reachable windows never coincide — the pair is legged, with a
typical 1-4 h single-sided carry, usually long the expensive side first. The
simultaneously-lockable executable ceiling is ~4% of games (≈1% at par). Any
target expressed as a completion rate over the book must be read against this
executable denominator, not the price denominator.

## Artifacts

Under `.claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/`:
`EXECUTABLE_CEILING_EVENTS.csv` (per event: classification, gap, which leg fills
first, reachable-interval counts) and `EXECUTABLE_CEILING_SUMMARY.json`.
