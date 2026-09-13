# Light decision-engine LAB

Scope: face only. The operator-selected light three-column sample is the LAB
implementation: side chart / shared decision engine / side chart; pressure
chain beneath. The sample supplies layout, not frozen data. No engine edits,
replay, conduct changes, regrading or feature experiments were performed.

## Source contract

Existing five face/grade/oracle files and index remain byte-identical to the
parent commit. The only changed game assets are source-bound pressure
projections rebuilt from their existing local receipt stages. FIELDS.md
documents every addition. No raw prints, books, API objects or stage streams
are included. Static build excludes 11,710 detail files (2,370,998,610 bytes).

The center shows the current recorded call independently of the call that
last set a bid's price and the later fill. Same-price renewals do not rewrite
that price-setting lineage. Fill hover keeps four stored English lines;
original assumptions/renewals/placing sentences remain in Details. Price age
is distinguished from order-lineage age.

Pressure-chain measurements not bound to these five games remain missing.
Trade volume and book size are real receipt readings, not implied absorption.
STEP price/volume factors are labeled last-checkpoint medians and watch-only;
an invalid stored validity status displays not rated, never a percentage.

Canonical corrected face clocks and receipt indices govern carrying. The
builder does not re-convert simultaneous receipt times or add an epsilon.
Timeline fill markers jump to the exact fill receipt. Fills draw above dense
renewal markers, preserving pointer and keyboard access.

## Verification

- `node --test window1-watch/test_light_lab.mjs`: all five source bindings,
  fill/price-setting lineage, causal read timestamps, canonical receipt clocks,
  missing-feature preservation, same-price holds and cancellation lineage.
- `npm run typecheck` and `npm run build:demo`: pass. Existing bundle-size
  warning remains; build is the static-only configuration, not server build.
- `node scripts/light-lab-proof.mjs`: five games, two charts each, recorded
  floors, perfect-sentence and call paths, no jargon on the default surface,
  source-bound pressure data, desktop/mobile overflow and header overlap,
  exact fill navigation, four-line fill card, Details, DESK and SCOREBOARD.
  Numerical results and screenshots are in LIGHT_LAB_LOCAL_PROOF.json.
- At T - 8hr 0 min: ALT bid-setting call/fill 60/60; GAS call/bid 38/38,
  not yet filled. Current calls 61/38.
- At T - 2hr 49 min: current calls 61/37, but bid-setting calls/fills
  60/60 and 38/38. Final pair 98, captured 2 of 4, grade C; recorded floors
  58/38. ALT's 60 price stood 6.09 minutes before its fill.
- Deployment uses the existing production-branch integration. Hosted proof
  is run against the production alias after it points at this commit.

Unchanged SHA256 pins:

| File | SHA256 |
|---|---|
| window1_v54_dual_belief_os.js | 70b68856cb4f0329048f9ae951e01c19c7d7465e3cc0ee183e325ce6c1fb0346 |
| window1_v54_functionable_os.js | 83f44682de821f754e99ecfdc0b56fd4ac8a03d65b0ee986f39c47f7df4e6c74 |
| build_window1_v54_dual_belief.js | 6136c8ca9cd2b6742f7a6235a27169cdc97b6b6543368a29d08f18c3185f5a8c |

Pre-existing package-lock and face_contract edits are not part of this change.
No scientific test from the accompanying design debate was started; proposed
effect-size bars in that debate are proposals, not an amended filed criterion.
