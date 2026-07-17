#!/usr/bin/env python3
"""C-FUND-TRACKER v2 — THE EQUITY ENGINE + THE TICKER + THE DAY SHEET +
THE FUND SHEET (Part 5b) + STATE FLAGS. One process: a single-writer
recorder thread polls Kalshi (the ONLY source — exchange truth) every
60s into state/fund_equity.db; a token-protected loopback HTTP app reads
ONLY the db (zero reconciliation by construction — this ledger is the
fund's single source of record; every organ cites it; a parallel figure
on any organ is a named defect on that organ).

Run:  python3 tools/fund_tracker.py          (tmux fund_tracker)
View: ssh -N -L 8788:127.0.0.1:8788 root@VPS ; open
      http://127.0.0.1:8788/?token=<token>   (token in state/fund_tracker.token)
Stdlib only. Live bot untouched — this organ only reads."""
import base64
import json
import secrets
import sqlite3
import threading
import time
from datetime import datetime, timedelta
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse, parse_qs
from zoneinfo import ZoneInfo

import requests
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import daysheet_panel as ds  # noqa: E402  [C-DAYSHEET-LIVE] POSITIONS/
# ORDERS/CLOSED panel — sibling module, same dir, stdlib only. See
# daysheet_panel.py + daysheet_template.py docstrings for the render spec
# this supersedes (155a1d6's pair-lens bundle, off the approved mock v4).
from daysheet_template import PAGE_TEMPLATE as DAYSHEET_PAGE  # noqa: E402

ET = ZoneInfo("America/New_York")
ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "state" / "fund_equity.db"
TOKEN_FILE = ROOT / "state" / "fund_tracker.token"
PORT = 8788
POLL_SEC = 60
BASE = "https://api.elections.kalshi.com"
AK = "f3b064d1-a02e-42a4-b2b1-132834694d23"
PK = serialization.load_pem_private_key(
    (ROOT / "kalshi.pem").read_bytes(), password=None,
    backend=default_backend())

OPERATOR_DAY_REF = 40.0    # $/day — the operator's objective reference,
                           # HIS line, never a machine target
OPERATOR_YIELD_REF = 8.0   # % — the operator's standing scaling reference


def sign(ts, m, p):
    sig = PK.sign((ts + m + p).encode(), padding.PSS(
        mgf=padding.MGF1(hashes.SHA256()),
        salt_length=padding.PSS.DIGEST_LENGTH), hashes.SHA256())
    return base64.b64encode(sig).decode()


def api_get(p):
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


def iso_ep(iso):
    """RFC3339 -> epoch; None on absence/garbage (never a fabricated 0)."""
    try:
        return datetime.fromisoformat(
            (iso or "").replace("Z", "+00:00")).timestamp()
    except Exception:
        return None


def day_of(ep):
    return datetime.fromtimestamp(ep, ET).strftime("%Y%m%d")


def init_db():
    DB.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB)
    con.executescript("""
    CREATE TABLE IF NOT EXISTS equity(
      ts REAL PRIMARY KEY, day TEXT, cash_c INTEGER, marked_c INTEGER,
      equity_c INTEGER, n_positions INTEGER);
    CREATE TABLE IF NOT EXISTS fills(
      fill_id TEXT PRIMARY KEY, ts REAL, day TEXT, ticker TEXT,
      action TEXT, side TEXT, count_fp REAL, yes_price_c INTEGER,
      is_taker INTEGER, order_id TEXT, raw TEXT);
    CREATE TABLE IF NOT EXISTS snap_positions(
      ts REAL, ticker TEXT, qty REAL, exposure_c INTEGER, mark_c INTEGER,
      PRIMARY KEY(ts, ticker));
    CREATE TABLE IF NOT EXISTS snap_orders(
      ts REAL, order_id TEXT, ticker TEXT, action TEXT,
      yes_price_c INTEGER, remaining REAL, PRIMARY KEY(ts, order_id));
    CREATE TABLE IF NOT EXISTS flags(
      ts REAL, day TEXT, kind TEXT, ticker TEXT, detail TEXT);
    CREATE TABLE IF NOT EXISTS orders_ledger(
      order_id TEXT PRIMARY KEY, ticker TEXT, action TEXT,
      yes_price_c INTEGER, created_time TEXT, created_ep REAL);
    CREATE INDEX IF NOT EXISTS eq_day ON equity(day);
    CREATE INDEX IF NOT EXISTS fl_day ON fills(day);
    """)
    con.commit()
    return con


