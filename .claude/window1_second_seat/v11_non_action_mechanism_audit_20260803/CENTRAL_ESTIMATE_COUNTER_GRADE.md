# COUNTER-GRADE + THE 95-vs-37 SHORTFALL — @35555882

License: LAW_INDEX @ 35555882, sha256 41784e6a… · L8 L11 L18 L20 L22 · TWO-WAY STREET F-VS-122 · welds.
Seat: CC verification.

## 0 — THE SHORTFALL DOES NOT EXIST — my error, corrected

**There is no 95-vs-37 gap.** My F-VS-124 counterfactual was computed with the hit test inverted: I scored `pred_cf <= realized_low` — which is the *miss* condition — instead of `realized_low <= pred_cf`. Recomputed correctly on the identical @17ed8291 rows, same populations, same phase bands:

| | filed | **corrected** | this build |
|---|---:|---:|---:|
| median signed error | −4 | **−4** | −4 |
| hit share | 3,028/3,179 = 95.3% | **1,214/3,179 = 38.2%** | 579/1,556 = **37.2%** |

Per leg, corrected counterfactual vs the build: BAR 0.000/0.000 · SVA 0.000/0.000 · DAN 0.056/0.000 · PAL 0.358/0.327 · PRA 0.769/0.769 · LAJ 0.773/0.776 · URS 0.878/0.895 · GIU 0.870/0.643. **The build reproduces the counterfactual to within one point overall and on six of eight legs.**

Row-diff of what differs: estimator input — identical (surface cells match my population; ATP_CHALL P00_10 q50 −4, P90_100 +3, and the build reconciles its 63,227 points against my 63,260 with the −33 difference named as `TERMINAL_PATH_POINT_PER_LEG_EXCLUDED`). Population selection — the build has 1,556 graded rows vs 3,179 because the new predictions changed placements and therefore the stage set (PAL 2,827→1,231); applying my per-leg rates to the build's mix predicts 91.6%, so mix is *not* the explanation either. Deadline construction and scoring basis — unchanged (`stale_deadline_emissions: 0`, same law text). **Nothing differs. The gate's `named_step_failures: PHASE_CENTRAL_ESTIMATE_DID_NOT_REPRODUCE_OR_BEAT_F_VS_124` is void — it fails against a number that was wrong.**

F-VS-126's census is unaffected: its attribution test used `own + q50 >= realized`, the correct direction.

## 1 — Counter-grade

| item | verdict |
|---|---|
| Five fills | all trade-id verified in fit-local prints.jsonl (price, ts ±10 ms, true_print): GIU 69/b113f8de · URS 57→rest 58/a4575e0c · PAL 40/34d9e70c · SVA 45/013d5fa3 · LAJ 53/8c5eeb51. **entry == standing rest 5/5** |
| Coherence at placement | **URSPAL both legs coherent-lane** (PAL 40 set @1784030027 COHERENT, LAYERED_COHERENT_ENVELOPE, conditioned expected future low 40; URS 58 set @1784031046 COHERENT, atomic-rearm replacement inside envelope [58,58]). **LAJSVA both legs and GIU were placed at DISAGREES from the live touch** (`OWN_EVIDENCED_LIVE_TOUCH_ENVELOPE_UNRESOLVED/NULL`) |
| DANPRA | **F-VS-121 CLOSED**: stamp is now `LAWFUL_INCOMPLETE` with `rest_at_floor_proven: true` and 6 rest-at-floor rows, proof `59+41=100; max(0,99-100)=0`, truth receipt cited. GIUBAR carries `UNSTAMPED_INCOMPLETE` (proven rests, offer 6) and the two completions `NOT_APPLICABLE_COMPLETE` |
| Touch receipt | independently verified: 707 rows; exactly **16** with `live_bid == audited truth floor`, and in **16/16** the action stood at the floor (GIUBAR|BAR 11, DANPRA|DAN 3, URSPAL|URS 1, LAJSVA|SVA 1). Receipt's 16/16 confirmed |
| Bias table | median −4 confirmed; 1,556 graded / 579 hits reproduce |
| Determinism · custody | each game replayed twice, all byte-identical before scoring; custodied trace + rearm receipt present on disk with matching sha256 (1544561c…, 0afd2bb5…) |

**Functionable-standard note (F-VS-108)**: only URSPAL was completed with the belief machine pricing both rests. LAJSVA's two legs were priced by the live touch at DISAGREES — a no-opinion completion, scoring **zero** on the bed. Bed under the standard: **1 of 4**.

## 2 — Δ2 anatomies, two-way attributed

**URSPAL — lawful floors 39+57 = 96 (Δ4); paid 40+58 = 98 (Δ2).**
- PAL +1: coherent placement at 40 (`conditioned_expected_future_low_cents: 40`, live bid 41, envelope [40,44]); the 39 floor printed at 1784042066.6, **69 s after** PAL filled at 40. A rest 1¢ lower fills on that later print. The conditioned population's lower quantile at PAL's phase reaches 39. → **DATA-UNCONSUMED** (central estimate used, lower quantile in the same consulted store licensed the floor).
- URS +1: envelope pinned degenerate [58,58] with live bid 56/ask 59; the 57 floor print filled the 58 rest. Same store, lower quantile licenses 57. → **DATA-UNCONSUMED**.

**LAJSVA — lawful floors 51+41 = 92 (offer 7); paid 53+45 = 98 (Δ2), LAJ +2 / SVA +4.**
- LAJ +2: placed at the live touch 53 (bid 53/ask 55) while the belief envelope stood at **[60,62]** — 9–11¢ above the eventual floor 51. The touch lane rescued the trade the belief would have missed entirely. → belief **MISREAD**, capture **DATA-UNCONSUMED** (floor 51 printed later; a 51 rest fills).
- SVA +4: placed at the live touch **45** while the belief envelope was **[39,43] — which contains the floor 41**. The touch lane over-rode an envelope that had the answer. → **DATA-UNCONSUMED, self-inflicted**: this is the direct cost of the consume-touch lane I recommended in F-VS-125, applied when the envelope is merely "unresolved" rather than absent. 4 of LAJSVA's 6 lost cents are here.

## 3 — GIUBAR, why incomplete, per leg

- **BAR (decisive)**: at the 27 floor print (1783841801.304) the rest stood at **25**, priced from the live touch bid 25 (ask 30, envelope null, DISAGREES) — the 27 traded *inside the spread*, above the touch, so a 25 rest cannot fill. BAR then walked 26/27/26/27… and stood **at 27 exactly, 11 times from 1783851291** — 2.6 h too late; 27 never printed again. Attribution: the touch street structurally cannot capture inside-spread prints; the conditioned store's upper quantile at BAR's phase (ATP_CHALL P10_30, q75 0 → own low 29 → rest 29) **would** have filled on the 27. → **DATA-UNCONSUMED**.
- **GIU**: filled 69 at 1783841972.759 from the live touch at DISAGREES — 3¢ above its own floor 66 and **7.6 h before** that floor printed. Not the cause of incompleteness (it did fill), but it locked the pair 3¢ worse than lawful.
- Pair result: 69 + no BAR fill = incomplete; lawful was 27+66 = 93.
