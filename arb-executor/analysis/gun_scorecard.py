#!/usr/bin/env python3
"""GUN SCORECARD [C-FUSED-GUN 2026-07-08] -- the standing tripwire renderer.

Every gun fire logs gun_source (+ gun_truth_delta when the scoreboard row
arrives). This script grades the night: per-cat detection %, median
|truth delta|, misses NAMED (never averaged away).

[TRUTH-JOIN FIX 2026-07-09] Truth is FIRE-SOURCE-INDEPENDENT: every fire,
whatever fired it, grades against the match's certification-grade tape
onset (trades CSV: first minute with prints in >=5 of the trailing 15
one-minute bins), with the observed_starts bank as fallback truth. The
onset search window is centered on the ANCHOR HIERARCHY's honest start
(clock_liar te_honest_start / pm_clock_shadow honest_start, i.e. the
datemiss-aware clock), NOT the raw fire time -- day-boundary tickers
(the MOCTAN class: truth joined 102 min before its own FRESH fire) join
via the honest clock or get flagged SUSPECT and are never averaged in.
A row either grades or is named UNJOINABLE with its reason -- no silent
halves. GRANULARITY LAW: the 349 training-grade recovered corpus bells
are FORBIDDEN as truth here; this script never reads shape_corpus.
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
    >=5 of the trailing 15 one-minute bins, across both legs.
    Returns (onset_ts | None, reason) -- reason names WHY when None
    (no_trades_csv / no_prints_in_window / no_flow_onset), so no row can
    half-join silently."""
    minutes = defaultdict(int)
    n_files = 0
    for f in TRADES.glob(ev + "-*.csv*"):
        n_files += 1
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
    if n_files == 0:
        return None, "no_trades_csv"
    if not minutes:
        return None, "no_prints_in_window"
    keys = sorted(minutes)
    for m in keys:
        active = sum(1 for k in range(m - 14 * 60, m + 60, 60) if minutes.get(k))
        if active >= 5:
            return m, "ok"
    return None, "no_flow_onset"