def recorder_loop():
    con = init_db()
    last_fill_sweep = 0.0
    while True:
        t0 = time.time()
        try:
            now = time.time()
            day = day_of(now)
            bal = api_get("/trade-api/v2/portfolio/balance")
            cash_c = int(bal.get("balance") or 0)
            # positions + marks (bid-side marks — conservative)
            marked_c = 0
            positions = []
            cur = ""
            while True:
                j = api_get("/trade-api/v2/portfolio/positions?"
                            "count_filter=position&settlement_status="
                            "unsettled&limit=200"
                            + (("&cursor=%s" % cur) if cur else ""))
                rows = (j or {}).get("market_positions", [])
                for p in rows:
                    q = float(p.get("position_fp") or 0)
                    if q == 0:
                        continue
                    m = api_get("/trade-api/v2/markets/%s" % p["ticker"])
                    b = ((m or {}).get("market") or {}).get(
                        "yes_bid_dollars")
                    mk = int(round(float(b) * 100 * q)) if b is not None \
                        else 0
                    marked_c += mk
                    positions.append((now, p["ticker"], q,
                                      int(abs(float(p.get(
                                          "market_exposure_dollars")
                                          or 0) * 100)), mk))
                cur = (j or {}).get("cursor")
                if not cur or not rows:
                    break
            con.execute("INSERT OR REPLACE INTO equity VALUES(?,?,?,?,?,?)",
                        (now, day, cash_c, marked_c, cash_c + marked_c,
                         len(positions)))
            con.execute("DELETE FROM snap_positions WHERE ts < ?",
                        (now - 7200,))
            con.executemany("INSERT OR REPLACE INTO snap_positions "
                            "VALUES(?,?,?,?,?)", positions)
            # resting orders snapshot
            orders = []
            cur = ""
            while True:
                j = api_get("/trade-api/v2/portfolio/orders?status="
                            "resting&limit=200"
                            + (("&cursor=%s" % cur) if cur else ""))
                rows = (j or {}).get("orders", [])
                for o in rows:
                    orders.append((now, o.get("order_id"), o["ticker"],
                                   o.get("action"),
                                   int(round(float(o.get(
                                       "yes_price_dollars") or 0) * 100)),
                                   float(o.get("remaining_count_fp")
                                         or 0)))
                    # [PLACED-ET build, 07-17 — the open-ledger gap
                    # closes] Kalshi's own order created_time banked
                    # PERMANENTLY (snap_orders retains 2h; this ledger
                    # never purges — placed/filled render truthfully)
                    _ct = o.get("created_time")
                    con.execute(
                        "INSERT OR IGNORE INTO orders_ledger "
                        "VALUES(?,?,?,?,?,?)",
                        (o.get("order_id"), o["ticker"], o.get("action"),
                         int(round(float(o.get("yes_price_dollars")
                                         or 0) * 100)), _ct,
                         iso_ep(_ct)))
                cur = (j or {}).get("cursor")
                if not cur or not rows:
                    break
            con.execute("DELETE FROM snap_orders WHERE ts < ?",
                        (now - 7200,))
            con.executemany("INSERT OR REPLACE INTO snap_orders "
                            "VALUES(?,?,?,?,?,?)", orders)
            # fills feed — the operator's own portfolio records
            if now - last_fill_sweep > 120:
                last_fill_sweep = now
                cur = ""
                midnight = datetime.now(ET).replace(
                    hour=0, minute=0, second=0, microsecond=0).timestamp()
                for page in range(10):
                    j = api_get("/trade-api/v2/portfolio/fills?limit=200"
                                + (("&cursor=%s" % cur) if cur else ""))
                    rows = (j or {}).get("fills", [])
                    if not rows:
                        break
                    stop = False
                    for f in rows:
                        # [PLACED-ET build 07-17] documented field
                        # primary, undocumented ts fallback (the filed
                        # recorder fragility's remedy, open ledger 07-16)
                        ep = (iso_ep(f.get("created_time"))
                              or f.get("ts") or 0)
                        if ep < midnight - 86400:
                            stop = True
                        con.execute(
                            "INSERT OR IGNORE INTO fills VALUES"
                            "(?,?,?,?,?,?,?,?,?,?,?)",
                            (f.get("fill_id") or f.get("trade_id"), ep,
                             day_of(ep), f["ticker"], f.get("action"),
                             f.get("side"),
                             float(f.get("count_fp") or 0),
                             int(round(float(f.get("yes_price_dollars")
                                             or 0) * 100)),
                             1 if f.get("is_taker") else 0,
                             f.get("order_id"), json.dumps(f)[:800]))
                    cur = (j or {}).get("cursor")
                    if stop or not cur:
                        break
            # STATE FLAGS — wrong-by-state, no event needed
            con.execute("DELETE FROM flags WHERE ts < ?", (now - 86400,))
            flags = state_flags(con, now, positions, orders)
            for k, tk, det in flags:
                con.execute("INSERT INTO flags VALUES(?,?,?,?,?)",
                            (now, day, k, tk, det))
            con.commit()
        except Exception as e:
            try:
                con.execute("INSERT INTO flags VALUES(?,?,?,?,?)",
                            (time.time(), day_of(time.time()),
                             "recorder_error", "", str(e)[:200]))
                con.commit()
            except Exception:
                pass
        time.sleep(max(5, POLL_SEC - (time.time() - t0)))


