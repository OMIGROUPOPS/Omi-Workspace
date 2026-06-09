#!/usr/bin/env python3
"""#0-infra: clean SIGTERM/SIGINT shutdown.

Validates the testable core (signal install needs a real Unix loop, exercised at activation):
  (1) _request_shutdown is idempotent: 1st signal sets the flag + arms the force-exit watchdog at
      V4_SHUTDOWN_TIMEOUT_SEC and does NOT exit; a 2nd signal escalates to hard exit.
  (2) _force_exit hard-exits.
  (3) _shutdown_drain cancels ONLY resting v4 ENTRY bids (entry_resting + is_v4 + order_id),
      leaves active/exit positions, swallows per-cancel API errors, and reports attempted/cancelled.

Run: cd arb-executor && python3 tests/test_shutdown.py
"""
import sys, types, asyncio
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
import live_v4 as M

fails = 0
def check(c, m):
    global fails
    print(("PASS " if c else "*** FAIL ") + m)
    fails += (0 if c else 1)


class _FakeLoop:
    def __init__(self): self.scheduled = []
    def call_later(self, delay, cb): self.scheduled.append((delay, cb))


def make_bot():
    s = types.SimpleNamespace()
    s._shutdown_requested = False
    s.positions = {}
    s._logs = []
    s._log = lambda ev, det=None, ticker=None: s._logs.append((ev, det))
    for nm in ("_request_shutdown", "_force_exit", "_shutdown_drain"):
        setattr(s, nm, types.MethodType(getattr(M.LiveV3, nm), s))
    return s


# ---- capture os._exit + the event loop (signal handlers run on the loop thread) ----
exits = []
_orig_exit = M.os._exit
_orig_getloop = M.asyncio.get_running_loop
M.os._exit = lambda code=0: exits.append(code)
_fake = _FakeLoop()
M.asyncio.get_running_loop = lambda: _fake

# (1) first signal -> flag set, watchdog armed, NO exit
s = make_bot()
s._request_shutdown("SIGTERM")
check(s._shutdown_requested is True, "first signal -> _shutdown_requested=True")
check(exits == [], "first signal -> NO hard exit")
check(len(_fake.scheduled) == 1 and abs(_fake.scheduled[0][0] - M.V4_SHUTDOWN_TIMEOUT_SEC) < 1e-9,
      "first signal -> force-exit watchdog armed at V4_SHUTDOWN_TIMEOUT_SEC (%ds)" % M.V4_SHUTDOWN_TIMEOUT_SEC)

# (2) second signal -> hard exit (idempotent escalation)
s._request_shutdown("SIGTERM")
check(1 in exits, "second signal -> hard exit(1)")

# (3) _force_exit -> hard exit
exits.clear()
s._force_exit()
check(exits == [1], "_force_exit -> hard exit(1)")

M.asyncio.get_running_loop = _orig_getloop   # restore for asyncio.run below

# (4) _shutdown_drain: cancel only entry_resting+v4+order_id; swallow errors; correct counts
cancelled = []
async def fake_cancel(self, tk, oid, label=""):
    if tk == "BOOM":
        raise RuntimeError("api down")
    cancelled.append((tk, oid, label))
    return True

def pos(phase, oid, is_v4=True):
    return types.SimpleNamespace(phase=phase, entry_order_id=oid, is_v4=is_v4)

d = make_bot()
d.cancel_order = types.MethodType(fake_cancel, d)
d.positions = {
    "A":    pos("entry_resting", "oidA"),            # cancel
    "B":    pos("active",        "oidB"),            # skip: not entry_resting (exit bid left)
    "C":    pos("entry_resting", None),              # skip: no order_id
    "D":    pos("entry_resting", "oidD", is_v4=False),  # skip: not v4
    "BOOM": pos("entry_resting", "oidX"),            # raises -> swallowed, counted as attempted
}
asyncio.run(d._shutdown_drain())
got = {tk for tk, _, _ in cancelled}
check(got == {"A"}, "drain cancels only entry_resting+v4+order_id (got %s)" % got)
check(all(l == "shutdown_cancel" for _, _, l in cancelled), "drain uses label=shutdown_cancel")
evs = [e for e, _ in d._logs]
check("shutdown_drain_begin" in evs and "shutdown_drain_done" in evs, "drain logs begin + done")
check(any(e == "shutdown_cancel_error" for e in evs), "drain swallows + logs the BOOM cancel error")
done = [det for e, det in d._logs if e == "shutdown_drain_done"][0]
check(done["attempted"] == 2 and done["cancelled"] == 1, "drain counts: attempted=2 (A,BOOM), cancelled=1 (A)")

M.os._exit = _orig_exit
print("RESULT:", "ALL PASS" if fails == 0 else "%d FAILS" % fails)
sys.exit(1 if fails else 0)
