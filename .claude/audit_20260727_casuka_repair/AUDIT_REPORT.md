# INDEPENDENT AUDIT — CASUKA LIVE-SAFETY REPAIR @ 94be4113 — RULING: PASS (one named baseline note)

**PASS. All three repairs (D1 exit-intent serialization, D2 sell-side exchange-truth clamp, D3 pair-classifier truth) verify under 21/21 auditor-authored adversarial probes plus the 12/12 focused fixtures in clean checkouts; both organ orderings converge to exactly one lawful five-lot exit; the sell clamp fails closed on every probed path and never gates buys; FARRIU/VEGKAW-class false flags are eliminated while genuine fills classify correctly; the complete script census shows EXACT parity — the parent's 38 historical failures reproduce with identical identities and identical failure-cause signatures, zero regressions, and the only delta is the new passing suite. All hashes verify; no deployment, live access, or T2 change occurred. One accuracy note on the claimed baseline identity is named below and must ride into the deployment ceremony.**

Date: 2026-07-27 · Branch: `audit/window1-independent` · Additions-only child of `b442908f3b253d1e13d5b2a5e93c3dbf0491320d` · Auditor: independent CC session
Under audit: `94be41137c0b64bfa448546c8bc3ee7c4ae32a60` on `codex/casuka-live-safety-repair`, parent exactly `a4996dd00e82ed3534f97a09251697f1d82dbbab`.

## 1. Lineage and containment — PASS

Parent exact; remote `codex/casuka-live-safety-repair` = 94be4113; clean worktree at checkout. Scope is precisely **1 modified file (`arb-executor/live_v4.py`, +359/−19) plus 10 additive test/receipt files** — no deployment, config, state, strategy, research, or T2 file. (a4996dd0 has a second child, `3a476b5c` — an unrelated Jul-22 ops commit on another branch; 94be4113 is the sole child on the repair branch.) Control bindings verify: my audit report blob `c31f208e…` and repair-packet blob `cd41db2e…` at `b442908f` match exactly.

## 2. Causal sequence and baseline — reproduced, with one named note

The repair's replay preserves the controlling sequence exactly (2-lot exit cancelled → lawful 5-lot heal → same-cycle stale top-up of 3 → oversell), and the committed `CASUKA_CAUSAL_REPLAY.json` values match my own harness run bit-for-bit. No exchange/retry/reporting explanation is substituted — the engine race remains the proven cause.

**Baseline note (accuracy, non-blocking):** the PRE_RUN claims the parent engine blob (`949f6995`) equals "the engine independently reproduced in the CASUKA audit." That blob equals the copy tracked in my audit *commit's tree* — but the **running engine I audited is blob `f1857199`** (P0 guard v1, VPS commit `eca101c6`). The repair parent is **two undeployed commits ahead** (P0 REAL-START GUARD v2+v3) with a 239-line divergence that is **entirely confined to entry-buy start-guard surfaces**; a keyword scan of the inter-blob diff shows **zero hits** on the reconcile/exit/top-up/sell/pair-classifier surfaces, so the repair targets exactly the audited causal engine. Consequence: **deploying this repair also deploys P0 guards v2+v3** — the deployment ceremony must gate that explicitly (its outcome-proof must cover the P0 guards as well).

## 3. D1 — exit-intent serialization — PASS

Verified in the diff and by probe: a decorator brackets `reconcile()` with a per-ticker intent ledger; heals/consolidations record resets only when every cancel succeeded; posts raise a cycle floor; the stale `pos_map/ord_map` top-up is replaced by `_reconcile_exit_topup_from_truth`, which re-reads the authoritative paginated snapshot post-heal (and the chokepoint re-reads again). My probes: **heal→top-up → one 5-lot exit, top-up posts 0 with a named no-op receipt; top-up→heal → converges to the same single 5-lot; two consecutive cycles idempotent; conservation resting ≤ held holds.** Lawful heal behavior preserved (inherited suites pass).

## 4. D2 — sell-side exchange-truth clamp — PASS

The clamp is the final operation before every sell POST at the single submission chokepoint: fresh paginated positions (unsettled) + resting-sell census, repeated-cursor and missing/malformed truth fail closed, `new_sell ≤ max(0, position − max(resting, cycle_floor))`, refusal in full (never clipped) with `sell_exchange_truth_refused` receipt + operator alert. My probes: oversell 6-vs-5 refused with zero POSTs; exact-5 allowed; fully-covered refuses any sell; zero/negative refused; **fractional residue never rounds up**; zero-position refused; API-unavailable fails closed pre-submission; **the buy path is not gated** (it proceeds deep into pre-existing buy gates without the sell guard firing); refusals receipted. Buy-side, post-only, retry, exit, and quarantine laws untouched by the diff.

## 5. D3 — classifier truth — PASS

`filled` now requires booked `entry_qty > 0` **and** positive unsettled exchange holding; settled legs are named `settled`; probes confirm: zero-booked `entry_resting` → `absent` (FARRIU-RIU class), resting bid → `resting`, settled → `settled` (no pair flag possible), stale booked-but-no-holding → `absent` (VEGKAW-VEG class), genuine fill → `filled`, fitting-gap naming preserved.

## 6–7. Fixtures and tests — PASS

All five controlling acceptance fixtures from the frozen EXECUTION_REPAIR_PACKET reproduce (F1 heal-then-topup 0-post, F2 covered-position refusal, F3 oversell clamp, F4 settled/entry-resting classifier, F5 full CASUKA regression → exactly one 5-lot, resting ≤ held). Clean-checkout runs: **12/12 focused; 7/7 relevant inherited suites** (`lane_a_live_safety`, `lane_a_review_fixes`, `order_v2`, `bbo_settlement_gate`, `shutdown`, `monotonic_cut`, `fv_quote`); deployment AST lint PASS (flake8 absent, as disclosed); `py_compile` PASS.

## 8. 38-failure parity — PASS (independently reproduced)

In my own clean environment, script-by-script census: **parent 46/84 pass with 38 failures; child 47/85 pass with the SAME 38 failures — identical file identities, identical failure-cause signatures (0 diffs), zero formerly-passing tests now failing, and the single new file (`test_casuka_live_safety_repair.py`) passing.** The claimed parity verifies exactly.

## 9. Hashes and committed-code provenance — PASS

Both source byte-SHA256s and git blob OIDs match the manifest (`live_v4.py` → `1809085d`, tests → `8287d4a5`); all 8 artifact-manifest rows verify; the parent/audit blob claims verify against git; all receipts reproduce from clean-checkout committed code (my reruns regenerate the same outcomes, and the replay receipt matches my independent harness run).

## 10. Non-action and T2 — PASS

The running engine is untouched: same PID 2241929 (boot Jul 25 00:12:01), same blob `f1857199`, no restart, no deployment, no order/position/halt action (this audit performed none either). The T2 research worktree stands exactly at **`87ac9382c23b586f536cf457883c507ebf366ba3` with a clean status**. The forbidden-access receipt is corroborated.

## RULING

**PASS.** This authorizes **only** the construction of a separately gated deployment package and the standard deployment ceremony (`deploy/deploy_live_v4.sh`: lint + smoke + prior-art + outcome-proof) — **not deployment itself**. The ceremony must (a) run the smoke replay the clean worktree could not (no `premarket_ticks` corpus — disclosed), and (b) explicitly account for the fact that this deploy also activates the undeployed P0 REAL-START GUARD v2+v3 riding below the repair.
