# Window-1 V23 immediate pair-cap ruling

V23 is one isolated replay variant of frozen A/V20. At a strictly later second-leg placement, it binds the known first-leg credited fill with `leg2_bid <= 99 - leg1_fill`. A cap at or above the current live bid may rest without chasing and requires strictly later qualifying-ask evidence for credit. A cap already below the current live bid abstains. Eleven same-second two-leg actions have no strictly prior credited first fill and are explicitly not armed.

On the independently audited 1,608-leg close ruler, JOINT is V19 `24`, A `33`, and V23 `45`. Relative to the replay-close ruler this is `+5`, `+6`, and `+8`; V23 is `+12` JOINT versus audited A. V23 has 204 completed pairs, 193 under par, 45 both strictly below audited own closes, and 88 strict carried pairs. The cap census is 161 resting-cap placements, 160 immediate abstentions below the live bid, 139 non-binding placements, and 11 same-second not-armed pairs. The frozen Phase-0 25 par failures are 18 at 100 and 7 at 101.

The close audit recovers 250 replay-null closes, leaves 51 legs without a lawful in-window true print, and changes the ruler without entering policy decisions.

The V22 Phase-1 close-landing estimator remains `NOT_BOUND` and was not run. The current V13 shape library has 39 shapes, 23 signable shapes, 1,343 assigned training legs, and 1,086 signable members, but it emits no numeric own-close landing distribution: numeric coverage is zero in every category. The separate V17 ordering surface has 339 climber-first identity-unresolved events; that is an ordering/direction identity hole, not a latent close estimate. A future estimator requires a separately ratified, training-only conditional landing distribution and thin/unresolved abstention law.

Immutable artifacts:

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/8b508215a10e8ed0950ff186e745c48b48c7d42d/.claude/window1_live_v4_replay/pair_cap_v23_audited_close_20260804/V23_VS_A.json

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/8b508215a10e8ed0950ff186e745c48b48c7d42d/.claude/window1_live_v4_replay/pair_cap_v23_audited_close_20260804/AUDITED_CLOSE_REGRADE.json

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/8b508215a10e8ed0950ff186e745c48b48c7d42d/.claude/window1_live_v4_replay/pair_cap_v23_audited_close_20260804/FRONTIER.json

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/8b508215a10e8ed0950ff186e745c48b48c7d42d/.claude/window1_live_v4_replay/pair_cap_v23_audited_close_20260804/REGRET_GAUGE.json

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/8b508215a10e8ed0950ff186e745c48b48c7d42d/.claude/window1_live_v4_replay/pair_cap_v23_audited_close_20260804/PHASE0_25_PAR_FAILURE_DISPOSITION.json

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/8b508215a10e8ed0950ff186e745c48b48c7d42d/.claude/window1_live_v4_replay/pair_cap_v23_audited_close_20260804/V22_PHASE1_LANDING_ESTIMATOR_SPEC.json

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/8b508215a10e8ed0950ff186e745c48b48c7d42d/.claude/window1_live_v4_replay/pair_cap_v23_audited_close_20260804/SOURCE_HASH_MANIFEST.json

Independent close ruler:

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/50ce0f4940c461cf0b6fa1b79000d96b335cd601/.claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/INDEPENDENT_CLOSE_AUDIT_1608.csv

V23 is a development replay result, not holdout validation or deployment authority. V22 Phase 1 awaits explicit ratification.
