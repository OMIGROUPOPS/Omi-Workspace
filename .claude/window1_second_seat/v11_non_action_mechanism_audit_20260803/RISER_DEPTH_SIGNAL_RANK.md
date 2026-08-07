# Riser depth signal rank — which inputs announce the deep dip

Analysis seat only. Read-only. **No placement counterfactual — signal rank first.** Population (V38 maker-only `2c54d724`): every **riser deep-excursion moment** = the **298 RISING_REST_FILLED_SHALLOW** sides + **38 one-off union-reach bottoms** (30 RISER_NO_TWO_VISIT_TRAILING_PULSE_FLOOR + 8 UNION_REACH_PRECEDED_RESIDENCY) = **336 riser sides**. The excursion instant is each side's sealed `reach_first_evidence_timestamp_epoch`; its signal slate comes from the V38 `reach_snapshot` (own book), the **paired leg tape** (mirror), and the sealed divot census `d1ac9497` (own pulse). **Control = the same legs at 3 non-spike receipts each** (|Δt|≥120s, W1 span) → 1,008 control rows. AUC = P(spike>control); lift = oriented tercile lift. Machine artifact: `.claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/RISER_DEPTH_SIGNAL_RANK.json`.

## The rank — what announces the deep riser dip (336 spikes vs 1,008 controls)

| bucket | signal | oriented AUC | lift | direction | spike med | ctl med |
|---|---|--:|--:|---|--:|--:|
| (a) other expr slide depth | `other_slide` | 0.686 | 1.53 | lower@spike | 0.0 | 0.5 |
| (e) dwell | `dwell` | 0.674 | 1.7 | lower@spike | 52.0 | 1488.0 |
| (e) spread | `spread` | 0.580 | 1.03 | higher@spike | 1.0 | 1.0 |
| (b) own-book pressure | `own_dr` | 0.572 | 1.21 | higher@spike | 0.416 | 0.382 |
| (c) other-book pressure mirror | `other_dr` | 0.541 | 1.17 | higher@spike | 0.408 | 0.387 |
| (f) cap room | `cap_room` | 0.521 | 1.04 | higher@spike | 99.0 | 99.0 |
| (d) own pulse rhythm | `pulse_depth` | 0.517 | 1.0 | higher@spike | 0.0 | 0.0 |
| (d) own pulse rhythm | `pulse_freq` | 0.514 | 0.99 | lower@spike | 0 | 0 |

**Combined logistic (in-sample) AUC = 0.708** — barely above the best single signal, so the slate is largely **redundant**: two inputs carry it.

## Reading the rank

- **(e) dwell is the material announcement.** At the deep dip the best ask has stood only a median **52 s** vs **1,488 s** (25 min) at control — a ~28× separation, lift 1.7. The deep riser excursion is a **fresh, transient ask descent**, not a long-parked quote. This is the divot doctrine restated on the signal side.
- **(a) other-expression slide ranks top by AUC but is sub-cent in magnitude.** The paired leg sits **at/near its running high** (slide ≈0) when the riser dips — the pair is **anti-coupled** at the excursion — but the absolute separation is a fraction of a cent, so it rank-orders without moving money.
- **(b) own bid-depth share weakly announces** (0.416 vs 0.382, lift 1.21): a modestly bid-heavy own book at the dip. **(c) the mirror depth ratio is weaker still.**
- **(d) own pulse rhythm is dead** (AUC ≈0.51, lift ≈1.0; median trailing troughs = 0 at both spike and control). A riser's own recent divot history does **not** foretell its deep excursion. **(f) cap room is inert** (median 99 both) — the pair almost never fills before the riser's dip, so headroom carries no signal.

## Per category — the rank re-orders

| category | n spikes | #1 | #2 | #3 |
|---|--:|---|---|---|
| ATP_CHALL | 152 | dwell (0.67/L1.66) | other_slide (0.67/L1.5) | own_dr (0.57/L1.2) |
| ATP_MAIN | 75 | dwell (0.78/L2.28) | other_slide (0.69/L1.5) | spread (0.64/L1.03) |
| WTA_CHALL | 55 | other_slide (0.72/L1.71) | other_dr (0.66/L1.46) | own_dr (0.55/L1.14) |
| WTA_MAIN | 54 | other_slide (0.70/L1.5) | dwell (0.68/L1.89) | own_dr (0.62/L1.39) |

**Dwell dominates ATP** (ATP_MAIN lift **2.28**), **other-slide dominates WTA**. Own pulse and cap room are bottom-ranked in every category.

## Named games

| game · riser leg | global dir | V38 owner | in 336? | reach | entry | excursion dwell | own dr | pulse visits |
|---|---|---|:-:|--:|--:|--:|--:|--:|
| NIKVRB · NIK | FALLING | RISING_REST_FILLED_SHALLOW | YES | 18 | 27 | **11 s** | 0.709 | 5 |
| ARNROM · ARN | UNKNOWN | RISER_PULSE_REST_OFF_REACH | no | 50 | None | **13667 s** | 0.438 | 0 |
| BOSCOP · COP | UNKNOWN | RISER_PULSE_REST_OFF_REACH | no | 47 | None | **25956 s** | 0.232 | 0 |

- **NIKVRB** — both legs are in scope (RISING_REST_FILLED_SHALLOW). NIK dips on an **11 s** fresh ask with own bid-share **0.709** (vs ~0.40 control); VRB on a **9 s** ask at **0.841**. Both sides are textbook: the short-dwell + bid-heavy signature the rank names. (NIK is FALLING by close yet RISING-owned at the dip — the excursion state, not the global direction.)
- **ARNROM · ARN** and **BOSCOP · COP** are the risers' **out-of-scope contrast**: their deep reaches (50, 47) are **RISER_PULSE_REST_OFF_REACH**, not shallow-fills — and they sit on **enormous dwell (ARN 13,667 s, COP 25,956 s)**, the *opposite* of the in-scope 52 s. That is exactly why the 2-visit pulse floor went off-reach: a durable long-parked deep level, not a transient divot. The dwell signal separates the catchable dip from the structural miss.

## Conservation

336 spike sides (298 shallow-fill + 30 no-two-visit + 8 union-reach-preceded) × 3 controls = 1,008 control rows. 8 signals ranked overall + per 4 categories. Combined logistic in-sample AUC 0.708. Divot census `d1ac9497`, union reach `57daf3c1`, V36 `bfde0d8`, V38 `2c54d724`. Tapes = fit-local ticks (Jul-6 depth columns).