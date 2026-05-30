# Exit-Strategy Handoff — State of the World (v3)

**Scope of this doc:** ATP_MAIN first. Method generalizes to ATP_CHALL / WTA_MAIN / WTA_CHALL after sign-off.
**Status:** Exit layer (Part 1) is the only thing in play. Entry discounts (Part 2) are NOT built.
**Purpose:** Everything we've learned, built, discovered, and the open question that needs an *objective* answer — written so two teams (Opus via the app/Cursor, and the agent here) can work it in parallel and keep each other honest.
**Hard rule:** No new data is being pulled. We are looking at the data we already have from its most absolute dimensions.

---

## 0. The one-paragraph summary

We are deriving, for each entry cent **5c–94c**, the single best **exit offset (+X)** to take profit on a Kalshi tennis contract. The "ground-truth" surface we built ranks every exit by EV / ROI / hit-rate. It is *mostly* right, but it has **two known defects**: (1) the thin, extreme cells (cheap underdogs 5–15c, deep favorites 87–94c) pick **lottery exits** that rest on a handful of jackpot samples; and (2) the neighbor-pooling kernel that's supposed to stabilize thin cells is **mis-weighted** — it's a wide, nearly-flat smear reaching ±15c instead of a tight, steeply-decaying kernel centered on the cell. The open question — believed to have an **objective answer** — is: *what is the optimal neighbor blend?* Own-cell dominant, ±1c heavily overlapped, ±2c lighter, ~zero past that — but derived, not hand-picked. Each cell keeps a **unique config** because every cent re-expresses the pooled move against its **own cost basis** (apples → oranges).

---

## 1. The trade and the data (what we actually know)

- **Instrument:** Kalshi tennis match contracts (binary, settle 0 or 100c). Four categories: ATP_MAIN, ATP_CHALL, WTA_MAIN, WTA_CHALL.
- **Entry anchor = T-20 premarket snapshot.** This is the **FLOOR** — a conservative entry assumption only. `anchor_price × 100 = entry cent`. We enter as a **taker** (`maker_bid_offset = 0`). This is intentional and conservative.
- **Part 2 (NOT built):** Real entry discounts from the T-4h → T-20 premarket drift. We know discounts exist; we have not "jumped down the entry hole." Do not conflate this with the exit layer.
- **Fixed sizing assumption:** 10 contracts / fill (10c cost-basis assumption). Favorites = "ballast" (high-hit stability). Cheap underdogs = "engine" (deep bounces, big returns).

### Corpus (the raw tape)
`data/durable/spike_volatility_map/atp_main_spike_perN.parquet` — **4137 rows** (ATP_MAIN).

| column | meaning |
|---|---|
| `anchor_price` | T-20 snapshot price (×100 = entry cent). The FLOOR. |
| `raw_max` | peak price the contract reached (×100 = peak cent). |
| `raw_max_ts` | timestamp of the peak. |
| `settlement_value` | final outcome, 0 or 1. |
| `time_to_max_min` | minutes from anchor to peak. |
| `spike_cents`, `spike_pct`, `truncation_delta_cents`, `old_metric_cents`, `size_qual_max_250`, `drop_reason` | supporting / diagnostic. |

**Critical limitation:** there is **NO pre-anchor price band / low field.** We only have the **anchor (T-20)** and the **peak (raw_max)**. We do NOT have the contract's full price excursion history. This is why re-bucketing by "what price the contract touched a penny above/below at any point" is **not possible and was correctly abandoned** — it would be inventing data we don't have.

### How an exit outcome is computed (the honest corpus reconstruction)
For entry cent `c` and exit offset `+X` (target price `c+X`):
- If the contract's peak reached the target (`raw_max×100 ≥ c+X`) → the exit **hits**, capture **+X** cents.
- Else → it rides to settlement: **win → +(100−c)**, **loss → −c**.
- `EV = mean PnL` across all positions for that cell; `ROI = EV / c × 100`; `hit = fraction that reached the target`.

Validated against `achievable`: e.g. **89c → +9: EV 4.92, hit 95.8%** matches exactly. Builder: `analysis/build_curve_atp_main.py` → `analysis/curve_atp_main.json`.

---

## 2. The ground-truth surface (what's built and what's trusted)

**File:** `data/durable/exit_atlas_v1/atp_main_pooled_surface_v3.json`
**Top keys:** `meta, cells, rows, achievable, achievableLocked, finest`

