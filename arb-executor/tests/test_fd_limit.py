#!/usr/bin/env python3
"""Regression: _raise_fd_limit() raises the RLIMIT_NOFILE soft limit at startup (replacing the
manual per-restart `ulimit -n`), is DEFENSIVE (never crashes startup), and is wired into main().
Cross-platform: on Unix it actually raises to min(262144, hard); on Windows (no `resource` module)
it returns None without raising. Startup-only -- no entry/exit behavior change.
Run: cd arb-executor && python3 tests/test_fd_limit.py"""
import sys
from pathlib import Path
REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
import live_v4 as M

fails = 0
def check(c, m):
    global fails
    print(("PASS " if c else "*** FAIL ") + m); fails += (0 if c else 1)

check(callable(getattr(M, "_raise_fd_limit", None)), "_raise_fd_limit exists and is callable")

# Defensive: must never raise, on any platform.
raised = False
try:
    r = M._raise_fd_limit()
except Exception as e:
    raised = True; r = None
    print("   (unexpected exception:", repr(e), ")")
check(not raised, "calling _raise_fd_limit() never raises (defensive startup)")

# Platform-specific outcome.
try:
    import resource
    have_resource = True
except Exception:
    have_resource = False

if have_resource:
    soft, hard = resource.getrlimit(resource.RLIMIT_NOFILE)
    check(r is not None and isinstance(r, tuple) and len(r) == 2,
          "Unix: returns (soft, hard) tuple")
    check(r[0] == min(262144, hard),
          "Unix: soft raised to min(262144, hard)=%d (got %s)" % (min(262144, hard), r[0] if r else None))
    check(soft >= min(262144, hard) or soft == r[0],
          "Unix: limit took (current soft now %d)" % soft)
    # idempotent: calling again is fine, never lowers below target
    r2 = M._raise_fd_limit()
    check(r2 is not None and r2[0] == min(262144, hard), "Unix: idempotent on a second call")
else:
    check(r is None, "Windows (no resource module): returns None gracefully, no crash")

# A failing setrlimit must be swallowed (target above hard is clamped, not raised; bogus call caught).
try:
    M._raise_fd_limit(10**12)   # absurd target -> clamped to hard, must not raise
    swallowed = True
except Exception:
    swallowed = False
check(swallowed, "absurd target (10^12) is clamped to hard, never raises")

# ---- source-pins ----
src = (REPO / "live_v4.py").read_text(encoding="utf-8", errors="ignore")
check("import resource" in src and "import resource\n" not in src.split("def _raise_fd_limit", 1)[0],
      "resource is lazy-imported INSIDE _raise_fd_limit (not module-top -> Windows-importable)")
check("resource.setrlimit(resource.RLIMIT_NOFILE, (new_soft, hard))" in src,
      "setrlimit raises soft to new_soft, preserves hard")
check("new_soft = min(target, hard)" in src, "soft is capped at the hard limit (no privilege needed)")
check("async def main():\n    _raise_fd_limit()" in src, "_raise_fd_limit() is called first thing in main()")
check("except Exception as e:" in src.split("def _raise_fd_limit", 1)[1].split("async def main", 1)[0],
      "try/except wraps the setrlimit (failure logs a warning, does not crash startup)")

print(f"\n{'ALL PASS' if fails == 0 else str(fails) + ' FAILED'}")
sys.exit(1 if fails else 0)
