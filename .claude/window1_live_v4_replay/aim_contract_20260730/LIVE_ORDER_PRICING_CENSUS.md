# What actually prices a live Window-1 entry

Source of truth: the exact deployed `live_v4.py` bytes at VPS commit
`c40a8f9abc3d38792b82be049adefb95c3d64752`, SHA-256
`834b9e04e2cd1781b7f55fdcf80ed90555bd12341b6e98ec75ad4b06d77f1d54`.
The later local changes in this commit add retention and the two safe gates;
they do not alter the pricing census below.

## Bottom line

`recut_cells.json` does not price a live order. The normal live path proposes
an ATLAS price and the sealed authority may overwrite that price inside
`place_order`.

No active table was found explicitly keyed on the Window-1 close. The
close-keyed defect is in the guidebook/shadow bridge. That does **not** make
the active tables lawful: the two tables capable of signing the final order
are fitted and consumed on different or undocumented keys.

1. ATLAS was fitted with `discovery = first-hour median`, but live selects its
   page using the fresh price at the exact consultation.
2. The sealed pair table has no machine-readable fit-key contract. Live
   selects it using a band called from the leg's first observed/window-open
   price and then computes `open - depth_p90`.

Neither is the ratified `(category, fresh last-traded one-cent cell at exact
consultation timestamp)` forward surface. Sealed action is therefore held
off, and ATLAS is not recertified by this work.

## Price path in execution order

| Layer/table | What live keys it on | Observable at decision time? | Can it sign the final initial order now? | Contract finding |
|---|---|---:|---:|---|
| `entry_table_percell_conservative.csv` | category + one-cent cell of `_v4_entry_anchor` | Yes. The anchor is fresh last trade, or tight-book mid only when the fresh trade is outside the book. | No in normal PATH mode; it creates a preliminary target that ATLAS replaces. | CSV has no retained fit-key timestamp/source contract. |
| `per_regime_offsets_v2.csv` | category + regime of the same current anchor | Yes | No in normal PATH mode | Same provenance gap; broader fallback grain. |
| `aim_table.json` | category + coarse bucket of current anchor | Yes | Only upstream of the later PATH replacement | Absolute-cent bucket surface; not the ratified spread-relative surface. |
| `cohort_surface_v1.json` | category + retired fav/dog role + coarse current-anchor bucket | Anchor yes; fav/dog frame is retired | Only upstream of PATH; can still mutate the proposed offset and dossier | Retired key and no exact consultation-time fit contract. |
| `entry_tables_sealed_v1.json` | nearest `anchor_med` within category when cohort is thin | Current anchor yes; fitted row key undocumented | Upstream of PATH; can steer/refuse the cohort branch | Nearest-row lookup silently shares a band; no exact fit-key contract. |
| `range_final_<category>.csv` + walk schedule | current anchor cell + scheduled time-to-start | Yes, subject to schedule error | Upstream of PATH | Clock-triggered absolute-cent structure; not the lawful flow-state surface. |
| current BBO/depth governor | current bid/ask and bid ladder | Yes | Upstream of PATH | A live-book rule, not a fitted forward aim surface. |
| `ATLAS_V1.json` | category + leader/underdog + coarse band of current consultation price | Yes | **Yes: default final signer before the order chokepoint** | Fit key is first-hour median; consume key is exact current anchor. Key mismatch. Timing axis is old `-0k` onset and is now refused. |
| `pair_policies_sealed_v1.json` | live cascade `flat_flat` + band; price is cascade open minus `depth_p90` | The cascade open/band are observable | **Yes when enabled: overwrites ATLAS inside `place_order`** | No machine-readable fit-key contract; uses first-seen/window-open rather than exact consultation. Held off. |
| pair/headroom cap | booked sibling basis and policy goal | Yes | Constrains the proposal before posting | Derived guard, not a depth surface. |
| `completion_cells_v1.csv` | post-fill/window-open cell | Only after the first leg story exists | Can reprice the sibling later, not the initial aim | Lawful only as a separately named completion authority; cannot be an initial pre-entry cell key. |
| `GUIDEBOOK_V1.json` | shadow lookup | N/A | No; shadow is disabled | Its builder relabeled close-keyed recut depth as discovery-relative. The builder now rejects this bridge. |
| `recut_cells.json` / OS recut | shadow lookup | N/A | No | Shadow-only; it was the wrong object to audit as the live signer. |

## Where the final price is chosen

The live router:

1. obtains the consultation anchor in `_v4_entry_anchor`;
2. calculates several preliminary table/book targets;
3. replaces the proposal with
   `current_consultation_price - ATLAS depth_p50`;
4. applies pair/headroom and safety guards;
5. calls `place_order`;
6. if one-authority is enabled and the live cascade names `SEAL`,
   overwrites the proposed price with
   `cascade_open - sealed depth_p90`;
7. posts that value to Kalshi.

The one-authority implementation is still not structural. The overwrite
occurs after some price-sensitive guards, authority lookup errors fail open,
and the caller is not returned the authorized final price. The separate
one-authority census enumerates those paths.
