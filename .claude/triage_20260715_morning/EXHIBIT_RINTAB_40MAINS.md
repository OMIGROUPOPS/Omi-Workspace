# EXHIBIT — RINTAB fill-by-fill exchange reconciliation + the 40-mains adjudication (C-MORNING-TRIAGE Part 1, 07-15)

## PRIOR ART (C45)
- ADJUDICATION_20260714 §EARLY-CHALL: "DEFECT: 40 mains legs pre-T-4h: [RINTAB-RIN, NEUPRA-NEU, NEUPRA-PRA, BUBHAL-BUB]" — the disk record this adjudication executes. Delta: the 4-name list is a `_ec_defect[:4]` render truncation (conviction_replay.py:859) — the true cohort is **40 placements across 17 tickers** (below).
- Maker/taker exchange-truth law (feedback_maker_taker_truth): fills judged by Kalshi /fills `is_taker`, applied throughout.

## 1. RINTAB (KXATPMATCH-26JUL14RINTAB-RIN) — fill-by-fill vs exchange
| # | exchange fill (Kalshi /fills) | our booking (log) | verdict |
|---|---|---|---|
| 1 | 07-14 05:43:29 AM buy 4@69 MAKER, order `a9d8be44`, fee $0.0150 | `entry_filled` qty=4 05:43:33 (+4s, fingerprint_readopt), exit 87×4 posted same second (order `1fe08df0`) | MATCH |
| 2 | 07-14 05:47:57 AM buy 1@69 MAKER, same order, fee $0.0038 | `entry_filled` +1 05:49:53 (+116s via active_partial_poll), exit reset 87×5 (order `c60d7013`) | MATCH (booking lag 116s, known poll path) |
| 3 | 07-15 04:17:54 AM sell 5@67 **TAKER**, order `b30b689b`, fee $0.0774 | `completion_action` verdict **flatten_kept** ev −3.75¢, same second: TAB 28¢ buy cancelled (completion_live_resolve) + RIN 87 exit cancelled + IOC sell 5@67 filled; `exit_filled` pnl −10¢ | MATCH |
**Reconciliation: 3/3 fills matched by order-id, price, and quantity. No daylight. Net leg: −10¢ + $0.096 fees.** Lineage notes: entry placed 01:16:24 AM 07-14 at 69 (repost of an orphan-cleaned 67 bid, trade T-20260714-0111); the pair never composed (TAB's 28¢ bid cancelled/reposted through the evening, drained at the 09:58 PM shutdown, re-placed, match_live-cancelled). The 4:17 AM taker flatten is one of the morning's 3-cap taker actions.

## 2. THE 40-MAINS ADJUDICATION (all 40 placements, exits confirmed)
The cohort = every `v4_place` with `min_before_start > 240` on ATP_MAIN/WTA_MAIN in the 07-14 log: **40 placements / 17 tickers / 9 events** (T−265min to T−719min; window stamps mix W1/W2 on lying evening clocks — several stamped W2 pre-start by early gun fires).

| ticker | placements | outcome | exit confirmed |
|---|---|---|---|
| RINTAB-RIN | 1 (69) | filled 5@69 → flattened 67 (−10¢) | YES — flatten cited above |
| NEUPRA-NEU | 1 (64) | filled 5@64 07-14 1:32 PM → exit 82×5 rested to settlement, settled LOSS −320¢ | YES — exit rested (order `dcaaa9be`), never reached |
| NEUPRA-PRA | 1 (33) | filled 5@33 → exit 40×5 FILLED +35¢ (07-14 1:53 PM) | YES — cashed |
| BUBHAL-BUB | 6 (65) | never filled | n/a (no fill) |
| BUBHAL-HAL | 3 (27–28) | filled 5@28 07-15 8:34 AM → exit 35×5 posted same second | YES — resting on exchange now |
| BASTIR-BAS | 2 (26–27) | filled 5@32 07-15 11:19 AM → exit 39×5 | YES — resting now |
| BASTIR-TIR | 3 (66→65) | buy 65×5 resting now (corridor-flagged in the grade) | open bid, no fill |
| CERKEC-CER / CERKEC-KEC | 2+2 (47/45) | never filled | n/a |
| RUBPEL-PEL / RUBPEL-RUB | 5+4 (22–23/64) | never filled; buys 27/71 resting now | open bids |
| TABMID-MID | 2 (22–23) | filled 5@24 07-15 10:32 AM → exit 31×5 | YES — resting now |
| TABMID-TAB | 3 (64–70) | never filled (corridor-flagged 64 bid 10:32 AM) | n/a |
| IBRBAD-IBR | 1 (12) | filled 5@14 07-15 6:38 AM → exit 19×5 | YES — resting now |
| IBRBAD-BAD | 1 (76) | never filled | n/a |
| OLIPRI-OLI | 2 (51) | never filled | n/a |
| SHEQUE-SHE | 1 (58) | filled 5@65 07-15 9:12 AM → exit 83×5 | YES — resting now |

**Adjudication: 8 of the 17 tickers filled; 8/8 filled legs have exits confirmed (5 resting on the exchange right now, 1 cashed +35¢, 1 flattened −10¢, 1 rested-to-settlement −320¢). Zero naked legs. The DEFECT stands as a placement-law violation (pre-T-4h mains placements against the EARLY-CANVAS-2 fence), not an exit-discipline failure.** Root queue: several placements sat T−9h to T−12h — beyond even the T−8h conception horizon on the schedule clock — the horizon's honest-anchor deferral vs these evening placements is the open question routed to the census (lying evening clocks on next-day mains).
