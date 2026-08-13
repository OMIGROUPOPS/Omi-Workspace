# LAYER-1 RESTAMP, credit-aware — the 1,808¢ map finalized [ANALYTICAL_ESTIMATE]

Analysis seat only. Read-only. **Supersedes the Layer-1 labels @ `e17af2dc` — the 346-game population, the
1,808¢, and Layer 2's feasibility columns stand untouched.** Inputs, SHA-pinned: the credit reconciliation @
`7a123d87` (`RECONCILIATION_2093_MATERIALIZED_MOMENTS.jsonl.gz`: all 2,093 materialized at-or-above moments
are `EXPORT_GRAIN_ILLUSION` — the leg was already credited before every cited print; 0 crediting defects; 1
source-count residue, BLOCKED for operator review) and the canonical-clock receipts @ `ab841995`
(`SLEEPER_OFFER_REACHABILITY_RECEIPT.json`: 0 of 11 sleeper offers reachable under the canonical runtime
onset). Full rows: `LAYER1_RESTAMP_CREDIT_AWARE.csv` (346) + `.json`.

## The restamp rules (receipt-driven, no re-scoring)

**`STOOD_ELSEWHERE(AT_OR_ABOVE_UNCREDITED_TIMING)` is dissolved as a class.** Of its 192 dominant-labeled
legs, 191 are reconciled: the leg **was credited** — a real fill at its standing rest — before every one of
its cited floor prints; the decision-only export had no fill-terminal row and carried the last standing
target forward. Each restamps by its true pre-credit state:

- **142 legs → `BOUGHT_SIDE(CREDITED_ABOVE_LATER_FLOOR)`**: after the credit, the same leg's floor printed
  **below** the entry — the bought side paid more than the market later offered. Depth per leg: median 3¢,
  p25 1 / p75 5, max 58; leg-grain depth sum 868¢ (not additive with the game-grain 1,808¢).
- **49 legs → `BOUGHT_SIDE(CREDIT_CLEAN_EXPORT_ECHO)`**: no later floor undercut the entry. The echo carries
  no mechanism; the leg drops from its game's label join (no game was left with an empty join).
- **1 leg → `UNRECONCILED(SOURCE_COUNT_RESIDUE)`**: `26JUL15ROMGAL|GAL` is the **only** anomaly-labeled leg
  with zero materialized identities — plausibly the missing 2,094th count, but no source moment ledger
  exists at `e17af2dc` to confirm. No verdict invented; flagged for operator review with the residue.

**`INPUT_GRAIN_ASLEEP` reclassifies under the canonical onset, per leg.** Of the receipt's 11 sleeper
offers, 8 were asleep-dominant here and restamp **`LAWFUL_UNREACHABLE(FLOOR_PRE_CANONICAL_ONSET)` — true
misses: 0** (all 11 would become reachable only under the rejected fit-grid counterfactual, which would
change frozen clause ①; the other 3 receipt legs were never asleep-dominant and their labels stand). The
**9 asleep-dominant legs outside the receipt's population** (the 346-wide extension beyond the 113) restamp
`INPUT_GRAIN_ASLEEP(UNADJUDICATED_BY_CANONICAL_RECEIPT)` — 74¢ awaiting canonical-onset receipts from
Codex before any verdict is owed.

## The re-ranked map — Layer-1 reason × Layer-2 feasibility (all 23 cells, three cleanest exemplars)

Categories: AC=ATP_CHALL, AM=ATP_MAIN, WC=WTA_CHALL, WM=WTA_MAIN. m = margin ¢ forgone. Layer-2 carried
untouched from `e17af2dc`.

