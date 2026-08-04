# Harvest rescore under the sealed gated-optima band authority

**CONDITIONAL ON RUNTIME AUDIT.** Codex owns the runtime-authority question. This
pass scores the harvest against the sealed gated-optima surface as instructed; it
does **not** adjudicate which surface the live runtime binds. If Codex's startup
receipts rule differently, the NEW (gated) columns here are the **counterfactual**
and the OLD (spike-map) columns stand. Analysis seat only, read-only, same 359
disjoint population and discipline as `V11_896_CARRY_CENTS.md`.

## Authority (cited, not litigated)

`BAND_AUTHORITY_RECEIPT.json` (commit e59aa4cc,
`…/naked_leg_disposition_v23_vs_a_20260804/`). Sealed surfaces:
`arb-executor/analysis/exit_charts/deploy_gated_optima_{full,WTA_MAIN,ATP_CHALL,WTA_CHALL}.csv`.
Working-tree CSVs **match the receipt's `git_blob_sha256` for all four**
(`checkout_sha256` differs by line-ending only — content identical).

- Lookup law: `CELL = CLAMP(ROUND(credited_entry_cents), 5, 94); X = CSV.X;
  TARGET = MIN(entry + X, 98)`.
- Touch law: **a true tape print at price ≥ TARGET, after fill, before the guarded
  right edge** (`arb-executor/audit/w1_grading.py`).
- **No HOLD cells** on this surface — all 359 held legs are banded (the spike-map
  surface had 32 HOLD cells, non-harvestable).

The credited entry = the held leg's `maker_floor` (its fill). The old spike-map
pass measured over the carry window `[fill, completion]`; the sealed law measures
`[fill, guarded_right_edge]`.

## Conservation

**31 OVERLAP + 359 DISJOINT = 390.** Every event in exactly one bucket
(`≤1h 106 · ≤2h 55 · ≤4h 86 · ≤8h 60 · >8h 52`). Denominator below is all **359**
(spike-map's 32 HOLD legs are non-harvest; gated has 0 HOLD).

## Old vs new harvest

| measure | harvests / 359 | rate |
|---|---:|---:|
| OLD spike-map, residency bid-touch (carry window) | 55 | 15.3% |
| OLD spike-map, print-backed (carry window) | 62 | 17.3% |
| **NEW gated-optima, band-touch — any true print (fill→right edge)** | **40** | **11.1%** |
| **NEW gated-optima, print-backed — buyer-aggressed (fill→right edge)** | **39** | **10.9%** |

**Under the sealed authority the harvest falls: print-backed 62 → 39 (−23),
band-touch 55 → 40 (−15).** Almost every gated touch is buyer-aggressed (40 vs 39).

### Why it falls — surface vs window, isolated

The sealed window is *broader* than the carry window, which alone would raise
touches — yet the count drops, because the gated exit bands are **higher** (larger
X → higher targets, harder to reach). Holding the window fixed:

- gated surface, same carry window: **30** print-backed (vs spike's 62) — the
  surface effect is **−32**;
- extending to the full fill→right-edge window: 30 → **39** — the window effect is
  **+9**;
- net **62 → 39**.

So the disagreement between the two surfaces is real and large, and it is a
*higher-band* disagreement, not a windowing artifact.

## Per carry-budget bucket

| bucket | n | OLD bid | OLD pb | NEW touch | NEW pb | Δpb | Δtouch |
|---|---:|---:|---:|---:|---:|---:|---:|
| ≤1h | 106 | 14 | 17 | 12 | 12 | −5 | −2 |
| ≤2h | 55 | 7 | 8 | 7 | 7 | −1 | 0 |
| ≤4h | 86 | 10 | 12 | 6 | 5 | −7 | −4 |
| ≤8h | 60 | 9 | 9 | 8 | 8 | −1 | −1 |
| >8h | 52 | 15 | 16 | 7 | 7 | −9 | −8 |
| **ALL** | **359** | **55** | **62** | **40** | **39** | **−23** | **−15** |

## Per category

| category | n | OLD bid | OLD pb | NEW touch | NEW pb | Δpb |
|---|---:|---:|---:|---:|---:|---:|
| ATP_CHALL | 167 | 19 | 23 | 20 | 20 | −3 |
| ATP_MAIN | 89 | 20 | 22 | 7 | 7 | **−15** |
| WTA_MAIN | 68 | 7 | 7 | 4 | 3 | −4 |
| WTA_CHALL | 35 | 9 | 10 | 9 | 9 | −1 |

The drop is concentrated in **ATP_MAIN** (22 → 7): its sealed exit bands sit far
above the spike-map bands, so most held-leg carries never reach the sealed target.
ATP_CHALL and WTA_CHALL are nearly unchanged — the two surfaces largely agree there.

## Reading (conditional)

If the runtime binds the sealed gated-optima surface, the harvest side of the
disjoint carry is **thinner than the spike-map pass reported** — ~11% of held legs
reach their sealed exit band before the window closes, vs ~17% under spike-map,
the gap driven almost entirely by ATP_MAIN's higher bands. The favorable-drift
carry finding (V11_896_CARRY_CENTS) is unchanged — that is a mid-drift fact,
independent of the exit surface — but fewer of those drifts clear the sealed band.
Which surface the runtime actually uses is Codex's receipt to sign; until then
these NEW columns are the counterfactual against the standing spike-map OLD ones.

## Artifacts

`GATED_HARVEST_EVENTS.csv` (per event: entry, gated cell/X/target, old vs new
touch/print-backed) and `GATED_HARVEST_SUMMARY.json`.
