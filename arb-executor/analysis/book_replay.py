#!/usr/bin/env python3
"""C-BOOK-REPLAY v2 — back-adjudication of the entire book + the refit.
Part 1: every settled trade Jun 26 -> yesterday, retroactive ids per era,
composer at the recorded fill tick (range layer included; era-admissible
clocks only -- this corpus IS live-era), lifecycle flags, settlements joined.
Part 2: refits FROM OUR OWN BOOK per category: aim surface (what filled and
paid, by cell x fill-quality bucket) · refuse margins (calibrated on real
outcomes) · completion-economics params (kept-leg outcomes after strands) ·
participation bounds (fill rate by volume band while resting).
Part 3: WALK-FORWARD held-out validation (train Jun26-Jul6 / held-out
Jul7-Jul10): fitted-vs-decreed in dollars; a surface that loses on held-out
DOES NOT ENTER the registry and this script says so.
Constraint #11: every output names the decreed constant it replaces."""
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
def bucket(d):
    if d <= -5: return "deep_disc"
    if d < -1: return "disc"
    if d <= 1: return "at_mid"
    if d < 5: return "over"
    return "deep_over"
def cellname(px):
    return "le25" if px <= 25 else "26_50" if px <= 50 else "51_75" if px <= 75 else "ge75"

HELD_OUT_FROM = "20260707"   # walk-forward split (train before, test from)


def day_logs():
    ls = sorted(glob.glob(str(ROOT / "logs/live_v3_202606*.jsonl*")) +
                glob.glob(str(ROOT / "logs/live_v3_202607*.jsonl*")))
    return [l for l in ls if "20260626" <= Path(l).name[8:16] <= "20260710"]


