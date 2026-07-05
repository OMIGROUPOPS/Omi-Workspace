# PART 1 SPEC — Plex's two preconditions, answered
**Engagement re-anchor · 2026-07-05 · branch blend/kalshi-occ-fallback**
Companion to `PLEX_REANCHOR_RULING.md` (reserved slot — verbatim body still owed by relay).
Everything below is verified against the running VPS and the repo at HEAD, not memory.

## Prior art (gate — added retroactively 2026-07-05 per PRIOR_ART_GATE.md / C45)
- Greps: `occurrence_datetime|expected_expiration|noon|schedule|start_time|coarse` over LESSONS.md, JUNE_VAULT.md(+APPENDIX), ROADMAP.md, .claude/rulings/, gated-flag inventory.
- Established (this spec RE-STATES, does not discover):
  - ROADMAP T51:211 / LESSONS §6 (2026-06-01): the Kalshi start fields are "frozen coarse placeholders — uniform noon-UTC"; T51_HARDENING_SPEC.md:8: the T-15 buffer fires at the wrong wall-clock off them.
  - C32 (2026-05-12): `expected_expiration_ts > settlement_ts`, 100% of probe.
  - Match-start-signal forensic (2026-06-19): `state/schedule.json` carries a per-match `status` the bot never reads; volume-burst cancel median +22min premature.
  - A35: volume/min is the cleanest match-start anchor (the gun's own prior art).
  - **Staged-but-never-armed prior build on this exact topic: C-KALSHI-OCC (`kalshi_occurrence_fallback`, June 30)** — the wide-envelope + tape-latch design whose envelope Part 1's fallback mode reuses. Gen-chain: JUNE_VAULT §0B.
- DELTA this spec adds: (1) the schedule.json schema FROZEN as a build target (crontab-verified `*/15`, 5 pinned warts — the ESPN `category` mislabel and `espn_midnight` semantics were not previously documented); (2) the staleness rule made explicit (45-min bar, HONEST/FILE-STALE/ENTRY-MISSING); (3) the per-category widening X quantified from the clock audit's offsets (CHALL 4h / ITF 7h / MAIN 8h, mains-negative skew direction); (4) the timing-only scope contract (clock never gates participation, never touches liveness — Gen-1's disease and Gen-3's regression both named and excluded).

---

## PRECONDITION 1 — THE TE/ESPN STATE FILE, FROZEN

### Path & refresh mechanism
- **File:** `/root/Omi-Workspace/arb-executor/state/schedule.json` (repo path `state/schedule.json`; `live_v4.py:239` `SCHEDULE_FILE = STATE_DIR / "schedule.json"`). Observed 2026-07-05 20:15 ET: 449,081 bytes, 2,256 entries, age 9.1 min.
- **Producer:** `refresh_schedule.py` via root crontab — **`*/15 * * * * cd /root/Omi-Workspace/arb-executor && python3 refresh_schedule.py >> /tmp/refresh_schedule.log 2>&1`** (verbatim, read from the VPS). ⚠ The file's own docstring says "every 30 minutes" — the **crontab is authoritative: 15 min**. Docstring drift noted, not fixed here (bot untouched).
- **Producer semantics:** fetches TennisExplorer (primary, ALL categories) + ESPN scoreboard (overlay, main draws only) for **today + tomorrow** (ET); tomorrow's entries never overwrite today's on key collision. Full-file rewrite via `json.dump(open(path,"w"))` — **NOT atomic** (no tmp+rename). A reader can catch a torn file; the consumer already handles this (below).
- **Consumer:** `live_v4.py` `_read_schedule_file()` (:1789) — parse errors → `schedule_error` + empty schedule; missing → `schedule_missing` + empty. Reload **every 5 min** in-bot (`DISCOVERY_INTERVAL`, :8676, parse off-loop). So worst-case honest-clock latency = 15 min (cron) + 5 min (reload) = **20 min**.

### Schema (FROZEN — the clock helper reads exactly this)
Top level:
```json
{"fetched_et": "2026-07-05 08:15:03 PM ET", "fetched_epoch": 1783123456.7,
 "today": "2026-07-05", "tomorrow": "2026-07-06", "count": 2256, "schedule": {…}}
```
`schedule` maps **6-char pair-code keys** (3+3 of surnames, BOTH orderings inserted, e.g. `SINMOC` and `MOCSIN` → same entry object) to:
```json
{"start_time": "2026-07-05T18:20Z",   // ISO-8601 UTC, minute precision, may omit seconds
 "status": "scheduled" | "live" | "completed",
 "p1": "...", "p2": "...", "tournament": "...",
 "category": "ATP_MAIN|WTA_MAIN|ATP_CHALL|WTA_CHALL",
 "source": "tennisexplorer" | "espn",
 "espn_midnight": true}                // OPTIONAL — present only on flagged placeholders
```
- `start_time` provenance: TE times are CET parsed → UTC; ESPN gives `startDate` directly. ESPN **overwrites** TE for main draws (better accuracy) EXCEPT when the ESPN time is the 00:00-ET placeholder.
- `status` provenance: TE inferred from set scores (≥2 total sets = completed, any set = live, none = scheduled); ESPN mapped from `state` (post/in/other). Live snapshot: 1,856 completed / 370 scheduled / 30 live.

### Frozen warts (the helper MUST honor these; anything fluid is now pinned)
1. **`category` is NOT trustworthy on ESPN entries** (observed live: Sinner–Mochizuki Wimbledon labeled `WTA_MAIN`; ESPN grouping quirk). The clock helper must key per-category behavior off the bot's own `get_category(ticker)`, **never** the schedule entry's `category`.
2. **`espn_midnight: true` = time placeholder** ("after previous match", 42 entries in the live snapshot). For clock purposes this entry is **MISSING** → fallback path.
3. **ITF coverage exists via TE** (the audit joined ITF_M/ITF_W at 16–17 distinct per-match times, zero duplicates) but **join misses ≈ 7%** (9/144 box events, player-code mismatches). A miss is an ENTRY-MISSING case, not an error.
4. **Non-atomic producer write** — a torn read surfaces as `schedule_error` (empty schedule for ≤5 min). Under the fallback rule this is FILE-STALE, handled, self-healing on next reload.
5. Both-ordering duplicate keys are the SAME object — dedupe by identity when counting, never iterate as if independent.

### What the honest anchor is worth (why this file, certified)
`CLOCK_AUDIT.md` (2026-07-05, 144-game box): the bot's current clock (`kalshi_schedule_primary` = Kalshi `expected_expiration_time`) is a **card/session marker** — hour-quantized, duplicated across the card, not a match time. schedule.json is per-match (zero ITF duplicates), and it independently certifies the tape gun on ITF/CHALL (gun−TE median +4..9m, 75% within ±30m) while convicting it on _MAIN. This file is the honest anchor; there is no per-match start anywhere in the Kalshi API surface for these series.

---

## PRECONDITION 2 — THE STALENESS FALLBACK, EXPLICIT

### Definitions (a clock lookup is exactly one of these)
- **HONEST:** schedule file loaded, `fetched_epoch` age ≤ **45 min** (3 missed cron cycles; normal is ≤15+ε), event joins an entry (direct 6-char or fuzzy-name — the EXISTING matcher, unchanged), entry has parseable `start_time`, and no `espn_midnight` flag.
- **FILE-STALE:** file missing / unparseable / `fetched_epoch` age > 45 min.
- **ENTRY-MISSING:** file fresh but no join for this event, or joined entry is `espn_midnight`, or `start_time` unparseable.

### The rule
> **FILE-STALE or ENTRY-MISSING → the event's window clock falls back to the Kalshi placeholder (`event_kalshi_occ` / `expected_expiration_time` — i.e., exactly today's `kalshi_schedule_primary` clock) and the entry window WIDENS by X per category, both edges: leading edge opens at placeholder − (240 min + X); late edge keeps coarse-envelope semantics (NO T-15/T-0 lock on the placeholder clock; give-up extended to placeholder + max(90 min, X)). The tape volume-burst/sustained latch — UNTOUCHED — remains the sole real-start governor.**

