#!/usr/bin/env python3
"""C-LIVE-VIEWER v1 — localhost command picture + per-trade viewer.
READ-ONLY end to end: tails the exact files the monitor/adjudication write
(spec section 0: if an API number disagrees with the nightly ledger's own
footer, the API is the bug, by definition). Loopback only. Nothing on the
order path. Spec: .claude/render/LIVE_BUILD_SPEC.md (verbatim slot pending;
spec wins on landing). Colors PROVISIONAL pending the spec's verbatim key."""
import glob, gzip, json, re, threading
from datetime import datetime, timezone, timedelta
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WS = ROOT.parent
ET = timezone(timedelta(hours=-4))
PORT = 8787

C = {"AGREE": "#10b981", "WOULD-REFUSE": "#ef4444", "NO-OPINION": "#71717a",
     "FITTED": "#10b981", "DECREED": "#f59e0b", "NAKED": "#ef4444"}
CSS = """<style>body{background:#111318;color:#e5e7eb;font-family:ui-monospace,monospace;
margin:1.2em}h1,h2{color:#93c5fd}table{border-collapse:collapse;font-size:12px}
td,th{border:1px solid #333;padding:2px 7px}.badge{padding:1px 7px;border-radius:9px;
font-size:11px;font-weight:700}.stale{background:#9ca3af;color:#111}
.fresh{background:#10b981;color:#111}.panel{border:1px solid #333;border-radius:8px;
padding:.7em;margin:.7em 0}a{color:#93c5fd}.bar{height:14px;display:inline-block}</style>"""


def latest(pat):
    fs = sorted(glob.glob(str(pat)))
    return Path(fs[-1]) if fs else None


def stamp(p):
    if p is None or not Path(p).exists():
        return '<span class="badge stale">MISSING</span>'
    age = (datetime.now(ET).timestamp() - Path(p).stat().st_mtime) / 60.0
    cls = "stale" if age > 90 else "fresh"
    return '<span class="badge %s">%s · %.0f min</span>' % (cls, Path(p).name, age)


def results():
    p = latest(WS / ".claude/adjudication/RESULTS_*.json")
    if not p:
        return None, None
    try:
        return json.loads(p.read_text(encoding="utf-8", errors="replace")), p
    except Exception:
        return None, p


def fsr_md():
    p = latest(WS / ".claude/adjudication/FULL_SLATE_REVIEW_*.md")
    return (p.read_text(encoding="utf-8", errors="replace"), p) if p else ("", None)


def day_events(tk, ymd):
    out = []
    lp = ROOT / "logs" / ("live_v3_%s.jsonl" % ymd)
    if not lp.exists():
        return out
    KEEP = ("order_placed", "order_cancelled", "entry_filled", "exit_filled",
            "v4_exit_posted", "settled", "v4_move_repost", "gun_fired",
            "scalp_filled", "fill_booked_reconcile")
    for line in open(lp, encoding="utf-8", errors="replace"):
        if tk not in line:
            continue
        try:
            d = json.loads(line)
        except ValueError:
            continue
        if d.get("ticker") != tk and (d.get("details") or {}).get("event", "") != tk.rsplit("-", 1)[0]:
            continue
        if d["event"] in KEEP:
            out.append(d)
    return out


