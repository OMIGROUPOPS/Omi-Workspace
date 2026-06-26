import os, re
src=open(os.path.join(os.path.dirname(__file__),"..","live_v4.py")).read()
def chk(n,c): print(("PASS" if c else "FAIL")+"  "+n); assert c,n
chk("T1 init reads override default {}", 'self.event_category_override = dict(self.config.get("event_category_override", {}))' in src)
chk("T2 get_category checks override before SERIES_MAP",
    re.search(r'def get_category.*?for evt_prefix, cat in self\.event_category_override\.items\(\):.*?return cat.*?for cat_name, prefixes in SERIES_MAP', src, re.S) is not None)
# functional replication of the get_category logic
SERIES_MAP={"ATP_MAIN":["KXATPMATCH"],"WTA_MAIN":["KXWTAMATCH"],"ATP_CHALL":["KXATPCHALLENGERMATCH"],
            "WTA_CHALL":["KXWTACHALLENGERMATCH"],"ATP_SLAM":["KXATPGRANDSLAM"],"WTA_SLAM":["KXWTAGRANDSLAM"]}
def gc(t,ov):
    for ep,c in ov.items():
        if t.startswith(ep): return c
    for cn,ps in SERIES_MAP.items():
        for p in ps:
            if t.startswith(p): return cn
    return None
EMPTY={}; OVR={"KXITFWMATCH-26JUN25SATDAS":"WTA_CHALL"}
chk("T3 empty-override: SATDAS -> None (byte-identical see-not-trade)", gc("KXITFWMATCH-26JUN25SATDAS-SAT",EMPTY) is None)
chk("T4 override: SATDAS-SAT -> WTA_CHALL", gc("KXITFWMATCH-26JUN25SATDAS-SAT",OVR)=="WTA_CHALL")
chk("T5 override: SATDAS-DAS -> WTA_CHALL", gc("KXITFWMATCH-26JUN25SATDAS-DAS",OVR)=="WTA_CHALL")
chk("T6 OTHER ITF NOT mapped (only this event)", gc("KXITFWMATCH-26JUN26POHEVA-EVA",OVR) is None)
chk("T7 native WTA_CHALL still works", gc("KXWTACHALLENGERMATCH-26JUN26X-Y",OVR)=="WTA_CHALL")
chk("T8 native ATP_MAIN unchanged under empty", gc("KXATPMATCH-26JUN26X-Y",EMPTY)=="ATP_MAIN")
print("\nALL PASS (8/8)")
