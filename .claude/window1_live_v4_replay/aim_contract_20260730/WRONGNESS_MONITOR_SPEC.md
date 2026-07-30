# Wrongness monitor

The monitor sits between consultation, decision, and order effect. It does not
judge P&L and it does not wait for an incident.

## Surface alarm

Every fitted artifact must carry a machine-readable fit-key contract. Every
consultation emits the key it actually used. Before the value can influence an
order, the monitor compares them field for field.

- missing fit contract → `FIT_CONTRACT_MISSING`, BLOCK;
- different anchor source, timestamp semantics, cell definition, category, or
  fallback branch → `FIT_CONSULT_KEY_MISMATCH`, BLOCK;
- fitted row `n < 20` or missing → `FITTED_ROW_THIN`, BLOCK.

The alarm line contains surface hash/version, exact fitted key, exact
consulted key, row `n`, decision ID, event, ticker, and consultation timestamp.

## Verdict alarm

Every actionable verdict receives a decision ID and declares its required
effect:

- `DROP` / `REFUSE` must terminate as `REFUSE`;
- an authorized price must terminate as `POST` at that exact price;
- a hold must terminate without cancel/repost;
- an explicit safety veto may replace an action only if the veto and its
  evidence are linked to the same decision ID.

The posting path consumes the decision ID. A different effect raises
`VERDICT_IGNORED`; a different post price raises
`AUTHORIZED_PRICE_IGNORED`; an order without a verdict raises
`EFFECT_WITHOUT_VERDICT`; a verdict with no terminal effect raises
`VERDICT_WITHOUT_EFFECT`.

## Operating behavior

All five alarms are loud structured events and deployment-blocking counters.
Fit/key mismatch and thin rows fail closed before placement. Verdict/effect
mismatches also trip the existing conception halt, because once the path has
proved it cannot honor its own decision, continuing to post is unsafe.

The pure monitor implementation is in `arb-executor/wrongness_monitor.py`.
It is not armed in live code in this change; wiring waits for the new lawful
surface and typed `AuthorizedEntryIntent`, so the monitor cannot legitimize
the current invalid tables by merely observing them.
