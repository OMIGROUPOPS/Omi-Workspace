# V54 repair iteration 2 — Foundation + conditional dip + early riser

Status: **SELF-STOPPED; NOT ADOPTED.** This is a four-game repair receipt only. The 804, sealed, live, and deployment lanes were not opened.

## Build

- Foundation `per_minute_features.parquet` is materialized into a compact 9,000-game retrieval index. Every source row is clipped to its native `match_start_ts`; `match_start_method=unknown` and post-boundary rows are excluded.
- Foundation citations are `MINUTE` grain and licensed only for `MACRO`/`MICRO`. They never sign tick timing or `MICRO-MICRO`.
- The four descriptive `spike_perN` atlases enter as a pattern supplement; superseded exit maps are not consumed.
- The blanket anchor-relative low ratio and its lineage blend are deleted. Each leg conditions a q25/q50/q75 remaining-dip distribution on that leg's own bounded dip/no-dip evidence. The q50 center is stamped `PROVISIONAL_DESCRIPTIVE`; lineage is fallback only when no conditional distribution exists.
- Fill handoff and pair conservation are retained unchanged.

## Coverage

The prior diet had 698 bounded games and 11,811 games without a bounded path. The Foundation build has 9,697 bounded games and 5,670 without a bounded path in a 15,367-game union. The compact store was derived from 9,330,878 minute rows; 295,483 unknown-method and 1,777,297 post-boundary rows were excluded.

## Gate

| game | candidate | required floor | result |
|---|---:|---:|---|
| GIUBAR | 27 + 69 = 96, Δ4 | Δ7 | FAIL |
| URSPAL | 57 + 40 = 97, Δ3 | Δ3 | PASS |
| LAJSVA | LAJ 54 credited; SVA terminal rest 41 | complete, Δ6 | FAIL |
| DANPRA | PRA 43 credited; DAN terminal rest 56 | observation only | PARTIAL |

The measured law scan found zero violations. The safety gate stopped the lane; there was no behavioral edit after observing outcomes.

## Early-riser forensic

The original SVA 36¢ target was produced by a bounded-neighbor blanket dip ratio, not a null fallback. Later targets also carried an uncredited sibling standing commitment through the frozen conservation arithmetic. Under the replacement, the first post-formation Foundation target was 24¢ and later stages fell back through 37/39/41. The rule was lawful but missed SVA's early 41¢ window, so it is not accepted.

## Case study and reproducibility

LAJSVA Panels A/B/C, both trade reports, and the v1/v2/v3 spine are retained. The four-game package and the case-study render each reproduce byte-identically across two clean builds. All committed artifacts are under the 50 MB cap; the 406,637,058-byte Foundation source remains in external custody with hash and row-count binding.

VAULTED: Foundation repair iteration 2 is a failed candidate with preserved receipts; V54's prior operative lineage remains unchanged.
