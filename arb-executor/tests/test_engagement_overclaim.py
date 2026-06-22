#!/usr/bin/env python3
"""[C-ENGAGEMENT-OVERCLAIM] regression test for the no_trade/stale routing gate. With band_gating=OFF
the engagement router claims staircase-eligible cells that aren't real engagement cells for the leg's
actual bucket/regime; the fix re-routes those to the walking staircase (overpay fix), while real
engagement cells stay. Tests the gate against the REAL pure helpers (_engagement_bucket, regime_lookup,
AST-extracted) and the REAL tables (engagement_cells_v1.csv, range_final_*.csv). Run from arb-executor."""
import ast, textwrap, os, csv, json
src = open(os.environ.get("LV4", "live_v4.py")).read()
tree = ast.parse(src)
# --- extract the two PURE helpers the gate uses ---
def extract(name):
    seg = next(ast.get_source_segment(src, n) for n in ast.walk(tree)
               if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == name)
    ns = {}; exec(textwrap.dedent(seg), ns); fn = ns[name]
    return lambda *a, **k: fn(None, *a, **k)   # bind a dummy self
_engagement_bucket = extract("_engagement_bucket")
regime_lookup = extract("regime_lookup")
# --- load the REAL tables (same files the bot loads) ---
EC = set((r["category"], r["bucket"], r["band"]) for r in csv.DictReader(open("docs/policy/engagement_cells_v1.csv")))
RF = {cat: set(int(r["c"]) for r in csv.DictReader(open("docs/policy/range_final_%s.csv" % cat)))
      for cat in ("ATP_MAIN", "WTA_MAIN", "ATP_CHALL", "WTA_CHALL")}

# --- the gate, EXACTLY as the diff (cat, ej, tts_sec) -> "staircase" | "engagement" ---
def route(cat, ej, tts_sec):
    ej_reg = regime_lookup(cat, ej)
    ej_bkt = _engagement_bucket(tts_sec)
    real_eng = (cat, ej_bkt, ej_reg) in EC
    stair_ok = (cat in RF) and (int(ej) in RF[cat])
    return "staircase" if (stair_ok and not real_eng) else "engagement"

fails = []
def chk(name, cond): print("  %s: %s" % (name, "PASS" if cond else "FAIL")); (None if cond else fails.append(name))

T240 = 239 * 60   # tts_sec in the T240_T60 bucket
print("(1) Barrientos-class -> STAIRCASE ; real engagement-cell -> ENGAGEMENT")
chk("(a) ANDBAR-BAR  ATP_CHALL ej=44 (r35_44,T240) -> staircase", route("ATP_CHALL", 44, T240) == "staircase")
chk("(b) ANDBAR-AND  ATP_CHALL ej=54 (r45_54,T240) -> staircase", route("ATP_CHALL", 54, T240) == "staircase")
chk("(c) GUNMAK-MAK  ATP_CHALL ej=70 (r65_74,T240) -> staircase (the +30 overpay leg)", route("ATP_CHALL", 70, T240) == "staircase")
chk("(d) VIDAKS-VID  WTA_CHALL ej=71 (r65_74,T240) -> staircase", route("WTA_CHALL", 71, T240) == "staircase")
chk("(e) GUNMAK-GUN  ATP_CHALL ej=30 (r25_34,T240) -> ENGAGEMENT (real cell, stays)", route("ATP_CHALL", 30, T240) == "engagement")
chk("(f) BENRUB-RUB  ATP_CHALL ej=77 (r75_84,T240) -> ENGAGEMENT (real cell, stays)", route("ATP_CHALL", 77, T240) == "engagement")
chk("(g) sanity: ej=44 IS staircase-eligible (in range_final)", 44 in RF["ATP_CHALL"])
chk("(h) sanity: (ATP_CHALL,T240_T60,r35_44) NOT a real engagement cell", ("ATP_CHALL", "T240_T60", "r35_44") not in EC)
chk("(i) sanity: (ATP_CHALL,T240_T60,r25_34) IS a real engagement cell", ("ATP_CHALL", "T240_T60", "r25_34") in EC)

# (2) re-run today's split against the REAL gate -> 10 reroute / 33 stay
print("(2) today's engagement_wave1 v4_place split (must be 10 reroute / 33 stay)")
n_total = n_stair = n_eng = 0
log = "logs/live_v3_20260620.jsonl"
if os.path.exists(log):
    for line in open(log):
        if '"v4_place"' not in line or "2026-06-21" not in line: continue
        try: d = json.loads(line)
        except: continue
        x = d.get("details", {})
        if x.get("table_src") != "engagement_wave1": continue
        n_total += 1
        r = route(x.get("cat"), int(x.get("cell") or 0), (x.get("min_before_start") or 0) * 60)
        if r == "staircase": n_stair += 1
        else: n_eng += 1
    print("   total=%d reroute->staircase=%d stay->engagement=%d" % (n_total, n_stair, n_eng))
    chk("(2) split is 10 reroute / 33 stay (43 total)", n_total == 43 and n_stair == 10 and n_eng == 33)
else:
    print("   (log absent -- skipping live-split assertion)")

# (3) STATIC: the routing block carries the gate (ties test to real code)
print("(3) static: routing block contains the gate")
chk("(3a) 'no_trade_staircase' branch present", '"no_trade_staircase"' in src)
chk("(3b) gate predicate present", "_stair_ok and not _real_eng" in src)
chk("(3c) real-engagement membership check present", "(cat, _ej_bkt, _ej_reg) in self.engagement_cells" in src)
chk("(3d) staircase-eligible check present", "int(_ej) in self._range_final[cat]" in src)

print("\nRESULT:", "ALL PASS" if not fails else "FAILURES %s" % fails)
assert not fails
