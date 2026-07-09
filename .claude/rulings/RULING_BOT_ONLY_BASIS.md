# RULING — BOT-ONLY BASIS (operator, 2026-07-09; supersedes nothing — names the frame every P&L read already owed)

## The operator's words, verbatim

> "FRAMAR is my manual. its to shake you up. just pay attention to bot only. the money that is traded on the bot is our basis.. every day at midnight its reset. thats how we gage true pnl without confusion."

## Operationalization (this build, C-BOT-ONLY-BASIS)

1. **The bot's traded money is THE basis.** Manual/foreign positions on the shared account (the reconciler's `reconcile_orphan_no_cell` class — no cell config, not a market the bot routes) are **flagged and named, never blended** into any P&L line, position grade, book count, or status read.
2. **The basis resets at 12:00 am Eastern, nightly.** True daily P&L = measured from that reset, bot-only.
3. **C47 audit semantics:** a foreign ticker held on the account is `foreign_position` — a **FLAG (visibility), never a FAIL, never a conception halt, never a self-clear deadlock**. The 07-09 4:07 pm FRAMAR sequence (external taker buy → `no_exit` FAIL → 40-minute halt that could never clear itself) is the proof case this closes. Every naked-leg/exit protection stays fully in force for BOT legs.
4. **Renderers inherit:** nightly ledger + day-close headline P&L are bot-only, anchored at the midnight-ET reset; manual/foreign book is a named side column when present; the settlement-vocabulary columns (cashed-via-exit ∥ rode-to-settlement) live inside the bot-only frame; dynamic-floor/combined-clause rendering untouched.
5. **The reconciliation identity (−1a000 spec, amended):** account-snapshot Δ = **bot-only P&L + manual book Δ + fees**, closing to cents, bot-only as the headline. Anchored account-delta lines (e.g. the +$17.90/25h) are hereby the CROSS-CHECK, never the answer.
6. **Manual-book actions are the operator's.** The bot (and CC) does not manage, exit, or hedge manual positions absent explicit word; any containment action taken on one is logged manual-class and surfaced for the operator to keep or unwind. (The 07-09 containment sell `7cf55a8c` was cancelled under this ruling — the FRAMAR book is his.)

Day-boundary note (flagged per the dispatch): the gun scorecard/analysis windows use a 6:00 pm-ET prior-day cut (`day0 − 6h`) for OVERNIGHT-WAVE grading; that is a grading window, not a P&L basis, and does not collide with the midnight-ET reset. No existing renderer carried a competing P&L day-boundary before this build.
