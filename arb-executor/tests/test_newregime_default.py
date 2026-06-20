#!/usr/bin/env python3
"""[C-NEWREGIME-FIX E147] regression test: _v4_manage_resting_inner's staircase walk-step path must NOT
raise UnboundLocalError on new_regime/new_offset, and the trailing v4_move_repost bookkeeping must read
correct defaults. Two layers (no import; AST-extract the REAL source, matching the staircase-test harness):
  DYNAMIC -- execute the REAL fixed code slice (default-init + the staircase/else branch) for both paths
             and assert the staircase path binds new_regime=pos.regime_at_posting and new_offset=0 (the
             pre-E147 UnboundLocalError) while the non-staircase path is unchanged (regime_lookup + row).
  STATIC  -- assert the default-init precedes the branch, the else-branch assignments are intact
             (non-staircase byte-identical), and the v4_move_repost log reads the now-defaulted vars.
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

# ---- DYNAMIC: exec the real slice (default-init through the branch's new_target) ----
i_start = next(i for i, l in enumerate(lines) if "Re-classify regime and recompute" in l)
i_end   = next(i for i, l in enumerate(lines) if "new_target = max(1, current_price - new_offset)" in l)
slice_body = textwrap.dedent("\n".join(lines[i_start:i_end + 1]))
frag = ("def _frag(self, pos, current_price, _sc_target):\n"
        + textwrap.indent(slice_body, "    ")
        + "\n    return new_regime, new_offset, new_target\n")
ns = {}
exec(frag, ns); _frag = ns["_frag"]

class Pos:
    def __init__(s, ref, regime="r55_64"):
        s.reference_source = ref; s.regime_at_posting = regime
class SelfStair:   # staircase path never touches regime_lookup/entry_table
    def regime_lookup(s, cat, px): raise AssertionError("staircase path must NOT call regime_lookup")
    entry_table = {}
class SelfJoin:    # non-staircase path uses both
    def regime_lookup(s, cat, px): return "r45_54"
    entry_table = {("ATP_MAIN", "r45_54"): (0, 7, 0, 0)}   # row_pm, new_offset, _, _

print("(DYNAMIC) real extracted slice")
# staircase path: pre-E147 this raised UnboundLocalError at the trailing read; now must return defaults
try:
    nr, no, nt = _frag(SelfStair(), Pos("staircase", regime="r55_64"), 70, 68)  # current_price=70, _sc_target=68
    chk("(1) staircase path completes WITHOUT UnboundLocalError", True)
    chk("(2) new_regime defaults to pos.regime_at_posting (no-op preserve)", nr == "r55_64")
    chk("(3) new_offset defaults to 0 (fixed-anchor, not meaningful)", no == 0)
    chk("(4) new_target == _sc_target on staircase path", nt == 68)
except UnboundLocalError as e:
    chk("(1) staircase path completes WITHOUT UnboundLocalError", False); print("    UnboundLocalError:", e)
# non-staircase path: byte-identical -> regime_lookup + row unpack
class _pos2: reference_source = "join_bid"; regime_at_posting = "r05_14"; category = "ATP_MAIN"
p2 = _pos2(); p2.category = "ATP_MAIN"
# the else-branch reads pos.category; SelfJoin.entry_table keyed on ("ATP_MAIN","r45_54")
class _selfjoin2(SelfJoin): pass
sj = _selfjoin2()
# give pos a category attr for the (pos.category, new_regime) lookup
class PosJoin:
    reference_source = "join_bid"; regime_at_posting = "r05_14"; category = "ATP_MAIN"
nr2, no2, nt2 = _frag(sj, PosJoin(), 48, 0)   # _sc_target ignored on non-staircase path
chk("(5) non-staircase: new_regime from regime_lookup (unchanged)", nr2 == "r45_54")
chk("(6) non-staircase: new_offset from entry_table row (unchanged)", no2 == 7)
chk("(7) non-staircase: new_target = max(1, current_price - new_offset)", nt2 == max(1, 48 - 7))

# ---- STATIC: structure guarantees against the bug + non-staircase identity ----
print("(STATIC) source structure")
ix_reclass    = fsrc.find("# Re-classify regime and recompute")   # the recompute block (2nd staircase branch)
ix_default_nr = fsrc.find("new_regime = pos.regime_at_posting")   # unique: else uses self.regime_lookup
ix_default_no = fsrc.find("new_offset = 0")                        # unique: else uses row unpack
ix_branch     = fsrc.find('if pos.reference_source == "staircase":', ix_reclass)  # the branch AFTER the comment
ix_log        = fsrc.find('"new_regime": new_regime, "new_offset": new_offset,')
chk("(8) default new_regime between reclass-comment and its branch", 0 <= ix_reclass < ix_default_nr < ix_branch)
chk("(9) default new_offset between reclass-comment and its branch", 0 <= ix_reclass < ix_default_no < ix_branch)
chk("(10) else-branch regime_lookup assignment intact (non-staircase)", "new_regime = self.regime_lookup(pos.category, current_price)" in fsrc)
chk("(11) else-branch row unpack intact (non-staircase)", "row_pm, new_offset, _, _ = row" in fsrc)
chk("(12) v4_move_repost log reads new_regime/new_offset (now bound on all paths)", ix_log > ix_branch)

print("\nRESULT:", "ALL PASS" if not fails else "FAILURES %s" % fails)
assert not fails
