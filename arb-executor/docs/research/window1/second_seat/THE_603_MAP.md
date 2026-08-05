# The 603 map — full-life, trading-phase close (canonical)  ·  `MODEL_FREE_CEILING`

Analysis seat only. Read-only. Print source = sealed re-pull (reconciliation 938dca47),
via `prints.jsonl` (full-life, 804/804). Machine artifact:
`.claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/THE_603_MAP.json`.
Canonical stamp: `TRADING_PHASE_CLOSE_BASIS`.

## Window law (ruled)

Full life = the exchange record span per market (first print/book → market close),
**804/804 by construction**. **Close = the final print of the *trading phase*** —
settlement collapse excluded: the terminal run into the decided band (≤10 loser / ≥90
winner) ending at an extreme (≤1/≥99) is dropped, and the close is the last **contested**
print (10 < price < 90) before that collapse. The whole analysis (traded-below, rest
levels, seller flow) is clipped to the trading phase.

The **settlement-value close** (raw final print) is stamped
**`DEGENERATE_SETTLEMENT_BASIS`** and retained only as a negative control: it floors
every loser leg at 1¢ → 758/804 structurally unreachable, 0 convertible (T1 40 / T2 763).

Prior guarded-window below-close counts (incl. the 340/390) stand stamped
**`WINDOW_TRUNCATION_ARTIFACT`**. Minutes the old guarded slice excluded: median **558**,
mean **713**, max **4,037** per game.

Trading-phase closes now sit in the contested band — winner legs ~70–89 (758), loser
legs ~11–30 (745) — not on the settlement floor.

## Tier census — full trading-phase life (conservation 804)

| tier | games |
|---|--:|
| **T1** both sides traded below own true close | **753** |
| **T2** one did, other did not (blocker named) | **48** |
| **T3** neither | **3** |
| **total** | **804** |

**T1-joint** (both below close AND sum < 100): **750**.

| category | T1-joint |
|---|--:|
| ATP_CHALL | 347 |
| WTA_MAIN | 145 |
| ATP_MAIN | 144 |
| WTA_CHALL | 114 |

Selected cat × region (T1-joint): ATP_CHALL 51_75/26_50 **123**, 26_50/51_75 **107**,
le25/ge76 53, ge76/le25 37 · ATP_MAIN 26_50/51_75 50, 51_75/26_50 48 · WTA_MAIN
26_50/51_75 40, 51_75/26_50 37, le25/ge76 24, ge76/le25 24 · WTA_CHALL 51_75/26_50 37,
26_50/51_75 35 (full grid in artifact).

## Presence-convertible mass

For the 51 non-T1 games (48 T2 + 3 T3), lawful rest levels come from decision-time
evidence (running traded-low band / qualifying-floor path, close-free). Seller-aggressed
flow landing 1c/2c/3c above a below-close rest converts the blocker.

**Convertible 1c / 2c / 3c = 1 / 1 / 1** (game FORHUA, ATP_CHALL). The mass is small not
because seller flow is absent but because **T1 already claims 750** — the blocker set is
only 51, and 47 of those are genuinely unreachable (the blocker's trading-phase low never
left room below its own close, or no seller flow approached it).

## The verdict — achievable joint

| conversion of T2/T3 (1c–3c) | achievable joint |
|---|--:|
| 0 % | 750 |
| 25 % / 50 % | 750 |
| 75 % / 100 % | **751** |
| — model-free ceiling (T1-joint + all convertible) | 751 |

**Against the 804 tape: 750 achievable joint on full trading-phase life; reachable-on-
tape 754; UNREACHABLE_ON_THIS_TAPE 50.** Against the operator's named **603** reachable
universe, the verdict clears it — the tape reaches **754**, and delivers **750** joint —
so 603 is a floor the full-life map exceeds, not a ceiling. What the market actually
offers, read on full trading-phase life, is **both legs below their own trading-phase
close in 750 of 804 games (93%)** — the true denominator every executable number
(R3 68, V32 41, no-chase 201) is a small fraction of.

## UNREACHABLE_ON_THIS_TAPE — 50

ATP_CHALL 18 · WTA_CHALL 22 · WTA_MAIN 7 · ATP_MAIN 3. Games where no seller flow ever
approached a below-close level on some side across the entire trading-phase life — the
irreducible residual. Conservation: 754 reachable + 50 unreachable = 804.

## Named rows

| game | trading-phase close | tier | joint? | note |
|---|---|---|---|---|
| **ARNROM** | ARN 11 · ROM 89 | T1 | yes | full life reveals ARN fell to 11 (from its guarded-slice 62) before collapsing to 1; both legs below close, joint |
| **LAJVAN** | LAJ 12 · VAN 89 | T1 | yes | both below trading-phase close |

(Both read as WINDOW_TRUNCATION_ARTIFACT joints at 94/95 on the old guarded slice; the
full-life trading-phase basis confirms the joint but re-prices the closes far lower.)

## Conservation

804 = 753 T1 + 48 T2 + 3 T3. Reachable 754 + unreachable 50 = 804. T1-joint 750;
achievable joint 750 → 751 at full conversion. Settlement-basis control (DEGENERATE):
T1 40 / T2 763 / T3 1, 764 unreachable, 0 convertible — on file, superseded.

*All figures `MODEL_FREE_CEILING`.*
