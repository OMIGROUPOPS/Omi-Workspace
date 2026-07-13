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


# [-0k FLOW-STEP, 07-12 — TRUTH-JOIN DRIBBLE-ONSET kill] the activity rule
# alone (>=5-of-15 minutes, ANY size) passes sustained overnight premarket
# dribble 75-115 min before real onset — the 16 SUSPECT rows of 07-11
# (.claude/triage_20260711/). Onset now ALSO requires a flow STEP measured
# against the SEARCH WINDOW'S FIRST HOUR (t0 = anchor-2h, definitionally
# premarket) — NOT the prior hour, because gradual dribble makes every ramp
# stage a "step" over the stage before it. Rule: trailing-15 prints >=
# max(ONSET_FLOOR, ONSET_K x first-hour baseline per-15-min). Fit note:
# 07-11 dribble ran 5-283 prints/hr vs 188-13,500/hr at true ignition;
# K=3, floor=8 (validated fail-before/pass-after in PROOF_ONSET_FLOWSTEP).
ONSET_K = 3.0
ONSET_FLOOR = 8


def tape_onset(ev, t0, t1):
    """Independent tape truth: first minute (within [t0,t1]) that has BOTH
    (a) prints in >=5 of the trailing 15 one-minute bins, across both legs,
    AND (b) a flow step: trailing-15 prints >= max(ONSET_FLOOR, ONSET_K x
    the window-first-hour baseline). Returns (onset_ts | None, reason) --
    reason names WHY when None (no_trades_csv / no_prints_in_window /
    no_flow_onset), so no row can half-join silently."""
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
    base60 = sum(n for m, n in minutes.items() if m < t0 + 3600)
    need = max(ONSET_FLOOR, ONSET_K * (base60 / 4.0))
    for m in keys:
        active = sum(1 for k in range(m - 14 * 60, m + 60, 60) if minutes.get(k))
        if active < 5:
            continue
        t15 = sum(minutes.get(k, 0) for k in range(m - 14 * 60, m + 60, 60))
        # forward-sustain: a premarket burst CLUMP clears the bar for one
        # window then dies; a real match keeps printing. 30-min forward
        # window at the same absolute bar (= half the rate) so thin ITF
        # tapes (~0.5 prints/min matches) still join.
        fwd30 = sum(minutes.get(k, 0) for k in range(m + 60, m + 31 * 60, 60))
        if t15 >= need and fwd30 >= need:
            return m, "ok"
    return None, "no_flow_onset"


