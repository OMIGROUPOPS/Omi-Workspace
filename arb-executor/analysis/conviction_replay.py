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
    # (iv) RANGE-LAYER honesty [Part 2b REVISED]: an empty/thin cell returns
    # NO-OPINION with the cell NAMED; a populated cell returns the fitted
    # prior with n + citation
    r4a = c.range_prior("ITF_M", "underdog", 3, 97.0)   # absurd corner: empty
    ok4a = r4a["opinion"] == "NO-OPINION" and "cell" in str(r4a)
    r4b = None
    for k, v in list(c.range_cells.items())[:200]:
        if v.get("n", 0) >= 5:
            cat, side, b, pc = k.split("|")
            px = {"le25": 20, "26_50": 40, "51_75": 60, "ge75": 80}[pc]
            frm = {"deep_disc": -6, "disc": -3, "at_mid": 0, "over": 3, "deep_over": 6}[b]
            r4b = c.range_prior(cat, side, px, px - frm)
            break
    ok4b = bool(r4b) and r4b.get("opinion") == "PRIOR" and "citation" in r4b
    results["range_layer"] = (ok4a and ok4b,
                              "empty->NO-OPINION ok=%s; populated->PRIOR ok=%s (%s)"
                              % (ok4a, ok4b, (r4b or {}).get("cell", "no populated cell found")))
    return results


