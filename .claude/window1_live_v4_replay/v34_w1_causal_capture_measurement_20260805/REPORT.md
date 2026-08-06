# V34-W1 causal capture measurement

The frozen V34 dual-side residency machine is replayed from each game's first two-sided book through the hard PRE-MATCH edge selected from REAL_START_LEDGER_V3 by exact_start_utc, else known_live_by_utc, else schedule_bound_utc. No action, state update, fill, cap arm, rest walk, or take occurs after that edge. Close values are telemetry only and are proven grade-invariant by deletion.

- STRICT completed / under par: 254 / 254.
- CENSUS completed / under par: 279 / 279.
- R3 same-window completed / under par: 229 / 217; original close-based reference: 68.
- Operator-named census-adjusted under-par offer: 680.
- STRICT maker / taker: 31 / 984.
- CENSUS maker / taker / one-cent census conversion: 6 / 958 / 77.
- Post-edge machine rows: 0.
- Full decision rows: 4508577; compact rows: 1608+1608.
- Full-life waited-and-lost at the hard edge: STRICT 318; CENSUS 311.

The supplied short identity 84b455c5 does not resolve as a Git object after fetch. The actual 804-row ledger is bound through Git path history at 224417da642a9f378a0d83f76edffe9890cb4a6f, SHA-256 1d7fe6a56837ceb0c0b8c932a05daecacc0cefbea94384e16c84975f2ed98ce5; no short identity was fabricated.