def load_schedule():
    try:
        sc = json.loads((ROOT / "state" / "schedule.json").read_text())
        out = {}
        if isinstance(sc, dict):
            for k, v in sc.items():
                st = (v or {}).get("start_time") or (v or {}).get("start")
                if st:
                    out[k] = st
        return out
    except Exception:
        return {}


def state_flags(con, now, positions, orders):
    """Wrong-by-state conditions, checked continuously (founding exhibit
    Wu/Bu = YIBYUN: Bu held 5@42 on a rescheduled match, Wu unworked)."""
    flags = []
    held = {p[1]: p for p in positions}
    buys = {}
    sells = {}
    for _ts, _oid, tk, act, px, rem in orders:
        (buys if act == "buy" else sells).setdefault(tk, 0)
        if act == "buy":
            buys[tk] = buys.get(tk, 0) + rem
        else:
            sells[tk] = sells.get(tk, 0) + rem
    sched = load_schedule()
    for tk, p in held.items():
        et = tk.rsplit("-", 1)[0]
        sib = None
        for cand in held:
            pass
        # sibling = the other leg of the event among ALL tickers we can see
        # (orders or positions); fall back to name arithmetic
        sib_tks = [t for t in set(list(buys) + list(sells) + list(held))
                   if t.rsplit("-", 1)[0] == et and t != tk]
        sib_worked = any(buys.get(s, 0) > 0 or s in held
                         for s in sib_tks)
        # window open = no evidence the match ended (position unsettled
        # IS that evidence here — unsettled + sibling book still quoted)
        if not sib_worked:
            flags.append(("one_sided_sibling_unworked", tk,
                          "held %.0f, no sibling position and no resting "
                          "sibling buy (Wu/Bu class)" % p[2]))
        if tk not in sells or sells.get(tk, 0) < p[2]:
            flags.append(("naked_leg", tk,
                          "held %.0f vs resting sells %.0f"
                          % (p[2], sells.get(tk, 0))))
        st = sched.get(et)
        if st:
            try:
                ep = datetime.fromisoformat(st).timestamp()
                if ep - now > 12 * 3600:
                    flags.append(("far_from_start", tk,
                                  "held %.0f with start %.1fh away"
                                  % (p[2], (ep - now) / 3600.0)))
            except Exception:
                pass
    # count drift: equity table's n_positions vs this snapshot
    row = con.execute("SELECT n_positions FROM equity ORDER BY ts DESC "
                      "LIMIT 1").fetchone()
    if row and abs(row[0] - len(positions)) > 5:
        flags.append(("count_drift", "",
                      "positions %d vs last snapshot %d"
                      % (len(positions), row[0])))
    return flags


