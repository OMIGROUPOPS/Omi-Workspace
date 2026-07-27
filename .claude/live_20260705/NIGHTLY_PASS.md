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

OS SHADOW 2026-07-20: n=10547 sites={'v4_place': 796, 'move_repost': 588, 'hold_review': 9163} | placement agree(±1c)=50 diverge=103 | divergence classes: {'decay_side|hold_window': 41, 'climb_side|hold_window': 26, 'climb_side|resting_window': 19, 'mains_join|hold_window': 17} | hold: {'reviews': 9163, 'quiet': 152, 'floor_miss': 3062, 'both': 29, 'diverge': 3156, 'floor_unevaluable': 0, 'pre_instrument': 0} | cap-sensitivity: DEFERRED (joint-shadow n>=30 gate, operator 07-09)

## PERCLASS 20260719 (era post-seal-20260720) — COMBINED PRIMARY (ruling 07-20 PM): sub-par(<=97)=pass; dual-negative=mastery meter
slate: 121 big-4 events · 105 scored pairs · skips {'thin_tape': 14, 'one_leg_file': 2, 'dead_band': 0, 'no_tape': 0}
- FLAT-FLAT (SEALED b2f0b670): pairs 27 duals 2 (completion 7%) · SUB-PAR(<=97) 2/2 = 100% -> PASS · tiers {'<=93': 2} · MASTERY dual-neg 0% (meter, never pass/fail) · medPairD -13
- MIRROR (REFUSE; fader drill on the mastery meter): pairs 53 duals 32 (completion 60%) · SUB-PAR(<=97) 0/32 = 0% -> FAIL · tiers {'98-100': 3, '>100': 29} · MASTERY dual-neg 0% (meter, never pass/fail) · medPairD +7
- NEITHER (counted apart): pairs 25 duals 13 (completion 52%) · SUB-PAR(<=97) 6/13 = 46% -> FAIL · tiers {'<=93': 2, '<=97': 4, '>100': 7} · MASTERY dual-neg 0% (meter, never pass/fail) · medPairD -1
- COMPLETION (volume drill): sub-par duals 8 / 105 slate pairs = 7.6%
  - flat_flat|ATP_CHALL: pairs 13 duals 1 (completion 8%) · SUB-PAR(<=97) 1/1 = 100% -> PASS · tiers {'<=93': 1} · MASTERY dual-neg 0% (meter, never pass/fail) · medPairD -7
  - flat_flat|ATP_MAIN: pairs 6 duals 0 — NO DUALS
  - flat_flat|WTA_MAIN: pairs 8 duals 1 (completion 12%) · SUB-PAR(<=97) 1/1 = 100% -> PASS · tiers {'<=93': 1} · MASTERY dual-neg 0% (meter, never pass/fail) · medPairD -19
  - mirror|ATP_CHALL: pairs 36 duals 21 (completion 58%) · SUB-PAR(<=97) 0/21 = 0% -> FAIL · tiers {'98-100': 3, '>100': 18} · MASTERY dual-neg 0% (meter, never pass/fail) · medPairD +10
  - mirror|ATP_MAIN: pairs 6 duals 3 (completion 50%) · SUB-PAR(<=97) 0/3 = 0% -> FAIL · tiers {'>100': 3} · MASTERY dual-neg 0% (meter, never pass/fail) · medPairD +6
  - mirror|WTA_CHALL: pairs 4 duals 3 (completion 75%) · SUB-PAR(<=97) 0/3 = 0% -> FAIL · tiers {'>100': 3} · MASTERY dual-neg 0% (meter, never pass/fail) · medPairD +4
  - mirror|WTA_MAIN: pairs 7 duals 5 (completion 71%) · SUB-PAR(<=97) 0/5 = 0% -> FAIL · tiers {'>100': 5} · MASTERY dual-neg 0% (meter, never pass/fail) · medPairD +7
  - neither|ATP_CHALL: pairs 15 duals 7 (completion 47%) · SUB-PAR(<=97) 2/7 = 29% -> FAIL · tiers {'<=93': 1, '<=97': 1, '>100': 5} · MASTERY dual-neg 0% (meter, never pass/fail) · medPairD +7
  - neither|ATP_MAIN: pairs 2 duals 2 (completion 100%) · SUB-PAR(<=97) 1/2 = 50% -> PASS · tiers {'<=97': 1, '>100': 1} · MASTERY dual-neg 0% (meter, never pass/fail) · medPairD +20
  - neither|WTA_CHALL: pairs 3 duals 1 (completion 33%) · SUB-PAR(<=97) 1/1 = 100% -> PASS · tiers {'<=97': 1} · MASTERY dual-neg 0% (meter, never pass/fail) · medPairD -13
  - neither|WTA_MAIN: pairs 5 duals 3 (completion 60%) · SUB-PAR(<=97) 2/3 = 67% -> PASS · tiers {'<=93': 1, '<=97': 1, '>100': 1} · MASTERY dual-neg 0% (meter, never pass/fail) · medPairD -3
- SEAL-DECAY TRIPWIRE: insufficient n (rolling duals 2 < 5) — no alarm, said

ADJUDICATION 20260720: AGREE 68/83 | REFUSE 11 | NO-OPINION 4 | pair97 5

