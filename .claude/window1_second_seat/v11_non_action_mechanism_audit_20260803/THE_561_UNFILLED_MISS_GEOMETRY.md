# THE 561 — miss geometry of every unfilled V41 leg

Analysis seat only. Read-only. V41 maker machine (`96d33316`). Every unfilled leg classified **exactly once** by how its lawful rest missed the flow. R\* = the rest's deepest lawful level (`resting_target_at_edge`, else join level, else bid−1); F = `union_reach` (deepest flow); nearest = |F − R\*|; a rest is *lawfully stood* from its join-arm time (else placement). Machine artifact: `…/THE_561_UNFILLED_MISS_GEOMETRY.json`.

## Population — the 561 reconciliation

Measured unfilled legs = **779** (779 = 343 naked empty sides + 218 skip games × 2). Of these only **4 are NEVER_PLACED** (admission-null) → **775 admitted-unfilled**. The operator's **561** assumed 218 admission-nulls; the ledger shows only 4 (`NEVER_PLACED_OR_CANCELLED`) — every skip leg was `RESTING_UNFILLED` (placed, never filled), so it is diagnosable, not admission-null. **All 779 are censused and classified exactly once** (the 4 admission-nulls as class e).

## The five miss classes — counts × nearest-miss cents

| class | legs | nearest-miss ¢ (total) |
|---|--:|--:|
| **(b) FLOW_ABOVE_REST — rest too deep** | 349 | 538 |
| **(c) FLOW_AT_REST_PRETRIGGER — trigger too late** | 172 | 119 |
| **(a) FLOW_BELOW_REST — rest too shallow/slow** | 94 | 66 |
| **(d) NO_FLOW_NEAR — dry / >3c off** | 160 | 2507 |
| **(e) NEVER_PLACED — admission-null** | 4 | 0 |
| **total** | **779** | — |

**615 of 779 misses are near-misses (≤3c) — a-c, genuinely fixable.** The story is not dryness: only 160 legs had no flow within 3c.

## Reading the geometry

- **(b) FLOW_ABOVE_REST dominates — 349 legs (45%).** The rest bid **1-3c too deep**; the ask dwelled just above it and never came the last cent down (total nearest-miss only 538¢ across 349 legs ≈ 1.5c each). **The law is systematically a shade too greedy on the bid** — the single biggest, cheapest-to-fix class.
- **(c) FLOW_AT_REST_PRETRIGGER — 172 legs (22%).** The flow hit the exact level but **before the rest lawfully stood** — the causality class the trigger frontier already flagged (an earlier, persistence-only arm would catch many).
- **(a) FLOW_BELOW_REST — 94 legs (12%).** Flow ran *under* a rest that walked down too slowly (law too slow).
- **(d) NO_FLOW_NEAR — 160 legs (21%).** Genuinely dry or the flow stayed >3c off (nearest-miss 2507¢ ≈ 16c each) — no law tweak reaches these.
- **(e) NEVER_PLACED — 4 legs.** No book / never armed.

## Per category (leg counts)

| class | ATP_CHALL | ATP_MAIN | WTA_CHALL | WTA_MAIN |
|---|--:|--:|--:|--:|
| Flow Above Rest | 185 | 34 | 78 | 52 |
| Flow At Rest Pretrigger | 96 | 27 | 23 | 26 |
| Flow Below Rest | 54 | 10 | 22 | 8 |
| No Flow Near | 56 | 27 | 51 | 26 |
| Never Placed | 2 | 2 | 0 | 0 |

FLOW_ABOVE_REST leads every category (ATP_CHALL 185, WTA_CHALL 78, WTA_MAIN 52, ATP_MAIN 34) — the too-deep bid is slate-wide.

## The 20 highest-value diagnosable games — by name (walkthrough queue)

Biggest under-par pair whose unfilled leg sits in a fixable class (a-c). *Value* = 100 − (partner + this-leg reach) — the locked cents a 1-3c law fix would have captured.

| value ¢ | game | type | class | unfilled leg (reach / rest / nearest) | partner |
|--:|---|---|---|---|--:|
| **58** | 26JUL13PENTHA | skip | a too-slow | THA (20 / 22 / 2) | 22 |
| **55** | 26JUL14KIRSEK | naked | c pre-trigger | KIR (28 / 30 / 2) | 17 |
| **49** | 26JUL18ZAKVAN | skip | b too-deep | VAN (50 / 49 / 1) | 1 |
| **46** | 26JUL13VANLEE | skip | a too-slow | VAN (53 / 54 / 1) | 1 |
| **37** | 26JUL12OFNTIR | naked | c pre-trigger | TIR (57 / 57 / 0) | 6 |
| **32** | 26JUL12ERJBOS | skip | c pre-trigger | BOS (17 / 19 / 2) | 51 |
| **21** | 26JUL14HRUBUY | skip | a too-slow | HRU (78 / 79 / 1) | 1 |
| **14** | 26JUL20AKSCOS | skip | a too-slow | COS (68 / 69 / 1) | 18 |
| **12** | 26JUL19BOHBOU | naked | a too-slow | BOU (83 / 86 / 3) | 5 |
| **10** | 26JUL19VANFAR | skip | c pre-trigger | FAR (54 / 55 / 1) | 36 |
| **9** | 26JUL13ROZISO | naked | b too-deep | ISO (28 / 27 / 1) | 63 |
| **9** | 26JUL19MCKOUA | skip | a too-slow | MCK (54 / 55 / 1) | 37 |
| **9** | 26JUL19WAWBUR | skip | c pre-trigger | BUR (62 / 65 / 3) | 29 |
| **8** | 26JUL12BARREI | skip | b too-deep | REI (31 / 28 / 3) | 61 |
| **8** | 26JUL13OUALIN | skip | c pre-trigger | LIN (17 / 18 / 1) | 75 |
| **8** | 26JUL19SINMAT | skip | b too-deep | SIN (31 / 28 / 3) | 61 |
| **8** | 26JUL19VUKGEA | skip | a too-slow | VUK (31 / 34 / 3) | 61 |
| **8** | 26JUL12HERKAZ | naked | b too-deep | HER (46 / 45 / 1) | 46 |
| **7** | 26JUL15SANERE | naked | b too-deep | SAN (43 / 42 / 1) | 50 |
| **7** | 26JUL19CASVAS | naked | b too-deep | CAS (39 / 38 / 1) | 54 |

**26JUL13PENTHA (58¢)** and **26JUL14KIRSEK (55¢)** lead: near-miss pairs left on the table by 2c. Most of the top-20 are **skip games where BOTH legs were 1-3c near-misses** — a small loosening of the bid (class b) or an earlier trigger (class c) converts them from skip to a deep-locked completion.

## Conservation

779 unfilled legs classified exactly once (True): FLOW_ABOVE_REST 349 + FLOW_AT_REST_PRETRIGGER 172 + FLOW_BELOW_REST 94 + NO_FLOW_NEAR 160 + NEVER_PLACED 4 = 779. Operator's 561/218-admission-null not reproduced (only 4 admission-null) — flagged. Source V41 MARKET 96d33316; R\*/F/timestamps from the leg ledger; nearest-miss = |union_reach − deepest lawful rest|.