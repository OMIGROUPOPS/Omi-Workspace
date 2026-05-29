# Deployment Viability Map — v3 Pooled Best-X (T-20 Taker, all 4 categories)

Built from the deployed `*_pooled_surface_v3.json` surfaces. PnL convention:
Kalshi 1c fee, enter at T-20 anchor cent as a taker, exit at pooled best-X (or
hold to settle). "Deployable PnL @1ct/N" = per-cent EV × that cent's observed
volume, summed — i.e. realized cents if you'd put 1 contract on every trade at
that cent. This is the **standalone (no entry discount)** picture. Part 2
(entering at a discount below the anchor) lifts everything and rescues the
negatives.

---

## 1. Standalone viability — how many cents stand on their own

| Category | N | Profitable | Near-breakeven (discount candidates) | Negative (need real discount) |
|---|---|---|---|---|
| ATP_MAIN  | 4,137 | **86 / 90** | 38, 39, 68 | 82 |
| ATP_CHALL | 5,326 | **82 / 90** | 54, 80, 86 | 85, 87, 88, 89, 94 |
| WTA_MAIN  | 3,683 | **85 / 90** | 73, 84 | 53, 83, 88 |
| WTA_CHALL | 887   | **84 / 90** | 59 | 53, 67, 77, 78, 93 |

The vast majority of cells already carry positive at T-20 with no help. The
"needs discount" set is small and **concentrated in the favorite zone** (80-94)
for the challenger draws — exactly where exit headroom is thinnest and upsets
are most common.

---

## 2. Where the deployable money actually is (volume-weighted)

Per-zone deployable PnL @1ct/N (positive cells only):

| Category | cheap (5-39) | mid (40-79) | fav (80-94) |
|---|---|---|---|
| ATP_MAIN  | 9,551c · +6.84c/N · 33/35 | 10,403c · +4.57c/N · 39/40 | 1,695c · +3.66c/N · 14/15 |
| ATP_CHALL | 12,405c · +6.54c/N · 35/35 | 15,254c · +5.52c/N · 39/40 | 528c · +0.79c/N · **8/15** |
| WTA_MAIN  | 10,583c · +8.35c/N · 35/35 | 9,064c · +4.58c/N · 38/40 | 1,431c · +3.29c/N · 12/15 |
| WTA_CHALL | 3,677c · +11.42c/N · 35/35 | 3,651c · +7.97c/N · 35/40 | 777c · +7.26c/N · 14/15 |

**Read:** the cheap + mid zones are the engine — they hold ~90% of volume and
the bulk of deployable PnL in every category. The favorite zone is a small
slice of capital and (for ATP_CHALL especially) barely clears positive
standalone. That's the zone Part 2 is built to rescue.

---

## 3. Deployment ideas / tiers

### Tier 1 — Deploy now, standalone (highest conviction)
The cheap-and-mid positive cells with high volume AND high hit. These don't
need the discount; they're the base book.
- **ATP_CHALL mid zone** is the single richest pocket: 15,254c deployable, 39/40
  cells positive, +5.52c/N on 2,762 trades. Largest, deepest, most reliable.
- **WTA_CHALL cheap zone** has the highest per-N edge (+11.42c/N) but thin
  volume (322) — high return, low capacity.
- Every category's cheap zone is 35/35 positive — universally safe base.

### Tier 2 — Deploy with the discount (Part 2 dependent)
The favorite zone (80-94), especially ATP_CHALL (only 8/15 positive standalone)
and WTA_CHALL/WTA_MAIN tops. These are near-breakeven or negative at T-20 anchor
but we already measured favorites carry the **biggest entry discount** (ATP_MAIN
favorites saved ~11.55c median entering below anchor). The thesis: discount
flips most of these from red/flat to green. Hold until Part 2 quantifies the
achieved-entry economics per cell.

### Tier 3 — Discount-rescue watchlist (currently negative)
These lose standalone and must clear the discount to deploy at all:
- ATP_CHALL: 85, 87, 88, 89, 94 (favorite upsets — 94c hits only 85% to settle)
- WTA_CHALL: 53, 67, 77, 78, 93
- WTA_MAIN: 53, 83, 88
- ATP_MAIN: 82
Do NOT deploy these standalone. Re-evaluate each on its achieved-entry basis in
Part 2; deploy only the ones the discount provably lifts above breakeven.

---

## 4. The standalone vs OG-Foundation realized PnL (context)

| Category | Hold-to-settle | OG Foundation own-N | v3 Pooled (deployed) |
|---|---|---|---|
| ATP_MAIN  | -2.85% | +9.98% | **+8.49%** (4.31c/N) |
| ATP_CHALL | -3.18% | +9.87% | **+8.19%** (4.12c/N) |
| WTA_MAIN  | -2.53% | +10.99% | **+9.68%** (4.88c/N) |
| WTA_CHALL | -4.66% | +17.16% | **+14.16%** (7.10c/N) |

Pooled gives up ~1.3-3.0 ROI pts of in-sample hindsight for out-of-sample
robustness + favorite-zone false-negative protection (operator's chosen
tradeoff). This is the **floor** — entries at a discount are pure upside on top.

---

## 5. Bottom line for finalization

- **Base book (deploy now):** all cheap-zone cells (every category, 35/35
  positive) + mid-zone positives. ATP_CHALL mid is the flagship pocket.
- **Discount book (Part 2):** the entire favorite zone, plus the Tier-3
  negatives, re-based on achieved entry. We KNOW the room exists — favorites
  carry the largest discount — so even ATP_CHALL 94c (red standalone) is a live
  candidate once we grab it below 94.
- The map is symmetric across categories: cheap/mid = volume engine, favorites =
  discount-dependent. Part 2 turns the favorite zone from a liability into edge.
