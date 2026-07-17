#!/usr/bin/env python3
"""P0v3 (6) — CENSUS OF THE 18 (FORENSIC_w2_fill.md, 2026-07-17 sheet).

Splits the 18 w2_fill_violation events into:
  PHANTOM — the gun fire that labeled the window W2 happened BEFORE the
            schedule floor (min of legacy/honest clocks at fire time, from the
            gun_fired line's own tts stamps). Under P0v3 (1) the fire is VOID;
            the fill's window is W1 (relabeled).
  TRUE    — fill landed at/after the schedule floor: a true post-bell fill,
            graded F on the day sheet.

Per PHANTOM event: was the rise print-backed (fire-detail evidence verbatim:
self_fill condition / fallback_bell rate / percat prints), and the price path
after the fire (aim_shadow tape_last/book series) — the opportunity read.
Per TRUE event: basis, exit state, dollars.
Plus: TAUBEJ / KREZHE one-sided-pair answer from the box, and the 3b clamp
census (premarket_walk_capped_honest binds + print-backed share + churn cost).

Read-only. Run on the VPS from arb-executor/.
"""
import json, glob, os, sys
from collections import defaultdict

LOGS = sorted(glob.glob("logs/live_v3_2026071[5-7].jsonl"))
OUT = sys.argv[1] if len(sys.argv) > 1 else "/tmp/CENSUS_OF_18.md"

# the 18, verbatim from FORENSIC_w2_fill.md (written 11:50:31 AM ET 07-17)
SHEET = [
    ("03:28:54", "KXATPCHALLENGERMATCH-26JUL17GALCOP-COP", 56, 1),
    ("06:15:47", "KXWTACHALLENGERMATCH-26JUL17BASCAR-BAS", 64, 5),
    ("06:23:06", "KXITFMATCH-26JUL17KOIFIT-FIT", 50, 5),
    ("06:43:52", "KXATPCHALLENGERMATCH-26JUL17NIJDEN-NIJ", 18, 5),
    ("06:44:03", "KXATPCHALLENGERMATCH-26JUL17NIJDEN-DEN", 79, 5),
    ("08:40:02", "KXATPMATCH-26JUL17HALSHE-HAL", 61, 5),
    ("09:07:37", "KXWTACHALLENGERMATCH-26JUL17ERJFEI-ERJ", 65, 5),
    ("09:12:07", "KXATPCHALLENGERMATCH-26JUL17KUMBOO-KUM", 54, 5),
    ("09:13:39", "KXATPCHALLENGERMATCH-26JUL17KUMBOO-BOO", 41, 5),
    ("09:39:51", "KXWTACHALLENGERMATCH-26JUL17VALFAL-VAL", 57, 5),
    ("09:58:47", "KXWTACHALLENGERMATCH-26JUL17VALFAL-FAL", 40, 5),
    ("10:08:09", "KXWTACHALLENGERMATCH-26JUL17VANTAN-VAN", 61, 5),
    ("10:08:11", "KXWTACHALLENGERMATCH-26JUL17VANTAN-TAN", 35, 5),
    ("10:32:19", "KXATPCHALLENGERMATCH-26JUL17NAPVIL-VIL", 35, 5),
    ("11:35:59", "KXWTACHALLENGERMATCH-26JUL17YANTRE-YAN", 59, 5),
    ("11:37:16", "KXWTACHALLENGERMATCH-26JUL17YANTRE-TRE", 37, 5),
    ("11:37:30", "KXATPMATCH-26JUL17BURMER-MER", 62, 5),
    ("11:42:09", "KXWTACHALLENGERMATCH-26JUL17BRARIE-BRA", 40, 5),
]
EVENTS = {tk.rsplit("-", 1)[0] for _, tk, _, _ in SHEET}
PAIR_Q = ["KXWTAMATCH-26JUL17TAUBEJ", "KXWTAMATCH-26JUL17KREZHE"]

# ---- one pass over the logs, bucketed by event/ticker -------------------
gun_fired = {}                     # et -> list of gun_fired lines
viol = defaultdict(list)           # tk -> w2_fill_violation lines
fills = defaultdict(list)          # tk -> entry_filled lines
exits = defaultdict(list)          # tk -> v4_exit_posted / exit_filled
settles = defaultdict(list)        # tk -> settlement lines
tape = defaultdict(list)           # tk -> (ts, tape_last, book_bid, book_ask)
binds = defaultdict(list)          # tk -> premarket_walk_capped(_honest) lines
reaims = defaultdict(int)          # tk -> window_truth_reaim count
reposts = defaultdict(int)         # tk -> v4_move_repost count
pairlines = defaultdict(list)      # et -> every line naming the event (PAIR_Q only)
bells = defaultdict(list)          # et -> self_fill_bell / bell detail lines