# ---------------- THE TICKER (HTTP, token, loopback) ----------------
def token():
    if TOKEN_FILE.exists():
        return TOKEN_FILE.read_text().strip()
    t = secrets.token_hex(16)
    TOKEN_FILE.write_text(t)
    return t


TOK = token()


def q(sql, args=()):
    con = sqlite3.connect("file:%s?mode=ro" % DB, uri=True, timeout=2)
    try:
        return con.execute(sql, args).fetchall()
    finally:
        con.close()


def day_series(day):
    return q("SELECT ts, equity_c, cash_c, marked_c FROM equity "
             "WHERE day=? ORDER BY ts", (day,))


def fund_sheet(day):
    """Part 5b — derived from the equity series + exchange fills only."""
    s = day_series(day)
    fills = q("SELECT ticker, action, count_fp, yes_price_c, is_taker, ts "
              "FROM fills WHERE day=? ORDER BY ts", (day,))
    out = {"day": day, "n_equity_points": len(s)}
    if s:
        eq = [r[1] / 100.0 for r in s]
        out["open"] = eq[0]
        out["high"] = max(eq)
        out["low"] = min(eq)
        out["close"] = eq[-1]
        out["day_pnl"] = round(eq[-1] - eq[0], 2)
        out["nav"] = eq[-1]
        peak, dd = eq[0], 0.0
        for v in eq:
            peak = max(peak, v)
            dd = min(dd, v - peak)
        out["running_drawdown"] = round(dd, 2)
    buys = [f for f in fills if f[1] == "buy"]
    out["fills"] = len(fills)
    out["maker"] = sum(1 for f in fills if not f[4])
    out["taker"] = sum(1 for f in fills if f[4])
    out["wagered"] = round(sum(f[2] * f[3] for f in buys) / 100.0, 2)
    if s and out.get("nav"):
        out["deployment_pct_of_nav"] = round(
            out["wagered"] / out["nav"] * 100.0, 1) if out["nav"] else None
    n = len(buys)
    out["expectancy_note"] = ("INSUFFICIENT-N (n=%d fills; per-trade "
                              "expectancy and Sharpe-class ratios print "
                              "with their n once the series earns them)"
                              % n) if n < 30 else None
    out["operator_reference_lines"] = {
        "day_dollar_ref": OPERATOR_DAY_REF,
        "yield_ref_pct": OPERATOR_YIELD_REF,
        "note": "the operator's decision lines, shown in exposure "
                "context — never machine targets"}
    return out


