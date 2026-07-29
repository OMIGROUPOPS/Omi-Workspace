#!/usr/bin/env python3
"""Keep the OS policy edge separate from the evaluation evidence edge."""

from __future__ import annotations

import math


def full_lawful_right(
    *,
    policy_right_ts: float,
    guarded_cutoff_ts: float | None,
    positive_window1_provable: bool,
) -> float | None:
    """Return the evidence edge without extending unresolved boundaries.

    ``policy_right_ts`` remains the time at which the OS may stop placing or
    cancel orders.  It is accepted here so callers must name both clocks, but
    it never shortens a positive evaluator window.
    """
    policy_right = float(policy_right_ts)
    if not math.isfinite(policy_right):
        raise ValueError("policy right is not finite")
    if not positive_window1_provable:
        return None
    if guarded_cutoff_ts is None:
        raise ValueError("positive boundary lacks guarded actual-start cutoff")
    cutoff = float(guarded_cutoff_ts)
    if not math.isfinite(cutoff):
        raise ValueError("guarded actual-start cutoff is not finite")
    return cutoff
