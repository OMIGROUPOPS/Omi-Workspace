# SEQUENTIAL FLOOR — BUCKET RE-CUT on the current grid (2026-07-08 night; fav/dog binary RETIRED as a frame)

**The grid: 90 cells/cat ([5,95) 1¢ cells) × 6 cats.** Each LEG keyed by its OWN W1-closing price cell — no side aggregates anywhere. Full 1¢ raw tables: `RECUT_TABLES.md` (538 populated cell rows) + `recut_cells.json`. Source: the existing seqfloor per-pair json (2,435 pairs → 4,870 legs), entry-only convention unchanged. **ITF_M/ITF_W exits are Challenger-BORROWED — `ITF_EXIT_BORROW = {'ITF_M': 'ATP_CHALL', 'ITF_W': 'WTA_CHALL'}` (live_v4.py:288, verified in the deployed tree; the durable exit dir carries exactly four native parquets, no ITF) — every ITF row below grades entries against a borrowed exit surface and is labeled so.** This VERIFIES AND CLOSES queued #17.

## §1 What the cell lens shows that fav/dog hid
**Depth is a property of the CELL, not the side.** The fav/dog binary was a proxy: "fav edge big / dog edge zero" decomposes into a smooth monotone cell curve —
- **Cells <50: edge p50 = 0 in every cat.** A leg closing under 50¢ has essentially no W1 dip below its close, whoever it is. Its deepest moment sits T−5..−23 min (late) and it dips first only 7–45% of the time.
- **The crossover is ~cell 50–55 (ITF), ~cell 80 (CHALL):** edge appears and rises with price.
- **Cells 75–94 (the heavy zone): ITF edge p50 per 5¢ band runs 6–19¢ (≥5¢ on 55–75% of legs), deepest moment T−36..−71 min, dip-first 68–84%.** CHALL 80–94: p50 3–10¢, ≥5¢ on 43–52%, dip-first 78–86%. Mains: 1–2¢ flat at every cell — the grid confirms par-lock cell-by-cell.
- OUT-OF-BAND cells (0–4, 95–99) shown in the raw tables for completeness; untradeable under C-BAND-CLAMP.

5¢-banded view of the heavy zone (full 1¢ grain in RECUT_TABLES.md):

| cat (exit provenance) | cells | n | edge p50 (med of cells) | ≥5¢ % | t_deep p50 | dip-first % |
|---|---|---|---|---|---|---|
| ITF_M (borrowed ATP_CHALL) | 75-79 | 86 | **19** | 62.8 | −41m | 68.6 |
| ITF_M (borrowed) | 80-84 | 72 | 12 | 61.1 | −56m | 73.6 |
| ITF_M (borrowed) | 85-89 | 56 | 9 | 64.3 | −55m | 76.8 |
| ITF_M (borrowed) | 90-94 | 91 | 9 | 67.0 | −47m | 78.0 |
| ITF_W (borrowed WTA_CHALL) | 75-79 | 78 | 6 | 55.1 | −36m | 70.5 |
| ITF_W (borrowed) | 80-84 | 66 | 12 | 63.6 | −71m | 78.8 |
| ITF_W (borrowed) | 85-89 | 79 | **19** | 69.6 | −54m | 72.1 |
| ITF_W (borrowed) | 90-94 | 55 | 12 | 69.1 | −70m | 83.6 |
| ATP_CHALL (native) | 80-84 | 37 | 3 | 46.0 | −77m | 78.4 |
| ATP_CHALL (native) | 85-89 | 29 | 10 | 51.7 | −57m | 86.2 |
| ATP_CHALL (native) | 90-94 | 35 | 4 | 42.9 | −69m | 82.9 |
| ATP_MAIN / WTA_MAIN (native) | 75-94 | 44/59 | 1–2 | 0–33 | early, diffuse | 40–80 |

## §2 Heavy-fav cells (75¢+) — the W1-clip vs the vaulted loser-crater
The vault's standing bleed exhibit is the heavy leg that LOSES: held to settlement it craters its full basis (FUCKUP-3 / MIXKRU class; the riser/faller asymmetry). The cell lens sizes the counterweight **inside W1, before the game can hurt anything**:
- **W1-clip opportunity per heavy cell (ITF): med 9–19¢ below the leg's own close, present on 55–75% of legs, landing T−36..−71 min.** That is the discount a resting bid at the cell's dip captures WITHOUT settlement exposure — buy the dip, and the leg's own W1 close is already above you by the clip amount before the bell rings.
- Per-cell detail (1¢) in the raw tables — e.g. ITF_W cells 85–89 individually run p50 14–24¢ with n 12–21 per cell.
- **Entry-only honesty: the clip is MEASURED to the W1 close, not to cash.** Whether the clip converts (sell into close, complete the pair, or carry) is the W1→W1 mandate's second factor — no settlement columns here, per the standing order. What the cell lens establishes is that the heavy zone's ENTRY discount is the largest on the whole grid — the primary bleed focus (the crater class) is also the primary clip surface.

## §3 S-line + AIM_V2 re-anchor, restated CELL-conditional
- **The dynamic S reference (replaces one-constant-per-cat as the aspiration):** a pair's sequential floor = Σ over its two legs of (leg's W1-close − edge_p50(cat, cell)). The cat constants proposed earlier (ITF 79/79, ATP_CHALL 92) are the corpus medians OF this formula and stand as the summary bar; the cell formula is what AIM_V2 should target per pair. Operator ratifies both or either.
- **AIM_V2 aim key = (cat, cell): aim depth = edge_p50(cat, cell), floored per existing rules.** Cells <50: aim depth 0 → JOIN policy (a depth aim there is aiming at nothing — restated from the fav/dog cut, now with the exact boundary). Cells 50–74: shallow aims (2–8¢ ITF). Cells 75–94: the deep-aim zone (9–19¢ ITF, bucket detail per 1¢ cell in the json — the table can be loaded directly as the aim surface prior).
- **Timing priors per cell ride the same json:** heavy cells dip T−36..−71 min (patience window); light cells' floors arrive T−5..−23 min (completion timing, flow-gated — the gun's habitat).
- **ITF caveat, labeled everywhere: these are ENTRY aims graded against Challenger-borrowed EXIT surfaces** — if the borrowed bands mis-price ITF exits, the clip's conversion (not its existence) moves; the exit-provenance labeling exists so no future readout silently blends the two.

## §4 Grid lineage (per operator, 07-08) — THE GRID goes on FOUNDATIONS
April 56-cell grid → VERSION B 41-cell → **current: 90 cells/cat ([5,95) 1¢) × 6 cats, ITF exits Challenger-borrowed.** Older frames are history-only under the chronology law; **any future analysis quoting a retired grid (56-cell, VERSION B 41, or the fav/dog binary as a frame) is a C45 failure.** The vault front page carries THE GRID from this close-out.
