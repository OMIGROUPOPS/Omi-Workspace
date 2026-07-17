#!/usr/bin/env python3
"""C-TODAY-SHEET v1 — THE OPERATOR'S DAILY SHEET. Render rules (vaulted,
census-enforced): (1) Match and Cat separate columns. (2) FULL MATCH
NAMES from the schedule source — tickers NEVER render. (3) All times ET
wall-clock; Placed and Filled are standing columns. (4) Fill¢ beside the
best-achievable W1 fill¢ with its timestamp. (5) Dual clock columns
where the real bell and Kalshi's schedule diverge — gun source named.
(6) Unfilled-bid language exact: "never traded that low" or "we pulled
it (reason, time ET)" — the word r*fused NEVER appears on this surface.
(7) A render violating any rule = STANDARD DEFECT (the nightly census
scans this file). No behavior changes — the sheet only.

Usage: python3 analysis/today_sheet.py [--date YYYYMMDD]
Out:   .claude/today_sheet/TODAY_SHEET_<date>.md (+ LATEST.md copy)"""
import argparse
import base64
import bisect
import gzip
import json
import sqlite3
import time
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import requests
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

ET = ZoneInfo("America/New_York")
ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT.parent / ".claude" / "today_sheet"
BASE = "https://api.elections.kalshi.com"
AK = "f3b064d1-a02e-42a4-b2b1-132834694d23"
PK = serialization.load_pem_private_key(
    (ROOT / "kalshi.pem").read_bytes(), password=None,
    backend=default_backend())


def sign(ts, m, p):
    return base64.b64encode(PK.sign((ts + m + p).encode(), padding.PSS(
        mgf=padding.MGF1(hashes.SHA256()),
        salt_length=padding.PSS.DIGEST_LENGTH), hashes.SHA256())).decode()


def get(p):
    for a in range(4):
        ts = str(int(time.time() * 1000))
        sp = p.split("?")[0]
        h = {"KALSHI-ACCESS-KEY": AK,
             "KALSHI-ACCESS-SIGNATURE": sign(ts, "GET", sp),
             "KALSHI-ACCESS-TIMESTAMP": ts,
             "Content-Type": "application/json"}
        try:
            r = requests.get(BASE + p, headers=h, timeout=20)
        except Exception:
            time.sleep(2)
            continue
        if r.status_code == 200:
            return r.json()
        if r.status_code == 429:
            time.sleep(2 + a)
            continue
        return {}
    return {}


def hm(ep):
    if ep is None:
        return "—"
    return datetime.fromtimestamp(ep, ET).strftime("%I:%M %p")


def cat_of(et):
    for pre, c in (("KXITFWMATCH", "ITF_W"), ("KXITFMATCH", "ITF_M"),
                   ("KXATPCHALLENGER", "ATP_CHALL"),
                   ("KXWTACHALLENGER", "WTA_CHALL"),
                   ("KXATPMATCH", "ATP_MAIN"), ("KXWTAMATCH", "WTA_MAIN")):
        if et.startswith(pre):
            return c
    return "?"


def load_names():
    """rule 2: full match names from the schedule source"""
    try:
        sc = json.loads((ROOT / "state" / "schedule.json").read_text())
        out = {}
        for code, v in (sc.get("schedule") or {}).items():
            out[code.upper()] = "%s vs %s" % (v.get("p1", "?"),
                                              v.get("p2", "?"))
        return out
    except Exception:
        return {}


NAMES = load_names()


def match_name(et):
    code = et.rsplit("-", 1)[-1][7:] if "-" in et else et
    # event code = the pair code after the date (26JUL16XXXXXX)
    seg = et.split("-")[-1]
    code = seg[7:] if len(seg) > 7 else seg
    nm = NAMES.get(code.upper())
    if nm:
        return nm
    # fall back to split code halves — still names-ish, never a ticker
    h = len(code) // 2
    return "%s vs %s (name join pending)" % (code[:h].title(),
                                             code[h:].title())


def leg_name(tk, et):
    """the leg rendered as the PLAYER code half, not the ticker"""
    leg = tk.rsplit("-", 1)[-1]
    return leg.title()