- **`rows`** — 90 rows, cents 5–94. Each row:
  `c, ownN, effN, sigma, breakevenFloorR, breakevenFloorForwardR, ceilingMaxR, complementC, neighbors[], achievable, achievableLocked`
  - `achievable = {bestX, bestT, ev, roi, hit, holdEv, basis, sigma, rule, cvErr}` — **THE answer key for exits.** `basis` ∈ {`own-N`, `pooled`}.
  - `neighbors[]` — the pooling kernel: `{c, ownN, weight, mass, pct}`.
- **`cells` grid = BROKEN.** It's relative-trajectory based and disagrees with `achievable` on 82/90 cells. **DO NOT USE.** (Corrected replacement built — see §4.)

**ATP_MAIN surface stats:**
- ownN min/med/max = **18 / 48 / 79**
- effN min/med/max = **324 / 712 / 987**
- sigma min/med/max = **4.68 / 6.0 / 9.80** (σ widens at the extremes)
- achievable basis split = **own-N: 75, pooled: 15**

---

## 3. THE STRATEGY THESIS (the insight that drives everything)

> Take any max the 5c ever got to. Every number under that peak was *reached* — somewhere. Somewhere in the high teens is bound to happen at a **frequency that generates alpha** — that's already >100% ROI on a single trade. **We do not want the giant jackpots.** It's the same logic flipped on the expensive end (the big-priced N).

**Translation:** Don't chase the rare ceiling-spike exit (huge ROI, tiny hit rate, rests on 4–7 lucky samples). Target the **high-frequency zone** where a still-huge ROI happens *often*. Mirror the logic on the favorite end (bank high-frequency small wins; don't stretch into the hit-rate cliff).

**Evidence (ATP_MAIN, own-N tape):**
- **5c cell:** jackpot +65 → hit ~16%, ROI ~1300% (rests on **4 of 21** positions). High-frequency zone: +15 → hit ~40% ROI ~300%; +18 → hit ~32% ROI ~360%; +20 → hit ~30% ROI ~400%. **Want the high-teens zone, not +65.**
- **9c cell:** +90 exit rests on **7 of 23** ceiling-spikes; hit is flat ~30% from +71→+99 because it's *the same 7 winners* — looks stale because it IS stale.
- **12c cell:** +20 rests on **15 of 21** (71%) — a REAL edge, not a lottery.
- **Favorite mirror, 89c:** +5 → hit 96% / ROI 6% vs +9 → hit 72% / ROI 10% — a hit cliff. Bank the high-frequency small win.

This is why the lottery exits in thin cells need recalibration to a **credible high-frequency basis**, and why pooling the tight neighborhood matters: it gives thin cells enough sample mass to find the real high-frequency zone instead of overfitting 4–7 lucky tapes.

---

## 4. What's been BUILT this session

| artifact | what it is |
|---|---|
| `analysis/build_curve_atp_main.py` → `analysis/curve_atp_main.json` | Honest corpus-reconstructed per-offset EV/hit/ROI (own cost basis, pure own-tape, no pooling). VALIDATED (89c→+9 matches achievable). |
| `analysis/build_corrected_surface.py` → `{cat}_corrected_surface_v3.json` (all 4) | Locked surface with the broken `cells` grid replaced by the corpus ground-truth grid `{c,R,ev,hit,roi,n}`. Argmax vs achievable: atp_main 82/90, atp_chall 80/90, wta_main 83/90, wta_chall 81/90. |
| `analysis/build_pyramid_html.py` → `{cat}_pyramid_v3.html` | INTERACTIVE D3 pyramid. Each cent = a vertical column (UNDERDOGS 5–49c top band, FAVORITES 50–94c bottom band). Y-axis = every offset +1→+94, labeled, scrollable. Lenses: best (EV×hit harmony), roi, ev, hit. White ring = achievable best-X; magenta dash = harmony exit; cyan shoulder tick. Hover tooltip = full readout + neighbor borrows. |
| `analysis/visualize_ground_truth_v3.py` → `{cat}_ground_truth_v3.html` | The original interactive triangular heatmap ("the actual pyramid" you referenced). Lenses EV/ROI/Achievable/Finest. NOTE: still injects the broken `cells` grid. |

**Prior-segment (committed) — exit floor wiring:**
`version_c_blueprint_v3.py` (per-cent, reads `achievable`), `analysis/gen_deployment_percent_v3.py`, `tennis_v5.py` (executor; `get_strategy_v5` ~line 228; `BABY_SIZING_MODE=True`, `BABY_ENTRY=10`, `BABY_DCA=5`; imports `version_c_blueprint_v3`), `analysis/build_pooled_surface_v3.py` (surface builder using `exit_chain_core` module: `_gauss_weights`, `_pooled_ev_hr_at`, `select_per_cent_sigma`, `finest_config`). Commits: 858af98, af38961, 483902e, 2976e93, f1a3cd9. `V3_EXIT_FLOOR_HANDOFF.md` committed.

