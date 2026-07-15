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
    # [C-CONTENTION-LAW v1, 07-15] SELECTOR: the operator's understanding
    # as selection law, priced nightly BEFORE it ever touches a live gate.
    # The would-have slate (TRADE-AT-PATH legs at their contention aims,
    # tape-touch fills -- the LIVE-AIM grading convention) vs the actual
    # slate, dollars and yield-on-wagered vs the 8% bar, per category; the
    # DROP list named with what those legs actually did.
    try:
        sel_rows, bells10 = {}, {}
        for line in open(log, encoding="utf-8", errors="replace"):
            if '"trendpath_shadow"' in line:
                d9 = json.loads(line)
                det9 = d9.get("details") or {}
                tk9 = d9.get("ticker", "")
                if tk9 and tk9 not in sel_rows and det9.get("selector"):
                    sel_rows[tk9] = (d9.get("ts_epoch", 0), det9)
            elif '"gun_fired"' in line:
                d9 = json.loads(line)
                ev9 = (d9.get("details") or {}).get("event", "")
                if ev9 and ev9 not in bells10:
                    bells10[ev9] = d9.get("ts_epoch", 0)
        if sel_rows:
            live_pnl10 = {r["tk"]: r["pnl_cents"] for r in rows
                          if r.get("pnl_cents") is not None}
            live_stk10 = defaultdict(float)
            live_act10 = defaultdict(float)
            for t9 in trades:
                live_stk10[cat_of(t9["tk"]) or "?"] += \
                    (t9.get("px") or 0) * (t9.get("qty") or 0) / 100.0
            for tk9, p9 in live_pnl10.items():
                live_act10[cat_of(tk9) or "?"] += p9 / 100.0
            SC = defaultdict(lambda: defaultdict(float))
            drops10 = []
            for tk9, (ats, det9) in sorted(sel_rows.items()):
                c9 = cat_of(tk9) or "?"
                v9 = det9["selector"]
                SC[c9][v9] += 1
                if v9 == "DROP":
                    drops10.append((tk9, det9.get("contention_best_pct"),
                                    live_pnl10.get(tk9)))
                    continue
                if v9 != "TRADE-AT-PATH":
                    continue
                aim9 = det9.get("contention_aim") or det9.get("path_aim")
                won = settles.get(tk9, {}).get("settle")
                if not aim9 or won not in ("WIN", "LOSS"):
                    continue
                obs9 = obs_cache.get(tk9) or leg_observations(tk9)
                obs_cache[tk9] = obs9
                w1e = bells10.get(tk9.rsplit("-", 1)[0], ats + 8 * 3600)
                fill = next((o for o in obs9 if ats <= o[0] <= w1e
                             and o[2] <= aim9), None)
                if fill is None:
                    continue
                cashed = any(o[2] >= aim9 + 8 for o in obs9
                             if o[0] > fill[0])
                SC[c9]["e"] += (8 if cashed else
                                ((100 - aim9) if won == "WIN"
                                 else -aim9)) * 5 / 100.0
                SC[c9]["stk"] += aim9 * 5 / 100.0
                SC[c9]["graded"] += 1
            L += ["", "## SELECTOR (C-CONTENTION-LAW: the path decides WHAT "
                      "we trade) — would-have slate vs actual, vs the 8% bar"]
            for c9, S9 in sorted(SC.items()):
                L.append("- %s: TRADE %d / DROP %d / NO-OPINION %d | "
                         "would-have $%+.2f on $%.0f staked (%s, %d graded) "
                         "| actual slate $%+.2f on $%.0f (%s)"
                         % (c9, S9["TRADE-AT-PATH"], S9["DROP"],
                            S9["NO-OPINION"], S9["e"], S9["stk"],
                            ("%+.1f%%" % (100 * S9["e"] / S9["stk"]))
                            if S9["stk"] else "—", S9["graded"],
                            live_act10.get(c9, 0.0), live_stk10.get(c9, 0.0),
                            ("%+.1f%%" % (100 * live_act10.get(c9, 0.0)
                                          / live_stk10[c9]))
                            if live_stk10.get(c9) else "—"))
            if drops10:
                dropped_pnl = sum(a9 for _, _, a9 in drops10
                                  if a9 is not None) / 100.0
                L.append("- **DROP list** (leg | contention %% | actual): " +
                         "; ".join("%s %s%% %s"
                                   % ("-".join(t9.split("-")[-2:]), b9,
                                      ("%+d¢" % a9) if a9 is not None
                                      else "untraded")
                                   for t9, b9, a9 in drops10[:12]) +
                         (" | dropped legs the bot DID trade: $%+.2f"
                          % dropped_pnl))
    except Exception:
        pass
    # [C-VAULT-WIRED-ENTRY v1 Part 2, 07-14] THE CONSULTATION CENSUS:
    # every decision site x every registry surface — CONSULTED / SHADOW /
    # NOT-APPLICABLE (reason) / GAP. Any GAP is a board item automatically
    # (idempotent append under the AUTO-GAPS marker). This is how "the
    # entry ignores fitted work" becomes impossible to miss again.
    try:
        SURFACES = ["atlas_page", "contention_selector", "pair_state",
                    "reach_law", "range_cell_m15", "dip_timing",
                    "flow_state", "refuse_margins",
                    "operator_adjudications", "fill_regime",
                    "honest_clock", "shadow_range_shape", "w1_cohort",
                    "window_phase"]
        # [C-W1-LIBRARY Part 2] cohort calibration: predicted dip_freq vs
        # realized dips on today's dossier'd legs (shadow grading before
        # anything acts)
        _coh_pred, _coh_real, _coh_n = 0.0, 0, 0
        cen = defaultdict(lambda: defaultdict(int))
        sites = defaultdict(int)
        gaps = defaultdict(set)
        n_dos = 0
        for line in open(log, encoding="utf-8", errors="replace"):
            if '"entry_dossier"' not in line:
                continue
            d9 = json.loads(line)
            det9 = d9.get("details") or {}
            n_dos += 1
            site9 = (det9.get("decision") or "?").split(":")[0]
            sites[site9] += 1
            for s9, v9 in (det9.get("surfaces") or {}).items():
                st9 = (v9 or {}).get("status", "GAP")
                cen[s9][st9] += 1
                if st9 == "GAP":
                    gaps[s9].add((v9 or {}).get("why", ""))
            _c14 = (det9.get("surfaces") or {}).get("w1_cohort") or {}
            if _c14.get("dip_freq") is not None and d9.get("ticker"):
                tk14 = d9["ticker"]
                obs14 = obs_cache.get(tk14) or leg_observations(tk14)
                obs_cache[tk14] = obs14
                disc14 = det9.get("discovery")
                if obs14 and disc14:
                    dipped = any(o[2] <= disc14 - 3 for o in obs14
                                 if o[0] >= d9["ts_epoch"])
                    _coh_pred += _c14["dip_freq"]
                    _coh_real += 1 if dipped else 0
                    _coh_n += 1
        if n_dos:
            L += ["", "## CONSULTATION CENSUS (C-VAULT-WIRED-ENTRY: %d "
                      "dossiers across sites %s)"
                      % (n_dos, dict(sites))]
            for s9 in SURFACES:
                c9 = cen.get(s9, {})
                if not c9:
                    gaps[s9].add("surface absent from every dossier")
                L.append("- %-20s %s" % (s9, dict(c9) if c9
                                         else "**GAP (never consulted)**"))
            if _coh_n:
                L.append("- W1-COHORT CALIBRATION (shadow): predicted "
                         "dip_freq mean %.2f vs realized %.2f across %d "
                         "graded legs"
                         % (_coh_pred / _coh_n, _coh_real / _coh_n,
                            _coh_n))
            if gaps:
                L.append("- **GAPS -> board items (the intake list): %s**"
                         % "; ".join("%s (%s)" % (k, "; ".join(w for w in v
                                                               if w)[:90])
                                     for k, v in gaps.items()))
                try:
                    bp9 = ROOT.parent / ".claude/BOARD.md"
                    bs9 = bp9.read_text(encoding="utf-8")
                    add9 = []
                    for k, v in gaps.items():
                        line9 = ("- AUTO-GAP (consultation census %s): %s — %s"
                                 % (ymd, k, ("; ".join(w for w in v if w)
                                             or "unconsulted")[:140]))
                        if ("AUTO-GAP (consultation census" in bs9
                                and k in bs9):
                            continue
                        add9.append(line9)
                    if add9:
                        mk9 = "## AUTO-GAPS (consultation census intake)"
                        if mk9 not in bs9:
                            bs9 += "\n\n" + mk9 + "\n"
                        bs9 = bs9.replace(mk9, mk9 + "\n" + "\n".join(add9),
                                          1)
                        bp9.write_text(bs9, encoding="utf-8")
                except Exception:
                    pass
    except Exception:
        pass
    # [C-WINDOW-LAW v1 Part 4, 07-14 — the operator directive: no night
    # grades again without the window split] THE WINDOW LEDGER: entries,
    # refusals, tape touches, fills, cashes-via-exit, rode-to-settlement,
    # and cancels split W1 / CORRIDOR / W2 per cat — the WINDOW_MAP_3WAY
    # axes as a standing instrument. Phase from the emitter stamp;
    # pre-stamp lines and missing joins = UNKNOWN, named.
    try:
        WL = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
        scheds, guns9 = {}, {}
        aims9 = {}
        for line in open(log, encoding="utf-8", errors="replace"):
            if '"schedule_match"' in line:
                d9 = json.loads(line)
                det9 = d9.get("details") or {}
                ev9 = det9.get("event")
                st9 = det9.get("start_time")
                if ev9 and st9 and ev9 not in scheds:
                    try:
                        scheds[ev9] = datetime.fromisoformat(st9).timestamp()
                    except Exception:
                        pass
                continue
            if '"gun_fired"' in line:
                d9 = json.loads(line)
                ev9 = (d9.get("details") or {}).get("event")
                if ev9 and ev9 not in guns9:
                    guns9[ev9] = d9["ts_epoch"]
                continue
            hit9 = None
            for e9, k9 in (('"v4_place"', "entries"),
                           ('"below_leg_floor_refused"', "refusals"),
                           ('"no_path_page_refused"', "refusals"),
                           ('"selector_drop_refused"', "refusals"),
                           ('"pair_seesaw_refused"', "refusals"),
                           ('"entry_filled"', "fills"),
                           ('"exit_filled"', "cash_via_exit"),
                           ('"settled"', "rode_to_settle"),
                           ('"order_cancelled"', "cancels"),
                           ('"match_live_resting_cancel"', "cancels"),
                           ('"trendpath_live_aim"', "aims")):
                if e9 in line:
                    hit9 = k9
                    break
            if not hit9:
                continue
            d9 = json.loads(line)
            det9 = d9.get("details") or {}
            if hit9 == "aims":
                tk9 = d9.get("ticker")
                if tk9 and tk9 not in aims9:
                    aims9[tk9] = (d9["ts_epoch"], det9.get("path_aim"))
                continue
            if hit9 == "entries" and d9.get("event") != "v4_place":
                continue
            ph9 = ((det9.get("window") or {}).get("phase")
                   if isinstance(det9.get("window"), dict) else None)
            if ph9 is None:
                ev9 = det9.get("event") or (d9.get("ticker") or
                                            "").rsplit("-", 1)[0]
                ts9 = d9["ts_epoch"]
                sc9, gn9 = scheds.get(ev9), guns9.get(ev9)
                ph9 = ("W2" if gn9 and ts9 >= gn9 else
                       "CORRIDOR" if sc9 and ts9 >= sc9 else
                       "W1" if sc9 else "UNKNOWN")
            c9 = cat_of(d9.get("ticker") or "") or "?"
            WL[c9][hit9][ph9] += 1
        # tape touches for path-aimed legs, phase at touch
        for tk9, (ats, aim9) in aims9.items():
            if not aim9:
                continue
            obs9 = obs_cache.get(tk9) or leg_observations(tk9)
            obs_cache[tk9] = obs9
            t9 = next((o for o in obs9 if o[0] >= ats and o[2] <= aim9),
                      None)
            if t9 is None:
                continue
            ev9 = tk9.rsplit("-", 1)[0]
            sc9, gn9 = scheds.get(ev9), guns9.get(ev9)
            ph9 = ("W2" if gn9 and t9[0] >= gn9 else
                   "CORRIDOR" if sc9 and t9[0] >= sc9 else
                   "W1" if sc9 else "UNKNOWN")
            WL[cat_of(tk9) or "?"]["tape_touches"][ph9] += 1
        if WL:
            L += ["", "## WINDOW LEDGER (C-WINDOW-LAW: W1 / CORRIDOR / W2 "
                      "— no night grades without the split)"]
            for c9 in sorted(WL):
                row9 = WL[c9]
                def _w(k):
                    v9 = row9.get(k, {})
                    return "W1:%d C:%d W2:%d U:%d" % (
                        v9.get("W1", 0), v9.get("CORRIDOR", 0),
                        v9.get("W2", 0), v9.get("UNKNOWN", 0))
                L.append("- %s: entries[%s] refusals[%s] touches[%s] "
                         "fills[%s] cash[%s] rode[%s] cancels[%s]"
                         % (c9, _w("entries"), _w("refusals"),
                            _w("tape_touches"), _w("fills"),
                            _w("cash_via_exit"), _w("rode_to_settle"),
                            _w("cancels")))
        # [C-CONVICTED-INSTRUMENTS Part 1, 07-14 — the reach refit armed
        # where expectation is consumed] REACH EXPECTED-VS-ACTUAL, the
        # honest bound: per new-book leg, E integrates placement ->
        # min(evidence gun, fill, day end). The sanity line names what the
        # old unbounded integral would have added (the 26.55-class).
        try:
            import math as _m9
            _lawp9 = ROOT.parent / ".claude/takerreach/LAW.json"
            _law9 = (json.loads(_lawp9.read_text(encoding="utf-8"))
                     .get("law", {}) if _lawp9.exists() else {})
            _thr9 = {"ITF_M": 6, "ITF_W": 6, "ATP_CHALL": 16,
                     "WTA_CHALL": 16}
            _eL = _eU = 0.0
            _nA = _nG = 0
            _day_end9 = day0 + 24 * 3600
            for tk9, (ats9, aim9) in aims9.items():
                if not aim9:
                    continue
                c9 = cat_of(tk9) or "?"
                th9 = _thr9.get(c9)
                if not th9:
                    continue
                ev9 = tk9.rsplit("-", 1)[0]
                gun9 = bells10.get(ev9)
                fill9 = None
                for r9 in rows:
                    if r9["tk"] == tk9:
                        fill9 = True
                        break
                obs9 = obs_cache.get(tk9) or leg_observations(tk9)
                obs_cache[tk9] = obs9
                oT = [o[0] for o in obs9]
                oP = [o[2] for o in obs9]
                import bisect as _b9
                surv9 = 1.0
                t9 = ats9
                end_l = min(gun9 or _day_end9, _day_end9)
                while t9 < _day_end9:
                    lo9 = _b9.bisect_left(oT, t9 - 900)
                    hi9 = _b9.bisect_right(oT, t9)
                    pxs9 = oP[lo9:hi9]
                    if pxs9:
                        med9 = sorted(pxs9)[len(pxs9) // 2]
                        p309 = hi9 - _b9.bisect_left(oT, t9 - 1800)
                        r9x = p309 / float(th9)
                        fb9 = ("quiet" if r9x < 0.25 else
                               "warm" if r9x < 1.0 else "open")
                        Lw9 = _law9.get("%s|%s" % (c9, fb9)) or {}
                        X9 = min(max(int(round(med9 - aim9)), 1), 20)
                        rt9 = Lw9.get("rate_per_hr", {}).get(str(X9), 0.0)
                        p9x = 1 - _m9.exp(-rt9 * (120.0 / 3600.0))
                        if t9 < end_l:
                            _eL += surv9 * p9x
                        else:
                            _eU += surv9 * p9x
                        surv9 *= (1 - p9x)
                    t9 += 120.0
                _nG += 1
                if fill9:
                    _nA += 1
            if _nG:
                L.append("- REACH E-vs-A (refit: integration to the "
                         "evidence gun): lawful E[fills] %.2f vs actual %d "
                         "across %d legs | old-class unbounded would have "
                         "added %.2f (excluded)"
                         % (_eL, _nA, _nG, _eU))
        except Exception:
            pass
        # [Part 5 tripwire] gun-feed staleness (min since last NEW in-play
        # sighting — arrival-gap honest label)
        try:
            import sqlite3 as _sq9
            _osdb = ROOT / "state/observed_starts.db"
            _src9 = str(_osdb) if _osdb.exists() else str(ROOT / "tennis.db")
            _con9 = _sq9.connect("file:%s?mode=ro" % _src9, uri=True,
                                 timeout=2)
            _mx9 = _con9.execute(
                "SELECT MAX(inserted_at) FROM observed_starts").fetchone()[0]
            _con9.close()
            if _mx9:
                _age9 = (datetime.now() -
                         datetime.strptime(_mx9, "%Y-%m-%d %H:%M:%S")
                         ).total_seconds() / 60.0
                L.append("- GUN-FEED: last new in-play sighting %.0f min "
                         "ago (%s)%s" % (_age9, Path(_src9).name,
                                         " **> 30 min — TRIPWIRE**"
                                         if _age9 > 30 else ""))
        except Exception:
            pass
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
    # [C-TAKER-REACH rider, 07-14] the operator's metric as the nightly
    # headline: yield on capital wagered vs the 8% bar. Backfill on record
    # (C-PNL-TRUTH staked joins): 07-10 +1.6% ($341) · 07-11 +0.8% ($279) ·
    # 07-12 +0.1% ($279) · 07-13 −3.8% ($221).
    try:
        _stk = sum((t.get("px") or 0) * (t.get("qty") or 0) for t in trades) / 100.0
        _net = sum(r.get("pnl_cents") or 0 for r in rows) / 100.0
        L.insert(2, "")
        # [CUTOVER 07-14, STANDING LAW (operator, verbatim in the vault):
        # "the goal is solid yield on solid capital wagered — the nightly's
        # first line is forever YIELD-ON-WAGERED versus the 8% bar;
        # below-bar nights print their named reasons, diagnosed, never
        # explained away."]
        _y9 = 100.0 * _net / _stk if _stk else 0.0
        L.insert(3, "**YIELD-ON-WAGERED: %+.1f%% (net $%+.2f on $%.0f staked) vs the 8%% bar** "
                    "(backfill: 07-10 +1.6%% · 07-11 +0.8%% · 07-12 +0.1%% · 07-13 −3.8%%)"
                    % (_y9, _net, _stk))
        if _stk and _y9 < 8.0:
            _catp = defaultdict(float)
            _setl = _exl = 0.0
            for r9 in rows:
                p9 = r9.get("pnl_cents")
                if p9 is None:
                    continue
                _catp[r9.get("cat", "?")] += p9
                if r9["tk"] in settles:
                    _setl += p9
                else:
                    _exl += p9
            _worst = sorted(_catp.items(), key=lambda x: x[1])[:2]
            L.insert(4, "**BELOW-BAR NIGHT — named: settled legs $%+.2f vs "
                        "exited legs $%+.2f; worst categories %s; "
                        "diagnosis, not explanation: %s**"
                        % (_setl / 100.0, _exl / 100.0,
                           ", ".join("%s $%+.2f" % (c9, v9 / 100.0)
                                     for c9, v9 in _worst),
                           ("ride-to-zero settlements dominate — the "
                            "payoff-asymmetry class" if _setl < _exl
                            else "exit-side bleed — band/flatten review")))
    except Exception:
        pass
    # [C-GOLD-NOW Part 4, 07-15] THE REALIZATION LEDGER: returns from
    # subtraction, printed nightly while the addition arms -- the legs the
    # DROP decree refused, graded at what they actually did (tape-touch
    # fill at the would-have bid, band-exit-else-settle, the LIVE-AIM
    # convention), plus the consolidated-packet countdown.
    try:
        _ref9 = []
        _sees9 = _lift9 = _viol9 = 0
        for line in open(log, encoding="utf-8", errors="replace"):
            if '"pair_seesaw_refused"' in line:
                _sees9 += 1
                continue
            if '"pair_seesaw_lifted"' in line:
                _lift9 += 1
                continue
            if '"pair_law_violation"' in line and '"entry_filled"' in line:
                _viol9 += 1
            if '"selector_drop_refused"' not in line:
                continue
            d9 = json.loads(line)
            det9 = d9.get("details") or {}
            tk9 = d9.get("ticker", "")
            if tk9 and det9.get("would_target_bid"):
                _ref9.append((tk9, d9.get("ts_epoch", 0),
                              det9["would_target_bid"]))
        _saved = 0.0
        _graded9 = 0
        for tk9, ats, bid9 in _ref9:
            won = settles.get(tk9, {}).get("settle")
            if won not in ("WIN", "LOSS"):
                continue
            obs9 = obs_cache.get(tk9) or leg_observations(tk9)
            obs_cache[tk9] = obs9
            fill = next((o for o in obs9 if o[0] >= ats and o[2] <= bid9),
                        None)
            if fill is None:
                continue
            cashed = any(o[2] >= bid9 + 8 for o in obs9 if o[0] > fill[0])
            _saved -= (8 if cashed else
                       ((100 - bid9) if won == "WIN" else -bid9)) * 5 / 100.0
            _graded9 += 1
        _pk9 = ROOT.parent / ".claude/trendpath/PACKET_STATUS.json"
        _pks = (json.loads(_pk9.read_text(encoding="utf-8"))
                if _pk9.exists() else {})
        # [C-RESUME-CHECK Part 4, DECREED] the ntfy topic is unsubscribed —
        # the nightly header is the operator's fallback phone: packet
        # numbers + deadline + the STOP procedure verbatim, at the top.
        if _pks.get("fired") and not (_pks.get("cutover_done")
                                      or {}).get("verified"):
            _dl9 = _pks.get("go_deadline_epoch")
            _dls9 = (datetime.fromtimestamp(_dl9, ET).strftime(
                "%m-%d %I:%M %p ET") if _dl9 else "?")
            _sm9 = _pks.get("summary", {})
            L.insert(2, "**⚠ PACKET FIRED — DEFAULT-GO DEADLINE %s ⚠ "
                        "path %+.1f%%/reach %+.1f%%/selector %+.1f%% "
                        "(all doors: %s). STOP PROCEDURE: say STOP to the "
                        "relay; CC creates .claude/trendpath/OPERATOR_STOP; "
                        "silence past the deadline = trendpath_live flips "
                        "on the next boot with full audit.**"
                        % (_dls9,
                           _sm9.get("path", {}).get("yield_pct", 0),
                           _sm9.get("reach", {}).get("yield_pct", 0),
                           _sm9.get("selector", {}).get("yield_pct", 0),
                           " / ".join(_sm9.get(k, {}).get("door", "?")
                                      for k in ("path", "reach",
                                                "selector"))))
        L.insert(4, "**REALIZED-BY-SUBTRACTION: %d DROP-AS-PAIR refusals "
                    "(%d graded, dollars-not-lost $%+.2f) | seesaw: %d "
                    "refused / %d lifted | one-sided VIOLATIONS: %d | "
                    "PACKET COUNTDOWN: n=%s/300 (auto re-run %s%s)**"
                    % (len(_ref9), _graded9, _saved, _sees9, _lift9, _viol9,
                       _pks.get("n_min", "?"),
                       _pks.get("last_run_et", "never"),
                       "; PACKET FIRED" if _pks.get("fired") else ""))
    except Exception:
        pass
    # [C-INCUMBENT-SUNSET, 07-15] Part 1: INCUMBENT-COST — every dollar the
    # CONVICTED INCUMBENT (static aims / join-the-market / 97-remainder
    # completion pricing) loses from tonight is attributed to it; legs the
    # path-mode re-aimed (trendpath_live_aim stamp) are the replacement's.
    # Part 4: THE SUNSET LEDGER — each incumbent organ with its
    # replacement's status and distance-to-activation, so "why is this
    # still hardcoded" is always a printed answer with a date.
    try:
        _tp_legs = set()
        for line in open(log, encoding="utf-8", errors="replace"):
            if '"trendpath_live_aim"' in line:
                d9 = json.loads(line)
                if d9.get("ticker"):
                    _tp_legs.add(d9["ticker"])
        _inc_n = _inc_c = _rep_n = _rep_c = 0
        for r in rows:
            if r.get("pnl_cents") is None:
                continue
            if r["tk"] in _tp_legs:
                _rep_n += 1
                _rep_c += r["pnl_cents"]
            else:
                _inc_n += 1
                _inc_c += r["pnl_cents"]
        _cfp = ROOT / "config/deploy_v5_live.json"
        _cf9 = json.loads(_cfp.read_text(encoding="utf-8")) \
            if _cfp.exists() else {}
        _pk8 = ROOT.parent / ".claude/trendpath/PACKET_STATUS.json"
        _pks8 = (json.loads(_pk8.read_text(encoding="utf-8"))
                 if _pk8.exists() else {})
        L.insert(5, "**INCUMBENT-COST: $%+.2f across %d incumbent-entered "
                    "legs%s (attribution: trendpath_live_aim stamp)**"
                    % (_inc_c / 100.0, _inc_n,
                       (" | replacement legs $%+.2f across %d"
                        % (_rep_c / 100.0, _rep_n)) if _rep_n else ""))
        L += ["", "## SUNSET LEDGER (post-cutover 07-14, operator word: "
                  "the incumbent's organs and what replaced them)"]
        L.append("- static aim tables -> DELETED from the entry path "
                 "(cutover 07-14): path aims are THE law; no fitted page "
                 "= no entry (no_path_page_refused, named)")
        L.append("- join-the-market walking -> DELETED (path_mode_hold): "
                 "the bid rests at its fitted aim — get paid, not filled")
        L.append("- 97-remainder completion pricing -> remainder-as-TARGET "
                 "DELETED; the sibling's path aim prices the bid; the "
                 "C-BOUND remainder CEILING retained (operator "
                 "adjudication 07-05)")
        L.append("- leg-level entry permission -> PAIR-LAW "
                 "(orientation-composition + seesaw lift): LIVE 07-15")
        L.append("- static 5-lot sizing -> sizing engine v0 (sizing_live): "
                 "%s | awaiting the operator's SEPARATE sizing word "
                 "(drawdown floor still a named placeholder)"
                 % ("LIVE" if _cf9.get("sizing_live") else "DARK"))
        L.append("- undirected placement -> orientation layer "
                 "(orientation_live): %s | tells' own clock (week: 8%% "
                 "coverage, n=8/300) — layers in when its bar clears"
                 % ("LIVE" if _cf9.get("orientation_live") else "DARK"))
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
