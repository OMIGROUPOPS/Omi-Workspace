#!/usr/bin/env python3
# Tests for [C-KALSHI-OCC-OBSERVE]: proves (1) byte-identical/no-op when the flag is OFF,
# (2) zero order-path / zero state-mutation when ON (pure observe), (3) correct log emission,
# (4) once-per-event. Extracts and executes the ACTUAL observe block from live_v4.py (no copy).
import ast, sys, types, re, textwrap
from datetime import datetime, timezone, timedelta

LIVE = sys.argv[1] if len(sys.argv) > 1 else "live_v4.py"
SRC = open(LIVE, encoding="utf-8", errors="replace").read()
ET = timezone(timedelta(hours=-4))
KALSHI_COARSE_MAX_FUTURE_SEC = 129600
def _kalshi_occ_start(occ, now, maxf):     # trusted separately; stubbed to its contract for this test
    return occ if (occ and 0 < (occ - now) <= maxf) else None

fails = []
def check(name, cond, msg=""):
    print(f"  {'PASS' if cond else 'FAIL'}  {name}" + (f"  -- {msg}" if (msg and not cond) else ""))
    if not cond: fails.append(name)

# ---- 1) config flag defaults OFF (byte-identical baseline) ----
check("flag_defaults_off",
      'self.kalshi_occ_observe = bool(self.config.get("kalshi_occ_observe", False))' in SRC,
      "default-False config line missing")

# ---- locate the observe block source (the `if getattr(self, "kalshi_occ_observe", False):` suite) ----
lines = SRC.splitlines()
start = next((i for i,l in enumerate(lines) if 'if getattr(self, "kalshi_occ_observe", False):' in l), None)
check("observe_block_present", start is not None)
block_src = None
if start is not None:
    indent = len(lines[start]) - len(lines[start].lstrip())
    end = start + 1
    while end < len(lines):
        l = lines[end]
        if l.strip() and (len(l) - len(l.lstrip())) <= indent: break
        end += 1
    block_src = "\n".join(lines[start:end])

# ---- 2) AST: the block only LOGS + updates guard-sets; NO state mutation, NO order path ----
if block_src:
    tree = ast.parse(textwrap.dedent(block_src))
    assigns_attr, calls = [], []
    for n in ast.walk(tree):
        if isinstance(n, ast.Assign):
            for t in n.targets:
                # flag any assignment to self.<attr> (state mutation)
                if isinstance(t, ast.Subscript) and isinstance(t.value, ast.Attribute) and isinstance(t.value.value, ast.Name) and t.value.value.id == "self":
                    assigns_attr.append(t.value.attr)
                if isinstance(t, ast.Attribute) and isinstance(t.value, ast.Name) and t.value.id == "self":
                    assigns_attr.append(t.attr)
        if isinstance(n, ast.Call):
            f = n.func
            if isinstance(f, ast.Attribute): calls.append(f.attr)
    banned_state = {"event_start_time","event_start_source","coarse_source","event_unmatched_cycles"}
    banned_calls = {"place_order","_place_order","submit_order","create_order","_submit","place","cancel_order","_post","_place","_enter","open_position"}
    check("no_state_mutation", not (set(assigns_attr) & banned_state),
          f"mutates {set(assigns_attr) & banned_state}")
    check("no_order_path", not (set(calls) & banned_calls),
          f"calls {set(calls) & banned_calls}")
    check("only_log_and_setadd", set(calls) <= {"_log","setdefault","add","get","fromtimestamp","isoformat","round","_kalshi_occ_start","get_category"},
          f"unexpected calls {set(calls) - {'_log','setdefault','add','get','fromtimestamp','isoformat','round','_kalshi_occ_start','get_category'}}")

# ---- behavioral harness: exec the REAL block against a fake self ----
class FakeSelf:
    def __init__(self, observe):
        self.kalshi_occ_observe = observe
        self.event_kalshi_occ = {}
        self.event_start_time = {}
        self.event_start_source = {}
        self.logs = []
    def get_category(self, et): return "ITF_W"
    def _log(self, ev, d=None, ticker=""): self.logs.append((ev, d or {}))

