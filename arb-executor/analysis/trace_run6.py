#!/usr/bin/env python3
"""READ-ONLY RUN-6 per-event process trace. 26JUN03 cohort, entries after the RUN-6 restart
(boundary = last SYSTEM_START ts_epoch). Joins the structured bot log (v4_place / guards / fill /
exit) with fresh Kalshi /fills (is_taker ground truth). Both legs of each event side by side.
Flags: one-sided (which guard skipped the sibling), over-100 fills, deployable-not-bought, cross_on_move."""
import time, base64, requests, json, glob
from pathlib import Path
from collections import defaultdict
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

BASE = "https://api.elections.kalshi.com"; AK = "f3b064d1-a02e-42a4-b2b1-132834694d23"
PK = serialization.load_pem_private_key(Path("kalshi.pem").read_bytes(), password=None, backend=default_backend())
def sign(ts, m, p):
    return base64.b64encode(PK.sign((ts+m+p).encode(), padding.PSS(mgf=padding.MGF1(hashes.SHA256()),
        salt_length=padding.PSS.DIGEST_LENGTH), hashes.SHA256())).decode()
def get(path):
    ts = str(int(time.time()*1000)); h = {"KALSHI-ACCESS-KEY": AK, "KALSHI-ACCESS-SIGNATURE": sign(ts,"GET",path.split("?")[0]), "KALSHI-ACCESS-TIMESTAMP": ts}
    r = requests.get(BASE+path, headers=h, timeout=25); return r.json() if r.status_code==200 else {}

# ---- fills (is_taker truth) ----
fills = []; cur = ""
for _ in range(40):
    d = get("/trade-api/v2/portfolio/fills?limit=500" + ("&cursor="+cur if cur else ""))
    fills += d.get("fills", []); cur = d.get("cursor", "")
    if not cur: break
fillmap = defaultdict(list)
for f in fills:
    if "26JUN03" in f.get("ticker", ""):
        fillmap[f["ticker"]].append(f)

# ---- RUN-6 boundary = last SYSTEM_START ts_epoch ----
LOGS = sorted(glob.glob("logs/live_v3_2026060*.jsonl"))
boundary = 0.0
for lf in LOGS:
    for line in open(lf, errors="replace"):
        if '"system_start"' in line:
            try: boundary = max(boundary, json.loads(line).get("ts_epoch", 0))
            except Exception: pass
print("RUN-6 boundary ts_epoch = %.0f (last SYSTEM_START)\n" % boundary)

# ---- parse RUN-6 log events for 26JUN03 ----
WANT = ("v4_place","entry_filled","v4_exit_posted","paired_basis_skip","v4_fallback_blocked",
        "skip_fat_spread_taker","entry_cancelled","v4_t20m_fallback","v4_move_repost","v4_resting_cancel","order_placed")
place={}; filled={}; xposted={}; pbskip={}; fatskip={}; fblock={}; cancel={}; fallback={}; repost=defaultdict(list); degen={}
crosses = 0
for lf in LOGS:
    for line in open(lf, errors="replace"):
        if '"event"' not in line or not any(w in line for w in WANT): continue
        try: r = json.loads(line)
        except Exception: continue
        if r.get("ts_epoch", 0) < boundary: continue
        e = r.get("event"); tk = r.get("ticker",""); d = r.get("details",{}); ev = d.get("event","")
        if "26JUN03" not in (tk or ev): continue
        if e=="v4_place": place[tk]=d
        elif e=="entry_filled": filled[tk]=d
        elif e=="v4_exit_posted": xposted[tk]=d
        elif e=="paired_basis_skip": pbskip[tk]=d
        elif e=="skip_fat_spread_taker": fatskip[tk]=d
        elif e=="v4_fallback_blocked": fblock[tk]=d
        elif e=="entry_cancelled": cancel[tk]=d
        elif e=="v4_t20m_fallback": fallback[tk]=d
        elif e=="v4_resting_cancel" and d.get("reason","").startswith("degenerate"): degen[tk]=d
        elif e=="v4_move_repost":
            repost[tk].append(d.get("mode"))
            if d.get("mode")=="cross_on_move": crosses += 1

# ---- universe of legs: anything placed, skipped, or filled ----
legs = set(place)|set(pbskip)|set(fatskip)|set(filled)|set(fillmap)
events = defaultdict(list)
for tk in legs:
    events[tk.rsplit("-",1)[0]].append(tk)