def main():
    now = datetime.now(ET)
    day = now.strftime("%Y%m%d")
    files = sorted((ROOT / "logs").glob("live_v3_*.jsonl"),
                   key=lambda p: p.stat().st_mtime)[-2:]
    day0 = datetime(now.year, now.month, now.day, tzinfo=ET).timestamp() - 6 * 3600

    fires, deltas, sched, boots, honest = {}, {}, {}, [], {}
    for p in files:
        for line in open(p, encoding="utf-8", errors="replace"):
            if '"gun_fired"' not in line and '"gun_truth_delta"' not in line \
                    and '"schedule_match"' not in line \
                    and '"pm_clock_shadow"' not in line \
                    and '"clock_liar"' not in line \
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
            elif d["event"] == "pm_clock_shadow":
                # [TRUTH-JOIN FIX 07-09] the datemiss-aware honest anchor:
                # centers the onset search on lying-clock/day-boundary events
                # (MOCTAN class: raw ticker date joined an onset 102 min
                # before its own FRESH fire). Shadow rows (flag-gated) OR
                # armed-mode clock_liar rows both carry it.
                hs = det.get("honest_start")
                if hs:
                    try:
                        honest[ev] = datetime.fromisoformat(hs).timestamp()
                    except Exception:
                        pass
            elif d["event"] == "clock_liar":
                hs = det.get("te_honest_start")
                if hs:
                    try:
                        honest[ev] = float(hs)
                    except (TypeError, ValueError):
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
    # [TRUTH-JOIN FIX 07-09] both-leg matcher: each half of the event tail's
    # 6-char pair code must match a DIFFERENT player's name-token prefixes
    # (either order). The old any-single-code rule joined ~nothing uniquely
    # (46/50 fires never received truth). Single-leg unique is the fallback,
    # marked as such. Exact-position only (substring collides on JUL etc.).
    known_events = set(fires) | set(sched)
    ev_pair = {ev: ev.rsplit("-", 1)[-1][-6:].upper() for ev in known_events}
    te_grade = {}
    for p1, p2, kcode, fia in rows:
        sides = []
        for nm in (p1 or "", p2 or ""):
            s = set()
            for part in nm.replace(".", " ").replace(",", " ").replace("-", " ").split():
                if len(part) >= 3:
                    s.add(part[:3].upper())
            sides.append(s)
        kc = (kcode or "").upper()
        both, single = [], []
        for ev, pair in ev_pair.items():
            a, b = pair[:3], pair[3:]
            if ((a in sides[0] and b in sides[1])
                    or (a in sides[1] and b in sides[0])):
                both.append(ev)
            elif (any(a in s or b in s for s in sides) or kc in (a, b)):
                single.append(ev)
        hits = both if both else single
        if len(hits) == 1:
            try:
                t = datetime.strptime(
                    fia, "%Y-%m-%d %H:%M:%S").replace(tzinfo=ET).timestamp()
            except Exception:
                continue
            evh = hits[0]
            if evh not in te_truth or t < te_truth[evh]:
                te_truth[evh] = t
                te_grade[evh] = "both-leg" if both else "single-leg"

    lines, per_cat = [], defaultdict(lambda: {
        "n": 0, "hit3": 0, "deltas": [], "miss": [], "catchup": 0,
        "fresh": 0, "suspect": [], "unjoin": 0})
    lines.append("| event | cat | scheduled | gun fired | gun_source | fire_class | vol30@fire | truth | truth_src | delta_min |")
    lines.append("|---|---|---|---|---|---|---|---|---|---|")
    for ev in sorted(set(fires) | set(te_truth)):
        c = cat_of(ev)
        if not c:
            continue
        f = fires.get(ev)
        fclass = f.get("fire_class", "?") if f else "--"
        # [TRUTH-JOIN FIX 07-09] truth is FIRE-SOURCE-INDEPENDENT: every
        # fire grades against the match's own tape onset, searched in a
        # window centered on the ANCHOR (honest datemiss-aware clock >
        # schedule > fire time as last resort), never on the raw fire
        # time alone. observed_starts is the fallback truth. A row either
        # grades or is UNJOINABLE with a named reason.
        anchor = honest.get(ev) or sched.get(ev) or (f["ts"] if f else None)
        anchor_src = ("honest" if ev in honest
                      else ("sched" if ev in sched else "fire"))
        truth_ts, truth_src, unjoin = None, "--", None
        if f is not None and anchor is not None:
            w1 = max(anchor + 4 * 3600, f["ts"] + 1800)
            truth_ts, reason = tape_onset(ev, anchor - 2 * 3600, w1)
            if truth_ts is not None:
                truth_src = "tape@" + anchor_src
            else:
                unjoin = reason
        if truth_ts is None and ev in te_truth:
            truth_ts = te_truth[ev]
            truth_src = "obs_starts(%s)" % te_grade.get(ev, "?")
            unjoin = None
        delta = (round((f["ts"] - truth_ts) / 60.0, 1)
                 if (f and truth_ts is not None) else None)
        # SUSPECT: a truth predating its own FRESH fire (>15 min) is a bad
        # join (wrong day / wrong session tape), never averaged in; ditto
        # any join >120 min out on either side.
        suspect = None
        if delta is not None and fclass == "FRESH" and delta > 15.0:
            suspect = "truth_predates_fresh_fire"
        elif delta is not None and abs(delta) > 120.0:
            suspect = "join_out_of_bounds"
        truth_cell = (et_str(truth_ts) if truth_ts is not None
                      else ("UNJOINABLE:" + unjoin if (f and unjoin) else "--"))
        delta_cell = ("%s SUSPECT(%s)" % (delta, suspect) if suspect
                      else (delta if delta is not None else "--"))
        lines.append("| %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (
            ev.split("-", 1)[-1], c, et_str(sched.get(ev)),
            et_str(f["ts"]) if f else "NO FIRE",
            f["source"] if f else "--", fclass,
            (f.get("vol30") if f else None) if f and f.get("vol30") is not None else "--",
            truth_cell, truth_src, delta_cell))
        r = per_cat[c]
        if truth_ts or f:
            r["n"] += 1
        if f and fclass == "CATCH-UP":
            r["catchup"] += 1
        if f and fclass == "FRESH":
            r["fresh"] += 1
        if f and truth_ts is None:
            r["unjoin"] += 1
        if suspect:
            r["suspect"].append(ev.rsplit("-", 1)[-1][-6:])
        # the pre-registered +/-3-min pass bar grades FRESH fires only;
        # suspects are excluded from both the bar and the median
        elif delta is not None and fclass == "FRESH":
            r["deltas"].append(abs(delta))
            if abs(delta) <= PASS_TOL_MIN:
                r["hit3"] += 1
        if not f and truth_ts:
            r["miss"].append(ev.rsplit("-", 1)[-1][-6:])

    summary = []
    for c, r in sorted(per_cat.items()):
        dl = sorted(r["deltas"])
        med = dl[len(dl) // 2] if dl else None
        summary.append(
            "%s n=%d FRESH-within±3min=%d/%d med|Δ|=%s catchup=%d "
            "suspect=[%s] unjoinable=%d misses=[%s]" % (
                c, r["n"], r["hit3"], len(dl),
                ("%.1fm" % med) if med is not None else "--", r["catchup"],
                ",".join(r["suspect"][:4]) + ("…" if len(r["suspect"]) > 4 else ""),
                r["unjoin"],
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
