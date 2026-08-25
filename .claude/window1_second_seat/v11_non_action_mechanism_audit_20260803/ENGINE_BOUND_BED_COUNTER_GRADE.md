# ENGINE-BOUND BED COUNTER-GRADE — @d837b992

License: LAW_INDEX read @d837b992, sha256 41784e6a… (verified this seat).
Build: `window1: bind V54 engine and bank floor self-stop`.
Package: `stage1_store/v54_engine_binding_floor_capture_20260825/` (custodied trace read locally).
Verification seat: CC. Filed findings: F-VS-207 … F-VS-210.

---

## 1 — The binding is real. Six fills, not seven. Determinism holds.

**Records loaded.** `NEIGHBOR_SPECIALIST_BINDING.json`: 18,000 leave-self-out records over 9,000
bell-bounded library games, sealed excluded. Its `v3_key_law` states in words what F-VS-202 demanded:
"Each vote looks up the V3 row by that library member's own bounded close cents; the runtime live bid
never selects a V3 cell."

**Votes non-empty, licenses real — sampled rows.** Trace census: `specialist_votes` non-empty on
3,388/3,388 derivations; `mind_window` splits SHAPE_FLOOR_TIMING_WINDOW 2,163 / OWN_EVIDENCE_TOUCH_WINDOW
1,225 (a genuine vote — the old wiring tied 0-0 on every row); `v3_map.licensed` TRUE 3,388/3,388 with
`lookup_basis: LIBRARY_MEMBER_BOUNDED_CLOSE_CENTS` — contamination zero (the bid-keyed map, F-VS-202) is
gone at the row plane, not just in law text. Sampled ln51 GIU: map votes carry per-member weights,
library closes, licensed floors, and source receipts (`…SHEVAN-VAN@minute_ts=1776576720` et al.);
`mapped_cell_q50 70 / mapped_floor_q50 64 / mapped_depth 6` — real numbers, distinct per row.

**The engine prices.** Authority target − live bid over the 3,014 PRICING_AUTHORITY_TARGET_EXECUTED
rows spans −10…+9; only 278 rows sit at bid+0. The old wiring was 481/481 at the bid. The F-VS-205
"engine unplugged" defect is repaired.

