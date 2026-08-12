# Tape vs exchange diff — the iceberg check [ANALYTICAL_ESTIMATE]

Analysis seat only. Read-only. Sizing only — no repairs, no re-scoring. Machine artifact with every per-leg
count and the full (empty) phantom list: `TAPE_VS_EXCHANGE_DIFF.json`.

## Method, exactly

**Endpoint:** `GET https://api.elections.kalshi.com/trade-api/v2/markets/trades?ticker=…&limit=1000&cursor=…`
— Kalshi's public market-data API, no auth, newest-first cursor pagination. **Coverage: full trade history is
served for settled July markets** — verified by paginating every ticker past its W1 left edge (282 pages
total; per-leg `pagination_complete` recorded; any incomplete pagination would have graded the game PARTIAL —
none did). So the STOP condition did not trigger.

**Match key:** our fit-local print rows carry Kalshi's `trade_id` verbatim (`source: kalshi_public_trade` on
every row in the population — one source value, raw capture; no derivation stage exists in the trade layer).
Diff = trade_id set comparison per leg over the frozen W1 span, plus field agreement on every match: price
exact, |size Δ| ≤ 0.011 (both sides fractional `count_fp`), |ts Δ| ≤ 2 s.

**Population (conservation):** ② the 19 OFFERED games with par ≤ 30¢ from `PAR_SHEET_804.csv` @ `b7f12d6f`
(count reconciles: 19 exactly) — which **contains ① all three tiny completes** (MERDRO par 12, JACDA par 12,
KIRSEK par 23; overlap reported, not double-counted) · ③ the other four exemplar games (POLKUH, ARSMAR,
SANDAN, PUTJEA @ `96168790`) · ④ 30 random games from the remaining 781, **seed 20260812**. Total 53 games,
106 legs.

## The verdict — no iceberg

| | count |
|---|--:|
| games | 53 — **REAL 53 · CONTAMINATED 0 · PARTIAL 0** |
| trades matched (trade_id + all fields agree) | **67,598** |
| in-Kalshi-missing-from-ours | **0** |
| phantom (in ours, absent from Kalshi) | **0** |
| field mismatches on matched ids | **0** |
| random-30 phantom rate | **0.0** (0 / 10,002 trades) |

**Our recorded tape's trade layer is Kalshi's official record, verbatim** — same ids, same prices, same
fractional sizes, same timestamps, across every deep-discount game, every exemplar, and a seeded random
cross-section of the corpus. The deep pairs are not artifacts of our pipeline.

**MERDRO's 6¢ prints, by name:** exactly one per leg —
MER `c6b0dd11-f7a3-5aad-4d5f-4aab58733c31` (size 26.56) and DRO `9ce4c803-dcc7-45e4-8a5b-36ec014a7f5a`
(size 57.21), both `true_print`, both present in Kalshi's official record with exact field agreement.
**Verdict: REAL.** The Δ88 pair was bought from trades the exchange itself attests.

## The depth confirmation line

`GET /markets/{ticker}/orderbook` takes **no time parameter** and returns only the *current* book (empty for
settled markets — verified on MERDRO-MER); candlestick history is OHLC/volume only. **Kalshi offers no
historical order-book depth. Our book recording is the sole source for standing-state and must be kept.**

## Conservation

53 games = 19 (⊃ 3 tiny) + 4 + 30; 106 legs, each with ours_n / kalshi_n / matched / phantom / missing in the
JSON; 67,598 + 0 + 0 partitions the union of both records over the frozen spans; phantom list empty; every
leg `pagination_complete: true`. ANALYTICAL_ESTIMATE (the diff ran outside the executable, against the live
public API on 2026-08-12).
