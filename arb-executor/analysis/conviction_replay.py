#!/usr/bin/env python3
"""C-CONVICTION-REPLAY Parts 3a/4/5 — acceptance gate, slate replay, report.
Part 3a IS the gate: any test failure -> the replay DOES NOT RUN (constraint #1,
build-before-rerun) and this script says exactly that and exits nonzero."""
import glob, gzip, json, sys
from collections import defaultdict
from datetime import datetime, timezone, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from conviction_composer import Composer

ROOT = Path(__file__).resolve().parent.parent
ET = timezone(timedelta(hours=-4))
CAT = {"KXATPMATCH": "ATP_MAIN", "KXWTAMATCH": "WTA_MAIN",
       "KXATPCHALLENGERMATCH": "ATP_CHALL", "KXWTACHALLENGERMATCH": "WTA_CHALL",
       "KXITFMATCH": "ITF_M", "KXITFWMATCH": "ITF_W"}
def cat_of(tk):
    for k, v in CAT.items():
        if tk.startswith(k):
            return v
    return None


def leg_observations(tk, t0=None, t1=None):
    """(ts, 'print', px) from trades CSV + ('mid') from tight-book ticks."""
    obs = []
    for f in glob.glob(str(ROOT / "analysis/trades" / (tk + ".csv*"))):
        op = gzip.open if f.endswith(".gz") else open
        with op(f, "rt", encoding="utf-8", errors="replace") as fh:
            next(fh, None)
            for ln in fh:
                p = ln.split(",")
                try:
                    ts = datetime.strptime(p[0], "%Y-%m-%d %I:%M:%S %p").replace(tzinfo=ET).timestamp()
                    obs.append((ts, "print", float(p[2])))
                except Exception:
                    continue
    for f in glob.glob(str(ROOT / "analysis/premarket_ticks" / (tk + ".csv*"))):
        op = gzip.open if f.endswith(".gz") else open
        with op(f, "rt", encoding="utf-8", errors="replace") as fh:
            next(fh, None)
            n = 0
            for ln in fh:
                p = ln.split(",")
                if len(p) < 23:
                    continue
                n += 1
                if n % 10:      # thin the mid stream 10:1 (prints stay primary)
                    continue
                try:
                    ts = datetime.strptime(p[0], "%Y-%m-%d %I:%M:%S %p").replace(tzinfo=ET).timestamp()
                    bid, ask, mid = float(p[2]), float(p[12]), float(p[22])
                    if 0 < ask - bid <= 3:
                        obs.append((ts, "mid", mid))
                except Exception:
                    continue
    obs.sort()
    if t0 or t1:
        obs = [o for o in obs if (t0 or 0) <= o[0] <= (t1 or 9e12)]
    return obs


