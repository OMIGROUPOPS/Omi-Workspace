# Agent numeric verification — blend/agent-derivation

Verifies the three load-bearing claims in Opus's method derivation against the
real ATP_MAIN corpus (4137 tapes; own data only — anchor cent + peak cent, no
invented values). Script: `analysis/verify_blend_claims.py`.

## Outcome model (honest reconstruction)
For anchor cent `c`, offset `+X` (target `c+X`):
- hit if `peak_cent >= c+X` → capture `+X`
- else ride to settlement: win → `+(100-c)`, loss → `-c`
- `EV = mean PnL`, `ROI = EV/c*100`, `hit = P(peak>=c+X)`

---

## Claim 1 — CV bandwidth selector is broken — CONFIRMED
Own-curve-MSE vs σ is **monotone** for every cell tested → no interior minimum →
always a corner solution (slams to a grid endpoint). It is not a kernel chooser.

```
c=7 : s0.5=0.4  s1=1.8  s2=1.9  s3=1.9  s4=1.8  s6=3.1  s8=6.3   [wants σ→0 / unstable]
c=12: s0.5=0.8  s1=6.7  s2=13.6 s3=16.1 s4=17.5 s6=19.8 s8=22.5  [wants σ→0]
c=13: s0.5=0.7  s1=4.8  s2=8.7  s3=7.3  s4=6.1  s6=5.3  s8=6.0    [non-convex, noisy]
c=38: s0.5=2.3  s1=18.9 s2=40.3 s3=51.5 s4=57.8 s6=64.6 s8=67.5  [wants σ→0]
```

## Claim 3 — homogeneity direction is real — CONFIRMED (but see correction)
Relative-move (peak − c) distributions, two-sample KS:

```
37c vs 38c: KS=0.364 p=0.001  REJECT  (medians 44 vs 21) — genuinely different
19c vs 20c: KS=0.267 p=0.166  admit   (medians 32 vs 22)
20c vs 21c: KS=0.257 p=0.165  admit   (medians 22 vs 18)
12c vs 13c: KS=0.280 p=0.291  admit   (medians 28 vs 16)
 5c vs  6c: KS=0.274 p=0.289  admit   (medians 12 vs  7)
```
Blind 2c pool of [37,39): own constituent sum **+$39.90** → blind pool **+$9.80** (edge destroyed).
So 37/38 ARE different in *degree*. **Correction (below): this must express as
continuous down-weighting, NOT a binary reject.**

## Claim 2 — N* ≈ 40–60, only thin cells borrow — REFUTED
Bootstrap-argmax stability (share of 400 resamples whose best-X is within ±2c of
the full-sample best-X; "stable" = ≥80%) does **NOT** rise with own-N:

```
ownN [ 0, 30): 17 cells, mean modal-agreement 61%
ownN [30, 40): 14 cells, 50%
ownN [40, 50): 16 cells, 44%
ownN [50, 60): 20 cells, 42%
ownN [60,100): 16 cells, 46%      <-- deepest cells NOT more stable
```
Same own-N, opposite stability: favorites c=90,91,92,93 at own-N≈20 are **100%
stable**; cheap cells c=5–15 at own-N 21–28 are **lottery (32–64%)**. Sample
*count* is not the axis. What differs is move-distribution concentration — i.e.
the **weighted depth (eff-N)** of the cell's pool, not its raw count.

---

## THE CORRECTION (user-interjected — this is the final answer to the exit reconcile)

There is **no gate, no "borrow vs don't," no own-only cell.** Every cent ALWAYS
pools. Each cell's config is a weighted pool — cell heaviest, ±1 heavy, ±2
lighter, fading out — and that pool is **slightly differently weighted at every
single cent.** Walking c→c+1 re-centers the whole kernel and shifts every weight
by one notch, so the per-cent configs slide **smoothly**. The overlap is a
**necessity**, not an option: it is what gives every cent a unique-but-continuous
config and the **conviction** that the pick isn't standing on one thin tape.

- Homogeneity (37 vs 38) is right about *direction* but must be **continuous
  down-weighting**, never zero/one. Heterogeneous neighbors get *less* weight.
- **eff-N** = the **weighted depth of that always-on pool at each cent** — the
  reason every cent's config is slightly different. Not a threshold.
- The blend must be perfect at **every single cent** (conviction), then
  **converted apples→oranges** (the pooled relative-move re-expressed at each
  cent's OWN cost basis) to read out the **optimal config** per cell.

Open question for the method authority: what objectively sets the smooth,
per-cent-shifting weight decay, such that 19/20/21 overlap heavily yet each
re-expresses at its own cost basis?
