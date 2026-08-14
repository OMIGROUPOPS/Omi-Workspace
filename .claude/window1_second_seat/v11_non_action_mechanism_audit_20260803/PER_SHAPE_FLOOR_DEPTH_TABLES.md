# PER-SHAPE FLOOR DEPTH TABLES — the library the wiring consumes [ANALYTICAL_ESTIMATE · UNVALIDATED-CANDIDATE]

Averages die; shapes replace them. Priors-inform-never-gate. Corpus: taxonomy @ `e269779b` × truth table @
`c0056976` (verified pre-match spans only). Provenance triples in the JSON (source commit + path + sha256).
Full family×category grid (52 rows, cells n≥5): `PER_SHAPE_FLOOR_DEPTH_TABLES.{csv,json}`. Method: depth =
post-formation open − verified-span floor (¢); timing = floor position carried from `e269779b`; early-call =
for directional families the first path sample where drift reaches 2¢ in the family direction (f*, and %
declared by f=0.25/0.5), for still families the % still within ±2¢ of open at f=0.25/0.5.

## The one table — family rows (ALL categories; per-category rows in the CSV/JSON)

| family | legs | floor depth below open ¢ (p25/med/p75/p90) | floor timing (med pos) | early-call confidence |
|---|--:|---|--:|---|
| DRIFT_UP | 95 | −3.0 / **−2.0** / −1.0 / +1.0 (floor ≈ the open) | 0.07 | declares f*≈0.1; 80% by f=0.25, 96% by 0.5 |
| EARLY_SET_UP | 80 | −4.0 / **−3.0** / −2.0 / −0.5 | 0.06 | **declares immediately; 100% by f=0.25** |
| ONE_STEP_UP | 105 | −4.0 / **−2.5** / 0.0 / +3.0 | 0.23 | f*≈0.1; 62% by 0.25, 85% by 0.5 |
| LATE_BREAK_UP | 39 | −1.0 / **0.0** / +1.5 / +2.0 | 0.49 | **f*≈0.8; 28% by 0.25 — not early-callable** |
| DRIFT_DOWN | 44 | 7.0 / **8.5** / 10.0 / 13.5 | 0.97 | f*≈0.2; 59% by 0.25, 95% by 0.5 |
| EARLY_SET_DOWN | 62 | 7.5 / **9.0** / 11.0 / 14.0 | 0.59 | **declares immediately; 100% by f=0.25** |
| ONE_STEP_DOWN | 53 | 6.0 / **8.0** / 9.0 / 13.0 | 0.78 | f*≈0.3; 36% by 0.25, 77% by 0.5 |
| LATE_BREAK_DOWN | 37 | 7.0 / **8.0** / 12.0 / 15.0 | 0.99 | **f*≈0.9; 11% by 0.25 — not early-callable** |
| QUIET_WOBBLE | 615 | 0.0 / **1.0** / 3.0 / 4.0 | 0.54 | still-within-2¢: 62% at 0.25, 44% at 0.5 |
| ROUND_TRIP | 274 | 0.5 / **3.0** / 4.5 / 6.0 | 0.47 | still: 16% at 0.25, 6% at 0.5 (breaks ±2 then returns) |
| SLEEPER | 127 | −0.5 / **0.5** / 1.0 / 2.0 | 0.59 | still: 94% at 0.25, 89% at 0.5 |
| GRIND_WOBBLE_UP / _DOWN | 4 / 3 | −1.0 / +7.0 med | 0.14 / 0.86 | declares f*≈0.1 (tiny n) |

What the wiring reads from this, per shape instead of per average: **the down-shapes all carry the same
~8–9¢ median depth below open — but their floors arrive at opposite ends of the span (EARLY_SET_DOWN 0.59
vs LATE_BREAK_DOWN 0.99) and their callability is opposite (100% by f=0.25 vs 11%)**; the up-shapes' floors
ARE their opens (negative depth — stand at the open, early); the still families' depth is 0.5–3¢ with
ROUND_TRIP the only still family whose ±2¢ break is routine (84% break by f=0.25) yet returns. Per-category
rows preserve the cell differences — they are family-specific, not uniform (DRIFT_DOWN runs deepest in
ATP_CHALL, 10¢ median; EARLY_SET_DOWN deepest in WTA_MAIN, 10¢; ONE_STEP_DOWN flat at 8¢ across
categories; grid in the CSV).

Conservation: 52 rows over 1,552 corpus legs (family rows sum to 1,552; category cells n≥5 shown, remainder
in family-ALL); every number from the two provenance-tripled sources; no other input. UNVALIDATED-CANDIDATE
— a library for the plan organ to consume as priors, never gates. ANALYTICAL_ESTIMATE.
