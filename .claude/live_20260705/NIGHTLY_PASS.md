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

GUN SCORECARD 20260712: ATP_CHALL n=9 FRESH-within±3min=2/6 med|Δ|=6.5m catchup=0 suspect=[FORPAM] unjoinable=2 misses=[] | ATP_MAIN n=5 FRESH-within±3min=0/2 med|Δ|=13.8m catchup=0 suspect=[CINHEM,KRUFER,TABHUE] unjoinable=0 misses=[] | ITF_M n=8 FRESH-within±3min=1/1 med|Δ|=0.6m catchup=0 suspect=[JASMAT,DUBPET,GELKOD,LOPLAG…] unjoinable=1 misses=[] | ITF_W n=11 FRESH-within±3min=0/2 med|Δ|=18.6m catchup=0 suspect=[TIKSHE,CORBRU,LIUPUS,NOEISA…] unjoinable=1 misses=[IACSMI,MIRSHC] | WTA_CHALL n=4 FRESH-within±3min=2/2 med|Δ|=2.5m catchup=0 suspect=[] unjoinable=2 misses=[] | WTA_MAIN n=8 FRESH-within±3min=1/1 med|Δ|=1.5m catchup=0 suspect=[FETPIE,GARPRI,HERKAZ,KULZAA…] unjoinable=0 misses=[KAWWAL] | FIRES-vs-SLATE: fires=42 tracked_events=157 ratio=27% | BELLS-MISSING=3 [DURDOU,HERKAZ,MONSHI] | HALT-MIN=0.0 UNBOOKED-FILLS-BOOKED=0 (watch: night-over-night drops + uncovered live matches are named here, not a week later)

OS SHADOW 2026-07-12: n=9691 sites={'move_repost': 215, 'v4_place': 453, 'hold_review': 9023} | placement agree(±1c)=49 diverge=71 | divergence classes: {'climb_side|hold_window': 36, 'decay_side|hold_window': 23, 'climb_side|resting_window': 11, 'mains_join|hold_window': 1} | hold: {'reviews': 9023, 'quiet': 183, 'floor_miss': 4394, 'both': 160, 'diverge': 4257, 'floor_unevaluable': 0, 'pre_instrument': 0} | cap-sensitivity: DEFERRED (joint-shadow n>=30 gate, operator 07-09)

ADJUDICATION 20260712: AGREE 3/3 | REFUSE 0 | NO-OPINION 0 | pair97 0

GUN SCORECARD 20260713: ATP_CHALL n=14 FRESH-within±3min=2/2 med|Δ|=2.1m catchup=0 suspect=[ALVKUM,BINFUE,FORMAK,JONPET…] unjoinable=5 misses=[] | ATP_MAIN n=17 FRESH-within±3min=2/4 med|Δ|=5.2m catchup=0 suspect=[FELKEC,TSIBUS] unjoinable=11 misses=[] | ITF_M n=36 FRESH-within±3min=1/2 med|Δ|=7.2m catchup=0 suspect=[BATSYC,BEAMTI,BENWRI,BOLGUE…] unjoinable=20 misses=[] | ITF_W n=43 FRESH-within±3min=2/2 med|Δ|=3.0m catchup=1 suspect=[PANOUN,SUNYUN,WANKOS,ZIAYAN…] unjoinable=20 misses=[] | WTA_CHALL n=8 FRESH-within±3min=1/3 med|Δ|=3.7m catchup=0 suspect=[JONSPI] unjoinable=4 misses=[] | WTA_MAIN n=4 FRESH-within±3min=0/2 med|Δ|=14.4m catchup=0 suspect=[] unjoinable=2 misses=[] | FIRES-vs-SLATE: fires=122 tracked_events=300 ratio=41% | NON-MAINS (deletion-gate denominator, MAINS-OFF excluded by design): fires=101/236 ratio=43% | MULTI-SOURCE events=0 | SELF-FILL fires=37 unconfirmed-by-any-other-source=37 | BELLS-MISSING=6 [ALTGAS,LABMAN,MAYAER,MICSEB,PULWIR,SARANG] | HALT-MIN=0.0 UNBOOKED-FILLS-BOOKED=0 (watch: night-over-night drops + uncovered live matches are named here, not a week later)