## PERCLASS 20260720 (era post-seal-20260720) — COMBINED PRIMARY (ruling 07-20 PM): sub-par(<=97)=pass; dual-negative=mastery meter
slate: 98 big-4 events · 82 scored pairs · skips {'thin_tape': 16, 'one_leg_file': 0, 'dead_band': 0, 'no_tape': 0}
- FLAT-FLAT (SEALED b2f0b670; capture standard): **COMPLETION 4/19 = 21% x QUALITY 4/4 = 100% -> JOINT FAIL (bar 70/70)** · tiers {'<=93': 4} · MASTERY dual-neg 25% · medPairD -17
- MIRROR (REFUSE; fader drill on the mastery meter): pairs 42 duals 27 (completion 64%) · SUB-PAR(<=97) 0/27 = 0% -> FAIL · tiers {'98-100': 5, '>100': 22} · MASTERY dual-neg 0% (meter, never pass/fail) · medPairD +6
- NEITHER (counted apart): pairs 21 duals 14 (completion 67%) · SUB-PAR(<=97) 6/14 = 43% -> FAIL · tiers {'98-100': 2, '<=93': 2, '<=95': 1, '<=97': 3, '>100': 6} · MASTERY dual-neg 7% (meter, never pass/fail) · medPairD -2
- COMPLETION (volume drill): sub-par duals 10 / 82 slate pairs = 12.2%
  - flat_flat|ATP_CHALL: pairs 7 duals 2 (completion 29%) · SUB-PAR(<=97) 2/2 = 100% -> PASS · tiers {'<=93': 2} · MASTERY dual-neg 50% (meter, never pass/fail) · medPairD -17
  - flat_flat|ATP_MAIN: pairs 2 duals 1 (completion 50%) · SUB-PAR(<=97) 1/1 = 100% -> PASS · tiers {'<=93': 1} · MASTERY dual-neg 0% (meter, never pass/fail) · medPairD -7
  - flat_flat|WTA_CHALL: pairs 1 duals 0 — NO DUALS
  - flat_flat|WTA_MAIN: pairs 9 duals 1 (completion 11%) · SUB-PAR(<=97) 1/1 = 100% -> PASS · tiers {'<=93': 1} · MASTERY dual-neg 0% (meter, never pass/fail) · medPairD -24
  - mirror|ATP_CHALL: pairs 32 duals 19 (completion 59%) · SUB-PAR(<=97) 0/19 = 0% -> FAIL · tiers {'98-100': 4, '>100': 15} · MASTERY dual-neg 0% (meter, never pass/fail) · medPairD +5
  - mirror|WTA_CHALL: pairs 4 duals 3 (completion 75%) · SUB-PAR(<=97) 0/3 = 0% -> FAIL · tiers {'>100': 3} · MASTERY dual-neg 0% (meter, never pass/fail) · medPairD +6
  - mirror|WTA_MAIN: pairs 6 duals 5 (completion 83%) · SUB-PAR(<=97) 0/5 = 0% -> FAIL · tiers {'98-100': 1, '>100': 4} · MASTERY dual-neg 0% (meter, never pass/fail) · medPairD +12
  - neither|ATP_CHALL: pairs 11 duals 6 (completion 55%) · SUB-PAR(<=97) 3/6 = 50% -> PASS · tiers {'98-100': 1, '<=93': 1, '<=97': 2, '>100': 2} · MASTERY dual-neg 17% (meter, never pass/fail) · medPairD -2
  - neither|ATP_MAIN: pairs 2 duals 2 (completion 100%) · SUB-PAR(<=97) 0/2 = 0% -> FAIL · tiers {'>100': 2} · MASTERY dual-neg 0% (meter, never pass/fail) · medPairD +18
  - neither|WTA_CHALL: pairs 3 duals 2 (completion 67%) · SUB-PAR(<=97) 2/2 = 100% -> PASS · tiers {'<=93': 1, '<=97': 1} · MASTERY dual-neg 0% (meter, never pass/fail) · medPairD -5
  - neither|WTA_MAIN: pairs 5 duals 4 (completion 80%) · SUB-PAR(<=97) 1/4 = 25% -> FAIL · tiers {'98-100': 1, '<=95': 1, '>100': 2} · MASTERY dual-neg 0% (meter, never pass/fail) · medPairD +3
- SEAL-DECAY TRIPWIRE: **SEAL-DECAY — RED; operator ruling required; never auto-disarm** [rolling7 COMPLETION 6/19 = 32% < 70%]

GUN SCORECARD 20260721: ATP_CHALL n=16 FRESH-within±3min=3/10 med|Δ|=5.6m catchup=0 suspect=[KASWES] unjoinable=5 misses=[] | ATP_MAIN n=1 FRESH-within±3min=0/0 med|Δ|=-- catchup=0 suspect=[] unjoinable=1 misses=[] | ITF_M n=38 FRESH-within±3min=7/19 med|Δ|=4.1m catchup=0 suspect=[BECKOM,CHAELL,ICHYAM,KAWTAG…] unjoinable=8 misses=[] | ITF_W n=40 FRESH-within±3min=7/21 med|Δ|=4.7m catchup=0 suspect=[NAICHO,SCHBAK,WANWAR,GANFRU…] unjoinable=11 misses=[] | WTA_MAIN n=8 FRESH-within±3min=2/5 med|Δ|=6.3m catchup=0 suspect=[PRIUDV] unjoinable=2 misses=[] | FIRES-vs-SLATE: fires=103 tracked_events=368 ratio=28% | NON-MAINS (deletion-gate denominator, MAINS-OFF excluded by design): fires=94/330 ratio=28% | MULTI-SOURCE events=47 | SELF-FILL fires=3 unconfirmed-by-any-other-source=1 | BELLS-MISSING=11 [BILHOM,CARGUA,MARMON,MASKRO,OTZSVA,PIEMEL] | HALT-MIN=0.0 UNBOOKED-FILLS-BOOKED=0 (watch: night-over-night drops + uncovered live matches are named here, not a week later)

OS SHADOW 2026-07-21: n=5028 sites={'v4_place': 790, 'move_repost': 263, 'hold_review': 3975} | placement agree(±1c)=47 diverge=96 | divergence classes: {'climb_side|hold_window': 52, 'decay_side|hold_window': 32, 'climb_side|resting_window': 12} | hold: {'reviews': 3975, 'quiet': 130, 'floor_miss': 1527, 'both': 38, 'diverge': 1581, 'floor_unevaluable': 49, 'pre_instrument': 0} | cap-sensitivity: DEFERRED (joint-shadow n>=30 gate, operator 07-09)

