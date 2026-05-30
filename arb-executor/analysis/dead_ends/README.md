# Dead ends — what we tried and REJECTED (do not build on these)

These artifacts are kept for traceability so we don't re-walk the same wrong paths.
Each was superseded for a specific, documented reason. **None of these are ground truth.**

## Scorecard (built on the BROKEN `cells` grid)
- `scorecard_atp_main.py` / `.json` / `.png`
- `viz_scorecard_atp_main.py`

**Why rejected:** built on the original `cells` grid in the pooled surface, which is
relative-trajectory based and disagrees with the `achievable` answer key on 82/90 cells.
The corrected replacement is `analysis/build_corrected_surface.py` →
`{cat}_corrected_surface_v3.json`, which rebuilds the grid from the honest corpus
reconstruction (own cost basis, validated against `achievable`).

## Static PNG pyramids (superseded by interactive HTML)
- `pyramid_atp_main.py` / `.png`
- `pyramid_v3_atp_main.py` / `.png`

**Why rejected:** static images. The deliverable had to be an INTERACTIVE D3 pyramid
(hover, lenses, per-cell scrollable y-axis) matching the original "actual pyramid" the
user referenced. The live version is `analysis/build_pyramid_html.py` →
`{cat}_pyramid_v3.html`.

---

## The two strategy conclusions that drive everything (the "what not to do / what to lean into")

**DO NOT:**
- Use the `cells` grid — it's broken (relative-trajectory; disagrees with `achievable` 82/90).
- Chase jackpot exits — thin/extreme cells' deep exits rest on 4–7 lucky tapes (e.g. 5c→+65 on 4/21; 9c→+90 on the same 7 winners, which is why its hit looks flat/stale at ~30%).
- Pool aggressively — the locked doctrine (`../../data/durable/spike_volatility_map/ATP_MAIN_LOCKED_DOWN.md`) shows pooling cells 37/38 DESTROYED edge. Real cell heterogeneity is not noise.
- Re-bucket by price excursion — we only have anchor (T-20) + peak (raw_max), no pre-anchor band. Inventing a price-band history is inventing data.
- Let an approximation override the tape — "the tape always wins."

**LEAN INTO:**
- `achievable` is the answer key for exits — EXCEPT thin extreme cells need recalibration off a credible high-frequency basis.
- Target high-frequency zones that still generate alpha (e.g. 5c high-teens: +15→hit~40%/ROI~300%), not the rare jackpot. Mirror on the favorite end (bank high-frequency small wins; respect the hit cliff, e.g. 89c +5 hit96% vs +9 hit72%).
- Each cent 5–94 gets its OWN unique config via apples→oranges: pool the *move shape* across the TIGHT neighborhood (own dominant, ±1 heavy but below own, ±2 lighter, ~zero past), then re-express against each cent's OWN cost basis.
- T-20 is the conservative FLOOR (taker, `maker_bid_offset=0`). Entry discounts = Part 2, layered later.

See `../EXIT_STRATEGY_HANDOFF_v3.md` for the full state of the world.
