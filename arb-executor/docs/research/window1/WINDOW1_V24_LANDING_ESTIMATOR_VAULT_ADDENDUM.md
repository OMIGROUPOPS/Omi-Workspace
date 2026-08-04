# Window-1 V24 landing-estimator and phased-arming rulings

## Ruling 1 — V23 remains operative

V23 is the operative baseline and the non-regression floor: `45` audited JOINT pairs and `88` strict carried pairs. V24 is not promoted when either the JOINT floor or carried ceiling fails.

Source:

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/02ecf1d5858a4ec8244fa8c4d762e492f2756fc3/.claude/window1_live_v4_replay/landing_estimator_phased_arming_v24_20260804/FRONTIER.json

## Ruling 2 — the carry has no clock

No elapsed-time or wall-clock limit may enter a pair-lifecycle decision. The mirror bid lives or dies only by its own book against its aim, the causal read remaining resolved, its own fitted decline ordinal, and the guarded Window-1 boundary. Timestamps remain receipts and chronology proofs; they are not policy inputs. This extends the Granularity Law.

Source:

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/02ecf1d5858a4ec8244fa8c4d762e492f2756fc3/.claude/window1_live_v4_replay/landing_estimator_phased_arming_v24_20260804/RULINGS_RECEIPT.json

## Ruling 3 — landing-estimator build authorized, promotion rejected

V24 fits the audited own-W1-close minus decision-time live-ask distribution and emits `q25/q50/q75`. The central `q50` is the signing estimate; `q25/q75` remain uncertainty bounds. Fit is walk-forward, excludes the five exact-start games, uses a hard `n=30` hierarchy with named borrowing, and uses no future close at a decision. The `339` unresolved direction identities abstain on the mirror and do not veto the read side.

The phased mirror receives an aim but cannot place until its own qualified decline reaches the surviving coherent ordinal. The pair cap remains `leg2_bid <= 99 - leg1_fill`; a cap below the current live bid abstains without chasing. The V17 X relation is recorded as a non-signing cross-check only.

The build is causally valid but fails Ruling 1: V24 produced `47` acted legs, `44` credited legs, `4` completed pairs, `4` under-par pairs, `1` audited JOINT pair, and `1` carried pair. It therefore remains a rejected development variant; V23 stays operative.

Sources:

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/02ecf1d5858a4ec8244fa8c4d762e492f2756fc3/.claude/window1_live_v4_replay/landing_estimator_phased_arming_v24_20260804/LANDING_ESTIMATOR_FIT.json

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/02ecf1d5858a4ec8244fa8c4d762e492f2756fc3/.claude/window1_live_v4_replay/landing_estimator_phased_arming_v24_20260804/LANDING_ESTIMATE_RECEIPTS.jsonl.gz

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/02ecf1d5858a4ec8244fa8c4d762e492f2756fc3/.claude/window1_live_v4_replay/landing_estimator_phased_arming_v24_20260804/V17_X_RELATION_CROSS_CHECK.json

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/02ecf1d5858a4ec8244fa8c4d762e492f2756fc3/.claude/window1_live_v4_replay/landing_estimator_phased_arming_v24_20260804/FRONTIER.json

## First builder-side miss ledger

All `1,608` legs have exactly one address. There are `44` CAPTURED rows. The died-at counts are: landing path family unavailable `758`; unresolved identity `296`; live ask not strictly below q50 `180`; shape-pair read never resolved `176`; first fill unavailable for pair cap `100`; walk-forward minimum n not met `41`; mirror decline/shape state unresolved `7`; pair cap unreachable without chasing `3`; placed but uncredited `3`. The large path-family-unavailable class is the decisive evidence: the inherited V23 stream often carries old endpoint-labelled shapes, not a causal interim path-family identity. V24 abstains rather than treating those endpoint labels as decision inputs.

Sources:

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/02ecf1d5858a4ec8244fa8c4d762e492f2756fc3/.claude/window1_live_v4_replay/landing_estimator_phased_arming_v24_20260804/MISS_LEDGER_CONSERVATION.json

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/02ecf1d5858a4ec8244fa8c4d762e492f2756fc3/.claude/window1_live_v4_replay/landing_estimator_phased_arming_v24_20260804/MISS_LEDGER_1608.jsonl.gz

## Integrity and scope

Two clean builds produced `15` byte-identical regenerable artifacts with zero mismatches. Focused V24 tests are `9/9`; inherited V23 tests also pass. This is a development replay only: no holdout, live, network, order, position, exit, settlement, DCA, Window-2, scorer, deployment, or authorization action occurred.

Sources:

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/02ecf1d5858a4ec8244fa8c4d762e492f2756fc3/.claude/window1_live_v4_replay/landing_estimator_phased_arming_v24_20260804/DETERMINISM_RECEIPT.json

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/02ecf1d5858a4ec8244fa8c4d762e492f2756fc3/.claude/window1_live_v4_replay/landing_estimator_phased_arming_v24_20260804/ARTIFACT_HASH_MANIFEST.json

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/02ecf1d5858a4ec8244fa8c4d762e492f2756fc3/.claude/window1_live_v4_replay/landing_estimator_phased_arming_v24_20260804/FORBIDDEN_ACCESS_RECEIPT.json

V24 does not supersede V23. Its rejection is a measurement result, not authority to retune against this development replay.