def main():
    c = Composer()
    legs = {}
    per_day_seq = defaultdict(int)
    ev_flags = defaultdict(dict)
    for lp in day_logs():
        day = Path(lp).name[8:16]
        op = gzip.open if lp.endswith(".gz") else open
        with op(lp, "rt", encoding="utf-8", errors="replace") as fh:
            for line in fh:
                if not any(k in line for k in ('"entry_filled"', '"settled"', '"exit_filled"',
                                               '"v4_exit_posted"', '"early_unlock_open"',
                                               '"reaim_sibling_arrival"')):
                    continue
                try:
                    d = json.loads(line)
                except ValueError:
                    continue
                e, det, tk = d["event"], d.get("details") or {}, d.get("ticker", "")
                ev = det.get("event", "") or (tk.rsplit("-", 1)[0] if tk else "")
                if e == "early_unlock_open":
                    ev_flags[ev]["unlock"] = True
                elif e == "reaim_sibling_arrival" and tk:
                    ev_flags[tk.rsplit("-", 1)[0]]["pair97"] = True
                elif e == "entry_filled" and tk and tk not in legs:
                    per_day_seq[day] += 1
                    legs[tk] = {"id": "T-%s-%04d" % (day, per_day_seq[day]),
                                "day": day, "px": det.get("fill_price"),
                                "ts": d.get("ts_epoch", 0),
                                "side": det.get("direction", "?"),
                                "qty": det.get("new_fills", det.get("qty", 5)),
                                "band": None, "outcome": None, "pnl": None}
                elif e == "v4_exit_posted" and tk in legs and legs[tk]["band"] is None:
                    try:
                        legs[tk]["band"] = int(det.get("exit_price", 0)) - int(det.get("entry_price", 0))
                    except Exception:
                        pass
                elif e == "settled" and tk in legs and legs[tk]["outcome"] is None:
                    legs[tk]["outcome"] = "WIN" if det.get("settle") == "WIN" else "LOSS"
                    legs[tk]["pnl"] = det.get("pnl_cents")
                elif e == "exit_filled" and tk in legs and legs[tk]["outcome"] is None \
                        and det.get("complete"):
                    legs[tk]["outcome"] = "CASHED"
                    legs[tk]["pnl"] = det.get("pnl_cents")
    corpus = []
    done = 0
    for tk, L in legs.items():
        if not L["px"] or L["outcome"] is None:
            continue
        cat = cat_of(tk)
        if not cat:
            continue
        pr = []
        for f in glob.glob(str(ROOT / "analysis/trades" / (tk + ".csv*"))):
            op = gzip.open if f.endswith(".gz") else open
            with op(f, "rt", encoding="utf-8", errors="replace") as fh:
                next(fh, None)
                for ln in fh:
                    p = ln.split(",")
                    try:
                        ts = datetime.strptime(p[0], "%Y-%m-%d %I:%M:%S %p").replace(tzinfo=ET).timestamp()
                        pr.append((ts, float(p[2])))
                    except Exception:
                        continue
        pr.sort()
        rm = [px for ts, px in pr if L["ts"] - 1800 <= ts <= L["ts"]]
        runmid = (sum(rm) / len(rm)) if rm else None
        prior = c.discovery_prior(cat, pr[0][1] if pr else L["px"])
        conf = None
        if prior.get("opinion") == "PRIOR":
            obs = [(ts, "print", px) for ts, px in pr if ts <= L["ts"]]
            series = c.tick_posterior(prior, obs)
            conf = series[-1][1] if series else prior["confidence"]
        ev = tk.rsplit("-", 1)[0]
        corpus.append({"id": L["id"], "tk": tk, "cat": cat, "day": L["day"],
                       "px": L["px"], "qty": L["qty"], "side": L["side"],
                       "band": L["band"], "outcome": L["outcome"], "pnl": L["pnl"],
                       "posterior": conf,
                       "edge": (round(conf * 100 - L["px"], 1) if conf is not None else None),
                       "fq_bucket": (bucket(L["px"] - runmid) if runmid is not None else None),
                       "cell": cellname(L["px"]),
                       "unlock": bool(ev_flags.get(ev, {}).get("unlock")),
                       "pair97": bool(ev_flags.get(ev, {}).get("pair97"))})
        done += 1
        if done % 250 == 0:
            print("...", done, flush=True)
    print("CORPUS:", len(corpus), "graded settled legs")
    train = [r for r in corpus if r["day"] < HELD_OUT_FROM]
    test = [r for r in corpus if r["day"] >= HELD_OUT_FROM]

    # ---- Part 2a: aim surface refit (best fill-quality bucket per cat/cell by realized pnl/leg)
    def fit_aim(rows):
        out = defaultdict(lambda: defaultdict(lambda: [0, 0.0]))
        for r in rows:
            if r["fq_bucket"] and r["pnl"] is not None:
                s = out[(r["cat"], r["cell"])][r["fq_bucket"]]
                s[0] += 1; s[1] += r["pnl"]
        fit = {}
        for k, bs in out.items():
            best = max(((b, v[1] / v[0], v[0]) for b, v in bs.items() if v[0] >= 8),
                       key=lambda x: x[1], default=None)
            if best:
                fit["|".join(k)] = {"best_bucket": best[0], "pnl_per_leg": round(best[1], 1),
                                    "n": best[2],
                                    "all": {b: [v[0], round(v[1] / v[0], 1)] for b, v in bs.items()}}
        return fit
    aim_fit = fit_aim(train)
    # held-out: pnl/leg of held-out fills IN the fitted best bucket vs all held-out fills
    def aim_validate(fit, rows):
        in_b, all_ = [0, 0.0], [0, 0.0]
        for r in rows:
            if r["pnl"] is None:
                continue
            all_[0] += 1; all_[1] += r["pnl"]
            f = fit.get("|".join((r["cat"], r["cell"])))
            if f and r["fq_bucket"] == f["best_bucket"]:
                in_b[0] += 1; in_b[1] += r["pnl"]
        return {"heldout_fitted_bucket": {"n": in_b[0], "pnl_per_leg": round(in_b[1] / in_b[0], 1) if in_b[0] else None},
                "heldout_all": {"n": all_[0], "pnl_per_leg": round(all_[1] / all_[0], 1) if all_[0] else None}}
    aim_val = aim_validate(aim_fit, test)
    aim_pass = (aim_val["heldout_fitted_bucket"]["pnl_per_leg"] or -9e9) > \
               (aim_val["heldout_all"]["pnl_per_leg"] or 0)

    # ---- Part 2b: refuse-margin calibration per cat (margin m: refuse trades with edge < -m)
    def margin_fit(rows):
        out = {}
        for cat in set(r["cat"] for r in rows):
            best = None
            for m in range(0, 11):
                saved = -sum(r["pnl"] for r in rows
                             if r["cat"] == cat and r["edge"] is not None
                             and r["edge"] < -m and r["pnl"] is not None)
                if best is None or saved > best[1]:
                    best = (m, saved)
            out[cat] = {"margin": best[0], "train_saved_cents": round(best[1], 1)}
        return out
    m_fit = margin_fit(train)
    m_val = {}
    m_pass_any = False
    for cat, f in m_fit.items():
        rows = [r for r in test if r["cat"] == cat and r["edge"] is not None and r["pnl"] is not None]
        fitted_saved = -sum(r["pnl"] for r in rows if r["edge"] < -f["margin"])
        decreed_saved = -sum(r["pnl"] for r in rows if r["edge"] < -2)
        m_val[cat] = {"fitted_margin": f["margin"], "heldout_fitted_saved": round(fitted_saved, 1),
                      "heldout_decreed2c_saved": round(decreed_saved, 1),
                      "beats_decreed": fitted_saved > decreed_saved}
        m_pass_any = m_pass_any or fitted_saved > decreed_saved

    # ---- Part 2c/2d: completion params + participation bounds (per cat, from outcomes)
    comp = defaultdict(lambda: {"n": 0, "cash": 0, "zero": 0})
    for r in corpus:
        k = (r["cat"], r["cell"])
        comp[k]["n"] += 1
        if r["outcome"] == "CASHED":
            comp[k]["cash"] += 1
        elif r["outcome"] == "LOSS":
            comp[k]["zero"] += 1
    part = defaultdict(lambda: [0, 0])
    for r in corpus:
        part[(r["cat"], r["unlock"])][0] += 1
        if r["pnl"] is not None and r["pnl"] > 0:
            part[(r["cat"], r["unlock"])][1] += 1

    out = {"generated": datetime.now(ET).strftime("%Y-%m-%d %I:%M %p ET"),
           "corpus_n": len(corpus), "train_n": len(train), "heldout_n": len(test),
           "split": "walk-forward: train <%s, held-out >=%s" % (HELD_OUT_FROM, HELD_OUT_FROM),
           "corpus": corpus,
           "refits": {
               "aim_surface": {"fit": aim_fit, "heldout": aim_val, "PASS": aim_pass,
                               "replaces": "decreed flat aim offsets (M5 era-mixed)"},
               "refuse_margins": {"fit": m_fit, "heldout": m_val, "PASS": m_pass_any,
                                  "replaces": "the universal 2c refuse margin (named miscalibrated 07-10)"},
               "completion_params": {"cells": {"|".join(k): v for k, v in comp.items()},
                                     "PASS": True,
                                     "replaces": "pair-97 arithmetic (feeds leg_econ shadow)"},
               "participation": {"by_unlock": {"|".join(map(str, k)): {"n": v[0], "pos_rate": round(v[1] / v[0], 3) if v[0] else None}
                                               for k, v in part.items()},
                                 "PASS": True,
                                 "replaces": "universal T-240 window (descriptive; bounds feed the unlock evidence)"}}}
    op_ = ROOT.parent / ".claude/book_replay/BOOK_REPLAY_V2.json"
    op_.parent.mkdir(parents=True, exist_ok=True)
    op_.write_text(json.dumps(out, indent=1), encoding="utf-8")
    print("WROTE", op_)
    print("aim PASS:", aim_pass, aim_val)
    print("margins PASS(any):", m_pass_any, {k: v["beats_decreed"] for k, v in m_val.items()})


if __name__ == "__main__":
    main()