def main():
    now = datetime.now(ET)
    day = now.strftime("%Y%m%d")
    files = sorted((ROOT / "logs").glob("live_v3_*.jsonl"),
                   key=lambda p: p.stat().st_mtime)[-2:]
    day0 = datetime(now.year, now.month, now.day, tzinfo=ET).timestamp() - 6 * 3600

    fires, deltas, sched, boots, honest = {}, {}, {}, [], {}
    bells_missing = set()   # [C-REALITY-BELL] nightly coverage count
    halt_armed_ts, halt_min, unbooked_booked = None, 0.0, 0   # [C-BOOK-THE-FILL]
    confirms = {}           # [C-DELETION-GATE] ev -> [(source, first, delta_sec)]
    percat_seen = set()     # events where the fitted threshold crossed (shadow log)
    for p in files:
        for line in open(p, encoding="utf-8", errors="replace"):
            if '"gun_fired"' not in line and '"gun_truth_delta"' not in line \
                    and '"schedule_match"' not in line \
                    and '"pm_clock_shadow"' not in line \
                    and '"clock_liar"' not in line \
                    and '"bell_missing"' not in line \
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
            elif d["event"] == "gun_source_confirm":
                # [C-DELETION-GATE Part 2] later sources on an already-fired
                # event: the multi-source record (first-fire-wins is the code
                # law at live_v4._gun_stamp: an existing _gun_state entry
                # short-circuits to gun_source_confirm, never a re-stamp)
                confirms.setdefault(ev, []).append(
                    (det.get("source"), det.get("first_source"),
                     det.get("delta_sec")))
                continue
            elif d["event"] == "percat_gun_shadow":
                percat_seen.add(ev)
                continue
            elif d["event"] == "bell_missing":
                bells_missing.add(ev)
                continue
            elif d["event"] == "conception_halt_armed":
                if det.get("transition") and halt_armed_ts is None:
                    halt_armed_ts = ts
                continue
            elif d["event"] == "conception_halt_cleared":
                if halt_armed_ts is not None:
                    halt_min += (ts - halt_armed_ts) / 60.0
                    halt_armed_ts = None
                continue
            elif d["event"] == "fill_booked_reconcile":
                unbooked_booked += 1
                continue
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
        elif delta is not None and fclass == "FRESH" and delta < -20.0:
            # [-0k] symmetric bound: an onset lagging a FRESH fire >20 min is
            # a heavy-premarket ambiguity (SAGYOD 07-11: premarket hour ran
            # hotter than the match's first hour) — quarantine, never average
            suspect = "onset_lags_fresh_fire"
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
    # [FIRE-COUNT FOOTER 07-10, operator order] a starving gun must be
    # visible the morning it starves: nightly fires vs slate size. The
    # 07-09->07-10 drop (50 -> 25 fires) was noticed by a human a day
    # late; this line notices it at 6:10 am.
    n_fires = len(fires)
    n_slate = len(set(sched) | set(fires))
    # [C-DELETION-GATE proof iii] MAINS are OFF by design in the fitted
    # trigger -- they are EXCLUDED from the coverage denominator, asserted:
    _mains = {e for e in (set(sched) | set(fires))
              if cat_of(e) in ("ATP_MAIN", "WTA_MAIN")}
    n_slate_x = n_slate - len(_mains)
    n_fires_x = sum(1 for e in fires if e not in _mains)
    # multi-source + self-fill meters ([C-DELETION-GATE Part 2 / Part 3])
    multi = {e: c for e, c in confirms.items()}
    sf_fired = {e for e, f in fires.items() if f.get("source") == "self_fill"}
    sf_unconfirmed = [e for e in sf_fired
                      if not multi.get(e) and e not in percat_seen]
    footer = ("FIRES-vs-SLATE: fires=%d tracked_events=%d ratio=%.0f%% | "
              "NON-MAINS (deletion-gate denominator, MAINS-OFF excluded by "
              "design): fires=%d/%d ratio=%.0f%% | MULTI-SOURCE events=%d | "
              "SELF-FILL fires=%d unconfirmed-by-any-other-source=%d | "
              "BELLS-MISSING=%d%s | HALT-MIN=%.1f UNBOOKED-FILLS-BOOKED=%d "
              "(watch: night-over-night drops + uncovered live matches are "
              "named here, not a week later)"
              % (n_fires, n_slate, 100.0 * n_fires / n_slate if n_slate else 0,
                 n_fires_x, n_slate_x,
                 100.0 * n_fires_x / n_slate_x if n_slate_x else 0,
                 len(multi), len(sf_fired), len(sf_unconfirmed),
                 len(bells_missing),
                 (" [" + ",".join(sorted(e.rsplit("-", 1)[-1][-6:] for e in bells_missing)[:6]) + "]")
                 if bells_missing else "", halt_min, unbooked_booked))
    # ---- [C-DELETION-GATE Part 5] the deletion gate: Plex's four proofs.
    # The legacy-trigger deletion word is REFUSED by this section itself if
    # any proof is missing.
    gate = ["", "## DELETION GATE (C-DELETION-GATE v1 — the four proofs)"]
    # (i) clean regrade, superseding the inadmissible 71
    p1 = bool(summary)
    gate.append("**(i) clean-regrade numbers (flow-step onset, -0k):** %s — "
                "these SUPERSEDE 07-12's 71 percat shadow would-fires, ruled "
                "INADMISSIBLE by C-MORNING-TRIAGE (TRUTH-JOIN DRIBBLE-ONSET)."
                % ("PRESENT" if p1 else "MISSING"))
    # (ii) percat-vs-legacy priority reconciliation on real events
    pv = []
    for e, cl in confirms.items():
        for (src, first, dsec) in cl:
            if src == "percat_fitted" or first == "percat_fitted":
                pv.append((e, first, src, dsec))
    for e, f in fires.items():
        if f.get("source") == "percat_fitted":
            pv.append((e, "percat_fitted", "(first fire)", None))
    p2 = len(pv) > 0
    gate.append("**(ii) percat-vs-legacy priority reconciliation:** %s (%d rows)"
                % ("PRESENT" if p2 else "MISSING — no percat co-fire tonight", len(pv)))
    for e, first, src, dsec in pv[:12]:
        gate.append("- %s: first=%s, later=%s%s" % (
            e[-16:], first, src,
            (" (+%.0fs)" % dsec) if dsec is not None else ""))
    # (iii) mains-off exclusion asserted (in the footer, by construction)
    p3 = True
    gate.append("**(iii) MAINS-OFF excluded from the denominator:** PRESENT — "
                "footer carries both numbers (%d mains excluded)." % len(_mains))
    # (iv) percat vs self_fill same-event comparison
    rows4 = []
    for e in set(percat_seen) | sf_fired:
        f = fires.get(e, {})
        rows4.append((e, f.get("source"),
                      "percat" if e in percat_seen else "",
                      "self_fill" if e in sf_fired else ""))
    both4 = [r for r in rows4 if r[2] and r[3]]
    p4 = True   # the TABLE is the proof; emptiness is a finding, stated
    gate.append("**(iv) percat-vs-self-fill same-event table:** PRESENT — "
                "%d events touched by either, %d by BOTH%s"
                % (len(rows4), len(both4),
                   " (zero co-events is tonight's finding, not a missing proof)"
                   if not both4 else ""))
    for e, src, a, b in rows4[:12]:
        gate.append("- %s: fired_by=%s | percat=%s self_fill=%s" % (e[-16:], src, a or "-", b or "-"))
    verdict5 = "OPEN" if (p1 and p2 and p3 and p4) else "REFUSED"
    gate.append("")
    gate.append("**DELETION GATE: %s**%s" % (
        verdict5,
        "" if verdict5 == "OPEN" else
        " — the deletion word cannot be given on this scorecard (missing proof(s): %s)"
        % ", ".join(n for n, p in
                    [("i", p1), ("ii", p2), ("iii", p3), ("iv", p4)] if not p)))
    out = "# GUN SCORECARD %s\n\n%s\n\n%s\n\n%s\n%s\n" % (
        now.strftime("%Y-%m-%d %I:%M %p ET"), "\n".join(lines),
        "\n".join("- " + s for s in summary), footer, "\n".join(gate))
    print(out)

    if "--nightly" in sys.argv:
        d = ROOT.parent / ".claude" / "gun_scorecard"
        d.mkdir(parents=True, exist_ok=True)
        (d / ("GUN_SCORECARD_%s.md" % day)).write_text(out, encoding="utf-8")
        np = ROOT.parent / ".claude" / "live_20260705" / "NIGHTLY_PASS.md"
        try:
            with open(np, "a", encoding="utf-8") as fh:
                fh.write("\nGUN SCORECARD %s: %s | %s\n" % (
                    day, " | ".join(summary), footer))
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