def gate_3a(c):
    results = {}
    # (i) HONESTY: no admissible models -> NO-OPINION, not a number
    r = c.discovery_prior("ATP_MAIN", 55)
    results["honesty"] = (r["opinion"] == "NO-OPINION" and "G1" in r.get("missing", ""),
                          r.get("missing", str(r))[:120])
    # (ii) POSTERIOR: Dellien confidence collapses on the live prints
    prior = c.discovery_prior("ATP_CHALL", 59, lifetime_vol=5000)
    obs = leg_observations("KXATPCHALLENGERMATCH-26JUL10SAIDEL-DEL",
                           t0=1783695000, t1=1783702800)   # 10:50a -> 1:00p
    series = c.tick_posterior(prior, obs)
    if prior.get("opinion") == "PRIOR" and series:
        peak = max(x[1] for x in series[: len(series) // 2] or series)
        trough = min(x[1] for x in series)
        results["posterior"] = (peak - trough >= 0.20 and trough < 0.40,
                                "conf peak %.2f -> trough %.2f over %d obs" % (peak, trough, len(series)))
    else:
        results["posterior"] = (False, "no prior/series")
    # (iii) ERA: an ITF event offered archive anchors refuses them
    r = c.discovery_prior("ITF_W", 30, offered_anchor_era="archive")
    results["era"] = (r["opinion"] == "NO-OPINION" and "REFUSED" in r.get("missing", ""),
                      r.get("missing", "")[:120])
    return results


def main():
    c = Composer()
    res = gate_3a(c)
    print("== PART 3a GATE ==")
    ok = True
    for name, (passed, detail) in res.items():
        print(" %s: %s  (%s)" % (name, "PASS" if passed else "FAIL", detail))
        ok = ok and passed
    if not ok:
        print("GATE FAILED -- the replay DOES NOT RUN (constraint #1: build before rerun)")
        sys.exit(1)
    print("gate PASS -> Part 4 replay authorized")

    # ---- PART 4: July 10 slate replay (every filled entry since midnight ET) ----
    day0 = datetime(2026, 7, 10, tzinfo=ET).timestamp()
    trades, settles, exits, unlocked, pair97 = [], {}, {}, {}, set()
    log = ROOT / "logs" / "live_v3_20260710.jsonl"
    for line in open(log, encoding="utf-8", errors="replace"):
        if not any(k in line for k in ('"entry_filled"', '"settled"', '"exit_filled"',
                                       '"early_unlock_open"', '"reaim_sibling_arrival"',
                                       '"sibling_repost_placed"')):
            continue
        try:
            d = json.loads(line)
        except ValueError:
            continue
        ts, det, tk = d.get("ts_epoch", 0), d.get("details") or {}, d.get("ticker", "")
        if ts < day0:
            continue
        e = d["event"]
        if e == "entry_filled" and tk:
            trades.append({"tk": tk, "ts": ts, "px": det.get("fill_price"),
                           "qty": det.get("qty", 5), "cycle": det.get("cycle", 1),
                           "in_play": det.get("in_play", False)})
        elif e == "settled" and tk:
            settles[tk] = det
        elif e == "exit_filled" and tk:
            exits.setdefault(tk, []).append(det)
        elif e == "early_unlock_open":
            unlocked[det.get("event", "")] = det.get("vol")
        elif e in ("reaim_sibling_arrival", "sibling_repost_placed"):
            pair97.add(d.get("ticker") or "")
    trades.sort(key=lambda t: t["ts"])
    rows, stats = [], defaultdict(lambda: defaultdict(int))
    obs_cache = {}
    for i, t in enumerate(trades, 1):
        tid = "T-20260710-%04d" % i
        tk, cat = t["tk"], cat_of(t["tk"])
        et = tk.rsplit("-", 1)[0]
        if tk not in obs_cache:
            obs_cache[tk] = leg_observations(tk)
        obs = [o for o in obs_cache[tk] if o[0] <= t["ts"]]
        disc_px = obs[0][2] if obs else t["px"]
        prior = c.discovery_prior(cat, disc_px, lifetime_vol=unlocked.get(et))
        if prior.get("opinion") != "PRIOR":
            grade, why, conf = "NO-OPINION", prior.get("missing", ""), None
        else:
            series = c.tick_posterior(prior, obs)
            conf = series[-1][1] if series else prior["confidence"]
            edge = conf * 100 - t["px"]
            if edge >= -2:
                grade, why = "AGREE", "posterior %.2f vs paid %d (edge %+.1f)" % (conf, t["px"], edge)
            else:
                grade, why = "WOULD-REFUSE", ("conviction_gap: posterior %.2f says the leg is "
                                              "worth %.0f, we paid %d (%.1f over conviction)"
                                              % (conf, conf * 100, t["px"], -edge))
        # dollars where settlement/exit prices the disagreement
        pnl = None
        st = settles.get(tk)
        if st is not None:
            pnl = st.get("pnl_cents")
        elif exits.get(tk):
            pnl = sum(x.get("pnl_cents", 0) for x in exits[tk])
        legacy = "pair97" if tk in pair97 else ""
        rows.append({"id": tid, "tk": tk, "cat": cat, "ts_et": datetime.fromtimestamp(
            t["ts"], ET).strftime("%I:%M:%S %p"), "px": t["px"], "cycle": t["cycle"],
            "in_play": t.get("in_play", False), "grade": grade, "why": why[:160],
            "posterior": conf, "legacy_constant": legacy, "pnl_cents": pnl})
        stats[cat][grade] += 1
        if legacy:
            stats[cat]["pair97_touched"] += 1
    out = {"generated": datetime.now(ET).strftime("%Y-%m-%d %I:%M %p ET"),
           "gate_3a": {k: {"pass": v[0], "detail": v[1]} for k, v in res.items()},
           "n_trades": len(trades), "rows": rows,
           "per_cat": {k: dict(v) for k, v in stats.items()}}
    op = ROOT.parent / ".claude/conviction_20260710/REPLAY_RESULTS.json"
    op.parent.mkdir(parents=True, exist_ok=True)
    op.write_text(json.dumps(out, indent=1), encoding="utf-8")
    print("== PART 4 REPLAY == %d trades -> %s" % (len(trades), op))
    for cat, s in sorted(stats.items()):
        print(" ", cat, dict(s))


if __name__ == "__main__":
    main()
