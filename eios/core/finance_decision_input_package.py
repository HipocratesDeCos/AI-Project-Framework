"""Complete selected Finance Basic input capture without analytical execution."""
from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from hashlib import sha256
import json

from eios.finance.models import FinanceBasicInput
from eios.parameters.center import ParameterConfigurationCenter
from eios.parameters.resolution import ResolvedConfiguration
from .decision_input_package import DecisionInputPackage, build_decision_input_package
from .models import DecisionContext, Evidence, PurchaseOperation

SCHEMA_VERSION = "FIN-DIP-01/v0.1"


def _canonical(value):
    if isinstance(value, Decimal):
        return format(value, "f")
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, dict):
        return {key: _canonical(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [_canonical(item) for item in value]
    return value


def _numeric(resolution: ResolvedConfiguration) -> Decimal:
    try:
        value = Decimal(resolution.value)
    except (InvalidOperation, ValueError, TypeError) as exc:
        raise ValueError(f"{resolution.parameter_id} must be numeric") from exc
    if not value.is_finite():
        raise ValueError(f"{resolution.parameter_id} must be finite")
    return value


@dataclass(frozen=True, init=False)
class FinanceDecisionInputPackage:
    """Immutable selected capture; does not certify cash-flow completeness/origin."""

    _base: DecisionInputPackage
    _material: bytes

    def __init__(self) -> None:
        raise TypeError("Use build_finance_decision_input_package")

    def to_payload(self) -> dict:
        return json.loads(self._material)

    @property
    def fingerprint(self) -> str:
        return sha256(self._material).hexdigest()

    @property
    def schema_version(self) -> str:
        return self.to_payload()["schema_version"]

    @property
    def decision_input_package(self) -> DecisionInputPackage:
        return self._base

    @property
    def finance_input(self) -> FinanceBasicInput:
        return FinanceBasicInput.model_validate(self.to_payload()["finance_input"])

    @property
    def horizon_resolution(self) -> ResolvedConfiguration:
        return next(item for item in self._base.configurations if item.parameter_id == "P-FIN-001")

    @property
    def treasury_minimum_resolution(self) -> ResolvedConfiguration | None:
        if self.finance_input.treasury_minimum is None:
            return None
        return next(item for item in self._base.configurations if item.parameter_id == "P-FIN-002")


def build_finance_decision_input_package(
    *, purchase: PurchaseOperation, context: DecisionContext,
    evidence: tuple[Evidence, ...], finance_input: FinanceBasicInput,
    company_id: str, effective_at: datetime,
    requested_parameter_ids: tuple[str, ...], center: ParameterConfigurationCenter,
) -> FinanceDecisionInputPackage:
    """Capture supplied inputs and bind selected parameters without calling engines."""
    if not isinstance(finance_input, FinanceBasicInput):
        raise TypeError("finance_input must be FinanceBasicInput")
    if not isinstance(context, DecisionContext):
        raise TypeError("context must be DecisionContext")
    finance_copy = FinanceBasicInput.model_validate(deepcopy(finance_input.model_dump(mode="python")))
    context_copy = DecisionContext.model_validate(deepcopy(context.model_dump(mode="python")))
    if finance_copy.context != context_copy:
        raise ValueError("Finance input must match the complete DecisionContext")
    if not isinstance(effective_at, datetime):
        raise TypeError("effective_at must be a datetime")
    if effective_at.date() != finance_copy.snapshot.as_of_date:
        raise ValueError("Financial parameter resolution must match the snapshot date")
    if not isinstance(requested_parameter_ids, tuple):
        raise TypeError("requested_parameter_ids must be a tuple")
    if "P-FIN-001" not in requested_parameter_ids:
        raise ValueError("P-FIN-001 must be explicitly selected")
    if finance_copy.treasury_minimum is not None and "P-FIN-002" not in requested_parameter_ids:
        raise ValueError("A supplied treasury minimum requires explicit P-FIN-002 selection")

    base = build_decision_input_package(
        purchase=purchase, context=context_copy, evidence=evidence,
        financial_snapshot=finance_copy.snapshot, company_id=company_id,
        effective_at=effective_at, requested_parameter_ids=requested_parameter_ids,
        center=center,
    )
    resolutions = {item.parameter_id: item for item in base.configurations}
    horizon = resolutions.get("P-FIN-001")
    if horizon is None:
        raise ValueError("P-FIN-001 configuration is unavailable; no horizon fallback")
    horizon_days = _numeric(horizon)
    if (horizon.unit != "días" or horizon_days <= 0
            or horizon_days != horizon_days.to_integral_value()
            or horizon_days != finance_copy.horizon_days):
        raise ValueError("P-FIN-001 does not match the supplied financial horizon")

    if finance_copy.treasury_minimum is not None:
        minimum = resolutions.get("P-FIN-002")
        if minimum is None:
            raise ValueError("P-FIN-002 configuration is unavailable; no minimum fallback")
        amount = _numeric(minimum)
        if (minimum.unit not in {"EUR", "€"} or finance_copy.snapshot.currency != "EUR"
                or amount < 0 or amount != finance_copy.treasury_minimum):
            raise ValueError("P-FIN-002 does not match the supplied treasury minimum/unit")

    payload = dict(schema_version=SCHEMA_VERSION,
                   decision_input_package=base.to_payload(),
                   finance_input=_canonical(finance_copy.model_dump(mode="python")))
    material = json.dumps(payload, ensure_ascii=False, sort_keys=True,
                          separators=(",", ":"), allow_nan=False).encode("utf-8")
    package = object.__new__(FinanceDecisionInputPackage)
    object.__setattr__(package, "_base", base)
    object.__setattr__(package, "_material", material)
    return package


__all__ = ["FinanceDecisionInputPackage", "SCHEMA_VERSION", "build_finance_decision_input_package"]
