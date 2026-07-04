#!/usr/bin/env python3
"""Deploy-gate smoke replay: NO DEPLOY WITHOUT THIS PASSING (law of 2026-07-04).

Instantiates the FULL LiveV3 class exactly as it will run tonight (the real
deploy config, all currently-armed flags, paper_mode forced ON so zero real
orders can exist) and drives it against a recorded slate hour rebuilt from the
bot's own premarket_ticks book recordings, fed through the REAL WS ingest path
(_ingest_ws_frame -> apply_snapshot/apply_trade -> on_bbo_update/routing_tick).

FAIL conditions (any -> exit 1, deploy refused):
  * any uncaught exception out of routing_tick / on_bbo_update / check_fills /
    validate_resting_buys / reconcile
  * any logged event in ERROR_EVENTS (the caught-and-logged crash class that
    hid the 2026-07-04 _sibling_ticker TypeError for 8 hours)
  * zero placements, or zero DOG-leg (sub-50) placement evaluations -- a smoke
    that never walks the path that broke last time proves nothing

MUST run inside an ISOLATED copy of arb-executor (deploy_gate.sh does the
rsync): the class writes tick CSVs, resting-state and log files relative to
its own directory, and must never touch the live bot's state.

Usage (from inside the smoke env, next to live_v4.py):
  python3 deploy/smoke_replay.py --ticks-dir /path/to/recorded/premarket_ticks \
      [--minutes 60] [--max-tickers 200]
"""
import argparse
import asyncio
import csv
import importlib.util
import json
import os
import sys
import time
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent   # arb-executor root (smoke copy)
ERROR_EVENTS = {"error", "on_bbo_update_error", "order_error", "paper_error",
                "ws_error", "schedule_error"}
# events that count as coverage of the paths the gate exists to protect
COVERAGE_KEYS = ["v4_place", "order_placed", "staircase_hold_place",
                 "match_live_detected", "match_live_grace_armed",
                 "match_live_resting_cancel", "v4_exit_posted",
                 "premarket_walk_capped", "leg2_reshuffle_reaim",
                 "window_open_set"]


def build_smoke_config():
    live_cfg = HERE / "config" / "deploy_v5_live.json"
    cfg = json.loads(live_cfg.read_text())
    cfg["paper_mode"] = True          # the ONLY change vs tonight's real config
    out = HERE / "config" / "smoke_generated.json"
    out.write_text(json.dumps(cfg, indent=2))
    return "config/smoke_generated.json"


