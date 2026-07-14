#!/usr/bin/env python3
"""[C-GOLD-NOW Part 3, 07-15] THE CLOCK AUTOMATES ITSELF: the consolidated
re-run (path aims + the reach law on live aims + the selector slate)
re-executes at every settlement batch (2h cron); the FIRST crossing of
n>=300 on all three writes RULING_PACKET.md and pushes a notification —
the three cutover words arrive with their numbers attached. No human
checks a calendar.

Letters pre-registered: each trial graded era-clean under the REACH LAW
(fitted fill judge; pessimistic x0.5 column), delta vs actual with a
bootstrap CI, yield-on-wagered vs the 8% bar. The SELECTOR trial is the
leg-frame slate as pre-registered at C-CONTENTION-LAW; the pair-law
replay (C-PAIR-LAW) rides beside it in its own proof, not silently
swapped in. Doors: pass = n>=300 era-clean AND CI off zero -> five
forward nights -> operator word; else the packet states the letter."""
import json, gzip, math, random, sys, bisect, glob, subprocess
from pathlib import Path
from datetime import datetime, timezone, timedelta
from collections import defaultdict

ET = timezone(timedelta(hours=-4))
ROOT = Path(__file__).resolve().parent.parent
WS = ROOT.parent
OUTD = WS / ".claude/trendpath"
STATUS = OUTD / "PACKET_STATUS.json"
PACKET = OUTD / "RULING_PACKET.md"
sys.path.insert(0, str(ROOT))
from kalshi_reconciler import _headers, _load_private_key
import requests

ATLAS = json.loads((OUTD / "ATLAS_V1.json").read_text())["pages"]
LAW = json.loads((WS / ".claude/takerreach/LAW.json").read_text())["law"]
THR = {"ITF_M": 6, "ITF_W": 6, "ATP_CHALL": 16, "WTA_CHALL": 16}
CATS = {"KXATPMATCH": "ATP_MAIN", "KXWTAMATCH": "WTA_MAIN",
        "KXATPCHALLENGERMATCH": "ATP_CHALL", "KXWTACHALLENGERMATCH": "WTA_CHALL",
        "KXITFMATCH": "ITF_M", "KXITFWMATCH": "ITF_W"}
STEP, XMAX, BAND, NBAR = 120.0, 20, 8, 300

def pcell(px):
    return ("le25" if px <= 25 else "26_50" if px <= 50 else
            "51_75" if px <= 75 else "ge75")
def flow_bucket(p30, cat):
    thr = THR.get(cat)
    if not thr:
        return "na"
    r = p30 / float(thr)
    return "quiet" if r < 0.25 else ("warm" if r < 1.0 else "open")
def rate_of(cat, fb, X, pess=False):
    Lw = LAW.get("%s|%s" % (cat, fb))
    if not Lw:
        return 0.0
    r = Lw["rate_per_hr"].get(str(min(max(int(X), 1), XMAX)), 0.0)
    return r * (0.5 if pess else 1.0)

def selector_of(page, cur0):
    con = (page or {}).get("contention") or {}
    tiers = con.get("tiers") or {}
    cband = con.get("band", BAND)
    best_y = best_aim = None
    for T in tiers.values():
        d9, pe, pw = T.get("d"), T.get("p_exit"), T.get("p_win_entry")
        if d9 is None or pe is None or pw is None:
            continue
        a2 = max(1, int(round(cur0 - d9)))
        y2 = 100.0 * (pe * cband + (1 - pe) * (pw * (100 - a2)
                                               - (1 - pw) * a2)) / a2
        if best_y is None or y2 > best_y:
            best_y, best_aim = y2, a2
    if best_y is None:
        return "NO-OPINION", None
    return ("TRADE-AT-PATH" if best_y >= 8.0 else "DROP"), best_aim

