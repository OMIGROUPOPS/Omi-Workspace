# THE COLLAPSE-CLASS SETTLEMENT AUDIT [ANALYTICAL_ESTIMATE]

Analysis seat only. Read-only. No re-scoring — counts and receipts; the operator rules the consequence.
Full rows: `COLLAPSE_CLASS_SETTLEMENT_AUDIT.csv` + `.json` (per-market resolutions verbatim, iceberg diffs,
settlement terms).

**Pins.** Population and crediting: the dev-804 ledgers @ `4716657a`
(`MARKET_EVENT_LEDGER_804` / `FOUR_STATE_EVENT_LEDGER_804` / `POST_ONSET_OFFER_CAPTURE_LEDGER_804`).
Tape: `OMI-Window1-private/fit-local/prints.jsonl`. Verification method: the iceberg diff @ `db470ec8`
(match by `trade_id`, price exact, size ≤0.011, ts ≤2 s, cursor-paginated past every W1 left edge).
Exchange: `GET api.elections.kalshi.com/trade-api/v2/markets/{ticker}`, `/markets/trades`,
`/series/{series}`, fetched 2026-08-13. Rulebook pointer: the series' `contract_url`
`https://assets.kalshi.com/regulatory/product-certifications/TENNISMATCH.pdf`
(sha256 `7d33c5b7eb4ad4099141f584f37fe9de3a7008461401c50a273b1269e7909e92`) — a templated generic
certification; the operative tennis settlement terms are the per-market `rules_primary`/`rules_secondary`
and the series `product_metadata`, quoted verbatim below.

## The class — 19 legs / 19 games

Definition: a dev-804 leg whose post-onset Window-1 tape (canonical `onset_sel` → `w1_right_epoch`)
prints ≤9¢ after having printed ≥50¢. Scan: 1,608 legs = 1,536 with post-onset in-window prints + 49
without a canonical onset (incl. the four legs of NO_TAPE `26JUL14MATMOR`/`26JUL18CORSAC`) + 23 with an
onset but zero in-window prints. **GUEGOM and SHEVAN both appear**, as required.

| game | cat | collapse leg | ① prints real? | ② resolution (verbatim `status`/`result`) | exam state | comb. | margin¢ | ③ pays as scored? |
|---|---|---|---|---|---|--:|--:|---|
| 26JUL12BASABB | WTA_CHALL | ABB (50→1¢, 81 pr) | 314/314 by trade_id | ABB `finalized`/`no` · BAS `finalized`/`yes` | COMPLETE | 98 | 2 | YES_PAYS_AS_SCORED |
| 26JUL12BROGIU | ATP_CHALL | GIU (82→1¢, 244 pr) | 2,791/2,791 | GIU `no` · BRO `yes` | COMPLETE | 99 | 1 | YES_PAYS_AS_SCORED |
| 26JUL12BUEMAR | ATP_MAIN | BUE (53→1¢, 61 pr) | 401/401 | BUE `no` · MAR `yes` | COMPLETE | 99 | 1 | YES_PAYS_AS_SCORED |
| 26JUL12DODDEL | ATP_CHALL | DOD (87→1¢, 535 pr) | 3,608/3,608 | DOD `no` · DEL `yes` | COMPLETE | 84 | 16 | YES_PAYS_AS_SCORED |
| 26JUL12GANJAN | ATP_CHALL | JAN (51→1¢, 177 pr) | 532/532 | JAN `no` · GAN `yes` | PARTIAL (JAN@38) | — | — | NO_MARGIN_SCORED |
| 26JUL12GUEGOM | ATP_MAIN | GUE (72→1¢, 268 pr) | 1,641/1,641 | GUE `no` · GOM `yes` | PARTIAL (GUE@58) | — | — | NO_MARGIN_SCORED |
| 26JUL12HESKOT | WTA_CHALL | HES (60→3¢, 89 pr) | 1,339/1,339 | HES `no` · KOT `yes` | COMPLETE | 99 | 1 | YES_PAYS_AS_SCORED |
| 26JUL12KULZAA | WTA_MAIN | ZAA (81→1¢, 169 pr) | 2,370/2,370 | ZAA `no` · KUL `yes` | COMPLETE | 97 | 3 | YES_PAYS_AS_SCORED |
| 26JUL12MICKUL | WTA_MAIN | KUL (82→1¢, 202 pr) | 1,309/1,309 | KUL `no` · MIC `yes` | COMPLETE | 91 | 9 | YES_PAYS_AS_SCORED |
| 26JUL12PALCOL | WTA_CHALL | PAL (86→1¢, 119 pr) | 904/904 | PAL `no` · COL `yes` | COMPLETE | 93 | 7 | YES_PAYS_AS_SCORED |
| 26JUL12PRASAI | ATP_MAIN | SAI (56→1¢, 175 pr) | 1,908/1,908 | SAI `no` · PRA `yes` | COMPLETE | 99 | 1 | YES_PAYS_AS_SCORED |
| 26JUL12RAFAGU | ATP_CHALL | **RAF (79→3¢, 688 pr)** | 3,405/3,405 | **RAF `yes`** · AGU `no` | COMPLETE | 88 | 12 | YES_PAYS_AS_SCORED |
| 26JUL12ROUGAN | ATP_CHALL | ROU (70→1¢, 601 pr) | 648/648 | ROU `no` · GAN `yes` | COMPLETE | 99 | 1 | YES_PAYS_AS_SCORED |
| 26JUL12SHEVAN | WTA_CHALL | **SHE (50→1¢, 439 pr)** | 1,290/1,290 | **SHE `yes`** · VAN `no` | COMPLETE | 92 | 8 | YES_PAYS_AS_SCORED |
| 26JUL12SKASAC | ATP_MAIN | SAC (64→1¢, 302 pr) | 952/952 | SAC `no` · SKA `yes` | COMPLETE | 99 | 1 | YES_PAYS_AS_SCORED |
| 26JUL12TABHUE | ATP_MAIN | HUE (62→1¢, 195 pr) | 978/978 | HUE `no` · TAB `yes` | COMPLETE | 94 | 6 | YES_PAYS_AS_SCORED |
| 26JUL12VILRAH | ATP_CHALL | RAH (66→1¢, 50 pr) | 729/729 | RAH `no` · VIL `yes` | COMPLETE | 84 | 16 | YES_PAYS_AS_SCORED |
| 26JUL20DJECIN | ATP_MAIN | CIN (75→9¢, 3 pr) | 124/124 | **CIN `finalized`/`scalar` @ `settlement_value_dollars` `0.3500` · DJE `scalar` @ `0.6500`**, `expiration_value` empty | COMPLETE | 92 | 8 | OTHER — scalar fair-price, 0.65+0.35 = **1.0000 exactly**; the pair's 8¢ pays in full |
| 26JUL20GALARN | ATP_CHALL | GAL (82→1¢, 358 pr) | 2,831/2,831 | GAL `no` · ARN `yes` | COMPLETE | 96 | 4 | YES_PAYS_AS_SCORED |

