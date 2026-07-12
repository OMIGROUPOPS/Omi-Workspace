# NIGHTLY PASS — the week's standing analysis (run every morning, push everything)

From `/root/Omi-Workspace/arb-executor` on the VPS. Log = the current session's
`logs/live_v3_YYYYMMDD.jsonl` (+ previous night's file for the full window).

```bash
# 1. Standing ledger pass: chains + exchange truth (edit EVENTS list to the night's slate,
#    or extend causal_audit.py to auto-discover from entry_filled/window_open events)
python3 ../.claude/live_20260705/audit/causal_audit.py          # -> /tmp/causal_audit.json

# 2. Grades + stamps: the monitor's live_validation.jsonl already carries per-fill
#    stamp/chain/Δaim rows (EARNED/GIFT_CLASS/MIXED); A-F letter grades via
#    ../.claude/overnight_20260705/on3_ledger.py + grade2.py when a full window closes.

# 3. THE LEAK DECOMPOSITION (appends to week_leak.jsonl, deduped by date+event)
python3 ../.claude/live_20260705/audit/leak_decomposition.py \
    logs/live_v3_<prev>.jsonl logs/live_v3_<today>.jsonl

# 4. Evidence-stream counters
grep -c 'bid_grade' ../.claude/live_20260705/live_validation.jsonl   # repriceable stream
python3 - <<'EOF'
# fv_observe riser accumulation vs the ~100 target
import json,glob
n=0
for lp in sorted(glob.glob('logs/live_v3_*.jsonl'))[-7:]:
    for l in open(lp,encoding='utf-8',errors='replace'):
        if 'fv_burst_anchor' in l and '"event"' in l:
            o=json.loads(l)
            if (o['details'].get('entry_price') or 0)>=50 and o['details'].get('fv_mid') is not None: n+=1
print('fv-graded riser legs to date:',n,'/ ~100 target')
EOF

# 5. Commit + push (the monitor auto-commits .claude/live_20260705/; for the rest:)
cd /root/Omi-Workspace && git add .claude/live_20260705/ && git commit -m "nightly pass <date>" && git push origin blend/kalshi-occ-fallback
```

Pass bars each night: zero-tolerance board clean (or same-day patch through the gate —
defects are exempt from the config hold); leak table updated; counters reported.

## W1 GRADING (2026-07-06 upgrade, Vault 0E) -- PRIMARY LINE
Run audit/w1_grading.py after full_tape_regrade.py: W1-cash rate per category is the headline; BOUHAR-class (both legs W1_CASHED) reported as its own rate; A requires the W1 shape. Baseline 07-05 box: 0/257 legs -- honest-clock era measured against zero.
## LATCH-BLIND (C-THIN-GUN calibration)
Run audit/latch_blind_forensic.py on settled slates; grade gun_thin_shadow fires vs honest start; graduation = catches the blind class at honest start +/-minutes with ~zero false pregame fires.

- **JOINT SHADOW rollup (Plex walk-cap ruling, from 2026-07-07 nights):** `python3 analysis/joint_shadow_rollup.py` -> JOINT_SHADOW_<date>.md/json — conversion/starvation of combined-vs-each-alone + <=97 held on constrained pairs. Feeds the walk_cap_honest_anchor + expression_invariant arm gates.

GUN SCORECARD 20260709: ATP_CHALL n=3 FRESH-within±3min=0/0 med|Δ|=-- catchup=0 misses=[] | ITF_M n=22 FRESH-within±3min=0/1 med|Δ|=102.2m catchup=3 misses=[] | ITF_W n=19 FRESH-within±3min=0/0 med|Δ|=-- catchup=0 misses=[] | WTA_CHALL n=6 FRESH-within±3min=0/0 med|Δ|=-- catchup=0 misses=[]

GUN SCORECARD 20260710: ATP_CHALL n=1 FRESH-within±3min=0/0 med|Δ|=-- catchup=0 suspect=[FEAKOZ] unjoinable=0 misses=[] | ITF_M n=8 FRESH-within±3min=0/0 med|Δ|=-- catchup=0 suspect=[HARTHU,IMANAK,MOCJAS,THORIC…] unjoinable=0 misses=[] | ITF_W n=11 FRESH-within±3min=0/0 med|Δ|=-- catchup=2 suspect=[DUELEY,DYUSAG,FRISOL,PLOERC…] unjoinable=2 misses=[] | WTA_CHALL n=5 FRESH-within±3min=0/0 med|Δ|=-- catchup=1 suspect=[CURVAN,QUEWAL] unjoinable=1 misses=[STEMAR,VOLMAN]

OS SHADOW 2026-07-10: n=3213 sites={'v4_place': 121, 'move_repost': 105, 'hold_review': 2987} | placement agree(±1c)=16 diverge=31 | divergence classes: {'decay_side|hold_window': 14, 'climb_side|hold_window': 9, 'climb_side|resting_window': 8} | hold: {'reviews': 2987, 'quiet': 0, 'floor_miss': 2496, 'both': 0, 'diverge': 2496, 'floor_unevaluable': 0, 'pre_instrument': 0} | cap-sensitivity: DEFERRED (joint-shadow n>=30 gate, operator 07-09)

ADJUDICATION 20260710: AGREE 122/131 | REFUSE 7 | NO-OPINION 2 | pair97 45

GUN SCORECARD 20260711: ATP_MAIN n=4 FRESH-within±3min=0/0 med|Δ|=-- catchup=0 suspect=[HUEBUT,MICHEM,MONHER,TABJEB] unjoinable=0 misses=[] | ITF_M n=15 FRESH-within±3min=2/6 med|Δ|=4.8m catchup=0 suspect=[NAKMAT,POLMIY,DOUROB,SHIROB…] unjoinable=3 misses=[VANZAM] | ITF_W n=14 FRESH-within±3min=3/6 med|Δ|=3.9m catchup=0 suspect=[ERCHRU,HOSCIR,KUBRYS,MAKSHO…] unjoinable=1 misses=[] | WTA_CHALL n=1 FRESH-within±3min=0/0 med|Δ|=-- catchup=0 suspect=[] unjoinable=1 misses=[] | FIRES-vs-SLATE: fires=33 tracked_events=99 ratio=33% | BELLS-MISSING=2 [SNIMAZ,STATOM] | HALT-MIN=0.0 UNBOOKED-FILLS-BOOKED=0 (watch: night-over-night drops + uncovered live matches are named here, not a week later)

OS SHADOW 2026-07-11: n=2346 sites={'move_repost': 61, 'v4_place': 100, 'hold_review': 2185} | placement agree(±1c)=12 diverge=12 | divergence classes: {'decay_side|hold_window': 6, 'climb_side|resting_window': 5, 'mains_join|hold_window': 1} | hold: {'reviews': 2185, 'quiet': 0, 'floor_miss': 1324, 'both': 0, 'diverge': 1324, 'floor_unevaluable': 0, 'pre_instrument': 0} | cap-sensitivity: DEFERRED (joint-shadow n>=30 gate, operator 07-09)

ADJUDICATION 20260711: AGREE 87/119 | REFUSE 4 | NO-OPINION 28 | pair97 27
