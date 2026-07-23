import json, sqlite3, collections, datetime as dt, statistics
ld=lambda p:[json.loads(l) for l in open(p)]
ev=ld("/srv/omi-research/window1-20260722/normalized/events.jsonl")
c=sqlite3.connect("file:/mnt/omi-trading-data-nyc3/active/tennis.db?mode=ro",uri=True)
sched={e["event_id"]: e.get("scheduled_start_exchange_ts") for e in ev}
evids=set(sched)
def ev_of(tk):  # normalize a kalshi_ticker to event_id (strip leg suffix if present)
    tk=str(tk or "")
    return tk if tk in evids else tk.rsplit("-",1)[0]
# observed_starts.first_inplay_at
obs={}
for tk,fip in c.execute("SELECT kalshi_ticker, first_inplay_at FROM observed_starts WHERE first_inplay_at IS NOT NULL"):
    e=ev_of(tk)
    if e in evids and (e not in obs): obs[e]=fip
# live_scores onset = MIN(last_updated) per kalshi_ticker
ons={}
for tk,mn in c.execute("SELECT kalshi_ticker, MIN(last_updated) FROM live_scores GROUP BY kalshi_ticker"):
    e=ev_of(tk)
    if e in evids and mn is not None and e not in ons: ons[e]=mn
print("sample observed_starts kalshi_ticker:", c.execute("SELECT kalshi_ticker,first_inplay_at FROM observed_starts LIMIT 1").fetchone())
print("=== REAL-START SOURCE COVERAGE (of 804) ===")
print("  observed_starts.first_inplay_at : %d/804"%sum(1 for e in evids if e in obs))
print("  live_scores onset               : %d/804"%sum(1 for e in evids if e in ons))
print("  either (recoverable real start) : %d/804"%sum(1 for e in evids if e in obs or e in ons))
def parse(v):
    if v in (None,""): return None
    try: return float(v)
    except:
        try: return dt.datetime.fromisoformat(str(v).replace("Z","+00:00")).timestamp()
        except: return None
deltas=[]; big=[]
for e in evids:
    sc=parse(sched.get(e)); rs=parse(obs.get(e)) or parse(ons.get(e))
    if sc is not None and rs is not None:
        d=(rs-sc)/60.0; deltas.append((e,d))
print("=== real_start - scheduled (minutes) ===")
if deltas:
    ds=sorted(x[1] for x in deltas)
    print("  n=%d  p10=%.1f p50=%.1f p90=%.1f  min=%.1f max=%.1f"%(len(ds),ds[int(len(ds)*.1)],statistics.median(ds),ds[int(len(ds)*.9)],ds[0],ds[-1]))
    print("  |delta|>15min: %d/%d (%.1f%%)  |delta|>60min: %d  earlier-than-sched(<-15): %d"%(
        sum(1 for _,d in deltas if abs(d)>15),len(deltas),100*sum(1 for _,d in deltas if abs(d)>15)/len(deltas),
        sum(1 for _,d in deltas if abs(d)>60), sum(1 for _,d in deltas if d<-15)))
print("=== BENCHMARK SUBSTITUTION GAP ===")
recov=sum(1 for e in evids if e in obs or e in ons)
print("  benchmark used verified start: 40/804 -> 764 schedule-only")
print("  BUT recoverable real start exists for %d/804 -> %d substitutions were AVOIDABLE"%(recov,max(0,recov-40)))
