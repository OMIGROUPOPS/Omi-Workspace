# Window‑1 quote reachability and causal OS re-score

## Plain-English result

Quote-touch expands the maker opportunity ceiling, but it does **not** explain
the OS's low completion count.

- Population: 804 games.
- Positive evaluator window: 693.
- Both legs measurable for the reachability ladder: 622.
- Print-only ceiling: 580 negative-combined-delta pairs; 340 with both legs
  below their own Window‑1 closes.
- Maker-union ceiling (true print **or** sustained opposite quote):
  - 10 seconds: 598 / 367.
  - 30 seconds: 598 / 365.
  - 60 seconds: 596 / 364.
  - 300 seconds: 593 / 359.
- Best unchanged-OS result was JOIN at 10 seconds: 86 completions, 23 negative
  combined delta, and 11 with both legs below their own closes.
- JOIN print-only was 82 / 20 / 10. The quote correction therefore adds only
  four completions, three negative-delta completions, and one both-legs-under-
  close completion.

The large gap is still order placement: at 10 seconds the tape supports 598
negative-delta maker pairs, while the best OS path realizes 23.

## Fill laws

All causal replays execute committed `live_v4` unchanged through the full
scheduler. Only the named entry-aim mode and replay fill law vary.

- `PRINT_ONLY`: a later true print at or through the resting limit.
- `QUOTE_OR_PRINT_DWELL_N`: a true print immediately, or the opposite best
  quote at or through the resting limit continuously for N seconds.
- If the OS posts into an already-crossing book, quote dwell starts at the
  order's post timestamp.
- No depth proof, quote-size proof, or five-contract gate is imposed.

The pre-existing paper evaluator was **not** print-only: it used true prints or
instantaneous opposite-BBO touch. The older instantaneous result file used
different committed `live_v4` bytes, so it is disclosed but not merged into
the same-OS matrix.

## Opportunity ceiling

`Negative` means negative combined delta to the two Window‑1 closes.
`Both<close` means each leg is individually below its own close.

| Reach law | Available | Negative | Both<close | Δ≤−2 | Δ≤−3 | Δ≤−5 | Δ≤−10 |
|---|---:|---:|---:|---:|---:|---:|---:|
| Print only | 622 | 580 | 340 | 477 | 362 | 177 | 34 |
| Quote only, 10s | 622 | 532 | 224 | 412 | 273 | 127 | 24 |
| Quote only, 30s | 622 | 531 | 217 | 405 | 268 | 123 | 24 |
| Quote only, 60s | 622 | 525 | 213 | 400 | 259 | 119 | 23 |
| Quote only, 300s | 622 | 503 | 193 | 379 | 245 | 113 | 18 |
| Print or quote, 10s | 622 | 598 | 367 | 508 | 390 | 193 | 38 |
| Print or quote, 30s | 622 | 598 | 365 | 506 | 389 | 193 | 38 |
| Print or quote, 60s | 622 | 596 | 364 | 502 | 384 | 191 | 38 |
| Print or quote, 300s | 622 | 593 | 359 | 498 | 383 | 191 | 38 |

The full ladders through Δ≤−20 and both-leg rungs through −10 are in
`WINDOW1_QUOTE_TOUCH_LADDERS.json`.

## Unchanged-OS outcomes

