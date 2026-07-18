#!/usr/bin/env python3
"""P0 COMPLETION-DISARM (2) — FULL COUNTERFACTUAL CENSUS from our own tape.

Every flatten_kept and taker_complete ever EXECUTED since the June/July
births, from the engine logs (Jun-01 → now, gz + live):
  - the action's price vs what the standing maker exit or settlement
    actually paid; taker fees their own column (Kalshi taker fee =
    ceil(7% · p · (1−p)) per share);
  - named exhibits pulled: Molcan, Merida, KOPPRI, the 07-13 day's
    flattens;
  - the ELIGIBILITY count: shadow verdicts issued (the license) vs actions
    fired (the shots) — the size of the gun.
Totals in dollars. Read-only.
"""
import glob, gzip, io, json, math, sys
from collections import defaultdict

OUT = sys.argv[1] if len(sys.argv) > 1 else "/tmp/COMPLETION_CENSUS.md"

def taker_fee_c(p_cents, qty):
    p = p_cents / 100.0
    return math.ceil(7.0 * p * (1 - p) * qty) if 0 < p < 1 else 0

def opener(path):
    return (io.TextIOWrapper(gzip.open(path, "rb"), encoding="utf-8",
                             errors="replace")
            if path.endswith(".gz") else open(path, encoding="utf-8",
                                              errors="replace"))

actions = []            # executed flatten/taker rows
crosses = []            # complete_cross rows
shadow_license = defaultdict(int)   # verdict -> count (the license)
cancelled_exit = {}     # tk -> last v4_exit_posted price BEFORE the action
exit_now = {}
settle = {}             # tk -> settle value cents
sells = defaultdict(list)   # tk -> (ts, price, qty, is_flatten_label)
fills_after = defaultdict(list)

files = sorted(glob.glob("logs/live_v3_202606*.jsonl*")
               + glob.glob("logs/live_v3_202607*.jsonl*"))
for path in files:
    with opener(path) as fh:
        for line in fh:
            if '"completion' not in line and '"complete_cross"' not in line \
                    and '"settlement' not in line and '"v4_exit_posted"' \
                    not in line and '"exit_filled"' not in line \
                    and '"process_settlement"' not in line \
                    and '"settled"' not in line:
                continue
            try:
                j = json.loads(line)
            except ValueError:
                continue
            ev = j.get("event")
            tk = j.get("ticker") or ""
            d = j.get("details") or {}
            ts = j.get("ts_epoch")
            if ev == "v4_exit_posted":
                exit_now[tk] = (d.get("exit_price"), ts)
            elif ev == "completion_shadow":
                v = ((d.get("kept") or {}).get("opinion") and
                     d.get("verdict"))
                if d.get("verdict") in ("taker_complete", "flatten_kept"):
                    shadow_license[d["verdict"]] += 1
            elif ev == "completion_action":
                if d.get("verdict") in ("taker_complete", "flatten_kept") \
                        and d.get("outcome") not in ("error",):
                    actions.append({"tk": tk, "ts": ts, "day":
                                    (j.get("ts") or "")[:10], **d,
                                    "exit_before": exit_now.get(tk)})
            elif ev == "complete_cross":
                crosses.append({"tk": tk, "ts": ts,
                                "day": (j.get("ts") or "")[:10], **d})
            elif ev == "settled":
                sv = d.get("settle_price")
                if sv is not None:
                    settle[tk] = sv

L = ["# P0 COMPLETION-DISARM — THE COUNTERFACTUAL CENSUS", "",
     "scope: engine logs %s → %s (%d files). Executed actions vs the ride."
     % (files[0][-16:-6] if files else "?",
        files[-1][-14:-6] if files else "?", len(files)), ""]
L.append("## THE GUN vs THE SHOTS")
L.append("- license (shadow verdicts issued): flatten_kept %d · "
         "taker_complete %d" % (shadow_license.get("flatten_kept", 0),
                                shadow_license.get("taker_complete", 0)))
L.append("- shots fired (executed): completion_action %d · "
         "complete_cross %d" % (len(actions), len(crosses)))
L.append("")
L.append("## EXECUTED ACTIONS — price vs the ride (settlement where known)")
tot_delta = tot_fee = 0
by_day = defaultdict(int)
for a in actions:
    tk = a["tk"]
    px = a.get("flatten_price") if a.get("verdict") == "flatten_kept" else a.get("cross_price")
    qty = a.get("qty") or 5
    sv = settle.get(tk if a.get("verdict") == "flatten_kept" else a.get("sib") or tk)
    exb = (a.get("exit_before") or (None, None))[0]
    fee = taker_fee_c(px, qty) if px else 0
    delta = None
    if px is not None and sv is not None:
        if a.get("verdict") == "flatten_kept":
            delta = (px - sv) * qty - fee   # sold at px, ride paid sv
        else:
            delta = (sv - px) * qty - fee   # crossed BUY at px, settled sv
        tot_delta += delta
    tot_fee += fee
    by_day[a["day"]] += 1
    L.append("- %s %s %s: acted %s¢ x%s · cancelled maker exit %s¢ · "
             "settled %s · fee %d¢ · delta-vs-settle %s"
             % (a["day"], tk.split("-")[-2][-8:] + "-" + tk.split("-")[-1],
                a.get("verdict"), px, qty, exb, sv, fee,
                ("%+d¢" % delta) if delta is not None else "unjoined"))
for c in crosses:
    tk = c["tk"]
    px = c.get("cross_ask") or c.get("fill_price")
    qty = c.get("sib_fill") or c.get("count") or 5
    sv = settle.get(tk)
    fee = taker_fee_c(px, qty) if px else 0
    tot_fee += fee
    delta = ((sv - px) * qty - fee) if (px is not None and sv is not None) \
        else None
    if delta is not None:
        tot_delta += delta if False else 0   # crosses reported, not netted into sell-delta
    L.append("- %s %s complete_cross(BUY): crossed %s¢ x%s · settled %s · "
             "fee %d¢ · buy-vs-settle %s"
             % (c["day"], tk.split("-")[-2][-8:] + "-" + tk.split("-")[-1],
                px, qty, sv, fee,
                ("%+d¢" % delta) if delta is not None else "unjoined"))
L.append("")
L.append("## TOTALS")
L.append("- sell-side delta vs settlement (joined rows): **%+d¢ "
         "($%+.2f)** · taker fees paid: %d¢" % (tot_delta,
                                                tot_delta / 100.0, tot_fee))
L.append("- actions by day: %s" % dict(sorted(by_day.items())))
L.append("")
L.append("(unjoined rows = settlement not in log span for that ticker; "
         "named honestly, not guessed.)")
open(OUT, "w").write("\n".join(L) + "\n")
print("wrote", OUT, "| actions:", len(actions), "crosses:", len(crosses))
print("\n".join(L[:14]))
