# The causal reach — the answer key re-cut to collectable flow

Analysis seat only. Read-only. The any-time union reach counts a level whenever union-channel evidence *ever* appears — including flow that arrived **before a lawful rest could stand there**. The **causal reach** counts a level only on CANON union-channel evidence (TRADED_AT_LEVEL any-trade + PRINT_CROSS seller-print + QUOTE_TOUCH ask-descent-dwell ≥10 s) timestamped **strictly after** its placement family's earliest lawful trigger:

- **tracking rest** → first two-sided book;
- **persistent-join** → the moment bid persistence ≥300 s **and** first seller-hit at the level both stand;
- **pulse floor** → the second ask-divot visit.

`causal_floor = min(deepest post-trigger trade, deepest post-trigger 10 s-dwelled ask)`. Machine artifacts: `…/CAUSAL_REACH.json`, `…/CAUSAL_LEG_TABLE.json`.

## The causal reach beside the any-time ceiling

| answer key | completable | under-par | locked ¢ | ≤93 / ≤95 / ≤97 / <100 |
|---|--:|--:|--:|---|
| **ANYTIME_CEILING** *(sealed union, telemetry only — no build graded on it again)* | 637 | **637** | **5253** | 120 / 183 / 345 / 637 |
| same-model, no trigger *(reproduces the ceiling — validates the model)* | 636 | 632 | 5228 | — |
| **CAUSAL REACH** | 536 | **504** | **3319** | 82 / 128 / 252 / 504 |

**133 under-par games and 1934¢ (≈37% of the ceiling) evaporate as uncollectable** — flow the sealed key counted but no lawful rest could have taken. The same-model-no-trigger row (632/5228¢) reproduces the sealed ceiling, so the drop is the **trigger**, not the fill model.

## Causal reach by category (under-par / locked ¢)

| category | under-par | locked ¢ |
|---|--:|--:|
| ATP_CHALL | 222 | 1070 |
| ATP_MAIN | 117 | 682 |
| WTA_CHALL | 68 | 1060 |
| WTA_MAIN | 97 | 507 |

## Where the flow is uncollectable — by placement family

| family | legs | depth lost on collectable ¢ | legs collecting **nothing** |
|---|--:|--:|--:|
| tracking | 864 | 8 | 0 |
| persistent_join | 203 | 120 | 4 |
| pulse_floor | 206 | 95 | 105 |

**Tracking (fallers) is causally clean** — its trigger (first two-sided book) is early, so ~all flow is post-trigger (depth lost 8¢, 0 legs empty). **The riser families pay the cost**: persistent-join loses 120¢ + 4 empty; **pulse-floor loses 95¢ and 105 of 206 legs collect nothing** — the second-divot-visit arms after the flow, or never (no 2-visit).

## Grading V36's actual 270 against the causal reach — the honest residual

Of V36's **270** completed pairs, 45 fall outside the V38 causal universe → **225 gradeable**. A V36 leg fill is *causally collectable* only if it is at or above the deepest post-trigger level (a fill deeper than any post-trigger flow relied on pre-trigger evidence).

| | pairs | locked ¢ |
|---|--:|--:|
| V36 completed (gradeable) | 225 | 670 |
| **survive the causal cut** | **90** | **156** |
| killed (uncollectable) | 135 | — |

**Only 90 of 225 V36 completions survive** (40%); locked collapses **670→156¢**. 148 legs were uncollectable, **layer-bound**: pulse-floor 62 · tracking 73 · persistent-join 13. V36's book leaned on flow that arrived before a lawful rest could stand.

## Named games

| game · leg | family | anytime reach | trade floor | quote floor | **causal reach** | reaches anytime? |
|---|---|--:|--:|--:|--:|:-:|
| ARNROM · ARN | persistent_join | 50 | 56 | 56 | **56** | NO |
| ARNROM · ROM | tracking | 38 | 38 | 38 | **38** | yes |
| ARNROM · combined | — | 88 | — | — | **94** | — |
| BOSCOP · BOS | tracking | 28 | 28 | 28 | **28** | yes |
| BOSCOP · COP | pulse_floor | 47 | 47 | 71 | **47** | yes |
| BOSCOP · combined | — | 75 | — | — | **75** | — |
| NIKVRB · NIK | pulse_floor | 18 | 18 | 18 | **18** | yes |
| NIKVRB · VRB | pulse_floor | 68 | 73 | 68 | **68** | yes |
| NIKVRB · combined | — | 86 | — | — | **86** | — |
| WESPAA · PAA | tracking | 38 | 38 | 38 | **38** | yes |
| WESPAA · WES | pulse_floor | 60 | None | None | **None** | NO |
| WESPAA · combined | — | 98 | — | — | **None** | — |

- **ARNROM · ARN** — persistent-join, anytime 50 → **causal 56**. The two trades at 50 (and any ask-dwell there) are **pre-trigger**: by the time the bid had persisted 300 s *and* been seller-hit, the deep-50 selling was done — after the arm the deepest flow is 56. Even the poster child causally loses its bottom. Combined 88 → **94** (barely under par).
- **BOSCOP · COP** — pulse-floor, **causally reachable at 47** via a lone post-arm **trade** (quote only reached 71). This **diverges from the stated expectation** (unreachable at 47): COP's bid never held 300 s at 47 on the fine tape, so it is pulse-family, and one trade at 47 lands after the second divot visit. Reported, not forced.
- **NIKVRB** — fully causally reachable, combined **86 = anytime 86**. QUOTE_TOUCH rescues **VRB to 68** (trade-only would stop at 73): the climber's ask dwelled ≥10 s at 68 post-trigger. The 3-channel CANON matters here.
- **WESPAA · WES** — **causally UNcompletable**: WES has no second ask-divot visit → the pulse floor never arms → trigger null → collects nothing; the pair (anytime 98) drops out entirely. PAA reaches 38, but a pair needs both.

## Conservation

637 games / 1274 legs. Families: tracking 865 · persistent-join 203 · pulse-floor 206. ANYTIME_CEILING 637/5253¢ (telemetry); same-model-no-trigger 632/5228¢ (validates model); **CAUSAL 504/3319¢**. V36 270 → 225 gradeable → 90 survive / 156¢. Sealed union 57daf3c1, V38 2c54d724, V36 bfde0d8, divot census d1ac9497. QUOTE_TOUCH + TRADED_AT_LEVEL + PRINT_CROSS, post-trigger.