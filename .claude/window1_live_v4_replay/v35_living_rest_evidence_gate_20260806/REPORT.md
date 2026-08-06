# V35 living rest + evidence gate

V35 repairs the V34-W1 rest and take authorities without changing the first-two-sided-book to V3 PRE-MATCH hard edge, strict/census fill laws, pair cap, dual-evidence state telemetry, or close-free grading. The living rest equals min(best_bid-1, pair cap) on every own-book receipt, up or down. Take authority ignores the state label and requires a ten-second, five-lot ask at or below the running seller-hit/qualifying-ask evidence floor. A newly formed qualifying-ask floor cannot authorize its own TAKE while FALLING quote/pressure evidence remains unabsorbed; an established floor is immediately takeable. Absorption is observed only on later receipts against the inherited 300-second state horizon; there is no timer or clock decision input.

- STRICT completed / under par: 264 / 264; V34-W1: 254 / 254.
- CENSUS completed / under par: 550 / 550; V34-W1: 279 / 279.
- R3 same-window completed / under par: 229 / 217; original joint reference: 68.
- STRICT maker / taker: 155 / 862.
- CENSUS maker / taker / one-cent conversion: 27 / 707 / 603.
- STRICT bleed conversions: {"REST_STARVED":46,"STATE_MISLABEL":39,"TAKE_PREEMPT":27,"CAP_STRANGLED":2}; new losses from V34 completed: 104.
- CENSUS bleed conversions: {"REST_STARVED":128,"TAKE_PREEMPT":80,"STATE_MISLABEL":70,"CAP_STRANGLED":32}; new losses from V34 completed: 39.
- STRICT rest exact tracking: 2004999/2004999; max gap 0c; reprices up/down 428465/197025.
- CENSUS rest exact tracking: 1603420/1603420; max gap 0c; reprices up/down 328663/164305.
- Post-edge machine rows: 0. Close fields consumed by grading: 0.

The supplied short identity 84b455c5 remains unresolved. The actual 804-row ledger is bound through Git path history at 224417da642a9f378a0d83f76edffe9890cb4a6f, SHA-256 1d7fe6a56837ceb0c0b8c932a05daecacc0cefbea94384e16c84975f2ed98ce5.