OS SHADOW 2026-07-13: n=6096 sites={'v4_place': 406, 'move_repost': 291, 'hold_review': 5399} | placement agree(±1c)=13 diverge=24 | divergence classes: {'climb_side|hold_window': 13, 'climb_side|resting_window': 8, 'decay_side|hold_window': 3} | hold: {'reviews': 5399, 'quiet': 37, 'floor_miss': 5079, 'both': 37, 'diverge': 5042, 'floor_unevaluable': 2, 'pre_instrument': 0} | cap-sensitivity: DEFERRED (joint-shadow n>=30 gate, operator 07-09)

GUN SCORECARD 20260714: ATP_CHALL n=17 FRESH-within±3min=1/3 med|Δ|=7.4m catchup=0 suspect=[EREPAV,GUIBON,KRATOR,NAGCRE…] unjoinable=9 misses=[] | ATP_MAIN n=9 FRESH-within±3min=0/1 med|Δ|=8.3m catchup=0 suspect=[BORKOU,SVRDIM,TSIBUS] unjoinable=5 misses=[] | ITF_M n=74 FRESH-within±3min=6/21 med|Δ|=4.8m catchup=1 suspect=[DEMTRI,FERMOC,JONELL,SIKSCH…] unjoinable=33 misses=[] | ITF_W n=85 FRESH-within±3min=10/28 med|Δ|=3.8m catchup=0 suspect=[BECMIL,KATYAN,KOSANX,LACLUE…] unjoinable=19 misses=[] | WTA_CHALL n=8 FRESH-within±3min=4/5 med|Δ|=1.8m catchup=0 suspect=[] unjoinable=3 misses=[] | WTA_MAIN n=3 FRESH-within±3min=2/3 med|Δ|=2.5m catchup=0 suspect=[] unjoinable=0 misses=[] | FIRES-vs-SLATE: fires=196 tracked_events=455 ratio=43% | NON-MAINS (deletion-gate denominator, MAINS-OFF excluded by design): fires=184/407 ratio=45% | MULTI-SOURCE events=96 | SELF-FILL fires=43 unconfirmed-by-any-other-source=14 | BELLS-MISSING=68 [ABOSME,ADERAD,ALCTOR,ALMDEL,ALTGAS,ANDAUE] | HALT-MIN=0.0 UNBOOKED-FILLS-BOOKED=0 (watch: night-over-night drops + uncovered live matches are named here, not a week later)

ADJUDICATION 20260714: AGREE 236/314 | REFUSE 47 | NO-OPINION 31 | pair97 26

GUN SCORECARD 20260715: ATP_CHALL n=7 FRESH-within±3min=2/3 med|Δ|=0.9m catchup=0 suspect=[] unjoinable=4 misses=[] | ATP_MAIN n=3 FRESH-within±3min=0/1 med|Δ|=8.0m catchup=1 suspect=[RINTAB] unjoinable=1 misses=[] | ITF_M n=94 FRESH-within±3min=16/41 med|Δ|=3.8m catchup=3 suspect=[BEAOGU,BOUHUL,HAZMCF,IBRBOB…] unjoinable=35 misses=[] | ITF_W n=79 FRESH-within±3min=15/35 med|Δ|=3.7m catchup=1 suspect=[FAIADA,KHALIN,OTWTAY,SELSAT…] unjoinable=26 misses=[] | WTA_CHALL n=4 FRESH-within±3min=1/1 med|Δ|=1.9m catchup=0 suspect=[RADCHI,YANLAN] unjoinable=1 misses=[] | WTA_MAIN n=1 FRESH-within±3min=0/0 med|Δ|=-- catchup=0 suspect=[] unjoinable=0 misses=[UDVKAW] | FIRES-vs-SLATE: fires=187 tracked_events=453 ratio=41% | NON-MAINS (deletion-gate denominator, MAINS-OFF excluded by design): fires=184/417 ratio=44% | MULTI-SOURCE events=112 | SELF-FILL fires=1 unconfirmed-by-any-other-source=0 | BELLS-MISSING=71 [ADKINO,ANSSAV,AUNALV,BAIGIL,BERMAD,BLAMAR] | HALT-MIN=0.0 UNBOOKED-FILLS-BOOKED=0 (watch: night-over-night drops + uncovered live matches are named here, not a week later)

