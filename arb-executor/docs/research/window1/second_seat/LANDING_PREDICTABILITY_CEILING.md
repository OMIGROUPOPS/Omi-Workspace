# Landing predictability ceiling — model-free, all 1,608 legs

Analysis seat only. Descriptive. Read-only from raw tapes and the independent
audited closes (`INDEPENDENT_CLOSE_AUDIT_1608.csv`, commit 50ce0f49). **No access
to any fitted estimator or its artifacts — the isolation is the point.** Per-leg
rows in `LANDING_PREDICTABILITY_LEGS.csv`; grids in
`LANDING_PREDICTABILITY_SUMMARY.json`.

## Method

For each leg, the **read-moment** is its first qualifying floor on its own raw tape
— the first row where the ask sits at the running-minimum ask, has dwelled ≥10s at
that price, and shows top size ≥5. Using the qualifying-floor read-moment uniformly
(the stated fallback) keeps the pass fully tape-derived and isolated from any
pair-resolution pipeline. Only information observable at that instant on that leg's
own tape is used — no future rows. Three naive causal predictors of the audited
close, scored by signed error `predictor − close`:

- **(a)** current mid at read-moment
- **(b)** lowest qualifying ask so far (the floor price itself)
- **(c)** last true print so far (carried last trade)

## Conservation and coverage

**1,608 = 1,512 covered + 96 uncovered** (sum check 1608 = 1608). Uncovered: 82
legs never formed a qualifying floor (no read-moment — dead/thin book), 51 have no
in-window audited close; the two sets overlap to a union of 96. Coverage 94.0%.

## Overall (1,512 covered legs)

| predictor | MAE | bias |
|---|---:|---:|
| **(a) current mid** | **4.89** | −0.59 |
| (b) lowest qualifying ask | 5.35 | +1.35 |
| (c) last true print | 9.62 | −5.66 |

Mid is the best naive predictor and nearly unbiased. The last true print is badly
biased (−5.66): at the read-moment the last trade sits ~5.7¢ **below** where the
leg closes — the price rises from the last print to the landing far more often
than not.

## Per category × price region — the ceiling

`ceiling = best-of-three MAE` per cell = the floor a fitted estimator must beat to
be worth wiring. `drift = mean(close − mid)`; `dir` = share of legs drifting the
majority direction.

| cell | n | MAE a | MAE b | MAE c | **ceiling** | best | drift | dir | flag |
|---|---:|---:|---:|---:|---:|:--:|---:|---:|---|
| WTA_MAIN ge76 | 44 | 1.39 | 1.11 | 1.34 | **1.11** | b | +0.68 | 0.80 | SMALL_KNOWN |
| WTA_MAIN le25 | 59 | 1.60 | 1.49 | 1.86 | **1.49** | b | −0.23 | 0.53 | SMALL_KNOWN |
| ATP_MAIN le25 | 33 | 3.35 | 3.36 | 2.79 | 2.79 | c | +1.23 | 0.55 | HARD_NOISY |
| ATP_CHALL ge76 | 97 | 3.60 | 2.88 | 16.44 | 2.88 | b | +1.28 | 0.74 | HARD_NOISY |
| **WTA_MAIN 51_75** | 83 | 3.56 | 3.10 | 3.84 | **3.10** | b | **+2.58** | 0.78 | **HARD_EXPLOITABLE** |
| WTA_MAIN 26_50 | 84 | 3.33 | 3.31 | 5.80 | 3.31 | b | −1.26 | 0.50 | HARD_NOISY |
| ATP_MAIN 26_50 | 108 | 3.72 | 4.40 | 5.16 | 3.72 | a | −1.38 | 0.51 | HARD_NOISY |
| ATP_CHALL 26_50 | 251 | 3.94 | 5.87 | 11.02 | 3.94 | a | −0.41 | 0.54 | HARD_NOISY |
| **ATP_CHALL 51_75** | 245 | 4.13 | 4.19 | 13.38 | **4.13** | a | **+2.14** | 0.72 | **HARD_EXPLOITABLE** |
| ATP_CHALL le25 | 114 | 4.37 | 6.90 | 6.01 | 4.37 | a | −1.07 | 0.55 | HARD_NOISY |
| **ATP_MAIN 51_75** | 104 | 4.86 | 4.88 | 7.54 | **4.86** | a | **+2.72** | 0.66 | **HARD_EXPLOITABLE** |
| ATP_MAIN ge76 | 26 | 5.52 | 5.35 | 5.31 | 5.31 | c | +0.60 | 0.62 | HARD_NOISY |
| **WTA_CHALL ge76** | 42 | 8.92 | 7.17 | 11.50 | **7.17** | b | **+2.99** | 0.76 | **HARD_EXPLOITABLE** |
| WTA_CHALL le25 | 44 | 8.00 | 9.48 | 8.41 | 8.00 | a | −1.82 | 0.59 | HARD_NOISY |
| **WTA_CHALL 51_75** | 84 | 9.20 | 8.85 | 14.21 | **8.85** | b | **+3.29** | 0.79 | **HARD_EXPLOITABLE** |
| WTA_CHALL 26_50 | 94 | 12.31 | 12.30 | 17.33 | **12.30** | b | −1.73 | 0.55 | HARD_NOISY |

## The two flags

**SMALL_KNOWN (2 cells): close ≈ already known at the read-moment.** WTA_MAIN ge76
(ceiling 1.11) and WTA_MAIN le25 (1.49). A naive current-price read lands within
~1-1.5¢; a fitted estimator has almost nothing to add — don't wire one here.

**HARD_EXPLOITABLE (5 cells): naively hard, but the drift is one-directional.**
The entire **51_75 band across all four categories** (WTA_MAIN +2.58, ATP_CHALL
+2.14, ATP_MAIN +2.72, WTA_CHALL +3.29) plus **WTA_CHALL ge76 (+2.99)**. Every one
drifts **up** into the close (66-79% of legs same-signed) — the climb-side climbing
into the bell, quantified: the read-moment mid systematically **understates** the
landing by 2-3¢. A naive predictor cannot see it (ceiling MAE 3-9¢), but the drift
is systematic and directionally exploitable, and a fitted estimator that encodes
the climb is where wiring pays.

**HARD_NOISY (9 cells): hard and two-sided.** Ceiling MAE 2.8-12.3¢ but drift is
small or sign-mixed (dir ≤ 0.6). WTA_CHALL 26_50 (12.3) and the WTA_CHALL le25/51_75
cells are the noisiest — the most MAE headroom for a fitted estimator, but no clean
directional drift to lean on, so the gains there are uncertain.

## Reading

The floor a fitted landing estimator must beat is **best-of-three MAE ≈ 1-12¢ per
cell, ~4.9¢ pooled** (current mid). In two WTA_MAIN cells the close is already
known — an estimator is wasted. In the five HARD_EXPLOITABLE cells the naive floor
is high *and* the miss is one-directional (the 51_75 climb), so both a better
estimator and a drift-aware entry have room. In the nine HARD_NOISY cells the naive
floor is the honest bar and the residual is two-sided — a fitted estimator must
demonstrate it beats current-mid before it earns the wire. Model-free, hindsight
never used; every read-moment and predictor is reconstructable from the leg's own
tape rows before the instant.

## Artifacts

`LANDING_PREDICTABILITY_LEGS.csv` (per leg: read-moment mid/qual-ask/last-print,
three signed errors, drift) and `LANDING_PREDICTABILITY_SUMMARY.json`.
