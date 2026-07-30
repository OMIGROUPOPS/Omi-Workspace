#!/usr/bin/env python3
"""Audit whether a range-spectrum artifact can fit a lawful entry-aim surface.

The audit is deliberately read-only. It distinguishes:

* a consultation timestamp reconstructable from a poll snapshot; from
* an actual last-trade timestamp/staleness proof required to call the anchor
  fresh.

The former is useful lineage. It is not silently promoted to the latter.
"""

import argparse
import datetime as dt
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


def _first_observed_trade(leg):
    for tick in leg.get("ticks") or ():
        if len(tick) >= 4 and tick[3]:
            return tick
    return None


def _event_date(event_id):
    match = re.search(
        r"-(\d{2})(JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)(\d{2})",
        event_id or "",
    )
    if not match:
        return None
    return dt.datetime.strptime("".join(match.groups()), "%y%b%d").date()


def _quantile(values, fraction):
    if not values:
        return None
    ordered = sorted(values)
    return ordered[min(len(ordered) - 1, int(fraction * (len(ordered) - 1)))]


def census(path):
    counts = Counter()
    by_cat = defaultdict(Counter)
    cells = defaultdict(Counter)
    branch_cells = defaultdict(lambda: defaultdict(Counter))
    cat_dates = defaultdict(set)

    with Path(path).open(encoding="utf-8") as fh:
        for line in fh:
            if not line.strip():
                continue
            event = json.loads(line)
            counts["events"] += 1
            cat = event.get("cat") or "UNKNOWN"
            event_date = _event_date(event.get("event"))
            if event_date is not None:
                cat_dates[cat].add(event_date)
            for leg_id, leg in (event.get("legs") or {}).items():
                counts["leg_slots"] += 1
                by_cat[cat]["leg_slots"] += 1
                rule = leg.get("anchor_rule") or "missing_rule"
                counts["rule:" + rule] += 1
                by_cat[cat]["rule:" + rule] += 1
                anchor = leg.get("anchor")
                if anchor is None:
                    continue
                counts["anchors"] += 1
                by_cat[cat]["anchors"] += 1
                anchor_cell = int(anchor)
                if 5 <= anchor_cell < 95:
                    cells[cat][str(anchor_cell)] += 1
                    counts["anchors_inside_5_95"] += 1
                    by_cat[cat]["anchors_inside_5_95"] += 1
                else:
                    counts["anchors_outside_5_95"] += 1
                    by_cat[cat]["anchors_outside_5_95"] += 1

                explicit_ts = leg.get("anchor_ts")
                if explicit_ts is not None:
                    counts["explicit_anchor_ts"] += 1
                    by_cat[cat]["explicit_anchor_ts"] += 1

                first = _first_observed_trade(leg)
                reconstructed = (
                    rule == "first_after_t8"
                    and first is not None
                    and int(first[3]) == int(anchor)
                )
                if reconstructed:
                    counts["reconstructable_consultation_ts"] += 1
                    by_cat[cat]["reconstructable_consultation_ts"] += 1
                    bid = int(first[1] or 0)
                    ask = int(first[2] or 0)
                    last = int(first[3])
                    if bid > 0 and ask > bid:
                        spread = ask - bid
                        if spread <= 2 and not (bid <= last <= ask):
                            branch = "tight_mid"
                            key_px = round((bid + ask) / 2)
                        else:
                            branch = "fresh_last_trade"
                            key_px = last
                    else:
                        branch = "no_bbo_denominator"
                        key_px = None
                    counts["branch:" + branch] += 1
                    by_cat[cat]["branch:" + branch] += 1
                    if key_px is not None and 5 <= int(key_px) < 95:
                        branch_cells[branch][cat][str(int(key_px))] += 1
                        counts["branch_inside_5_95:" + branch] += 1
                        by_cat[cat]["branch_inside_5_95:" + branch] += 1
                    elif key_px is not None:
                        counts["branch_outside_5_95:" + branch] += 1
                        by_cat[cat]["branch_outside_5_95:" + branch] += 1

                # A poll timestamp is not a trade timestamp. These explicit
                # fields (or an equivalent raw event receipt) are required to
                # prove freshness instead of assuming it.
                if (
                    leg.get("anchor_trade_ts") is not None
                    and leg.get("anchor_consulted_ts") is not None
                    and leg.get("anchor_source")
                    and leg.get("anchor_staleness_sec") is not None
                ):
                    counts["strict_fresh_anchor_contract"] += 1
                    by_cat[cat]["strict_fresh_anchor_contract"] += 1

    cell_summary = {}
    for cat, cat_cells in sorted(cells.items()):
        ns = list(cat_cells.values())
        cell_summary[cat] = {
            "occupied_cells": len(ns),
            "cells_n_ge_20": sum(n >= 20 for n in ns),
            "legs": sum(ns),
            "min_n": min(ns) if ns else 0,
            "max_n": max(ns) if ns else 0,
        }

    branch_summary = {}
    for branch, cats in sorted(branch_cells.items()):
        branch_summary[branch] = {}
        for cat, cat_cells in sorted(cats.items()):
            ns = list(cat_cells.values())
            branch_summary[branch][cat] = {
                "occupied_cells": len(ns),
                "cells_n_ge_20": sum(n >= 20 for n in ns),
                "legs": sum(ns),
            }

    optimistic_collection_time = {}
    for cat in sorted(set(cells) | set(cat_dates)):
        dates = sorted(cat_dates.get(cat) or ())
        span_days = (dates[-1] - dates[0]).days + 1 if dates else None
        cat_result = {
            "observed_date_span_days": span_days,
            "first_event_date": str(dates[0]) if dates else None,
            "last_event_date": str(dates[-1]) if dates else None,
            "warning": (
                "optimistic lower bound from retrospective anchor values; "
                "not a forecast for the strict fresh-anchor branch"
            ),
        }
        for label, source_cells in (
            ("all_anchor_values", cells.get(cat, {})),
            (
                "reconstructable_fresh_last_trade_like",
                branch_cells["fresh_last_trade"].get(cat, {}),
            ),
        ):
            if not span_days:
                cat_result[label] = None
                continue
            days = []
            zero_cells = 0
            for cell in range(5, 95):
                n = int(source_cells.get(str(cell), 0))
                if n <= 0:
                    zero_cells += 1
                else:
                    days.append(round(20.0 * span_days / n, 1))
            cat_result[label] = {
                "zero_observation_cells": zero_cells,
                "median_days_to_n20": _quantile(days, 0.50),
                "p90_days_to_n20": _quantile(days, 0.90),
                "slowest_observed_cell_days_to_n20": max(days) if days else None,
            }
        optimistic_collection_time[cat] = cat_result

    return {
        "source": str(Path(path).resolve()),
        "counts": dict(sorted(counts.items())),
        "by_category": {
            cat: dict(sorted(cat_counts.items()))
            for cat, cat_counts in sorted(by_cat.items())
        },
        "all_anchor_value_cells": cell_summary,
        "reconstructable_branch_cells": branch_summary,
        "optimistic_collection_time": optimistic_collection_time,
        "interpretation": {
            "reconstructable_consultation_ts":
                "first poll at/after T-8 with a nonzero last matching anchor",
            "strict_fresh_anchor_contract":
                "requires trade timestamp, consultation timestamp, source, "
                "and staleness; a poll timestamp alone does not qualify",
        },
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("range_spectrum_jsonl")
    args = parser.parse_args()
    print(json.dumps(census(args.range_spectrum_jsonl), indent=2,
                     sort_keys=True))


if __name__ == "__main__":
    main()