## PERCLASS 20260721 (era post-seal-20260720) — COMBINED PRIMARY (ruling 07-20 PM): sub-par(<=97)=pass; dual-negative=mastery meter
slate: 82 big-4 events · 79 scored pairs · skips {'thin_tape': 2, 'one_leg_file': 1, 'dead_band': 0, 'no_tape': 0}
- FLAT-FLAT (SEALED b2f0b670; capture standard): **COMPLETION 7/22 = 32% x QUALITY 7/7 = 100% -> JOINT FAIL (bar 70/70)** · tiers {'<=93': 7} · MASTERY dual-neg 14% · medPairD -15
- MIRROR (REFUSE; fader drill on the mastery meter): pairs 35 duals 20 (completion 57%) · SUB-PAR(<=97) 0/20 = 0% -> FAIL · tiers {'98-100': 5, '>100': 15} · MASTERY dual-neg 0% (meter, never pass/fail) · medPairD +2
- NEITHER (counted apart): pairs 22 duals 14 (completion 64%) · SUB-PAR(<=97) 5/14 = 36% -> FAIL · tiers {'98-100': 2, '<=93': 1, '<=95': 3, '<=97': 1, '>100': 7} · MASTERY dual-neg 21% (meter, never pass/fail) · medPairD +0
- COMPLETION (volume drill): sub-par duals 12 / 79 slate pairs = 15.2%
  - flat_flat|ATP_CHALL: pairs 10 duals 4 (completion 40%) · SUB-PAR(<=97) 4/4 = 100% -> PASS · tiers {'<=93': 4} · MASTERY dual-neg 25% (meter, never pass/fail) · medPairD -15
  - flat_flat|ATP_MAIN: pairs 4 duals 1 (completion 25%) · SUB-PAR(<=97) 1/1 = 100% -> PASS · tiers {'<=93': 1} · MASTERY dual-neg 0% (meter, never pass/fail) · medPairD -10
  - flat_flat|WTA_CHALL: pairs 5 duals 2 (completion 40%) · SUB-PAR(<=97) 2/2 = 100% -> PASS · tiers {'<=93': 2} · MASTERY dual-neg 0% (meter, never pass/fail) · medPairD -18
  - flat_flat|WTA_MAIN: pairs 3 duals 0 — NO DUALS
  - mirror|ATP_CHALL: pairs 33 duals 19 (completion 58%) · SUB-PAR(<=97) 0/19 = 0% -> FAIL · tiers {'98-100': 5, '>100': 14} · MASTERY dual-neg 0% (meter, never pass/fail) · medPairD +2
  - mirror|ATP_MAIN: pairs 1 duals 1 (completion 100%) · SUB-PAR(<=97) 0/1 = 0% -> FAIL · tiers {'>100': 1} · MASTERY dual-neg 0% (meter, never pass/fail) · medPairD +9
  - mirror|WTA_MAIN: pairs 1 duals 0 — NO DUALS
  - neither|ATP_CHALL: pairs 18 duals 11 (completion 61%) · SUB-PAR(<=97) 3/11 = 27% -> FAIL · tiers {'98-100': 2, '<=95': 3, '>100': 6} · MASTERY dual-neg 18% (meter, never pass/fail) · medPairD +2
  - neither|ATP_MAIN: pairs 1 duals 1 (completion 100%) · SUB-PAR(<=97) 0/1 = 0% -> FAIL · tiers {'>100': 1} · MASTERY dual-neg 0% (meter, never pass/fail) · medPairD +8
  - neither|WTA_CHALL: pairs 2 duals 1 (completion 50%) · SUB-PAR(<=97) 1/1 = 100% -> PASS · tiers {'<=97': 1} · MASTERY dual-neg 0% (meter, never pass/fail) · medPairD -5
  - neither|WTA_MAIN: pairs 1 duals 1 (completion 100%) · SUB-PAR(<=97) 1/1 = 100% -> PASS · tiers {'<=93': 1} · MASTERY dual-neg 100% (meter, never pass/fail) · medPairD -8
- SEAL-DECAY TRIPWIRE: **SEAL-DECAY — RED; operator ruling required; never auto-disarm** [rolling7 COMPLETION 13/41 = 32% < 70%]

GUN SCORECARD 20260722: ATP_CHALL n=8 FRESH-within±3min=3/3 med|Δ|=0.4m catchup=0 suspect=[HOLJOH,MICGEA,MOCSEK] unjoinable=2 misses=[] | ATP_MAIN n=2 FRESH-within±3min=0/2 med|Δ|=11.4m catchup=0 suspect=[] unjoinable=0 misses=[] | ITF_M n=48 FRESH-within±3min=5/18 med|Δ|=4.6m catchup=0 suspect=[CHAHIR,FONZAR,HULVAN,JOVBOB…] unjoinable=12 misses=[] | ITF_W n=61 FRESH-within±3min=15/29 med|Δ|=2.7m catchup=0 suspect=[ALAUEM,ARAFAI,CHAJOH,IPUUCH…] unjoinable=15 misses=[] | WTA_MAIN n=2 FRESH-within±3min=1/2 med|Δ|=12.4m catchup=0 suspect=[] unjoinable=0 misses=[] | FIRES-vs-SLATE: fires=121 tracked_events=310 ratio=39% | NON-MAINS (deletion-gate denominator, MAINS-OFF excluded by design): fires=117/304 ratio=38% | MULTI-SOURCE events=53 | SELF-FILL fires=2 unconfirmed-by-any-other-source=0 | BELLS-MISSING=36 [ALAUEM,ARAFAI,BAKSYC,BENHER,BERHAM,BRULAZ] | HALT-MIN=0.0 UNBOOKED-FILLS-BOOKED=0 (watch: night-over-night drops + uncovered live matches are named here, not a week later)