for path in LOGS:
    with open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            if '"event"' not in line:
                continue
            try:
                j = json.loads(line)
            except ValueError:
                continue
            ev = j.get("event"); tk = j.get("ticker") or ""
            d = j.get("details") or {}
            et = d.get("event") or (tk.rsplit("-", 1)[0] if "-" in tk else "")
            if ev == "gun_fired" and et in EVENTS | set(PAIR_Q):
                gun_fired.setdefault(et, []).append(j)
            elif ev == "w2_fill_violation":
                viol[tk].append(j)
            elif ev == "entry_filled":
                fills[tk].append(j)
            elif ev in ("v4_exit_posted", "exit_filled"):
                exits[tk].append(j)
            elif ev in ("settlement", "ws_settled", "position_settled",
                        "settlement_processed"):
                settles[tk].append(j)
            elif ev == "aim_shadow" and (et in EVENTS or et in PAIR_Q):
                tape[tk].append((j.get("ts_epoch"), d.get("tape_last"),
                                 d.get("book_bid"), d.get("book_ask")))
            elif ev in ("premarket_walk_capped_honest", "premarket_walk_capped"):
                binds[tk].append(j)
            elif ev == "window_truth_reaim":
                reaims[tk] += 1
            elif ev == "v4_move_repost":
                reposts[tk] += 1
            elif ev == "self_fill_bell" and et in EVENTS | set(PAIR_Q):
                bells[et].append(j)
            if et in PAIR_Q and ev in (
                    "v4_place", "order_placed", "entry_filled", "entry_dossier",
                    "pair_seesaw_refused", "pair_seesaw_scoreboard",
                    "below_discovery_floor_refused", "no_path_page_refused",
                    "pair_incomplete_violation", "gun_buy_refused",
                    "conception_horizon_defer", "aim_unresolved_refused",
                    "skip_live_match", "buy_blocked_position_full",
                    "repost_place_failed", "cell_not_eligible"):
                pairlines[et].append(j)

def fire_for(et, before_ts):
    """the gun_fired line governing a fill at before_ts (last fire <= fill)."""
    cands = [g for g in gun_fired.get(et, [])
             if g.get("ts_epoch", 0) <= before_ts + 1]
    return cands[-1] if cands else (gun_fired.get(et) or [None])[-1]

def sched_floor(g):
    """schedule floor at fire time from the fire line's own tts stamps
    (min of legacy/honest = the P0v3 clamp's floor)."""
    if not g:
        return None
    d = g.get("details") or {}
    fts = g.get("ts_epoch")
    tts = [d.get("tts_legacy_min"), d.get("tts_honest_min")]
    tts = [t for t in tts if t is not None]
    if not tts or fts is None:
        return None
    return fts + min(tts) * 60.0

def money(tk):
    """basis / exit state / realized for a leg, from the log's own lines."""
    f = fills.get(tk) or []
    basis = qty = 0
    for j in f:
        d = j.get("details") or {}
        q = float(d.get("new_fills") or d.get("qty") or 0)
        basis += (d.get("fill_price") or 0) * q
        qty += q
    exl = [j for j in exits.get(tk, []) if j.get("event") == "exit_filled"]
    exp_ = [j for j in exits.get(tk, []) if j.get("event") == "v4_exit_posted"]
    stl = settles.get(tk) or []
    state, real = "OPEN", None
    if exl:
        d = exl[-1].get("details") or {}
        px = d.get("fill_price") or d.get("exit_price") or 0
        q = float(d.get("qty") or d.get("filled") or qty or 0)
        state, real = "EXITED @%s" % px, px * q - basis
    elif stl:
        d = stl[-1].get("details") or {}
        sv = d.get("settle_val_cents", d.get("value"))
        if sv is not None:
            state, real = "SETTLED @%s" % sv, sv * qty - basis
        else:
            state = "SETTLED (value unparsed)"
    elif exp_:
        d = exp_[-1].get("details") or {}
        state = "OPEN, exit resting @%s" % d.get("exit_price")
    return qty, basis, state, real

