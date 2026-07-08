# OUTCOME PROOF (C46, two-lane) — C-CONCEPTION-HORIZON (T-8h early bound, INTERIM SCAFFOLDING)

**Candidate SHA: `6d9ebe31`** (router gate + manage-pass sweep + place_order chokepoint refusal + C47 flag, shared `_horizon_state`; live-monitor flow-state gauge rides the same commit).

## THE DECLARATION (goes in the vault entry verbatim)
The T-8h bound is **INTERIM SCAFFOLDING** — a map edge drawn while unstudied territory gets studied, **NEVER a target**. It moves automatically on the early-canvas study's evidence + operator ruling. The cap-as-goal grave (97-wall, three resurrections) is the named prior for why a bound must not be allowed to become an aim.

## Prior art (C45)
- **LIVING_VAULT FOUNDATIONS / front page** — the three observable prices; the entry doctrine (early POSITION, late FILL); **PRE-T-4H named as an open analysis debt** ("first look done 07-06: B3 §4 T-8h coverage sized; exploitation spec = week deliverable (c)"). This bound formalizes the edge of what those debts have actually studied.
- **HOURLY_APPENDIX 07-07 (FLOOR-BY-HOUR)** — ITF prints/min **0.00 until T-3h** (early book = wide 4-5.5¢ silent lattice quoting ~99); **MAINS quote-touch floor 100.0 flat in every bin T-8→T-1** (liquid at par all day — the early hypothesis REFUTED); CHALL intermediate. **Per-cat mechanisms differ — never flatten.** Everything beyond T-8h is terra incognita: the appendix's own coverage stops there.
- **PAIR-STORY 07-07** — the floor is LATE (med bestT −15/−17 min; post-ramp 72-77%); "early posting buys POSITION, not early fills." A bid resting 15h out buys queue position in a lattice that has never once been observed to pay before T-8h.
- **RETIRED grave: cap-as-goal** (97-wall, three resurrections) — the reason for the scaffolding declaration above.
- **C-BAND-CLAMP-WALK `a5a64962` (this morning)** — the chokepoint-makes-the-cancel-stick lesson, applied here at build time instead of after a live exhibit: the sibling-repost scan re-derives placements and re-posts them (JANFUN-FUN class below), so the sweep alone would churn.
- **24h router edge (`time_to_start - _pm_widen > 86400`)** — the existing map edge this bound tightens; same clock, same widen semantics.
- **C-PM-CLOCK / per_match_clock (LIVE since 07-06)** — supplies the honest anchor; `_horizon_state` reuses `_pm_clock_resolve` verbatim so the gate, sweep, and audit flag agree with the router by construction. No anchor → the bound NEVER blocks (schedule_gap class keeps its existing handling).

## The pre-deploy census (exchange truth, 18:06Z)
101 resting buys; 82 inside horizon; 7 schedule-unknown (bound never touches); **12 BEYOND T-8h (12.9–14.9h out)** — the sweep list:

| leg | bid | tts | note |
|---|---|---|---|
| KXWTACHALLENGERMATCH-26JUL08VANSEL-SEL | 59 | 14.9h | sibling of held VAN leg |
| KXITFMATCH-26JUL08GILOBR-GIL / -OBR | 5 / 93 | 14.4h | **the exhibit — GILOBR's 2 bids** |
| KXITFMATCH-26JUL08TORMEL-TOR / -MEL | 34 / 62 | 14.4h | |
| KXITFMATCH-26JUL08BEKPAN-BEK / -PAN | 21 / 78 | 14.4h | |
| KXITFMATCH-26JUL08JUHKLO-KLO / -JUH | 36 / 60 | 14.4h | |
| KXITFMATCH-26JUL08JANFUN-FUN | 42 | 14.4h | **sibling of held JAN leg — the churn-class exhibit** |
| KXITFMATCH-26JUL08ZIVMIK-ZIV / -MIK | 5 / 92 | 12.9h | ZIV is a partial (1 held on MIK side) |

## LANE 1 — MECHANISM (deterministic)
- **Replay of the current book under the bound:** the 12 beyond-horizon bids cancel at the first manage pass post-boot (`conception_horizon_cancel`, named); unfilled pairs free via `_untombstone_entry` (pos deleted + processed_events cleared) and the router re-conceives each the moment its match crosses T-8h. Held-sibling pairs (JANFUN, VANSEL, ZIVMIK): the sibling scan's re-post attempts are REFUSED at the chokepoint (`conception_horizon_refused`, dedup-logged) — no churn loop, re-post lands at T-8h. **Exits untouched everywhere** (sells never gated); completion-reprice bids dispatch before the sweep.
- **In-window behavior byte-identical:** every gate is a pure early-exit on `tts_eff > 28800`; today's session activity (all fills 16:00Z–18:00Z were on matches inside 8h) replays unchanged. The 24h edge remains (subsumed).
- **A legally-placed bid can never age INTO violation** (tts only falls); the sweep exists for pre-horizon-era bids (this census) and schedule corrections that push a start out.
- **What the bound forfeits, stated honestly:** queue position accumulated 8–15h early in the ITF silent lattice, and early pair-completion on held-sibling pairs until T-8h. HOURLY_APPENDIX/PAIR-STORY evidence: no observed fill value before T-8h anywhere in the studied corpus (ITF prints/min 0.00 until T-3h; mains par-locked; the 5-13% early-floor pairs all sit INSIDE T-8h bins). The unstudied part (beyond T-8h) is exactly what Part 2 studies while the bound holds.
- **Regression counter:** C47 audit flag `conception_beyond_horizon` — a resting buy beyond horizon after the sweep = both the gate and the sweep evaded → must stay 0.

## LANE 2 — SETTLEMENT P&L
$0 claimed (deferral/refusal-only; no price or size logic touched). Flagged, not claimed: the 12 swept bids' counterfactual fills between now and their T-8h re-conception are unknowable in either direction — that unknown is the entire reason the study runs.

**Verdict: a bound on unstudied exposure, built at the three chokepoints the last two defect classes taught (route, sweep, chokepoint-refusal), with the anchor the honest clock already supplies. Deploys through the full gate; the horizon key's default is the only config-shaped delta and it ships as scaffolding, not tuning.**
