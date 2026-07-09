# OUTCOME PROOF (C46, two-lane) — C-BOT-ONLY-BASIS (operator ruling + BOARD −2a foreign-position fix, one gated deploy)

**Candidate SHA: cited in the deploy record** (live_v4.py audit-scope fix + analysis/daily_ledger.py + RULING_BOT_ONLY_BASIS.md; no order-path change beyond flag semantics; the one manual-book cancel is direct-API, outside bot code).

## Prior art (C45)
- **FOREIGN-POSITION INCIDENT (vault 07-09 4:07→4:47 pm)** — the proof case: external taker buy `a500c5e9` (250sh KXWCGAME-26JUL09FRAMAR-MAR) → C47 `no_exit` FAIL → 40-min conception halt that could never self-clear; contained by resting sell `7cf55a8c`. This build makes the class structurally halt-proof and executes the operator's ruling on it.
- **RECONCILIATION (07-09 ~3:20 pm)** — the underdetermined cash convention; this ruling supplies the identity's FRAME (bot-only headline, manual Δ a named term); the −1a000 derivation stays queued.
- **SETTLEMENT VOCABULARY ruling (07-09)** — cashed-via-exit ∥ rode columns; `daily_ledger.py` inherits them inside the bot-only frame.
- **`reconcile_orphan_no_cell` (existing reconciler class)** — already names foreign tickers and refuses adoption; the audit now consumes the same predicate (`get_category is None`) instead of failing on the class.
- **C47 v1.2 assert-and-halt + OPERATOR REPORTING LAW (ET 12-hour) + CATEGORY LAW** — all inherited; every bot-leg assertion (buy_stack, cycle_cap_breach, conception_on_owned, no_exit, exit_qty, post-fire, fingerprint) unchanged for BOT legs.

## LANE 1 — MECHANISM (today's 4:07 pm sequence replayed under the fix)
- **The replay:** an external buy lands on a no-cell ticker → reconciler logs `reconcile_orphan_no_cell` and refuses adoption (unchanged) → the audit reaches the ticker, `get_category(tk) is None` → **`foreign_position` FLAG appended, row marked, `continue`** — no failure, no `conception_halt_armed`, no self-clear deadlock. Under the old code the same input produced `no_exit` FAIL + a 40-minute halt (observed live today).
- **Live confirmation is the deploy itself:** FRAMAR is still held on the account; after the gated restart the boot audit must print `foreign_position` in flags with verdict PASS — and again after the containment sell is cancelled (held-with-no-exit, the exact 4:07 pm state). Recorded in the close-out.
- **Byte-identity:** tickers with a category (every bot leg) take the identical code path — the new block is a no-op for them. No other order-path change.
- **Renderer:** `daily_ledger.py` is new, read-only over jsonl; midnight-ET anchor checked against existing day-boundary logic (the scorecard's −6h cut is a grading window, not a P&L basis — flagged in the ruling file; no collision).

## LANE 2 — SETTLEMENT P&L
$0 claimed. The cancel of `7cf55a8c` touches the operator's manual book (noted, not claimed, logged manual-class). The ledger renderer measures; it does not trade.

## Regression watches
`foreign_position` flag present (never a failure) while FRAMAR is held · `conception_halt_armed` must NOT fire on foreign tickers · bot-leg failure checks still fire on seeded violations (unchanged code path) · daily_ledger.py bot-only totals exclude foreign by construction · exit_checker exempt line covers the manual book.
