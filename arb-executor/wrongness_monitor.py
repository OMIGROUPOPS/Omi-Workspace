"""Runtime wrongness alarms for fitted-surface and decision-path contracts.

This module does not decide or price. It makes silent semantic mismatches
observable at the moment they occur.
"""

from dataclasses import asdict, dataclass


MIN_FITTED_N = 20


@dataclass(frozen=True)
class WrongnessAlarm:
    code: str
    severity: str
    details: dict

    def as_dict(self):
        return asdict(self)


def audit_surface_consult(surface_id, fit_contract, consult_key, fitted_n,
                          min_n=MIN_FITTED_N):
    """Return alarms for a surface consultation.

    ``fit_contract`` and ``consult_key`` intentionally use the same field
    names. Every contract field must be present and equal; extra consultation
    fields are retained evidence and do not invalidate the call.
    """
    alarms = []
    if not fit_contract:
        alarms.append(WrongnessAlarm(
            "FIT_CONTRACT_MISSING", "BLOCK",
            {"surface_id": surface_id},
        ))
    else:
        mismatch = {
            field: {
                "fitted": expected,
                "consulted": consult_key.get(field),
            }
            for field, expected in fit_contract.items()
            if consult_key.get(field) != expected
        }
        if mismatch:
            alarms.append(WrongnessAlarm(
                "FIT_CONSULT_KEY_MISMATCH", "BLOCK",
                {"surface_id": surface_id, "mismatch": mismatch},
            ))
    if fitted_n is None or int(fitted_n) < int(min_n):
        alarms.append(WrongnessAlarm(
            "FITTED_ROW_THIN", "BLOCK",
            {
                "surface_id": surface_id,
                "n": fitted_n,
                "minimum_n": int(min_n),
            },
        ))
    return alarms


class VerdictMonitor:
    """Bind a computed verdict to the downstream effect that must honor it."""

    def __init__(self):
        self._pending = {}

    def record(self, decision_id, ticker, verdict, expected_effect,
               expected_price=None):
        if decision_id in self._pending:
            return [WrongnessAlarm(
                "DUPLICATE_DECISION_ID", "BLOCK",
                {"decision_id": decision_id, "ticker": ticker},
            )]
        self._pending[decision_id] = {
            "ticker": ticker,
            "verdict": verdict,
            "expected_effect": expected_effect,
            "expected_price": expected_price,
        }
        return []

    def observe(self, decision_id, effect, actual_price=None, order_id=None):
        decision = self._pending.pop(decision_id, None)
        if decision is None:
            return [WrongnessAlarm(
                "EFFECT_WITHOUT_VERDICT", "BLOCK",
                {
                    "decision_id": decision_id,
                    "effect": effect,
                    "order_id": order_id,
                },
            )]
        alarms = []
        if effect != decision["expected_effect"]:
            alarms.append(WrongnessAlarm(
                "VERDICT_IGNORED", "BLOCK",
                {
                    "decision_id": decision_id,
                    "ticker": decision["ticker"],
                    "verdict": decision["verdict"],
                    "expected_effect": decision["expected_effect"],
                    "actual_effect": effect,
                    "order_id": order_id,
                },
            ))
        expected_price = decision.get("expected_price")
        if (
            effect == "POST"
            and expected_price is not None
            and actual_price != expected_price
        ):
            alarms.append(WrongnessAlarm(
                "AUTHORIZED_PRICE_IGNORED", "BLOCK",
                {
                    "decision_id": decision_id,
                    "ticker": decision["ticker"],
                    "expected_price": expected_price,
                    "actual_price": actual_price,
                    "order_id": order_id,
                },
            ))
        return alarms

    def unresolved(self):
        return [
            WrongnessAlarm(
                "VERDICT_WITHOUT_EFFECT", "BLOCK",
                {"decision_id": decision_id, **decision},
            )
            for decision_id, decision in sorted(self._pending.items())
        ]