PAGE = """<!doctype html><html><head><meta charset="utf-8">
<title>OMI FUND — THE TICKER</title><style>
body{background:#0b0e13;color:#cdd6e0;font:13px/1.45 ui-monospace,monospace;margin:16px}
h1,h2{color:#e8eef4;font-size:15px} table{border-collapse:collapse;width:100%%;margin:8px 0}
td,th{border:1px solid #263041;padding:3px 7px;text-align:left;font-size:12px}
th{background:#141a24;cursor:pointer} .pos{color:#5dd39e}.neg{color:#e0705d}
.flag{color:#e0b25d} svg{background:#10151d;border:1px solid #263041}
.ref{color:#7d8aa0;font-style:italic} a{color:#6aa5e0}</style></head><body>
<h1>OMI FUND — THE TICKER <span class="ref">(single source of record; every organ cites this ledger)</span> · <a href="/daysheet?token=%(tok)s">DAY SHEET (pair lens)</a></h1>
%(nav)s
<h2>EQUITY — %(daylabel)s (midnight ET closes the session) · <a href="?token=%(tok)s&day=all">ALL</a></h2>
%(chart)s
<h2>THE FUND SHEET (Part 5b — derived, nothing new collected)</h2><pre>%(fundsheet)s</pre>
<h2>STATE FLAGS (wrong-by-state, continuous — no event needed)</h2>%(flags)s
<h2>OPEN POSITIONS</h2>%(positions)s
<h2>CLOSED / FILLS TODAY (Kalshi's own fills feed, verbatim)</h2>%(fills)s
<h2>OPEN BIDS</h2>%(bids)s
<h2>THE DAY SHEET (one row per game — the 405 game reports' front page)</h2>%(daysheet)s
<script>
document.querySelectorAll('th').forEach(function(th){th.onclick=function(){
var t=th.closest('table'),i=[].indexOf.call(th.parentNode.children,th);
var r=[].slice.call(t.tBodies[0].rows);
r.sort(function(a,b){var x=a.cells[i].innerText,y=b.cells[i].innerText;
var nx=parseFloat(x),ny=parseFloat(y);
return (!isNaN(nx)&&!isNaN(ny))?nx-ny:x.localeCompare(y)});
if(th.dataset.d=='1'){r.reverse();th.dataset.d=''}else{th.dataset.d='1'}
r.forEach(function(x){t.tBodies[0].appendChild(x)})}});
</script></body></html>"""


def chart_svg(rows, w=1080, h=220):
    if not rows:
        return "<p>no equity points yet</p>"
    eq = [r[1] / 100.0 for r in rows]
    lo, hi = min(eq), max(eq)
    if hi - lo < 1:
        hi, lo = hi + 0.5, lo - 0.5
    pts = []
    for i, v in enumerate(eq):
        x = 10 + i * (w - 20) / max(1, len(eq) - 1)
        y = h - 15 - (v - lo) * (h - 30) / (hi - lo)
        pts.append("%.1f,%.1f" % (x, y))
    o, c = eq[0], eq[-1]
    col = "#5dd39e" if c >= o else "#e0705d"
    return ("<svg width='%d' height='%d'><polyline fill='none' "
            "stroke='%s' stroke-width='1.6' points='%s'/>"
            "<text x='12' y='14' fill='#7d8aa0' font-size='11'>O %.2f  "
            "H %.2f  L %.2f  C %.2f  ΔDAY %+.2f</text></svg>"
            % (w, h, col, " ".join(pts), o, max(eq), min(eq), c, c - o))


def table(headers, rows):
    if not rows:
        return "<p>—</p>"
    th = "".join("<th>%s</th>" % h for h in headers)
    trs = "".join("<tr>%s</tr>" % "".join(
        "<td>%s</td>" % c for c in r) for r in rows)
    return ("<table><thead><tr>%s</tr></thead><tbody>%s</tbody></table>"
            % (th, trs))


