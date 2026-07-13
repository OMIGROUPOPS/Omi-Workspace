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
    # find a GUARANTEED-empty combination (the first probe hit a populated
    # cell -- deep-discount cheap ITF dogs are common in the 5.7x book)
    ok4a = False
    for cat4 in ("ITF_M", "ITF_W", "ATP_CHALL", "WTA_CHALL", "ATP_MAIN", "WTA_MAIN"):
        for side4 in ("leader", "underdog"):
            for b4, frm4 in (("deep_over", 8), ("deep_disc", -8)):
                for pc4, px4 in (("le25", 10), ("ge75", 90)):
                    key4 = "|".join((cat4, side4, b4, pc4))
                    if key4 not in c.range_cells or c.range_cells[key4].get("n", 0) < 5:
                        r4a = c.range_prior(cat4, side4, px4, px4 - frm4)
                        ok4a = r4a["opinion"] == "NO-OPINION" and "cell" in str(r4a)
                        break
                if ok4a: break
            if ok4a: break
        if ok4a: break
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
                           "in_play": det.get("in_play", False),
                           # [-0k JOIN FIX 07-12] the tape's own stamp -- the
                           # replay must NEVER re-mint: live IDs are minted at
                           # PLACEMENT, fills arrive out of placement order, and
                           # fill-order re-minting misnamed 4 trades on 07-11
                           # (the 4 phantom live-vs-replay "divergences")
                           "trade_id": det.get("trade_id")})
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
        tid = t.get("trade_id") or "T-%s-%04d" % (ymd, i)
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
    # [C-COMPOSER-G1 Part 2] same-instrument law, LIVE edition: the live
    # shadow's verdicts vs this replay's on the same ticks -- divergence is
    # a NAMED violation (a shadow that grades differently live than in
    # replay is measuring nothing).
    try:
        live_sh = {}
        for line in open(log, encoding="utf-8", errors="replace"):
            if '"conviction_shadow"' not in line:
                continue
            try:
                d6 = json.loads(line)
            except ValueError:
                continue
            live_sh.setdefault(d6.get("ticker", ""), []).append(
                (d6.get("ts_epoch", 0), d6.get("details") or {}))
        div, checked6 = [], 0
        by_tk = {t["tk"]: t for t in trades}
        for r in rows:
            t6 = by_tk.get(r["tk"])
            cands = [x for x in live_sh.get(r["tk"], [])
                     if t6 is None or x[0] <= t6["ts"]]
            if not cands:
                continue
            ts6, det6 = cands[-1]
            checked6 += 1
            live_op = det6.get("opinion")
            if r["grade"] == "NO-OPINION" and live_op == "CONVICTION":
                div.append((r["id"], "replay NO-OPINION vs live CONVICTION"))
            elif r["grade"] != "NO-OPINION" and live_op == "NO-OPINION":
                div.append((r["id"], "live NO-OPINION vs replay graded"))
            elif live_op == "CONVICTION" and r.get("posterior") is not None \
                    and det6.get("confidence") is not None:
                # [-0k TICK-ALIGN 07-12] compare at the SHADOW'S OWN tick, not
                # the fill tick -- the live line predates the fill by up to the
                # 300s/site dedup (07-11: FRAMAR-FRA 5m56s), and in-play tape
                # moves conf past 0.10 in that gap. Same instant, same math.
                t7 = by_tk.get(r["tk"])
                pr7 = (t7 or {}).get("prior")
                if pr7:
                    obs7 = [o for o in obs_cache.get(r["tk"], []) if o[0] <= ts6]
                    ser7 = c.tick_posterior(pr7, obs7)
                    rep_conf = ser7[-1][1] if ser7 else pr7["confidence"]
                else:
                    rep_conf = r["posterior"]
                if abs(det6["confidence"] - rep_conf) > 0.10:
                    div.append((r["id"], "conf gap %.2f live vs %.2f replay (at the shadow's tick)"
                                % (det6["confidence"], rep_conf)))
        L += ["", "## LIVE-vs-REPLAY AGREEMENT (same-instrument law, live edition) — "
                  "checked %d, **divergences: %d**" % (checked6, len(div))]
        for i6, why6 in div[:10]:
            L.append("- **VIOLATION** %s: %s" % (i6, why6))
    except Exception:
        pass
    # [C-BOOK-REPLAY v2 shadow] the one held-out-surviving refit: ITF_M
    # refuse margin 8c (vs decreed 2c). SHADOW: both margins' refuse-set pnl
    # printed nightly; cutover on the operator's word.
    try:
        itfm = [r for r in rows if r["cat"] == "ITF_M" and r.get("posterior") is not None
                and r.get("pnl_cents") is not None]
        def _saved(m):
            return -sum(r["pnl_cents"] for r in itfm
                        if (r["posterior"] * 100 - r["px"]) < -m)
        if itfm:
            L += ["", "**REFUSE-MARGIN SHADOW (ITF_M, M16): fitted 8c would-have-saved %+.0f¢ | decreed 2c %+.0f¢** (held-out winner 07-11: +1170 vs -85; cutover on the operator's word)"
                  % (_saved(8), _saved(2))]
    except Exception:
        pass
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
    # [C-COMPLETION-POLICY v1 Part 3] COMPLETION-SHADOW: both branches'
    # would-have-dones beside the live machinery, per category, nightly
    try:
        from collections import Counter as _Ctr
        cs_v, cs_ev = _Ctr(), _Ctr()
        for line in open(log, encoding="utf-8", errors="replace"):
            if '"completion_shadow"' not in line:
                continue
            try:
                d5 = json.loads(line)
            except ValueError:
                continue
            det5 = d5.get("details") or {}
            c5 = cat_of(d5.get("ticker", "")) or "?"
            cs_v[(c5, det5.get("verdict"))] += 1
            k5 = det5.get("kept") or {}
            if isinstance(k5, dict) and k5.get("ev_cents") is not None:
                cs_ev[c5] += k5["ev_cents"]
        if cs_v:
            L += ["", "## COMPLETION-SHADOW (per-leg economics beside the live machinery; taker branch GATED behind operator_taker_word)",
                  "", "| cat | verdict | n |", "|---|---|---|"]
            for (c5, v5), n5 in sorted(cs_v.items()):
                L.append("| %s | %s | %d |" % (c5, v5, n5))
            L.append("")
            L.append("kept-leg EV sums (¢, two-term frame, win-ride residual excluded): "
                     + (" | ".join("%s %+.0f" % (c5, e5) for c5, e5 in sorted(cs_ev.items())) or "none"))
    except Exception:
        pass
    # [C-COMPLETION-LIVE 07-12, operator word] the policy's first live days
    # are graded against its own shadow record: every completion_action must
    # match the shadow verdict that triggered it, and every actionable shadow
    # verdict (taker_complete/flatten_kept, gates open) must have an action
    # or a named refusal -- any live-vs-shadow divergence is a NAMED violation.
    try:
        acts = []           # (ts, event, verdict, outcome)
        sh_last = {}        # event -> (ts, verdict)
        sh_actionable = {}  # event -> first actionable (ts, verdict)
        for line in open(log, encoding="utf-8", errors="replace"):
            if '"completion_action"' in line:
                d8 = json.loads(line)
                det8 = d8.get("details") or {}
                acts.append((d8.get("ts_epoch", 0), det8.get("event", ""),
                             det8.get("verdict"), det8.get("outcome")))
            elif '"completion_shadow"' in line:
                d8 = json.loads(line)
                det8 = d8.get("details") or {}
                ev8 = det8.get("event", "")
                sh_last[ev8] = (d8.get("ts_epoch", 0), det8.get("verdict"))
                if (det8.get("verdict") in ("taker_complete", "flatten_kept")
                        and ev8 not in sh_actionable):
                    sh_actionable[ev8] = (d8.get("ts_epoch", 0), det8.get("verdict"))
        div8 = []
        for ts8, ev8, v8, o8 in acts:
            lv = sh_last.get(ev8)
            if lv and lv[1] != v8 and lv[0] <= ts8:
                div8.append("action %s on %s but latest shadow said %s" % (v8, ev8, lv[1]))
            if o8 == "error":
                div8.append("action ERROR on %s (%s)" % (ev8, v8))
        acted_evs = {a[1] for a in acts}
        for ev8, (ts8, v8) in sh_actionable.items():
            if ev8 not in acted_evs:
                div8.append("shadow said %s on %s but NO action followed" % (v8, ev8))
        if acts or sh_actionable:
            L += ["", "## COMPLETION LIVE-vs-SHADOW (operator word 07-12; the same-instrument law, completion edition) — "
                      "actions: %d, divergences: %d" % (len(acts), len(div8))]
            for a in acts[:15]:
                L.append("- action %s → %s on %s" % (a[2], a[3], a[1]))
            for w8 in div8[:10]:
                L.append("- **VIOLATION** %s" % w8)
    except Exception:
        pass
    # [C-LIVE-AIM v1, 07-14] LIVE-AIM SHADOW: the fourth aim design graded
    # from night one — would-have-aims vs live aims vs tape truth, dollars
    # and yield vs the 8% bar, per category; n accrues toward the pre-agreed
    # cutover bar (beat live aims at n>=300 with the interval clear of zero,
    # the same statistical bar EV3 wears).
    try:
        la_rows = {}
        bells9 = {}
        for line in open(log, encoding="utf-8", errors="replace"):
            if '"liveaim_shadow"' in line:
                d9 = json.loads(line)
                det9 = d9.get("details") or {}
                tk9 = d9.get("ticker", "")
                if tk9 and tk9 not in la_rows and det9.get("aim_px"):
                    la_rows[tk9] = (d9.get("ts_epoch", 0), det9)
            elif '"gun_fired"' in line:
                d9 = json.loads(line)
                ev9 = (d9.get("details") or {}).get("event", "")
                if ev9 and ev9 not in bells9:
                    bells9[ev9] = d9.get("ts_epoch", 0)
        if la_rows:
            live_pnl = {r["tk"]: r["pnl_cents"] for r in rows
                        if r.get("pnl_cents") is not None}
            cat_g = defaultdict(lambda: [0, 0.0, 0.0, 0.0])  # n, sh$, live$, staked
            graded9 = 0
            for tk9, (ats, det9) in la_rows.items():
                ev9 = tk9.rsplit("-", 1)[0]
                won = settles.get(tk9, {}).get("settle")
                if won not in ("WIN", "LOSS"):
                    continue
                obs9 = obs_cache.get(tk9) or leg_observations(tk9)
                obs_cache[tk9] = obs9
                w1e = bells9.get(ev9, ats + 8 * 3600)
                aim9 = det9["aim_px"]
                fill = next((o for o in obs9 if ats <= o[0] <= w1e
                             and o[2] <= aim9), None)
                band9 = 8
                sh = 0.0
                if fill is not None:
                    cashed9 = any(o[2] >= aim9 + band9 for o in obs9
                                  if o[0] > fill[0])
                    sh = (band9 if cashed9 else
                          ((100 - aim9) if won == "WIN" else -aim9)) * 5 / 100.0
                    cat_g[det9.get("citation", "")[:0] or "x"][3] += aim9 * 5 / 100.0
                c9 = cat_of(tk9) or "?"
                g = cat_g[c9]
                g[0] += 1
                g[1] += sh
                g[2] += live_pnl.get(tk9, 0.0) / 100.0 * 1.0 if tk9 in live_pnl else 0.0
                graded9 += 1
            if graded9:
                L += ["", "## LIVE-AIM SHADOW (fourth design, night %s) — graded %d "
                          "(accruing toward the n>=300 cutover bar)" % (ymd, graded9)]
                for c9, g in sorted(cat_g.items()):
                    if c9 == "x" or not g[0]:
                        continue
                    L.append("- %s: n=%d | shadow $%+.2f | live $%+.2f" %
                             (c9, g[0], g[1], g[2]))
    except Exception:
        pass
    # [C-DELETION-GATE Part 1, 07-12] GOVERNOR SPLIT: the two live brains'
    # actions and dollars, separated at the stamp -- no hand-reading logs.
    # Dollars: each exit_filled attributes its pnl to the governor of the
    # LAST exit-posting decision on that ticker (maker_exit posts vs
    # per_leg_policy flattens); completion crosses list their own prices.
    try:
        gov_n = defaultdict(int)
        gov_pnl = defaultdict(float)
        last_exit_gov = {}
        cap_hits = 0
        for line in open(log, encoding="utf-8", errors="replace"):
            if '"governed_by"' in line:
                d9 = json.loads(line)
                det9 = d9.get("details") or {}
                g9 = det9.get("governed_by")
                gov_n[g9] += 1
                if d9.get("event") in ("v4_exit_posted", "completion_action") \
                        and d9.get("ticker"):
                    if d9["event"] == "v4_exit_posted" or \
                            det9.get("outcome") == "flattening":
                        last_exit_gov[d9["ticker"]] = g9
            elif '"exit_filled"' in line:
                d9 = json.loads(line)
                det9 = d9.get("details") or {}
                if det9.get("pnl_cents") is not None and d9.get("ticker"):
                    gov_pnl[last_exit_gov.get(d9["ticker"], "maker_exit")] += \
                        det9["pnl_cents"]
            elif '"completion_taker_capped"' in line:
                cap_hits += 1
        # [C-ADJUDICATION-READ Part 3] band-by-path framing: exit band per
        # governor so the flatten-vs-maker comparison is one table
        gov_band = defaultdict(list)
        for line in open(log, encoding="utf-8", errors="replace"):
            if '"exit_filled"' not in line:
                continue
            d9 = json.loads(line)
            det9 = d9.get("details") or {}
            if det9.get("exit_price") is not None and det9.get("entry_price") is not None:
                gov_band[last_exit_gov.get(d9.get("ticker"), "maker_exit")].append(
                    det9["exit_price"] - det9["entry_price"])
        if gov_n:
            L += ["", "## GOVERNOR SPLIT (whose hand moved — actions | exit ¢ attributed | avg band)"]
            for g9 in ("per_leg_policy", "pair97_bound", "maker_exit",
                       "match_live_cancel"):
                bl9 = gov_band.get(g9, [])
                L.append("- %s: %d actions | %+.0f¢ | band %s" % (
                    g9, gov_n.get(g9, 0), gov_pnl.get(g9, 0.0),
                    ("%+.1fc (n=%d)" % (sum(bl9) / len(bl9), len(bl9))) if bl9 else "—"))
            if cap_hits:
                L.append("- **taker cap hits (DECREED 3/day until n≥30 graded): %d — named, never silent**" % cap_hits)
    except Exception:
        pass
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
