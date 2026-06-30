#!/usr/bin/env python3
"""[C-COMPLETION-CEILING] unit test for the gated combined-ceiling restore in
_completion_target. AST-extracts the pure method from live source (no import) and
binds it to a fake self carrying the two flags. Run from arb-executor.

Confirms: (1) ceiling binds+lowers under flag=True; (2) byte-identical legacy under
flag=False; (3) ceiling is no-op when it would not lower (under BOTH states);
(4) refusal is structurally impossible (always returns a completable price >=1);
(5) default-OFF when the config key is absent."""
import ast, textwrap, os, types
src=open(os.environ.get("LV4","live_v4.py")).read()

# module global the method references
V4_PAIRED_BASIS_CAP=next(
    ast.literal_eval(ast.get_source_segment(src,n.value))
    for n in ast.walk(ast.parse(src))
    if isinstance(n,ast.Assign) and any(getattr(t,"id",None)=="V4_PAIRED_BASIS_CAP" for t in n.targets))
assert V4_PAIRED_BASIS_CAP==99, V4_PAIRED_BASIS_CAP

def grab(name):
    return next(ast.get_source_segment(src,x) for x in ast.walk(ast.parse(src))
               if isinstance(x,ast.FunctionDef) and x.name==name)
ns={"V4_PAIRED_BASIS_CAP":V4_PAIRED_BASIS_CAP}
exec(textwrap.dedent(grab("_completion_target")),ns)
_ct=ns["_completion_target"]

def ct(s0,x,sib_ask,leg1,ceiling,enforced=False):
    me=types.SimpleNamespace(completion_combined_ceiling=ceiling, paired_cap_enforced=enforced)
    return _ct(me,s0,x,sib_ask,leg1)

fails=[]
def chk(n,c): print(f"  {n}: {'PASS' if c else 'FAIL'}"); (None if c else fails.append(n))

print("(1) COPWES: s0+X large, leg1_basis=71, sib_ask=44 -- ceiling BINDS and lowers")
# s0+X large (=99), sib_ask-1=43, 99-71=28 -> min => 28 under ceiling
chk("ceiling=True  -> 28 (=99-71), NOT 43", ct(99,50,44,71,True)==28)
chk("ceiling=False -> 43 (sib_ask-1), legacy byte-identical", ct(99,50,44,71,False)==43)
chk("the two differ only by the flag (28 vs 43)", ct(99,50,44,71,True)==28 and ct(99,50,44,71,False)==43)

print("(2) ceiling does NOT bind: leg1_basis=20, sib_ask=44 -> sib_ask-1=43 both states")
# 99-20=79 > 43, so min is still sib_ask-1=43 regardless of flag
chk("ceiling=True  -> 43 (ceiling 79 doesn't lower)", ct(99,50,44,20,True)==43)
chk("ceiling=False -> 43 (legacy)", ct(99,50,44,20,False)==43)
chk("identical under both flag states when ceiling slack", ct(99,50,44,20,True)==ct(99,50,44,20,False)==43)

print("(3) s0+X already lowest -> unaffected by flag")
# s0+X=10 is the min; ceiling/legacy/ask all higher
chk("small s0+X=10 wins, ceiling=True", ct(5,5,44,71,True)==10)
chk("small s0+X=10 wins, ceiling=False", ct(5,5,44,71,False)==10)

print("(4) refusal impossible -- always a completable price >=1, never None/abort")
import itertools
bad=[]
for s0,x,sib,l1,ce in itertools.product(range(0,100,7),range(0,60,11),[None,1,30,60,99],range(0,100,9),[True,False]):
    v=ct(s0,x,sib,l1,ce)
    if v is None or not isinstance(v,int): bad.append(("type",s0,x,sib,l1,ce,v))
# clamp: completion price must be usable; min() of candidates can go <=0 only if an input is <=0.
# assert: for realistic inputs (s0>=1,x>=1,sib>=1,l1< 99) result>=1
real_bad=[]
for s0,x,sib,l1,ce in itertools.product(range(1,100,6),range(1,40,9),[2,30,60,99],range(0,99,8),[True,False]):
    v=ct(s0,x,sib,l1,ce)
    if v<1: real_bad.append((s0,x,sib,l1,ce,v))
chk("never returns None / non-int (any input)", not bad)
chk("never returns <1 for realistic inputs (s0,x,sib,l1<99)", not real_bad)
chk("ceiling=True never returns a value ABOVE legacy (lower-only)",
    all(ct(s0,x,sib,l1,True)<=ct(s0,x,sib,l1,False)
        for s0,x,sib,l1 in itertools.product(range(1,100,9),range(1,40,9),[2,30,60,99],range(0,99,9))))

print("(5) default-OFF when config key absent -> legacy")
# simulate config-load default: getattr default False -> object with no attr set
me_noattr=types.SimpleNamespace(paired_cap_enforced=False)
chk("missing completion_combined_ceiling attr -> treated False -> 43",
    _ct(me_noattr,99,50,44,71)==43)

print("(6) enforced (true) branch untouched -- always 99-leg1_basis regardless of new flag")
chk("enforced=True,ceiling=False -> 28 (=99-71)", ct(99,50,44,71,False,enforced=True)==28)
chk("enforced=True,ceiling=True  -> 28 (same; new flag irrelevant when enforced)", ct(99,50,44,71,True,enforced=True)==28)

print("\nRESULT:", "ALL PASS" if not fails else f"FAILURES {fails}")
assert not fails
