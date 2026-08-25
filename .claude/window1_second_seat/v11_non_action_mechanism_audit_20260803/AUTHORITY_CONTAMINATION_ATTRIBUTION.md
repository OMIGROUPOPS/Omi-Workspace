# AUTHORITY CONTAMINATION ATTRIBUTION — @71b179b3

License: LAW_INDEX read this turn @ 71b179b3, sha256 `41784e6ab62d6341…` — verified against the order's `41784e6a…`. Laws: L8 L11 L18 L20 L22 · F-VS-200 (every function has a function) · TWO-WAY STREET F-VS-122 · DEFINITION LOCK · welds.
Seat: CC verification. Every number measured by me from the custodied trace (1,594 DECISION_STAGE / 2 FILL_EVENT / **3,016 leg-derivations / 10 orders**), the raw print store, the raw book tapes, and the code at 71b179b3. Governing floors: W1TT-C-001/002; LAJSVA and DANPRA base c0056976. Par 99; Δ = 100 − sum. Ceilings (F-VS-188, twice confirmed): GIUBAR 93/Δ7 · URSPAL 96/Δ4 · LAJSVA 92/Δ8 · DANPRA none.

## Headline

**The crowned brain is the bid-follower.** The restored pricing authority is the base V3-map/mind-window chain — the chain F-VS-196 catalogued as displaced telemetry — and its map is keyed by `CURRENT_CAUSAL_EVIDENCED_TOUCH_CENTS`: **the live bid**. Measured: **all 481 `PRICING_AUTHORITY_TARGET_EXECUTED` rows have `target == live_bid`; the spread eye — the added eye built to disprove stale bids — consumed 0 of 3,016 rows; all ten orders were placed at the bid.** Contract C01 then forbids every repaired lane from substituting a level. The result: **zero completions** (was three), two fills — one 2¢ *worse* than the demoted path (BAR entry 29 over a 27 floor) and one 1¢ better (LAJ 53, the F-VS-175 cent) — and **the DANPRA abstention proof destroyed**: the arithmetic (59+41=100, offer 0) is computed in the receipt and the stamp is withheld because the rests never stood at the floors.

Of the three §5 contaminations the order names, **two are moot at this tip by demotion** — the mid-derived ceiling and the 20¢ constant no longer price anything, because the entire dual chain they contaminated no longer prices anything. The build answered the contamination list by demoting the contaminated brain and crowning a different one — **whose own anchor is the original contamination of this series: the touch re-keying (`LIBRARY_CLOSE_CENTS → CURRENT_BEST_BID`), the collision the seat first filed as F-VS-165.**

---

## 1 — Verification

| claim | verdict |
|---|---|
| contracts registered | **CONFIRMED in form.** A frozen contract register exists in the OS (C01 `PRICING_AUTHORITY_OVER_LANE_LEVEL_SELECTION` · C06 `LANE_LANE_LEVEL_SELECTION` · C09 `PAR_CONSERVATION_OVER_PRICE` with resnap · C15 `SPREAD_EYE_IS_EVIDENCE_ONLY`, os:65-79 sampled), each with senior/junior/resolution — the F-VS-199 triage contracts written down. `TECHNIQUE_CONTRACT_REGISTER` passes on 3,016 |
| zero substitutions | **MEASURED TRUE, AND IT IS THE PROBLEM.** `base_target_cents == target_cents` on **481 of 481** authority rows — no lane substituted a level. The lanes that captured floors at be412a2f/4a96ded9 were contract-bound to write the authority's bid-anchored price |
| allocator deletion | **CONFIRMED for the allocator**: `allocatePairActions`/`rewriteAllocatedAction` are gone from functionable_os (0 hits). **NOT complete**: `supportingShapeIdsForLevel` (os:141) and `lineageTarget` (os:552) are still defined — consumption to be settled by the lanes |
| spread-eye inertness | **MEASURED: TOTAL.** `spread_eye_consumed: true` on **0 rows**. The one mechanism that could have moved an authority level off a stale bid (`staleQuotedBidDisproved`, os:263-271) never fired. Registered (C15, junior), inert in fact |
| the unstamped DANPRA proof | **THE PROOF WAS COMPUTED AND THE STAMP WITHHELD.** `LAWFUL_INCOMPLETE_RECEIPT.json` carries DANPRA's arithmetic — floors 59+41 = 100, `strictly_under_par_offer_cents: 0`, the exact F-VS-121 proof — and stamps `UNSTAMPED_INCOMPLETE`, because `rest_at_floor_rows: []`: the authority rested DAN at 53 and PRA at 37, never at the floors, so the abstention cannot be *proven by conduct*. The crown did not just miss fills; it un-proved the one lawful abstention |
| determinism | X2, `all_byte_identical: true`, label current |

