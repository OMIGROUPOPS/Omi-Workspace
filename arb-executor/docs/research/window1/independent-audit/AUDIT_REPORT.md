# Window-1 Independent Reproduction & Adversarial Audit (CC)

Read-only. Run separately from `codex/window1-definition`. No raw identities, account data,
or credentials are committed. All numbers are aggregate. Source evidence: frozen normalized
dir, immutable `live_v3` engine logs, Codex export/join artifacts, and authorized read-only
GET queries (tier probe).

## Product 1 — Independent lifecycle evidence census

Unit = **game/leg lifecycle** (reposts collapsed by conception/trade/leg lineage), not repost IDs.
`D = 804` (events.jsonl = 804, every event has exactly 2 legs). Fills = 903 complete private
fill receipts. Orders (repost legs) = 9,447.

Game-level classification (FILL requires a complete private fill receipt; NONFILL requires the
full evidence conjunction — confirmed terminal/no-placement with zero fills; ambiguous → CENSORED,
kept in D):

| Class | Count |
|---|---:|
| D (denominator games) | 804 |
| C — dual 5×5 capture (both legs filled ≥5) | 39 |
| P — partial (exactly one leg filled) | 226 |
| N — nonfill (both legs confirmed nonfill/no-placement) | 441 |
| I — censored (ambiguous; incl. the 703 unconfirmed accepted orders) | 98 |

Sum 39+226+441+98 = 804 (D immutable). Leg-level: FILL 304, PARTIAL 9, NONFILL 362,
NO-PLACEMENT 643, CENSORED 290.

**Dual 5×5 capture rate vs ≥75% objective:** lower **4.9%** (39/804, censored = non-capture),
upper **17.0%** ((39+98)/804, censored all-capture). **Far below the ≥75% objective** under a
receipt-based, censored-bounded reading. (The rate is sensitive to the denominator definition;
against full immutable D it is 5–17%.)

**Captured-game economics (par and delta reported separately, not conflated):** 39 priced
captured games; combined cost min 90¢ / p50 97¢ / max 102¢; **33/39 under 100¢**; 3 games cost
>100¢ (negative edge). Per-leg average fill prices are computed per game (not committed raw).

Pagination completeness (from Codex export receipt + diagnostics, independently read): live
orders/fills paginated to empty cursor, 0 request errors, 0 cursor cycles; `matched_exchange_fills`
= 903 (equals my fill count).

## Product 2 — Depth-pressure integrity audit

**Full-depth and prints are ABSENT for Window-1.** `books.jsonl` = **0 rows**
("full-ladder July archives absent or rotated before integrity validation"); `prints.jsonl`
= **0 rows** ("subsecond source lacks exchange receipt identity; no true prints admitted").
`tennis.db.book_prices` is a **fair-value/odds** table (event_ticker, book_pN_fv_cents, raw_odds,
vig) — **no bid/ask ladder, no per-market BBO, no depth**.

**Verdict:** the depth-pressure enhancement (distance-weighted imbalance, persistence, add/cancel
flow, absorption, depletion, replenishment, 5-contract executable depth) is **unsubstantiable for
Window-1 — the underlying order-book microstructure data does not exist in the frozen evidence.**
There is no full-depth to compare against a BBO+prints baseline, and no admitted prints either;
both baselines are degraded to absent. Any full-depth "enhancement" claim over Window-1 cannot be
validated.

## Falsification results

| Failure mode | Verdict | Evidence |
|---|---|---|
| queue position inferred from aggregate depth | N/A (unfalsifiable) | no depth data exists |
| same-price print counted as a fill | not present | prints=0; fills = 903 receipts only |
| zero/missing size promoted to volume | passes | 0 zero/neg-size fills (min 0.01) |
| tape/WS/transition duplicates | passes | 903/903 unique fill_ids, 0 dup receipts |
| Yes/No complementary books double-counted | passes | 0 trade_ids span >1 ticker |
| missing depth removes games from D | passes | D=804 intact despite books=0 |
| par vs delta conflated | passes | reported separately (cost vs 100−cost) |
| repost IDs counted as independent decisions | passes | census collapses to game/leg; 703 = repost legs of 375 trades |
| **schedule substituted for verified real start** | **PRESENT** | all 717 evaluation edges = `scheduled_start+60m`; only **40/804** events have a verified start; schedule_source = exchange occurrence_datetime for all 804 |
| depth walls disappear before execution | N/A (unfalsifiable) | no depth data |
| policy selection after holdout inspection | not performed here | census is measurement only |

## Review of Codex commits (reproduced independently)

- **`39968b50` tier reconciliation** — reproduced: 703 target set; exclusive lifecycle partition
  671 (successful cancel) + 4 (terminal cancel-fail) + 28 (never-cancelled) = 703, plus 198
  orphan/re-adopted and 1 immediate-fill; all sampled targets 404 on exact live lookup; absent
  from paginated live and historical; controls found live; cutoff **2026-05-24** → July orders are
  live-partition (historical cannot hold them); raw 201 bodies/exact status not preserved. **Agree.**
- **`d882e340` identity bridge** — reproduced: tier1/tier2/tier3 join = 0/0/0, **703 unresolved**,
  46 time-incompatible composite candidates (0 valid unique recoveries). **Agree.**
  Minor flag: `exchange_accepted_response_corroborated: 703` is engine-side corroboration; the
  raw 201 is not preserved (Codex's own tier-recon states this) — the label overstates certainty.

## Independent verdict

- `D=804` immutable — **reproduced.**
- Unit = game/leg, reposts collapsed — **reproduced** (703 = repost legs of 375 trades).
- 703 unresolved by exact id and by unique composite; absent from live and (per May-24 cutoff)
  ineligible for historical — **reproduced, agree with Codex.**
- 703 correctly **CENSORED** (ambiguous), remain in D — **agree.**
- Dual 5×5 capture is **4.9–17%**, far below the ≥75% objective (my methodology; denominator-sensitive).
- Depth-pressure enhancement is **unsubstantiable** — no order-book depth/prints exist for Window-1.
- Material integrity defect: **evaluation edges are schedule-derived for ~95% of games** (verified
  real start for only 40/804) — the same schedule-vs-real-start hazard the P0 guard targeted.
