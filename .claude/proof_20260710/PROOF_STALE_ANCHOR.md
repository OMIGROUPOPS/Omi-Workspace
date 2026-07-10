# OUTCOME PROOF (C46, two-lane) — C-STALE-ANCHOR-ALLOWANCE (operator threshold ruling; config-scope)

**Candidate SHA: `dba7770c`** (live_v4.py per-ticker threshold resolution + anchor_age_sec stamp, config `early_unlock_anchor_age_sec: 7200`, daily_ledger band split, RULING_STALE_ANCHOR_ALLOWANCE.md).

## Prior art (C45)
- **C-TAPE-SEED close-out + PROOF_TAPE_SEED.md (tonight)** — ended with the exact sentence this executes: honest ages showed every unlock-qualified leg's true print 35–120 min old; ">30-min skip = an operator ruling on the threshold, never a code fix." This is that ruling, recorded first.
- **RULING_EARLY_UNLOCK.md** — the unlock predicate (realized ≥2,500, ITF only, never projected) this allowance keys on; same `_early_unlock_live` map, no second predicate invented.
- **The last-trade discipline** — UNTOUCHED: no BBO-mid fallback; never-traded books (lt_age = inf) still skip at ANY allowance; the 1,800s constant is not edited — non-unlock tickers take the identical old path.

## LANE 1 — MECHANISM
- **Per-ticker resolution at the single anchor gate** (`_v4_entry_anchor`): unlock-open event → 7,200s allowance; else 1,800s. One comparison bound moves, only where `_early_unlock_live` holds the event — the same map the placement-window unlock uses, so window and anchor widen/narrow together by construction.
- **Self-measuring:** every buy stamps `anchor_age_sec` (age at resolution) beside `tape_basis`; daily_ledger splits cohorts fresh (≤1,800) vs stale-allowance (>1,800) — the stale cohort's fill rate and Δaim grade against fresh before the allowance is trusted.
- **Live verification (close-out):** each unlock leg's admit/skip at the new allowance with its honest age, plus any placement lines that fire.

## LANE 2 — SETTLEMENT P&L
$0 claimed. The cohort split exists so the allowance's P&L is measured before it is claimed.

## Regression watches
Non-unlock skip lines keep 1,800s behavior (ages 1,800–7,200 on non-unlock tickers must still skip) · never-traded books never anchor · stale-anchor cohort fill rate + Δaim vs fresh · `tape_seed_live_confirm` delta vs anchor age (does an old print still tell the truth when the book wakes).