def leg_row(tk):
    p = place.get(tk, {}); fl = filled.get(tk, {}); xp = xposted.get(tk, {})
    fs = fillmap.get(tk, [])
    buys = [f for f in fs if f["action"]=="buy"]
    taker = "-" ; paid = "-"
    if buys:
        taker = "TAKER" if any(b["is_taker"] for b in buys) else "maker"
        paid = round(float(buys[0]["yes_price_dollars"])*100) if buys[0].get("outcome_side")=="yes" else round(float(buys[0]["no_price_dollars"])*100)
    guards = []
    if tk in pbskip: guards.append("PAIRED_BASIS(comb=%s>%s)" % (pbskip[tk].get("combined"), pbskip[tk].get("cap")))
    if tk in fatskip: guards.append("FAT_SPREAD")
    if tk in fblock: guards.append("FALLBACK_BLOCKED(%s)" % fblock[tk].get("reason"))
    if tk in cancel: guards.append("MATCH_BUFFER")
    if tk in degen: guards.append("DEGENERATE")
    status = "settled?" if not p and not fs else ("filled" if buys else ("skipped" if (tk in pbskip or tk in fatskip) else "resting/placed"))
    if buys and not xp and status=="filled": status="filled/NO-EXIT"
    return {
        "leg": tk.rsplit("-",1)[1], "dir": (p.get("direction") or (fl.get("direction") or "?"))[:8],
        "cell": p.get("current_price"), "tgt": p.get("target_bid"), "off": p.get("offset"),
        "tsrc": (p.get("table_src") or "-"), "mode": (p.get("entry_mode") or "-"),
        "fallback": "T20m@%s" % fallback[tk].get("take_price") if tk in fallback else "-",
        "guards": ",".join(guards) if guards else "-",
        "taker": taker, "paid": paid, "ask@plc": p.get("current_ask"),
        "exit": xp.get("exit_price"), "band": xp.get("band_x"),
        "repost": "/".join(repost[tk]) if tk in repost else "-", "status": status,
        "_filled": bool(buys), "_paid": paid if buys else None, "_taker": (taker=="TAKER"),
        "_skip": (tk in pbskip or tk in fatskip), "_skipguard": guards[0] if guards else None,
    }

print("="*150)
print("RUN-6 PER-EVENT LIFECYCLE (26JUN03, entry after %.0f) — %d events" % (boundary, len(events)))
print("="*150)
oneside=[]; over100=[]
for ev in sorted(events):
    legs2 = sorted(set(events[ev]))
    print("\n#### %s" % ev.replace("KX",""))
    print("  %-5s %-8s %4s %4s %4s %-10s %-14s %-26s %6s %5s %6s %5s %-12s %s" % (
        "leg","dir","cell","tgt","off","mode","fallback","guards","taker","paid","exit","band","repost","status"))
    rows=[]
    for tk in legs2:
        r=leg_row(tk); rows.append(r)
        print("  %-5s %-8s %4s %4s %4s %-10s %-14s %-26s %6s %5s %6s %5s %-12s %s" % (
            r["leg"], r["dir"], r["cell"], r["tgt"], r["off"], r["mode"][:10], r["fallback"], r["guards"][:26],
            r["taker"], r["paid"], r["exit"], r["band"], r["repost"][:12], r["status"]))
    # flags
    filledrows=[r for r in rows if r["_filled"]]; skiprows=[r for r in rows if r["_skip"]]
    if len(filledrows)>=1 and len(skiprows)>=1:
        oneside.append((ev, [r["leg"] for r in filledrows], [(r["leg"],r["_skipguard"]) for r in skiprows]))
        print("  >>> ONE-SIDED: filled %s ; sibling skipped %s" % ([r["leg"] for r in filledrows], [(r["leg"],r["_skipguard"]) for r in skiprows]))
    if len(filledrows)==2 and all(r["_paid"] for r in filledrows):
        comb=sum(r["_paid"] for r in filledrows)
        tag=" *** OVER-100" if comb>100 else ""
        print("  >>> BOTH-LEGS FILLED: combined basis %d (%s)%s" % (comb, " + ".join("%s:%d/%s"%(r["leg"],r["_paid"],"T" if r["_taker"] else "m") for r in filledrows), tag))
        if comb>100: over100.append((ev,comb))

print("\n" + "="*60)
print("FLAGS SUMMARY")
print("  cross_on_move count (fix-3 must be 0): %d" % crosses)
print("  one-sided events (leg filled, sibling skipped): %d" % len(oneside))
for ev,f,s in oneside: print("     %s filled=%s skipped=%s" % (ev.replace("KX","")[:34], f, s))
print("  over-100 both-legs-filled: %d" % len(over100))
for ev,c in over100: print("     %s combined=%d" % (ev.replace("KX",""), c))
print("  paired_basis_skips on maker path (the 3068 question): %d legs" % len(pbskip))