## 2 — The price autopsy

### The chain, identified

`pricingAuthorityForLeg` (os:252-293):

```js
const baseTarget = cent(baseRow?.derivation?.derived_target_cents) ?? cent(baseRow?.action?.target_cents);
...
const target = staleQuotedBidDisproved ? clearingTarget : baseLawful ? baseTarget : null;
return { authority: "BASE_V3_MAP_JOINT_DEPTH_MIND_WINDOW_VOTE", ... no_lane_may_replace_target: true }
```

The authority's level is the **base chain's `derived_target_cents`** — touch pricing licensed by the V3 map (`lookup_basis: "CURRENT_CAUSAL_EVIDENCED_TOUCH_CENTS"`) and the joint depth license, voted by the mind-window. That is the chain retired from the decision path across seven builds and restored whole. Its anchor is the touch — the live bid — and the measurement is total: **481/481 authority targets equal the live bid; 0 spread-eye overrides; 10/10 orders at the bid.**

### The smoking row — URS, ln343

URS placed **57 — its exact eventual floor — at ln216** (first receipt of the span, bid 57). At **ln343, ts 1784024401**, the authority repriced it to **52**:

```
action: REPRICE_REST → 52, reason BASE_PRICING_AUTHORITY_EXECUTED_BY_LANE
pricing_authority.base_target_cents: 52 = live bid 52
v3_map.cell: { category ATP_CHALL, price_cell 52, edge_p50 7 }   ← the cell is LOOKED UP BY THE BID
evidenced_floor_cents on the same row: 64 (OBSERVED_TRUE_TRADE_PRINT)
```

The V3 map did not *decide* 52; **the bid selected which map cell was consulted.** The row's own tape-anchored fields read a running low of 64 with 57 printing later. This is F-VS-147's URSPAL regression in its third appearance — 57 abandoned for the bid 8,296 s before the 57 print — now protected by contract C01 against the lanes that fixed it twice.

### The three §5 contaminations, attributed at this tip

| contamination | status in the decision path @71b179b3 | contribution to the placed levels |
|---|---|---|
| **(2) mid-derived envelope ceiling** | **MOOT BY DEMOTION** — the envelope no longer prices; no coherent-lane order exists; `ENVELOPE_HIGH_PROVENANCE` (observed 5,376) labels the field in telemetry | **0¢ on all ten orders** — substitute (b), an evidenced ceiling, changes no placed level because no ceiling touched any placed level |
| **(3) the 20¢ lane constant** | **MOOT BY DEMOTION** — lane selection no longer prices (the authority prices; lanes execute); the constant survives at os:11 as evidence | **0¢ on all ten orders** — substitute (c), a derived bound, is structurally inert at this tip |
| **(1) the 14 hand-authored weights + evidence-match formula** | **LIVE** — they shape the neighborhood → specialist vote mass → the mind-window and the depth blend the authority consumes (`basis_weights`, `vote_mass` are on the authority object) | bounded per level by the lanes' substitute recomputation (addendum); **but on every one of the ten orders the weight-shaped depth was ultimately overridden by the anchor**: the executed level equals the bid, not the blend |
| **(0) THE ANCHOR THE ORDER'S LIST DOES NOT NAME** | the **V3 touch re-keying** — `${category}|${liveBid}` selects the cell; the bid is not an input to the level, it **is** the level | **the whole of all ten placements.** Substitutes (a)/(b)/(c) all leave the levels unchanged because none of the three touches the anchor |

