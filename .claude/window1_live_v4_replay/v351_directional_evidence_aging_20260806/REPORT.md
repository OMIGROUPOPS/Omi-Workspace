# V35.1 directional evidence aging

V35.1 makes one repair to V35 0799fba887f1d1e84f9c0ef3e73096fd9d76019e: the all-time downward evidence minimum remains authoritative only while the side's combined state is FALLING. Otherwise, downward receipts remain authoritative only inside the existing 300-second receipt horizon; after they age and the side is RISING or SETTLED, only a qualifying-ask floor genuinely re-formed by the current non-falling receipt can replace the stale minimum. An older descent-origin shelf cannot be relabeled by a later flicker. The transition is evaluated only on book receipts. There is no timer or wall-clock action trigger. Living-rest mechanics, strict/census fill laws, pair cap, hard V3 PRE-MATCH edge, and close-free grading are unchanged.

- STRICT completed / under par: 283 / 283; V35: 264 / 264; V34-W1: 254 / 254.
- CENSUS completed / under par: 552 / 552; V35: 550 / 550; V34-W1: 279 / 279.
- R3 same-window completed / under par: 229 / 217; original joint reference: 68.
- STRICT maker / taker: 143 / 907.
- CENSUS maker / taker / one-cent conversion: 26 / 709 / 604.
- STRICT bleed conversions: {"REST_STARVED":53,"STATE_MISLABEL":42,"TAKE_PREEMPT":25,"CAP_STRANGLED":2}; new losses from V34 completed: 93.
- CENSUS bleed conversions: {"REST_STARVED":129,"TAKE_PREEMPT":80,"STATE_MISLABEL":70,"CAP_STRANGLED":32}; new losses from V34 completed: 38.
- STRICT rest exact tracking: 2020817/2020817; max gap 0c; reprices up/down 439098/204682.
- CENSUS rest exact tracking: 1607376/1607376; max gap 0c; reprices up/down 331167/165570.
- ARNROM STRICT: 38 + 56 = 94, under par true.
- Post-edge machine rows: 0. Close fields consumed by grading: 0.

The supplied short identity 84b455c5 remains unresolved. The actual 804-row ledger is bound through Git path history at 224417da642a9f378a0d83f76edffe9890cb4a6f, SHA-256 1d7fe6a56837ceb0c0b8c932a05daecacc0cefbea94384e16c84975f2ed98ce5.