OS SHADOW 2026-07-22: n=11985 sites={'v4_place': 1451, 'move_repost': 365, 'hold_review': 10169} | placement agree(±1c)=80 diverge=139 | divergence classes: {'climb_side|hold_window': 72, 'decay_side|hold_window': 46, 'climb_side|resting_window': 14, 'mains_join|hold_window': 7} | hold: {'reviews': 10169, 'quiet': 477, 'floor_miss': 2889, 'both': 166, 'diverge': 3034, 'floor_unevaluable': 49, 'pre_instrument': 0} | cap-sensitivity: DEFERRED (joint-shadow n>=30 gate, operator 07-09)

## PERCLASS 20260722 (era post-seal-20260720) — COMBINED PRIMARY (ruling 07-20 PM): sub-par(<=97)=pass; dual-negative=mastery meter
slate: 48 big-4 events · 45 scored pairs · skips {'thin_tape': 3, 'one_leg_file': 0, 'dead_band': 0, 'no_tape': 0}
- FLAT-FLAT (SEALED b2f0b670; capture standard): **COMPLETION 0/19 = 0% x QUALITY 0/0 = 0% -> JOINT FAIL (bar 70/70)** · tiers {} · MASTERY dual-neg 0% · medPairD +0
- MIRROR (REFUSE; fader drill on the mastery meter): pairs 17 duals 8 (completion 47%) · SUB-PAR(<=97) 1/8 = 12% -> FAIL · tiers {'<=97': 1, '>100': 7} · MASTERY dual-neg 0% (meter, never pass/fail) · medPairD +16
- NEITHER (counted apart): pairs 9 duals 2 (completion 22%) · SUB-PAR(<=97) 1/2 = 50% -> PASS · tiers {'<=93': 1, '>100': 1} · MASTERY dual-neg 0% (meter, never pass/fail) · medPairD +23
- COMPLETION (volume drill): sub-par duals 2 / 45 slate pairs = 4.4%
  - flat_flat|ATP_CHALL: pairs 2 duals 0 — NO DUALS
  - flat_flat|ATP_MAIN: pairs 10 duals 0 — NO DUALS
  - flat_flat|WTA_CHALL: pairs 1 duals 0 — NO DUALS
  - flat_flat|WTA_MAIN: pairs 6 duals 0 — NO DUALS
  - mirror|ATP_CHALL: pairs 10 duals 6 (completion 60%) · SUB-PAR(<=97) 1/6 = 17% -> FAIL · tiers {'<=97': 1, '>100': 5} · MASTERY dual-neg 0% (meter, never pass/fail) · medPairD +14
  - mirror|ATP_MAIN: pairs 3 duals 0 — NO DUALS
  - mirror|WTA_CHALL: pairs 2 duals 2 (completion 100%) · SUB-PAR(<=97) 0/2 = 0% -> FAIL · tiers {'>100': 2} · MASTERY dual-neg 0% (meter, never pass/fail) · medPairD +20
  - mirror|WTA_MAIN: pairs 2 duals 0 — NO DUALS
  - neither|ATP_CHALL: pairs 5 duals 0 — NO DUALS
  - neither|ATP_MAIN: pairs 1 duals 1 (completion 100%) · SUB-PAR(<=97) 0/1 = 0% -> FAIL · tiers {'>100': 1} · MASTERY dual-neg 0% (meter, never pass/fail) · medPairD +34
  - neither|WTA_CHALL: pairs 1 duals 0 — NO DUALS
  - neither|WTA_MAIN: pairs 2 duals 1 (completion 50%) · SUB-PAR(<=97) 1/1 = 100% -> PASS · tiers {'<=93': 1} · MASTERY dual-neg 0% (meter, never pass/fail) · medPairD +12
- SEAL-DECAY TRIPWIRE: **SEAL-DECAY — RED; operator ruling required; never auto-disarm** [rolling7 COMPLETION 13/60 = 22% < 70%]

GUN SCORECARD 20260723: ATP_CHALL n=7 FRESH-within±3min=1/5 med|Δ|=3.4m catchup=0 suspect=[NOGRIC,ALCDIE] unjoinable=0 misses=[] | ATP_MAIN n=1 FRESH-within±3min=1/1 med|Δ|=2.4m catchup=0 suspect=[] unjoinable=0 misses=[] | ITF_M n=40 FRESH-within±3min=3/8 med|Δ|=9.2m catchup=0 suspect=[BECSHI,BOOTAK,BOUMOC,CHASAI…] unjoinable=8 misses=[] | ITF_W n=44 FRESH-within±3min=3/13 med|Δ|=7.3m catchup=0 suspect=[CABIVA,JARVOL,PENKUL,STEWAN…] unjoinable=10 misses=[] | WTA_MAIN n=1 FRESH-within±3min=0/1 med|Δ|=3.4m catchup=0 suspect=[] unjoinable=0 misses=[] | FIRES-vs-SLATE: fires=93 tracked_events=235 ratio=40% | NON-MAINS (deletion-gate denominator, MAINS-OFF excluded by design): fires=91/230 ratio=40% | MULTI-SOURCE events=27 | SELF-FILL fires=5 unconfirmed-by-any-other-source=1 | BELLS-MISSING=15 [CENBAJ,GUTVAN,INIBIO,KATMIL,KHODEL,LAZCOR] | HALT-MIN=0.0 UNBOOKED-FILLS-BOOKED=0 (watch: night-over-night drops + uncovered live matches are named here, not a week later)