**SCRAPPED (do not build on):** `scorecard_atp_main.*`, `viz_scorecard_atp_main.py` (built on broken cells grid).

---

## 5. THE OPEN QUESTION — the optimal neighbor blend (needs an objective answer)

### 5a. The bug, in hard numbers
The current kernel for **20c** (σ = 7.03) is a near-flat smear reaching **±15c**:

```
  20c  w=1.000   (own — dominant, correct)
  19c  w=0.990   21c  w=0.990   ← essentially equal to own; should be heavy but BELOW own
  18c  w=0.960   22c  w=0.960   ← barely decayed
  17c  w=0.913   23c  w=0.913
  16c  w=0.850   24c  w=0.850
  15c  w=0.776   25c  w=0.776
   ...
  10c  w=0.363   30c  w=0.363   ← still 36% weight TEN cents away
   9c  w=0.294   31c  w=0.294
   ...
  35c  w=0.102                  ← still pooling a cent FIFTEEN away
```

**Why it's wrong (user's exact point):** the cell should be "the main plug, but overtly overlapped by 19c and 21c; same but a little less for 18c and 22c," and then fall off fast. The current kernel instead spreads weight almost evenly across a ±5–6c band and keeps a non-trivial tail out to ±15c. That makes hit rates look stale/uniform and the neighbor borrows look like a meaningless flat list (e.g. tooltip shows "25c 6%, 26c 6%, 17c 6%, 18c 6%, 22c 6%, 20c 5%" — no center of gravity).

**Second defect (provenance mismatch):** the deployed thin-underdog picks are `basis: own-N` (they used ZERO pooling), yet the tooltip *displays* the wide pooled-neighbor weights. So the tooltip's provenance is misleading — it shows a blend that wasn't actually used to make the pick.

