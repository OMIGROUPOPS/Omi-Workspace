"""OS LAYER — DECISION CORE (2026-07-09, Plex T1-T4 cleared; GAME_LIFECYCLE
steps 2-5 as code). PURE: no imports from live_v4, no order-path reach —
enforced by the gate's import-boundary assertion (lint_gate.py). The core
consumes ONE assembled input vector and returns the would-be action.
Every rule cites its ruling. SHADOW-ONLY: the arm path is a dormant flag
gated on coverage ruling + dedup lock + certification + four bars + word.
"""

# fill-probability states [VOLUME_LEDGER + FILL_REDO, corrected grid 07-09]
OPEN_PRINTS_30M = {"ITF_M": 6, "ITF_W": 6, "ATP_CHALL": 16, "WTA_CHALL": 16,
                   "ATP_MAIN": 16, "WTA_MAIN": 16}
# regime per cell [THE GRID + FILL_REDO: mains join-only; <50 decay; 50+ climb]
def regime(cat, cell):
    if cat in ("ATP_MAIN", "WTA_MAIN"):
        return "mains_join"          # depth forbidden: the cliff [FILL_REDO P1]
    if cell is None:
        return "unknown"
    if cell < 50:
        return "decay_side"          # floor IS the close, timing not depth [SEQFLOOR]
    return "climb_side"              # depth cells; 75-94 the deep zone [RECUT]


def timing_state(tts_min, onset_age_min):
    """[CLIMBSIDE_SPEC + EXTENSIVE P3] T-90 resting; onset+-15 hold; then stand down.
    tts_min: minutes to anchored start (None = unknown -> no posture).
    onset_age_min: minutes since volume onset (None = book not woken)."""
    if tts_min is None:
        return "no_anchor"
    if onset_age_min is not None and onset_age_min > 15:
        return "stand_down"          # the climb owns the tape: NEVER chase [EXTENSIVE]
    if onset_age_min is not None:
        return "hold_window"         # the dip is live (~3-min median dwell)
    if tts_min <= 90:
        return "resting_window"      # the bid must pre-exist the window [T-90]
    return "early"                   # pre-T-90: no climb-side post yet


def decide(vec):
    """vec keys (each citing its ruling):
      cat, cell            -- THE GRID (90x6; cell = leg's own price cell)
      edge_p50, thin_tape  -- recut_cells_volume (COMBINED-PRICE CLAUSE inputs)
      close_ref            -- last-trade/W1-close reference (A37 honest reference)
      bid, ask, spread     -- the three observables [0A]
      bid_ex_self          -- non-self chain [EXPRESSION INVARIANT]
      prints_30m           -- micro volume state [GRANULARITY LAW: tape times]
      tts_min              -- anchored clock [C-ANCHOR]
      onset_age_min        -- volume-onset age (None = quiet)
      ask_falling          -- ask-hold conditioning [POST_FILL: reprice leading edge]
      qual_stage           -- staged qualification [STEP1 P1b: placement-light]
    Returns the would-be action dict. NO side effects, NO order paths."""
    cat, cell = vec.get("cat"), vec.get("cell")
    reg = regime(cat, cell)
    state = timing_state(vec.get("tts_min"), vec.get("onset_age_min"))
    is_open = (vec.get("prints_30m") or 0) >= OPEN_PRINTS_30M.get(cat, 16)
    out = {"regime": reg, "timing": state, "flow_open": is_open,
           "action": "none", "level": None, "posture": None,
           "cited": ["GAME_LIFECYCLE 2-5"]}

    if reg == "unknown" or state == "no_anchor":
        out["action"] = "defer"
        out["cited"].append("no_reliable_commence / grid")
        return out

    bid = vec.get("bid") or 0
    ask = vec.get("ask") or 100
    bx = vec.get("bid_ex_self")
    join_level = min(bx if bx is not None else bid, ask - 1)  # never marketable [PLEX]

    if reg == "mains_join":
        # join-at-touch ONLY in OPEN; depth aims at nothing [FILL_REDO]
        if is_open:
            out.update(action="rest", posture="join_touch", level=max(1, join_level))
            out["cited"].append("FILL_REDO mains JOIN 40-50%@V3")
        else:
            out["action"] = "wait_flow"
        return out

    if reg == "decay_side":
        # join-at-close, flow-gated, LATE window (floor T-9..-17) [SEQFLOOR]
        if state in ("hold_window", "stand_down") or (state == "resting_window" and is_open):
            out.update(action="rest", posture="join_close", level=max(1, join_level))
            out["cited"].append("SEQFLOOR decay floor = close")
        else:
            out["action"] = "wait_window"
        return out

    # climb_side [CLIMBSIDE_SPEC]
    edge = vec.get("edge_p50") or 0
    close_ref = vec.get("close_ref")
    if close_ref is None:
        out["action"] = "defer"
        return out
    fitted = max(1, int(close_ref - edge))            # the FITTED level; never walked up
    fitted = min(fitted, ask - 1)                     # never marketable
    if vec.get("ask_falling"):
        # reprice in progress: the fill would be its leading edge — hold the
        # fitted level, do NOT lift toward it [POST_FILL ask-hold conditioning]
        out["cited"].append("POST_FILL ask-hold")
    if state == "early":
        out["action"] = "wait_t90"
    elif state in ("resting_window", "hold_window"):
        out.update(action="rest", posture="fitted_aim_hold", level=fitted)
        out["cited"].append("CLIMBSIDE_SPEC T-90 aim-then-HOLD")
        if vec.get("thin_tape"):
            out["cited"].append("thin-tape cell (weighted at refit)")
        if vec.get("qual_stage") == "sub_floor_watch":
            out["cited"].append("STEP1 staged qual: placement-light")
    elif state == "stand_down":
        out.update(action="stand_down", posture="join_close_or_skip",
                   level=max(1, join_level))
        out["cited"].append("EXTENSIVE never-chase onset+15")
    return out