def path_after(tk, t0, t1):
    """(lo,hi,last) of tape_last between t0..t1 from the aim_shadow series."""
    pts = [p for ts, p, _, _ in tape.get(tk, [])
           if ts and p and t0 <= ts <= (t1 or ts)]
    if not pts:
        return None
    return min(pts), max(pts), pts[-1]

L = []
L.append("# CENSUS OF THE 18 — P0v3 (6), 2026-07-17")
L.append("")
L.append("Method: for each w2_fill_violation on the 11:50 AM sheet, the governing")
L.append("gun_fired line's OWN tts stamps give the schedule floor at fire time")
L.append("(min of legacy/honest — the P0v3 (1) clamp floor). Fire before floor =")
L.append("PHANTOM (fire voided under the new law); fill before floor = the fill's")
L.append("window is W1, relabeled. Fill at/after floor = TRUE post-bell fill, F.")
L.append("Dollars from the log's own fill/exit/settlement lines (shares x cents).")
L.append("")

phantom, true_, unk = [], [], []
for hhmm, tk, px, q in SHEET:
    et = tk.rsplit("-", 1)[0]
    vj = None
    for j in viol.get(tk, []):
        if (j.get("ts") or "").find(hhmm) >= 0 or abs(
                (j.get("details") or {}).get("fill_price", -1) - px) == 0:
            vj = j
            break
    fill_ts = (vj or {}).get("ts_epoch")
    g = fire_for(et, fill_ts or 9e12)
    fl = sched_floor(g)
    gd = (g or {}).get("details") or {}
    src = gd.get("source")
    fire_ts = (g or {}).get("ts_epoch")
    row = {"tk": tk, "px": px, "q": q, "src": src, "fire_ts": fire_ts,
           "floor": fl, "fill_ts": fill_ts, "g": gd}
    if fl is None or fill_ts is None:
        unk.append(row)
    elif fire_ts is not None and fire_ts < fl:
        row["cls"] = "PHANTOM_FIRE"
        row["fill_pre_sched"] = fill_ts < fl
        phantom.append(row)
    else:
        true_.append(row)

L.append("## Split: %d phantom-fire / %d true post-bell / %d undeterminable"
         % (len(phantom), len(true_), len(unk)))
L.append("")
L.append("### PHANTOM-BELL EVENTS (fire pre-sched -> VOID under P0v3 (1))")
tot_ph = 0.0
for r in phantom:
    tk = r["tk"]; gd = r["g"]
    pre = "fill ALSO pre-sched -> W1 RELABEL" if r["fill_pre_sched"] \
        else "fill landed post-sched (fire mislabeled the corridor; refire would still grade it W2)"
    cond = gd.get("condition") or ""
    pb = ("NOT print-backed (self-quote walk: %s)" % cond
          if cond == "exceeds_sanctioned_walk" else
          "print-backed (%s)" % (cond or "rate/threshold fire: " + str(
              {k: gd.get(k) for k in ("prints_10m", "rate_per_min",
                                      "prints_30m", "trades_in_window",
                                      "vol_prints_30m") if gd.get(k) is not None})))
    qty, basis, state, real = money(tk)
    pa = path_after(tk, r["fire_ts"] or 0, r["floor"])
    tot_ph += (real or 0) * (qty and 1)
    L.append("- **%s** %sc x%s gun=%s fired %.1f min pre-floor — %s" % (
        tk.split("-")[-2] + "-" + tk.split("-")[-1], r["px"], r["q"], r["src"],
        ((r["floor"] - r["fire_ts"]) / 60.0) if r["fire_ts"] else -1, pre))
    L.append("    - rise: %s" % pb)
    L.append("    - price path fire->floor (tape_last lo/hi/close): %s" % (
        "%s/%s/%s" % pa if pa else "no prints recorded in the shadow series"))
    L.append("    - money: qty %s basis %sc state %s realized %s" % (
        qty, basis, state, ("%+.0fc" % real) if real is not None else "n/a"))
L.append("")
L.append("### TRUE POST-BELL FILLS (graded F on the sheet)")
tot_tr = 0.0
for r in true_:
    tk = r["tk"]
    qty, basis, state, real = money(tk)
    if real is not None:
        tot_tr += real
    L.append("- **%s** %sc x%s gun=%s — basis %sc, %s, realized %s" % (
        tk.split("-")[-2] + "-" + tk.split("-")[-1], r["px"], r["q"], r["src"],
        basis, state, ("%+.0fc" % real) if real is not None else "unsettled"))
