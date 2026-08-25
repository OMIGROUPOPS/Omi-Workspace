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

---

# ADDENDUM — 12 lanes returned; my mechanism attribution corrected, the street table overturned

Filed as F-VS-211 … F-VS-214. Every lane ran with an adversarial verify pass; every number below
was recomputed by at least two independent seats from the trace, prints.jsonl, the raw book tapes,
and `git show d837b992:` code. Where the lanes refuted my first-push claims, the corrections are here.

## A — The mechanism is not floor-capture. It is `min(traded_low, ask−1)`, and the ask pulls the trigger.

My §2 read the lifts as the engine consuming the evidenced floor. The code and a 46-row controlled
experiment in the trace say otherwise (`window1_v54_functionable_os.js` @d837b992):

- `:741` — once a leg's own tape has ANY true print, the authority target IS the running observed
  traded low (`boundedTradeLow`); the map/votes/mind chain is consulted only before the first print.
- `:672` `postOnlyCap = liveAsk − 1` and `:778` `lawful = min(proposed, postOnlyCap)` — a price
  REDEFINITION (contradicting C03's own register text "NEVER_REDEFINE_THE_PRICE").
- `:801` — reprice whenever active ≠ derived. Symmetric; no rule keeps a deeper standing rest.

**URS ln1721 fired on the ask tick, not the floor.** Rows ln1675–1720 — 46 consecutive URS rows,
1784028269–1784030535 — all read `traded_low 58, proposed 58, cap 57 (ask 58), HOLD 57`. The floor
input had been 58 for 2,827 s and moved nothing. The single row where the ask reads 59 is the single
row with an order; and min(64, 58) = 58 shows the ask move alone sufficed. The 57 "stand" I credited
was itself clamp arithmetic — min(proposed 64, ask−1) — never a floor belief. Verified against the
raw book tape at both anchor rows (rows 3647 and 4294). Same identity on the other legs: GIU's 68
and LAJ's 53 were `min(traded_low, ask−1)` artifacts, and each lift is the clamp releasing on an ask
tick toward the running low. LAJ's endgame descent 56→55→54→53 was `min(pair_cap 58 = 99−41, ask−1)` —
LAJ's true-trade low was still 62 on one print; even my "efloor 54" framing at ln1784 was wrong about
what priced the row. **The mind-window prices nothing anywhere**: its uses are serialization
(`:750/:813/:814/:832`); `member_floor_fraction` feeds vote classification (`:555-562`) but no output
reaches a price. On URS, authority == ask−1 on 1,502/1,507 rows (99.7%); run-wide 1,626/3,014 (53.9%).
**The bid-collision of @71b179b3 became an ask-collision.** My §1 "the engine prices (target−bid
spans −10…+9)" therefore splits: the spread is mostly the clamp; the genuinely engine-priced orders
are the pre-first-print V3-rung ones — 54 of 320 price-bearing orders (63/528 with cancels).
And vote non-emptiness is structurally guaranteed (always exactly 7 = fixed retrieval k; 23,716 =
3,388×7) — what evidences the binding is record content (0/18,000 field mismatches against the
corpus formula) and the weight/behavior laws, which do verify. No corpus rebuild: FOUNDATION_LIBRARY
is blob-identical (928f3d1d) across all 18 v54 packages at both commits; the 18,000 eligible legs
existed at 71b179b3 — only the binding call was missing, exactly F-VS-205.

**ln343's class census, corrected upward: 18 reprices off levels that later filled** (URS 14, LAJ 2,
BAR 1, GIU 1). And the protection that should catch it is blind two layers deep: both the OS predicate
(`dual_belief_os.js:1351/:1361`) and the URS-specific guard (`build.js:2589-2592`) require the rest to
sit exactly AT the evidenced floor — a cap-clamped rest one cent below the floor being dragged up is
invisible to both, on every leg. On URS the `active == floor` conjunct was satisfiable only during the
final 26.7 minutes, after ln1721 — the guard could never have fired in time. The SAME_RECEIPT law's
lift disposition (`DENIED_DEEP_REST_LIFTED_TO_NEW_EVIDENCED_FLOOR`, :1056) never fired anywhere in the
run — all six SAME_RECEIPT rows took the hold branch; every lift was executed by `:741/:801`.

