#!/usr/bin/env python3
"""[C-REPOST-RUNWAY-FIX] regression test: _v4_manage_resting_inner's staircase repost path must NOT raise
UnboundLocalError on repost_runway (the var c03e010 left behind: it defaulted new_regime/new_offset but
repost_runway is assigned only in the non-staircase else-branch (~5940) yet read unconditionally at
pos.runway_status = repost_runway (:6027) and the v4_move_repost log (:6034)). Same two-layer harness as
test_newregime_default.py (no import; AST-extract the REAL source):
  DYNAMIC -- exec the REAL fixed slice (default-init through the else-branch's _runway_status re-derive)
             for BOTH paths; assert staircase binds repost_runway = pos.runway_status (preserve, no-op at
             :6027) WITHOUT calling _runway_status, while non-staircase still re-derives via _runway_status.
  STATIC  -- assert the default precedes the branch, reads pos.runway_status, the else-branch re-derive is
             intact (non-staircase byte-identical), and :6027/:6034 still consume repost_runway.
Run from arb-executor."""
import ast, textwrap, os
src = open(os.environ.get("LV4", "live_v4.py")).read()
tree = ast.parse(src)
fn = next(n for n in ast.walk(tree)
          if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == "_v4_manage_resting_inner")
fsrc = ast.get_source_segment(src, fn)
lines = fsrc.split("\n")
fails = []
def chk(name, cond): print("  %s: %s" % (name, "PASS" if cond else "FAIL")); (None if cond else fails.append(name))

# ---- DYNAMIC: exec the real slice (default-init through the else-branch repost_runway re-derive) ----
i_start = next(i for i, l in enumerate(lines) if "Re-classify regime and recompute" in l)
i_end   = next(i for i, l in enumerate(lines) if 'late_tag="late_remap")' in l)   # closes the else repost_runway stmt
slice_body = textwrap.dedent("\n".join(lines[i_start:i_end + 1]))
frag = ("def _frag(self, pos, current_price, _sc_target, time_to_start):\n"
        + textwrap.indent(slice_body, "    ")
        + "\n    return new_regime, new_offset, new_target, repost_runway\n")
ns = {}
exec(frag, ns); _frag = ns["_frag"]

class Pos:
    def __init__(s, ref, runway="full", regime="r55_64"):
        s.reference_source = ref; s.regime_at_posting = regime; s.runway_status = runway
        s.category = "ATP_MAIN"
class SelfStair:   # staircase path must touch NEITHER regime_lookup NOR _runway_status (fixed anchor)
    def regime_lookup(s, cat, px): raise AssertionError("staircase path must NOT call regime_lookup")
    def _runway_status(s, *a, **k): raise AssertionError("staircase path must NOT re-derive _runway_status")
    entry_table = {}
class SelfJoin:    # non-staircase path uses regime_lookup + entry_table row + _runway_status
    def regime_lookup(s, cat, px): return "r45_54"
    def _runway_status(s, placement_min, time_to_start, late_tag="late_window"): return "late_remap_calc"
    entry_table = {("ATP_MAIN", "r45_54"): (0, 7, 0, 0)}   # row_pm, new_offset, _, _

print("(DYNAMIC) real extracted slice")
# staircase path: pre-fix this raised UnboundLocalError at :6027; now preserves pos.runway_status
try:
    nr, no, nt, rr = _frag(SelfStair(), Pos("staircase", runway="late_window", regime="r55_64"), 70, 68, 90.0)
    chk("(1) staircase path completes WITHOUT UnboundLocalError", True)
    chk("(2) repost_runway defaults to pos.runway_status (preserve, no-op at :6027)", rr == "late_window")
    chk("(3) new_target == _sc_target on staircase path", nt == 68)
    chk("(4) new_regime/new_offset still defaulted (c03e010 intact)", nr == "r55_64" and no == 0)
except UnboundLocalError as e:
    chk("(1) staircase path completes WITHOUT UnboundLocalError", False); print("    UnboundLocalError:", e)
except AssertionError as e:
    chk("(1) staircase path completes WITHOUT calling regime_lookup/_runway_status", False); print("   ", e)

# non-staircase path: byte-identical -> still re-derives repost_runway via _runway_status
nr2, no2, nt2, rr2 = _frag(SelfJoin(), Pos("join_bid", runway="full", regime="r05_14"), 48, 0, 30.0)
chk("(5) non-staircase: repost_runway from _runway_status re-derive (unchanged)", rr2 == "late_remap_calc")
chk("(6) non-staircase: new_offset from entry_table row (unchanged)", no2 == 7)
chk("(7) non-staircase: new_regime from regime_lookup (unchanged)", nr2 == "r45_54")

# ---- STATIC: structure guarantees ----
print("(STATIC) source structure")
ix_reclass   = fsrc.find("# Re-classify regime and recompute")
ix_default   = fsrc.find("repost_runway = pos.runway_status")          # the new default
ix_branch    = fsrc.find('if pos.reference_source == "staircase":', ix_reclass)
ix_elsederive= fsrc.find("repost_runway = self._runway_status(")       # else-branch re-derive intact
ix_assign    = fsrc.find("pos.runway_status = repost_runway", ix_branch)  # :6027 consumer (skip the comment ref before the branch)
ix_log       = fsrc.find('"runway_status": repost_runway,')            # :6034 consumer
chk("(8) default repost_runway between reclass-comment and the branch", 0 <= ix_reclass < ix_default < ix_branch)
chk("(9) default reads pos.runway_status (preserve, not a guess)", ix_default >= 0)
chk("(10) else-branch _runway_status re-derive intact (non-staircase)", ix_elsederive > ix_branch)
chk("(11) :6027 consumer pos.runway_status = repost_runway present after branch", ix_assign > ix_branch)
chk("(12) :6034 v4_move_repost log reads repost_runway (now bound on all paths)", ix_log > ix_branch)

print("\nRESULT:", "ALL PASS" if not fails else "FAILURES %s" % fails)
assert not fails