def day_lines(ymd):
    p = ROOT / "logs" / ("live_v3_%s.jsonl" % ymd)
    if p.exists():
        return open(p, encoding="utf-8", errors="replace")
    pz = ROOT / "logs" / ("live_v3_%s.jsonl.gz" % ymd)
    if pz.exists():
        return gzip.open(pz, "rt", encoding="utf-8", errors="replace")
    return []


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", default=datetime.now(ET).strftime("%Y%m%d"))
    args = ap.parse_args()
    ymd = args.date
    mid = datetime.strptime(ymd, "%Y%m%d").replace(tzinfo=ET).timestamp()
    now = time.time()
    OUT.mkdir(parents=True, exist_ok=True)

    # ---------- collect the session from the logs (today + carried) ----
    fills, exits, setl, buys, cancels = {}, {}, {}, defaultdict(list), \
        defaultdict(list)
    guns, sched, seen, dossier_reason = {}, {}, set(), {}
    exitpost = {}
    prev = (datetime.strptime(ymd, "%Y%m%d") - timedelta(days=1)
            ).strftime("%Y%m%d")
    for day in (prev, ymd):
        for line in day_lines(day):
            if not any(k in line for k in (
                    '"entry_filled"', '"exit_filled"',
                    '"event": "settled"', '"order_placed"',
                    '"order_cancelled"', '"event": "gun_fired"',
                    '"schedule_match"', '"v4_exit_posted"',
                    '"entry_dossier"', '"skipped"')):
                continue
            try:
                d = json.loads(line)
            except ValueError:
                continue
            e = d.get("event")
            det = d.get("details") or {}
            tk = d.get("ticker", "")
            ep = d.get("ts_epoch", 0)
            et = det.get("event") or (tk.rsplit("-", 1)[0] if tk else "")
            if et:
                seen.add(et)
            if e == "schedule_match" and et and et not in sched:
                st = det.get("start_time")
                if st:
                    try:
                        sched[et] = datetime.fromisoformat(st).timestamp()
                    except Exception:
                        pass
            elif e == "gun_fired" and et and et not in guns:
                g = {"ts": ep, "source": det.get("source")}
                th = det.get("tts_honest_min")
                if th is not None:
                    g["honest"] = g["ts"] + th * 60.0
                guns[et] = g
            elif e == "order_placed" and tk:
                if det.get("action") == "buy":
                    buys[tk].append({"ts": ep, "px": det.get("price"),
                                     "qty": det.get("count"),
                                     "oid": det.get("order_id", "")[:8]})
            elif e == "order_cancelled" and tk:
                cancels[tk].append({"ts": ep, "label": det.get("label")})
            elif e == "entry_filled" and tk and tk not in fills:
                fills[tk] = {"ts": ep, "px": det.get("fill_price"),
                             "qty": det.get("qty") or 5,
                             "window": (det.get("window") or {}).get(
                                 "phase")}
            elif e == "v4_exit_posted" and tk:
                exitpost[tk] = {"px": det.get("exit_price"),
                                "band": det.get("band_x"),
                                "oid": det.get("order_id", "")[:8]}
            elif e == "exit_filled" and tk:
                exits[tk] = {"ts": ep, "px": det.get("exit_price"),
                             "pnl": det.get("pnl_cents"),
                             "tid": det.get("trade_id", "")}
            elif e == "settled" and tk:
                setl[tk] = {"ts": ep, "res": det.get("settle"),
                            "px": det.get("settle_price"),
                            "pnl": det.get("pnl_cents"),
                            "tid": det.get("trade_id", "")}
            elif e == "entry_dossier" and tk:
                dc = str(det.get("decision", ""))
                if dc.startswith("refused"):
                    dossier_reason.setdefault(tk, dc.split(":", 1)[-1])

    # session scope: rows whose FILL or last BUY or SETTLE is today, or
    # open-at-midnight carried, or posted for a post-midnight match
    def in_session(tk):
        f = fills.get(tk)
        if f and f["ts"] >= mid:
            return True, False
        if f and tk not in exits and tk not in setl:
            return True, True     # carried open
        if f and (exits.get(tk, {}).get("ts", 0) >= mid
                  or setl.get(tk, {}).get("ts", 0) >= mid):
            return True, f["ts"] < mid
        bb = buys.get(tk) or []
        if any(b["ts"] >= mid for b in bb):
            return True, False
        et = tk.rsplit("-", 1)[0]
        if bb and sched.get(et, 0) >= mid:
            return True, True     # carried resting for a post-midnight match
        return False, False

    # tape per touched event (small slate: only events with session rows)
    tape_cache = {}

    def tape(et):
        if et in tape_cache:
            return tape_cache[et]
        rows = {}
        d0 = get("/trade-api/v2/markets?event_ticker=%s&limit=100" % et)
        for m in d0.get("markets", []):
            r, cur = [], ""
            for page in range(20):
                d = get("/trade-api/v2/markets/trades?ticker=%s&limit=1000"
                        % m["ticker"] + (("&cursor=" + cur) if cur else ""))
                tr = d.get("trades", [])
                if not tr:
                    break
                for t in tr:
                    ep = datetime.fromisoformat(
                        t["created_time"].replace("Z", "+00:00")
                        ).timestamp()
                    r.append((ep, round(float(
                        t["yes_price_dollars"]) * 100)))
                cur = d.get("cursor", "")
                if not cur:
                    break
                time.sleep(0.1)
            r.sort()
            rows[m["ticker"]] = r
        tape_cache[et] = rows
        return rows

    def bell_of(et):
        g = guns.get(et, {})
        return g.get("honest") or g.get("ts"), g.get("source")

    def w1_best(tk, et):
        """rule 4: best-achievable W1 fill = tape low BEFORE the real
        bell (or before Kalshi sched when no bell), with its timestamp"""
        bell, _src = bell_of(et)
        cut = bell or sched.get(et) or now
        rows = tape(et).get(tk) or []
        pre = [(px, ep) for ep, px in rows if ep <= cut and ep >= mid - 86400]
        if not pre:
            return None, None
        px, ep = min(pre)
        return px, ep

    def best_after(tk, fill_ts):
        rows = tape(et_of(tk)).get(tk) or []
        after = [(px, ep) for ep, px in rows if ep > fill_ts]
        if not after:
            return None, None
        px, ep = max(after)
        return px, ep

    def et_of(tk):
        return tk.rsplit("-", 1)[0]

    def dual_clock(et):
        bell, src = bell_of(et)
        ks = sched.get(et)
        if bell and ks and abs(bell - ks) > 600:
            return ("bell %s (%s)" % (hm(bell), src or "?"),
                    "sched %s (Δ%+.0fm)" % (hm(ks), (bell - ks) / 60.0))
        if bell:
            return ("bell %s (%s)" % (hm(bell), src or "?"), "agrees")
        return ("no bell yet", "sched %s" % hm(ks) if ks else "no join")

    def pulled_language(tk):
        """rule 6 — exact language, the banned word never prints"""
        cc = [c for c in (cancels.get(tk) or []) if c["ts"] >= mid]
        bb = [b for b in (buys.get(tk) or [])]
        if cc:
            c = cc[-1]
            label = {"match_live_cancel": "match went live",
                     "v4_move_repost": "re-aimed",
                     "shutdown_cancel": "deploy drain",
                     "completion_live_resolve": "pair resolved",
                     "v4_t20m_fallback": "T-20m re-aim"}.get(
                c["label"], c["label"])
            return "we pulled it (%s, %s ET)" % (label, hm(c["ts"]))
        if bb:
            aim = bb[-1]["px"]
            lo, _ = w1_best(tk, et_of(tk))
            if lo is None or lo > aim:
                return "never traded that low"
            return "traded %d¢ at %s but our bid arrived later" % (
                lo, "—")
        return "never traded that low"

    # ---------- buckets ----------
    B1, B2, B3, B4 = [], [], [], []
    touched = set()
    for tk in sorted(set(list(fills) + list(buys))):
        ok, carried = in_session(tk)
        if not ok:
            continue
        et = et_of(tk)
        touched.add(et)
        cat = cat_of(et)
        nm = match_name(et)
        f = fills.get(tk)
        carry = " ◐carried" if carried else ""
        if f:
            wb, wbts = w1_best(tk, et)
            dc1, dc2 = dual_clock(et)
            xp = exitpost.get(tk) or {}
            hi, hits = best_after(tk, f["ts"])
            close = ("EXIT %d¢ %s" % (exits[tk]["px"], hm(exits[tk]["ts"]))
                     if tk in exits else
                     "SETTLED %s %d¢" % (setl[tk]["res"], setl[tk]["px"]
                                         or 0) if tk in setl else "OPEN")
            pnl = (exits.get(tk) or setl.get(tk) or {}).get("pnl")
            first_buy = min((b["ts"] for b in buys.get(tk, [])),
                            default=None)
            row = [nm + carry, cat, leg_name(tk, et),
                   "%d¢" % (xp.get("band") or 0),
                   hm(first_buy), hm(f["ts"]),
                   "%d¢" % f["px"],
                   ("%d¢ @%s" % (wb, hm(wbts))) if wb is not None
                   else "no pre-bell tape",
                   dc1, dc2,
                   ("%d¢ (+%d)" % (xp.get("px") or 0, xp.get("band") or 0))
                   if xp else "—",
                   ("%d¢ @%s" % (hi, hm(hits))) if hi is not None else "—",
                   close,
                   ("%+d¢ (%.0f%% of basis %d¢)" % (
                       pnl, pnl / f["px"] * 100 if f["px"] else 0,
                       f["px"])) if pnl is not None else "open"]
            if tk in exits or tk in setl:
                B1.append(row)
            else:
                mk = get("/trade-api/v2/markets/%s" % tk).get(
                    "market", {}).get("yes_bid_dollars")
                mkc = round(float(mk) * 100) if mk is not None else None
                B2.append(row[:13] + [
                    ("%d¢ (%+d¢ vs basis)" % (mkc, mkc - f["px"]))
                    if mkc is not None else "no bid",
                    ("%d¢ ×%s (order %s)" % (xp.get("px") or 0,
                                             f["qty"], xp.get("oid", "—")))
                    if xp else "NO EXIT RESTING"])
        else:
            bb = [b for b in buys.get(tk, [])]
            aim = bb[-1]["px"] if bb else None
            lo, lots = w1_best(tk, et)
            B3.append([nm + carry, cat, leg_name(tk, et),
                       "%d¢" % aim if aim is not None else "—",
                       ("%d¢ @%s" % (lo, hm(lots))) if lo is not None
                       else "no tape",
                       pulled_language(tk)])

    # bucket 4: seen today, never bid
    for et in sorted(seen):
        if et in touched:
            continue
        est = sched.get(et)
        if est and not (mid <= est <= mid + 86400 * 1.5):
            continue
        cat = cat_of(et)
        legs_bid = any(t.startswith(et + "-") for t in buys)
        if legs_bid:
            continue
        reasons = {dossier_reason.get(et + "-" + s) for s in ("", )}
        rs = [v for k, v in dossier_reason.items()
              if k.startswith(et + "-")]
        plain = ("below volume floor" if any("discovery" in r for r in rs)
                 else "aim under the lawful floor — never conceived"
                 if any("leg_floor" in r for r in rs)
                 else "pair could not compose" if any(
                     "seesaw" in r or "pair" in r for r in rs)
                 else "no fitted page — never conceived" if any(
                     "path_page" in r for r in rs)
                 else "outside window" if any(
                     "w1_preference" in r or "expression" in r for r in rs)
                 else "never conceived")
        intent = "intentional" if rs else "never reached a decision"
        B4.append([match_name(et), cat, "—", intent, plain,
                   "tape: see game report"])

    # ---------- header ----------
    navrow = None
    try:
        con = sqlite3.connect("file:%s?mode=ro" % (
            ROOT / "state" / "fund_equity.db"), uri=True, timeout=2)
        navrow = con.execute("SELECT equity_c, cash_c, marked_c FROM "
                             "equity ORDER BY ts DESC LIMIT 1").fetchone()
        con.close()
    except Exception:
        pass
    real_tail = real_path = wag = 0.0
    for tk, x in list(exits.items()) + list(setl.items()):
        if x.get("ts", 0) < mid:
            continue
        p = x.get("pnl") or 0
        if str(x.get("tid", "")).startswith("T-" + ymd):
            real_path += p
        else:
            real_tail += p
    for tk, f in fills.items():
        if f["ts"] >= mid:
            wag += (f["px"] or 0) * (f["qty"] or 5) / 100.0
    n_filled = sum(1 for tk in fills if in_session(tk)[0])
    n_posted = len(B3)
    n_listed = len(seen)
    p_off = (n_filled / (n_filled + n_posted) * 100.0
             if (n_filled + n_posted) else 0.0)
    p_mkt = ((n_filled) / max(1, n_listed * 2) * 100.0)

    L = ["# TODAY'S SHEET — %s (session 12:00 AM ET onward; ◐ = carried)"
         % datetime.strptime(ymd, "%Y%m%d").strftime("%B %d, %Y"),
         "(C-TODAY-SHEET v1 — render rules vaulted + census-enforced; "
         "generated %s ET)" % datetime.now(ET).strftime("%I:%M %p"), ""]
    L.append("**NAV %s** · session realized: TAIL %+.0f¢ | PATH %+.0f¢ · "
             "wagered today $%.2f · **P-offered (executor) %.0f%% "
             "(%d filled / %d posted-unfilled)** · **P-market (funnel) "
             "%.1f%% (%d filled legs / ~%d listed legs)**"
             % ("$%.2f" % (navrow[0] / 100.0) if navrow else "warming",
                real_tail, real_path, wag, p_off, n_filled, n_posted,
                p_mkt, n_filled, n_listed * 2))
    # [ENTRY-MECHANICS P2b 07-17] THE CHURN METER — reposts per leg per
    # session-hour, nightly (the panel carries the trailing-hour twin).
    # Exhibits sized the bar: BURMER 42, top legs 40-53/leg/hr on 07-17.
    _ch_counts = {}
    _ch_hours = {}
    for tk, cl in cancels.items():
        for c in cl:
            if c.get("label") == "v4_move_repost" and c["ts"] >= mid:
                _ch_counts[tk] = _ch_counts.get(tk, 0) + 1
                _ch_hours.setdefault(tk, set()).add(int(c["ts"] // 3600))
    if _ch_counts:
        _ch_rates = sorted(((n / max(1, len(_ch_hours.get(t, ()))), t, n)
                            for t, n in _ch_counts.items()), reverse=True)
        _ch_tot = sum(_ch_counts.values())
        L.append("**CHURN METER** · %d reposts / %d legs today · worst: %s"
                 % (_ch_tot, len(_ch_counts),
                    " · ".join("%s %.0f/hr (%d)" % (
                        t.split("-")[-2][-8:] + "-" + t.split("-")[-1],
                        r, n) for r, t, n in _ch_rates[:4])))
    # [ENTRY-MECHANICS ADDENDUM (a) 07-17] THE CUTOFF IS LAW: every meter
    # splits old-era vs new-era at the new-law boot epoch — the day reads
    # as a before/after experiment.
    try:
        _ep_p = ROOT / "state" / "new_law_epoch.json"
        if _ep_p.exists():
            _ep = float(json.loads(_ep_p.read_text()).get("epoch") or 0)
            if _ep and _ep > mid:
                _f_old = sum(1 for f in fills.values() if f["ts"] < _ep)
                _f_new = sum(1 for f in fills.values() if f["ts"] >= _ep)
                _r_old = _r_new = 0
                for cl in cancels.values():
                    for c in cl:
                        if c.get("label") == "v4_move_repost" \
                                and c["ts"] >= mid:
                            if c["ts"] < _ep:
                                _r_old += 1
                            else:
                                _r_new += 1
                _hrs_old = max(0.1, (_ep - mid) / 3600.0)
                _hrs_new = max(0.1, (time.time() - _ep) / 3600.0)
                L.append("**ERA SPLIT (new-law epoch %s ET)** · fills "
                         "old %d / new %d · reposts old %d (%.0f/hr) / "
                         "new %d (%.0f/hr)"
                         % (datetime.fromtimestamp(_ep, ET).strftime(
                             "%I:%M %p"), _f_old, _f_new,
                            _r_old, _r_old / _hrs_old,
                            _r_new, _r_new / _hrs_new))
    except Exception:
        pass

    def table(title, headers, rows):
        L.append("")
        L.append("## %s (%d)" % (title, len(rows)))
        if not rows:
            L.append("- none")
            return
        L.append("| " + " | ".join(headers) + " |")
        L.append("|" + "---|" * len(headers))
        for r in rows:
            L.append("| " + " | ".join(str(c) for c in r) + " |")

    table("① SETTLED",
          ["Match", "Cat", "Leg", "Band", "Placed ET", "Filled ET",
           "Fill¢", "W1-best¢ @ET", "Real bell", "vs Kalshi sched",
           "Exit required", "Best tick after fill", "Close", "$"], B1)
    table("② OPEN",
          ["Match", "Cat", "Leg", "Band", "Placed ET", "Filled ET",
           "Fill¢", "W1-best¢ @ET", "Real bell", "vs Kalshi sched",
           "Exit required", "Best tick after fill", "Close",
           "Mark", "Exit resting"], B2)
    table("③ POSTED, DID NOT FILL",
          ["Match", "Cat", "Leg", "Aim¢", "Tape low¢ @ET",
           "Why unfilled"], B3)
    table("④ NOT BID",
          ["Match", "Cat", "Band", "Intent", "Plain reason",
           "What the tape did"], B4)

    body = "\n".join(L) + "\n"
    fp = OUT / ("TODAY_SHEET_%s.md" % ymd)
    fp.write_text(body, encoding="utf-8")
    (OUT / "LATEST.md").write_text(body, encoding="utf-8")
    print("today_sheet: %s (S%d O%d P%d N%d)" % (
        fp, len(B1), len(B2), len(B3), len(B4)))


if __name__ == "__main__":
    main()