## B — The street table, re-attributed (corrects §3): MISREAD 5¢ · DATA-UNCONSUMED 2¢ · DATA-GAP 1¢

My first-push totals (UNCONSUMED 3 / GAP 5 / MISREAD 0) are dead. Per cent, lane-verified:

| leg | cents | street | why |
|---|---|---|---|
| GIU | 3 | **MISREAD ×3** | `:741` promoted the running traded low (set by the OPENING-HIGH prints 70/71) to the target the instant GIU first printed; 66 was producible from four consumed stores — one of three evidence-grade-1.0 voters licensed 66 (the trio's floors: 55/64/66), every consulted cell's p25–p50 band contained 66, the timing store put the floor at fraction 0.87–0.95 (true: 0.884 — accurate to ~13 min) while the machine paid at 0.238, and a delta-consuming pair cap (100−7−27) lands exactly 66. 66 never appears in any target field of any row; 66 was postable on 51/51 GIU rows. DATA-GAP: none. |
| URS | 1 | **MISREAD** | the ask−1 redefinition — the book side consumed as the level, the same family as old ln343's bid. Not my "DATA-GAP by design." The counterfactual 57 rest stands to the floor print and fills at 57 (no sub-58 print intervenes — verified). |
| LAJ | 1 | **MISREAD** | ln1788: the clamp released 53→54 on the ask tick; five ≤53 prints followed before the floor. |
| LAJ | 1 | **DATA-UNCONSUMED** | sub-52 vote floors (38/43/44; `deepest_supported_floor_cents 38`) sat on the rows while q50 aggregation emitted 43–59 — and the machine had already STOOD at a map-priced 52 for 3,449 s: ln1755 lifted 52→61 on the FIRST print (the 62-print), one receipt after SAME_RECEIPT held it — the single most expensive reprice in LAJ's life (a held 52 fills at 52 on the floor print → Δ7, one cent from spec). |
| LAJ | 1 | **DATA-GAP** | the exact level 51 appears in no consumed channel ever — candidate floor lattice jumps 50→54, post-formation q50 set {43,52,55,58,59}; a sub-51 rest misses the floor entirely (only exactly 51 captures 51). |
| PAL | 1 | **DATA-UNCONSUMED** | the authority's own pair-allocation machinery proposed PAL 39 (rejected_candidate_targets {PAL: 39, URS: 63}) through the churn, and the live bid 39 = the true floor sat on the lift row; `:741` took the traded low 40. |

BAR and SVA: 0¢ — and BAR's fill is the clean capture (its standing-license receipt IS the 27¢ floor
print @1783841801.3048, the W1TT-C-001 moment; fill 112 ms later). SVA is the chase that got lucky:
it witnessed the first 41 print resting 40 (SAME_RECEIPT hold), lifted to 41 seven seconds later, and
the second 41 print rescued it 0.484 s after that.

**The self-stop fired on exactly these cents.** SAFETY_FLOORS (7/4/8) has two post-hoc consumers —
the gate tripwire AND `self_stop_triggered` (build:1468/:1471; gate `self_stop: true, stop_reason:
CURRENT_BED_TRIPWIRE`) — while the placement path never reads it. The commit's own headline mechanism
halted the run over the 8¢ its pricing identity surrendered.

## C — DANPRA and the forfeited seventh (extends §4; two of my claims corrected)

