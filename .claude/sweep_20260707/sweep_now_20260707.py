#!/usr/bin/env python3
"""EMERGENCY BOOK SWEEP (2026-07-07 evening). Exchange decides.
Paginated positions+orders NOW; per leg held vs resting exits vs open buys.
FORCED THIS PASS: naked legs -> post the gap at the standing band (band =
last v4_exit_posted for the leg today, else existing resting-sell px; GTC,
post_only=False so ITM bands cannot 400); buy stacks / over-lot buys ->
collapse to one lawful bid (keep best-px fitting under lot-held).
Prints BEFORE/AFTER table. Idempotent: recomputes live gaps before acting."""
import base64, json, sys, time, uuid
from collections import defaultdict
from pathlib import Path
import requests
sys.path.insert(0, "/root")
from forensic_pull_20260707 import load_creds, get, paged

BASE = "https://api.elections.kalshi.com"
LOT = 5.0
LOG = "/root/Omi-Workspace/arb-executor/logs/live_v3_20260707.jsonl"


def hdr(ak, pk, method, path):
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.asymmetric import padding
    ts = str(int(time.time() * 1000))
    msg = ("%s%s%s" % (ts, method, path.split("?")[0])).encode()
    sig = pk.sign(msg, padding.PSS(mgf=padding.MGF1(hashes.SHA256()),
                  salt_length=padding.PSS.DIGEST_LENGTH), hashes.SHA256())
    return {"KALSHI-ACCESS-KEY": ak, "KALSHI-ACCESS-SIGNATURE": base64.b64encode(sig).decode(),
            "KALSHI-ACCESS-TIMESTAMP": ts, "Content-Type": "application/json"}


def post_order(ak, pk, tk, side, px, cnt, post_only=False):
    path = "/trade-api/v2/portfolio/events/orders"
    payload = {"ticker": tk, "side": side, "count": cnt,
               "price": "%.2f" % (px / 100.0), "time_in_force": "good_till_canceled",
               "self_trade_prevention_type": "taker_at_cross", "post_only": post_only,
               "client_order_id": str(uuid.uuid4())}
    r = requests.post(BASE + path, headers=hdr(ak, pk, "POST", path), json=payload, timeout=30)
    return r.status_code, r.text[:160]


def cancel(ak, pk, oid):
    path = "/trade-api/v2/portfolio/events/orders/%s" % oid
    r = requests.delete(BASE + path, headers=hdr(ak, pk, "DELETE", path), timeout=30)
    return r.status_code


def snapshot(ak, pk):
    held = {p["ticker"]: float(p["position_fp"]) for p in paged(
        ak, pk, "/trade-api/v2/portfolio/positions?count_filter=position"
                "&settlement_status=unsettled&limit=200", "market_positions")
        if float(p.get("position_fp") or 0) > 0}
    buys, sells = defaultdict(list), defaultdict(list)
    for o in paged(ak, pk, "/trade-api/v2/portfolio/orders?status=resting&limit=200", "orders"):
        rec = {"oid": o["order_id"], "px": round(float(o["yes_price_dollars"]) * 100),
               "qty": float(o["remaining_count_fp"])}
        (buys if o["action"] == "buy" else sells)[o["ticker"]].append(rec)
    return held, buys, sells


