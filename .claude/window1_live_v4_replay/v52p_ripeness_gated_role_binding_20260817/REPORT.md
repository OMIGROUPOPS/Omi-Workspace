# V52p Iteration - ripeness-gated role binding

V52p supersedes the V52m/n/o observation bindings while retaining them as controls. It preserves V52l behavior below the exact published ripeness gate. The candidate role is the benchmarked causal drift read; effective ripeness is max(class, category). ROLE_DOWN consumes the existing frequency-weighted category down-family depth aggregate; ROLE_UP is immediate evidence-backed; ROLE_STILL and below-gate reads retain V52l. No constants were introduced.

- Cohort: 5 pins + 25 fresh deterministic category x census-stamp games; seed 56305dc6bc335a7632a0439706183c2f36782e4c23c7fd187818ef9bf97f755a; every V52b-o fresh overlap is zero.
- Ripeness source: 41c1f7244af3afa4dade63bc9824808090ada41d/e2a216299804ba16b6dec4d1b0f09e60babbae2be6a6e59135629b1c5d3a3011; class gates {"ROLE_UP":0.023,"ROLE_DOWN":0.448,"ROLE_STILL":0.65}; category gates {"WTA_MAIN":0.206,"ATP_MAIN":0.351,"ATP_CHALL":0.703,"WTA_CHALL":0.964}.
- Bound coverage at terminal: 20/60 (0.3333333333333333); claim >=60% false.
- Accuracy on called truth-role legs: 11/20 (0.55); claim >=90% false.
- ROLE_DOWN floor gap: {"n":0,"null_n":0,"sum":0,"min":null,"p25":null,"median":null,"p75":null,"p90":null,"max":null}; <=1.5c median false.
- Up/still preservation: 38/38; preserved true.
- Mean banked delta: V52l 2.142857142857143c; V52p 2.142857142857143c; >1.94c true.
- One-sided exposure: created 0, resolved 0; pins lawful true; REFLEX_POST 0.
- Live realizability: verified/scheduled binding divergence 51384 receipts, 21 legs, 17 games; MATERIAL_LIVE_FIDELITY_ITEM. The observation uses verified spans; scheduled spans are the live proxy telemetry, not a behavior change.
- Four-state observation: V52l {"COMPLETE_AT_DELTA":14,"PARTIAL_FOR_REASON":8,"NEITHER_FOR_REASON":7,"UNKNOWN_BELL_NON_GRADEABLE":1}; V52p {"COMPLETE_AT_DELTA":14,"PARTIAL_FOR_REASON":8,"NEITHER_FOR_REASON":7,"UNKNOWN_BELL_NON_GRADEABLE":1}. Assertions PASS.
- Outcomes are observations only. No full-804, sealed, deployment, authorization, live, order, position, or holdout action occurred.
