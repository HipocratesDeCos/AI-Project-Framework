"""O2 Scenario Engine: controlled, immutable scenario versioning.

O2 creates hypotheses only. It does not evaluate, rank, recommend, negotiate,
approve, execute, or mutate the real purchase operation or its evidence.
"""
from __future__ import annotations

import hashlib
import json
from enum import Enum
from typing import Any
from uuid import NAMESPACE_URL, uuid5

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .models import DecisionContext


class ScenarioStatus(str, Enum):
    DRAFT = "DRAFT"
    VALID = "VALID"
    INVALID = "INVALID"
    EVALUATED = "EVALUATED"


class AuthorizedScenarioChange(BaseModel):
    """One hypothesis change; authorization is validated at scenario creation."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    variable: str = Field(min_length=1, max_length=128)
    base_value: Any
    simulated_value: Any
    unit: str | None = Field(default=None, max_length=64)
    authorization: bool
    origin: str = Field(min_length=1, max_length=128)

    @model_validator(mode="after")
    def validate_change(self) -> "AuthorizedScenarioChange":
        if self.base_value == self.simulated_value:
            raise ValueError("El cambio debe representar una hipótesis distinta del valor base")
        return self


def _canonical_value(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _canonical_value(value[key]) for key in sorted(value, key=str)}
    if isinstance(value, (list, tuple)):
        return [_canonical_value(item) for item in value]
    if isinstance(value, set):
        return sorted((_canonical_value(item) for item in value), key=lambda item: repr(item))
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return value


def canonical_scenario_changes(
    changes: tuple[AuthorizedScenarioChange, ...],
) -> tuple[dict[str, Any], ...]:
    """Normalize changes independently of their input order."""
    normalized = [
        {
            "variable": change.variable,
            "base_value": _canonical_value(change.base_value),
            "simulated_value": _canonical_value(change.simulated_value),
            "unit": change.unit,
            "authorization": change.authorization,
            "origin": change.origin,
        }
        for change in changes
    ]
    normalized.sort(
        key=lambda item: (
            item["variable"],
            json.dumps(item["simulated_value"], ensure_ascii=False, sort_keys=True, default=str),
            item["unit"] or "",
            item["authorization"],
            item["origin"],
        )
    )
    return tuple(normalized)


def scenario_fingerprint(
    context: DecisionContext,
    parent_scenario_id: str | None,
    changes: tuple[AuthorizedScenarioChange, ...],
) -> str:
    """Return the deterministic fingerprint of scenario identity and content."""
    payload = {
        "decision_id": context.decision_id,
        "scenario_id": context.scenario_id,
        "rules_version": context.rules_version,
        "parameters_version": context.parameters_version,
        "data_snapshot_id": context.data_snapshot_id,
        "parent_scenario_id": parent_scenario_id,
        "changes": canonical_scenario_changes(changes),
    }
    canonical = json.dumps(
        payload, ensure_ascii=False, separators=(",", ":"), sort_keys=True, default=str
    ).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


class ScenarioVersion(BaseModel):
    """Immutable, traceable representation of a controlled hypothesis."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    scenario_id: str = Field(min_length=1, max_length=64)
    parent_scenario_id: str | None = Field(default=None, max_length=64)
    decision_id: str = Field(min_length=1, max_length=64)
    rules_version: str = Field(min_length=1, max_length=64)
    parameters_version: str = Field(min_length=1, max_length=64)
    data_snapshot_id: str = Field(min_length=1, max_length=64)
    changes: tuple[AuthorizedScenarioChange, ...] = ()
    fingerprint: str = Field(min_length=64, max_length=64)
    status: ScenarioStatus

    @model_validator(mode="after")
    def validate_version(self) -> "ScenarioVersion":
        if self.status == ScenarioStatus.EVALUATED:
            raise ValueError("EVALUATED está reservado para una integración futura")
        if self.status == ScenarioStatus.VALID and not self.changes:
            raise ValueError("VALID requiere al menos un cambio autorizado")
        if self.parent_scenario_id == self.scenario_id:
            raise ValueError("Un escenario no puede ser padre de sí mismo")
        return self


def create_scenario(
    context: DecisionContext,
    changes: tuple[AuthorizedScenarioChange, ...] = (),
    parent_scenario_id: str | None = None,
    validate: bool = True,
) -> ScenarioVersion:
    """Create a scenario version without applying any change to real data."""
    if not changes:
        status = ScenarioStatus.DRAFT
    elif any(not change.authorization for change in changes):
        status = ScenarioStatus.INVALID
    elif not validate:
        status = ScenarioStatus.DRAFT
    else:
        status = ScenarioStatus.VALID

    normalized = canonical_scenario_changes(changes)
    fingerprint = scenario_fingerprint(context, parent_scenario_id, changes)
    scenario_id = str(
        uuid5(NAMESPACE_URL, f"eios:o2:{context.decision_id}:{fingerprint}")
    )
    return ScenarioVersion(
        scenario_id=scenario_id,
        parent_scenario_id=parent_scenario_id,
        decision_id=context.decision_id,
        rules_version=context.rules_version,
        parameters_version=context.parameters_version,
        data_snapshot_id=context.data_snapshot_id,
        changes=tuple(
            AuthorizedScenarioChange.model_validate(item) for item in normalized
        ),
        fingerprint=fingerprint,
        status=status,
    )


__all__ = [
    "AuthorizedScenarioChange",
    "ScenarioStatus",
    "ScenarioVersion",
    "canonical_scenario_changes",
    "create_scenario",
    "scenario_fingerprint",
]
