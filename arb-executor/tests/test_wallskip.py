#!/usr/bin/env python3
"""STEP 3 test for [C-WALL-SKIP]. Uses the REAL LiveV3._wall_skip_pair + real Book class."""
import live_v4
from live_v4 import LiveV3, Book

def make_bot(threshold=10000, enforce=True):
    bot = object.__new__(LiveV3)              # skip heavy __init__
    bot.wall_skip_contracts = threshold
    bot.wall_skip_enforce = enforce
    bot.books = {}
    return bot

ET = "KXATPMATCH-26JUN26DRAHUM"
LEG_A = ET + "-DRA"
LEG_B = ET + "-HUM"

def case(name, qa, qb, threshold=10000):
    bot = make_bot(threshold)
    bot.books[LEG_A] = Book(bids={64: qa}, best_bid=64)
    bot.books[LEG_B] = Book(bids={36: qb}, best_bid=36)
    skip, q, tk = bot._wall_skip_pair(ET, [LEG_A, LEG_B])
    print(f"  {name:52s} qa={qa:6d} qb={qb:6d} -> skip={skip!s:5s} maxq={q:6d} worst={tk[-3:] if tk else '-'}")
    return skip, q, tk

print("=== ON (enforce=True), threshold=10000 ===")
r1 = case("both thin  -> BOTH POST (skip False)",            500,   800)
r2 = case("leg A walled -> SKIP BOTH (no naked single)",   17353,  800)
r3 = case("leg B walled -> SKIP BOTH (either-leg, symmetric)", 500, 15623)
r4 = case("both walled -> SKIP BOTH (whole game missed)",  12000, 11000)
r5 = case("exactly AT bar (10000) -> not > bar -> POST",   10000,  900)
r6 = case("one tick over bar (10001) -> SKIP",             10001,  900)

print("\n=== assertions ===")
ok = True
def chk(label, cond):
    global ok
    print(f"  [{'PASS' if cond else 'FAIL'}] {label}"); ok = ok and cond
chk("both thin -> skip False (both legs post)",            r1[0] is False)
chk("leg A walled -> skip True (both skipped)",            r2[0] is True and r2[2]==LEG_A)
chk("leg B walled -> skip True (either-leg works)",        r3[0] is True and r3[2]==LEG_B)
chk("both walled -> skip True",                            r4[0] is True)
chk("AT threshold (==bar) -> skip False (strict >)",       r5[0] is False)
chk("one over threshold -> skip True",                     r6[0] is True)

# purity: helper must not mutate book/state
bot = make_bot(); bot.books[LEG_A]=Book(bids={64:50000},best_bid=64); bot.books[LEG_B]=Book(bids={36:10},best_bid=36)
before = (dict(bot.books[LEG_A].bids), dict(bot.books[LEG_B].bids), bot.books[LEG_A].best_bid)
bot._wall_skip_pair(ET,[LEG_A,LEG_B])
after = (dict(bot.books[LEG_A].bids), dict(bot.books[LEG_B].bids), bot.books[LEG_A].best_bid)
chk("helper is read-only (no book/state mutation)", before==after)

# missing-book robustness (in-window event before book populated)
bot = make_bot(); bot.books[LEG_A]=Book(bids={},best_bid=0)  # empty book, no B at all
skip,_,_ = bot._wall_skip_pair(ET,[LEG_A,LEG_B])
chk("empty/absent books -> no false skip (fail-open)", skip is False)

print("\nRESULT:", "ALL PASS" if ok else "FAILURES PRESENT")
import sys; sys.exit(0 if ok else 1)
