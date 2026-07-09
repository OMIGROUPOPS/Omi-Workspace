#!/usr/bin/env python3
"""GUN SCORECARD [C-FUSED-GUN 2026-07-08] -- the standing tripwire renderer.

Every gun fire logs gun_source (+ gun_truth_delta when the scoreboard row
arrives). This script grades the night: per-cat detection %, median
|truth delta|, misses NAMED (never averaged away). Independent ground truth
per row = a source that match's gun decision did NOT consume:
  - gun_source == te_scoreboard  -> truth = TAPE flow onset (trades CSV:
    first minute with prints in >=5 of the trailing 15 minutes)
  - any other source             -> truth = TE observed_starts first_inplay
Usage:
  python3 gun_scorecard.py            # render table for today (ET)
  python3 gun_scorecard.py --nightly  # also append the GUN SCORECARD line to
                                      # NIGHTLY_PASS.md + write dated table + git push
"""
import gzip, json, re, sqlite3, subprocess, sys
from collections import defaultdict
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ET = timezone(timedelta(hours=-4))
TRADES = ROOT / "analysis" / "trades"
CAT = {"KXATPMATCH": "ATP_MAIN", "KXWTAMATCH": "WTA_MAIN",
       "KXATPCHALLENGERMATCH": "ATP_CHALL", "KXWTACHALLENGERMATCH": "WTA_CHALL",
       "KXITFMATCH": "ITF_M", "KXITFWMATCH": "ITF_W"}
PASS_TOL_MIN = 3.0


def cat_of(ev):
    for k, v in CAT.items():
        if ev.startswith(k):
            return v
    return None


def et_str(ts):
    return datetime.fromtimestamp(ts, ET).strftime("%I:%M:%S %p") if ts else "--"


