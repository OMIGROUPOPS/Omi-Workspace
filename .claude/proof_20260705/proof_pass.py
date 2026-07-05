#!/usr/bin/env python3
"""[READ-ONLY] PROOF PASS 2026-07-05 — per-game guilty code + per-fix tape replay.
Consumes /tmp/ftr_dump.json (full_tape_regrade.py, re-run first), state/schedule.json
(honest clock), the live logs (posted-never-filled bids), and Kalshi REST trades (mains
tape). Writes /tmp/proof_rows.json + /tmp/proof_summary.txt. NO bot-state writes.

REPLAY CONVENTIONS (stated, conservative):
- A fill is claimed ONLY where the dump's tape work already proved a catchable dip at/below
  the claimed level (legs[].best catchable, fader.cheapest_pre) or REST prints show it.
- FIX A (per_match_clock, staged ce38ca8c): completion-recovery channel — naked single where
  the fader's dip<=bound passed BEFORE the bound existed (half_timing). Replayed as: honest
  window opens T-240m on the TE/ESPN clock; leg1's catchable best dip must occur inside the
  honest window AND before the fader divot; then the pair completes at leg1_best + fader_divot.
  Dollars = pair settle (100-combined)*qty vs actual naked pnl. No honest join -> NO CHANGE.
- FIX B (scale-aware gun, Part-3 shadow -> proposed on _MAIN only): posted-never-filled mains
  bids cancelled on the premature latch; replay = bid survives (gun invalid on _MAIN, proxy
  fire = honest TE start); fill if REST prints <= posted px between actual cancel and proxy;
  settle outcome from the market result. Losses count NEGATIVE (no free credit).
- FIX C (riser_post revision, proposed CHALL 3/ITF 3/2, mains hold): riser fills re-posted
  depth c lower; retained iff legs[].best.px <= revised (catchable); retained -> +depth*qty c;
  lost -> -(that leg's actual pnl) (pair-break risk flagged, sibling kept as-is).
"""
import json, re, sys, time, base64
from pathlib import Path
from collections import Counter, defaultdict
from datetime import datetime, timezone, timedelta

ROOT = Path("/root/Omi-Workspace/arb-executor")
ET = timezone(timedelta(hours=-4))
GOAL = 97
DEPTH = {"ATP_CHALL": 3, "WTA_CHALL": 3, "ITF_M": 3, "ITF_W": 2}   # riser revision; mains hold

dump = json.load(open("/tmp/ftr_dump.json"))
games = dump["games"]

# ---------- honest clock join ----------
sch = json.load(open(ROOT / "state" / "schedule.json"))
sched = sch.get("schedule", {})
def pair_code(ev):
    m = re.search(r"\d{2}[A-Z]{3}\d{2}([A-Z]+)$", ev)
    return m.group(1) if m else None
def honest_start(ev):
    pc = pair_code(ev)
    if not pc or len(pc) != 6:
        return None
    for k in (pc, pc[3:] + pc[:3]):
        e = sched.get(k)
        if e and not e.get("espn_midnight"):
            st = e.get("start_time", "")
            try:
                return datetime.fromisoformat(st.replace("Z", "+00:00")).timestamp()
            except Exception:
                pass
    return None

# ---------- guilty-line map from the RUNNING source ----------
src = open(ROOT / "live_v4.py", encoding="utf-8", errors="replace").read().splitlines()
def line_of(pat):
    for i, l in enumerate(src, 1):
        if re.search(pat, l):
            return i
    return None
L = {
    "kprim": line_of(r'"method": "kalshi_schedule_primary"'),
    "maxlead": line_of(r"^V4_MAX_PLACEMENT_SEC"),
    "ctarget": line_of(r"def _completion_target"),
    "anchor": line_of(r"def _v4_entry_anchor"),
    "mlive": line_of(r"def _is_match_live"),
    "mcancel": line_of(r'"match_live_resting_cancel"') or line_of(r"match_live_resting_cancel"),
    "t20m": line_of(r"v4_t20m_fallback"),
    "riser": line_of(r"riser_post"),
    "hold": line_of(r"def _v4_check_exits") or line_of(r"settled"),
}
def gl(key, label):
    n = L.get(key)
    return "%s (live_v4.py:%s)" % (label, n if n else "?")

# ---------- Kalshi REST (mains tape only) ----------
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.backends import default_backend
import requests
pk = serialization.load_pem_private_key((ROOT / "kalshi.pem").read_bytes(), password=None, backend=default_backend())
B = "https://api.elections.kalshi.com/trade-api/v2"
KEY = "f3b064d1-a02e-42a4-b2b1-132834694d23"
def sgn(m, p):
    ts = str(int(time.time() * 1000)); sp = "/trade-api/v2" + p.split("?")[0]
    sig = pk.sign((ts + m + sp).encode(), padding.PSS(mgf=padding.MGF1(hashes.SHA256()),
                  salt_length=padding.PSS.DIGEST_LENGTH), hashes.SHA256())
    return {"KALSHI-ACCESS-KEY": KEY, "KALSHI-ACCESS-SIGNATURE": base64.b64encode(sig).decode(),
            "KALSHI-ACCESS-TIMESTAMP": ts}
