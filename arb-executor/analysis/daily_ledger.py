#!/usr/bin/env python3
"""DAILY LEDGER [C-BOT-ONLY-BASIS 2026-07-09] -- the canonical bot-only
day-P&L renderer (operator ruling, RULING_BOT_ONLY_BASIS.md):

  "just pay attention to bot only. the money that is traded on the bot is
   our basis.. every day at midnight its reset. thats how we gage true
   pnl without confusion."

- Basis = BOT-traded money only; the day anchors at 12:00 am ET (the reset).
- Manual/foreign positions (no-cell-config class: reconcile_orphan_no_cell /
  foreign_position audit flags) are a NAMED side section, never blended.
- Settlement vocabulary inherits (ruling 07-09): cashed-via-exit and
  rode-to-settlement are separate columns, always.
- Category law: per-cat rows, no cross-cat aggregate without decomposition.
- Dollar caveat: jsonl pnl_cents is the bot's own fee-blind convention
  (P0 #5); cents-exact account reconciliation awaits the -1a000 derivation.
  This ledger is the bot-only FRAME; the anchored account delta is the
  cross-check, never the answer.

Usage: python3 analysis/daily_ledger.py [--date YYYYMMDD]
"""
import json, sys
from collections import defaultdict
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ET = timezone(timedelta(hours=-4))
CAT = {"KXATPMATCH": "ATP_MAIN", "KXWTAMATCH": "WTA_MAIN",
       "KXATPCHALLENGERMATCH": "ATP_CHALL", "KXWTACHALLENGERMATCH": "WTA_CHALL",
       "KXITFMATCH": "ITF_M", "KXITFWMATCH": "ITF_W"}


def cat_of(tk):
    for k, v in CAT.items():
        if tk.startswith(k):
            return v
    return None  # None = FOREIGN (not a series the bot routes)