def tape_svg(tk, marks):
    """Triptych: price polyline + prints dots + decision markers (Exhibit-1 grammar)."""
    pts, prints = [], []
    for f in glob.glob(str(ROOT / "analysis/premarket_ticks" / (tk + ".csv*"))):
        op = gzip.open if f.endswith(".gz") else open
        with op(f, "rt", encoding="utf-8", errors="replace") as fh:
            next(fh, None)
            for i, ln in enumerate(fh):
                if i % 5:
                    continue
                p = ln.split(",")
                if len(p) < 23:
                    continue
                try:
                    ts = datetime.strptime(p[0], "%Y-%m-%d %I:%M:%S %p").replace(tzinfo=ET).timestamp()
                    pts.append((ts, float(p[22])))
                except Exception:
                    continue
    for f in glob.glob(str(ROOT / "analysis/trades" / (tk + ".csv*"))):
        op = gzip.open if f.endswith(".gz") else open
        with op(f, "rt", encoding="utf-8", errors="replace") as fh:
            next(fh, None)
            for ln in fh:
                p = ln.split(",")
                try:
                    ts = datetime.strptime(p[0], "%Y-%m-%d %I:%M:%S %p").replace(tzinfo=ET).timestamp()
                    prints.append((ts, float(p[2])))
                except Exception:
                    continue
    if not pts and not prints:
        return "<i>no tape on disk for %s</i>" % tk
    allx = [x for x, _ in pts] + [x for x, _ in prints] + [m[0] for m in marks]
    x0, x1 = min(allx), max(allx) or 1
    W, H = 900, 220
    def X(t):
        return 40 + (t - x0) / max(1, x1 - x0) * (W - 60)
    def Y(v):
        return H - 15 - v / 100.0 * (H - 30)
    poly = " ".join("%.1f,%.1f" % (X(t), Y(v)) for t, v in pts[::max(1, len(pts) // 800)])
    dots = "".join('<circle cx="%.1f" cy="%.1f" r="2.2" fill="#60a5fa"/>' % (X(t), Y(v))
                   for t, v in prints)
    mk = ""
    for ts, label, col in marks:
        mk += ('<line x1="%.1f" y1="12" x2="%.1f" y2="%d" stroke="%s" stroke-dasharray="3,3"/>'
               '<text x="%.1f" y="10" fill="%s" font-size="9">%s</text>'
               % (X(ts), X(ts), H - 15, col, X(ts) - 15, col, label[:16]))
    return ('<svg width="%d" height="%d" style="background:#0b0d10">'
            '<polyline points="%s" fill="none" stroke="#e5e7eb" stroke-width="1"/>%s%s'
            '<text x="4" y="%d" fill="#666" font-size="9">0</text>'
            '<text x="4" y="14" fill="#666" font-size="9">100</text></svg>'
            % (W, H, poly, dots, mk, H - 16))


def page_command():
    res, rp = results()
    md, mp = fsr_md()
    ledger = (ROOT / "docs/CLASS_LEDGER.md")
    lv = WS / ".claude/live_20260705/LIVE_STATUS.md"
    h = ["<html><head><title>OMQS command</title>%s<meta http-equiv=refresh content=60></head><body>" % CSS,
         "<h1>COMMAND — read-only picture (truth = the nightly files; if this page disagrees, the page is the bug)</h1>"]
    # migration bars
    h.append('<div class="panel"><h2>Migration meter %s</h2>' % stamp(rp))
    if res:
        for cat, s in sorted(res.get("per_cat", {}).items()):
            n = sum(v for k, v in s.items() if k in ("AGREE", "WOULD-REFUSE", "NO-OPINION"))
            ag = s.get("AGREE", 0)
            pct = 100.0 * ag / n if n else 0
            h.append('%s <span class="bar" style="width:%.0fpx;background:%s"></span>'
                     '<span class="bar" style="width:%.0fpx;background:%s"></span> '
                     'AGREE %d/%d (%.0f%%) · pair97 %d<br>' % (
                         cat.ljust(10).replace(" ", "&nbsp;"), pct * 2.2, C["AGREE"],
                         (100 - pct) * 2.2, C["DECREED"], ag, n, pct,
                         s.get("pair97_touched", 0)))
    m = re.search(r"STEP-LEVEL MIGRATION METER: (.*?)\*\*", md)
    if m:
        h.append("<b>Step-level:</b> %s" % m.group(1))
    h.append("</div>")
    # ranked fix queue + no-fill taxonomy + exchange truth (parsed from the slate review)
    h.append('<div class="panel"><h2>Ranked fix queue %s</h2><table>' % stamp(mp))
    part4 = md.split("## Part 4")[-1]
    for row in re.findall(r"\| (.+?) \| (\d+) \| ([\d.]+) \|", part4)[:8]:
        h.append("<tr><td>%s</td><td>%s</td><td>$%s</td></tr>" % row)
    h.append("</table></div>")
    nf = re.search(r"## Part 2 — the no-fill cohort \((\d+) legs", md)
    tax = re.findall(r"\| .*? \| .*? \| \d+ \| \d+ \| ([a-z_]+)", md.split("## Part 2")[-1].split("## Part 3")[0]) if md else []
    from collections import Counter
    h.append('<div class="panel"><h2>No-fill taxonomy %s</h2>%s<table>' % (
        stamp(mp), ("<b>%s legs never filled</b>" % nf.group(1)) if nf else ""))
    for k, v in Counter(tax).most_common():
        h.append("<tr><td>%s</td><td>%d</td></tr>" % (k, v))
    h.append("</table></div>")
    xt = re.search(r"exchange day buy-fills: (\d+) across (\d+) tickers \| \*\*violations: (\d+)\*\*", md)
    h.append('<div class="panel"><h2>Exchange truth (nightly cadence) %s</h2>%s</div>' % (
        stamp(mp), ("day buy-fills %s / %s tickers — <b style='color:%s'>violations: %s</b>"
                    % (xt.group(1), xt.group(2),
                       C["WOULD-REFUSE"] if int(xt.group(3)) else C["AGREE"], xt.group(3))) if xt else "n/a"))
    # class badges
    h.append('<div class="panel"><h2>Class ledger %s</h2>' % stamp(ledger))
    try:
        for cl in re.findall(r"## (CLASS — [^\n]+)", ledger.read_text(encoding="utf-8", errors="replace")):
            h.append('<span class="badge" style="background:#334155;color:#e5e7eb;margin:2px">%s</span> ' % cl[:60])
    except OSError:
        pass
    h.append("</div>")
    # trades index
    h.append('<div class="panel"><h2>Trades (%s)</h2>' % (res.get("generated", "?") if res else "?"))
    if res:
        for r in res["rows"]:
            h.append('<a href="/trade/%s">%s</a> <span style="color:%s">%s</span> %s @%s &nbsp; '
                     % (r["id"], r["id"], C.get(r["grade"], "#ccc"), r["grade"][:1],
                        r["tk"].replace("KX", "")[:24], r["px"]))
    h.append("</div>")
    h.append('<div class="panel">LIVE_STATUS %s · NIGHTLY_PASS %s</div>' % (
        stamp(lv), stamp(WS / ".claude/live_20260705/NIGHTLY_PASS.md")))
    h.append("</body></html>")
    return "".join(h)


def page_trade(tid):
    res, rp = results()
    md, mp = fsr_md()
    if not res:
        return "<html><body>no RESULTS on disk</body></html>"
    row = next((r for r in res["rows"] if r["id"] == tid), None)
    if row is None:
        return "<html><body>unknown trade id %s</body></html>" % tid
    tk = row["tk"]
    ymd = tid.split("-")[1]
    evs = day_events(tk, ymd)
    marks = []
    for d in evs:
        e, det = d["event"], d.get("details") or {}
        col = {"entry_filled": C["AGREE"], "exit_filled": "#60a5fa", "settled": "#a78bfa",
               "gun_fired": C["WOULD-REFUSE"]}.get(e, "#f59e0b")
        marks.append((d["ts_epoch"], e.replace("_", " "), col))
    open_trade = not any(d["event"] in ("settled",) for d in evs) and row.get("pnl_cents") is None
    # L1-L9 strip from the slate review (row data, never hardcoded)
    strip = []
    for mrow in re.findall(r"\| %s \| (L\d) \| (.+?) \| (FITTED|DECREED|NAKED) \|" % tid, md):
        strip.append('<td style="border-top:4px solid %s"><b>%s</b><br><small>%s</small></td>'
                     % (C[mrow[2]], mrow[0], mrow[1][:48]))
    h = ["<html><head><title>%s</title>%s%s</head><body>" % (
            tid, CSS, "<meta http-equiv=refresh content=5>" if open_trade else ""),
         "<h1>%s — %s <span style='color:%s'>%s</span> @%s (cycle %s) %s</h1>" % (
             tid, tk.replace("KX", ""), C.get(row["grade"], "#ccc"), row["grade"],
             row["px"], row["cycle"], "<span class='badge fresh'>OPEN · 5s poll</span>" if open_trade else ""),
         "<p>posterior %s · pnl¢ %s · %s</p>" % (row.get("posterior"), row.get("pnl_cents"),
                                                 row.get("why", "")[:140]),
         '<div class="panel"><h2>Triptych (tape · prints · decisions) %s</h2>%s</div>' % (
             stamp(latest(ROOT / "analysis/premarket_ticks" / (tk + ".csv*"))), tape_svg(tk, marks)),
         '<div class="panel"><h2>L1–L9 step strip %s</h2><table><tr>%s</tr></table></div>' % (
             stamp(mp), "".join(strip) or "<td>no step rows found for this id</td>"),
         '<div class="panel"><h2>Decision log</h2><table>']
    for d in evs[:60]:
        h.append("<tr><td>%s</td><td>%s</td><td>%s</td></tr>" % (
            d["ts"][11:22], d["event"], json.dumps(d.get("details") or {})[:130].replace("<", "&lt;")))
    h.append("</table></div><p><a href='/command'>&larr; command</a></p></body></html>")
    return "".join(h)


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass
    def do_GET(self):
        try:
            if self.path.startswith("/trade/"):
                body = page_trade(self.path.split("/trade/")[1].split("?")[0])
            elif self.path.startswith("/api/results"):
                r, _ = results()
                body = json.dumps(r or {})
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(body.encode())
                return
            else:
                body = page_command()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(body.encode("utf-8", "replace"))
        except Exception as e:
            try:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(("viewer error: %s" % e).encode())
            except Exception:
                pass


if __name__ == "__main__":
    srv = HTTPServer(("127.0.0.1", PORT), H)   # loopback ONLY, read-only
    print("live_viewer on http://127.0.0.1:%d (loopback; read-only)" % PORT)
    srv.serve_forever()