OS SHADOW 2026-07-23: n=14863 sites={'v4_place': 1856, 'move_repost': 423, 'hold_review': 12584} | placement agree(±1c)=99 diverge=202 | divergence classes: {'climb_side|hold_window': 106, 'decay_side|hold_window': 71, 'climb_side|resting_window': 15, 'mains_join|hold_window': 10} | hold: {'reviews': 12584, 'quiet': 788, 'floor_miss': 2965, 'both': 167, 'diverge': 3419, 'floor_unevaluable': 49, 'pre_instrument': 0} | cap-sensitivity: DEFERRED (joint-shadow n>=30 gate, operator 07-09)

## PERCLASS 20260723 (era post-seal-20260720) — COMBINED PRIMARY (ruling 07-20 PM): sub-par(<=97)=pass; dual-negative=mastery meter
slate: 24 big-4 events · 24 scored pairs · skips {'thin_tape': 0, 'one_leg_file': 0, 'dead_band': 0, 'no_tape': 0}
- FLAT-FLAT (SEALED b2f0b670; capture standard): **COMPLETION 2/4 = 50% x QUALITY 2/2 = 100% -> JOINT FAIL (bar 70/70)** · tiers {'<=93': 2} · MASTERY dual-neg 0% · medPairD -14
- MIRROR (REFUSE; fader drill on the mastery meter): pairs 17 duals 11 (completion 65%) · SUB-PAR(<=97) 0/11 = 0% -> FAIL · tiers {'98-100': 1, '>100': 10} · MASTERY dual-neg 0% (meter, never pass/fail) · medPairD +9
- NEITHER (counted apart): pairs 3 duals 3 (completion 100%) · SUB-PAR(<=97) 2/3 = 67% -> PASS · tiers {'<=93': 2, '>100': 1} · MASTERY dual-neg 0% (meter, never pass/fail) · medPairD -6
- COMPLETION (volume drill): sub-par duals 4 / 24 slate pairs = 16.7%
  - flat_flat|ATP_CHALL: pairs 2 duals 1 (completion 50%) · SUB-PAR(<=97) 1/1 = 100% -> PASS · tiers {'<=93': 1} · MASTERY dual-neg 0% (meter, never pass/fail) · medPairD -18
  - flat_flat|WTA_MAIN: pairs 2 duals 1 (completion 50%) · SUB-PAR(<=97) 1/1 = 100% -> PASS · tiers {'<=93': 1} · MASTERY dual-neg 0% (meter, never pass/fail) · medPairD -11
  - mirror|ATP_CHALL: pairs 13 duals 9 (completion 69%) · SUB-PAR(<=97) 0/9 = 0% -> FAIL · tiers {'98-100': 1, '>100': 8} · MASTERY dual-neg 0% (meter, never pass/fail) · medPairD +9
  - mirror|ATP_MAIN: pairs 1 duals 1 (completion 100%) · SUB-PAR(<=97) 0/1 = 0% -> FAIL · tiers {'>100': 1} · MASTERY dual-neg 0% (meter, never pass/fail) · medPairD +3
  - mirror|WTA_CHALL: pairs 3 duals 1 (completion 33%) · SUB-PAR(<=97) 0/1 = 0% -> FAIL · tiers {'>100': 1} · MASTERY dual-neg 0% (meter, never pass/fail) · medPairD +25
  - neither|ATP_CHALL: pairs 2 duals 2 (completion 100%) · SUB-PAR(<=97) 1/2 = 50% -> PASS · tiers {'<=93': 1, '>100': 1} · MASTERY dual-neg 0% (meter, never pass/fail) · medPairD +0
  - neither|WTA_CHALL: pairs 1 duals 1 (completion 100%) · SUB-PAR(<=97) 1/1 = 100% -> PASS · tiers {'<=93': 1} · MASTERY dual-neg 0% (meter, never pass/fail) · medPairD -6
- SEAL-DECAY TRIPWIRE: **SEAL-DECAY — RED; operator ruling required; never auto-disarm** [rolling7 COMPLETION 15/64 = 23% < 70%]

GUN SCORECARD 20260724: ATP_CHALL n=6 FRESH-within±3min=2/2 med|Δ|=1.4m catchup=0 suspect=[HOLDRA,MATCHI,INCSMI,ONCGEN] unjoinable=0 misses=[] | ITF_M n=25 FRESH-within±3min=2/9 med|Δ|=7.2m catchup=0 suspect=[BOUHUL,DELJOV,FERMAR,PAPAND…] unjoinable=10 misses=[] | ITF_W n=19 FRESH-within±3min=4/5 med|Δ|=1.4m catchup=0 suspect=[ALEKUR,ARAUCH,MILAIA,WANYOS…] unjoinable=4 misses=[] | WTA_MAIN n=2 FRESH-within±3min=1/2 med|Δ|=5.6m catchup=0 suspect=[] unjoinable=0 misses=[] | FIRES-vs-SLATE: fires=52 tracked_events=137 ratio=38% | NON-MAINS (deletion-gate denominator, MAINS-OFF excluded by design): fires=50/135 ratio=37% | MULTI-SOURCE events=5 | SELF-FILL fires=2 unconfirmed-by-any-other-source=0 | BELLS-MISSING=0 | HALT-MIN=0.0 UNBOOKED-FILLS-BOOKED=0 (watch: night-over-night drops + uncovered live matches are named here, not a week later)

OS SHADOW 2026-07-24: n=20333 sites={'v4_place': 2226, 'move_repost': 500, 'hold_review': 17607} | placement agree(±1c)=135 diverge=249 | divergence classes: {'climb_side|hold_window': 130, 'decay_side|hold_window': 85, 'mains_join|hold_window': 18, 'climb_side|resting_window': 16} | hold: {'reviews': 17607, 'quiet': 969, 'floor_miss': 3196, 'both': 176, 'diverge': 3813, 'floor_unevaluable': 49, 'pre_instrument': 0} | cap-sensitivity: DEFERRED (joint-shadow n>=30 gate, operator 07-09)

