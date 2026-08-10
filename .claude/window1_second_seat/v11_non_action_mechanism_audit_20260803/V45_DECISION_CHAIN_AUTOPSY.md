# The decision-chain autopsy — V45, by where the buy-chain broke

Analysis seat only. Read-only. Every unfilled leg of the non-completed games under V45 (`3bda0a54`) diagnosed by **process, not outcome** — the earliest broken link in the buy-decision chain, assigned exactly once. **L1 ADMIT → L2 READ → L3 TARGET → L4 POST → L5 REPRICE → L6 STAND.** A misread counts as the break only when it **propagated** to a placement failure; a read that recovered downstream is scored at its true mechanical link. **This supersedes outcome-stamp classification — MARKET_NO is lawful only as an L6 verdict.** Machine artifact: `…/V45_DECISION_CHAIN_AUTOPSY.json`.

## The chain — counts × cents at stake

| link | legs | cents at stake |
|---|--:|--:|
| **L2 MISREAD** | 58 | 43 |
| **L3 NO_TARGET** | 4 | 0 |
| **L3 WRONG_LEVEL** | 11 | 1 |
| **L4 LATE_POST** | 47 | 45 |
| **L5 STALE_REPRICE** | 34 | 77 |
| **L6 NO_COUNTERPARTY** | 173 | 346 |
| **L6 OVERPAR** | 143 | 0 |
| **total** | **470** | — |

**Two-thirds of the residual is the market's no, not the machine's.** L6 verdicts total **316 legs (67%)** — the rest stood present and correct but **no counterparty came (173)** or **the pair never summed < 100 (143)**. The machine's own faults are the other **154 legs (33%)**.

## Among the machine's faults, the read is still the top breaker

- **L2 MISREAD — 58 legs — the top machine-side break**, ahead of L4 LATE_POST (47) and L5 STALE_REPRICE (34). The 157-mislabel organ is still the leading silent breaker of the machine's own misses.
- **But it is pervasive-and-self-correcting.** The raw read-organ rate is **232 of 366 comparable unfilled legs (63%)** read against the frozen path — yet only **58 propagated** to a lost fill; the other ~174 recovered (the rest still stood near the flow despite the wrong read). The misread is the most *common* deviation, not the most *costly*.
- **Direction bias**: the machine over-reads **FALLING** — read-vs-frozen FALLING_vs_RISING 64, FALLING_vs_SETTLED 52, RISING_vs_SETTLED 46 — climbers and flats mis-called as fallers.

- **L4 LATE_POST (47) / L5 STALE_REPRICE (34)**: the arming lag and the non-tracking rest — the causal-docket's "collectable" top games (LUZTSE, PANFAL, KHOZHA, KRASAL) land in **L5**: the machine posted a rest but it went stale as flow moved. **L3 (no/wrong target) is nearly empty (4 + 11)** — targeting is not the problem.

## Per category (leg counts)

| link | ATP_CHALL | ATP_MAIN | WTA_CHALL | WTA_MAIN |
|---|--:|--:|--:|--:|
| L2 MISREAD | 39 | 6 | 8 | 5 |
| L3 NO_TARGET | 2 | 2 | 0 | 0 |
| L3 WRONG_LEVEL | 7 | 0 | 3 | 1 |
| L4 LATE_POST | 27 | 5 | 7 | 8 |
| L5 STALE_REPRICE | 7 | 4 | 22 | 1 |
| L6 NO_COUNTERPARTY | 100 | 27 | 22 | 24 |
| L6 OVERPAR | 71 | 16 | 35 | 21 |

**WTA_CHALL is the STALE_REPRICE hotspot** (22 of 34) — its books move and the rest lags. L6 market-no dominates every category.

## SALIBR — the L6 verdict

SALIBR·IBR — the causal docket's #1 (48¢) — is **CHAIN_L6_PRESENT_BUT_NO_COUNTERPARTY**: the rest stood at 43¢, one cent under the 44¢ causal flow, present and correct; **the seller never crossed the last cent**. The machine did everything the chain asks. It is a market-no verdict, not a fixable miss — exactly the distinction the process view enforces.

## Top-5 exemplars per link — by name

| link | exemplars (value ¢) |
|---|---|
| **L2 MISREAD** | 26JUL19NIKVRB (8¢), 26JUL17HALSHE (6¢), 26JUL12MARFOR (5¢), 26JUL13POLMIY (4¢), 26JUL12CHAJON (3¢) |
| **L3 NO_TARGET** | 26JUL14MATMOR, 26JUL14MATMOR, 26JUL18CORSAC, 26JUL18CORSAC |
| **L3 WRONG_LEVEL** | 26JUL13KABPER (1¢), 26JUL12FANBIG (0¢), 26JUL12WESSEL (-1¢), 26JUL12MALTUR (-1¢), 26JUL19SINMAT (-3¢) |
| **L4 LATE_POST** | 26JUL14SURECH (13¢), 26JUL12BARREI (6¢), 26JUL12ROUJAK (5¢), 26JUL12KUZDE (4¢), 26JUL12BARVIS (3¢) |
| **L5 STALE_REPRICE** | 26JUL18LUZTSE (10¢), 26JUL13PANFAL (8¢), 26JUL13PANFAL (8¢), 26JUL13KRASAL (7¢), 26JUL13KHOZHA (7¢) |
| **L6 NO_COUNTERPARTY** | 26JUL14SALIBR (48¢), 26JUL12BROHUA (8¢), 26JUL12HERKAZ (7¢), 26JUL19COSAKS (7¢), 26JUL15HOLMAY (6¢) |
| **L6 OVERPAR** | 26JUL12CHISEA (0¢), 26JUL12CHOGAS (0¢), 26JUL12HOUJOR (0¢), 26JUL12KARMAR (0¢), 26JUL12MEJSOT (0¢) |

## Conservation

470 unfilled legs, each exactly one link (True): L2 58 + L3_NO_TARGET 4 + L3_WRONG_LEVEL 11 + L4 47 + L5 34 + L6_NO_COUNTERPARTY 173 + L6_OVERPAR 143 = 470. Machine faults 154 / market-no 316. L2 organ 232/366 pervasive, 58 propagated. Source V45 3bda0a54, causal reach d3db740f, frozen directions from the sealed reachability path, certified closes 57daf3c1.