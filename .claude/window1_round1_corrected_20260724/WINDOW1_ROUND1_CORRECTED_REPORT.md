# Round-1 Window-1 corrected record

Status: **controlling correction** to results commit `f7cd420951f074104dbc602b84137c5eed7455da`
under independent audit `024f03bb5b1944bae39ad5afef6ee019ef5dc06d`. No strategy candidate was
rerun and no score was recomputed from a new order stream.

## Selected result preserved

- D = 804
- C = 10
- PC = 9
- S = 9
- IC = 4
- selected candidate = `drift_cohort_orientation__walk__reaim`

These values independently reproduce from the 804 selected-event rows.

## Corrected failure census

The former `nonfill = 678` headline is replaced by:

- 582 genuine zero-fill events;
- 84 naked single-leg fills;
- 12 zero-length Window-1 opportunities.

The 102 censored events remain separate: 85 start-boundary censored,
11 missing-feature/no-causal-birth-book censored, and 6 queue-ambiguous.
Feature absence is never counted as a nonfill.

## Scope of the optimistic bound

The 26 optimistic completions bound only the selected candidate's
counterfactual order stream and, because it was the grid maximum, the
frozen 24-candidate Round-1 grid, including its lawfully allowed
post-start intervals. It is not a market ceiling, a data ceiling, or a
bound on a candidate with different per-leg timing or price expression.

## T8/T6 lookahead correction

The following comparison rows are struck from lawful comparison:

- `pair_divot_core__park__hold`
- `pair_divot_core__park__reaim`
- `pair_divot_core__walk__hold`
- `pair_divot_core__walk__reaim`

They posted at T8 but priced their sealed-depth term with a
`called_band` derived at T6. The selected candidate is unaffected.
No replacement values are asserted without a newly frozen rerun.

## Nominal OS-family capability

| family | loaded | available | evaluated | decision-changing | selected |
|---|---:|---:|---:|---:|---:|
| pair_divot_core | True | False | True | unusable | False |
| drift_cohort_orientation | True | True | True | True | True |
| mirror_deceleration | True | True | True | False | False |
| dynamic_recut_atlas | True | True | True | True | False |
| causal_micro_pressure | True | True | True | True | False |
| full_chronological_stack | True | True | True | True | False |

The six family names therefore did not represent six independently
decision-changing behaviors. Mirror was decision-identical to the
selected drift family; the pair family is ineligible because of lookahead.

## Feature-family capability

| family | loaded | available | evaluated | decision-changing | selected |
|---|---:|---:|---:|---:|---:|
| pair_law | True | True | True | True | True |
| first_fill_sibling_response | True | partial | True | True | True |
| sealed_bands | True | partial | True | False | False |
| dual_divot_steering_and_catch | True | partial | True | True | True |
| drift_recognition | True | partial | True | False | False |
| cohort_steering | True | partial | True | False | False |
| orientation_prior | True | partial | True | False | False |
| walk_park_posture | True | partial | True | True | True |
| riser_deceleration_mirror_seesaw | True | partial | False | False | False |
| dynamic_floor_and_recut_cells | True | partial | True | True | False |
| atlas | True | partial | True | True | False |
| reach | True | partial | True | False | False |
| shape_corpus | True | False | False | False | False |
| bookmaker_fv | True | partial | True | True | False |
| pinnacle | False | False | False | False | False |
| causal_bbo | True | partial | True | True | True |
| top_five_pressure | True | partial | True | True | False |
| true_print_flow | True | True | True | True | True |
| own_order_fingerprints | True | partial | True | False | False |
| real_start_guard | True | partial | True | True | True |
| raw_ws_full_depth | False | False | False | False | False |

Here `decision-changing` means an observed lawful Round-1 grid decision
or result changed through that actuator; `selected` means the selected
candidate actually used it to change at least one eligible decision.

## Unavailable or non-actuating Round-1 machinery

- full depth: unavailable; snapshot ancestry and gap-free sequence
  reconstruction were not proved;
- Pinnacle: unavailable (zero causal rows);
- shape corpus: unavailable without an independent non-AIM causal mapping;
- reach and own-order fingerprints: loaded/coverage-evaluated but inert;
- asynchronous per-leg divot timing and exact one-cent non-self walk:
  absent from Round 1 and therefore the central Round-2 repair.

July 24-26 remains unopened. This correction touched no production, live,
configuration, order, position, settlement, exit, DCA, or Window-2 surface.