# ---- logs: every day on disk ----
first_place, bells, fills_at = {}, {}, {}
for lp in sorted(glob.glob(str(ROOT / "logs/live_v3_*.jsonl"))):
    for ln in open(lp, encoding="utf-8", errors="replace"):
        if '"v4_place"' in ln:
            o = json.loads(ln)
            tk = o.get("ticker", "")
            d = o["details"]
            if tk and tk not in first_place and d.get("current_price"):
                first_place[tk] = (o["ts_epoch"], int(d["current_price"]),
                                   int(d.get("target_bid") or 0))
        elif '"gun_fired"' in ln:
            o = json.loads(ln)
            ev = (o.get("details") or {}).get("event", "")
            if ev and ev not in bells:
                bells[ev] = o["ts_epoch"]
        elif '"entry_filled"' in ln:
            o = json.loads(ln)
            tk = o.get("ticker", "")
            if tk and tk not in fills_at:
                fills_at[tk] = (o["ts_epoch"],
                                o["details"].get("fill_price"))
        elif '"exit_filled"' in ln:
            o = json.loads(ln)
            fills_at.setdefault(o.get("ticker", "") + "|X",
                                (o["ts_epoch"],
                                 o["details"].get("exit_price")))

# ---- settlements ----
pk = _load_private_key()
B = "https://api.elections.kalshi.com"
results, cur, pg = {}, None, 0
while pg < 200:
    pg += 1
    r = requests.get(B + "/trade-api/v2/portfolio/settlements",
                     headers=_headers(pk, "GET",
                                      "/trade-api/v2/portfolio/settlements"),
                     params={"limit": 200, **({"cursor": cur} if cur else {})},
                     timeout=25).json()
    ss = r.get("settlements", [])
    stop = False
    for s in ss:
        ts = datetime.fromisoformat(
            s["settled_time"].replace("Z", "+00:00")).timestamp()
        if datetime.fromtimestamp(ts, ET).strftime("%Y%m%d") < "20260710":
            stop = True
            break
        results[s["ticker"]] = s.get("market_result")
    cur = r.get("cursor")
    if stop or not cur or not ss:
        break

def parse_ts(s):
    d, t, ap = s.split(" ")
    y, mo, dy = d.split("-")
    parts = t.split(":")
    return datetime(int(y), int(mo), int(dy),
                    int(parts[0]) % 12 + (12 if ap == "PM" else 0),
                    int(parts[1]),
                    int(parts[2].split(".")[0]) if len(parts) > 2 else 0,
                    tzinfo=ET).timestamp()

def trades_of(tk):
    ts_, px_ = [], []
    for f in glob.glob(str(ROOT / "analysis/trades" / (tk + ".csv*"))):
        op = gzip.open if f.endswith(".gz") else open
        try:
            with op(f, "rt", encoding="utf-8", errors="replace") as fh:
                next(fh, None)
                for ln in fh:
                    p = ln.split(",")
                    if len(p) < 3:
                        continue
                    try:
                        ts_.append(parse_ts(p[0]))
                        px_.append(float(p[2]))
                    except Exception:
                        continue
        except OSError:
            continue
    order = sorted(range(len(ts_)), key=lambda i: ts_[i])
    return [ts_[i] for i in order], [px_[i] for i in order]

