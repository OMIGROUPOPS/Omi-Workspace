# OUTCOME PROOF (C46, two-lane) — C-TRUTH-JOIN (gun_scorecard truth-join debug, BOARD −2)

**Candidate SHA: `572d678a`** (analysis/gun_scorecard.py only — live_v4, order path, oslayer byte-untouched; rides the 6:10 AM VPS cron path, hence this gate run).

## Prior art (C45)
- **C-FUSED-GUN 6d84f27e + GUN SCORECARD tripwire (07-08)** — the renderer this debugs; its truth convention (te fires → tape onset; others → observed_starts) is the defect: 46/50 overnight fires never received truth.
- **Fire-class labeling (operator 07-08)** — CATCH-UP/FRESH split unchanged; the ±3-min pre-registered bar unchanged and still FRESH-only.
- **C-ANCHOR 1eeebc7b (lying-clock fix, 07-08)** — the anchor hierarchy + datemiss_36h machinery whose jsonl stamps (`clock_liar.te_honest_start`, `pm_clock_shadow.honest_start`) this join now consumes; the MOCTAN day-boundary class is the same class C-ANCHOR closed in the bot, now closed in the grader.
- **GRANULARITY LAW (ruling, 07-09)** — the training/certification bell split; the 349 recovered bells stay FORBIDDEN as truth (script never reads shape_corpus).
- **GUN_SCORECARD_20260709.md (6:10 AM)** — the exhibit night: ITF_M 1 graded at |Δ|=102.2m (MOCTAN), misses=[] everywhere, ESTAGU/SNIAND/VONZID half-joins.

## LANE 1 — MECHANISM (offline A/B on the VPS, same jsonl window, old vs new code, no --nightly side effects)
Full tables + exhibits: `.claude/gun_scorecard/TRUTH_JOIN_AB_20260709.md`.
- **Last night's 50 fires:** truth-disposition coverage 3/50 → **50/50** (7 clean-graded, 42 SUSPECT named with reasons, 1 UNJOINABLE named). Per cat: ATP_CHALL 0→0 clean (3 suspect) · ITF_M 3→4 (17 suspect, 1 unjoinable) · ITF_W 0→1 (18 suspect) · WTA_CHALL 0→2 (4 suspect).
- **Anchor census (full-day, 173 fires):** 165 joins centered on the honest datemiss-aware clock, 4 on schedule, 1 on fire-time — the MOCTAN class routes through the anchor path; MOCTAN itself now `SUSPECT(truth_predates_fresh_fire)`, excluded from the median it used to poison (old med|Δ| 168.4m → new ITF_M 8.3m / ITF_W 1.7m on clean FRESH).
- **Half-joins:** structurally impossible now — `tape_onset()` returns a reason; VONZID (old silent half) grades 0.5 min via `obs_starts(both-leg)`.
- **Miss path:** synthetic drop-one-fire (VONZID's fire removed) → `NO FIRE` row + `misses=[VONZID]`. Tonight's real `misses=[]` is true: all 8 observed_starts-joined events fired.
- **Byte-identity:** the bot's behavior is untouched; the ±3-min bar, fire-class rules, and vol30 column are unchanged; suspects cannot affect bar passes (≥15 min > ±3 min by construction).

## LANE 2 — SETTLEMENT P&L
$0 claimed. Measurement-only change; no order is placed or cancelled by this code.

## Regression watches
Tonight's 6:10 AM certification-night-3 render: every fire row must carry a disposition (truth / SUSPECT(reason) / UNJOINABLE(reason)); `misses` prints names when a truth-covered event has no fire; per-cat clean-graded counts and med|Δ| read from non-suspect FRESH only.
