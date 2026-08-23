# DIVES T1 v3 — companion map complete; eight-game adjudication held for seed binding

## Binding

- Licensed analysis tip: `4d16922c`.
- Redundancy register: `165caa8a` / F-VS-094. The touch-vs-depth question stays adjudicated; this package does not reopen it.
- Source library: `CORPUS_INDEX.jsonl.gz` at `99233ab28f50be5a89fa1ddf96cf27ac3b36ce41`, SHA-256 `0c5aa898c29014fe97bec13ff0d81a2c323d87f739644e62fdc4df2428abf996`.
- Scope: measurement only. No policy replay, no 804, no sealed, no live.

## Re-derived cell-conditional depth map

The map keys each leg by `(category, own bounded-library close integer cell)` on the ratified `[5,95)` one-cent grid. `edge = close_cents - low_cents`. Only rows with a lawful bounded right edge are consumed. Type-7 quantiles retain their raw values; integer-cent fields round half up.

| category | bounded games | mapped legs | populated cells | out-of-grid legs |
|---|---:|---:|---:|---:|
| ATP_CHALL | 3,792 | 7,224 | 90 | 360 |
| ATP_MAIN | 2,596 | 4,896 | 90 | 296 |
| ITF_M | 95 | 155 | 77 | 35 |
| ITF_W | 89 | 158 | 74 | 20 |
| WTA_CHALL | 681 | 1,276 | 90 | 86 |
| WTA_MAIN | 2,444 | 4,619 | 90 | 269 |
| **total** | **9,697** | **18,328** | **511** | **1,066** |

The source contains 15,367 games. The 5,670 unbounded games are excluded. All 19,394 bounded legs conserve exactly to 18,328 mapped plus 1,066 out-of-grid; missing-price and negative-edge counts are both zero. Bell-method counts remain exposed in the JSON and per-cell rows rather than flattened.

Two clean generations are byte-identical. The receipt hashes are in `DETERMINISM_RECEIPT.json`.

## Section 2 and 3 hold

The original Tranche-1 v2 seed declaration is absent from every repository ref, attachment, and local task receipt available to this seat. `DIVE_QUEUE_V2.json` contains 642 ranked games but no eight-event seed. Choosing its first eight would be a new sampling law, so the sixteen adjudications were not fabricated.

Consequently these required outputs remain held:

- sixteen `KNOWABLE?` walk/capture-vs-ceiling adjudications;
- sixteen row-verified `TOUCH-SUFFICIENT?` adjudications against the five filed touch wins;
- sixteen `DEPTH-LICENSED?` citations to the corrected map or `UNMAPPED`;
- the evidence-based selection between chain-pressure and the three-way touch census.

The exact resume input is the original eight event IDs (or Tranche-1 v2 sections 1 and 4). `TRANCHE1_V2_BINDING_AUDIT.json` records the fail-loud boundary.