def load_module():
    sys.path.insert(0, str(HERE))   # sibling modules: fv, intelligence, tennis_schedule
    spec = importlib.util.spec_from_file_location("live_v4_smoke", HERE / "live_v4.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["live_v4_smoke"] = mod
    spec.loader.exec_module(mod)
    return mod


def _tail_rows(path, tail_bytes=524288):
    """Header + last `tail_bytes` of a CSV, parsed as dict rows. Bounded I/O so
    the gate stays fast on multi-day 40k-row recordings."""
    with open(path, "rb") as fh:
        header = fh.readline().decode("utf-8", "replace").strip().split(",")
        fh.seek(0, 2)
        size = fh.tell()
        fh.seek(max(len(",".join(header)) + 1, size - tail_bytes))
        blob = fh.read().decode("utf-8", "replace")
    lines = blob.split("\n")[1:] if size > tail_bytes else blob.split("\n")
    out = []
    for ln in lines:
        parts = ln.strip().split(",")
        if len(parts) == len(header):
            out.append(dict(zip(header, parts)))
    return out


def pick_window(ticks_dir, minutes, max_tickers):
    """Replay the MOST RECENT recorded `minutes` across the tick CSVs: only
    files modified inside the window are read (tail-bounded), so the gate is
    fast and always replays a real, current slate hour."""
    ticks_dir = Path(ticks_dir)
    all_files = list(ticks_dir.glob("*.csv"))
    if not all_files:
        sys.exit("SMOKE FAIL: no tick CSVs in %s" % ticks_dir)
    latest = max(f.stat().st_mtime for f in all_files)
    w0 = latest - minutes * 60
    files = [f for f in all_files if f.stat().st_mtime >= w0]
    t0 = datetime.fromtimestamp(w0)
    t1 = datetime.fromtimestamp(latest)
    win = {}
    for f in files:
        rows = []
        for r in _tail_rows(f):
            try:
                ts = datetime.strptime(r["ts_et"], "%Y-%m-%d %I:%M:%S %p")
            except Exception:
                continue
            if t0 <= ts <= t1:
                rows.append(r)
        if rows:
            win[f.stem] = rows
    if not win:
        sys.exit("SMOKE FAIL: no rows inside window %s -> %s" % (t0, t1))
    # keep the most active tickers, but ALWAYS keep both legs of kept events
    by_activity = sorted(win, key=lambda k: -len(win[k]))[:max_tickers]
    keep = set(by_activity)
    for tk in by_activity:
        ev = tk.rsplit("-", 1)[0]
        for other in win:
            if other.rsplit("-", 1)[0] == ev:
                keep.add(other)
    return {k: win[k] for k in keep}, (t0, t1)


def snapshot_frame(tk, row):
    yes, no = [], []
    for i in range(1, 6):
        b, bs = row.get(f"bid_{i}"), row.get(f"bid_{i}_sz")
        a, asz = row.get(f"ask_{i}"), row.get(f"ask_{i}_sz")
        try:
            if b and bs and int(bs) > 0 and 0 < int(b) < 100:
                yes.append([int(b) / 100.0, int(bs)])
        except Exception:
            pass
        try:
            if a and asz and int(asz) > 0 and 0 < int(a) < 100:
                no.append([(100 - int(a)) / 100.0, int(asz)])
        except Exception:
            pass
    return json.dumps({"type": "orderbook_snapshot",
                       "msg": {"market_ticker": tk, "yes": yes, "no": no}})


def trade_frame(tk, price_cents, count=25, side="yes"):
    return json.dumps({"type": "trade", "msg": {"market_ticker": tk,
                       "yes_price": price_cents / 100.0 if price_cents < 100 else price_cents,
                       "count": count, "taker_side": side}})


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ticks-dir", required=True)
    ap.add_argument("--minutes", type=int, default=60)
    ap.add_argument("--max-tickers", type=int, default=200)
    args = ap.parse_args()

    os.environ["LIVE_V4_CONFIG"] = build_smoke_config()
    mod = load_module()
    # redirect every path the class writes, INSIDE the smoke copy
    mod.LOG_DIR = HERE / "smoke_out" / "logs"
    mod.TICK_DIR = HERE / "smoke_out" / "ticks"
    mod.TRADE_DIR = HERE / "smoke_out" / "trades"
    for d in (mod.LOG_DIR, mod.TICK_DIR, mod.TRADE_DIR):
        d.mkdir(parents=True, exist_ok=True)

    bot = mod.LiveV3()
    if mod._PAPER_API is None:
        sys.exit("SMOKE FAIL: paper_mode did not engage -- refusing (would trade real money)")
    import aiohttp
    bot.session = aiohttp.ClientSession()   # pass-through READS only; orders/cancels are paper-intercepted

    counts = Counter()
    errors = []
    real_log = bot._log
    def spy_log(event, details=None, ticker=""):
        counts[event] += 1
        if event in ERROR_EVENTS:
            errors.append((event, ticker, str(details)[:400]))
        return real_log(event, details, ticker)
    bot._log = spy_log

    win, (t0, t1) = pick_window(args.ticks_dir, args.minutes, args.max_tickers)
    events = sorted({tk.rsplit("-", 1)[0] for tk in win})
    print(f"SMOKE: window {t0} -> {t1} | tickers={len(win)} events={len(events)}")

    # seed schedule state: stagger starts so the replay exercises far-window,
    # placement-window, near-start and already-live branches
    now = time.time()
    offsets = [235 * 60, 120 * 60, 45 * 60, -10 * 60]
    for i, ev in enumerate(events):
        bot.event_start_time[ev] = now + offsets[i % len(offsets)]
        bot.event_start_source[ev] = "smoke_replay"
        for tk in win:
            if tk.rsplit("-", 1)[0] == ev:
                bot.event_tickers[ev].add(tk)

    # merge rows time-ordered across tickers
    stream = []
    for tk, rows in win.items():
        for r in rows:
            stream.append((r["ts_et"], tk, r))
    stream.sort(key=lambda x: x[0])
    print(f"SMOKE: {len(stream)} recorded book states to replay")

    async def drain_bbo():
        for tk in list(bot._bbo_dirty):
            bot._bbo_dirty.discard(tk)
            await bot.on_bbo_update(tk)

    last_trade_seen = defaultdict(int)
    dog_evals = 0
    for i, (ts, tk, row) in enumerate(stream):
        bot._ingest_ws_frame(snapshot_frame(tk, row))
        try:
            lt = int(float(row.get("last_trade") or 0))
        except Exception:
            lt = 0
        if lt > 0 and lt != last_trade_seen[tk]:
            last_trade_seen[tk] = lt
            bot._ingest_ws_frame(trade_frame(tk, lt, count=5))
        b = bot.books.get(tk)
        if b and 0 < b.best_bid < 50:
            dog_evals += 1
        await drain_bbo()
        if i % 200 == 199:                       # ~ a routing sweep per 200 frames
            await bot.routing_tick()
            await bot.check_fills()
        if i % 700 == 699:
            await bot.validate_resting_buys()
            await bot.reconcile(quiet=True)

    # ---- burst phase: force the latch -> grace -> cancel chain on events with
    # resting paper bids (the exact machinery of grace_kill/latch_override) ----
    resting_evts = sorted({p.event_ticker for p in bot.positions.values()
                           if getattr(p, "phase", "") == "entry_resting"})[:4]
    burst_evts = resting_evts or events[:3]
    print(f"SMOKE: burst phase on {len(burst_evts)} events {burst_evts[:4]}")
    def inject_burst(evts):
        tks_out = []
        for ev in evts:
            tks = sorted(bot.event_tickers.get(ev, ()))
            tks_out += tks
            for j in range(20):                  # >= LIVE_TRADE_BURST within the window
                for tk in tks:
                    b = bot.books.get(tk)
                    px = (b.last_trade_price or b.best_bid or 50) if b else 50
                    bot._ingest_ws_frame(trade_frame(tk, max(1, min(99, px)), count=8))
        return tks_out

    # place burst events PAST their start (tts<=0): skips the TTS floor and the
    # E113 premarket movement gate, exactly like a real in-play match
    for ev in burst_evts:
        bot.event_start_time[ev] = time.time() - 600
    burst_tks = inject_burst(burst_evts)         # burst #1 -> stage-1 arms
    for tk in burst_tks:
        await bot.on_bbo_update(tk)
    # two-stage confirm needs a burst >= CONFIRM_MIN_GAP later; backdate stage-1
    # (still inside the 300s TTL) instead of sleeping 60s in a deploy gate
    for ev in list(getattr(bot, "_live_stage1", {})):
        bot._live_stage1[ev] -= 61.0
    inject_burst(burst_evts)                     # burst #2 -> latch
    # trades do NOT mark tickers bbo-dirty; the latch lives in _v4_manage_resting
    # (on_bbo_update / validate_resting_buys). Drive both real entry points.
    for tk in burst_tks:
        await bot.on_bbo_update(tk)
    await bot.validate_resting_buys()
    await bot.routing_tick()
    # rewind latch stamps so grace is ELAPSED on the next pass (replaying 300s of
    # wall-clock is not viable in a gate; this drives the REAL cancel branch)
    for p in bot.positions.values():
        if getattr(p, "match_live_latch_ts", 0) > 0:
            p.match_live_latch_ts -= 301.0
    for tk in burst_tks:
        await bot.on_bbo_update(tk)
    await bot.validate_resting_buys()
    await bot.routing_tick()
    await drain_bbo()
    await bot.check_fills()

    await bot.session.close()

    # ---- verdict ----
    print("\nSMOKE coverage:", {k: counts.get(k, 0) for k in COVERAGE_KEYS})
    print(f"SMOKE dog-leg (sub-50 best-bid) book states routed: {dog_evals}")
    failed = False
    if errors:
        failed = True
        print(f"SMOKE FAIL: {len(errors)} error-class log events:")
        for e in errors[:10]:
            print("   ", e)
    if counts.get("order_placed", 0) == 0:
        failed = True
        print("SMOKE FAIL: zero paper orders placed -- replay exercised nothing")
    if dog_evals == 0:
        failed = True
        print("SMOKE FAIL: zero dog-leg book states -- the 2026-07-04 crash class was never walked")
    if counts.get("match_live_detected", 0) == 0:
        print("SMOKE WARN: latch never fired in burst phase (grace/cancel chain unexercised)")
    print("SMOKE:", "FAIL -- deploy refused" if failed else "PASS")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
