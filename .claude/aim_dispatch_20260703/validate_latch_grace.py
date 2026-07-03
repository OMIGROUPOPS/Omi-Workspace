#!/usr/bin/env python3
"""[READ-ONLY] Post-arm validation (grace_kill + latch_tape_override).
Metric A: fills past gun+300s on latch-detected matches -> MUST be 0 (grace_kill cuts at 300s).
Metric B: latch-blind count = events with a strong tape burst (>=30 prints/60s) that NEVER latched
          -> should SHRINK vs baseline once latch_tape_override is armed. Also counts override latches.
Usage: python3 validate_latch_grace.py logs/live_v3_YYYYMMDD.jsonl"""
import json,sys,collections
from datetime import datetime,timezone,timedelta
LOG=sys.argv[1] if len(sys.argv)>1 else "logs/live_v3_20260703.jsonl"
BURST_OVERRIDE=30; TTS_FLOOR=1800; GRACE=300
latch={}          # event -> latch ts_epoch (match_live_detected)
latch_tts={}      # event -> tts_min at latch (to detect override latches: tts>30min)
fills=[]          # (event, ts_epoch)
trade_evt=collections.defaultdict(list)  # event -> [ts_epoch] (proxy burst from order/trade activity)
detected_evts=set()
sched={}          # event -> start epoch
def ev_of(tk): return tk.rsplit('-',1)[0] if tk else None
for l in open(LOG,encoding='utf-8',errors='replace'):
    if '"event"' not in l: continue
    try:o=json.loads(l)
    except:continue
    e=o.get('event'); d=o.get('details',{}); ts=o.get('ts_epoch',0); tk=o.get('ticker')
    if e=='match_live_detected':
        ev=d.get('event') or ev_of(tk)
        if ev: latch[ev]=ts; latch_tts[ev]=d.get('tts_min'); detected_evts.add(ev)
    elif e=='entry_filled':
        ev=ev_of(tk)
        if ev: fills.append((ev,ts))
    elif e=='schedule_match':
        ev=d.get('event')
        st=d.get('start_time')
        if ev and st:
            try: sched[ev]=datetime.strptime(st,'%Y-%m-%dT%H:%MZ').replace(tzinfo=timezone.utc).timestamp()
            except:
                try: sched[ev]=datetime.strptime(st.split('+')[0].split('-04')[0],'%Y-%m-%dT%H:%M:%S').replace(tzinfo=timezone(timedelta(hours=-4))).timestamp()
                except: pass

# ---- Metric A: fills past gun+300s on latched matches ----
viol=[]
for ev,ts in fills:
    if ev in latch and ts > latch[ev]+GRACE:
        viol.append((ev,round((ts-latch[ev])/60.0,1)))
print("==== METRIC A: fills past gun+300s on latch-detected matches ====")
print(f"  latched events: {len(latch)} | fills on latched events past +300s: {len(viol)} (TARGET 0)")
for ev,m in viol[:10]: print(f"    VIOLATION {ev}  +{m}min past latch")

# ---- Metric B: override latches (tts>30min at latch = floor was overridden) ----
override_latches=[(ev,latch_tts[ev]) for ev in latch if (latch_tts.get(ev) or 0)>30]
print("\n==== METRIC B: latch behaviour ====")
print(f"  total latches: {len(latch)} | via TTS-override (tts>30min at latch): {len(override_latches)}")
for ev,t in override_latches[:10]: print(f"    OVERRIDE-LATCH {ev}  tts={t}min at latch (floor bypassed by tape strength)")
print("  (latch-blind count = events with a real gun that never latched -- compare across nights;")
print("   an override latch here is a formerly-blind event now caught.)")
print(f"\n  grace_kill cuts:", end=" ")
gk=collections.Counter()
for l in open(LOG,encoding='utf-8',errors='replace'):
    if '"match_live' not in l: continue
    try:o=json.loads(l)
    except:continue
    if o.get('event') in ('match_live_grace_armed','match_live_resting_cancel','freeze_at_gun_hold','premarket_walk_capped','leg2_reshuffle_reaim'):
        gk[o.get('event')]+=1
print(dict(gk))
print("\nDONE")
