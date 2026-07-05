# NIGHTLY PASS — night 1 of the week (window: aba83af boot 21:32:48 ET Jul 4 → 733341f restart 10:39:44 ET Jul 5)

**Headline: the bound stack works at volume — 41 of 69 completed pairs landed at EXACTLY
97 — and the night found one real defect (patched same-day through the gate, defect
exemption): the T-20m fallback bypassing the pair bound under the dormant T50 check.**

## (1) The staged passes

**Zero-tolerance board (with morning adjudication):** 15 raw monitor flags decompose to:
- **1 real defect, patched**: `t20m_fallback` pair-bound bypass — MUCKRE **110** (KRE 38
  filled; reshuffle held MUC pinned at 59=97−38 through a dozen clamps; the fallback then
  cancelled the pinned bid and rebid 62→72, filled), SAFDJO **100**, SABOSA **100**. Root:
  the fallback's T50 check is `[C-CAP-REMOVAL site 2]` — dormant under
  `paired_cap_enforced=false` (the June-12 residual's third strike). **C-FALLBACK-BOUND
  armed in `733341f`** (gated deploy 10:39): fallback price clamps lower-only to
  `goal − sibling_basis` (same basis resolution as complete_cross), ≤2¢ stays flat,
  clamped bid rests pinned. No tuning change — pure bound enforcement.
- **Metric A = 3** (IEMBER +5.1min @98, DELNIC +5.8min @78, DALARI +5.2min @94): all three
  are **`complete_cross` insurance completions** — deliberate post-grace-cancel IOC
  crosses inside their own armed cap (`ENTRY_COMPLETE_BASIS_CAP=102`), producing pairs at
  102/101/100. NOT stale bids, NOT crash-mediated. **OPERATOR ADJUDICATION NEEDED**: three
  pair bounds now coexist — goal 97 (reshuffle/re-aim/ZT), completion ceiling 99 (d2ac207),
  cross cap 102 — and the ZT class flags all >97. Either the ZT definition gets
  path-exceptions or the caps get pulled to 97; the monitor now path-tags every over-goal
  violation (defect vs armed-design) so the board reads honestly meanwhile.
- **6 pairs at 98–99**: completion-ceiling-legal (≤99). Same adjudication.
- **1 walk_cap flag (JANRYA 94c)**: monitor false positive — a completion-reprice buy with
  the sibling's fill booked late; the walk cap governs premarket walks, not completion
  pricing. Monitor fixed (uncorrelated buys reclassify to an info line).

**Ledger (98 events, all six cats): 27A / 12B / 31C / 16D / 12F** — vs healthy Jul-2
baseline 17/8/25/15/14 over 79. A-rate 28% (was 22%). **20 STRONG pairs (both legs under
FV, ≤100) — every prior night had ~0.** WTA_CHALL back in the book (8 events, 4A).

**Exchange truth:** cash **$842.73** + portfolio $76.96. ⚠ The ~$1,850 cash decrease vs
Jul-4 afternoon is NOT bot trading (+$19.81 realized, all 5-lots): the operator's manual
MLB NO-side (−1000×2) and TRUMP (+1000 @ ~70.7) positions bind roughly that collateral —
flagged for operator confirmation. 321 API fill rows in the window; ledger tickers
reconcile. Window realized (bot log): **exits +$53.51 (108 legs), settles −$33.70 (31),
net +$19.81, 30 open at window close.**

**Leak decomposition:** appended to `week_leak.jsonl` (37 new events; cumulative 58).

## (2) Rollups

| metric | night 1 | baseline (healthy Jul-2) |
|---|---|---|
| fills / pairs | **169 / 71** | 149 / 57 |
| tracked / rested | 234 / 129 | 193 / 82 |
| combined ≤97 | **56/69 (81%)** — 41 exactly 97, 8 ≤95 | (not measured then) |
| combined 98–100 / >100 | 9 / 4 | — |
| FV-capture | mean **+1.0¢**, 54% pos | +1.3¢ / 61% |
| FV riser/faller split | riser **+5.9¢ emfb, 37% under-FV** / faller **−2.6¢, 53% under-FV** (N=43/43) | audit: 8/11 risers above FV |
| half-arms | 27/98 (27.5%) | 28% |
| chase rate (fills at/after gun) | 70/169 (41%) | 57% |
| fv_observe riser accumulation | **452 — the ~100 gate is already exceeded**; the riser Plex bounce can run at full n whenever the operator calls it | 18 at week open |
| repriceable counter | 58 true / 593 false cumulative | — |

## (3) Night-2 check on night-1's headline — half_timing does NOT simply dominate anymore

Night-1 (crash-era sample, 21 events): half_timing 8 events / ~131¢ dominated.
Night-2 (held-config, 43 events): **by count, `half_no_dip` leads (22)** — bounds the tape
never offered, mostly deep bounds off cheap leg-1 fills; **by cents, ITF_W half_timing is
still the single biggest block (132¢, e.g. DEKCAK: fader printed 11 pre-leg1 vs bound
72)** — the early-fader-divot forfeit persists exactly where deliverable (c) lives (ITF
early window). pair_over_97's 40¢ ATP_CHALL faller_component was mostly the now-patched
fallback class. Revised week hypothesis: **the leak is bimodal — ITF timing (fader divots
pre-bound) + structural no-dip on deep bounds; the riser concession is a rounding error.**

## (4) Sub-B (grade-domain rollup, all KNOWN classes; chains in graded3_full.txt)

- 27× half-arm STARVATION (sib rested, unfilled) −$7.82 — the standing class; per-bid tape
  grading now separates true NO_FLOW from queue/set-below.
- 18× fragile (bought above onset) +$10.80 net (tape-rescued gifts).
- 6× over-par >100 −$2.50 — the fallback defect (patched) + crosses (adjudication).
- 4× exit-harvest FUCKUP-3 −$9.75 — pre-existing, untouched by the week's flags.
- 4× zero-discount +$4.30.
- **NEW classes: none beyond the patched fallback bypass.** Timing discipline: 161/161
  placed premarket; chase-fills 41% (was 57%).

Artifacts: on3_agg/ledger/participation/dump, graded3_full.txt, night1_rollups output,
metricAB_night1, leak run — committed under .claude/nightly_20260705/ + week_leak.jsonl.