def main():
    now = datetime.now(ET)
    ymd = now.strftime("%Y%m%d")
    for i, a in enumerate(sys.argv):
        if a == "--date" and i + 1 < len(sys.argv):
            ymd = sys.argv[i + 1]
    d = datetime.strptime(ymd, "%Y%m%d")
    day0 = datetime(d.year, d.month, d.day, tzinfo=ET).timestamp()  # 12:00 am ET: THE RESET
    day1 = day0 + 24 * 3600

    files = sorted((ROOT / "logs").glob("live_v3_*.jsonl"),
                   key=lambda p: p.stat().st_mtime)[-3:]
    per = defaultdict(lambda: {"entries": 0, "entry_sh": 0.0,
                               "exit_n": 0, "exit_pnl": 0.0,
                               "rode_n": 0, "rode_pnl": 0.0})
    # [C-EARLY-UNLOCK 07-09] the early cohort renders separately so the
    # entry-table refit grades early entries against the standard window
    eu = defaultdict(lambda: {"placed": 0, "filled": 0, "vols": []})
    # [C-TAPE-SEED 07-09] bids anchored on rest_seeded vs ws_live graded as
    # separate cohorts
    tb = defaultdict(lambda: defaultdict(lambda: {"placed": 0, "filled": 0}))
    foreign = {}
    KEEP = ('"entry_filled"', '"exit_filled"', '"scalp_filled"', '"settled"',
            '"reconcile_orphan_no_cell"', '"foreign_position"',
            '"post_boot_audit"', '"early_unlock"', '"tape_basis"')
    for p in files:
        for line in open(p, encoding="utf-8", errors="replace"):
            if not any(k in line for k in KEEP):
                continue
            try:
                row = json.loads(line)
            except ValueError:
                continue
            ts = row.get("ts_epoch", 0)
            if not (day0 <= ts < day1):
                continue
            ev, det = row.get("event", ""), row.get("details") or {}
            tk = row.get("ticker") or det.get("ticker") or det.get("tk") or ""
            if ev == "post_boot_audit":
                for fl in det.get("flags", []):
                    if fl.get("flag") == "foreign_position":
                        foreign[fl.get("tk", "?")] = "held (audit flag)"
                continue
            if ev == "reconcile_orphan_no_cell":
                if cat_of(tk) is None and tk:
                    foreign[tk] = "no cell config (reconciler)"
                continue
            c = cat_of(tk)
            if c is None:
                if tk:
                    foreign.setdefault(tk, "fill event outside bot series")
                continue  # BOT-ONLY BASIS: never blended
            r = per[c]
            pnl = det.get("pnl_cents")
            if det.get("early_unlock"):
                if ev == "order_placed" and det.get("action") == "buy":
                    eu[c]["placed"] += 1
                    if det.get("unlock_vol") is not None:
                        eu[c]["vols"].append(float(det["unlock_vol"]))
                elif ev == "entry_filled":
                    eu[c]["filled"] += 1
            if det.get("tape_basis"):
                if ev == "order_placed" and det.get("action") == "buy":
                    tb[c][det["tape_basis"]]["placed"] += 1
                elif ev == "entry_filled":
                    tb[c][det["tape_basis"]]["filled"] += 1
            if ev == "entry_filled":
                r["entries"] += 1
                r["entry_sh"] += float(det.get("new_fills") or det.get("qty") or 0)
            elif ev in ("exit_filled", "scalp_filled"):
                r["exit_n"] += 1
                r["exit_pnl"] += float(pnl or 0)
            elif ev == "settled":
                r["rode_n"] += 1
                r["rode_pnl"] += float(pnl or 0)

    day_lbl = datetime.fromtimestamp(day0, ET).strftime("%Y-%m-%d")
    out = ["# DAILY LEDGER (BOT-ONLY BASIS) — %s, anchored 12:00 AM ET" % day_lbl,
           "", "Basis = bot-traded money only (RULING_BOT_ONLY_BASIS). "
           "jsonl fee-blind convention; account reconciliation = cross-check "
           "(−1a000).", "",
           "| cat | entries (shares) | cashed-via-exit n / ¢ | rode-to-settlement n / ¢ | day ¢ |",
           "|---|---|---|---|---|"]
    tot = [0.0, 0.0]
    for c in sorted(per):
        r = per[c]
        tot[0] += r["exit_pnl"]; tot[1] += r["rode_pnl"]
        out.append("| %s | %d (%.0f) | %d / %+.0f | %d / %+.0f | %+.0f |" % (
            c, r["entries"], r["entry_sh"], r["exit_n"], r["exit_pnl"],
            r["rode_n"], r["rode_pnl"], r["exit_pnl"] + r["rode_pnl"]))
    out.append("| **TOTAL (decomposed above)** |  | %+.0f | %+.0f | **%+.0f** |"
               % (tot[0], tot[1], tot[0] + tot[1]))
    if eu:
        out += ["", "## EARLY-UNLOCK COHORT (C-EARLY-UNLOCK — graded separately, never blended)",
                "", "| cat | buys placed under unlock | fills | med vol@placement |",
                "|---|---|---|---|"]
        for c in sorted(eu):
            vs = sorted(eu[c]["vols"])
            out.append("| %s | %d | %d | %s |" % (
                c, eu[c]["placed"], eu[c]["filled"],
                ("%.0f" % vs[len(vs) // 2]) if vs else "--"))
    if tb:
        out += ["", "## TAPE-BASIS COHORTS (C-TAPE-SEED — anchor memory source, graded separately)",
                "", "| cat | basis | buys placed | fills |", "|---|---|---|---|"]
        for c in sorted(tb):
            for b in sorted(tb[c]):
                out.append("| %s | %s | %d | %d |" % (
                    c, b, tb[c][b]["placed"], tb[c][b]["filled"]))
    if foreign:
        out += ["", "## MANUAL / FOREIGN (named, NEVER blended — the operator's book)",
                ""] + ["- `%s` — %s" % (k, v) for k, v in sorted(foreign.items())]
    print("\n".join(out))


if __name__ == "__main__":
    main()
