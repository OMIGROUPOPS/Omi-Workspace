# Pre-staged morning validation — 2026-07-05 (the five-flag stack's TRUE first night)

**Window:** e422055 boot **18:27:55 ET Jul 4** (epoch 1783204075) → morning. Log:
`logs/live_v3_20260704.jsonl` (contains 3 boots today — the ledger BOOT_LIVE filter is set;
fills before 18:27 ET belong to earlier builds).

**Build under test:** e422055 = ba08243 flags + 775dac33 `_sibling_ticker` hotfix +
paper-v2 fix + error tripwire. All five flags armed: per_cat_depth, leg2_reshuffle,
premarket_walk_cap, match_live_grace_kill, latch_tape_override. Deployed THROUGH the gate
(lint PASS + smoke PASS 21k states / 11.7k dog evals / 169 paper orders / 0 errors).

## One-shot commands (on VPS, from /root/Omi-Workspace/arb-executor)

```bash
# 1. Metric A/B  (Metric A MUST be 0 on this build — no crash excuse remains)
python3 ../.claude/aim_dispatch_20260703/validate_latch_grace.py logs/live_v3_20260704.jsonl

# 2. Regression census vs last night + hourly (scripts are in git, not /tmp)
python3 ../.claude/overnight_20260704/regress_census.py logs/live_v3_20260703.jsonl logs/live_v3_20260704.jsonl
python3 ../.claude/overnight_20260704/hourly_regress.py logs/live_v3_20260704.jsonl

# 3. Ledger (writes /tmp/on3_*)
python3 ../.claude/overnight_20260705/on3_ledger.py logs/live_v3_20260704.jsonl 1783204075
# then grade locally: python grade2.py against on3_dump.json (edit path)

# 4. Tripwire check (must NOT exist unless something broke)
ls -la /tmp/live_v4_TRIPWIRE.json 2>/dev/null || echo "tripwire quiet"
```

## Pass bars and baselines

| metric | bar / baseline |
|---|---|
| Metric A (fills past gun+300s, latched) | **0** — hard bar, no crash excuse |
| Metric B latches | ≥ 22 (prior baseline); override latches expected; spot-check 3+ for real matches |
| error-class log events | **0** (`error`, `on_bbo_update_error`); tripwire artifact absent |
| fills | vs 149 (Jul-2 night, healthy) — NOT vs 20 (crash night) |
| pairs completed | vs 57 healthy baseline |
| half-arm rate | vs **28%** healthy baseline (crash night's 75% is void) |
| over-par completions | 0 (held from ceiling+walk_cap; prior healthy night had 15) |
| FV_capture | vs +1.3c mean / 61% pos healthy baseline |
| in-play chase rate | vs 57% healthy baseline |
| leg2_reshuffle_reaim | FIRST real fire count — inspect each: to ≤ combined_goal − leg1_basis |
| per_cat_depth | dog fills paid-by-dip % vs 68% ATP baseline |
| premarket_walk_capped | each fire: target clamped to conception+cap, no liquid-repost conflict |
| freeze_at_gun_hold | 0 (shelved) |
| ITF stale-book watch | books >1h stale on a HEALTHY loop = new incident, escalate |

Named classes per game (A–F grading, grade2.py): over-par / par-zero-lock / deep-neg-FV /
in-play chase / half-arm (STARVATION vs PAIRING) — count vs the Jul-2 healthy night, not
the crash night.
