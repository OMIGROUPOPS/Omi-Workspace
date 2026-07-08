#!/usr/bin/env python3
"""POST-FILL MOVE QUOTE (read-only). Cohort: honest-era filled legs (from the
evening slate_ledger_v2.json) + tonight's 12 named. Per leg, post-fill, from
premarket_ticks (top-of-book):
 1 time-to-undercut (first best_bid < fill) + undercut depth at +5/15/30/60m
 2 DIVOT vs REPRICE (operator classifier):
   DIVOT  = bid dips below fill BUT min ask(+30m) >= pre-fill ask - 2 AND some
            bid >= fill within 30m of the undercut (book snapped back)
   REPRICE= min ask(+30m) <= pre-fill ask - 3 AND mid(+30m) < fill
   else NO_UNDERCUT (bid never < fill in +60m) or AMBIG.
 3 W1 consequence: band (exit_lvl) touched pregame post-fill (ledger disp/touch
   for era legs; trades-tape prints >= band in fill->bell for tonight's).
Output: /root/post_fill_move.json + printed tables."""
import gzip, json, sys
from collections import defaultdict
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path("/root/Omi-Workspace/arb-executor")
ET = timezone(timedelta(hours=-4))
LEDGER = "/tmp/slate_ledger_v2.json"
TONIGHT = {"KXATPCHALLENGERMATCH-26JUL07BORZEN-ZEN", "KXITFMATCH-26JUL07LOMTOM-TOM",
           "KXITFMATCH-26JUL07NAKSHI-NAK", "KXITFMATCH-26JUL07NAKSHI-SHI",
           "KXITFMATCH-26JUL07NASLEE-LEE", "KXITFMATCH-26JUL07OKIMAT-OKI",
           "KXITFMATCH-26JUL07YAMNAK-YAM", "KXITFWMATCH-26JUL07CHOCAO-CAO",
           "KXITFWMATCH-26JUL07GURKAL-KAL", "KXITFWMATCH-26JUL07WEISUN-SUN",
           "KXITFWMATCH-26JUL07WEISUN-WEI", "KXITFWMATCH-26JUL08TUPPAN-PAN"}

_dc = {}
def pts(s):
    try:
        d, t, ap = s.split(" ")
        if d not in _dc:
            y, mo, dy = d.split("-")
            _dc[d] = datetime(int(y), int(mo), int(dy), tzinfo=ET).timestamp()
        hh, mm, ss = t.split(":")
        return _dc[d] + (int(hh) % 12 + (12 if ap == "PM" else 0)) * 3600 + int(mm) * 60 + int(ss)
    except Exception:
        return None


def ticks_window(tk, t0, t1):
    for suf in (".csv", ".csv.gz"):
        f = ROOT / "analysis" / "premarket_ticks" / (tk + suf)
        if f.exists():
            op = gzip.open if suf.endswith("gz") else open
            out = []
            with op(f, "rt", encoding="utf-8", errors="replace") as fh:
                next(fh, None)
                for ln in fh:
                    p = ln.split(",")
                    if len(p) < 13:
                        continue
                    t = pts(p[0])
                    if t is None or t < t0 or t > t1:
                        continue
                    try:
                        b = int(p[2]) if p[2] else None
                        a = int(p[12]) if p[12] else None
                    except ValueError:
                        continue
                    out.append((t, b, a))
            return out
    return None


