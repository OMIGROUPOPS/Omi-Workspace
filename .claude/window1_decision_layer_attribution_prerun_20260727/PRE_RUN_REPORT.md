# Window-1 decision-layer attribution PRE-RUN

This additions-only package diagnoses the independently passed asynchronous
opportunity census V2. It neither constructs opportunities nor scores,
changes, ranks, or tunes a policy.

- Parent: `e60f6af4f6db5bab5b8a30704a0cb1fc98c774a7`
- Controlling independent PASS: `26dd6e5e19a7890f02b538cc8b14a900f36e5b2f`
- D: 804 per candidate
- Recovered candidate rows: 47 across 25 distinct games
- Shared recovered games: 22
- Macro-hold only recovered games: 0
- Macro-micro only recovered games: 3
- Never exposed / moved away / capacity unproved: 28 / 17 / 2
- Decision-layer counts: `{"LIVE_AIM_reprice":1,"capacity_measurement_unproved":2,"corridor_window_termination":8,"first_fill_sibling_response_failed_to_create_exposure":24,"headroom_reprice":8,"target_selection_never_included_lawful_X":4}`
- Qualifying episodes: 3,226 / 3,275 = 6,501
- Positive-d2 candidate episodes inside strict combined headroom: 6,310
- No-fill counterfactual event unions: 65 / 68
- No-fill shared / hold-only / micro-only games: 65 / 0 / 3
- All benchmark/performance metrics: null

Candidate rows, distinct games, episodes, price reach, capacity, policy
exposure, and counterfactual paths remain separate throughout.