OS SHADOW 2026-07-15: n=12300 sites={'v4_place': 567, 'move_repost': 149, 'hold_review': 11584} | placement agree(±1c)=3 diverge=31 | divergence classes: {'climb_side|resting_window': 13, 'decay_side|hold_window': 10, 'climb_side|hold_window': 7, 'mains_join|hold_window': 1} | hold: {'reviews': 11584, 'quiet': 4, 'floor_miss': 10941, 'both': 4, 'diverge': 10937, 'floor_unevaluable': 0, 'pre_instrument': 0} | cap-sensitivity: DEFERRED (joint-shadow n>=30 gate, operator 07-09)

ADJUDICATION 20260715: AGREE 120/150 | REFUSE 16 | NO-OPINION 14 | pair97 0

GUN SCORECARD 20260716: ATP_CHALL n=4 FRESH-within±3min=0/1 med|Δ|=5.9m catchup=0 suspect=[ALCANG] unjoinable=2 misses=[] | ATP_MAIN n=4 FRESH-within±3min=2/2 med|Δ|=1.2m catchup=0 suspect=[FARRUU,MERDRO] unjoinable=0 misses=[] | ITF_M n=83 FRESH-within±3min=15/24 med|Δ|=2.5m catchup=0 suspect=[FERSIK,HULCHA,OCOELL,VIISAC…] unjoinable=50 misses=[] | ITF_W n=61 FRESH-within±3min=10/22 med|Δ|=3.3m catchup=0 suspect=[LINRUS,WEBFAI,ARYKRO,CEXLOV…] unjoinable=27 misses=[] | WTA_CHALL n=2 FRESH-within±3min=1/1 med|Δ|=0.8m catchup=0 suspect=[] unjoinable=1 misses=[] | WTA_MAIN n=1 FRESH-within±3min=1/1 med|Δ|=2.7m catchup=0 suspect=[] unjoinable=0 misses=[] | FIRES-vs-SLATE: fires=155 tracked_events=268 ratio=58% | NON-MAINS (deletion-gate denominator, MAINS-OFF excluded by design): fires=150/259 ratio=58% | MULTI-SOURCE events=53 | SELF-FILL fires=0 unconfirmed-by-any-other-source=0 | BELLS-MISSING=43 [ANTHAR,BARMAK,BELGHA,BERAND,BLADOM,BOCHRI] | HALT-MIN=0.0 UNBOOKED-FILLS-BOOKED=0 (watch: night-over-night drops + uncovered live matches are named here, not a week later)

OS SHADOW 2026-07-16: n=31879 sites={'v4_place': 1211, 'move_repost': 261, 'hold_review': 30407} | placement agree(±1c)=9 diverge=125 | divergence classes: {'climb_side|resting_window': 50, 'climb_side|hold_window': 37, 'decay_side|hold_window': 36, 'mains_join|hold_window': 2} | hold: {'reviews': 30407, 'quiet': 40, 'floor_miss': 25902, 'both': 18, 'diverge': 25906, 'floor_unevaluable': 5, 'pre_instrument': 0} | cap-sensitivity: DEFERRED (joint-shadow n>=30 gate, operator 07-09)

ADJUDICATION 20260716: AGREE 11/13 | REFUSE 2 | NO-OPINION 0 | pair97 0