def main():
    # [C-NIGHTLY-ADJUDICATION] --date YYYYMMDD (default: the day that just
    # closed when run 00:00-06:00 ET, else today); --nightly commits
    # ADJUDICATION_<date>.md + NIGHTLY_PASS footer + git push.
    now = datetime.now(ET)
    ymd = None
    for i, a in enumerate(sys.argv):
        if a == "--date" and i + 1 < len(sys.argv):
            ymd = sys.argv[i + 1]
    if ymd is None:
        ref = now.timestamp() - (6 * 3600 if now.hour < 6 else 0)
        ymd = datetime.fromtimestamp(ref, ET).strftime("%Y%m%d")
    dd = datetime.strptime(ymd, "%Y%m%d")
    c = Composer()
    res = gate_3a(c)
    print("== PART 3a GATE ==")
    ok = True
    for name, (passed, detail) in res.items():
        print(" %s: %s  (%s)" % (name, "PASS" if passed else "FAIL", detail))
        ok = ok and passed
    if not ok:
        print("GATE FAILED -- the replay DOES NOT RUN (constraint #1: build before rerun)")
        if "--nightly" in sys.argv:
            op = ROOT.parent / (".claude/adjudication/ADJUDICATION_%s.md" % ymd)
            op.parent.mkdir(parents=True, exist_ok=True)
            op.write_text(
                "# ADJUDICATION %s\n\nGATE FAILED (3a): %s\n"
                "The replay did not run (constraint #1)." % (
                    ymd, {k: v[1] for k, v in res.items()}), encoding="utf-8")
        sys.exit(1)
    print("gate PASS -> Part 4 replay authorized")

    # ---- PART 4: the slate replay (every filled entry in the day, ET) ----
    day0 = datetime(dd.year, dd.month, dd.day, tzinfo=ET).timestamp()
    trades, settles, exits, unlocked, pair97 = [], {}, {}, {}, set()
    day1 = day0 + 24 * 3600
    log = ROOT / "logs" / ("live_v3_%s.jsonl" % ymd)
    if not log.exists():
        print("no log for %s" % ymd)
        sys.exit(0)
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
        if not (day0 <= ts < day1):
            continue
        e = d["event"]
        if e == "entry_filled" and tk:
            # [C-DAYLIGHT-ROOTS] qty here is the INCREMENT (new_fills), never
            # the cumulative `qty` field -- summing cumulative made the
            # reconciliation column report 7-vs-5 on partial-fill legs
            # (VANKOI: 2-then-5 cumulative = 7; increments 2+3 = 5 = exchange)
            trades.append({"tk": tk, "ts": ts, "px": det.get("fill_price"),
                           "qty": det.get("new_fills", det.get("qty", 5)),
                           "cycle": det.get("cycle", 1),
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
        tid = "T-%s-%04d" % (ymd, i)
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
            t["prior"] = prior
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
        t.update({"id": tid, "cat": cat, "prior": t.get("prior")})
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
    op = ROOT.parent / (".claude/adjudication/RESULTS_%s.json" % ymd)
    op.parent.mkdir(parents=True, exist_ok=True)
    op.write_text(json.dumps(out, indent=1), encoding="utf-8")
    print("== PART 4 REPLAY == %d trades -> %s" % (len(trades), op))
    for cat, s2 in sorted(stats.items()):
        print(" ", cat, dict(s2))
    # ---- the ADJUDICATION report (the migration meter, self-printing) ----
    n = len(rows)
    ag = sum(1 for r in rows if r["grade"] == "AGREE")
    wr = sum(1 for r in rows if r["grade"] == "WOULD-REFUSE")
    no = sum(1 for r in rows if r["grade"] == "NO-OPINION")
    p97n = sum(1 for r in rows if r["legacy_constant"] == "pair97")
    L = ["# ADJUDICATION %s (nightly conviction replay; gate 3a passed)" % ymd, "",
         "| id | ticker | cat | fill ET | paid | cyc | grade | posterior | legacy | pnl¢ |",
         "|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        L.append("| %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (
            r["id"], r["tk"].replace("KX", "")[:28], r["cat"], r["ts_et"], r["px"],
            r["cycle"], r["grade"],
            ("%.2f" % r["posterior"]) if r["posterior"] is not None else "—",
            r["legacy_constant"] or "", r["pnl_cents"] if r["pnl_cents"] is not None else "open"))
    if n:
        L += ["", "**MIGRATION METER: fitted-conviction AGREE %d/%d (%.1f%%) | "
                  "WOULD-REFUSE %d | NO-OPINION %d | pair-97 touched %d (%.1f%%)**"
              % (ag, n, 100.0 * ag / n, wr, no, p97n, 100.0 * p97n / n),
             "", "Per category: " + " | ".join(
                 "%s A%d/R%d/N%d p97:%d" % (cat, s3.get("AGREE", 0),
                                            s3.get("WOULD-REFUSE", 0),
                                            s3.get("NO-OPINION", 0),
                                            s3.get("pair97_touched", 0))
                 for cat, s3 in sorted(stats.items()))]
    md = ROOT.parent / (".claude/adjudication/ADJUDICATION_%s.md" % ymd)
    md.write_text("\n".join(L), encoding="utf-8")
    print("adjudication ->", md)
    # [C-FULL-SLATE-REVIEW] the nightly instrument inherits the full depth:
    # per-step L1-L9 grades, the no-fill cohort, exchange truth, class filings
    try:
        import full_slate_review as fsr
        per_tk, per_ev = fsr.collect_day(ymd, log)
        fout, fsummary, fixq = fsr.run(ymd, trades, per_tk, per_ev, c,
                                       obs_cache, settles, leg_observations)
        print("full-slate ->", fout)
        with open(md, "a", encoding="utf-8") as fh:
            fh.write("\n\n## FULL-SLATE SUMMARY\n%s\n" % fsummary)
    except Exception:
        import traceback
        print("full-slate ERROR:", traceback.format_exc()[-400:])
    if "--nightly" in sys.argv:
        import subprocess
        np = ROOT.parent / ".claude" / "live_20260705" / "NIGHTLY_PASS.md"
        try:
            with open(np, "a", encoding="utf-8") as fh:
                fh.write("\nADJUDICATION %s: AGREE %d/%d | REFUSE %d |"
                         " NO-OPINION %d | pair97 %d\n"
                         % (ymd, ag, n, wr, no, p97n))
        except OSError:
            pass
        for cmd in (["git", "-C", str(ROOT.parent), "add", str(md.parent), str(np)],
                    ["git", "-C", str(ROOT.parent), "commit", "-m",
                     "ADJUDICATION %s (nightly conviction replay)" % ymd],
                    ["git", "-C", str(ROOT.parent), "push", "origin", "HEAD"]):
            subprocess.run(cmd, check=False)


if __name__ == "__main__":
    main()
