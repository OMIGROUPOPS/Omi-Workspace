#!/usr/bin/env python3
"""[C-ORDER-V2] unit test for the create-order-v2 payload builder + flat-response parser. AST-extracts
the two pure module-level helpers from the live source (no import). Run from arb-executor."""
import ast, textwrap, os
src=open(os.environ.get("LV4","live_v4.py")).read()
def grab(n): return next(ast.get_source_segment(src,x) for x in ast.walk(ast.parse(src)) if isinstance(x,ast.FunctionDef) and x.name==n)
ns={}
exec(textwrap.dedent(grab("build_order_payload_v2")),ns)
exec(textwrap.dedent(grab("parse_order_response_v2")),ns)
B=ns["build_order_payload_v2"]; P=ns["parse_order_response_v2"]
fails=[]
def chk(n,c): print(f"  {n}: {'PASS' if c else 'FAIL'}"); (None if c else fails.append(n))

print("(1) build_order_payload_v2 -- request mapping")
b=B("KXWTAMATCH-26JUN19PEGKEY-PEG","buy",57,5,True,"coid-1")
chk("buy -> side bid", b["side"]=="bid")
chk("count int 5 -> str '5'", b["count"]=="5" and isinstance(b["count"],str))
chk("price 57c -> '0.57'", b["price"]=="0.57")
chk("post_only=True -> time_in_force GTC", b["time_in_force"]=="good_till_canceled")
chk("self_trade_prevention_type taker_at_cross", b["self_trade_prevention_type"]=="taker_at_cross")
chk("post_only preserved (bool True)", b["post_only"] is True)
chk("client_order_id preserved", b["client_order_id"]=="coid-1")
chk("ticker preserved", b["ticker"]=="KXWTAMATCH-26JUN19PEGKEY-PEG")
chk("NO legacy keys (action/yes_price/type)", all(k not in b for k in ("action","yes_price","type")))
chk("sell -> side ask", B("t","sell",42,5,True,"c")["side"]=="ask")
chk("price 5c -> '0.05'", B("t","buy",5,5,True,"c")["price"]=="0.05")
chk("price 99c -> '0.99'", B("t","buy",99,5,True,"c")["price"]=="0.99")
chk("count 10 -> '10'", B("t","buy",50,10,True,"c")["count"]=="10")
chk("not post_only -> time_in_force IOC", B("t","buy",57,5,False,"c")["time_in_force"]=="immediate_or_cancel")
chk("post_only=False preserved", B("t","buy",57,5,False,"c")["post_only"] is False)

print("(2) parse_order_response_v2 -- flat response")
oid,st,fc,avg=P({"order_id":"abc","remaining_count":"0","fill_count":"5","average_fill_price":"0.57"})
chk("filled: order_id direct", oid=="abc")
chk("filled: status (remaining 0 -> filled)", st=="filled")
chk("filled: fill_count parsed", fc==5)
chk("filled: avg_fill_price 0.57 -> 57c", avg==57)
oid,st,fc,avg=P({"order_id":"x","remaining_count":"5","fill_count":"0"})
chk("resting: status (remaining>0 -> resting)", st=="resting")
chk("resting: fill_count 0", fc==0)
chk("resting: avg None", avg is None)
oid,st,fc,avg=P({"order_id":"y","remaining_count":"3","fill_count":"2","average_fill_price":"0.40"})
chk("partial: status resting", st=="resting")
chk("partial: fill_count 2", fc==2)
chk("partial: avg 0.40 -> 40c", avg==40)
oid,st,fc,avg=P({"order_id":"z","fill_count":"0"})
chk("missing remaining_count -> resting (safe)", st=="resting")
chk("non-dict -> empty tuple", P(None)==("","?",0,None))
oid,_,_,_=P({"order":{"order_id":"legacy"}})
chk("legacy wrapper resp -> empty oid (expects FLAT)", oid=="")

print("\nRESULT:", "ALL PASS" if not fails else f"FAILURES {fails}")
assert not fails
