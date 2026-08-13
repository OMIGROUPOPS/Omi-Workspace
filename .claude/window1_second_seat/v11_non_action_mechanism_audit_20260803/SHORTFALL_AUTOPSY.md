# The shortfall autopsy — dev-804 exam @ 4716657a [ANALYTICAL_ESTIMATE]

Analysis seat only. Read-only. Population: every shortfall game in the four-state disposition —
**232 PARTIAL_FOR_REASON + 301 NEITHER_FOR_REASON + 4 COMPLETE_AT_LOSS = 537.** Sources: the exam's own
four-state event ledger + post-onset offer capture ledger (`4716657a`; its offer classes reproduce
`22441e05` exactly: 612/72/82/36/2). Money = the offered margin (100 − post-onset pair floor), **no fee
adjustments anywhere — a 1¢ margin is 1¢ of real money and is reported as such.** Machine rows:
`SHORTFALL_AUTOPSY.json`.

## Separated by fact, not excuse

- **(a) The awake market never offered — 191 games** (floors never summed <100 post-onset): abstention
  structurally correct; 0¢ forgone by construction. Their gate reasons are still named below.
- **(b) Offered and not completed — 346 games, 1,808¢ forgone.** By reason, thin margins included as their
  own band, no justification language.

Cross-conservation: 804 = 267 COMPLETE_AT_DELTA (266 on offered games + 1 on a non-offered game) + 537
shortfalls (346 offered + 191 not-offered); the 612 offered = 266 completed-at-delta + 4 completed-at-loss +
342 partial/neither... stated exactly: offered × state = 266 CAD + 4 CAL + 231 PARTIAL + 111 NEITHER = 612. ✓

## THE RANKED TABLE — reason → games → cents → exemplars (the next loop round's screw list)

| # | fact | dominant reason | games | ¢ forgone | margin bands (1–2/3–4/5–9/10+) | categories (AC/AM/WC/WM) | three cleanest exemplars |
|--:|---|---|--:|--:|---|---|---|
| 1 | OFFERED | **STABILITY_ONSET_NOT_REACHED** | 113 | **890** | 43/26/24/**20** | 59/20/8/26 | **MERDRO (exact, m13)** · DEGEE (exact, m12) · MULSHE (exact, m11) |
| 2 | OFFERED | **PAIR_POST_ONSET_LOWS_NOT_UNDER_PAR** | 176 | **659** | 91/35/44/6 | 87/29/32/28 | **PELSIL (exact, m36)** · NIKVRB (exact, m9) · ZINGAL (exact, m8) |
| 3 | OFFERED | onset + pair-lows mixed | 32 | 111 | 20/8/3/1 | 16/5/9/2 | OKAIPE (exact, m4) · GORMIN (exact, m2) · MARROS (exact, m1) |
| 4 | OFFERED | **MACHINE_READ_LEVEL_AUTHORITY_NOT_EARNED** | 15 | 109 | 3/5/5/2 | 5/3/4/3 | MALTUR (exact, m5) · KABCHI (exact, m3) · RUSKAZ (exact, m1) |
| 5 | OFFERED | **COMPLETED_AT_LOSS** | 4 | 20 | 0/2/2/0 | 0/1/0/3 | BERSAI (exact, m4) · VANDRO (m7) · BARYUA (m5) |
| 6 | OFFERED | authority + pair-lows mixed | 4 | 14 | 2/1/1/0 | 2/0/2/0 | DILFAL (m8) · ZHUYUN (m3) · ARSRIC (m2) |
| 7 | OFFERED | authority + onset mixed | 2 | 5 | 1/1/0/0 | 2/0/0/0 | GENPET (m4) · DONWES (m1) |
| 8 | NOT_OFFERED | pair-lows (correct abstention) | 81 | 0 | — | 45/4/23/9 | BINGIL · FUEROS · HOHSUR (all exact) |
| 9 | NOT_OFFERED | onset (correct abstention) | 61 | 0 | — | 37/4/12/8 | FANBIG · LAGTEP · SALARN (all exact) |
| 10 | NOT_OFFERED | onset + pair-lows mixed | 46 | 0 | — | 23/5/17/1 | BOUGAN · CHOSUR · GOMARN (all exact) |
| 11 | NOT_OFFERED | **NO_GATE_BLOCK_RECORDED** | 2 | 0 | — | 1/1/0/0 | MATMOR · CORSAC — **named gap: shortfall with no recorded block; provenance item** |
| 12 | NOT_OFFERED | authority + pair-lows | 1 | 0 | — | 0/0/1/0 | BASRUS |
| | | **Σ** | **537** | **1,808** | | | |

## Reading the screw list

- **Screw #1 — onset (890¢, half the bill):** the wake-up qualifier is the single largest named blocker on
  offered games, and its exemplar list is headed by **MERDRO at exact bell with a 13¢ margin** — the gate
  sat out the campaign's own deep-discount archetype because clause ① never fired. This is the PRIMED
  refinement's money case (§8: the interim binding is CODEX-INTERIM; 111 games already flip on candidate
  choice).
- **Screw #2 — pair-lows-under-par (659¢, the widest, thinnest):** 91 of its 176 games sit in the 1–2¢ band —
  reported as real money without justification language, per order; its head exemplar is anything but thin
  (**PELSIL, exact, 36¢**). Clause ④'s under-par arithmetic on running lows is the second organ.
- **Screw #3 — level authority (109¢ + 19¢ mixed):** small but dense (median band 3–9¢) — the four-check
  authority earn (clause ③/N4) refuses levels on offered games.
- **COMPLETED_AT_LOSS (4 games, 20¢):** the only class where money was lost rather than forgone; license
  autopsy exists in the exam dir.
- **Rows 8–10 (188 games):** structurally correct abstention — the market never summed under par while awake.
  **Row 11 (2 games): NO_GATE_BLOCK_RECORDED — a shortfall with no named block is a provenance defect, not an
  excuse; flagged.**

## Conservation

537 = 346 offered (890+659+111+109+20+14+5 = 1,808¢) + 191 not-offered (0¢); states 232+301+4; margin bands
sum within each row; categories sum to row counts; offered × state cross-table exact (above). Exemplars
exact-bell preferred (rows 1–5 heads all exact). ANALYTICAL_ESTIMATE.
