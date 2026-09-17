"""Selected input aggregation; content identity is not proof of source origin."""
from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict, dataclass
from datetime import date, datetime
from decimal import Decimal
from hashlib import sha256
import json
from typing import TypeVar

from pydantic import BaseModel

from eios.finance.models import FinancialSnapshot
from eios.parameters.center import Configuration, ParameterConfigurationCenter
from eios.parameters.resolution import ResolvedConfiguration, resolve_configuration_for_context
from .models import DecisionContext, Evidence, PurchaseOperation

SCHEMA_VERSION = "DIP-AGG-01/v0.1"
Model = TypeVar("Model", bound=BaseModel)


def _snapshot(value: Model, expected: type[Model]) -> Model:
    if not isinstance(value, expected):
        raise TypeError(f"Expected {expected.__name__}")
    return expected.model_validate(deepcopy(value.model_dump(mode="python")))


def _identifier(value: str) -> None:
    if not isinstance(value, str) or not value or value != value.strip():
        raise ValueError("Identifiers must be nonempty strings without outer whitespace")


def _configuration_snapshot(value: Configuration, parameter_id: str, company_id: str) -> Configuration:
    if not isinstance(value, Configuration):
        raise TypeError("Expected Configuration from the Centre")
    value = deepcopy(value)
    if type(value.configuration_id) is not int:
        raise TypeError("configuration_id must be an integer")
    for field in ("parameter_id", "company_id", "value"):
        if not isinstance(getattr(value, field), str):
            raise TypeError(f"Configuration.{field} must be a string")
    for field in ("value_type", "unit"):
        item = getattr(value, field)
        if item is not None and not isinstance(item, str):
            raise TypeError(f"Configuration.{field} must be a string or None")
    for field in ("valid_from", "created_at", "updated_at"):
        if not isinstance(getattr(value, field), datetime):
            raise TypeError(f"Configuration.{field} must be a datetime")
    if value.valid_to is not None and not isinstance(value.valid_to, datetime):
        raise TypeError("Configuration.valid_to must be a datetime or None")
    if value.parameter_id != parameter_id or value.company_id != company_id:
        raise ValueError("Configuration does not match selected parameter/company")
    return value