### 5b. What the optimal blend must satisfy (the spec)
1. **Own-cell dominant.** Cell `c`'s own tape is the main plug.
2. **±1c heavily overlapped, but strictly below own.** 19c/21c carry strong weight (they're the same opportunity a penny off), but **less than** the cell itself — not the current ~0.99 near-tie.
3. **±2c meaningfully lighter.** 18c/22c contribute but clearly tapered.
4. **~Zero past ±2–3c.** No 0.10 weights fifteen cents away. The tail must die.
5. **Apples → oranges (the unique-config rule):** pool the *shape of the move* (relative trajectory) across the tight neighborhood, then **every cent re-expresses it against its OWN cost basis** for EV/ROI/hit. 19c, 20c, 21c overlap on the move (apples) but a +X offset costs 19c vs 20c vs 21c to enter (oranges). This is what gives every cent a **unique config** even though neighbors inform it.
6. **Objective, not hand-picked.** The falloff shape should be *measured/derived* from the data, not eyeballed.

### 5c. Candidate objective formulations (for both teams to attack)
- **Held-out predictive fit:** treat blend weights as a fit problem — which kernel (which σ, or which decay family) best predicts a held-out cell's **own-tape** outcome curve from its neighbors? The kernel that minimizes out-of-sample error on the move-shape is the objective answer.
- **Sample-mass floor:** pick the *tightest* kernel that still clears a minimum effective sample count to make the high-frequency-zone exit statistically credible (ties to the strategy thesis — enough N to trust the high-teens zone without smearing in far cents).
- **Stop-rule for best-X (separate but related):** once the blend is fixed, the exit pick must avoid jackpots. Candidate rules discussed (NOT locked): frequency floor (~35% hit), frequency×ROI peak, or knee-of-the-ROI-curve. The thesis leans toward "highest-frequency zone that still generates alpha, no jackpots."

### 5d. Open design decisions (NOT locked — both teams should converge)
- Exact decay family + width (Gaussian σ? triangular? something derived?).
- The minimum effective-N floor for thin cells.
- The best-X stop-rule (frequency floor vs freq×ROI vs knee).
- How to surface provenance honestly in the tooltip (show the blend that was *actually* used).

---

## 6. Repo / access

- **Repo:** github.com/OMIGROUPOPS/Omi-Workspace (public, main). Working dir `arb-executor/`.
- **Clone:** `/home/user/workspace/Omi-Workspace`.
- **HEAD:** f1a3cd9 (v3 exit floor: own-tape-gated blueprint replaces version_b; rewire tennis_v5).
- Prior-segment artifacts (blueprint/executor rewire) are committed; the corrected surface + pyramid + this analysis round are **uncommitted**.

---

## 7. Guardrails (lessons the user keeps enforcing)

- **The tape always wins.** An approximation / pooled-smoothing that *overrides* ground truth is the failure mode to avoid. `achievable` is the answer key — EXCEPT thin extreme cells are overfit own-N lottery picks that need recalibration to a high-frequency basis.
- **Don't constrict the data.**
- **T-20 is only the floor.** Don't conflate the exit layer with the unbuilt entry-discount layer (Part 2).
- **Don't invent data.** We do NOT have pre-anchor price bands — only anchor + peak. Re-bucketing by price excursion was correctly abandoned.
- **Each cell = unique config**, achieved via apples→oranges (pool the move, re-express against own cost basis) — NOT by single-anchor-price bucketing (too thin/artificial).
- **Show renders before committing.** Never deploy off the broken `cells` grid.
- **Whatever objectively makes the most sense.** This blend question is believed to have an objective answer — derive it.

---

## 8. FOR OPUS — your task (read this first)

You're one of two agents working this in parallel. A second agent is running the numeric derivation in the sandbox/Cursor against the real data. **Your job is the METHOD, not the numbers** — you do not have the data files loaded, so do not invent values. Derive the *objectively-correct* kernel form and fit procedure; the other agent executes it and we diff the two answers to keep each other honest. **Push back** on the assumptions in §5b–§5c — do not rubber-stamp this doc.

### The codebase carries everything (it's a public repo)
The data and the project's own verbiage are committed — not just this doc. Key paths (all under `arb-executor/`):

- **This doc:** `arb-executor/analysis/EXIT_STRATEGY_HANDOFF_v3.md`
- **Ground-truth surface:** `arb-executor/data/durable/exit_atlas_v1/atp_main_pooled_surface_v3.json` (`rows[].achievable` = answer key; `rows[].neighbors[]` = the current mis-weighted kernel; `cells` grid = BROKEN, ignore).
- **Raw corpus (the tape):** `arb-executor/data/durable/spike_volatility_map/atp_main_spike_perN.parquet` (4137 rows; anchor_price + raw_max only — no pre-anchor band).
- **Honest reconstruction:** `arb-executor/analysis/build_curve_atp_main.py` → `curve_atp_main.json`.
- **Corrected surface:** `arb-executor/analysis/build_corrected_surface.py` → `{cat}_corrected_surface_v3.json`.
- **Interactive pyramid:** `arb-executor/analysis/build_pyramid_html.py` → `{cat}_pyramid_v3.html`.
- **Surface builder + kernel math (where the bug lives):** `arb-executor/analysis/build_pooled_surface_v3.py` + `arb-executor/analysis/exit_chain_core.py` (`_gauss_weights`, `_pooled_ev_hr_at`, `select_per_cent_sigma`, `finest_config`).

### CRITICAL existing finding — the doctrine verbiage (read before proposing aggressive pooling)
`arb-executor/data/durable/spike_volatility_map/ATP_MAIN_LOCKED_DOWN.md` is the project's locked doctrine (codes A21/A39/B13/B16/B18/E32/G22; "Plex-confirmed methodology"). It contains a result that **directly constrains your answer**:

> Pooling adjacent 1c cells *DESTROYED* edge in two specific cases: pooling cells 37 (+$42, X=39c) and 38 (−$12.60, X=1c) into [37,39) produced −$8.10 (constituent sum was +$29.40). **Direct evidence that some of the 1c-vs-3c gap is real cell-by-cell heterogeneity that pooling destroys, not pure over-optimization.**

Also from that doc: cheap regime (5–30c) deploys 8% of capital but makes 38% of dollar profit; A39 geometry — 1c of move at 7c entry = 14% ROI vs 1c at 90c = 1% ROI. The cheap cells are exactly the thin/extreme cells with the lottery-exit problem.

### The tension you must resolve
There are two opposing forces, and the objective kernel sits between them:
- **Thin cells need sample mass** (own-N as low as 18–23) → argues *for* borrowing from neighbors.
- **Pooling demonstrably destroys real heterogeneity** (the 37/38 case) → argues *against* borrowing, or for borrowing only from the *immediately* overlapping cents.

The user's stated shape (own dominant; ±1 heavy but strictly below own; ±2 lighter; ~zero past that) is the hypothesis. Your task: is that shape *objectively* correct, and how do you fit its exact decay from the data without hand-picking σ? Define the held-out validation that would prove it.

### Deliverable from you
1. The kernel family + an objective fit procedure (how to set the decay from data, not by eye).
2. The best-X **stop-rule** that avoids jackpots (frequency floor vs freq×ROI peak vs knee-of-curve — pick and justify).
3. How to honestly surface provenance (the tooltip currently shows a pooled blend that wasn't actually used for own-N picks).
4. Explicit reconciliation with the 37/38 anti-pooling evidence above.
