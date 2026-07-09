"""OS LAYER — HOLD GATE (Plex T4, BINDING: wired before logging starts).
Placement gate != hold gate. Quiet defined SYMMETRIC to the pair-story ramp
definition: sustained fall below the leg's OWN T-8h->T-4h activity baseline
for the comparable window -> HOLD-REVIEW, never silent rest.

TWO SEPARATE READINGS per leg per review — NEVER one merged boolean:
  quiet_flag      : anti-selection reading (the book died under the bid)
  floor_miss_flag : volume-floor pace reading (the match will finish sub-floor)
Divergence between them is visible BY CONSTRUCTION. The threshold NUMBER is
reserved for Plex once shadow data shows where quiet-book dumps cluster —
the constants below are SHADOW defaults, never a ruling. PURE module."""

QUIET_FALL_RATIO = 0.35     # shadow default: current window < 35% of own baseline
QUIET_SUSTAIN_MIN = 30      # sustained for >= 30 min
FLOOR_TARGET = 2500.0       # ITF floor [NEVERWAKE]; per-cat at the ruling


def review(own_baseline_p30m, recent_p30m_series, cum_vol, tts_min,
           expected_share_by_now):
    """own_baseline_p30m: leg's own med prints/30m over its T-8h->T-4h span
       recent_p30m_series: list of trailing prints/30m readings (newest last,
                           one per ~5 min) covering >= QUIET_SUSTAIN_MIN
       cum_vol: running W1 contracts (both legs)
       expected_share_by_now: corpus share of final volume typically traded
                              by this tts (per-cat curve; caller supplies)
    Returns the two readings, separately, plus the raw inputs echoed."""
    quiet_flag = False
    if own_baseline_p30m and recent_p30m_series:
        n_need = max(1, QUIET_SUSTAIN_MIN // 5)
        recent = recent_p30m_series[-n_need:]
        if len(recent) >= n_need and all(
                r < QUIET_FALL_RATIO * own_baseline_p30m for r in recent):
            quiet_flag = True

    floor_miss_flag = False
    projected = None
    if expected_share_by_now and expected_share_by_now > 0:
        projected = cum_vol / expected_share_by_now
        floor_miss_flag = projected < FLOOR_TARGET

    return {"quiet_flag": quiet_flag,
            "floor_miss_flag": floor_miss_flag,
            "own_baseline_p30m": own_baseline_p30m,
            "recent_p30m": (recent_p30m_series or [])[-6:],
            "cum_vol": round(cum_vol, 1) if cum_vol is not None else None,
            "projected_w1_vol": round(projected, 1) if projected else None,
            "tts_min": tts_min}
