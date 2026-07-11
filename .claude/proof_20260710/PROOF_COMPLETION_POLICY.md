# OUTCOME PROOF (C46, two-lane) — C-COMPLETION-POLICY v1 (−0h, fix-queue #1: 55 instances/$6.25 today, −$50.65 June; SHADOW, trades nothing)

**Candidate SHA: `490affa6`** (oslayer/leg_econ.py pure engine + _completion_shadow hook + config gates + COMPLETION-SHADOW nightly section).

## Prior art (C45)
- **CLASS — ADVERSE-SELECTION STRAND** (this is its closing design): June 93 priced/−$50.65 (COMPLETION_FUNNEL); July-10 55 instances/$6.25 (#1 in the ranked fix queue); the June verdict verbatim — cross to complete, or never hold the kept leg naked.
- **RULING_PAIR_ECONOMICS** — the replacement's binding frame, implemented as code: each leg an independent scalp, EV = P(exit-fills)×band − P(ride-zero)×basis; pair-97 consulted NOWHERE (constraint #11; DOCTRINE CONFLICT's interim clock now has its named bound shipping).
- **M15 RANGE LAYER** — the fitted surface pricing both probabilities per cell (cash/loss splits, WINDOW_MAP_3WAY axes); win-ride residual EXCLUDED from EV (conservative slack, named).
- **MIGRATION DOCTRINE** — shadow → nightly grade (COMPLETION-SHADOW section) → cutover on the operator's word → pair-97 DELETED.
- **oslayer boundary** — the engine is order-path-pure (gate-asserted).

## LANE 1 — MECHANISM
- **Part 4 (replay-harness law): today's 44 strands replayed through the engine — 44/44 produce a verdict AND a price.** Distribution: hold 21 · flatten_kept 18 · taker_complete 1 · NO-OPINION 4 (thin range cells, named — never a guess).
- Shadow hook: every one-sided pair, each check_fills pass (600s dedup/event): kept-leg EV + both branches logged (`completion_shadow`); branch (b) carries `taker_word: false` — it computes and logs its would-have-dones nightly and CANNOT act until the operator flips the word.
- No live behavior changes anywhere: the hook is log-only (never raises), the engine is pure, the taker branch is double-gated (verdict-only + word).

## LANE 2 — SETTLEMENT P&L
$0 claimed. The COMPLETION-SHADOW nightly section builds the cutover case on paper.

## Regression watches
completion_shadow lines/night per cat + verdict mix · taker_complete would-have-dones (the operator_taker_word evidence base) · flatten_kept would-have prices vs the actual strand outcomes (the June-mechanism check, nightly) · NO-OPINION share falls as range cells thicken.