def _canonical(value):
    if isinstance(value, Decimal):
        return format(value, "f")
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, dict):
        return {key: _canonical(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [_canonical(item) for item in value]
    return value


def _restore_configuration(payload: dict) -> ResolvedConfiguration:
    data = dict(payload["configuration"])
    for field in ("valid_from", "valid_to", "created_at", "updated_at"):
        if data[field] is not None:
            data[field] = datetime.fromisoformat(data[field])
    return ResolvedConfiguration(
        configuration=Configuration(**data),
        parameters_version=payload["parameters_version"],
        effective_at=datetime.fromisoformat(payload["effective_at"]),
    )


@dataclass(frozen=True, init=False)
class DecisionInputPackage:
    """Factory-built immutable capture of selected inputs, not a trust seal.

    No deserialization/import constructor is supplied by this first slice.
    The fingerprint does not authenticate Centre ports or external snapshots.
    """

    _material: bytes

    def __init__(self) -> None:
        raise TypeError("Use build_decision_input_package")

    def to_payload(self) -> dict:
        """Independent JSON-compatible representation of all captured material."""
        return json.loads(self._material)

    @property
    def fingerprint(self) -> str:
        return sha256(self._material).hexdigest()

    @property
    def schema_version(self) -> str:
        return self.to_payload()["schema_version"]

    @property
    def company_id(self) -> str:
        return self.to_payload()["company_id"]

    @property
    def effective_at(self) -> datetime:
        return datetime.fromisoformat(self.to_payload()["effective_at"])

    @property
    def requested_parameter_ids(self) -> tuple[str, ...]:
        return tuple(self.to_payload()["requested_parameter_ids"])

    @property
    def purchase(self) -> PurchaseOperation:
        return PurchaseOperation.model_validate(self.to_payload()["purchase"])

    @property
    def context(self) -> DecisionContext:
        return DecisionContext.model_validate(self.to_payload()["context"])

    @property
    def evidence(self) -> tuple[Evidence, ...]:
        return tuple(Evidence.model_validate(item) for item in self.to_payload()["evidence"])

    @property
    def financial_snapshot(self) -> FinancialSnapshot | None:
        data = self.to_payload()["financial_snapshot"]
        return None if data is None else FinancialSnapshot.model_validate(data)

    @property
    def configurations(self) -> tuple[ResolvedConfiguration, ...]:
        return tuple(_restore_configuration(item) for item in self.to_payload()["configurations"])

    @property
    def missing_parameter_ids(self) -> tuple[str, ...]:
        return tuple(self.to_payload()["missing_parameter_ids"])


def build_decision_input_package(
    *, purchase: PurchaseOperation, context: DecisionContext,
    evidence: tuple[Evidence, ...], financial_snapshot: FinancialSnapshot | None,
    company_id: str, effective_at: datetime,
    requested_parameter_ids: tuple[str, ...], center: ParameterConfigurationCenter,
) -> DecisionInputPackage:
    """Revalidate, capture and aggregate without judging quality or completeness."""
    _identifier(company_id)
    if not isinstance(effective_at, datetime):
        raise TypeError("effective_at must be a datetime")
    if not isinstance(center, ParameterConfigurationCenter):
        raise TypeError("center must be ParameterConfigurationCenter")
    if not isinstance(evidence, tuple) or not isinstance(requested_parameter_ids, tuple):
        raise TypeError("evidence and requested_parameter_ids must be tuples")
    for parameter_id in requested_parameter_ids:
        _identifier(parameter_id)
    if len(set(requested_parameter_ids)) != len(requested_parameter_ids):
        raise ValueError("Duplicate selected parameter IDs")

    purchase_copy = _snapshot(purchase, PurchaseOperation)
    context_copy = _snapshot(context, DecisionContext)
    evidence_copy = tuple(_snapshot(item, Evidence) for item in evidence)
    financial_copy = None if financial_snapshot is None else _snapshot(financial_snapshot, FinancialSnapshot)
    if (purchase_copy.decision_id, purchase_copy.scenario_id) != (context_copy.decision_id, context_copy.scenario_id):
        raise ValueError("Purchase/context identity mismatch")
    evidence_ids = tuple(item.evidence_id for item in evidence_copy)
    if len(set(evidence_ids)) != len(evidence_ids):
        raise ValueError("Duplicate evidence IDs")
    if financial_copy is not None and (
        financial_copy.company_scope != company_id
        or financial_copy.data_snapshot_id != context_copy.data_snapshot_id
    ):
        raise ValueError("Financial snapshot company/context mismatch")

    configurations: list[ResolvedConfiguration] = []
    missing: list[str] = []
    for parameter_id in requested_parameter_ids:
        configuration = center.get_configuration_at(company_id, parameter_id, effective_at)
        if configuration is None:
            missing.append(parameter_id)
            continue
        configuration_copy = _configuration_snapshot(configuration, parameter_id, company_id)
        resolved = resolve_configuration_for_context(configuration_copy, context_copy, effective_at)
        if not isinstance(resolved, ResolvedConfiguration):
            raise TypeError("Expected a resolved configuration")
        if (resolved.parameters_version != context_copy.parameters_version
                or resolved.effective_at != effective_at
                or resolved.configuration != configuration_copy):
            raise ValueError("Configuration resolution binding mismatch")
        configurations.append(resolved)

    present = tuple(item.parameter_id for item in configurations)
    if set(present) & set(missing) or set(present) | set(missing) != set(requested_parameter_ids):
        raise ValueError("Incomplete configuration partition")
    payload = dict(
        schema_version=SCHEMA_VERSION,
        purchase=purchase_copy.model_dump(mode="python"),
        context=context_copy.model_dump(mode="python"),
        evidence=[item.model_dump(mode="python") for item in evidence_copy],
        financial_snapshot=None if financial_copy is None else financial_copy.model_dump(mode="python"),
        company_id=company_id, effective_at=effective_at,
        requested_parameter_ids=requested_parameter_ids,
        configurations=[asdict(item) for item in configurations],
        missing_parameter_ids=missing,
    )
    material = json.dumps(_canonical(payload), ensure_ascii=False, sort_keys=True,
                          separators=(",", ":"), allow_nan=False).encode("utf-8")
    package = object.__new__(DecisionInputPackage)
    object.__setattr__(package, "_material", material)
    return package


__all__ = ["DecisionInputPackage", "SCHEMA_VERSION", "build_decision_input_package"]