- **The seventh fill was forfeited by contract.** PRA's floor 41 printed TWELVE times in-span (first
  at the truth floor moment, 1784342553.971). PRA was pinned at 40 from ln1875 (ts 1784341326). At
  ln1886 and ln1894 the engine's own authority target read **41** — `authority_target_divergence
  {authority 41, final 40, diverged: true, senior_authority_reason: C04_CANCEL_REARM_RESTORES_PRICE}` —
  the rearm contract restored the 40 over the engine's floor answer, and four 41¢ prints passed over
  the rest after the rearm burst (last in-span @1784372115.642). DAN reached its floor 59 only
  7,948 s (132.5 min) after its floor moment — every ≤59 print predates the tenure; the banked
  rest-at-floor tenure never coincided with a floor-priced print.
- **The run breached its span.** ln1893 @1784373056 (span_end + 896 s) cancelled both legs;
  ln1894 @1784373060 (+900 s) PLACED a new PRA rest at 40 — an order after the governing span end
  1784372160. Every DANPRA row carries `window_end_epoch 1784373060` (the bell) — the known
  bell-for-span_end error is inside the trace's own window_timing, inflating every DANPRA
  window_fraction the two-behavior specialists key on. The story renders the post-span placement
  as its final transition.
- **Correction to my §4:** the cross-file receipts on the 17 DAN rows are NOT a defect — decision
  stages are pair-level and either leg's book row lawfully triggers them (ONE_DECISION_PER_RECEIPT).
  Retracted. The real defects: the one-legged proof is PACKAGE-WIDE — all four LAWFUL_INCOMPLETE rows
  stamp `rest_at_floor_proven: true` on single-leg conduct (GIUBAR: 2 rows all BAR, GIU zero; URSPAL:
  400 all URS, PAL zero; LAJSVA: 1 SVA, LAJ zero; DANPRA: 17 DAN, PRA zero) — the field's definition
  is the defect, not the DANPRA instance. And "stood 51/33 at the bell" is a HARDCODED GENERATOR
  LITERAL — fixed template text at `build_window1_v54_dual_belief.js:1220`, F-VS-204's class, inside
  a story corpus that otherwise verifies 684/684 citations with zero mismatches.

## D — The thrash storm and the receipts that cannot see it

- **PAL: 400 orders — 194 same-price cancel→restore cycles over 4.95 h** (median inter-cancel 4 s,
  peak 19 in a sliding minute), driven by two contradictory lawfulness predicates: the atomic branch
  cancels 32 as outside the envelope [35,35] (os:1204-1209); the restore predicate re-places the same
  32 with NO envelope test (os:1257-1260). 190/194 cycles show identical state (active 32,
  authority-chosen 40). The churn ended at ln635 @1784024261 when the ask-tracking URS target reached
  59, making 40+59 = 99 lawful — 8,436 s BEFORE the URS fill. Total uncovered time across restored
  cycles: 1,624.8 s. Rearm attempts = decision-row sampling (355 attempts = 355 rows). F-VS-176's
  class at +71% (528 vs 309); GIUBAR alone (21 orders) is at the historical 22–23 scale.
- **The storm receipts cannot fire.** `ATOMIC_CANCEL_REPLACE_RECEIPT.json` claims
  `cancel_storm_disappeared: true` — its metric draws only consistency-flagged DANPRA rows
  (build:2465-2467) and reports `repaired_distinct_cancel_receipts: 0` while this run's DANPRA emitted
  8 real cancels and URSPAL manufactured a 194-cancel storm it never examines. `EVERY_CANCEL_REARMS`
  passes any status beginning `REARM_` — it verifies arming, not restoration; DAN's terminal cancel
  never resolved and passed.
- **Gate residue (F-VS-204's class, third generation):** two literals were genuinely repaired
  (`authority_restored` → vote_count > 0; `no_lane_may_replace_target` → derived), but
  `lane_level_replaced_authority` became a TAUTOLOGY — computed one line after
  `targets[legId] = authorityTarget ?? active` (os:989-991), false by construction, and consumed by
  the PRICING_AUTHORITY_RESTORED gate (build:2905). New self-agreeing check:
  `authority_target_divergence.licensed_senior` — the producer enumerates its own excuse and the
  checker consumes it (build:1535); 774 diverged rows, 774/774 licensed. And the run's self-grade
  contradicts its own gate: TRADE_REPORT_FOUR grades all three completed pairs
  `GOOD_COHERENT_UNDER_PAR_COMPLETION` while the same commit self-stops on exactly those pairs —
  a ZERO CONTRADICTIONS item (two internal rules wanting opposite things about the same run).
- **Story machinery:** the transition denominators are exact (19/508/46/32 reproduce from
  build:1188-1199 verbatim), but the renderer's mandatory-inclusion guarantee is dead on long games —
  `.slice(0, 8)` (build:1201-1211) discards the fill-handoff and terminal transitions it just marked
  mandatory; the URSPAL story renders 8/508 with zero of that game's 196 cancels and no fills.
  TRADE_REPORT_FOUR's six fill lines all mislabel their citation: the "trade:" field carries the
  licensing receipt, not the filling trade.