## ① Iceberg verdict — all real

28,074 of our post-onset in-window prints diffed against Kalshi's official public trade record across 46
pages (38,988 official trades fetched, spanning past every W1 left edge): **28,074 matched by `trade_id`
with exact price and in-tolerance size/time; 0 missing, 0 phantom, 0 field mismatches. All 4,756 collapse
prints (≤9¢) verified individually.** The violent collapses are real exchange trades, not capture artifacts.

## ② Resolutions histogram

- **18 games**: both legs `status=finalized`, complementary `result=yes`/`result=no` — exactly one winner
  per game, `expiration_value` = the winning player's name.
- **1 game (26JUL20DJECIN)**: both legs `status=finalized`, `result=scalar`, `expiration_value` empty —
  the pre-match-cancellation path: DJE settled at `0.6500`, CIN at `0.3500` (`settlement_ts`
  2026-07-21T00:44:59Z), **summing to 1.0000 exactly**.
- Collapse-leg resolutions: 16 `no` · **2 `yes` (RAF and SHE collapsed to single digits and then WON their
  matches — the collapse tape is not destiny)** · 1 `scalar`. Zero VOIDED, zero refunds, anywhere.

## ③ The money — 0¢ rests on non-paying resolutions

Exam-credited among the class: **17 COMPLETE_AT_DELTA pairs carrying 97¢ of locked margin — all 97¢ pay as
scored** (16 via complementary yes/no where the pair collects exactly 100¢; DJECIN's 8¢ via complementary
scalar settlement that also sums to 100¢). The 2 PARTIAL games credited one leg each (JAN@38¢, GUE@58¢ —
both resolved `no`; as one-sided positions they would have lost their entries, but the exam scores no margin
on partials, so no credited margin rests on them). **Cents of exam-credited margin resting on VOIDED or
otherwise non-paying resolutions: 0.**

## The rule the resolution data implies — Kalshi's own words

From the market objects (identical template across all four tennis series; GUE quoted):
`rules_primary`: *"If Andrea Guerrieri wins the Guerrieri vs Gomez professional tennis match in the 2026
ATP Umag Qualification Final **after a ball has been played**, then the market resolves to Yes."*
`rules_secondary`: *"If the match does not occur (signaled by a ball being played) due to a player injury,
walkover, forfeiture, or any other cancellation (all before the match starts), **the market will resolve to
a fair price in accordance with the rules**. If this match is postponed or delayed, the market will remain
open and close after the rescheduled match has finished (within two weeks)."*
Series `product_metadata.important_info` (KXATPMATCH-2026-04-09): *"If the match does not begin (signaled
by a ball being played), all markets, including set winner markets, will resolve to a **fair price** for
each player in accordance with the rules. If a player withdraws or forfeits after the match has begun, that
player will resolve to **No** for the main match market."* Settlement sources: ATP (atptour.com) / WTA
(wtatennis.com); regulatory certification at the `contract_url` pinned above.

**Implied rule, as observed:** pre-match withdrawal → **not a void** — a scalar fair-price settlement whose
per-leg values summed to exactly 100¢ in the one observed instance (DJECIN); in-match retirement → the
retiring side resolves `no` and the pair still pays 100¢. Under these terms a completed under-par pair's
margin survived every resolution mode that actually occurred in this class. The one-instance base for the
scalar-complement observation (n=1) is stated as such — whether "fair price" always sums to par is Kalshi's
discretion under the rules, not a proven invariant.

## Conservation

Class: 19 legs / 19 games (17 on Jul 12, 2 on Jul 20) out of 804 games / 1,608 legs (802 games
onset-bearing; 49 no-onset legs incl. MATMOR/CORSAC; 23 onset-bearing legs with zero in-window prints).
Iceberg: 28,074/28,074 matched, 4,756/4,756 collapse prints verified, 0 anomalies. Resolutions: 38 markets
= 36 yes/no + 2 scalar. Credited margin: 97¢ scored, 97¢ paying, 0¢ fictitious. No score, policy, or ledger
byte touched. ANALYTICAL_ESTIMATE.
