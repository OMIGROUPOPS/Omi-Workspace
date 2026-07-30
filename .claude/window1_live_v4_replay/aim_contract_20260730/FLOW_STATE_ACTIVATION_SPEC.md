# Flow-state aim activation specification

## Current state

Vault §5 is not wired to entry activation.

The engine currently computes a partial flow read inside `_entry_dossier`,
after an aim already exists. It counts trailing-30-minute prints, taking the
maximum of the WebSocket count and a REST cache count. It then labels:

- ITF: quiet below 1.5 prints/30m, warm below 6, open at 6+;
- Challenger: quiet below 4 prints/30m, warm below 16, open at 16+;
- mains: no entry-flow model.

The deployed labels are `quiet/warm/open`; doctrine says
`QUIET/WAKING/OPEN`. More importantly, the deployed read contains no
spread-tightening state and does not gate aim activation. It informs the
dossier/reach law and several bell/corridor paths only.

## Causal flow vector

At each consultation, before any aim surface is read, compute one immutable
event-level flow vector from information available then:

- deduplicated non-self trade counts and rates over trailing 1, 5, 15, and
  30 minutes, for the pair and each leg;
- current bid, ask, and spread per leg;
- median spread over trailing 5, 15, and 30 minutes;
- spread slope and tightening ratio against the event's retained causal
  baseline;
- proportion of observations with a fresh two-sided book;
- source timestamps, staleness, trade IDs, and raw-message hashes;
- `NO_DATA` flags per component.

WebSocket and REST trade counts must be unioned by exchange trade ID. Taking
their maximum is not a lawful deduplication rule.

## Category state

Each of the six categories is fitted independently. Existing evidence is a
starting hypothesis, not a shared production threshold:

| Category | Existing print evidence | Existing spread evidence | Current honest status |
|---|---|---|---|
| ITF_M | QUIET 0/30m; WAKING 1–5; OPEN 6+ | dead lattice roughly 6¢, then 4→3→2¢ as participation arrives | print boundary fitted; joint print+spread transition must be fitted |
| ITF_W | QUIET 0/30m; WAKING 1–5; OPEN 6+ | same qualitative convergence, fit separately | print boundary fitted; joint transition must be fitted |
| ATP_CHALL | OPEN inflects at 16+/30m | generally already near 2¢ | fit independently; no borrowed WTA row |
| WTA_CHALL | OPEN inflects at 16+/30m | generally already near 2¢ | fit independently; no borrowed ATP row |
| ATP_MAIN | fill probability stayed roughly flat across volume states | usually tight/liquid but par-locked | `NO_FLOW_MODEL`; volume must not activate aim |
| WTA_MAIN | fill probability stayed roughly flat across volume states | usually tight/liquid but par-locked | `NO_FLOW_MODEL`; volume must not activate aim |

The fitted state vocabulary is:

- `NO_DATA`: required causal observations absent or stale;
- `QUIET`: no fitted transition evidence;
- `WAKING`: transition underway, not yet stable enough to activate;
- `OPEN`: fitted joint print/spread state supports aim activation;
- `RECEDING`: previously OPEN, now below the fitted persistence boundary.

Thresholds and hysteresis are table outputs with `n`; they are not code
constants.

## Consumption boundary

The integration point is immediately before `_selector_verdict`/the future
lawful aim-authority consultation, not inside the dossier and not after price
calculation.

1. Horizon/identity/book freshness gates establish that the event is eligible
   to be observed.
2. `_flow_state_at_consultation(event, timestamp)` emits the causal vector and
   fitted state.
3. `OPEN` permits the single named authority to consult its macro aim surface.
4. `QUIET`, `WAKING`, `RECEDING`, `NO_DATA`, an unfitted category, or a thin
   state row returns `DEFER_FLOW`; no order price is computed.
5. Flow state may activate or defer the macro aim. It may never change its
   cell, depth regime, or price.

This is `macro assumption × micro confirmation`: the historical surface
answers where; observed flow answers whether the market has opened.

## Fitting study

Use development tape only; the holdout stays sealed.

- Reconstruct the causal vector at every consultation/tick without looking
  forward.
- Use actual bell only as the lawful right-censoring boundary and outcome
  label, never as a live trigger.
- Hard-partition all six categories.
- Fit state transitions from joint print-rate and spread-tightening features.
- Label whether each canonical aim regime is subsequently touched before the
  lawful cutoff, plus first-touch latency.
- Prevent same-event leakage across train/evaluation folds; evaluate
  walk-forward by date.
- Report `n`, confidence interval, transition persistence, false-open rate,
  and the earliest-open tail per category.
- Require `n>=20` for every consumed state row. Thin rows stay `THIN`.
- Produce a source-hashed flow-state table and machine-readable fit-key
  contract for the wrongness monitor.

No clock-distance value and no per-minute historical timing statistic may be
consumed as the activation trigger.
