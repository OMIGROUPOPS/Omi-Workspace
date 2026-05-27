# v6 position exit re-post — bringing open positions to v6 R — 2026-05-27

The v6 deploy preserved **old R** on existing positions (reconcile *adopts* existing resting sells), so the old-R / +1c-trap exits were still resting. This brings all open positions' exits to **v6 R** (entry + v6 band R, cap 98). Live order operations on the real-money account.

## Final state (verified)
**36 open positions · 36 resting sells · 0 duplicate sells (no over-exposure) · 0 naked · 0 mismatched (all at v6 R) · 0 unmanaged/orphans · 0 tracebacks.**

## Method (and a correction mid-execution)
1. **Cancelled 22** mismatched old-R sells (http 200 each). Plan was: let the bot's v6-aware reconcile re-post each at v6 R (single writer = no double-sell).
2. **The bot re-posted only ~5.** Discovered the bot's `_v4_reconcile_naked` only re-posts naked positions whose **event is still in its active schedule**; for in-play / older matches it skips. → ~24 positions were left **naked (no exit)**.
3. **Posted v6-R exits on all 24 naked positions myself** (http 201 each, `post_only` maker, fresh-check per ticker → 0 duplicates). Safe now: the bot had its reconcile pass and isn't re-posting these, so no two-writer race.

**Why not cancel+repost atomically from the start:** two writers (me + the bot's reconcile both posting) can collide in the cancel→repost gap and create duplicate sells = naked short / over-exposure. Cancel-only avoided that but under-reposted; the corrected approach (cancel → let bot try → post the remainder myself once the bot is provably idle on them) kept duplicate-sells at **0** throughout.

## Cancels (22) — old-R sell → v6 R target
DUC e6→old38→v6R63@69 · JOV e53→85→R11@64 · MER e66→85→R20@86 · PAO e64→98→R33@97 · PUT e43→96→R4@47 · OSO e58→95→R8@66 · RAK e11→18→R46@57 · MUC e90→97→R5@95 · RIN e49→57→R3@52 · BER e52→90→R11@63 · TEI e41→77→R31@72 · LYS e22→65→R45@67 · BOU e21→64→R33@54 · POT e80→87→R11@91 · KES e23→58→R45@68 · MIC e64→98→R8@72 · HUR e58→77→R18@76 · MAC e15→57→R6@21 · SON e16→20→R6@22 · YIB e28→98→R3@31 · MED e31→35→R12@43 · GAS e12→29→R6@18

## Re-posts (24 — the 22 above re-created + DED, BAD that were already naked)
All posted `post_only` sell, qty 5, at entry+v6_R (cap 98), http 201:
DED@93 · DUC@69 · BAD@65 · JOV@64 · MER@86 · PAO@97 · PUT@47 · OSO@66 · RAK@57 · MUC@95 · RIN@52 · BER@63 · TEI@72 · LYS@67 · BOU@54 · POT@91 · KES@68 · MIC@72 · HUR@76 · MAC@21 · SON@22 · YIB@31 · MED@43 · GAS@18

## Notes
- **Bot still running** (PID unchanged), v6 tables live, 0 tracebacks, 0 duplicate sells.
- New entries continue to get v6 R from `_v4_apply_exit` at fill (already correct). This was a one-time correction of the *pre-existing* positions the deploy had adopted at old R.
- **Standing item:** the bot's reconcile won't re-post naked positions for out-of-schedule (in-play) events — any future exit-table swap needs this manual repost step for already-open positions, or a code change so reconcile re-resolves adopted exits to the current table.
- Caveat carried: v6 R is raw_max-optimistic vs the prior size_qual model.

*Live order operations (cancel ×22, post ×24) on the real-money account, operator-authorized. Final state verified: 0 duplicates, 0 naked, all v6 R.*