def main():
    ak, pk = load_creds()
    # band map from today's jsonl (last v4_exit_posted per leg)
    band = {}
    hold_rule = set()
    for line in open(LOG, encoding="utf-8", errors="replace"):
        if '"v4_exit_posted"' in line or '"hold_to_settle"' in line or '"reconcile_exit_posted"' in line or '"reconcile_exit_topup"' in line:
            try:
                e = json.loads(line)
            except Exception:
                continue
            tk = e.get("ticker", "")
            d = e.get("details", {})
            if e["event"] == "hold_to_settle":
                hold_rule.add(tk)
            elif d.get("exit_price"):
                band[tk] = int(d["exit_price"])
                hold_rule.discard(tk)
    held, buys, sells = snapshot(ak, pk)
    print("=== BEFORE (exchange truth %s UTC) ===" % time.strftime("%H:%M:%S", time.gmtime()))
    print("| leg | held | exit qty (px) | buy orders (qty@px) | class |")
    print("|---|---|---|---|---|")
    naked, stacks = [], []
    for tk in sorted(set(list(held) + list(buys))):
        h = held.get(tk, 0.0)
        sq = sum(r["qty"] for r in sells.get(tk, []))
        bq = sum(r["qty"] for r in buys.get(tk, []))
        nb = len(buys.get(tk, []))
        cls = []
        if h >= 1.0 and (h - sq) >= 1.0 and tk not in hold_rule:
            cls.append("NAKED %g" % (h - sq)); naked.append((tk, h, sq))
        if nb > 1 or (bq > 0 and h + bq > LOT + 0.01):
            cls.append("STACK/OVERLOT"); stacks.append(tk)
        if cls:
            print("| %s | %g | %g (%s) | %d (%s) | %s |" % (
                tk, h, sq, ",".join(str(r["px"]) for r in sells.get(tk, [])) or "-",
                nb, ",".join("%g@%g" % (r["qty"], r["px"]) for r in buys.get(tk, [])) or "-",
                "+".join(cls)))
    print("naked legs: %d | stacked/over-lot legs: %d" % (len(naked), len(stacks)))
    print()
    print("=== ACTIONS ===")
    for tk, h, sq in naked:
        gap = h - sq
        px = band.get(tk) or (sells.get(tk) or [{}])[0].get("px")
        if not px:
            print("SKIP-NO-BAND %s gap=%g (no exit ever posted today, not hold-rule) -> NAMED for audit class" % (tk, gap))
            continue
        cnt = ("%d" % int(gap)) if abs(gap - round(gap)) < 1e-9 else ("%.2f" % gap)
        code, body = post_order(ak, pk, tk, "ask", int(px), cnt, post_only=False)
        print("EXIT-POST %s %s@%d -> HTTP %s %s" % (tk, cnt, px, code, body[:90]))
        time.sleep(0.15)
    for tk in stacks:
        h = held.get(tk, 0.0)
        lst = sorted(buys.get(tk, []), key=lambda r: -r["px"])
        keep, acc, kill = [], h, []
        for r in lst:
            if not keep and acc + r["qty"] <= LOT + 0.01:
                keep.append(r); acc += r["qty"]
            else:
                kill.append(r)
        for r in kill:
            code = cancel(ak, pk, r["oid"])
            print("CANCEL-STACK %s %g@%g oid=%s -> HTTP %s (held=%g kept=%s)" % (
                tk, r["qty"], r["px"], r["oid"][:12], code,
                h, ",".join("%g@%g" % (k["qty"], k["px"]) for k in keep) or "-"))
            time.sleep(0.15)
    time.sleep(2)
    held2, buys2, sells2 = snapshot(ak, pk)
    print()
    print("=== AFTER ===")
    print("| leg | held | exit qty | buys | naked | stack |")
    print("|---|---|---|---|---|---|")
    n2 = s2 = 0
    for tk in sorted(set(list(held2) + list(buys2))):
        h = held2.get(tk, 0.0)
        sq = sum(r["qty"] for r in sells2.get(tk, []))
        bq = sum(r["qty"] for r in buys2.get(tk, []))
        nb = len(buys2.get(tk, []))
        nk = h >= 1.0 and (h - sq) >= 1.0 and tk not in hold_rule
        stk = nb > 1 or (bq > 0 and h + bq > LOT + 0.01)
        if nk: n2 += 1
        if stk: s2 += 1
        if nk or stk:
            print("| %s | %g | %g | %d/%g | %s | %s |" % (tk, h, sq, nb, bq, nk, stk))
    print("AFTER: naked=%d stacked=%d" % (n2, s2))


if __name__ == "__main__":
    main()