GUN SCORECARD 20260717: ATP_CHALL n=4 FRESH-within±3min=0/0 med|Δ|=-- catchup=1 suspect=[GALCOP] unjoinable=3 misses=[] | ATP_MAIN n=5 FRESH-within±3min=0/2 med|Δ|=14.5m catchup=0 suspect=[BUBHAL] unjoinable=2 misses=[] | ITF_M n=44 FRESH-within±3min=2/5 med|Δ|=3.5m catchup=0 suspect=[FERDEL,BLAGHA,DINKHO,IZQPER…] unjoinable=27 misses=[] | ITF_W n=37 FRESH-within±3min=3/11 med|Δ|=5.3m catchup=0 suspect=[SUBTHO,WEBYAN,BOJKON,BROBRA…] unjoinable=10 misses=[] | WTA_CHALL n=5 FRESH-within±3min=0/0 med|Δ|=-- catchup=0 suspect=[ANDKRA] unjoinable=4 misses=[] | WTA_MAIN n=1 FRESH-within±3min=0/0 med|Δ|=-- catchup=0 suspect=[] unjoinable=1 misses=[] | FIRES-vs-SLATE: fires=96 tracked_events=184 ratio=52% | NON-MAINS (deletion-gate denominator, MAINS-OFF excluded by design): fires=90/165 ratio=55% | MULTI-SOURCE events=29 | SELF-FILL fires=2 unconfirmed-by-any-other-source=2 | BELLS-MISSING=16 [BLAGHA,KIMDOI,LANBOS,MALKAL,MCKTSI,OMABER] | HALT-MIN=0.0 UNBOOKED-FILLS-BOOKED=0 (watch: night-over-night drops + uncovered live matches are named here, not a week later)

OS SHADOW 2026-07-17: n=1815 sites={'v4_place': 272, 'move_repost': 42, 'hold_review': 1501} | placement agree(±1c)=5 diverge=16 | divergence classes: {'climb_side|resting_window': 10, 'mains_join|hold_window': 2, 'decay_side|hold_window': 2, 'climb_side|hold_window': 2} | hold: {'reviews': 1501, 'quiet': 0, 'floor_miss': 1170, 'both': 0, 'diverge': 1170, 'floor_unevaluable': 0, 'pre_instrument': 0} | cap-sensitivity: DEFERRED (joint-shadow n>=30 gate, operator 07-09)

ADJUDICATION 20260717: AGREE 33/53 | REFUSE 8 | NO-OPINION 12 | pair97 1

GUN SCORECARD 20260718: ATP_CHALL n=5 FRESH-within±3min=0/1 med|Δ|=13.6m catchup=0 suspect=[FORTOM,SMIYUN,WONJOH] unjoinable=1 misses=[] | ATP_MAIN n=2 FRESH-within±3min=0/1 med|Δ|=3.2m catchup=0 suspect=[HIPGIU] unjoinable=0 misses=[] | ITF_M n=27 FRESH-within±3min=2/9 med|Δ|=7.6m catchup=0 suspect=[OCODEL,AGIOVC,TURSNI] unjoinable=15 misses=[] | ITF_W n=18 FRESH-within±3min=4/9 med|Δ|=5.4m catchup=0 suspect=[DOTROJ,JANYOD,KALWAN,ROUFAL…] unjoinable=4 misses=[] | WTA_CHALL n=1 FRESH-within±3min=0/1 med|Δ|=14.5m catchup=0 suspect=[] unjoinable=0 misses=[] | WTA_MAIN n=4 FRESH-within±3min=2/3 med|Δ|=1.5m catchup=0 suspect=[HONTHA] unjoinable=0 misses=[] | FIRES-vs-SLATE: fires=57 tracked_events=141 ratio=40% | NON-MAINS (deletion-gate denominator, MAINS-OFF excluded by design): fires=51/104 ratio=49% | MULTI-SOURCE events=14 | SELF-FILL fires=0 unconfirmed-by-any-other-source=0 | BELLS-MISSING=2 [VERDEL,VOGNIJ] | HALT-MIN=0.0 UNBOOKED-FILLS-BOOKED=0 (watch: night-over-night drops + uncovered live matches are named here, not a week later)