**Fills.** The trace, `FILL_HANDOFF_RECEIPT.json` (6 entries), and the stories all carry **six** fills.
The ordered "all seven fills" has no referent — no seventh fill exists anywhere in the package
(DAN never filled; PRA's 40 rest never filled). All six resolve in `fit-local/prints.jsonl` by trade id,
and entry == prior standing rest on every one (F-VS-107):

| leg | entry | trigger print | print ts | trade id | vs true floor |
|---|---|---|---|---|---|
| BAR | 27 | 27 | 1783841801.417 | 4fa381b8… | **floor exact** |
| GIU | 69 | 69 | 1783841972.759 | b113f8de… | +3 (floor 66) |
| URS | 58 | 57 | 1784032697.601 | a4575e0c… | +1 (floor 57; filled ON the floor print) |
| PAL | 40 | 40 | 1784041997.986 | 34d9e70c… | +1 (floor 39, printed 69 s later) |
| SVA | 41 | 41 | 1784020209.484 | 62c5acca… | **floor exact** |
| LAJ | 54 | 54 | 1784050973.062 | 16abd619… | +3 (floor 51) |

SVA's fill is lawful on the second 41 print: its 41 rest was established ts 1784020209, after the
governing first 41 print @1784020201.830 (which set efloor 41 and licensed the reprice).

Pairs: GIUBAR 96/Δ4 (req 7) · URSPAL 98/Δ2 (req 4) · LAJSVA 95/Δ5 (req 8) · DANPRA no entry.
The gate's only failing check is CURRENT_BED_TRIPWIRE, on exactly these three — my F-VS-188 ceilings,
now the spec, correctly catch the build.

**Determinism.** X2 replay byte-identical per game (GIUBAR sha 04f29297… both runs, 77,187,539 bytes;
gate DETERMINISM passes on all four).

**DANPRA rest-at-floor and the stamp — half-proven.** See §4: the LAWFUL_INCOMPLETE stamp stands on
DAN-only conduct, and the DANPRA story text contradicts the trace.

---

## 2 — THE PARITY REGRESSION: ln343's class survived. It is now licensed, inverted, and it fired four times.

**The exact step that moved URS off 57:** trace **ln1721, ts 1784031096 — REPRICE_REST 57→58**.
Row: bid 55, ask 59, mode PRICING_AUTHORITY_TARGET_EXECUTED, mind_window OWN_EVIDENCE_TOUCH_WINDOW,
`base_target 58 = evidenced_floor 58 = mapped_floor_q50 58`, `no_lane_may_replace_target: true`.
The machine had stood at 57 — the exact eventual floor — since 1784028247. Two 58 prints
(@1784028256.440) set the evidenced floor to 58; the engine consumed that floor as its target and
lifted the standing rest up onto it. 1,601 s later the 57 print (a4575e0c) arrived and filled the
58 rest at 58. Cost: 1¢, the tripwire's URSPAL cent.

**Is this ln343's class?** Yes — under a new name and the opposite sign. The class was never
"reprice down to the bid"; it is **the authority's own current reading outranking a standing rest that
sat at (or under) the true floor, protected by `no_lane_may_replace_target`**. At @71b179b3 the reading
was a bid-keyed map cell and the move was down (57→52, no fill). Here the reading is the evidenced
floor and the move is up (57→58, fill 1¢ worse). The build licenses it in the stories' own header:
*"lifts toward evidenced floors remain lawful."* The demoted-era hold family (the no-lift ratchet,
F-VS-205ii) would have refused this lift; the engine binding removed that refusal.

**The same step fired on four legs — the lift-to-evidence reprice:**

| leg | step | stood at | lifted to | on-row counter-evidence | outcome |
|---|---|---|---|---|---|
| URS | ln1721 ts 1784031096 | 57 (true floor) | 58 = efloor | its own stand | filled 58 on the 57 print. −1¢ |
| PAL | ln635 ts 1784024261 | (32) | 40 = efloor | **live bid 39 on the row** = true floor | filled 40, 69 s before the 39 print. −1¢ |
| LAJ | ln1788 ts 1784036642 | 53 (11,785 s) | 54 = efloor | **live bid 53 on the row** | filled 54; a 53 print came 1,857 s later. −1¢ |
| GIU | ln51 ts 1783841972 | 68 (7,868 s) | 69 = efloor (prints @1783841251, @1783841801) | **own map floor q50 64 on the row** | filled 69 at .759 s. −1¢ vs the stand |

GIU stood at 68 through three 69 prints unfilled, was lifted onto the printing level, and the next
69 print hit it. **Mechanism: every governing floor printed 1–3¢ below the prior evidenced floor, so a
rest placed AT current floor evidence systematically fills 1¢+ above the true floor.** The at-evidence
rest only wins when the evidenced floor already is the final floor — SVA (41) and BAR (27), the two
exact-floor fills. URSPAL's Δ4→Δ2 is precisely one lift per leg. A misnaming rides along:
OWN_EVIDENCE_TOUCH_WINDOW's target on ln1721 is the floor (58), not the touch (bid 55) — the F-VS-192
name-vs-conduct class on a window label.

---

## 3 — THE LAST CENTS, per leg, per cent (TWO-WAY STREET)

**GIU 69 vs floor 66 — 3¢.** At the lift row (ln51) the engine's own map floor q50 read **64**;
spread-eye read clearing 70, recorded not consumed; the machine's standing 68 was live and post-only
lawful under ask 70. Post-fill tape: 67 @1783867479.636, then 66 @1783869375.227 (+ two more 66s),
all inside the span.
- 69→68: **DATA-UNCONSUMED** — the machine held 68; the lift surrendered it with its own map floor
  (64) sitting on the same row. A held 68 fills at 68 on the 67 print.
- 68→67, 67→66: **DATA-GAP at the fill moment** (no sub-68 print yet existed), foreclosed by the
  voluntary lift — had the machine still stood, 67 was reachable by efloor-tracking after the 67
  print, and 66 by the same stand-1-under-evidence conduct it was already exhibiting at 68 vs 69.

**LAJ 54 vs floor 51 — 3¢.** At the lift row (ln1788): bid 53, efloor 54, map floor 55.
Post-fill tape: 53 @1784052830.356, then nothing between — no 52 print exists — then 51 @1784060123.219
(the floor print).
- 54→53: **DATA-UNCONSUMED** — the live bid 53 was on the lift row and the machine had stood at 53
  for 11,785 s; the lift surrendered a rest the tape validated 1,857 s after the fill.
- 53→52, 52→51: **DATA-GAP** — every sub-53 quantum of evidence postdates the fill; the machine's own
  apparatus read floor 55 (map) / 54 (efloor). The 51 evidence exists only at 1784060123.219.

**URS 58 vs floor 57 — 1¢: DATA-GAP by design.** Nothing was misread (efloor 58 was two real prints)
and nothing sat unconsumed (the target equalled the map floor and the efloor). The stand at 57 needed
**no data at all** — it existed; the design spent it. The 57-will-print fact entered the world only at
1784032697.601, as the very print that filled the lifted rest.

**PAL 40 vs floor 39 — 1¢: DATA-UNCONSUMED.** The live bid 39 — the true floor — was on the lift row
itself (ln635); the engine chose efloor 40 over touch 39. The 39 print arrived 69 s after the 40 fill.

**Where the machine stood, summarized:** 4 lifts, 4¢ realized above stands; 2 exact-floor fills where
evidence and floor coincided; spread-eye recorded-never-consumed throughout (SPREAD_EYE_RECORDED_NO_
AUTHORITY_LEVEL_CHANGE on the sampled decisive rows). Street totals across the three graded pairs:
DATA-UNCONSUMED 3¢ (GIU 1, LAJ 1, PAL 1) · DATA-GAP 5¢ (GIU 2, LAJ 2, URS 1) · MISREAD 0¢.
The bed deltas (7/4/8) were tape-real (F-VS-188 stands); this build banked Δ4/Δ2/Δ5 and left 8¢,
of which 3¢ had licensed evidence on the very rows that spent them.

---

## 4 — DANPRA: the proof is half-proven and mis-receipted; the story contradicts the trace

`LAWFUL_INCOMPLETE_RECEIPT.json` DANPRA row: floors 59+41 = 100 > 99, `strictly_under_par_offer 0`,
stamp LAWFUL_INCOMPLETE, `rest_at_floor_proven: true`, 17 rest_at_floor_rows. Verified against trace:

- **All 17 rows are DAN at 59.** DAN genuinely rested at its floor from ln1876 ts 1784347255
  (REPRICE 58→59, efloor 59, OWN_EVIDENCE_TOUCH_WINDOW) to cancel @1784373056. Real conduct proof.
- **PRA has zero rows and never rested at its floor 41.** It stood at 40 — one cent below — from
  ln1875 ts 1784341326 through the bell. A 40 rest can never fill (min print 41), so the abstention
  is real, but "rest at floor proven" is asserted for the pair on single-leg conduct.
- **13 of the 17 DAN rows cite PRA's book file** (`DANPRA-PRA.csv.gz#row-…` under `leg_id: DAN`) —
  a receipt/leg mismatch inside the proof rows.
- **The story contradicts the trace.** FOUR_STORIES.md (DANPRA): "The OS did not chase the displayed
  59/40 pair; it stood **51/33** at the bell, and neither rest filled." The trace: DAN rested **59**
  (17 receipted rows), PRA rested **40**. The same paragraph says "PRA: … PLACE_REST at 40¢" — the
  sentence is internally contradictory and matches the @71b179b3-era crown levels, not this build.
  The self-stop the commit message banks ("bank floor self-stop") is thus banked on a receipt whose
  conduct rows are half of the pair and whose story text describes a different machine.

The build's own parity tables (stories) self-report both regressions: URSPAL lineage 57+40 Δ3 vs
layered 58+40 Δ2; LAJSVA lineage 53+41 Δ6 vs layered 54+41 Δ5.

---

*Adversarial verification lanes (12) running; corrections, if any, will be filed as an addendum.*
