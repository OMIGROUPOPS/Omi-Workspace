# PLEX RATIFICATION — T3 SUPERSESSION + T4 HOLD-GATE CLAUSE (relayed 2026-07-09 night; recorded before code per the dispatch's sequencing)

> ⚠ **VERBATIM BODY PENDING — the paste channel dropped Plex's full ruling text.** The dispatch states the operator relayed it verbatim, but neither the dispatch body nor git carries the text (checked: `.claude/rulings/PLEX_*.md`, recent commits). Per the HANDOFF contract this is said plainly, not papered over. **This slot is reserved for the word-for-word text; the relay owes it.** What follows is the ruling's CONTENT as the dispatch itself states it — binding now, superseded in wording by the verbatim when it lands.

## The ruling, as relayed (dispatch of 07-09 night, FINAL wording)

1. **T3 supersession RATIFIED** — the riser is retired; lineage stated in `CLIMBSIDE_SPEC.md` (climb-side/decay-side supersedes the riser frame).
2. **T4 hold-gate clause RATIFIED; the threshold NUMBER stays reserved** for Plex, to be set on shadow data (where quiet-book dumps cluster).
3. **Dispatch CLEARED with a binding sequencing note** — the dual-flag shadow condition below ships before the threshold dataset accumulates.
4. **Plex's explicit upgrade, stated as LAW, not footnote:** *the hold-gate now carries two jobs — anti-selection defense (the original T4 ask) and the volume floor's only enforcement point (P1b's finding).*

## The binding condition (T4), in its exact shape

Every hold-gate shadow line reports **two separate named flags per leg, never one merged boolean**:
- **`quiet_flag`** (anti-selection): would-hold/would-review judged against the leg's **own T−8h→T−4h activity baseline**, with the **baseline value logged**;
- **`floor_miss_flag`** (volume floor): **realized volume to now + staged-floor qualification state**.

**Plex's stated reason (and it lives in the code comment, `oslayer/holdgate.py`):** if the two readings ever diverge, that divergence must be **visible in the data**, not hidden inside one number.

## Execution record (C-T4-DUAL-FLAG, this deploy)
- Pre-instrument state, named honestly: the live `hold_review` lines carried both flag FIELDS but the floor reading was **structurally dead** — the caller passed `expected_share_by_now=None`, so `floor_miss_flag` was a constant False, and the quiet baseline was a running median of ALL samples rather than the leg's own T−8h→T−4h span. That fails the condition; instrumented now.
- Instrument: per-event realized **contract** volume from ws trades (unit-matched to the staged 2.5k floor; basis named `ws_contracts_since_boot` on every line) · T−8h→T−4h baseline banked separately per leg · shadow-default per-cat share curve (coarse, sourced to the 07-07 HOURLY_APPENDIX shape, refit at the threshold pass — never a ruling) · `floor_qual` state on every line (`qualified_now` / `on_pace` / `below_pace` / `unevaluable` — never silent).
- **Fence:** lines without the `t4: dual_flag_v1` stamp are `pre_instrument` — counted visibly in the rollup, excluded from Plex's threshold dataset. **The T4 accumulation clock starts at the first dual-flag line after this deploy** (time stated in the close-out).
- Arm prerequisites UNCHANGED: four bars · joint-shadow n≥30 · shadow-first · `os_active` untouched (dormant).
