#!/usr/bin/env python3
"""[C-FV-QUOTE] the operator's on-demand FV quote -- read-only, never a gate.

blend_quote is the single codepath for both consumers (the CLI tool and the
flag-gated FV-OBSERVE v4_place hook, default OFF pending Plex's split
countersign). Uniform weights over FRESH sources; single fresh source
refuses to call itself a blend; stale sources dropped AND named.
Run: cd arb-executor && python3 tests/test_fv_quote.py
"""
import sys, types, inspect, json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
import live_v4 as M
import importlib.util
_spec = importlib.util.spec_from_file_location(
    "fv_quote_mod", Path(REPO) / "analysis" / "fv_quote.py")
FQ = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(FQ)
blend_quote = FQ.blend_quote

fails = 0
def check(c, m):
    global fails; print(("PASS " if c else "*** FAIL ") + m); fails += (0 if c else 1)

# ---- 1. the blend (the Plex skeleton: uniform weights) ----
fv, label, used, dropped = blend_quote([("odds_implied", 78.0, True),
                                        ("kalshi_mid", 80.0, True)])
check(fv == 79.0 and label == "blend_uniform_2" and dropped == [],
      "two fresh sources -> uniform blend 79.0")
fv, label, used, dropped = blend_quote([("odds_implied", 78.0, False),
                                        ("kalshi_mid", 80.0, True)])
check(fv == 80.0 and label == "single:kalshi_mid" and dropped == ["odds_implied"],
      "single fresh source -> printed as single-source, REFUSES the blend label; stale named")
fv, label, used, dropped = blend_quote([("odds_implied", None, False),
                                        ("kalshi_mid", None, False)])
check(fv is None and label == "no_fresh_source" and set(dropped) == {"odds_implied", "kalshi_mid"},
      "no fresh source -> UNAVAILABLE, both dropped and named")

# ---- 2. never-bans: reference only, no order surface ----
src_tool = inspect.getsource(FQ)
check("NEVER-BANS" in src_tool and "place_order" not in src_tool
      and "cancel_order" not in src_tool and "api_post" not in src_tool
      and "api_delete" not in src_tool,
      "tool has ZERO order surface (no place/cancel/post/delete) + never-bans header")

# ---- 3. the FV-OBSERVE hook: one codepath, flag default OFF ----
src_init = inspect.getsource(M.LiveV3.__init__)
check('config.get("fv_observe", False)' in src_init,
      "fv_observe default OFF (pending Plex split countersign)")
cfg = json.load(open(Path(REPO) / "config" / "deploy_v5_live.json"))
check("fv_observe" not in cfg, "deploy config does NOT enable fv_observe")
src_route = inspect.getsource(M.LiveV3._route_event)
check('getattr(self, "fv_observe", False)' in src_route,
      "v4_place hook guarded by the flag (zero cost when off)")
src_hook = inspect.getsource(M.LiveV3._fv_observe_fields)
check('"analysis" / "fv_quote.py"' in src_hook and "mod.blend_quote" in src_hook,
      "hook consumes THE SAME blend_quote codepath as the CLI tool")
# hook failure degrades to empty (never breaks a placement)
s = types.SimpleNamespace()
s._fv_observe_fields = types.MethodType(M.LiveV3._fv_observe_fields, s)
out = s._fv_observe_fields(None, None)   # garbage inputs -> exception path
check(out == {}, "hook degrades to {} on any failure (never blocks a placement)")

print("RESULT:", "ALL PASS" if fails == 0 else "%d FAILS" % fails)
sys.exit(1 if fails else 0)