def gget(p):
    for _ in range(4):
        try:
            return requests.get(B + p, headers=sgn("GET", p), timeout=30).json()
        except Exception:
            time.sleep(0.5)
    return {}
def trades_of(tk):
    out, cur = [], ""
    for _ in range(20):
        r = gget("/markets/trades?ticker=%s&limit=1000%s" % (tk, "&cursor=" + cur if cur else ""))
        for t in r.get("trades", []):
            try:
                ts = datetime.fromisoformat(t["created_time"].replace("Z", "+00:00")).timestamp()
                px = t.get("yes_price")
                if px is None:
                    px = round(float(t["yes_price_dollars"]) * 100)
                out.append((ts, int(px)))
            except Exception:
                pass
        cur = r.get("cursor", "")
        if not cur:
            break
    return sorted(out)

# ---------- FIX B substrate: mains posted-never-filled bids ----------
mains_bids = {}   # tk -> {posted_px, posted_ts, cancel_ts}
filled_tks = {l["tk"] for g in games for l in (g.get("legs") or [])}
mains_evs = {g["ev"]: g for g in games if g["cat"] in ("ATP_MAIN", "WTA_MAIN")}
buys = defaultdict(list); cxl = defaultdict(list)
for LOG in ("logs/live_v3_20260704.jsonl", "logs/live_v3_20260705.jsonl"):
    p = ROOT / LOG
    if not p.exists():
        continue
    for line in open(p, encoding="utf-8", errors="replace"):
        if '"order_placed"' not in line and "cancel" not in line:
            continue
        try:
            o = json.loads(line)
        except Exception:
            continue
        tk = o.get("ticker") or ""
        ev = tk.rsplit("-", 1)[0] if tk else ""
        if ev not in mains_evs or tk in filled_tks:
            continue
        e, d, ts = o.get("event"), o.get("details", {}), o.get("ts_epoch", 0)
        if e == "order_placed" and d.get("action") == "buy" and d.get("price") is not None:
            buys[tk].append((ts, d["price"]))
        elif e in ("order_canceled", "order_cancelled", "match_live_resting_cancel"):
            cxl[tk].append(ts)

def settle_side(ev, suf):
    """Winner from any settled sibling in the dump, else REST market result."""
    g = mains_evs.get(ev)
    for l in (g.get("legs") or []):
        oc = l.get("outc", "")
        if oc.startswith("settle_"):
            won = oc == "settle_WIN"
            return won if l["suf"] == suf else (not won)
    r = gget("/markets?tickers=%s-%s" % (ev, suf)).get("markets", [])
    if r and r[0].get("result") in ("yes", "no"):
        return r[0]["result"] == "yes"
    return None

# ---------- per-game rows ----------
def hm_px(hit):
    return datetime.fromtimestamp(hit[0], ET).strftime("%H:%M")

