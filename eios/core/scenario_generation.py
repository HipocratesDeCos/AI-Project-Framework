"""O4 controlled scenario generation.

This module generates bounded, deterministic candidate scenario changes.
It does not evaluate rules or viability and does not create ScenarioVersion
identity/versioning; O2 remains the authority for scenario representation.
"""

from __future__ import annotations

from enum import Enum
from itertools import product
from typing import Any, Mapping

from pydantic import BaseModel, ConfigDict, Field, field_validator


class GenerationStatus(str, Enum):
    GENERATED = "GENERATED"
    EMPTY = "EMPTY"
    BLOCKED = "BLOCKED"
    NOT_EVALUABLE = "NOT_EVALUABLE"
    FAILED = "FAILED"


class ScenarioVariable(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    variable_id: str = Field(min_length=1)
    value_type: str = Field(min_length=1)
    values: tuple[Any, ...]
    max_cardinality: int | None = Field(default=None, ge=0)

    @field_validator("values")
    @classmethod
    def reject_unhashable_values(cls, value: tuple[Any, ...]) -> tuple[Any, ...]:
        try:
            len({repr(item) for item in value})
        except Exception as exc:  # pragma: no cover - defensive boundary
            raise ValueError("values must be canonicalizable") from exc
        return value


class GenerationLimits(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    max_variables: int = Field(ge=0)
    max_cardinality_per_variable: int = Field(ge=0)
    max_total_combinations: int = Field(ge=0)
    max_depth: int = Field(ge=0)
    max_emitted: int = Field(ge=0)


class GenerationPolicy(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    policy_version: str = Field(min_length=1)
    mode: str = "CARTESIAN"
    allow_cartesian: bool = True
    structural_pruning: tuple[Mapping[str, Any], ...] = ()

    @field_validator("mode")
    @classmethod
    def cartesian_only(cls, value: str) -> str:
        if value != "CARTESIAN":
            raise ValueError("O4 MVP supports only CARTESIAN generation")
        return value


class ScenarioGenerationRequest(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    decision_id: str = Field(min_length=1)
    scenario_id: str = Field(min_length=1)
    parent_scenario_id: str | None = None
    variables: tuple[ScenarioVariable, ...] = ()
    limits: GenerationLimits
    policy: GenerationPolicy
    depth: int = Field(default=0, ge=0)
    authorized: bool = True


class ScenarioCandidate(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    scenario_id: str
    parent_scenario_id: str | None
    changes: tuple[tuple[str, Any], ...]


class ScenarioGenerationResult(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    decision_id: str
    scenario_id: str
    status: GenerationStatus
    candidates: tuple[ScenarioCandidate, ...] = ()
    limitations: tuple[str, ...] = ()
    failure_reason: str | None = None

    @field_validator("failure_reason")
    @classmethod
    def failure_only(cls, value: str | None, info: Any) -> str | None:
        status = info.data.get("status")
        if status == GenerationStatus.FAILED and not value:
            raise ValueError("FAILED requires failure_reason")
        if status != GenerationStatus.FAILED and value is not None:
            raise ValueError("failure_reason is only valid for FAILED")
        return value


def _canonical_value(value: Any) -> tuple[str, Any]:
    if value is None:
        return ("none", None)
    if isinstance(value, bool):
        return ("bool", value)
    if isinstance(value, int) and not isinstance(value, bool):
        return ("int", value)
    if isinstance(value, float):
        return ("float", value)
    if isinstance(value, str):
        return ("str", value)
    return (type(value).__name__, repr(value))


def generate_scenarios(request: ScenarioGenerationRequest) -> ScenarioGenerationResult:
    """Generate a finite deterministic candidate set without evaluating it."""
    if not request.authorized:
        return ScenarioGenerationResult(
            decision_id=request.decision_id,
            scenario_id=request.scenario_id,
            status=GenerationStatus.BLOCKED,
            limitations=("unauthorized scenario space",),
        )

    if len(request.variables) > request.limits.max_variables:
        return ScenarioGenerationResult(
            decision_id=request.decision_id,
            scenario_id=request.scenario_id,
            status=GenerationStatus.BLOCKED,
            limitations=("max_variables exceeded",),
        )

    if request.depth > request.limits.max_depth:
        return ScenarioGenerationResult(
            decision_id=request.decision_id,
            scenario_id=request.scenario_id,
            status=GenerationStatus.BLOCKED,
            limitations=("max_depth exceeded",),
        )

    for variable in request.variables:
        if len(variable.values) > request.limits.max_cardinality_per_variable:
            return ScenarioGenerationResult(
                decision_id=request.decision_id,
                scenario_id=request.scenario_id,
                status=GenerationStatus.BLOCKED,
                limitations=(f"max_cardinality_per_variable exceeded: {variable.variable_id}",),
            )
        if variable.max_cardinality is not None and len(variable.values) > variable.max_cardinality:
            return ScenarioGenerationResult(
                decision_id=request.decision_id,
                scenario_id=request.scenario_id,
                status=GenerationStatus.BLOCKED,
                limitations=(f"variable cardinality exceeded: {variable.variable_id}",),
            )

    cardinality = 1
    for variable in request.variables:
        cardinality *= len(variable.values)
        if cardinality > request.limits.max_total_combinations:
            return ScenarioGenerationResult(
                decision_id=request.decision_id,
                scenario_id=request.scenario_id,
                status=GenerationStatus.BLOCKED,
                limitations=("max_total_combinations exceeded",),
            )

    if cardinality == 0:
        return ScenarioGenerationResult(
            decision_id=request.decision_id,
            scenario_id=request.scenario_id,
            status=GenerationStatus.EMPTY,
        )

    ordered = sorted(request.variables, key=lambda item: item.variable_id)
    candidates: list[ScenarioCandidate] = []
    seen: set[tuple[tuple[str, Any], ...]] = set()

    for values in product(*(variable.values for variable in ordered)):
        changes = tuple(
            (variable.variable_id, _canonical_value(value))
            for variable, value in zip(ordered, values)
        )
        if changes in seen:
            continue
        seen.add(changes)
        candidates.append(
            ScenarioCandidate(
                scenario_id=request.scenario_id,
                parent_scenario_id=request.parent_scenario_id,
                changes=changes,
            )
        )
        if len(candidates) >= request.limits.max_emitted:
            break

    return ScenarioGenerationResult(
        decision_id=request.decision_id,
        scenario_id=request.scenario_id,
        status=GenerationStatus.GENERATED,
        candidates=tuple(candidates),
    )
