# RULING — STALE-PRINT ANCHOR ALLOWANCE for unlock-qualified ITF books (operator, 2026-07-10 early; the threshold ruling C-TAPE-SEED's close-out named)

## The ruling, as dispatched

> For events with an OPEN early-unlock (realized ≥2,500, ITF only), the anchor freshness allowance is **7,200 s**; all non-unlock tickers keep **1,800 s** unchanged. Never-traded books still skip. No BBO-mid fallback — the discipline stands; only the allowance widens where volume qualifies the book.

## Lineage
- **C-TAPE-SEED (07-10)** ended with: honest ages proved every unlock-qualified exhibit leg's true print sat 35–120 min old — ">30-min skip = an operator ruling on the threshold, never a code fix." This is that ruling.
- **RULING_EARLY_UNLOCK (07-09)** — the unlock predicate this allowance keys on (realized ≥ staged floor, ITF only, never projected).
- The last-trade discipline (three observable prices; no constructed mids) is UNTOUCHED — a stale print is still a print; a book with no print still skips.

## Operationalization (C-STALE-ANCHOR-ALLOWANCE)
- Per-ticker threshold resolution at the anchor gate: unlock-open event → `early_unlock_anchor_age_sec` (config, 7,200); everything else → `V4_LAST_TRADE_MAX_AGE_SEC` (1,800, unchanged constant).
- Every buy stamps `anchor_age_sec` (age at resolution) alongside `tape_basis`; daily_ledger splits the tape-basis cohorts by anchor-age band (fresh ≤1,800 vs stale-allowance >1,800) so the stale-anchor cohort's fill rate and Δaim grade against the fresh cohort before anyone trusts it.
- Watches: `tape_seed_live_confirm` delta distribution vs anchor age · stale-anchor cohort fill rate + Δaim vs fresh-anchor cohort.