## PERCLASS 20260724 (era post-seal-20260720) — COMBINED PRIMARY (ruling 07-20 PM): sub-par(<=97)=pass; dual-negative=mastery meter
slate: 38 big-4 events · 38 scored pairs · skips {'thin_tape': 0, 'one_leg_file': 0, 'dead_band': 0, 'no_tape': 0}
- FLAT-FLAT (SEALED b2f0b670; capture standard): **COMPLETION 2/8 = 25% x QUALITY 2/2 = 100% -> JOINT FAIL (bar 70/70)** · tiers {'<=93': 2} · MASTERY dual-neg 0% · medPairD -12
- MIRROR (REFUSE; fader drill on the mastery meter): pairs 24 duals 15 (completion 62%) · SUB-PAR(<=97) 0/15 = 0% -> FAIL · tiers {'98-100': 1, '>100': 14} · MASTERY dual-neg 0% (meter, never pass/fail) · medPairD +17
- NEITHER (counted apart): pairs 6 duals 4 (completion 67%) · SUB-PAR(<=97) 2/4 = 50% -> PASS · tiers {'<=93': 2, '>100': 2} · MASTERY dual-neg 0% (meter, never pass/fail) · medPairD -2
- COMPLETION (volume drill): sub-par duals 4 / 38 slate pairs = 10.5%
  - flat_flat|ATP_CHALL: pairs 2 duals 0 — NO DUALS
  - flat_flat|ATP_MAIN: pairs 2 duals 1 (completion 50%) · SUB-PAR(<=97) 1/1 = 100% -> PASS · tiers {'<=93': 1} · MASTERY dual-neg 0% (meter, never pass/fail) · medPairD -9
  - flat_flat|WTA_CHALL: pairs 1 duals 1 (completion 100%) · SUB-PAR(<=97) 1/1 = 100% -> PASS · tiers {'<=93': 1} · MASTERY dual-neg 0% (meter, never pass/fail) · medPairD -16
  - flat_flat|WTA_MAIN: pairs 3 duals 0 — NO DUALS
  - mirror|ATP_CHALL: pairs 15 duals 8 (completion 53%) · SUB-PAR(<=97) 0/8 = 0% -> FAIL · tiers {'98-100': 1, '>100': 7} · MASTERY dual-neg 0% (meter, never pass/fail) · medPairD +16
  - mirror|ATP_MAIN: pairs 2 duals 2 (completion 100%) · SUB-PAR(<=97) 0/2 = 0% -> FAIL · tiers {'>100': 2} · MASTERY dual-neg 0% (meter, never pass/fail) · medPairD +5
  - mirror|WTA_CHALL: pairs 3 duals 3 (completion 100%) · SUB-PAR(<=97) 0/3 = 0% -> FAIL · tiers {'>100': 3} · MASTERY dual-neg 0% (meter, never pass/fail) · medPairD +17
  - mirror|WTA_MAIN: pairs 4 duals 2 (completion 50%) · SUB-PAR(<=97) 0/2 = 0% -> FAIL · tiers {'>100': 2} · MASTERY dual-neg 0% (meter, never pass/fail) · medPairD +24
  - neither|ATP_CHALL: pairs 3 duals 3 (completion 100%) · SUB-PAR(<=97) 2/3 = 67% -> PASS · tiers {'<=93': 2, '>100': 1} · MASTERY dual-neg 0% (meter, never pass/fail) · medPairD -10
  - neither|ATP_MAIN: pairs 2 duals 1 (completion 50%) · SUB-PAR(<=97) 0/1 = 0% -> FAIL · tiers {'>100': 1} · MASTERY dual-neg 0% (meter, never pass/fail) · medPairD +40
  - neither|WTA_MAIN: pairs 1 duals 0 — NO DUALS
- SEAL-DECAY TRIPWIRE: **SEAL-DECAY — RED; operator ruling required; never auto-disarm** [rolling7 COMPLETION 17/72 = 24% < 70%]

GUN SCORECARD 20260725: ATP_CHALL n=3 FRESH-within±3min=0/2 med|Δ|=9.4m catchup=0 suspect=[MOCMON] unjoinable=0 misses=[] | ITF_M n=14 FRESH-within±3min=2/7 med|Δ|=5.9m catchup=0 suspect=[SINGEL,WIJQAB] unjoinable=5 misses=[] | ITF_W n=11 FRESH-within±3min=2/7 med|Δ|=8.3m catchup=0 suspect=[TSAARA,MIRSAN] unjoinable=2 misses=[] | FIRES-vs-SLATE: fires=28 tracked_events=130 ratio=22% | NON-MAINS (deletion-gate denominator, MAINS-OFF excluded by design): fires=28/88 ratio=32% | MULTI-SOURCE events=6 | SELF-FILL fires=0 unconfirmed-by-any-other-source=0 | BELLS-MISSING=0 | HALT-MIN=0.0 UNBOOKED-FILLS-BOOKED=0 (watch: night-over-night drops + uncovered live matches are named here, not a week later)

OS SHADOW 2026-07-25: n=1915 sites={'v4_place': 156, 'move_repost': 48, 'hold_review': 1711} | placement agree(±1c)=17 diverge=25 | divergence classes: {'climb_side|hold_window': 11, 'decay_side|hold_window': 8, 'mains_join|hold_window': 4, 'climb_side|resting_window': 2} | hold: {'reviews': 1711, 'quiet': 28, 'floor_miss': 88, 'both': 0, 'diverge': 116, 'floor_unevaluable': 0, 'pre_instrument': 0} | cap-sensitivity: DEFERRED (joint-shadow n>=30 gate, operator 07-09)

