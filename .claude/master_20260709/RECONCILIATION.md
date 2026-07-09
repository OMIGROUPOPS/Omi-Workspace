# NEVERWAKE RECONCILIATION — the +$502.59 vs exchange truth (2026-07-09 ~3:20 pm ET; raw in reconcile.json)

## THE ANCHORS, pulled and stated first (the operator's instruction — and the first finding)
- **No clean pre-Jul-8 anchor EXISTS.** `balance_snapshots.json` begins **2026-07-08 16:01:20Z** at **cash $757.26 + Kalshi mark $75.35 + PM $80.00 = $912.61** — the "first clean snapshot since Feb" (the Feb-rot era killed the ledger before that). **A Jul-2 start anchor is unreconstructable; the week-scale identity cannot be run to the cent BY CONSTRUCTION.** The identity below runs on the anchored window (Jul-8 12:01 pm ET → cut).
- Current live read (cut 1:18 pm): **cash $782.21 + mark $68.30 (34 open) + PM $80.00 = $930.51.**

## THE ONE SOLID LINE
**Total portfolio, anchored window: $912.61 → $930.51 = +$17.90 over ~25 hours** — snapshot vs live read, both exchange-truth, no convention needed. Everything finer-grained hits the findings below.

## THE IDENTITY ATTEMPT — and what it convicted
Line-by-line (fills API: buys $1,152.11 · sells-booked $763.17 · fill fees $0.52 · settlement fees $0.61; settlements API in-window):
1. **The settlements `revenue` field is DEAD — 0 on every record**; true costs live in `*_total_cost_dollars` (not the keys my earlier passes read). **Every prior "+$3.87 realized" line — the red-morning decomposition's realized number and the vocabulary entry's residue column — parsed ghosts and is RETRACTED as a dollar figure.** (The red-morning *conclusion* survives on snapshot evidence alone: cash fell ~$65 while total portfolio held flat → cash→inventory conversion is directly observable without settlement fields.)
2. **The sell-side cash booking is convention-ambiguous:** Kalshi books our yes-exits as `action=sell, side=no` with both sides' gross counts surviving to settlement (RODKUZ-KUZ: yes 5 + no 5, credit $5 at settle). Three parsings bracket the cash residual: **+$405.74** (dead-revenue parse) / **−$1,388.24** (full both-side credits + sells-as-proceeds) / **−$138.10** (sells-as-no-buys). **None closes to $1 — the residual is NAMED, not smoothed: the sell/no cash-timing convention is underdetermined by the API docs we hold.**
3. **QUEUED (the closure path): derive the convention EMPIRICALLY against the hourly balance snapshots** — they exist since Jul-8 16:01Z, so every future window closes to cents once the per-hour regression picks the convention. This is the reconciliation law's own missing tool, now specified.
4. **FEES ARE REAL: ~$144 of exchange fees on the week's fills** (order-of-magnitude; exact split pending the convention pass) — the jsonl `pnl_dollars` is fee-blind BY DOCUMENTED DESIGN (P0 #5), which alone invalidates cent-claims built on it.
5. Manual book: **$0.00 in the anchored window** (no fills, no settlements on non-bot tickers) — the manual line stays cleanly separate and empty.
6. Deploy-timeline footnote: one deploy inside the window (12:36 am, `d8d0c62f` — logging + config hygiene only, no trading-logic delta) — not a driver.

## THE +$502.59: RETRACTED AS AN ACCOUNTING NUMBER
It was built from jsonl computed pnl: **fee-blind (P0 #5), A54-fabricated basis on mold legs (~50% of week legs), and cross-checked against API fields now proven dead.** It stands ONLY as what it always was structurally: a **relative** two-column comparison (exit-cash vs F-bucket on the bot's own computed basis) — the exits-carry-the-week / rides-burn-it SHAPE is real; the dollar level is not certifiable without the convention pass + an anchor that doesn't exist.

## THE NEVER-WAKE RESTATE — does the floor ruling survive honest accounting? **DIRECTIONALLY YES; the $77/week does not.**
- **Parse-independent facts (counts, not dollars): stand.** Ride-rate 30% sub-floor vs 19% at 6k+ · **16 band-touched-no-buyer events sub-floor vs 5 at 6k+ on 2.2× legs** · 37% of sub-2.5k matches never wake (corpus).
- **The dollar gradient survives EVERY parsing:** under the exchange-credits parse, per-ticker realized margin = ITF_M sub-floor **+1.63** vs 6k+ **+3.08** (1.9×); ITF_W **+2.12** vs **+3.67** (1.7×) — same ordering as the jsonl-relative read (−$77 → +$42). **Sub-floor is the worst band in both ITF cats under both conventions.**
- **RESTATED RULING BASIS: the ITF ≥2.5k floor stands on (a) the never-wake structural third, (b) the unsweepable-exit concentration, (c) the ride-rate, and (d) a volume-monotone margin gradient robust to parsing — NOT on the retracted "$77/week" figure.** The absolute dollar value re-prices after the convention derivation; the ruling need not wait on it.
