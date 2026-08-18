# V52r Iteration - assembled policy

V52r is an operator-selected assembly over adopted V52l. Recognition is the pinned TRD5 frontier point using V52q's corrected spread-settle anchor: after max(causal onset, formation end), the first directional call with five post-onset trades binds and is held until the same instrument flips. ROLE_DOWN alone targets the running post-onset session low minus one cent, re-evaluated as new lows print and bounded by the current touch and clause 6. ROLE_UP, ROLE_STILL, and ABSTAIN use V52l unchanged. V52m/n/p/q remain observations, not decision inputs.

- Cohort: 5 pins + 25 fresh deterministic category x census-stamp games; seed 5b7d1be463f09af002f9350bd3057c2ad36b62e25ffb108c4d80f0c2b9acc0ff; every V52b-q fresh overlap is zero.
- Recognition source: 71de534a3f9e21faf569cd487d9aae735a084e7a/a002897e8956e1115a028eb120caf9f164215c0982378c7c6fbd757af49bf68e; target source: ab609761c5df44097f46ad2364f539bbd0751d54/60ed459127f4e996d551a21844f77e317426242b23610f55437575b2de8b5c8e; fitted constants introduced here 0.
- Runtime/offline corrected-anchor parity: 133074/133074 (1); claim >=99% true.
- Bound coverage: 26/58 (0.4482758620689655); claim >=85% false.
- Held-role accuracy: 13/26 (0.5); claim >=90% false.
- DOWN fills 6; fill-floor {"n":6,"null_n":0,"sum":5,"min":0,"p25":0,"median":0,"p75":2,"p90":3,"max":3}; median <=2c true; kiss 4/6 (0.6666666666666666); claim >=50% true.
- Up/still preservation 37/37; preserved true.
- Mean banked delta: V52l 2.933333333333333c; V52r 2.875c; >2.4c true.
- One-sided exposure: created 0, resolved 1; both clocks are present on every role receipt true.
- Pins lawful true; REFLEX_POST 0; assertions PASS.
- Four-state observation: V52l {"COMPLETE_AT_DELTA":15,"PARTIAL_FOR_REASON":13,"NEITHER_FOR_REASON":1,"UNKNOWN_BELL_NON_GRADEABLE":1}; V52r {"COMPLETE_AT_DELTA":16,"PARTIAL_FOR_REASON":12,"NEITHER_FOR_REASON":1,"UNKNOWN_BELL_NON_GRADEABLE":1}. Claims are reported exactly as landed, never forced.
- No full-804, sealed, deployment, authorization, live, order, position, or holdout action occurred.
