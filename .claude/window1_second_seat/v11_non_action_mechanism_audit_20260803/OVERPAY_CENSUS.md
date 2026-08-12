# The overpay census — discount depth on pairs we already won [ANALYTICAL_ESTIMATE]

Analysis seat only. Read-only. Measurement only — no build proposals. Population: **the 396 completed dev
pairs, V47 `fb74c8b8`, machine records only** — rest paths from the lane-deduped ACTION_TRACE (doctrine 3),
prints fit-local, the quarantined CAUSAL_LEG_TABLE **not used**. Per credited leg: **overpay = entry − lowest
true print eligible while the rest lawfully stood** (p ≤ the standing rest at its moment, withhold-held levels
included; span = first action → fill). Machine artifact: `…/OVERPAY_CENSUS.json`.

## The headline — the won book is nearly overpay-free

| | value |
|---|--:|
| credited legs scored | 792 (396 pairs × 2) |
| **legs with any overpay** | **63 (8.0%)** |
| **total cents left on the table** | **119¢** (vs 571¢ locked — the discount headroom on won pairs is ~21% of the lock, thin per leg) |
| distribution (all 792) | p25 0 · median 0 · p75 0 · **max 15** |

By leg-of-pair: **FIRST legs 40¢ total (max 8)** · **SECOND legs 79¢ (max 15)** — the second leg overpays 2×
the first. Per category (totals): in the JSON (`overpay_distribution.per_category`); ATP-side carries most.

Mechanically, an overpaid leg is one whose **fill print landed below the standing rest** — trades-as-truth
fills at the rest's level, so the machine paid the rest while the tape printed deeper; any earlier sub-rest
print would itself have been the (earlier) fill, which is why medians are zero.

## Mechanism classes (every overpaid leg exactly one; anatomy-site keyed)

| class (site) | legs | cents |
|---|--:|--:|
| **STOOD_TOO_HIGH_FROM_JOIN** (S4/S6) | 25 | **59** |
| **CAP_BOUND** (S16 — rest pinned at the cap when the deep print came) | 27 | 48 |
| WALKED_AWAY_FROM_LOW (S7/S10 tracking) | 11 | 12 |
| GUARD_DELAYED (S12 — low during a withhold) | 0 | 0 |
| ARRIVED_AFTER_LOW (S17/window) | 0 | 0 |
| other-named | 0 | 0 |
| **total** | **63** | **119** |

- The join is the largest single source (25 legs / 59¢): the armed join stood above where the crossing print
  actually landed — the S4/S6 discount organ's entire dossier is 59¢.
- CAP_BOUND (27/48¢) is the cap's *second* face: on won pairs it pins the second rest at 99−first-entry and the
  fill prints deeper — same S16 organ as the richness defect, here costing cents instead of pairs.
- GUARD_DELAYED is empty — no eligible low printed during a withhold on won pairs.
- ARRIVED_AFTER_LOW is structurally empty on this brain: V47 places at the first two-sided receipt, so no
  pre-stand window exists inside the fit span (measured, not assumed: 0 legs with a pre-stand session low
  below entry).

## Conservation

396 pairs → 792 credited legs, all scored; 63 overpaid = 25+27+11+0+0+0, cents 119 = 59+48+12; first+second
totals 40+79 = 119. Denominators: dev-804 fit windows, V47 fb74c8b8 crediting; prints = fit-local reconciled
corpus; rest paths lane-deduped per doctrine 3. ANALYTICAL_ESTIMATE (trace-reconstructed standing spans).
This is the entry dossier for the discount build — measurement only.
