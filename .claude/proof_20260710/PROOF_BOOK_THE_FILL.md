# OUTCOME PROOF (C46, two-lane) — C-BOOK-THE-FILL (the −0f healer + the −0c cancel-race fix; CLASS — UNBOOKED FILL's closing design)

**Candidate SHA: `86c0a23d`** (post-rebase; the code commit's content = 070d2b5b: live_v4.py audit healer + resolver hold, gun_scorecard HALT-MIN/UNBOOKED footer, CLASS_LEDGER entry).

## Prior art (C45)
- **CLASS — UNBOOKED FILL (CLASS_LEDGER.md, added first per the dispatch)** — 13 tickers July 10, 5 halts, 276.8 min downtime; parents TUPMAK 07-09 11:24 pm + GHASPI recurrences.
- **C-RIDE-LIVE-RACE-FIX (06-13) / `_v4_reconcile_naked`** — the proven booking path this healer routes through (books via `_book_v4_entry_fill`, posts the native band exit — existing policy, §0A unchanged).
- **C-P0-RACE `_cancel_entry_and_resolve`** — the resolver whose "cancelled" verdict ignored `ok=False` with the order still live: TUPMAK's fill landed 6 s after the poll; the caller placed 45dfd41b; conception_on_owned halted 10 min.
- **C-ORPHAN-FINGERPRINT** — the lineage register that decides booked-vs-halted (a fill OUR order lineage explains is booked; no lineage → the halt stands).
- **REPLAY-HARNESS LAW (LIFECYCLE.md, binding)** — satisfied below.

## LANE 1 — MECHANISM (replay-harness law: fails before, passes after)
**FAIL-BEFORE, on tape and re-run:** the recorded halts ARE the before (GHASPI 12:22:23 pm no_exit → 7.5 min halt; 1:31:59 pm recurrence; TUPMAK 07-09 11:24:12 cancel success=false → replacement placed → 10-min halt). Additionally the harness accidentally ran once against the OLD code still on the VPS and reproduced the exact FAIL on the same recorded inputs (verdict FAIL, no_exit GHASPI-SPI) — the fail-before demonstrated live. (That run also exposed that the audit writes+commits halt artifacts even under test — three junk artifacts purged, the harness now runs pre-halted so the side-effect path never fires.)
**PASS-AFTER (4/4 on `86c0a23d`):**
1. GHASPI recorded state (held 5, no exit, our buy fingerprint @24) → **BOOKED** via `_v4_reconcile_naked` (basis 24 = exposure/qty), flag `unbooked_fill_booked`, **audit PASS, NO HALT**, `fill_booked_reconcile` logged with lineage.
2. Same holding WITHOUT lineage → `no_exit` failure **stands** — the halt remains for genuinely unexplained holdings.
3. TUPMAK recorded state (cancel `success=false`, order live, fill not yet visible) → resolver returns **"unresolved"** + `cancel_failed_hold` → the caller ABORTS the replacement. The race dies at its source.
4. Confirmed cancel → "cancelled" — the repost path is byte-identical when the cancel actually succeeds.

## LANE 2 — SETTLEMENT P&L
$0 claimed. The healer posts the same native band exit the fill should have received (§0A unchanged); the resolver refuses a duplicate placement.

## Regression watches (Part 4 — the KILLED claim is zeros nightly, or the class reopens itself)
Scorecard footer now prints **HALT-MIN** and **UNBOOKED-FILLS-BOOKED** beside BELLS-MISSING · `cancel_failed_hold` occurrences (each = a caught race) · `fill_book_error` stays absent · `conception_on_owned` failures stay 0.