Fallback ≡ status quo + widening: today the bot runs 100% on the placeholder clock, so the fallback leg can never be worse than current behavior; the honest leg is the improvement.

### X per category — derived from the clock audit (kalshi − TE/ESPN offsets, n=135 joined)
| category | median skew | observed extreme | **proposed X** | derivation |
|---|---|---|---|---|
| ATP_CHALL | +110 min (n=82) | +175 min | **240 min (4 h)** | max obs + 60 min margin, rounded up to the hour |
| WTA_CHALL | +105 min (n=12) | +175 min | **240 min (4 h)** | same |
| ITF_M | +263 min (n=17) | +360 min | **420 min (7 h)** | same |
| ITF_W | +244 min (n=16) | +360 min | **420 min (7 h)** | same |
| ATP_MAIN | **−135 min** (n=4) | −105 min spot | **480 min (8 h)** | see note |
| WTA_MAIN | **−95 min** (n=4) | — | **480 min (8 h)** | see note |

- ITF/CHALL skew is POSITIVE (placeholder runs LATE): the widening that matters is the **leading edge** — without it, ITF windows "open" a median 24 min *after* the true start (the audit's "ITF has no premarket" finding, and the half_timing leak's mechanism). X covers the observed max +360 min plus one refresh cycle.
- MAINS skew is NEGATIVE (card marker ≈ card open; matches span the card, n=8 small): the widening that matters is the **tail** — the placeholder T-0 can pass hours before the true start. 8 h ≈ a Wimbledon card span; the tape latch (valid premarket volume notwithstanding — see Part 3) plus `tape_gated_abandon` semantics govern reality.
- The 60-min margin = one cron cycle + parse latency. **X is PROPOSED, pre-registered for Plex to adjust at the source gate** — the mechanism (per-cat table in code, one constant dict) makes retuning a one-line change.