| Fill law | Aim path | Legs filled | Pairs | Negative | Both<close |
|---|---|---:|---:|---:|---:|
| Print | ATLAS | 213 | 47 | 1 | 1 |
| Print | Orientation | 213 | 47 | 1 | 1 |
| Print | JOIN | 586 | 82 | 20 | 10 |
| Print | Touch−1 | 272 | 56 | 2 | 1 |
| Print | One spread | 268 | 57 | 2 | 1 |
| 10s | ATLAS | 217 | 49 | 1 | 1 |
| 10s | Orientation | 217 | 49 | 1 | 1 |
| 10s | JOIN | 601 | 86 | 23 | 11 |
| 10s | Touch−1 | 274 | 57 | 3 | 2 |
| 10s | One spread | 270 | 58 | 3 | 2 |
| 30s | ATLAS | 217 | 49 | 1 | 1 |
| 30s | Orientation | 217 | 49 | 1 | 1 |
| 30s | JOIN | 599 | 85 | 23 | 11 |
| 30s | Touch−1 | 275 | 58 | 3 | 2 |
| 30s | One spread | 270 | 58 | 3 | 2 |
| 60s | ATLAS | 215 | 47 | 1 | 1 |
| 60s | Orientation | 215 | 47 | 1 | 1 |
| 60s | JOIN | 599 | 84 | 22 | 11 |
| 60s | Touch−1 | 274 | 57 | 3 | 2 |
| 60s | One spread | 270 | 58 | 3 | 2 |
| 300s | ATLAS | 214 | 47 | 1 | 1 |
| 300s | Orientation | 213 | 47 | 1 | 1 |
| 300s | JOIN | 595 | 83 | 21 | 10 |
| 300s | Touch−1 | 273 | 56 | 2 | 1 |
| 300s | One spread | 269 | 57 | 2 | 1 |

At 10 seconds, JOIN records 122 quote-dwell fills and 479 true-print fills.
That is only 15 more filled legs than print-only because many quote fills
replace fills that a later print would have produced. Orientation and ATLAS
are outcome-identical at every reported threshold.

## Quote down-and-resume census

There are 392,282 raw down-and-resume episodes across 629 events and 1,121
legs. Most are one-cent, sub-ten-second top-of-book oscillations. Sustained
episodes are much fewer:

| Side / leg direction | Dwell | Episodes | Legs | Median depth | P90 depth | Median T−scheduled |
|---|---:|---:|---:|---:|---:|---:|
| All | 10s | 23,556 | 1,088 | 1¢ | 2¢ | 260.2m |
| All | 30s | 13,088 | 1,072 | 1¢ | 2¢ | 187.1m |
| All | 60s | 8,589 | 1,055 | 1¢ | 2¢ | 114.1m |
| All | 300s | 5,309 | 973 | 1¢ | 2¢ | 94.3m |
| Ask, climbing | 10s | 4,571 | 384 | 1¢ | 1¢ | 259.3m |
| Ask, climbing | 30s | 2,839 | 380 | 1¢ | 2¢ | 225.3m |
| Ask, climbing | 60s | 1,702 | 373 | 1¢ | 2¢ | 149.1m |
| Ask, climbing | 300s | 1,065 | 344 | 1¢ | 2¢ | 147.0m |
| Ask, falling | 10s | 2,667 | 297 | 1¢ | 2¢ | 151.3m |
| Ask, falling | 30s | 1,852 | 292 | 1¢ | 3¢ | 127.5m |
| Ask, falling | 60s | 1,464 | 287 | 1¢ | 3¢ | 99.6m |
| Ask, falling | 300s | 895 | 265 | 1¢ | 3¢ | 84.9m |

The directional finding survives the population: climbing-leg ask troughs
arrive earlier than falling-leg ask troughs at every dwell threshold. It is a
tendency, not a universal schedule. The individual episode file includes bid
and ask, peak/trough/resume prices and timestamps, dwell, depth, repeat count,
direction, category, and T-minus cluster.

## Identity and completeness

- Comparable OS matrix: 20,100 rows =
  804 games × 5 aim paths × 5 requested fill laws.
- Additional current-bytes instantaneous-orientation diagnostic: 804 rows.
- Current committed `live_v4.py` SHA-256:
  `f6fb1d20f3943f7bac26d94ccf1e9d98a5f22762cd3357394adfc8a3b108d760`.
- Historical instantaneous baseline SHA-256:
  `25698d80642524c70f39d850ef0a7041edda6df9c4d2dbac0c666d58aab56a63`.
- The two identities are not merged.
- Quote reachability: 804 games, 1,608 leg rows.
- Divot census: 392,282 individual episode rows.
- Causal replay: 20,904/20,904 completed; zero worker error logs.