## PERCLASS 20260725 (era post-seal-20260720) — COMBINED PRIMARY (ruling 07-20 PM): sub-par(<=97)=pass; dual-negative=mastery meter
slate: 55 big-4 events · 54 scored pairs · skips {'thin_tape': 1, 'one_leg_file': 0, 'dead_band': 0, 'no_tape': 0}
- FLAT-FLAT (SEALED b2f0b670; capture standard): **COMPLETION 1/11 = 9% x QUALITY 1/1 = 100% -> JOINT FAIL (bar 70/70)** · tiers {'<=93': 1} · MASTERY dual-neg 0% · medPairD -9
- MIRROR (REFUSE; fader drill on the mastery meter): pairs 25 duals 16 (completion 64%) · SUB-PAR(<=97) 1/16 = 6% -> FAIL · tiers {'<=97': 1, '>100': 15} · MASTERY dual-neg 0% (meter, never pass/fail) · medPairD +9
- NEITHER (counted apart): pairs 18 duals 7 (completion 39%) · SUB-PAR(<=97) 3/7 = 43% -> FAIL · tiers {'98-100': 2, '<=93': 3, '>100': 2} · MASTERY dual-neg 14% (meter, never pass/fail) · medPairD -2
- COMPLETION (volume drill): sub-par duals 5 / 54 slate pairs = 9.3%
  - flat_flat|ATP_MAIN: pairs 5 duals 1 (completion 20%) · SUB-PAR(<=97) 1/1 = 100% -> PASS · tiers {'<=93': 1} · MASTERY dual-neg 0% (meter, never pass/fail) · medPairD -9
  - flat_flat|WTA_CHALL: pairs 3 duals 0 — NO DUALS
  - flat_flat|WTA_MAIN: pairs 3 duals 0 — NO DUALS
  - mirror|ATP_CHALL: pairs 7 duals 4 (completion 57%) · SUB-PAR(<=97) 1/4 = 25% -> FAIL · tiers {'<=97': 1, '>100': 3} · MASTERY dual-neg 0% (meter, never pass/fail) · medPairD +8
  - mirror|ATP_MAIN: pairs 5 duals 3 (completion 60%) · SUB-PAR(<=97) 0/3 = 0% -> FAIL · tiers {'>100': 3} · MASTERY dual-neg 0% (meter, never pass/fail) · medPairD +23
  - mirror|WTA_CHALL: pairs 6 duals 3 (completion 50%) · SUB-PAR(<=97) 0/3 = 0% -> FAIL · tiers {'>100': 3} · MASTERY dual-neg 0% (meter, never pass/fail) · medPairD +20
  - mirror|WTA_MAIN: pairs 7 duals 6 (completion 86%) · SUB-PAR(<=97) 0/6 = 0% -> FAIL · tiers {'>100': 6} · MASTERY dual-neg 0% (meter, never pass/fail) · medPairD +7
  - neither|ATP_CHALL: pairs 3 duals 0 — NO DUALS
  - neither|ATP_MAIN: pairs 5 duals 3 (completion 60%) · SUB-PAR(<=97) 1/3 = 33% -> FAIL · tiers {'98-100': 1, '<=93': 1, '>100': 1} · MASTERY dual-neg 33% (meter, never pass/fail) · medPairD -1
  - neither|WTA_CHALL: pairs 1 duals 0 — NO DUALS
  - neither|WTA_MAIN: pairs 9 duals 4 (completion 44%) · SUB-PAR(<=97) 2/4 = 50% -> PASS · tiers {'98-100': 1, '<=93': 2, '>100': 1} · MASTERY dual-neg 0% (meter, never pass/fail) · medPairD -6
- SEAL-DECAY TRIPWIRE: **SEAL-DECAY — RED; operator ruling required; never auto-disarm** [rolling7 COMPLETION 18/83 = 22% < 70%]

GUN SCORECARD 20260726: ATP_CHALL n=15 FRESH-within±3min=1/11 med|Δ|=6.3m catchup=0 suspect=[BASOZD,BAYTUR] unjoinable=2 misses=[] | ATP_MAIN n=9 FRESH-within±3min=1/3 med|Δ|=3.9m catchup=0 suspect=[WONRUB,MAGJOH,PASSMI] unjoinable=3 misses=[] | ITF_M n=13 FRESH-within±3min=2/2 med|Δ|=2.3m catchup=0 suspect=[BOOMAT] unjoinable=10 misses=[] | ITF_W n=8 FRESH-within±3min=2/5 med|Δ|=3.6m catchup=0 suspect=[ARAAIA] unjoinable=2 misses=[] | WTA_CHALL n=15 FRESH-within±3min=3/3 med|Δ|=1.0m catchup=0 suspect=[KURKUW] unjoinable=11 misses=[] | FIRES-vs-SLATE: fires=60 tracked_events=248 ratio=24% | NON-MAINS (deletion-gate denominator, MAINS-OFF excluded by design): fires=51/217 ratio=24% | MULTI-SOURCE events=12 | SELF-FILL fires=2 unconfirmed-by-any-other-source=0 | BELLS-MISSING=2 [BONVRB,MALKAZ] | HALT-MIN=0.0 UNBOOKED-FILLS-BOOKED=0 (watch: night-over-night drops + uncovered live matches are named here, not a week later)

OS SHADOW 2026-07-26: n=11692 sites={'v4_place': 680, 'move_repost': 141, 'hold_review': 10871} | placement agree(±1c)=47 diverge=114 | divergence classes: {'climb_side|hold_window': 54, 'decay_side|hold_window': 40, 'mains_join|hold_window': 12, 'climb_side|resting_window': 8} | hold: {'reviews': 10871, 'quiet': 298, 'floor_miss': 1935, 'both': 70, 'diverge': 2093, 'floor_unevaluable': 0, 'pre_instrument': 0} | cap-sensitivity: DEFERRED (joint-shadow n>=30 gate, operator 07-09)