def daysheet_html(day):
    p = ROOT.parent / ".claude" / "game_reports" / day / "DAYSHEET.json"
    if not p.exists():
        return ("<p>DAYSHEET.json not generated yet for %s (the nightly "
                "game-report run writes it; on-demand: analysis/"
                "game_report.py --date %s)</p>" % (day, day))
    try:
        rows = json.loads(p.read_text())
    except Exception as e:
        return "<p>daysheet unreadable: %s</p>" % e
    return table(
        ["game", "cat", "leg", "role", "entry¢ (basis)", "window",
         "combined", "outcome", "grade", "$ (¢ vs basis)"],
        [[r.get(k, "") for k in ("game", "cat", "leg", "role", "entry",
                                 "window", "combined", "outcome", "grade",
                                 "dollars")] for r in rows])


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _send(self, body, ctype, extra=None):
        if isinstance(body, str):
            body = body.encode()
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        for k, v in (extra or {}).items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        u = urlparse(self.path)
        qs = parse_qs(u.query)
        if (qs.get("token") or [""])[0] != TOK:
            self.send_response(403)
            self.end_headers()
            self.wfile.write(b"token required")
            return
        # [C-DAYSHEET-LIVE, 07-16 — supersedes 155a1d6's pair-lens bundle
        # per operator ruling: the approved POSITIONS/ORDERS/CLOSED mock v4
        # is the real spec, and post-dates that bundle's deploy] Day Sheet
        # panel, self-contained page + 4 JSON routes, same port/token/
        # tunnel as always. Old pair-lens component tree under
        # components/trading/arb/panels/daysheet/* and
        # lib/trading/daysheet-parser.ts is left in the repo untouched —
        # cleanup is a separate, later push, not this one.
        if u.path == "/daysheet":
            self._send(DAYSHEET_PAGE, "text/html; charset=utf-8")
            return
        if u.path == "/api/positions.json":
            # two honest ages (07-16 stale-render catch): last-fill age
            # grows lawfully on a quiet book; RECORDER age is the
            # feed-liveness signal the panel must alarm on.
            age = ds.tape_age_seconds()
            rec = ds.recorder_age_seconds()
            self._send(json.dumps(ds.build_positions()),
                       "application/json",
                       {"X-Tape-Age-Seconds": ("%.0f" % age)
                        if age is not None else "",
                        "X-Recorder-Age-Seconds": ("%.0f" % rec)
                        if rec is not None else ""})
            return
        if u.path == "/api/orders.json":
            self._send(json.dumps(ds.build_orders()), "application/json")
            return
        if u.path == "/api/slate.json":
            day_param = (qs.get("day") or [None])[0]
            self._send(json.dumps(ds.build_slate(day_param)),
                       "application/json")
            return
        if u.path == "/api/closed.json":
            day_param = (qs.get("day") or [None])[0]
            # [P4 DAY BANK, 07-17] a CLOSED day serves from the archive
            # and never rebuilds: first serve of a past day banks the
            # payload verbatim; every later request reads the bank —
            # grades, bells, walks frozen as the day ended (the
            # dropdown brief reads this archive).
            today = datetime.now(ET).strftime("%Y%m%d")
            if day_param and day_param < today:
                bank = ROOT / "state" / "daysheet_bank"
                bank.mkdir(parents=True, exist_ok=True)
                bp = bank / ("closed_%s.json" % day_param)
                if bp.exists():
                    self._send(bp.read_text(encoding="utf-8"),
                               "application/json")
                    return
                body = json.dumps(ds.build_closed(day_param))
                try:
                    bp.write_text(body, encoding="utf-8")
                except OSError:
                    pass
                self._send(body, "application/json")
                return
            self._send(json.dumps(ds.build_closed(day_param)),
                       "application/json")
            return
        if u.path.startswith("/api/tape/") and u.path.endswith(".json"):
            ticker = u.path[len("/api/tape/"):-len(".json")]
            self._send(json.dumps(ds.build_tape(ticker)), "application/json")
            return
        if u.path == "/daysheet.md":
            p = ROOT.parent / ".claude" / "today_sheet" / "LATEST.md"
            if p.exists():
                self._send(p.read_text(encoding="utf-8"),
                           "text/plain; charset=utf-8",
                           {"x-sheet-mtime": datetime.fromtimestamp(
                               p.stat().st_mtime, ET).isoformat()})
            else:
                self.send_response(404)
                self.end_headers()
            return
        day = (qs.get("day") or [datetime.now(ET).strftime("%Y%m%d")])[0]
        if day == "all":
            rows = q("SELECT ts, equity_c, cash_c, marked_c FROM equity "
                     "ORDER BY ts")
            daylabel = "ALL (the fund's life)"
        else:
            rows = day_series(day)
            daylabel = day
        now = time.time()
        pos = q("SELECT ticker, qty, exposure_c, mark_c FROM "
                "snap_positions WHERE ts=(SELECT MAX(ts) FROM "
                "snap_positions)")
        sells = dict((r[0], (r[1], r[2])) for r in q(
            "SELECT ticker, yes_price_c, remaining FROM snap_orders "
            "WHERE ts=(SELECT MAX(ts) FROM snap_orders) AND "
            "action='sell'"))
        posrows = []
        for tk, qty, exp, mk in pos:
            basis = int(exp / qty) if qty else 0
            unre = mk - exp
            xo = sells.get(tk)
            posrows.append([
                tk[-22:], "%.0f" % qty,
                "%d¢" % basis, "%d¢" % (mk / qty if qty else 0),
                "<span class='%s'>%+d¢ (%.0f%% of basis)</span>"
                % ("pos" if unre >= 0 else "neg", unre,
                   (unre / exp * 100) if exp else 0),
                ("exit %d¢ ×%.0f resting" % (xo[0], xo[1])) if xo
                else "<span class='flag'>NO EXIT RESTING</span>"])
        fills = q("SELECT ts, ticker, action, count_fp, yes_price_c, "
                  "is_taker FROM fills WHERE day=? ORDER BY ts DESC",
                  (day if day != "all"
                   else datetime.now(ET).strftime("%Y%m%d"),))
        fillrows = [[datetime.fromtimestamp(r[0], ET).strftime("%I:%M:%S%p"),
                     r[1][-22:], r[2], "%.2f" % r[3], "%d¢" % r[4],
                     "taker" if r[5] else "maker"] for r in fills[:80]]
        bids = q("SELECT ticker, yes_price_c, remaining FROM snap_orders "
                 "WHERE ts=(SELECT MAX(ts) FROM snap_orders) AND "
                 "action='buy'")
        bidrows = [[r[0][-22:], "%d¢" % r[1], "%.0f" % r[2]]
                   for r in bids[:120]]
        fl = q("SELECT ts, kind, ticker, detail FROM flags WHERE "
               "ts > ? ORDER BY ts DESC", (now - 3700,))
        flagrows = [[datetime.fromtimestamp(r[0], ET).strftime("%I:%M%p"),
                     "<span class='flag'>%s</span>" % r[1], r[2][-22:],
                     r[3]] for r in fl[:40]]
        latest = q("SELECT equity_c, cash_c, marked_c, n_positions FROM "
                   "equity ORDER BY ts DESC LIMIT 1")
        nav = ("<p>NAV <b>$%.2f</b> (cash $%.2f + marked $%.2f) · "
               "positions %d · fills today %d (maker %d / taker %d) "
               "<span class='ref'>· operator reference lines: $%.0f/day "
               "and %.0f%% — his decision lines, in exposure context, "
               "never machine targets</span></p>"
               % (latest[0][0] / 100.0, latest[0][1] / 100.0,
                  latest[0][2] / 100.0, latest[0][3], len(fills),
                  sum(1 for f in fills if not f[5]),
                  sum(1 for f in fills if f[5]),
                  OPERATOR_DAY_REF, OPERATOR_YIELD_REF)) if latest \
            else "<p>recorder warming…</p>"
        html = PAGE % {
            "tok": TOK, "daylabel": daylabel,
            "nav": nav, "chart": chart_svg(rows),
            "fundsheet": json.dumps(fund_sheet(
                day if day != "all"
                else datetime.now(ET).strftime("%Y%m%d")), indent=1),
            "flags": table(["ts", "kind", "ticker", "detail"], flagrows)
            if flagrows else "<p class='pos'>none — clean state</p>",
            "positions": table(["leg", "qty", "basis", "mark",
                                "unrealized (¢ beside basis)", "exit"],
                               posrows),
            "fills": table(["ts", "leg", "action", "shares", "price",
                            "maker/taker"], fillrows),
            "bids": table(["leg", "aim", "shares"], bidrows),
            "daysheet": daysheet_html(
                day if day != "all"
                else datetime.now(ET).strftime("%Y%m%d"))}
        body = html.encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def main():
    init_db()
    t = threading.Thread(target=recorder_loop, daemon=True)
    t.start()
    print("fund_tracker: recorder running; ticker on "
          "http://127.0.0.1:%d/?token=%s" % (PORT, TOK))
    ThreadingHTTPServer(("127.0.0.1", PORT), H).serve_forever()


if __name__ == "__main__":
    main()