**The attribution the order asks for, stated plainly:** the placed levels — GIUBAR 29/63, URSPAL 33/52, LAJSVA 53/36, DANPRA 53/37 — are **the live bids at their receipts**. With store-validated weights (a): unchanged. With an evidenced ceiling (b): unchanged. With a derived lane bound (c): unchanged. The contamination that priced this run predates the §5 list: it is the authority's anchor itself, and the correct substitute is the one the demoted path already implements — **the evidenced traded floor as the level source** — which captured PAL 39, SVA 41, PRA 41 and BAR 27 in the two prior builds.

## 3 — The comparison that decides: crown vs tape at each floor moment

Last derivation row at or before each governing floor moment; "demoted path" = the realized entries of the 4a96ded9/be412a2f lineage:

| leg | crown's level | tape floor | gap | tape fields on the same row | demoted path realized | cents vs demoted |
|---|---:|---:|---:|---|---:|---:|
| BAR | 29 → **filled 29** | 27 | **+2** | efloor null pre-print; floor printed 1783841801.305 | **27 captured** | **−2** |
| GIU | 63 | 66 | **−3** | `evidenced_floor 67` on the row | 67 filled | fill lost |
| PAL | 33 | 39 | **−6** | `evidenced_floor 40` on the row | **39 captured** | fill lost |
| URS | 52 (stood at 57, repriced off) | 57 | **−5** | `evidenced_floor 58` on the row | 58 filled | fill lost |
| LAJ | 53 → **filled 53** | 51 | +2 | `evidenced_floor 54`, base 53 = bid 53 | 54 filled | **+1** |
| SVA | 36 | 41 | **−5** | floor printed 1784020201.83 | **41 captured** | fill lost |
| DAN | 53 held **while the authority itself read 58** (base 58 = bid 58 at the floor instant) | 59 | −6 | `evidenced_floor 59` on the row | 58 rested (no fill possible) | proof lost |
| PRA | 37 | 41 | **−4** | `evidenced_floor 43` on the row | **41 captured** | fill lost |

**Attribution by input, per F-VS-122:** on GIU, PAL, URS, SVA, DAN and PRA the tape-anchored reading — `evidenced_floor_cents` with its print receipt — sat **on the same rows** the authority priced from. Nothing was missing: **MISREAD** on all six (the bid consumed as the level, under a contract forbidding correction), with URS the aggravated case (it *stood* on its floor and was moved off). BAR is **MISREAD** with a 2¢ realized cost (entry 29 against a captured 27 last build). LAJ is the crown's one genuine credit: **+1¢**, the exact cent F-VS-175 named — and even there the level equals the bid at the reprice row, so whether the authority *believed* 53 or *followed* 53 is settled by the same census as everything else: 481/481 at the bid.

**Score:** completions 3 → **0**; fills 7 → 2; the sole abstention proof un-proved; one cent gained on LAJ against two lost on BAR and every capturing leg's fill forgone. The mode census adds the last irony: `EVIDENCED_FLOOR_REST_HELD_CURRENT_SURVIVOR_SUPPORT` fires on **2,285 rows holding rests that are not at floors** — PAL at 33 for 1,166 rows, URS at 52 for 638, GIU at 63 for 174 — the F-VS-192 captured-rest class, now the dominant mode in the run, holding the bid-anchored levels *against* the authority's own later readings (DAN held 53 while the authority read 58 at its floor instant).

## Verdict

CERTIFIED: the contracts are registered and honored as written (zero substitutions, measured); the second allocator is deleted; determinism holds; the DANPRA arithmetic is honestly computed; the LAJ 53 capture is real and is the F-VS-175 cent.

FAULTED, decisively: **the restored authority is the bid-follower under a crown** — 481/481 targets at the live bid, ten of ten orders at the bid, the spread eye inert at 0 consumptions — and contract C01 converts every previously-repaired lane into its executor. The three §5 contaminations contribute nothing to the placed levels because two are moot by demotion and the third is overridden by the anchor; **the operative contamination is the V3 touch re-keying itself**, the oldest defect in this series, now senior to everything that was built to correct it. The floors were on the rows; the machine was forbidden to use them.
