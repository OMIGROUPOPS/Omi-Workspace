#!/usr/bin/env python3
"""Round-4 V2 overlay for the amended Item-5 availability law.

V1 remains byte-authoritative whenever causal_role is available. Missing role
is a steering NO_CALL. Missing lawful positive-size external BBO is a separate
market-evidence NO_CALL with no order and continued D membership.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable, Mapping, MutableMapping

import window1_round2_instrument as r2
import window1_round4_instrument as v1


VERSION = "window1-round4-item5-amended-overlay-v2"
BASE_INSTRUMENT_VERSION = v1.VERSION
CANDIDATE_SPEC_PATH = (
    "arb-executor/docs/research/window1/WINDOW1_ROUND4_CANDIDATES_V2.json"
)
ATLAS_PATH = v1.ATLAS_PATH
DRIFT_PATH = v1.DRIFT_PATH
InstrumentError = v1.InstrumentError
CAUSAL_ROLE_NO_CALL = (
    "causal_role_unavailable_role_specific_steering_disabled"
)
MARKET_EVIDENCE_NO_CALL = (
    "lawful_positive_size_external_bbo_unavailable_no_order"
)
FORBIDDEN_INERT_PARAMETERS = {
    "first_fill_sibling_max_combined_cost_cents",
    "maximum_pair_order_cost_cents",
}


def load_candidate_spec(repo: Path) -> dict[str, Any]:
    spec = r2.read_json(repo / CANDIDATE_SPEC_PATH)
    if spec.get("schema_version") != "window1-round4-candidates-v2":
        raise InstrumentError("Round-4 V2 candidate spec mismatch")
    if spec.get("instrument_version") != BASE_INSTRUMENT_VERSION:
        raise InstrumentError("Round-4 V1 base instrument changed")
    if spec.get("overlay_version") != VERSION:
        raise InstrumentError("Round-4 V2 overlay mismatch")
    if list(spec.get("candidate_ids") or []) != [
        "r4_pair_presence__park_join__causal_headroom_ladder",
        "r4_full_drift_stack__causal_headroom_ladder",
    ]:
        raise InstrumentError("Round-4 V2 candidate order changed")
    parameters = dict(spec.get("common_parameters") or {})
    if FORBIDDEN_INERT_PARAMETERS.intersection(parameters):
        raise InstrumentError("retired 100-cent parameter present")
    if spec.get("free_numeric_parameters") != []:
        raise InstrumentError("Round-4 V2 cannot expose free parameters")
    return spec


def candidate_policy(
    spec: Mapping[str, Any],
    candidate_id: str,
    *,
    ablations: Iterable[str] = (),
) -> dict[str, Any]:
    policy = v1.candidate_policy(
        spec, candidate_id, ablations=ablations
    )
    if FORBIDDEN_INERT_PARAMETERS.intersection(policy["parameters"]):
        raise InstrumentError("V2 consumer received retired parameter")
    return policy


def load_atlas(repo: Path) -> dict[str, Any]:
    return v1.load_atlas(repo)


headroom_b2_max = v1.headroom_b2_max
strict_pair_budget = v1.strict_pair_budget


class Round4InstrumentV2(v1.Round4Instrument):
    """V1 mechanics with only the amended availability semantics."""

    def _new_state(
        self, event: Mapping[str, Any], leg: Mapping[str, Any],
    ) -> MutableMapping[str, Any]:
        state = super()._new_state(event, leg)
        unavailable = state["availability"].get("causal_role") is not True
        state["causal_role_no_call"] = unavailable
        state["neutral_role_fallback"] = (
            "join_external_best_bid" if unavailable else None
        )
        if not unavailable:
            return state
        missing = [
            str(name) for name in state.get("missing_features") or []
            if str(name) != "causal_role"
        ]
        actions = []
        for action in state["actions"]:
            if (
                action["action"] == "feature_censor"
                and action["reason"] == "required_feature_absent"
                and "causal_role" in (
                    action.get("missing_features") or []
                )
            ):
                remaining = [
                    str(name)
                    for name in action.get("missing_features") or []
                    if str(name) != "causal_role"
                ]
                if remaining:
                    replacement = dict(action)
                    replacement["missing_features"] = remaining
                    actions.append(replacement)
                continue
            actions.append(action)
        state["actions"] = actions
        state["missing_features"] = missing
        state["feature_censored"] = bool(missing)
        r2._action(
            state,
            self.left,
            "feature_no_call",
            CAUSAL_ROLE_NO_CALL,
            family_id="leg_specific_posture",
            response_status="NO_CALL_UNAVAILABLE",
            underlying_policy_continues=True,
            role_specific_steering_enabled=False,
            role_inferred=False,
            neutral_posture_when_BBO_exists="join_external_best_bid",
        )
        return state

    def _posture(self, state: Mapping[str, Any]) -> str:
        if state.get("causal_role_no_call"):
            return "join_external_best_bid"
        return super()._posture(state)

    def _target_price(
        self,
        state: Mapping[str, Any],
        *,
        include_top5: bool = True,
    ) -> int:
        if not state.get("causal_role_no_call"):
            return super()._target_price(
                state, include_top5=include_top5
            )
        book = state["current_book"]
        bid_rows = r2.external_bids(book, self._subtract_own())
        ask_rows = r2.asks(book)
        if not bid_rows or not ask_rows:
            raise InstrumentError(
                "neutral presence requires lawful positive-size external BBO"
            )
        external_bid = int(bid_rows[0][0])
        maker_ceiling = int(ask_rows[0][0]) - 1
        return max(1, min(maker_ceiling, external_bid))

    def _terminalize(self, state: MutableMapping[str, Any]) -> None:
        if state.get("birth_anchor") is not None:
            super()._terminalize(state)
            return
        # No order price can be instantiated. Do not call the inherited
        # feature-censor path and do not substitute an execution print.
        state["feature_censored"] = False
        state["missing_features"] = [
            str(name) for name in state.get("missing_features") or []
            if str(name) != "positive_size_external_bbo"
        ]
        r2._action(
            state,
            self.horizon,
            "feature_no_call",
            MARKET_EVIDENCE_NO_CALL,
            family_id="independent_pair_presence",
            response_status="NO_CALL_UNAVAILABLE",
            underlying_policy_continues=True,
            D_membership_continues=True,
            placement_created=False,
            fabricated_price=False,
            print_substituted_for_BBO=False,
        )
        state["terminal"] = "market_evidence_unavailable_no_call"
        r2._action(
            state,
            self.horizon,
            "terminal",
            "market_evidence_unavailable_no_call",
            quantity=float(state["quantity"]),
            vwap_cents=None,
            feature_censors=[],
            D_membership_continues=True,
        )


# Preserve V1 serialized schema/instrument identity so the 799 unaffected
# event streams per candidate remain byte-identical.
Round4Instrument = Round4InstrumentV2
