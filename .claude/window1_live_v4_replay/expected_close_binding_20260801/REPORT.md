# Window-1 expected-close binding audit

Score-free. Fit is July 12-17; calibration is disjoint July 18-20. No five-game or 804 policy replay was run.

## Binding result

**NOT_BOUND** — The disjoint internal estimator beats the current-ask baseline in 0/16 category-price cells, 10 cells are thin, 301 legs lack close labels, and external-book predictive comparison is impossible because fresh July coverage is zero.

## External books

Fresh Pinnacle/Betfair/Matchbook decision-time reads: 0/1608. External predictive comparison is NOT_MEASURABLE_ZERO_FRESH_EXTERNAL_READS.

## Internal candidate

The candidate returns a weighted empirical distribution of own-close minus current ask. It consumes current bid/ask/spread/dwell, receipt-identified true last trade, executed volume/cadence, quote cadence, scheduled clock, sibling book, and fit-only surviving quote shapes. Every training leg contributes at most one closest residual per query.

Post-fit labeled legs: 449; unlabeled: 109. The model beats the current-ask baseline on median absolute error in 0 of 16 category/price-region cells; predicted-edge >=15c rows: 0. Thin and non-thin cells are listed in the calibration artifact; no pooled performance metric is emitted.

## Decisions

- Fee-aware take: BLOCKED_EXPECTED_CLOSE_NOT_BOUND.
- First-leg commitment: BLOCKED_JOINT_SIBLING_REACH_AND_OPERATOR_RISK_NOT_BOUND.
- Take versus rest: BLOCKED_SELLER_PRINT_SHARE_IS_NOT_ORDER_FILL_PROBABILITY.