rows = []
tot = {"A": 0.0, "B": 0.0, "C": 0.0}
diag = Counter()
for g in games:
    ev, cat, grade = g["ev"], g["cat"], g["grade"]
    pnl = g.get("pnl") or 0.0
    legs = g.get("legs") or []
    fader = g.get("fader") or {}
    errs = g.get("err") or []
    hst = honest_start(ev)

    # ----- guilty line -----
    guilty = []
    naked = g["n_legs"] == 1
    half_timing = naked and fader.get("pre_dip_le_bound") and not fader.get("bound_arrived_in_time")
    if half_timing:
        guilty.append(gl("kprim", "placeholder clock window (kalshi_schedule_primary)") + " + " + gl("maxlead", "T-4h lead on that clock"))
    elif naked:
        guilty.append(gl("anchor", "partner never reached: _v4_entry_anchor level vs tape / queue"))
    if any("over-par" in e for e in errs):
        guilty.append(gl("ctarget", "pre-ruling bound hole (FIXED live 21eaad4 C-BOUND-RULING)"))
    if any("zero-discount" in e for e in errs) or any(l.get("side") == "riser" and (l.get("d_aim") or 0) <= 1 for l in legs):
        guilty.append(gl("riser", "riser_post=0 aim (aim_table.json): bid at the going rate"))
    if any("directional hold" in e for e in errs):
        guilty.append("hold-to-settle on the losing leg (exit design; OUT OF SCOPE per Vault 0A)")
    if any("deep-neg FV" in e for e in errs) and not guilty:
        guilty.append(gl("riser", "riser adverse selection (C44: fills when the leg fades in)"))
    if not guilty:
        guilty.append("none charged (grade %s)" % grade)

    # ----- FIX A: completion recovery on the honest clock -----
    dA, nA = 0.0, "no change"
    if half_timing:
        diag["A_half_timing_games"] += 1
        if hst is None:
            nA = "no honest join -> NO CLAIM"
            diag["A_no_join"] += 1
        else:
            l1 = legs[0]
            b = l1.get("best") or {}
            divot_ts = fader.get("cheapest_pre_ts")
            win_open = hst - 240 * 60
            if (b.get("catchable") and divot_ts and b.get("ts")
                    and b["ts"] >= win_open and b["ts"] < divot_ts
                    and fader.get("cheapest_pre_ts") >= win_open):
                comb = (b["px"] or 0) + (fader.get("cheapest_pre_px") or 0)
                if comb <= 100:
                    qty = l1.get("qty") or 5
                    new_pnl = (100 - comb) * qty / 100.0
                    dA = round(new_pnl - pnl, 2)
                    nA = "pair completes %dc (leg1@%d pre-divot + fader@%d) -> %s" % (
                        comb, b["px"], fader.get("cheapest_pre_px"),
                        "A/B" if comb <= GOAL else "C")
                else:
                    nA = "honest window pair >100c -> NO CLAIM"
                    diag["A_over100"] += 1
            else:
                nA = "tape: leg1 catchable dip not before fader divot in honest window -> NO CLAIM"
                diag["A_no_predivot_dip"] += 1
    tot["A"] += dA

    # ----- FIX B: mains scale-gun survival -----
    dB, nB = 0.0, "no change"
    if cat in ("ATP_MAIN", "WTA_MAIN"):
        for tk, bl in buys.items():
            if not tk.startswith(ev):
                continue
            if not cxl.get(tk):
                continue
            posted_ts, posted_px = sorted(bl)[-1]
            cts = max(cxl[tk])
            proxy = hst if hst else None
            tape = trades_of(tk)
            hit = next((t for t in tape if t[0] > cts and (proxy is None or t[0] <= proxy + 90 * 60) and t[1] <= posted_px), None)
            if hit:
                suf = tk.rsplit("-", 1)[1]
                won = settle_side(ev, suf)
                qty = 5
                if won is True:
                    dB += (100 - posted_px) * qty / 100.0
                    nB = "%s bid %dc survives, fills @%s, settles WIN" % (suf, posted_px, hm_px(hit))
                elif won is False:
                    dB += -posted_px * qty / 100.0
                    nB = "%s bid %dc survives, fills, settles LOSS (counted)" % (suf, posted_px)
                else:
                    nB = "fillable after cancel but result unknown -> NO CLAIM"
            else:
                nB = "no print <= posted after premature cancel -> no change"
    dB = round(dB, 2)
    tot["B"] += dB

    # ----- FIX C: riser depth revision -----
    dC, parts = 0.0, []
    lostC = retC = 0
    dep = DEPTH.get(cat)
    if dep:
        for l in legs:
            if l.get("side") != "riser" or not l.get("fill"):
                continue
            b = l.get("best") or {}
            revised = l["fill"] - dep
            qty = l.get("qty") or 5
            post_ts = l.get("posted_first_ts") or l.get("fill_ts") or 0
            end_ts = g.get("latch_ts") or 9e12
            # retained ONLY if the REAL TAPE prints <= revised while the revised bid rests
            # (post time -> tape latch), the same forward-min convention as riser_depth_replay
            tape = trades_of(l["tk"])
            fwd_hit = any(post_ts <= t <= end_ts and px <= revised for t, px in tape)
            if fwd_hit:
                dC += dep * qty / 100.0
                retC += 1
                parts.append("%s retained @%d (+%dc)" % (l["suf"], revised, dep))
            else:
                dC += -(l.get("pnl") or 0.0)
                lostC += 1
                parts.append("%s LOST (floor %s / t) -> -leg pnl %.2f" % (l["suf"], b.get("px"), l.get("pnl") or 0.0))
    dC = round(dC, 2)
    nC = "; ".join(parts) if parts else "no riser leg / mains hold"
    if lostC and g["n_legs"] == 2:
        nC += " [pair breaks -> naked risk]"
    tot["C"] += dC
    diag["C_retained"] += retC
    diag["C_lost"] += lostC

    rows.append({"ev": ev, "cat": cat, "grade": grade, "pnl": round(pnl, 2),
                 "guilty": " | ".join(guilty), "dA": dA, "nA": nA,
                 "dB": dB, "nB": nB, "dC": dC, "nC": nC,
                 "honest_join": hst is not None})

json.dump({"generated": time.time(), "boot": dump.get("boot"), "lines": L,
           "rows": rows, "totals": {k: round(v, 2) for k, v in tot.items()}},
          open("/tmp/proof_rows.json", "w"), indent=1)

with open("/tmp/proof_summary.txt", "w") as f:
    f.write("games=%d actual_pnl=%.2f\n" % (len(rows), sum(r["pnl"] for r in rows)))
    for k in ("A", "B", "C"):
        ch = sum(1 for r in rows if r["d" + k])
        f.write("FIX %s: delta $%.2f across %d games (others: no change)\n" % (k, tot[k], ch))
    f.write("honest joins: %d/%d\n" % (sum(1 for r in rows if r["honest_join"]), len(rows)))
    f.write("diag: %s\n" % dict(diag))
    f.write("lines: %s\n" % L)
print(open("/tmp/proof_summary.txt").read())