for r in unk:
    L.append("- UNDETERMINABLE: %s (no gun_fired tts stamps in range)" % r["tk"])
L.append("")
L.append("### Totals (settled/exited only; open legs marked)")
L.append("- true-F realized: **%+.0fc ($%+.2f)**" % (tot_tr, tot_tr / 100.0))
L.append("")

# ---- TAUBEJ / KREZHE ----------------------------------------------------
L.append("## TAUBEJ / KREZHE — the one-sided pairs, answered from the box")
for et in PAIR_Q:
    legs = sorted({(j.get("ticker") or "").rsplit("-", 1)[-1]
                   for j in pairlines.get(et, []) if j.get("ticker")})
    L.append("### %s" % et)
    per_leg = defaultdict(list)
    for j in pairlines.get(et, []):
        per_leg[(j.get("ticker") or "").rsplit("-", 1)[-1] or "(event)"].append(j)
    for leg, rows in sorted(per_leg.items()):
        kinds = defaultdict(int)
        for j in rows:
            kinds[j.get("event")] += 1
        L.append("- leg %s: %s" % (leg, dict(kinds)))
    both = {tk.rsplit("-", 1)[-1] for tk in reaims if tk.startswith(et)}
    for tk in [t for t in reaims if t.startswith(et)]:
        L.append("- churn on %s: window_truth_reaim %d / reposts %d / clamp binds %d"
                 % (tk.rsplit("-", 1)[-1], reaims[tk], reposts[tk],
                    len(binds.get(tk, []))))
    g = (gun_fired.get(et) or [None])[-1]
    if g:
        gd = g.get("details") or {}
        L.append("- gun: %s at %s (tts_legacy %s / tts_honest %s, condition %s)"
                 % (gd.get("source"), g.get("ts"), gd.get("tts_legacy_min"),
                    gd.get("tts_honest_min"), gd.get("condition")))
    L.append("")

# ---- 3b clamp census ----------------------------------------------------
L.append("## 3b — THE FIXED CLAMP'S HISTORICAL BILL (premarket_walk_capped_honest)")
n_bind = sum(len(v) for v in binds.values())
n_tks = len(binds)
L.append("- binds in the scanned window (Jul 15-17 logs): **%d** across %d legs"
         % (n_bind, n_tks))
pb_bind = 0
churn18 = []
for tk, blist in binds.items():
    # print-backed proxy: a real tape print AT/ABOVE the proposed target within
    # 30 min of the bind, from the aim_shadow tape_last series
    hits = 0
    series = tape.get(tk, [])
    for j in blist:
        ts = j.get("ts_epoch") or 0
        tgt = (j.get("details") or {}).get("proposed_target") or 999
        if any(p and t and abs(t - ts) <= 1800 and p >= tgt
               for t, p, _, _ in series):
            hits += 1
    pb_bind += hits
    if tk.rsplit("-", 1)[0] in EVENTS | set(PAIR_Q):
        churn18.append((tk, len(blist), reaims.get(tk, 0), reposts.get(tk, 0)))
L.append("- binds that clamped a PRINT-BACKED rise (tape printed >= the proposed"
         " target within +/-30 min; aim_shadow tape_last proxy — shadow-series"
         " resolution, an undercount): **%d of %d**" % (pb_bind, n_bind))
L.append("- churn bill on the sheet's own events (each bind row = one"
         " cancel/repost queue-priority loss):")
for tk, nb, nr, np_ in sorted(churn18, key=lambda x: -x[1]):
    L.append("    - %s: %d binds / %d reaims / %d reposts" %
             (tk.split("-")[-2] + "-" + tk.split("-")[-1], nb, nr, np_))
L.append("- the cents: queue priority is not directly priced by the box; the"
         " measurable bill is the W2 conversion — every churned leg above that"
         " appears in the 18 filled AFTER its own churn burned its W1 queue"
         " position, and BURMER's self_fill gun WAS the churn (the joins read"
         " as live evidence). The fitted per-cat sanctioned-walk read replaces"
         " the constant as its own follow-on (P0v3 3b).")

open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n")
print("wrote %s (%d lines)" % (OUT, len(L)))
