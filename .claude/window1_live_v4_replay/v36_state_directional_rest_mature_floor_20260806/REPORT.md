# V36 state-directional rest + mature-floor take

V36 is derived from V35 0799fba887f1d1e84f9c0ef3e73096fd9d76019e. FALLING rests obey the V32 no-chase law and never walk upward into a live decline. RISING/SETTLED rests preserve V35 bid-minus-one tracking. A floor take requires no new-low evidence receipt inside the existing 300-second state horizon; maturity is re-evaluated only on book receipts, never by a timer. A non-falling qualifying shelf can replace an older minimum only when it was causally re-formed and has matured. Strict/census fill laws, pair cap, hard V3 PRE-MATCH edge, and close-free grading remain unchanged.

- Status: REJECTED_V36_BAR_V35_REMAINS_OPERATIVE.
- STRICT completed / under par: 270 / 270; V35: 264 / 264; V34-W1: 254 / 254.
- STRICT frontier <=93 / <=95 / <=97 / <100: 9 / 20 / 77 / 270.
- CENSUS completed / under par: 548 / 548; V35: 550 / 550; V34-W1: 279 / 279.
- STRICT maker / taker: 153 / 882. Falling maker fills: 24; positive adverse tail: 24; total cents: 323.
- STRICT bleed conversions: {"REST_STARVED":42,"STATE_MISLABEL":38,"TAKE_PREEMPT":26,"CAP_STRANGLED":2}; new losses from V34 completed: 92.
- CENSUS bleed conversions: {"REST_STARVED":125,"TAKE_PREEMPT":80,"STATE_MISLABEL":68,"CAP_STRANGLED":32}; new losses from V34 completed: 36.
- Named checks: {"GANJAN_recovers_toward_23":false,"FETPIE_completes":false,"JONSPI_completes":false,"ARNROM_38_plus_56_equals_94":true,"KRALOR_LOR_keeps_5":true,"BOSCOP_BOS_keeps_32":true,"ARNROM_ROM_38_zero_regret":true}.
- Post-edge machine rows: 0. Close fields consumed by grading: 0.

The supplied short identity 84b455c5 remains unresolved. The actual 804-row ledger is bound through Git path history at 224417da642a9f378a0d83f76edffe9890cb4a6f, SHA-256 1d7fe6a56837ceb0c0b8c932a05daecacc0cefbea94384e16c84975f2ed98ce5.
