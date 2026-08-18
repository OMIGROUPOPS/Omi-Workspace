# V52q Iteration - anchor correction

V52q changes one role-instrument input over frozen V52p: post-formation open is the published spread-settle midpoint at formation end, and the causal price series is floored at formation end. Ripeness gates, DOWN depth targeting, UP immediacy, V52l fallback, clauses 1-6, referee, trades-as-truth crediting, scavenger OFF, and REFLEX_POST=0 are frozen.

- Cohort: 5 pins + 25 fresh deterministic category x census-stamp games; seed a357bea450f69f2699d3c20a6fdc86a062cbacfe980ca0576442bae814d89563; every V52b-p fresh overlap is zero.
- Corrected anchor: e269779b0ec025d55f67d576e3cfb0cb575d5890/5d821226544f9e1891d0572b82386ac4907dc0692c0c91852d146105a446d599; discrepancy receipt 620fe4c1/6a7be3e48d0dad8830fdf54cbdb1313c1077e340a6b7c569d0c3412c2a782469; price-series floor FORMATION_END_INCLUSIVE.
- Runtime/offline parity on ungated receipt calls: 139430/139430 (1); >=99% true.
- Bound coverage at terminal: 23/60 (0.38333333333333336); claim >=60% false.
- Accuracy on called truth-role legs: 16/23 (0.6956521739130435); claim >=90% false.
- ROLE_DOWN fills: 4; floor gap {"n":4,"null_n":0,"sum":-2,"min":-3,"p25":-3,"median":-1,"p75":1,"p90":1,"max":1}; >0 and <=1.5c median true.
- Up/still preservation: 38/39; preserved false.
- Mean banked delta: V52l 1.625c; V52q 1.8c; >2.14c false.
- One-sided exposure: created 2, resolved 4, created durations {"n":2,"null_n":0,"sum":61056.60700011253,"min":168.42700004577637,"p25":168.42700004577637,"median":168.42700004577637,"p75":60888.18000006676,"p90":60888.18000006676,"max":60888.18000006676}.
- Pins lawful true; REFLEX_POST 0; assertions PASS.
- Four-state observation: V52p {"PARTIAL_FOR_REASON":14,"COMPLETE_AT_DELTA":12,"NEITHER_FOR_REASON":3,"UNKNOWN_BELL_NON_GRADEABLE":1}; V52q {"COMPLETE_AT_DELTA":15,"PARTIAL_FOR_REASON":11,"NEITHER_FOR_REASON":3,"UNKNOWN_BELL_NON_GRADEABLE":1}. Outcomes are observations only; pre-stated claims are reported, never forced.
- No full-804, sealed, deployment, authorization, live, order, position, or holdout action occurred.
