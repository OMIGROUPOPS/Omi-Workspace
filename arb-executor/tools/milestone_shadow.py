#!/usr/bin/env python3
"""C-MILESTONE-SHADOW v1 (operator word, 07-16) — SHADOW-ONLY.

Polls Kalshi's public /milestones feed for every event the fund tracker
knows about (fills / positions / resting orders, today + yesterday) and
logs the THREE CLOCKS side by side per game:

    milestone actual start  vs  our clamped bell  vs  schedule

NO ENGINE BEHAVIOR CHANGES — this organ only appends to
state/milestone_shadow.jsonl (one row per observed status/start change)
and renders the nightly three-clock disagreement table. Arming the
milestone feed as a live gun source stays WORD-GATED pending this
shadow's evidence.

429 budget: one public GET per tracked event per poll (~0.15s spacing,
~100-200 events/day => well inside public read limits at */15 cadence).

Usage:
  python3 tools/milestone_shadow.py --poll             # cron */15
  python3 tools/milestone_shadow.py --table [--date D] # nightly 12:18a
"""
import argparse
import json
import sqlite3
import sys
import time
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).resolve().parent))
import daysheet_panel as ds  # noqa: E402  (join + clamped first-point)

ET = ZoneInfo("America/New_York")
ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "state" / "fund_equity.db"
OUT = ROOT / "state" / "milestone_shadow.jsonl"
TABLE_DIR = ROOT.parent / ".claude" / "milestone_shadow"


def _q(sql, args=()):
    con = sqlite3.connect("file:%s?mode=ro" % DB, uri=True, timeout=2)
    try:
        return con.execute(sql, args).fetchall()
    finally:
        con.close()


def tracked_events():
    days = [datetime.now(ET).strftime("%Y%m%d"),
            (datetime.now(ET) - timedelta(days=1)).strftime("%Y%m%d")]
    tks = {r[0] for r in _q(
        "SELECT DISTINCT ticker FROM fills WHERE day IN (?,?)", days)}
    tks |= {r[0] for r in _q(
        "SELECT DISTINCT ticker FROM snap_orders "
        "WHERE ts=(SELECT MAX(ts) FROM snap_orders)")}
    tks |= {r[0] for r in _q(
        "SELECT DISTINCT ticker FROM snap_positions "
        "WHERE ts=(SELECT MAX(ts) FROM snap_positions)")}
    return sorted({ds._ticker_pair_code(t)[1] for t in tks if t})


def fetch_milestone(ev):
    url = ("https://api.elections.kalshi.com/trade-api/v2/milestones"
           "?related_event_ticker=%s&limit=5" % ev)
    req = urllib.request.Request(url, headers={"User-Agent":
                                               "omi-milestone-shadow"})
    with urllib.request.urlopen(req, timeout=15) as r:
        d = json.load(r)
    for m in d.get("milestones") or []:
        det = m.get("details") or {}
        return {"status": det.get("status"),
                "start_date": m.get("start_date"),
                "start_ep": ds._iso_ep(m.get("start_date") or ""),
                "last_updated": m.get("last_updated_ts"),
                "source_id": m.get("source_id") or
                             (m.get("source_ids") or {}).get("source_3_id"),
                "title": m.get("title")}
    return None


def _last_rows():
    last = {}
    if OUT.exists():
        for line in open(OUT, encoding="utf-8", errors="replace"):
            try:
                j = json.loads(line)
                last[j["event"]] = j
            except ValueError:
                continue
    return last


