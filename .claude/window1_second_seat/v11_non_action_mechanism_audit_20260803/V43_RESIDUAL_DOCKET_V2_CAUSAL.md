# Docket v2 — the causal re-cut

Analysis seat only. Read-only. **Supersedes the v1 docket** (`6934634e`), which ranked by *anytime* reach and so credited flow no lawful rest could collect. Here every uncompleted game of **V45** (`3bda0a54`) is re-ranked by **causally-collectable value**: `100 − Σ(each leg's causal fill-or-reach)`, where causal reach = `reach_snapshot.causal_own_reach_low_cents` — union-channel flow **strictly after the leg's lawful rest could stand** (`d3db740f` machinery), in-window. Games with **zero causal reach on the missing side** are stamped **MARKET_NO**. Machine artifact: `…/V43_RESIDUAL_DOCKET_V2_CAUSAL.json`; packs under `exemplar_packs/v45_docket/`.

## Population

**408 uncompleted** = **155 with causal value > 0** + **93 MARKET_NO** (missing side has no post-trigger flow) + 160 causally-over-par. **253 of 408 are the market's no** under the causal lens — the flow was there anytime, but not after a lawful rest could stand.

## The v1 prizes collapse

The v1 top-5 headline values were **pre-trigger mirages**. Under the causal cut:

| game | v1 (anytime) | v2 (causal) | why |
|---|--:|--:|---|
| **LUZTSE** | 88¢ | **10¢** | TSE's 1¢ trade was pre-trigger; causal reach 79¢ (LUZ 11 + TSE 79 = 90) |
| **COLCER** | 61¢ | **MARKET_NO** | COL's deep flow entirely pre-trigger — no post-rest reach |
| **SMIYUN** | 48¢ | **MARKET_NO** | YUN's flow pre-trigger |
| **VANLEE** | 44¢ | **MARKET_NO** | LEE's flow pre-trigger |

The V45 executable proved exactly this: those rests could never have stood where the flow was.

## Top 15 by causally-collectable value

| # | causal ¢ | game | type | cat | miss story |
|--:|--:|---|---|---|---|
| 1 | **48** | 26JUL14SALIBR | naked | WTA_MAIN | IBR: rest 43c, causal reach 44c |
| 2 | **10** | 26JUL18LUZTSE | naked | ATP_MAIN | TSE: rest 79c, causal reach 79c (anytime 1 was pre-trigger) |
| 3 | **8** | 26JUL12BROHUA | naked | ATP_CHALL | BRO: rest 62c, causal reach 64c (anytime 63 was pre-trigger) |
| 4 | **8** | 26JUL13PANFAL | skip | WTA_CHALL | FAL: rest 44c, causal reach 47c (anytime 30 was pre-trigger); PAN: rest 54c, causal reach 45c (anytime 1 was pre-trigger) |
| 5 | **7** | 26JUL13KRASAL | naked | ATP_CHALL | KRA: rest 78c, causal reach 79c (anytime 43 was pre-trigger) |
| 6 | **7** | 26JUL13KHOZHA | naked | WTA_CHALL | KHO: rest 77c, causal reach 78c (anytime 6 was pre-trigger) |
| 7 | **7** | 26JUL12HERKAZ | naked | WTA_MAIN | HER: rest 45c, causal reach 47c (anytime 46 was pre-trigger) |
| 8 | **7** | 26JUL19COSAKS | naked | WTA_MAIN | COS: rest 63c, causal reach 59c |
| 9 | **6** | 26JUL15HOLMAY | naked | ATP_CHALL | MAY: rest 34c, causal reach 29c |
| 10 | **6** | 26JUL19DEMMAG | naked | ATP_CHALL | MAG: rest 93c, causal reach 88c |
| 11 | **6** | 26JUL18ROCBUE | naked | ATP_MAIN | BUE: rest 78c, causal reach 73c |
| 12 | **5** | 26JUL14IVAGIU | naked | ATP_CHALL | GIU: rest 41c, causal reach 42c |
| 13 | **5** | 26JUL14MRVCAN | naked | ATP_CHALL | MRV: rest 54c, causal reach 55c (anytime 54 was pre-trigger) |
| 14 | **5** | 26JUL19BARSTA | naked | ATP_CHALL | STA: rest 62c, causal reach 59c |
| 15 | **5** | 26JUL19JONISO | naked | ATP_CHALL | ISO: rest 56c, causal reach 52c |

## Reading the causal docket

- **SALIBR (48¢) is the only substantial causally-collectable game left** — and it is a genuine **FLOW_ABOVE 1¢ near-miss** (IBR causal reach 44¢, rest 43¢), reachable by a further +1¢ loosen, not a mirage. It topped the v1 list too and survives the cut intact.
- **Everything below it is ≤ 10¢ scraps.** The residual opportunity in V45 is essentially exhausted: once flow that preceded a lawful rest is removed, 253 of 408 uncompleted games are the market's no, and the collectable remainder is a long tail of single-digit cents.
- The recurring pattern in the top 15 is **causal reach ≈ rest + 1-2¢** with a much deeper **anytime reach flagged pre-trigger** — the deep prints existed but arrived before the join/track could lawfully occupy the level.

## Top-5 causal walkthrough packs

`DUAL_TIMELINE_V2.csv` + `DECISION_MARKS.json` (with anytime vs causal reach) under `exemplar_packs/v45_docket/` for the five highest causal-value games:

| # | game | causal ¢ | the miss |
|--:|---|--:|---|
| 1 | **26JUL14SALIBR** | 48 | IBR: rest 43c, causal reach 44c |
| 2 | **26JUL18LUZTSE** | 10 | TSE: rest 79c, causal reach 79c (anytime 1 was pre-trigger) |
| 3 | **26JUL12BROHUA** | 8 | BRO: rest 62c, causal reach 64c (anytime 63 was pre-trigger) |
| 4 | **26JUL13PANFAL** | 8 | FAL: rest 44c, causal reach 47c (anytime 30 was pre-trigger); PAN: rest 54c, causal reach 45c (anytime 1 was pre-trigger) |
| 5 | **26JUL13KRASAL** | 7 | KRA: rest 78c, causal reach 79c (anytime 43 was pre-trigger) |

## Conservation

408 uncompleted = 155 causal-value>0 + 93 MARKET_NO + 160 over-par (check 408). Top 15 named; top 5 packed. Supersedes v1 docket 6934634e. Source V45 3bda0a54, causal machinery d3db740f, certified closes 57daf3c1, fit-local tapes.