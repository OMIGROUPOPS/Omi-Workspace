#!/usr/bin/env python3
# FIX-1 TRACE (READ-ONLY): per-repost best-bid vs computed re-join target vs actual landing.
# Separates (b) depth-roll-below-touch  vs  (d) re-joined-at-touch-but-touch-moved-no-refire.
import json,glob,csv,os,datetime,bisect
TICK="/root/Omi-Workspace/arb-executor/analysis/premarket_ticks"
LEGS=["KXATPCHALLENGERMATCH-26JUN25CREMCD-CRE","KXATPCHALLENGERMATCH-26JUN25MICMON-MON",
      "KXATPCHALLENGERMATCH-26JUN25CREMCD-MCD","KXATPCHALLENGERMATCH-26JUN25MICMON-MIC",
      "KXATPCHALLENGERMATCH-26JUN23MIGSEY-MIG"]
def unixep(s):  # premarket_ticks ts "2026-06-25 03:37:39 PM" -> unix epoch (VPS local = ET)
    try: return datetime.datetime.strptime(s,"%Y-%m-%d %I:%M:%S %p").timestamp()
    except: return None
def load_ticks(tk):
    arr=[]
    p=os.path.join(TICK,tk+".csv")
    if not os.path.exists(p): return arr
    for r in csv.DictReader(open(p)):
        t=unixep(r["ts_et"])
        if t is None: continue
        try: arr.append((t,int(r["bid_1"] or 0),int(r["ask_1"] or 100),int(r["bid_1_sz"] or 0)))
        except: continue
    arr.sort(); return arr
def book_at(arr,t):
    if not arr: return (0,100,0)
    i=bisect.bisect_right([x[0] for x in arr],t)-1
    if i<0: i=0
    return (arr[i][1],arr[i][2],arr[i][3])
rows=[]
for f in sorted(glob.glob("/root/Omi-Workspace/arb-executor/logs/live_v3_2026062[3456].jsonl")):
    for l in open(f):
        try: rows.append(json.loads(l))
        except: pass
def ev(d):return d.get("event")
def D(d):return d.get("details",{})
byleg={tk:[] for tk in LEGS}
for d in rows:
    tk=d.get("ticker","")
    if tk in byleg and ev(d) in ("order_placed","v4_move_repost","order_cancelled","match_live_resting_cancel","staircase_hold_place"):
        byleg[tk].append(d)

tot_b=tot_d=0; cents_b=cents_d=0
for tk in LEGS:
    arr=load_ticks(tk)
    evs=sorted(byleg[tk],key=lambda d:d.get("ts_epoch",0))
    print(f"\n=== {tk[-22:]} ===  (ticks={len(arr)})")
    last_landing=None
    for d in evs:
        E=ev(d); x=D(d); t=d.get("ts_epoch",0); te=d.get("ts","")[11:22]
        bid,ask,sz=book_at(arr,t)
        if E=="order_placed" and x.get("action")=="buy":
            land=x.get("price"); last_landing=land
            tag = "AT-touch" if (land is not None and land>=bid) else f"BELOW touch by {bid-land if land else '?'}"
            print(f"  {te} order_placed   land={land:>3} | book bid={bid} ask={ask} sz={sz}  -> {tag}")
        elif E=="v4_move_repost":
            nt=x.get("new_target"); ca=x.get("current_ask"); cp=x.get("current_price"); mv=x.get("move_cents")
            # computed target vs touch at this instant
            roll = (bid - nt) if (nt is not None and bid) else None
            cause = "(b) DEPTH-ROLL below touch" if (roll is not None and roll>=2) else "(d) computed AT touch"
            print(f"  {te} MOVE_REPOST    new_target={nt} current_ask={ca} move_cents={mv} | book bid={bid} ask={ask} sz={sz} -> roll={roll} {cause}")
        elif E in ("order_cancelled","match_live_resting_cancel"):
            print(f"  {te} {E}  | book bid={bid}")
        elif E=="staircase_hold_place":
            print(f"  {te} staircase_hold_place bid={x.get('bid')} target={x.get('target')}")
    bg=arr[-1][1] if arr else None
    print(f"  FINAL: best-bid@gun={bg}  our_last_landing={last_landing}  stranded_by={bg-last_landing if (bg and last_landing) else '?'}")
print("\nNOTE: (b) = new_target computed >=2c below best-bid at that instant (depth_aware_join rolled off the thin touch).")
print("      (d) = re-join computed AT/above touch, but the touch later moved and no further repost fired (cadence).")
print("Per-repost classification above; ranked summary follows from the printed causes.")