## PERCLASS 20260726 (era post-seal-20260720) — COMBINED PRIMARY (ruling 07-20 PM): sub-par(<=97)=pass; dual-negative=mastery meter
slate: 125 big-4 events · 111 scored pairs · skips {'thin_tape': 12, 'one_leg_file': 2, 'dead_band': 0, 'no_tape': 0}
- FLAT-FLAT (SEALED b2f0b670; capture standard): **COMPLETION 4/29 = 14% x QUALITY 4/4 = 100% -> JOINT FAIL (bar 70/70)** · tiers {'<=93': 4} · MASTERY dual-neg 0% · medPairD -13
- MIRROR (REFUSE; fader drill on the mastery meter): pairs 46 duals 31 (completion 67%) · SUB-PAR(<=97) 1/31 = 3% -> FAIL · tiers {'98-100': 3, '<=97': 1, '>100': 27} · MASTERY dual-neg 0% (meter, never pass/fail) · medPairD +16
- NEITHER (counted apart): pairs 36 duals 23 (completion 64%) · SUB-PAR(<=97) 2/23 = 9% -> FAIL · tiers {'98-100': 3, '<=93': 2, '>100': 18} · MASTERY dual-neg 0% (meter, never pass/fail) · medPairD +7
- COMPLETION (volume drill): sub-par duals 7 / 111 slate pairs = 6.3%
  - flat_flat|ATP_CHALL: pairs 17 duals 3 (completion 18%) · SUB-PAR(<=97) 3/3 = 100% -> PASS · tiers {'<=93': 3} · MASTERY dual-neg 0% (meter, never pass/fail) · medPairD -15
  - flat_flat|ATP_MAIN: pairs 3 duals 1 (completion 33%) · SUB-PAR(<=97) 1/1 = 100% -> PASS · tiers {'<=93': 1} · MASTERY dual-neg 0% (meter, never pass/fail) · medPairD -7
  - flat_flat|WTA_CHALL: pairs 3 duals 0 — NO DUALS
  - flat_flat|WTA_MAIN: pairs 6 duals 0 — NO DUALS
  - mirror|ATP_CHALL: pairs 22 duals 12 (completion 55%) · SUB-PAR(<=97) 0/12 = 0% -> FAIL · tiers {'98-100': 2, '>100': 10} · MASTERY dual-neg 0% (meter, never pass/fail) · medPairD +6
  - mirror|ATP_MAIN: pairs 10 duals 7 (completion 70%) · SUB-PAR(<=97) 0/7 = 0% -> FAIL · tiers {'>100': 7} · MASTERY dual-neg 0% (meter, never pass/fail) · medPairD +29
  - mirror|WTA_CHALL: pairs 12 duals 10 (completion 83%) · SUB-PAR(<=97) 1/10 = 10% -> FAIL · tiers {'<=97': 1, '>100': 9} · MASTERY dual-neg 0% (meter, never pass/fail) · medPairD +32
  - mirror|WTA_MAIN: pairs 2 duals 2 (completion 100%) · SUB-PAR(<=97) 0/2 = 0% -> FAIL · tiers {'98-100': 1, '>100': 1} · MASTERY dual-neg 0% (meter, never pass/fail) · medPairD +10
  - neither|ATP_CHALL: pairs 17 duals 10 (completion 59%) · SUB-PAR(<=97) 2/10 = 20% -> FAIL · tiers {'98-100': 1, '<=93': 2, '>100': 7} · MASTERY dual-neg 0% (meter, never pass/fail) · medPairD +1
  - neither|ATP_MAIN: pairs 6 duals 4 (completion 67%) · SUB-PAR(<=97) 0/4 = 0% -> FAIL · tiers {'>100': 4} · MASTERY dual-neg 0% (meter, never pass/fail) · medPairD +9
  - neither|WTA_CHALL: pairs 7 duals 6 (completion 86%) · SUB-PAR(<=97) 0/6 = 0% -> FAIL · tiers {'98-100': 1, '>100': 5} · MASTERY dual-neg 0% (meter, never pass/fail) · medPairD +56
  - neither|WTA_MAIN: pairs 6 duals 3 (completion 50%) · SUB-PAR(<=97) 0/3 = 0% -> FAIL · tiers {'98-100': 1, '>100': 2} · MASTERY dual-neg 0% (meter, never pass/fail) · medPairD +7
- SEAL-DECAY TRIPWIRE: **SEAL-DECAY — RED; operator ruling required; never auto-disarm** [rolling7 COMPLETION 20/112 = 18% < 70%]

GUN SCORECARD 20260727: ATP_CHALL n=17 FRESH-within±3min=1/7 med|Δ|=5.4m catchup=0 suspect=[KRANIC,SAHTUR,VRBJAN] unjoinable=7 misses=[] | ATP_MAIN n=9 FRESH-within±3min=0/0 med|Δ|=-- catchup=0 suspect=[MAYPAS,WONBLA] unjoinable=7 misses=[] | ITF_M n=12 FRESH-within±3min=0/0 med|Δ|=-- catchup=0 suspect=[] unjoinable=12 misses=[] | ITF_W n=11 FRESH-within±3min=0/0 med|Δ|=-- catchup=0 suspect=[] unjoinable=11 misses=[] | WTA_CHALL n=7 FRESH-within±3min=4/5 med|Δ|=1.2m catchup=0 suspect=[] unjoinable=2 misses=[] | FIRES-vs-SLATE: fires=56 tracked_events=163 ratio=34% | NON-MAINS (deletion-gate denominator, MAINS-OFF excluded by design): fires=47/146 ratio=32% | MULTI-SOURCE events=11 | SELF-FILL fires=1 unconfirmed-by-any-other-source=0 | BELLS-MISSING=3 [BROMOU,SHAHIJ,SINREJ] | HALT-MIN=0.0 UNBOOKED-FILLS-BOOKED=0 (watch: night-over-night drops + uncovered live matches are named here, not a week later)