def poll():
    last = _last_rows()
    events = tracked_events()
    wrote = 0
    with open(OUT, "a", encoding="utf-8") as f:
        for ev in events:
            try:
                ms = fetch_milestone(ev)
            except Exception:
                ms = None  # transient fetch error — next poll retries
            time.sleep(0.15)
            if not ms:
                continue
            sj = ds.join_match_name(ev + "-X")
            sched_ep = sj.get("start_ep")
            fp = ds.first_point_for(ev, sched_ep)
            row = {
                "ts": time.time(),
                "event": ev,
                "ms_status": ms["status"],
                "ms_start": ms["start_date"],
                "ms_start_ep": ms["start_ep"],
                "sched_ep": sched_ep,
                "our_fp_ep": fp["ts"] if fp else None,
                "our_fp_src": fp["src"] if fp else None,
                "our_fp_observed": fp["observed"] if fp else None,
                "d_ms_vs_fp_min": (
                    round((ms["start_ep"] - fp["ts"]) / 60, 1)
                    if (ms["start_ep"] and fp and fp.get("ts")) else None),
                "d_ms_vs_sched_min": (
                    round((ms["start_ep"] - sched_ep) / 60, 1)
                    if (ms["start_ep"] and sched_ep) else None),
                "source_id": ms.get("source_id"),
            }
            prev = last.get(ev)
            # append only on change (status or start moved) — the jsonl
            # is a change-log, not a heartbeat
            if prev and prev.get("ms_status") == row["ms_status"] \
                    and prev.get("ms_start") == row["ms_start"]:
                continue
            f.write(json.dumps(row) + "\n")
            wrote += 1
    print("[%s] milestone_shadow poll: %d events, %d changes logged"
          % (datetime.now(ET).strftime("%I:%M:%S %p ET"), len(events),
             wrote))


def table(date=None):
    date = date or datetime.now(ET).strftime("%Y%m%d")
    day_start = datetime.strptime(date, "%Y%m%d").replace(
        tzinfo=ET).timestamp()
    rows = {}
    if OUT.exists():
        for line in open(OUT, encoding="utf-8", errors="replace"):
            try:
                j = json.loads(line)
            except ValueError:
                continue
            rows[j["event"]] = j  # latest observation per event wins
    def hm(ep):
        return (datetime.fromtimestamp(ep, ET).strftime("%I:%M:%S %p")
                if ep else "—")
    lines = ["# THREE-CLOCK DISAGREEMENT — %s (milestone SHADOW; "
             "no engine behavior)" % date,
             "", "| event | ms status | milestone start | sched | "
             "our first-pt (src) | ms−fp min | ms−sched min |",
             "|---|---|---|---|---|---|---|"]
    deltas_fp, deltas_sched = [], []
    for ev, j in sorted(rows.items()):
        lines.append("| %s | %s | %s | %s | %s (%s%s) | %s | %s |" % (
            ev.split("-", 1)[-1], j.get("ms_status"),
            hm(j.get("ms_start_ep")), hm(j.get("sched_ep")),
            hm(j.get("our_fp_ep")), j.get("our_fp_src") or "—",
            " LIVE" if j.get("our_fp_observed") else " EST",
            j.get("d_ms_vs_fp_min"), j.get("d_ms_vs_sched_min")))
        if j.get("d_ms_vs_fp_min") is not None:
            deltas_fp.append(j["d_ms_vs_fp_min"])
        if j.get("d_ms_vs_sched_min") is not None:
            deltas_sched.append(j["d_ms_vs_sched_min"])
    def qs(v):
        if not v:
            return "n=0"
        v = sorted(v)
        return ("n=%d p25=%.1f p50=%.1f p75=%.1f" %
                (len(v), v[len(v)//4], v[len(v)//2], v[3*len(v)//4]))
    lines += ["", "**ms−our-first-pt (min):** " + qs(deltas_fp),
              "**ms−sched (min):** " + qs(deltas_sched),
              "", "Arming as a live gun source stays WORD-GATED on this "
              "table's evidence."]
    TABLE_DIR.mkdir(parents=True, exist_ok=True)
    p = TABLE_DIR / ("CLOCKS_%s.md" % date)
    p.write_text("\n".join(lines), encoding="utf-8")
    print("three-clock table: %d events -> %s" % (len(rows), p))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--poll", action="store_true")
    ap.add_argument("--table", action="store_true")
    ap.add_argument("--date", default=None)
    a = ap.parse_args()
    if a.poll:
        poll()
    if a.table:
        table(a.date)