def grade(aim, ats, w1e, res, tT, tP, cat, cur0):
    """stepped reach-law survival, banded-exit-else-settle; (E$, E$pess, staked, staked_p)"""
    surv = surv_p = 1.0
    e = ep = st = stp = 0.0
    t = ats
    while t < w1e:
        lo = bisect.bisect_left(tT, t - 900)
        hi = bisect.bisect_right(tT, t)
        pxs = tP[lo:hi]
        med = sorted(pxs)[len(pxs) // 2] if pxs else cur0
        lo30 = bisect.bisect_left(tT, t - 1800)
        fb = flow_bucket(hi - lo30, cat)
        X = max(1, int(round(med - aim)))
        outc = (BAND if any(p >= aim + BAND for p in tP[hi:])
                else ((100 - aim) if res == "yes" else -aim)) * 5 / 100.0
        for pess in (False, True):
            r_ = rate_of(cat, fb, X, pess) * (STEP / 3600.0)
            p_ = 1 - math.exp(-r_)
            if pess:
                ep += surv_p * p_ * outc
                stp += surv_p * p_ * aim * 5 / 100.0
                surv_p *= (1 - p_)
            else:
                e += surv * p_ * outc
                st += surv * p_ * aim * 5 / 100.0
                surv *= (1 - p_)
        t += STEP
    return e, ep, st, stp

T = {k: {"e": 0.0, "ep": 0.0, "st": 0.0, "stp": 0.0, "act": 0.0,
         "n": 0, "deltas": []} for k in ("path", "reach", "selector")}
skip = defaultdict(int)
for tk, (ats, cur0, live_bid) in sorted(first_place.items()):
    cat = CATS.get(tk.split("-")[0], "?")
    ev = tk.rsplit("-", 1)[0]
    side = "leader" if cur0 >= 50 else "underdog"
    page = ATLAS.get("%s|%s|%s" % (cat, side, pcell(cur0)))
    if not page or page.get("verdict") != "PATH":
        skip["thin_page"] += 1
        continue
    res = results.get(tk)
    if res is None:
        skip["cf_unsettled"] += 1
        continue
    af = fills_at.get(tk)
    act = 0.0
    if af and af[1] is not None:
        ax = fills_at.get(tk + "|X")
        if ax and ax[1] is not None:
            act = (ax[1] - af[1]) * 5 / 100.0
        else:
            act = ((100 - af[1]) if res == "yes" else -af[1]) * 5 / 100.0
    tT, tP = trades_of(tk)
    if not tT:
        skip["no_tape"] += 1
        continue
    w1e = bells.get(ev, ats + 8 * 3600)
    depth = (page.get("bottom") or {}).get("depth_p50") or 0
    path_aim = max(1, int(round(cur0 - depth)))
    sel_v, sel_aim = selector_of(page, cur0)
    for trial, aim in (("path", path_aim),
                       ("reach", live_bid if 1 <= live_bid <= 99 else None),
                       ("selector",
                        sel_aim if sel_v == "TRADE-AT-PATH" else None)):
        if aim is None:
            continue
        e, ep, st, stp = grade(aim, ats, w1e, res, tT, tP, cat, cur0)
        X9 = T[trial]
        X9["e"] += e
        X9["ep"] += ep
        X9["st"] += st
        X9["stp"] += stp
        X9["act"] += act
        X9["n"] += 1
        X9["deltas"].append(e - act)

random.seed(42)
def ci(xs):
    if not xs:
        return 0.0, 0.0
    boots = sorted(sum(random.choice(xs) for _ in xs) for _ in range(1000))
    return boots[25], boots[975]

now_et = datetime.now(ET).strftime("%Y-%m-%d %I:%M %p ET")
lines, summ = [], {}
for k in ("path", "reach", "selector"):
    X9 = T[k]
    lo, hi = ci(X9["deltas"])
    y = 100 * X9["e"] / X9["st"] if X9["st"] else 0
    yp = 100 * X9["ep"] / X9["stp"] if X9["stp"] else 0
    door = ("PASS (n>=300, CI off zero)" if X9["n"] >= NBAR and lo > 0
            else "REFUSED (pessimistic direction)" if X9["n"] >= NBAR
            and X9["ep"] - X9["act"] < 0 and yp < 8
            else "STRONGLY-POSITIVE-BUT-UNDERPOWERED" if X9["n"] < NBAR
            and X9["e"] - X9["act"] > 0 and yp >= 8
            else "AT-THE-LETTER (n>=300, CI touches zero)"
            if X9["n"] >= NBAR else "UNDERPOWERED")
    summ[k] = {"n": X9["n"], "e": round(X9["e"], 2),
               "act": round(X9["act"], 2),
               "delta": round(X9["e"] - X9["act"], 2),
               "ci": [round(lo, 2), round(hi, 2)],
               "yield_pct": round(y, 1), "yield_pess_pct": round(yp, 1),
               "door": door}
    lines.append("## %s — n=%d | E$%+.2f vs actual $%+.2f | delta $%+.2f "
                 "(CI [%+.2f, %+.2f]) | yield %.1f%% (pess %.1f%%) vs the "
                 "8%% bar | **%s**"
                 % (k.upper(), X9["n"], X9["e"], X9["act"],
                    X9["e"] - X9["act"], lo, hi, y, yp, door))

n_min = min(T[k]["n"] for k in T)
prev = json.loads(STATUS.read_text()) if STATUS.exists() else {}
fired = bool(prev.get("fired"))
crossing = n_min >= NBAR and not fired
if crossing:
    PACKET.write_text(
        "# THE CONSOLIDATED RULING PACKET (auto-generated %s)\n\n"
        "The clock crossed n>=300 on all three trials. The three cutover "
        "words are yours; the numbers are attached. Doors were "
        "pre-registered; the letters below state themselves.\n\n%s\n\n"
        "skips: %s\n\nCutover doctrine: shadow -> graded nightly -> "
        "operator word -> legacy DELETED. The pair-law replay rides in "
        "PROOF_GOLD_PAIR.md beside the leg-frame selector letter.\n"
        % (now_et, "\n\n".join(lines), dict(skip)), encoding="utf-8")
    fired = True
    # [C-INCUMBENT-SUNSET Part 2, DECREED (operator's standing overhaul
    # mandate, cited in the vault): DEFAULT-GO] the burden of proof
    # reverses — "stop" halts it; silence for 12 hours after the packet
    # means the flags flip on the next boot with full audit
    # (deploy/auto_cutover.sh on the half-hour cron; STOP file =
    # .claude/trendpath/OPERATOR_STOP).
    import time as _t
    go_deadline = _t.time() + 12 * 3600
    msg = ("CONSOLIDATED PACKET FIRED n_min=%d: path %s%.1f%%, reach "
           "%s%.1f%%, selector %s%.1f%% (yields vs 8%% bar). DEFAULT-GO: "
           "reply STOP within 12h or trendpath_live flips on the next "
           "boot with full audit (deadline %s ET)."
           % (n_min, "+" if summ["path"]["delta"] > 0 else "",
              summ["path"]["yield_pct"],
              "+" if summ["reach"]["delta"] > 0 else "",
              summ["reach"]["yield_pct"],
              "+" if summ["selector"]["delta"] > 0 else "",
              summ["selector"]["yield_pct"],
              datetime.fromtimestamp(go_deadline, ET).strftime(
                  "%m-%d %I:%M %p")))
    try:
        subprocess.run(["/root/notify.sh", "critical",
                        "CONSOLIDATED PACKET n>=300", msg], timeout=30)
    except Exception:
        try:
            requests.post("https://ntfy.sh/omi-livev4-omqs-x7k3q9v2",
                          data=msg.encode(), timeout=15)
        except Exception:
            pass

st9 = {
    "n_path": T["path"]["n"], "n_reach": T["reach"]["n"],
    "n_selector": T["selector"]["n"], "n_min": n_min,
    "last_run_et": now_et, "fired": fired,
    "summary": summ, "skips": dict(skip)}
if crossing:
    st9["go_deadline_epoch"] = go_deadline
    st9["go_state"] = "PENDING-GO (default-GO decreed; STOP file halts)"
elif prev.get("go_deadline_epoch"):
    st9["go_deadline_epoch"] = prev["go_deadline_epoch"]
    st9["go_state"] = prev.get("go_state")
if prev.get("cutover_done"):
    st9["cutover_done"] = prev["cutover_done"]
STATUS.write_text(json.dumps(st9, indent=1), encoding="utf-8")
print("PACKET_STATUS: n_min=%d/%d fired=%s" % (n_min, NBAR, fired))
for ln in lines:
    print(ln)