### What the fallback does NOT do
- It never writes `event_start_time` differently from today's behavior — the fallback IS today's value.
- It never consults `status` for behavior (status is shadow-logged only; an ESPN-live cancel gate is a separate, future proposal per the match-start-signal forensic).
- It never feeds `_is_match_live`, `latch_tape_override`, `sustained_flow`, grace-kill, or any abandon/liveness path. Tape supremacy is absolute.

---

## PART 1 BUILD SHAPE (staged, gated, for Plex's source gate)

Two flags, both default **False = byte-identical**:
1. **`per_match_clock_shadow`** (observe-only): per event, once, log `pm_clock_shadow` — honest start (if resolvable), placeholder start, legacy `event_start_time`, deltas, staleness class, schedule `status`, category. Zero behavior. This satisfies "both clocks visible in logs".
2. **`per_match_clock`** (behavior, arms only after Plex ratifies + shadow validates): the **entry-window clock** — the `time_to_start` computed in `_route_event` (:5942) that feeds `_coarse_window_closed`, the 24 h horizon, `V4_MAX_PLACEMENT_SEC` leading edge, and the entry-table/staircase/engagement rows downstream in that one entry pipeline — resolves via: HONEST → per-match TE/ESPN time; else fallback rule above.

**Scope confinement (grep-proof at the diff):**
- `event_start_time` writes: UNTOUCHED — exit (`:7091`), cancels (`match_start_buffer` `:5272` stays on `pos.match_start_ts`, deliberate: cancels are tape-governed in practice), completion (BOTH mechanisms — `completion_reprice`/`_window_open` conception `:2495` AND `complete_cross`), meter, routing dispatch, liveness TTS floor (`:4162/:4279`) all keep reading the legacy clock byte-identically.
- ZERO tokens of the diff inside `_is_match_live`, `_sustained_flow_*`, grace-kill, abandon, `latch_tape_override` (its two-stage semantics explicitly preserved).
- Helpers pure (module-level, `_kalshi_occ_start` pattern): no awaits, no state writes, no IO per tick. Honest-clock resolution rides the EXISTING 5-min schedule reload + matcher; no new fetches.
- Tests: AST-extract the real bodies (per 706cb3c/47fa2ff pattern); byte-identical-OFF proof; AST sweep must list exactly the intended methods as changed.

## PART 3 (parallel) — SCALE-AWARE GUN, SHADOW ONLY
Flag `scale_gun_shadow` (default False): pure observe. Per event, compute a scale-aware burst bar (baseline premarket print-rate × multiplier, floor at `LIVE_TRADE_BURST`) from the same trade-time buffers `_is_match_live` reads (pure read); latch into a shadow dict; log `gun_scale_shadow` once on shadow-latch with {fired_at, recent_burst, baseline/min, scaled_bar, legacy_gun_state, tts}. **No consumer switches; the real gun, cancels, and latches unchanged.** Purpose: collect gun-agreement data on _MAIN (where the fixed bar of 10 prints/60 s trips hours early on Wimbledon-scale premarket volume) before any Part 3 proposal.

---
*Lint + smoke before anything arms. Bot untouched this session. Deploy only via `deploy/deploy_live_v4.sh` (the gate), on operator's word, after Plex ratifies.*
