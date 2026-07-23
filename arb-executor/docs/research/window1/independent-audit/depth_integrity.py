import json, collections, sqlite3
N="/srv/omi-research/window1-20260722/normalized"
ld=lambda p:[json.loads(l) for l in open(p)]
ev=ld(N+"/events.jsonl"); fills=ld(N+"/fills.jsonl")
print("=== DEPTH/PRINTS ARCHIVE PRESENCE (frozen normalized) ===")
import os
for f in ("books.jsonl","prints.jsonl"):
    p=N+"/"+f
    n=sum(1 for _ in open(p)) if os.path.exists(p) else "ABSENT"
    print("  %-14s: %s rows"%(f,n))
# tennis.db book_prices coverage for Window-1 (BBO substitute)
try:
    c=sqlite3.connect("file:/mnt/omi-trading-data-nyc3/active/tennis.db?mode=ro",uri=True)
    cols=[r[1] for r in c.execute("PRAGMA table_info(book_prices)")]
    print("=== tennis.db book_prices cols ===",cols[:16])
    # window-1 tickers
    wt=set()
    for e in ev:
        for L in e.get("legs") or []:
            if isinstance(L,dict) and L.get("ticker"): wt.add(L["ticker"])
    # sample: how many window-1 tickers have any book_prices row?
    have=0; checked=0
    for t in list(wt)[:120]:
        checked+=1
        r=c.execute("SELECT 1 FROM book_prices WHERE ticker=? LIMIT 1",(t,)).fetchone()
        if r: have+=1
    print("  book_prices coverage on 120 sampled W1 leg-tickers: %d/%d"%(have,checked))
    # does book_prices carry full depth (ladder) or only BBO?
    depthcols=[x for x in cols if "depth" in x.lower() or "ladder" in x.lower() or "size" in x.lower() or "bid" in x.lower() or "ask" in x.lower()]
    print("  book_prices depth-ish cols:",depthcols)
except Exception as e:
    print("book_prices probe err:",e)
print("=== FILL INTEGRITY (falsification) ===")
qs=[float(f.get("quantity") or 0) for f in fills]
print("  fills n=%d | zero/negative size: %d | min_qty=%s | fill_id unique: %d/%d"%(
    len(fills), sum(1 for q in qs if q<=0), min(qs), len(set(str(f.get("fill_id")) for f in fills)), len(fills)))
# Yes/No complementary double-count: are both legs of a game ever filled by the SAME fill_id/trade? (should not)
by_trade=collections.defaultdict(set)
for f in fills: by_trade[str(f.get("trade_id"))].add(str(f.get("ticker")))
cross=sum(1 for t,tks in by_trade.items() if len(tks)>1)
print("  trade_ids whose fills span >1 ticker (potential cross-leg):",cross)
# price sanity 1..99
print("  fills price out of [1,99]:",sum(1 for f in fills if not (1<=int(f.get('price_cents') or 0)<=99)))
print("=== VERIFIED REAL START vs SCHEDULE SUBSTITUTION ===")
src=ld("/mnt/omi-trading-data-nyc3/private-evidence/window1-20260722/joined/orders.jsonl")
es=collections.Counter(str(o.get("evaluation_end_source")) for o in src)
print("  evaluation_end_source dist (orders):",dict(es))
# events with verified start
vs=sum(1 for e in ev if e.get("schedule_source"))
print("  events schedule_source dist:",dict(collections.Counter(str(e.get("schedule_source")) for e in ev)))
