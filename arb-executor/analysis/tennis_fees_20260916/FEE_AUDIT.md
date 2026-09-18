# Tennis entry-fee audit — September 16, 2026

The official July 7 fee schedule lists maker/taker multipliers in that order:

> KXATPMATCH ATP Tennis Match 1 1
>
> KXWTAMATCH WTA Tennis Match 1 1

[Official schedule, pages 1, 5 and 10](https://kalshi.com/docs/kalshi-fee-schedule.pdf).

For one contract priced at p dollars, main-tour maker fee is 0.0175 p(1-p) dollars; taker fee is 0.07 p(1-p). Challenger and ITF maker multipliers default to zero; taker multipliers are one. No maker charge without a fill.

## Dates and evidence

Saved public series metadata and historical fee-change responses agree with that schedule. KXATPMATCH and KXWTAMATCH report the maker-fee regime beginning November 15, 2025, with no subsequent changes returned. Challenger and ITF return quadratic taker-only schedules and empty change histories. The served PDF is effective July 7, covering the studied July games; exact July 1–6 rounding was not independently archived. Current metadata was checked September 16 local time. See RECEIPT.json for response hashes and URLs. PDF download returned HTTP 429; its text was verified through the web PDF reader, not a locally hashed copy.

## Rounding and ruler

[Official rounding documentation](https://docs.kalshi.com/getting_started/fee_rounding) distinguishes direct-member 0.01-cent balance precision from non-direct-member 1-cent precision, with per-order rounding accumulation. For the single integer-cent contract modeled here, round the model fee upward to the respective balance precision. At 50 cents, main-tour maker charge is 0.44 cents / 1 cent; taker charge is 1.75 cents / 2 cents. Account type, negotiated terms, rebates and intermediary extras are unverified, so both scenarios are shown—not asserted as account debits.

The ruler preserves gross corrected W1-close minus entry; subtracts entry fees on every filled leg, including one-sided positions; and reports net marked-to-close value. A close mark is not an executed exit. No exit fee or executable closing price is invented. Original capture-only reports remain capture-only, now less all entry fees; they are not relabeled full P&L.

## Restatement coverage

FEE_RESTATEMENTS.md contains 696 separately identified table groups / 219,063 saved outcome records: conduct, ceilings, sentence/calibration/first-bind/promise tests, full-receipt feature MAIN, both atlas screens, four-way attribution, reach-map and close-delta policies, all five-game combinations and handoff variants. Frozen June remains separate. Original reports are untouched and remain gross; the addendum is the fee accounting. Original four-way offered-game capture totals are asserted unchanged before fee subtraction.

This is not a claim that every historical repository artifact or deployed face has been rewritten. Forecast-only statistics are unaffected. Unlinked legacy monetary tables must not be called net. Five unscorable games stay unknown. Full input/output hashes and coverage limits are in RESTATEMENT_RECEIPT.json.