def tape_onset(ev, t0, t1):
    """Independent tape truth: first minute (within [t0,t1]) with prints in
    >=5 of the trailing 15 one-minute bins, across both legs."""
    minutes = defaultdict(int)
    for f in TRADES.glob(ev + "-*.csv*"):
        op = gzip.open if f.name.endswith(".gz") else open
        try:
            with op(f, "rt", encoding="utf-8", errors="replace") as fh:
                next(fh, None)
                for ln in fh:
                    p = ln.split(",")
                    if len(p) < 3:
                        continue
                    try:
                        d, t, ap = p[0].split(" ")
                        y, mo, dy = d.split("-")
                        hh, mm, _ss = t.split(":")
                        ts = datetime(int(y), int(mo), int(dy),
                                      int(hh) % 12 + (12 if ap == "PM" else 0),
                                      int(mm), tzinfo=ET).timestamp()
                    except Exception:
                        continue
                    if t0 <= ts <= t1:
                        minutes[int(ts // 60) * 60] += 1
        except OSError:
            continue
    if not minutes:
        return None
    keys = sorted(minutes)
    for m in keys:
        active = sum(1 for k in range(m - 14 * 60, m + 60, 60) if minutes.get(k))
        if active >= 5:
            return m
    return None


def main():
    now = datetime.now(ET)
    day = now.strftime("%Y%m%d")
    files = sorted((ROOT / "logs").glob("live_v3_*.jsonl"),
                   key=lambda p: p.stat().st_mtime)[-2:]
    day0 = datetime(now.year, now.month, now.day, tzinfo=ET).timestamp() - 6 * 3600

    fires, deltas, sched, boots = {}, {}, {}, []
    for p in files:
        for line in open(p, encoding="utf-8", errors="replace"):
            if '"gun_fired"' not in line and '"gun_truth_delta"' not in line \
                    and '"schedule_match"' not in line \
                    and '"system_start"' not in line:
                continue
            try:
                d = json.loads(line)
            except ValueError:
                continue
            ts = d.get("ts_epoch", 0)
            det = d.get("details") or {}
            ev = det.get("event", "")
            if d["event"] == "system_start":
                boots.append(ts)
                continue
            if not ev or ts < day0:
                continue
            if d["event"] == "gun_fired":
                # [FIRE CLASS, operator 07-08] CATCH-UP = match already in-play
                # when the listener started (state-sync fire: te row predates
                # the boot / feed lag > 180s / fire inside the first poll
                # cycle after a boot). FRESH = transition observed live while
                # listening. The +/-3-min pass bar applies to FRESH only.
                lag = det.get("feed_lag_sec")
                last_boot = max((b for b in boots if b <= ts), default=0)
                catchup = ((lag is not None and lag > 180)
                           or (ts - last_boot) < 120)
                fires.setdefault(ev, {"ts": ts, "source": det.get("source"),
                                      "te_first": det.get("te_first_inplay"),
                                      "vol30": det.get("vol_prints_30m"),
                                      "fire_class": ("CATCH-UP" if catchup
                                                     else "FRESH")})
            elif d["event"] == "gun_truth_delta":
                deltas[ev] = det
            elif d["event"] == "schedule_match":
                st = det.get("start_time", "")
                try:
                    sched[ev] = datetime.fromisoformat(st).timestamp()
                except Exception:
                    pass

    # observed_starts truth (for non-te fires + the blind class)
    te_truth = {}
    try:
        con = sqlite3.connect("file:%s?mode=ro" % (ROOT / "tennis.db"), uri=True,
                              timeout=2)
        rows = con.execute(
            "SELECT player1, player2, kalshi_ticker, first_inplay_at"
            " FROM observed_starts WHERE first_inplay_at >= ?",
            (datetime.fromtimestamp(day0, ET).strftime("%Y-%m-%d %H:%M:%S"),)
        ).fetchall()
        con.close()
    except Exception as e:
        rows = []
        print("observed_starts unavailable: %s" % str(e)[:80])
    known_events = set(fires) | set(sched)
    for p1, p2, kcode, fia in rows:
        codes = {kcode.upper()} if kcode else set()
        for nm in (p1 or "", p2 or ""):
            for part in nm.replace(".", " ").replace(",", " ").split():
                if len(part) >= 3:
                    codes.add(part[:3].upper())
        # the event tail's last 6 chars are the two 3-letter leg codes; match
        # exact-position only (substring would collide on date tokens like JUL)
        hits = []
        for ev in known_events:
            pair = ev.rsplit("-", 1)[-1][-6:].upper()
            if any(c == pair[:3] or c == pair[3:] for c in codes if len(c) == 3):
                hits.append(ev)
        if len(hits) == 1:
            try:
                te_truth[hits[0]] = datetime.strptime(
                    fia, "%Y-%m-%d %H:%M:%S").replace(tzinfo=ET).timestamp()
            except Exception:
                pass

    lines, per_cat = [], defaultdict(lambda: {"n": 0, "hit3": 0, "deltas": [],
                                              "miss": [], "catchup": 0})
    lines.append("| event | cat | scheduled | gun fired | gun_source | fire_class | vol30@fire | truth | truth_src | delta_min |")
    lines.append("|---|---|---|---|---|---|---|---|---|---|")
    for ev in sorted(set(fires) | set(te_truth)):
        c = cat_of(ev)
        if not c:
            continue
        f = fires.get(ev)
        truth_ts, truth_src = None, "--"
        if f and f["source"] == "te_scoreboard":
            t0 = f["ts"] - 3 * 3600
            truth_ts = tape_onset(ev, t0, f["ts"] + 3600)
            truth_src = "tape_onset"
        elif ev in te_truth:
            truth_ts, truth_src = te_truth[ev], "te_scoreboard"
        delta = (round((f["ts"] - truth_ts) / 60.0, 1)
                 if (f and truth_ts) else None)
        fclass = f.get("fire_class", "?") if f else "--"
        lines.append("| %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (
            ev.split("-", 1)[-1], c, et_str(sched.get(ev)),
            et_str(f["ts"]) if f else "NO FIRE",
            f["source"] if f else "--", fclass,
            (f.get("vol30") if f else None) if f and f.get("vol30") is not None else "--",
            et_str(truth_ts), truth_src,
            delta if delta is not None else "--"))
        r = per_cat[c]
        if truth_ts or f:
            r["n"] += 1
        if f and fclass == "CATCH-UP":
            r["catchup"] += 1
        # the pre-registered +/-3-min pass bar grades FRESH fires only
        if delta is not None and fclass == "FRESH":
            r["deltas"].append(abs(delta))
            if abs(delta) <= PASS_TOL_MIN:
                r["hit3"] += 1
        if not f and truth_ts:
            r["miss"].append(ev.split("-", 1)[-1])

    summary = []
    for c, r in sorted(per_cat.items()):
        dl = sorted(r["deltas"])
        med = dl[len(dl) // 2] if dl else None
        summary.append("%s n=%d FRESH-within±3min=%d/%d med|Δ|=%s catchup=%d misses=[%s]" % (
            c, r["n"], r["hit3"], len(dl),
            ("%.1fm" % med) if med is not None else "--", r["catchup"],
            ",".join(r["miss"][:6]) + ("…" if len(r["miss"]) > 6 else "")))
    out = "# GUN SCORECARD %s\n\n%s\n\n%s\n" % (
        now.strftime("%Y-%m-%d %I:%M %p ET"), "\n".join(lines),
        "\n".join("- " + s for s in summary))
    print(out)

    if "--nightly" in sys.argv:
        d = ROOT.parent / ".claude" / "gun_scorecard"
        d.mkdir(parents=True, exist_ok=True)
        (d / ("GUN_SCORECARD_%s.md" % day)).write_text(out, encoding="utf-8")
        np = ROOT.parent / ".claude" / "live_20260705" / "NIGHTLY_PASS.md"
        try:
            with open(np, "a", encoding="utf-8") as fh:
                fh.write("\nGUN SCORECARD %s: %s\n" % (day, " | ".join(summary)))
        except OSError:
            pass
        try:
            subprocess.run(["git", "-C", str(ROOT.parent), "add",
                            str(d), str(np)], check=False)
            subprocess.run(["git", "-C", str(ROOT.parent), "commit", "-m",
                            "GUN SCORECARD %s (nightly tripwire)" % day],
                           check=False)
            subprocess.run(["git", "-C", str(ROOT.parent), "push", "origin",
                            "HEAD"], check=False)
        except Exception:
            pass


if __name__ == "__main__":
    main()