OS SHADOW 2026-07-18: n=7727 sites={'v4_place': 754, 'move_repost': 569, 'hold_review': 6404} | placement agree(±1c)=47 diverge=94 | divergence classes: {'decay_side|hold_window': 37, 'climb_side|hold_window': 23, 'climb_side|resting_window': 18, 'mains_join|hold_window': 16} | hold: {'reviews': 6404, 'quiet': 109, 'floor_miss': 2472, 'both': 22, 'diverge': 2537, 'floor_unevaluable': 0, 'pre_instrument': 0} | cap-sensitivity: DEFERRED (joint-shadow n>=30 gate, operator 07-09)

ADJUDICATION 20260718: AGREE 9/9 | REFUSE 0 | NO-OPINION 0 | pair97 3

GUN SCORECARD 20260719: ATP_CHALL n=13 FRESH-within±3min=1/5 med|Δ|=4.2m catchup=0 suspect=[LAJYUN,CALTEP,DEMBIT] unjoinable=5 misses=[] | ATP_MAIN n=1 FRESH-within±3min=0/1 med|Δ|=5.5m catchup=0 suspect=[] unjoinable=0 misses=[] | ITF_M n=23 FRESH-within±3min=0/5 med|Δ|=4.8m catchup=0 suspect=[SALTRI,VENBOO,CROMAC,DELTOR…] unjoinable=11 misses=[] | ITF_W n=23 FRESH-within±3min=2/12 med|Δ|=5.9m catchup=0 suspect=[THOAIA,BATCRI,CEHMYA,LABMAZ…] unjoinable=6 misses=[] | WTA_CHALL n=1 FRESH-within±3min=0/0 med|Δ|=-- catchup=0 suspect=[GRAKRA] unjoinable=0 misses=[] | WTA_MAIN n=9 FRESH-within±3min=2/6 med|Δ|=4.0m catchup=0 suspect=[JAKAVA,MALZAA,RUSKAZ] unjoinable=0 misses=[] | FIRES-vs-SLATE: fires=70 tracked_events=191 ratio=37% | NON-MAINS (deletion-gate denominator, MAINS-OFF excluded by design): fires=60/170 ratio=35% | MULTI-SOURCE events=14 | SELF-FILL fires=0 unconfirmed-by-any-other-source=0 | BELLS-MISSING=4 [ARSMAR,OTZPOL,PETVLC,POUJAN] | HALT-MIN=0.0 UNBOOKED-FILLS-BOOKED=0 (watch: night-over-night drops + uncovered live matches are named here, not a week later)

OS SHADOW 2026-07-19: n=6805 sites={'v4_place': 381, 'move_repost': 37, 'hold_review': 6387} | placement agree(±1c)=19 diverge=36 | divergence classes: {'climb_side|hold_window': 14, 'decay_side|hold_window': 11, 'mains_join|hold_window': 9, 'climb_side|resting_window': 2} | hold: {'reviews': 6387, 'quiet': 302, 'floor_miss': 1507, 'both': 75, 'diverge': 1659, 'floor_unevaluable': 0, 'pre_instrument': 0} | cap-sensitivity: DEFERRED (joint-shadow n>=30 gate, operator 07-09)

GUN SCORECARD 20260720:  | FIRES-vs-SLATE: fires=0 tracked_events=0 ratio=0% | NON-MAINS (deletion-gate denominator, MAINS-OFF excluded by design): fires=0/0 ratio=0% | MULTI-SOURCE events=0 | SELF-FILL fires=0 unconfirmed-by-any-other-source=0 | BELLS-MISSING=0 | HALT-MIN=0.0 UNBOOKED-FILLS-BOOKED=0 (watch: night-over-night drops + uncovered live matches are named here, not a week later)