| ¢ | games | Layer 1 (restamped) | Layer 2 | categories | exemplars |
|--:|--:|---|---|---|---|
| **894** | 102 | **bought-above-later-floor + pair-lows block** | FEASIBLE | AC39/AM29/WM27/WC7 | **26JUL12HECISO(m63)** · 26JUL12GUEGOM(m57) · 26JUL12HERALM(m46) |
| 247 | 27 | bought-above-later-floor + stood-too-deep | FEASIBLE | AC13/WM7/AM5/WC2 | 26JUL12GARPRI(m44) · 26JUL12GIUBAR(m43) · 26JUL12ECHMUN(m37) |
| 206 | 84 | pair-lows block (alone) | FEASIBLE | AC45/WC24/WM8/AM7 | 26JUL14SMIILA(m41) · 26JUL12CHAJON(m12) · 26JUL20AKSCOS(m9) |
| 152 | 65 | pair-lows block + stood-too-deep | FEASIBLE | AC34/WM12/WC10/AM9 | 26JUL13KHOZHA(m7) · 26JUL14KOVBAS(m7) · 26JUL15OLIPRI(m7) |
| 71 | 3 | bought-above-later-floor + lawful-unreachable | FEASIBLE | AC2/WC1 | 26JUL12GANJAN(m56) · 26JUL12DEGEE(m12) · 26JUL12VOLMAR(m3) |
| 47 | 1 | bought-above-later-floor + asleep-unadjudicated | FEASIBLE | WC1 | 26JUL12ROUJAK(m47) |
| 39 | 12 | authority block + pair-lows block | FEASIBLE | AC5/WC4/AM3 | 26JUL13KRASAL(m7) · 26JUL12MALTUR(m5) · 26JUL14GENPET(m4) |
| 22 | 4 | bought-above-later-floor + authority block | FEASIBLE | AC2/AM1/WM1 | 26JUL19DJOMAT(m12) · 26JUL13MATMIC(m6) · 26JUL12DEJGAU(m3) |
| 17 | 10 | stood-too-deep (alone) | FEASIBLE | AC9/WC1 | 26JUL13RINAST(m4) · 26JUL14MARMAY(m3) · 26JUL12YIBMAL(m2) |
| 16 | 10 | pair-lows block + stood-too-deep | FLOORS_PRECEDED_PRIMED | AC6/WC2/WM2 | 26JUL12OKAIPE(m4) · 26JUL12BRUGAD(m3) · 26JUL13MUNLEO(m2) |
| 15 | 3 | bought-above-later-floor (alone) | FEASIBLE | WM2/AM1 | 26JUL15VANDRO(m7) · 26JUL13ZHEBOU(m4) · 26JUL18BERSAI(m4) |
| 14 | 2 | authority block + stood-too-deep | FEASIBLE | AC1/WC1 | 26JUL14DILFAL(m8) · 26JUL12BROHUA(m6) |
| 11 | 6 | pair-lows block (alone) | FLOORS_PRECEDED_PRIMED | AC5/AM1 | 26JUL12MARFOR(m4) · 26JUL15GENDE(m2) · 26JUL16ADDGHI(m2) |
| 10 | 3 | asleep-unadjudicated + pair-lows block | FLOORS_PRECEDED_PRIMED | AC2/WC1 | 26JUL12BARREI(m6) · 26JUL19SINMAT(m3) · 26JUL16ZANTRE(m1) |
| 10 | 2 | asleep-unadjudicated (alone) | FEASIBLE | AM1/WC1 | 26JUL12SOKNUG(m8) · 26JUL19MARSKA(m2) |
| 8 | 2 | lawful-unreachable + pair-lows block | FEASIBLE | AC1/AM1 | 26JUL12REJMID(m5) · 26JUL19TOKMIY(m3) |
| 6 | 2 | lawful-unreachable (alone) | FEASIBLE | AC2 | 26JUL13SHIHAR(m3) · 26JUL17ADDIVA(m3) |
| 5 | 1 | stood-too-deep + unreconciled-residue | FEASIBLE | AC1 | 26JUL15ROMGAL(m5) |
| 5 | 3 | authority block (alone) | FEASIBLE | WM3 | 26JUL12HERKAZ(m2) · 26JUL17PUTSHE(m2) · 26JUL19RUSKAZ(m1) |
| 4 | 1 | asleep-unadjudicated (alone) | FLOORS_PRECEDED_PRIMED | AC1 | 26JUL13GREVAN(m4) |
| 4 | 1 | lawful-unreachable + pair-lows block | FLOORS_PRECEDED_PRIMED | AC1 | 26JUL13PERTOB(m4) |
| 3 | 1 | asleep-unadjudicated + pair-lows block | FEASIBLE | AC1 | 26JUL14URSPAL(m3) |
| 2 | 1 | authority block + pair-lows block | FLOORS_PRECEDED_PRIMED | AC1 | 26JUL20VALGOM(m2) |

The former 963¢ head cell survives with its exemplars intact under the corrected name — PELSIL (m36, SIL
credited 7¢ above a later floor), MERDRO (m13, 10¢), KORJIM (m11, 10¢) all restamp
bought-above-later-floor + pair-lows.

## Mechanism totals (game counted once per mechanism in its join — rows overlap; the cells above partition)

| mechanism | games | ¢ |
|---|--:|--:|
| LICENSE_BLOCKED(PAIR_POST_ONSET_LOWS_NOT_UNDER_PAR) | 287 | 1,345 |
| BOUGHT_SIDE(CREDITED_ABOVE_LATER_FLOOR) | 140 | 1,296 |
| STOOD_TOO_DEEP | 115 | 451 |
| LAWFUL_UNREACHABLE(FLOOR_PRE_CANONICAL_ONSET) | 8 | 89 |
| LICENSE_BLOCKED(MACHINE_READ_LEVEL_AUTHORITY_NOT_EARNED) | 22 | 82 |
| INPUT_GRAIN_ASLEEP(UNADJUDICATED_BY_CANONICAL_RECEIPT) | 8 | 74 |
| UNRECONCILED(SOURCE_COUNT_RESIDUE) | 1 | 5 |

## Conservation

346 games and 1,808¢ exact across the 23 cells; Layer 2 unchanged (324 feasible / 1,761¢ + 22
floors-preceded-primed / 47¢; never-jointly-under-99 empty by construction). Anomaly accounting: 192
dominant legs = 191 reconciled-credited (142 bought-above + 49 credit-clean) + 1 source residue; 2,093
materialized moments dissolved, the 2,094th count frozen as residue @ `7a123d87`, not re-invented here.
Sleeper accounting: 11 receipt legs = 8 restamped lawful-unreachable + 3 never asleep-dominant; true misses
0; 9 asleep legs unadjudicated. No score, policy, or Layer-2 artifact touched. ANALYTICAL_ESTIMATE.
