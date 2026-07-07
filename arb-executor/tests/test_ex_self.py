#!/usr/bin/env python3
"""[C-EX-SELF] unit tests: _book_ex_self + _express_target extracted from live_v4.py
(AST real-body extraction, the house pattern) and driven against the same cases the
spread-recount engine reconstructs — one source of truth for the non-self math."""
import ast, sys, types
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "live_v4.py"
tree = ast.parse(SRC.read_text(encoding="utf-8"))
fns = {}
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name in ("_book_ex_self", "_express_target"):
        mod = ast.Module(body=[node], type_ignores=[])
        ns = {}
        exec(compile(mod, "<extract>", "exec"), ns)
        fns[node.name] = ns[node.name]
assert set(fns) == {"_book_ex_self", "_express_target"}, "extraction failed"

class Book:
    def __init__(self, bids, ask):
        self.bids = bids; self.best_ask = ask
        self.best_bid = max(bids) if bids else 0
class Pos:
    def __init__(self, px, phase="entry_resting", oid="x"):
        self.entry_price = px; self.phase = phase; self.entry_order_id = oid
class Bot:
    def __init__(self, book, pos=None, flag=True):
        self.books = {"TK": book}; self.positions = {"TK": pos} if pos else {}
        self.entry_size = 5; self.expression_invariant = flag
        self.logged = []
    def _log(self, ev, d, ticker=None): self.logged.append((ev, d))
Bot._book_ex_self = fns["_book_ex_self"]
Bot._express_target = fns["_express_target"]

P = F = 0
def chk(name, cond):
    global P, F
    print(("  [PASS] " if cond else "  [FAIL] ") + name)
    P += cond; F += (not cond)

# 1. no own order -> identity
b = Bot(Book({60: 100, 58: 40}, 65))
chk("no-own: bid stays 60", b._book_ex_self("TK") == (60, 65))
# 2. own alone at top (size == ours) -> falls to next real level (the recount case)
b = Bot(Book({60: 5, 58: 40}, 65), Pos(60))
chk("own-alone-top: falls to 58", b._book_ex_self("TK") == (58, 65))
# 3. own shares the top level with others -> level survives
b = Bot(Book({60: 25, 58: 40}, 65), Pos(60))
chk("shared-level: stays 60", b._book_ex_self("TK") == (60, 65))
# 4. own alone at top AND next level -> double fall-through
b = Bot(Book({60: 5, 58: 4, 55: 10}, 65), Pos(60))
chk("thin-next: 58(4)<no own there stays 58", b._book_ex_self("TK") == (58, 65))
# 5. own everywhere it can be counted once only (single entry order)
b = Bot(Book({60: 5}, 65), Pos(60))
chk("only-our-level: empty book -> None", b._book_ex_self("TK") == (None, 65))
# 6. express: target below chain -> untouched
b = Bot(Book({60: 100}, 65))
chk("express: deep rest untouched", b._express_target("TK", 55, "t") == 55)
# 7. express: join allowed", target == bid_ex+0/+1 untouched
chk("express: join untouched", b._express_target("TK", 60, "t") == 60)
chk("express: improve1 untouched", b._express_target("TK", 61, "t") == 61)
# 8. express: above chain -> clamped to bid_ex+1 (the walk-reflection killer)
chk("express: 68 -> 61", b._express_target("TK", 68, "t") == 61)
# 9. express vs OWN reflection: book top is our own order -> clamp vs the REAL chain
b = Bot(Book({70: 5, 62: 30}, 80), Pos(70))
chk("express: walk above own 70 clamps to 63 (real chain 62)", b._express_target("TK", 71, "t") == 63)
# 10. flag OFF -> byte-identical
b = Bot(Book({60: 100}, 65), flag=False)
chk("flag OFF: 68 stays 68", b._express_target("TK", 68, "t") == 68)

print(f"\nRESULT: {'ALL PASS' if F == 0 else f'{F} FAILED'} ({P} passed)")
sys.exit(1 if F else 0)
