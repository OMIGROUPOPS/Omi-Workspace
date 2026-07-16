#!/usr/bin/env python3
"""C-THE-WALK v1 — the OS answers for itself (standing protocol).
Renders THE ACCOUNT for a flagged game from the logs: every consultation
(external -> what it said -> action taken), placements/cancels/fills/
exits/settles with window stamps, entry grade per the rubric, footnote
class. AMENDMENT and PROOF sections are templated for the walk runner —
the amendment is verbalized consultation logic, never a ticker-shaped
patch; a correction no existing external could supply names the MISSING
EXTERNAL as the finding.

Usage: python3 analysis/the_walk.py --event FOMLIM [--date YYYYMMDD]
Out:   .claude/walks/<date>/WALK_<event>.md (account auto-filled)"""
import argparse
import gzip
import json
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

ET = ZoneInfo("America/New_York")
ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT.parent / ".claude" / "walks"


def day_open(ymd):
    p = ROOT / "logs" / ("live_v3_%s.jsonl" % ymd)
    if p.exists():
        return open(p, encoding="utf-8", errors="replace")
    pz = ROOT / "logs" / ("live_v3_%s.jsonl.gz" % ymd)
    if pz.exists():
        return gzip.open(pz, "rt", encoding="utf-8", errors="replace")
    return None


def hm(ep):
    return datetime.fromtimestamp(ep, ET).strftime("%I:%M:%S %p")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--event", required=True,
                    help="pair code, e.g. FOMLIM")
    ap.add_argument("--date",
                    default=datetime.now(ET).strftime("%Y%m%d"))
    args = ap.parse_args()
    code = args.event.upper()
    days = [(datetime.strptime(args.date, "%Y%m%d")
             - timedelta(days=1)).strftime("%Y%m%d"), args.date]
    rows = []
    for d in days:
        fh = day_open(d)
        if not fh:
            continue
        for line in fh:
            if code not in line:
                continue
            try:
                j = json.loads(line)
            except ValueError:
                continue
            e = j.get("event", "")
            if any(s in e for s in ("shadow", "reality_divergence",
                                    "half_arm", "ws_settled",
                                    "schedule_abandon", "skipped",
                                    "tape_seed")):
                continue
            rows.append(j)
    rows.sort(key=lambda j: j.get("ts_epoch", 0))
    L = ["# THE WALK — %s (%s)" % (code, args.date),
         "(C-THE-WALK v1 — the OS answers for itself; account "
         "auto-rendered from the logs)", "",
         "## ① THE ACCOUNT (external → what it said → action taken)"]
    seen = set()
    for j in rows:
        e = j["event"]
        det = j.get("details") or {}
        tk = (j.get("ticker") or "").rsplit("-", 1)[-1]
        key = (e, tk, json.dumps(det, sort_keys=True)[:80])
        if key in seen:
            continue
        seen.add(key)
        t = hm(j.get("ts_epoch", 0))
        if e == "entry_dossier":
            s = det.get("surfaces") or {}
            said = []
            for name in ("atlas_page", "reach_law", "flow_state",
                         "cash_window", "window_phase"):
                v = s.get(name) or {}
                said.append("%s:%s" % (
                    name, v.get("status", "?")[:4] + (
                        "(%s)" % (v.get("why") or v.get("verdict")
                                  or v.get("bucket") or v.get("phase")
                                  or "")[:40]
                        if v.get("status") != "CONSULTED" or
                        name in ("flow_state", "cash_window",
                                 "window_phase") else "")))
            L.append("- %s **consultation %s** → decision `%s` aim=%s | %s"
                     % (t, tk, det.get("decision"), det.get("aim"),
                        " · ".join(said)))
        elif e in ("order_placed", "order_cancelled", "entry_filled",
                   "exit_filled", "v4_exit_posted", "settled",
                   "gun_fired", "path_mode_hold", "completion_action",
                   "cancel_fill_race", "w2_fill_violation",
                   "schedule_match", "bell_missing", "clock_liar"):
            w = det.get("window") or {}
            L.append("- %s %s %s %s%s" % (
                t, e, tk,
                json.dumps({k: det.get(k) for k in (
                    "action", "price", "count", "label", "success",
                    "fill_price", "exit_price", "pnl_cents", "settle",
                    "source", "held_price", "proposed", "start_time",
                    "min_past_start", "verdict") if det.get(k)
                    is not None})[:160],
                (" [%s%s]" % (w.get("phase", ""),
                              " gun" if w.get("gun_fired") else ""))
                if w else ""))
    L += ["", "## ② THE AMENDMENT (verbalized by the OS — consultation "
              "logic, never a ticker-shaped patch)",
          "AMENDMENT-HERE (if no existing external could supply the "
          "correction, the MISSING EXTERNAL is the finding)", "",
          "## ③ THE PROOF (the game's recorded tape re-run under the "
          "amended logic)", "PROOF-HERE (corrected fate + grade beside "
          "the original)", "",
          "## ④ THE FILING",
          "FILING-HERE (class ledger instance or NEW-CLASS numbered; "
          "shadow-first; the operator's word gates any live arming)"]
    outdir = OUT / args.date
    outdir.mkdir(parents=True, exist_ok=True)
    fp = outdir / ("WALK_%s.md" % code)
    fp.write_text("\n".join(L) + "\n", encoding="utf-8")
    print("walk account rendered: %s (%d events)" % (fp, len(seen)))


if __name__ == "__main__":
    main()
