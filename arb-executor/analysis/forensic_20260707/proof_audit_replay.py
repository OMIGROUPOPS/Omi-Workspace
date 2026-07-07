#!/usr/bin/env python3
"""[C46 OUTCOME PROOF] Lane-1 mechanism replay for C47-ENFORCE (post-boot book
audit, assert-and-halt). Replays the audit's exact assertions against the prior
slate's banked exchange snapshots:

  SNAPSHOT 1 — 09:38 ET 07-07 (pre-containment book: forensic_20260707.json
  resting orders + forensic_analysis2_20260707.json positions/coverage): the
  book every overnight boot (01:07/02:07/02:34) woke up into. The audit's
  verdict on it is deterministic; FAIL => conceptions would have HALTED within
  5 min of the 01:07 boot, hours before containment.

  PREVENTED (upper estimate, stated): class-(a) surplus buy fills during the
  02:34-boot window (orders conceived by blind post-boot reconciles) from the
  bleed attribution -- fills that cannot exist under an armed halt.

Deterministic, no settlement claims (Lane 2 flagged luck-polluted).
Usage (VPS): python3 proof_audit_replay.py"""
import json

LOT = 5.0


def main():
    fj = json.load(open("/root/forensic_20260707.json"))
    aj = json.load(open("/root/forensic_analysis2_20260707.json"))
    bl = json.load(open("/root/bleed_attribution_20260707.json"))

    buys, sells = {}, {}
    for o in fj["resting_orders"]:
        d = buys if o["action"] == "buy" else sells
        d.setdefault(o["ticker"], []).append(float(o["remaining_count_fp"]))
    held = {c["ticker"]: c["held"] for c in aj["coverage"]}
    resting_sell = {c["ticker"]: c["resting_sell"] for c in aj["coverage"]}

    stacks, mismatch, no_exit, conc_owned = [], [], [], []
    for tk in sorted(set(list(held) + list(buys))):
        h = held.get(tk, 0.0)
        b = sum(buys.get(tk, []))
        s = resting_sell.get(tk, sum(sells.get(tk, [])))
        if len(buys.get(tk, [])) > 1:
            stacks.append((tk, len(buys[tk]), b))
        if b > 0 and h + b > LOT + 0.01:
            conc_owned.append((tk, h, b))
        if h >= 1.0:
            if s <= 0.001:
                no_exit.append((tk, h))
            elif abs(h - s) >= 1.0:
                mismatch.append((tk, h, s))
    n_fail = len(stacks) + len(mismatch) + len(no_exit) + len(conc_owned)
    verdict = "FAIL" if n_fail else "PASS"

    print("## SNAPSHOT 1 — 09:38 ET pre-containment book, audit replay")
    print()
    print("| assertion | failures | exhibits |")
    print("|---|---|---|")
    print("| buy_stack | %d | %s |" % (len(stacks), ", ".join(t[-18:] for t, *_ in stacks[:6])))
    print("| exit_qty_mismatch | %d | %s |" % (len(mismatch), ", ".join(t[-18:] for t, *_ in mismatch[:6])))
    print("| no_exit (held>=1, no sell resting; hold-rule not distinguished in the banked snapshot — stated) | %d | %s |" % (len(no_exit), ", ".join(t[-18:] for t, *_ in no_exit[:6])))
    print("| conception_on_owned (held+buys>lot) | %d | %s |" % (len(conc_owned), ", ".join(t[-18:] for t, *_ in conc_owned[:6])))
    print()
    print("**VERDICT: %s (%d failures) — every overnight boot woke into this book; the audit halts conceptions within 5 min of the 01:07 boot.**" % (verdict, n_fail))
    print()

    # prevented upper estimate: class-(a) surplus fills in the 02:34-boot window
    prevented_sh = prevented_usd = 0.0
    n_tk = 0
    for tk, d in (aj.get("dup") or {}).items():
        rows = [r for r in d.get("buy_fills_48h", [])
                if r.get("window") == "boot@2026-07-07T06:34:20Z"]
        if not rows:
            continue
        # surplus = fills beyond the first admitted lot inside the window (upper est.)
        tot = sum(r["qty"] for r in rows)
        sur = max(0.0, tot - LOT) if d.get("held", 0) or tot > LOT else 0.0
        if sur > 0:
            n_tk += 1
            prevented_sh += sur
            prevented_usd += sur * (sum(r["px"] * r["qty"] for r in rows) / max(tot, 1e-9)) / 100
    print("## PREVENTED (upper estimate, stated): 02:34-boot-window surplus conceptions")
    print()
    print("**%d tickers, %.1f surplus shares, $%.2f committed** could not have filled under an armed halt (fills-in-window used as the placement proxy; VANBOO's 159fb665 placed 02:34:19 is the exhibit)."
          % (n_tk, prevented_sh, prevented_usd))
    print()
    print("Lane 2 (secondary, LUCK-POLLUTED small-n): the 07-07 class-(a) realized on those conceptions was part of the -$37.76 day; no settlement-based claim is the verdict — Lane 1's deterministic FAIL is.")


if __name__ == "__main__":
    main()