def classify(tk, vw, fts):
    tks = ticks_window(tk, fts - 600, fts + 3900)
    if not tks or sum(1 for t, b, a in tks if t > fts) < 5:
        return {"cls": "NO_TAPE"}
    pre_ask = [a for t, b, a in tks if t <= fts and a]
    ask_ref = pre_ask[-1] if pre_ask else None
    post = [(t, b, a) for t, b, a in tks if t > fts]
    und_t = next((t for t, b, a in post if b is not None and b < vw), None)
    def bid_at(mins):
        last = None
        for t, b, a in post:
            if t > fts + mins * 60:
                break
            if b is not None:
                last = b
        return last
    depth = {m: (max(0, round(vw - bid_at(m))) if bid_at(m) is not None else None)
             for m in (5, 15, 30, 60)}
    p30 = [(t, b, a) for t, b, a in post if t <= fts + 1800]
    min_ask30 = min((a for t, b, a in p30 if a), default=None)
    mid30 = None
    for t, b, a in p30[::-1]:
        if b and a:
            mid30 = (b + a) / 2.0
            break
    rec = {"undercut_min": (round((und_t - fts) / 60, 1) if und_t else None),
           "depth": depth, "ask_ref": ask_ref}
    if und_t is None:
        rec["cls"] = "NO_UNDERCUT"
        return rec
    recovered = any(b is not None and b >= vw for t, b, a in post
                    if und_t < t <= und_t + 1800)
    divot = (min_ask30 is not None and ask_ref is not None
             and min_ask30 >= ask_ref - 2 and recovered)
    reprice = (min_ask30 is not None and ask_ref is not None
               and min_ask30 <= ask_ref - 3 and mid30 is not None and mid30 < vw)
    rec["cls"] = "DIVOT" if divot else ("REPRICE" if reprice else "AMBIG")
    return rec


def main():
    D = json.load(open(LEDGER))
    legs = []
    for r in D["rows"]:
        for l in r["legs"]:
            if l.get("vw") is None or not l.get("fill_ts"):
                continue
            touched = ((l.get("disp") or "").startswith("EXIT_FILLED") and
                       (l.get("disp") != "EXIT_FILLED_W2")) or \
                      bool((l.get("touch") or {}).get("W1")) or \
                      bool((l.get("touch") or {}).get("COR"))
            legs.append({"tk": l["tk"], "cat": r["cat"], "vw": l["vw"],
                         "fts": float(l["fill_ts"]), "band": l.get("exit_lvl"),
                         "band_touched_pregame": touched,
                         "w1_filled": bool(l.get("w1_filled"))})
    # only W1/pre-bell fills make sense for the post-fill pregame story
    legs = [l for l in legs if l["w1_filled"]]
    out = []
    for i, l in enumerate(legs):
        rec = classify(l["tk"], l["vw"], l["fts"])
        rec.update({k: l[k] for k in ("tk", "cat", "vw", "band", "band_touched_pregame")})
        out.append(rec)
        if i % 50 == 0:
            print("...", i, "/", len(legs), file=sys.stderr, flush=True)
    json.dump(out, open("/root/post_fill_move.json", "w"))

    agg = {}
    for cat in sorted(set(r["cat"] for r in out)):
        rr = [r for r in out if r["cat"] == cat and r["cls"] != "NO_TAPE"]
        n = len(rr)
        if not n:
            continue
        c = defaultdict(int)
        for r in rr:
            c[r["cls"]] += 1
        und = sorted(r["undercut_min"] for r in rr if r.get("undercut_min") is not None)
        def touch_rate(cls):
            s = [r for r in rr if r["cls"] == cls and r.get("band") is not None]
            return ("%d/%d" % (sum(r["band_touched_pregame"] for r in s), len(s))) if s else "-"
        agg[cat] = {"n": n, "DIVOT": c["DIVOT"], "REPRICE": c["REPRICE"],
                    "NO_UNDERCUT": c["NO_UNDERCUT"], "AMBIG": c["AMBIG"],
                    "undercut_med_min": (und[len(und)//2] if und else None),
                    "band_touch|DIVOT": touch_rate("DIVOT"),
                    "band_touch|REPRICE": touch_rate("REPRICE"),
                    "band_touch|NO_UNDERCUT": touch_rate("NO_UNDERCUT")}
    print(json.dumps(agg, indent=1))
    print("\n== TONIGHT'S 12 ==")
    for l in sorted(TONIGHT):
        # tonight's legs may not be in the ledger yet -> classify ad hoc via fills map
        hits = [r for r in out if r["tk"] == l]
        if hits:
            r = hits[0]
            print(l[-16:], r["cls"], "undercut", r.get("undercut_min"), "depth", r.get("depth"))
        else:
            print(l[-16:], "NOT-IN-LEDGER (classify ad hoc below)")
    json.dump(agg, open("/root/post_fill_agg.json", "w"), indent=1)


if __name__ == "__main__":
    main()
