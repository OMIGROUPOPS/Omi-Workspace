# FILL RATE REDO — spread-relative depths + the traverse (2026-07-09 ~3:25 am ET; 2,448 pairs; findings only)

**The operator's correction, vindicated in both directions.** Full raw grid (all cats × zones × bands × 4 depths, with time-to-fill): `GRID_TABLES.md`; `aggregate.json` + `fill_redo.py` banked; per-pair rows on the VPS. Depths: JOIN (standing touch) · touch−1 · 1×spread below mid · 2×spread below mid. Zones by each leg's own last-quoted mid. Volume bands: trailing-30m prints, both legs (V0=0 · V1 1–5 · V2 6–15 · V3 16+).

## PART 1 — the corrected grid (headline rows; full tables in GRID_TABLES.md)

| cat | band | JOIN | touch−1 | 1×spread | 2×spread | read |
|---|---|---|---|---|---|---|
| ATP_MAIN | V3 | **40–50% (ttf 15–16m)** | 4–8% | 4–8% | ~1% | **a JOIN market: the touch pays richly at volume; ANY depth dies instantly** (1¢ world) |
| ATP_MAIN | V1 | 12–15% | 1.6–2.6% | 1.6–2.4% | ~1% | |
| ATP_MAIN | V0 | 5–7% | <1% | <1% | ~0 | |
| ITF_W | V3 | 57–67% (7–8m) | 47–55% | **43–52%** | **33–42%** | **a DEPTH market: the whole ladder lives — 2×spread (≈12¢ down) still fills a third of the time at volume** |
| ITF_W | V1 | 11–14% | 6–10% | 5–8% | 3–5% | |
| ITF_W | V0 | 3–4% | 1.8–2.6% | 1.2–1.7% | 0.7–1.1% | |
| ATP_CHALL | V3 | 55–62% (6–8m) | ~46% | **41–45%** | ~30% | depth-capable at volume (2¢ world: 1×spread is shallow in cents, rich in structure) |
| ATP_CHALL | V1 | ~13% | ~6% | ~5% | ~3% | |

- **The mains ~1% is DEAD, as you called it:** measured in mains' own physics, a maker JOINING the touch at V3 fills **40–50% within 30 min (ttf ~15 min)** on 9–11k W1 volume. The absolute-3¢ pass was asking a 1¢ book to print a 3¢ discount — discount scarcity, not fill probability.
- **The dead book stays dead at every depth INCLUDING the touch:** V0 JOIN = 3–7% everywhere — the first honest V0 measurement (the old pass couldn't even pose the question at V0).
- **The regime split is structural:** mains' fill curve CLIFFS below the touch (50%→5% in one tick-class); ITF's degrades gracefully (67→55→52→42) — fat spreads keep the whole depth ladder alive.

## PART 2 — THE TRAVERSE

| cat | zone | touch range (med) | net drift | path vol | patient-join fills med/p75 | capture total med/p75 |
|---|---|---|---|---|---|---|
| ITF_W | 75-94 | **45¢** | +29 | 158¢ | **0 / 0** | 0 / 0 |
| ITF_W | 50-74 | 26¢ | +6 | 97¢ | 0 / 0 | 0 / 0 |
| ITF_W | <50 | 18¢ | 0 | 71¢ | 0 / 0 | 0 / 0 |
| ATP_CHALL | 75-94 | 12¢ | +5 | 33¢ | 0 / 0 | 0 / 0 |
| ATP_MAIN | all zones | **1¢** | **0** | **2¢** | 0 / 0 | 0 / 0 |

**Two refutations, one confirmation:**
1. **The mains drift term is ZERO:** the mains touch moves a median of 1¢ over the whole 8-hour window (path volatility 2¢ cumulative). "1¢ spread × 10k volume × 8h drift = steep discounts assembled sequentially" fails at the drift factor — **there is no path to assemble.** What mains offers instead is Part 1's JOIN row: high-frequency fill AT the touch, edge bounded by the 1¢ spread (queue/adverse-selection economics, NOT measured here — flagged as the open question if a mains posture is ever wanted).
2. **The strict patient-join ratchet captures ~nothing ANYWHERE** (fills med AND p75 = 0): a downward-only touch−1 ratchet perpetually undercuts a falling book and is pierced only by knife prints; in mains it never fills because nothing moves. The compounding mechanism as specified does not exist in any cat.
3. **ITF's single-fat-divot mechanism confirmed against the alternative, same convention:** the ITF heavy-zone path is enormous (45¢ range, +29 net upward drift — the June winner-up shape at population scale) and its capture lives at DEPTH inside volume windows (S1/S2 at V3: 33–52%), not along a join-path.

## PART 3 — VERDICTS + RE-PROPOSALS (nothing ships; awaiting operator read)
- **Two regimes EXIST, and they are Part 1's rows, not the path thesis:** **MAINS REGIME** = join-at-touch, thin-edge, high-frequency, volume-gated (V3), depth forbidden (aims below the touch aim at nothing — the cliff). **ITF REGIME** = fat-divot at depth, volume-gated, cell-edge-scaled (the ratified aim surface). CHALL sits on the ITF side with compressed cents. **Consumption postures per the category law: macro (cat, cell) says which regime; tape (volume band) says when.**
- **Gauge re-fit, RE-STATED on the corrected grid:** ITF/CHALL unchanged from the first proposal in shape (QUIET V0 / WAKING V1 / OPEN ≥V2, deep-open V3) — now with JOIN-vs-depth fill curves per state. **MAINS-OFF verdict REVERSED as suspended: the gauge is meaningful in mains at the JOIN depth (V0 5–7% → V1 12–15% → V3 40–50%) — mains gauge ON, join-posture-only, if a mains posture is ever ruled.** The gauge config deploy still waits on the operator.
- **Open question flagged, not answered:** mains join-at-touch fill probability ≠ join-at-touch profitability (adverse selection at a 1¢ spread is the whole game there); measuring it needs an exit-side convention this entry-scoped pass deliberately does not touch (0A standing order).
