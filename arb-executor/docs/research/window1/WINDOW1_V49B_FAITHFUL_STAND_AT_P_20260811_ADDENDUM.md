# V49b faithful stand-at-P

Date: 2026-08-11

Status: PASS / RATIFIED ON MECHANISM-BOUND INSTRUMENTS. No deployment or live cutover is authorized.

V49b is the faithful re-open of the V49 substitution defect identified by
`bc0ce289`: on a frozen doctrine leg whose own tape has causally evidenced P,
the rest is posted at P itself. There is no bid-minus-one transform and no
synthetic-book substitution. If exact P conflicts with the pair cap or
post-only sanity after authority exists, the leg abstains rather than falling
back to another price. V47 is unchanged where doctrine authority is absent.

The frozen development replay contains 804 games and 1,608 legs. V47
reproduced exactly at 396 completed/under-par pairs, frontier
52/71/142/396/396, 331 strict completions, and +1,774 cents true book. V49b
produced 405 completed/under-par pairs, frontier 53/73/144/405/405, 330 strict
completions, and +1,778 cents true book. The strict build-verification count is
one below V47's 331; it is reported beside market scoring and is not used as a
market-value ruler under CANON's two-ruler law.

The mechanism ledger binds 81 games and 93 doctrine legs. It contains 173
authorized placement/reprice actions: all 173 are `AT_P`; there are zero
`BID_MINUS_ONE` rows and zero exact-target invariant violations. Ten doctrine
legs improve at or below their P and no previously successful bound doctrine
leg regresses. That is the mechanism-bound ratification.

The analytical 81-game ceiling is not claimed as captured. Only 9 of the 81
games completed with every doctrine leg at its own P or better. All remaining
identities are frozen in the outcome ledger. The nine incremental completed
pairs are shallow-skewed: two are at or below 97, with combined costs
91/98/99/99/99 at min/p25/median/p75/max. Aggregate <=97 depth share is 35.6%
for V49b versus 35.9% for development V47 and 25.3% for sealed V47.

The REGRET GAUGE uses the direct full-tape true-trade minimum and is stamped
`OPTIMISTIC_EX_POST_TRUE_TRADE_FLOOR`. The convicted `d3db740f` causal-floor
table is consumed by zero V49b decisions.

Two clean builds compared 39 pre-determinism artifacts byte-for-byte with zero
mismatches. Focused V47, V48, V49, and V49b policy tests pass. Forbidden access
is zero: no holdout policy evaluation, live access, network runtime, order,
position, exit, settlement, DCA, or deployment action occurred.

Controlling package:

`.claude/window1_live_v4_replay/v49b_faithful_stand_at_p_20260811/`
