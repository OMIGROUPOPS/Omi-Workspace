#!/usr/bin/env python3
"""Local dev-only harness for the /daysheet panel.

NOT part of the deployed server. fund_tracker.py itself can't run in this
sandbox (no Kalshi cert/creds, no live SQLite) and won't be run here per
the standing "no SSH, no live db" instruction. This script mounts the same
four routes plus /daysheet, using the exact same daysheet_panel.py +
daysheet_template.py modules the real fund_tracker.py imports, so the
screenshot below is genuinely the wired panel's own render code running
against fixture data — not a separate mockup.

Usage:
  DAYSHEET_FIXTURE=tools/daysheet_fixtures.json python3 tools/daysheet_dev_server.py
"""
import json
import os
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import daysheet_panel as ds
from daysheet_template import PAGE_TEMPLATE as DAYSHEET_PAGE

DEV_TOK = "devtoken"
PORT = int(os.environ.get("DAYSHEET_DEV_PORT", "8799"))


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
        from urllib.parse import urlparse, parse_qs
        u = urlparse(self.path)
        qs = parse_qs(u.query)
        if (qs.get("token") or [""])[0] != DEV_TOK:
            self.send_response(403)
            self.end_headers()
            self.wfile.write(b"token required")
            return
        if u.path == "/daysheet":
            self._send(DAYSHEET_PAGE, "text/html; charset=utf-8")
            return
        if u.path == "/api/positions.json":
            age = ds.tape_age_seconds()
            self._send(json.dumps(ds.build_positions()), "application/json",
                       {"X-Tape-Age-Seconds": ("%.0f" % age) if age is not None else ""})
            return
        if u.path == "/api/orders.json":
            self._send(json.dumps(ds.build_orders()), "application/json")
            return
        if u.path == "/api/slate.json":
            day_param = (qs.get("day") or [None])[0]
            self._send(json.dumps(ds.build_slate(day_param)), "application/json")
            return
        if u.path == "/api/closed.json":
            day_param = (qs.get("day") or [None])[0]
            self._send(json.dumps(ds.build_closed(day_param)), "application/json")
            return
        if u.path.startswith("/api/tape/") and u.path.endswith(".json"):
            ticker = u.path[len("/api/tape/"):-len(".json")]
            self._send(json.dumps(ds.build_tape(ticker)), "application/json")
            return
        self.send_response(404)
        self.end_headers()


if __name__ == "__main__":
    print("daysheet dev server -> http://127.0.0.1:%d/daysheet?token=%s"
          % (PORT, DEV_TOK))
    ThreadingHTTPServer(("127.0.0.1", PORT), H).serve_forever()