def run_block(self_obj, et, now):
    start_ts = self_obj.event_start_time.get(et)   # mirrors the real preceding line
    g = dict(datetime=datetime, ET=ET, _kalshi_occ_start=_kalshi_occ_start,
             KALSHI_COARSE_MAX_FUTURE_SEC=KALSHI_COARSE_MAX_FUTURE_SEC)
    l = dict(self=self_obj, et=et, now=now, start_ts=start_ts)
    exec(compile(textwrap.dedent(block_src), "<observe>", "exec"), g, l)

NOW = 1_800_000_000.0
# 3a) OFF -> no logs, no mutation
s = FakeSelf(observe=False); s.event_kalshi_occ["E1"]=NOW+3600
before = (dict(s.event_start_time), dict(s.event_start_source))
run_block(s, "E1", NOW)
check("off_no_logs", s.logs == [], f"emitted {s.logs}")
check("off_no_mutation", (dict(s.event_start_time),dict(s.event_start_source))==before)

# 3b) ON + primary-MISS + occ passes guard -> one kalshi_occ_observe, would_trade True, NO start set
s = FakeSelf(observe=True); s.event_kalshi_occ["E2"]=NOW+3600   # 1h future -> passes
run_block(s, "E2", NOW)
obs = [d for ev,d in s.logs if ev=="kalshi_occ_observe"]
check("on_miss_emits_observe", len(obs)==1)
check("on_miss_would_trade_true", bool(obs and obs[0].get("would_trade") is True and obs[0].get("would_resolve") is True))
check("on_miss_has_fields", bool(obs and all(k in obs[0] for k in ("event","category","occurrence_datetime","would_coarse_start","phase"))))
check("on_miss_no_start_set", "E2" not in s.event_start_time)

# 3c) ON + primary-MISS + occ STALE (past) -> would_resolve False (guard rejects), still no start
s = FakeSelf(observe=True); s.event_kalshi_occ["E3"]=NOW-3600
run_block(s, "E3", NOW)
obs = [d for ev,d in s.logs if ev=="kalshi_occ_observe"]
check("on_miss_stale_would_resolve_false", bool(obs and obs[0].get("would_resolve") is False and obs[0].get("would_trade") is False))
check("on_miss_stale_no_start", "E3" not in s.event_start_time)

# 3d) ON + RESOLVED via real source + occ present -> one kalshi_occ_delta with correct delta, no mutation
s = FakeSelf(observe=True); s.event_start_time["E4"]=NOW+1200; s.event_start_source["E4"]="tennisexplorer"; s.event_kalshi_occ["E4"]=NOW+1000
run_block(s, "E4", NOW)
dl = [d for ev,d in s.logs if ev=="kalshi_occ_delta"]
check("on_resolved_emits_delta", len(dl)==1)
check("on_resolved_delta_value", bool(dl and abs(dl[0].get("delta_sec",0)-200.0)<0.01), f"{dl}")
check("on_resolved_has_resolver_src", bool(dl and dl[0].get("resolver_source")=="tennisexplorer"))
check("on_resolved_start_unchanged", s.event_start_time["E4"]==NOW+1200)

# 3e) once-per-event: repeated cycles emit exactly one log per event
s = FakeSelf(observe=True); s.event_kalshi_occ["E5"]=NOW+3600
for _ in range(5): run_block(s, "E5", NOW)
check("once_per_event_miss", sum(1 for ev,_ in s.logs if ev=="kalshi_occ_observe")==1)
s = FakeSelf(observe=True); s.event_start_time["E6"]=NOW+600; s.event_start_source["E6"]="odds_api"; s.event_kalshi_occ["E6"]=NOW+600
for _ in range(5): run_block(s, "E6", NOW)
check("once_per_event_delta", sum(1 for ev,_ in s.logs if ev=="kalshi_occ_delta")==1)

print(f"\n{'ALL PASS' if not fails else 'FAILURES: '+', '.join(fails)}  ({0 if not fails else len(fails)} failed)")
sys.exit(1 if fails else 0)
