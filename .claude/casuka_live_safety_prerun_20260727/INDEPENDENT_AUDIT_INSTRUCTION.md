# Independent audit instruction

Fetch `codex/casuka-live-safety-repair` and audit its reported tip as an
additions-plus-focused-engine-repair child of
`a4996dd00e82ed3534f97a09251697f1d82dbbab`.

Bind the controlling reproduction commit
`b442908f3b253d1e13d5b2a5e93c3dbf0491320d`, report blob
`c31f208ef86f4831352f6dffe0cc958459d82fc3`, and packet blob
`cd41db2eaf0c37a2ac532682ecaade08c33649f7`.

Independently verify:

1. all live-engine changes are confined to D1 exit-intent serialization,
   D2 the final pre-POST sell exchange-truth refusal, and D3 pair-classifier
   booked-plus-unsettled truth;
2. every sell submission still has exactly one API POST chokepoint and that
   the authoritative position/resting-sell read immediately precedes it;
3. heal→top-up and top-up→heal both end with exactly one resting five-lot;
4. no proposed sell can make resting sells exceed authoritative held quantity;
5. `entry_resting`/settled/zero-booked stale state cannot classify `filled`
   or create `pair_incomplete`;
6. all 12 focused fixtures and the seven named inherited suites pass;
7. the complete inherited failure set is unchanged from the exact parent;
8. hashes and artifact receipts reconcile;
9. no deployment, live access, restart, configuration change, order mutation,
   position mutation, or T2 worktree change occurred.

Do not deploy or mutate any live surface. Return PASS/BLOCKED with exact
reproduction evidence to the operator.
