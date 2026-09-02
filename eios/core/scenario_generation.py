"""O4 controlled, finite and deterministic scenario generation.

O4 emits candidate changes only. It does not create O2 identities, evaluate
scenarios, rank alternatives, recommend actions, or execute operations.
"""
from __future__ import annotations

import json
from enum import Enum
from math import prod
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .models import DecisionContext
from .scenario_engine import AuthorizedScenarioChange

MAX_VARIABLES = 8
MAX_CARDINALITY_PER_VARIABLE = 20
MAX_TOTAL_CARDINALITY = 1000
MAX_DEPTH = 3
MAX_EMITTED_CANDIDATES = 1000


class GenerationStatus(str, Enum):
    GENERATED = "GENERATED"
    EMPTY = "EMPTY"
    BLOCKED = "BLOCKED"
    NOT_EVALUABLE = "NOT_EVALUABLE"
    FAILED = "FAILED"


class GenerationVariable(BaseModel):
    """Finite, explicitly authorized scenario variable."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    variable_id: str = Field(min_length=1, max_length=128)
    value_type: str
    base_value: Any
    domain: tuple[Any, ...] = ()
    excluded_values: tuple[Any, ...] = ()

    @model_validator(mode="after")
    def validate_definition(self) -> "GenerationVariable":
        if self.value_type not in {"string", "integer", "number", "boolean"}:
            raise ValueError("value_type no autorizado")
        for value in self.domain:
            if not _matches_type(value, self.value_type):
                raise ValueError("valor de dominio incompatible con value_type")
        return self


class GenerationPolicy(BaseModel):
    """Versioned deterministic MVP policy."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    policy_version: str = Field(min_length=1, max_length=64)
    max_variables: int = Field(default=MAX_VARIABLES, ge=0, le=MAX_VARIABLES)
    max_cardinality_per_variable: int = Field(
        default=MAX_CARDINALITY_PER_VARIABLE, ge=0, le=MAX_CARDINALITY_PER_VARIABLE
    )
    max_total_cardinality: int = Field(default=MAX_TOTAL_CARDINALITY, ge=0, le=MAX_TOTAL_CARDINALITY)
    max_depth: int = Field(default=MAX_DEPTH, ge=0, le=MAX_DEPTH)
    max_emitted_candidates: int = Field(
        default=MAX_EMITTED_CANDIDATES, ge=0, le=MAX_EMITTED_CANDIDATES
    )


class CandidateScenario(BaseModel):
    """O4 output; O2 remains responsible for scenario identity/versioning."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    parent_scenario_id: str | None = Field(default=None, max_length=64)
    depth: int = Field(ge=0)
    changes: tuple[AuthorizedScenarioChange, ...]


class GenerationResult(BaseModel):
    """Immutable technical result of one O4 generation attempt."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    status: GenerationStatus
    candidates: tuple[CandidateScenario, ...] = ()
    policy_version: str
    reason: str | None = None

    @model_validator(mode="after")
    def validate_result(self) -> "GenerationResult":
        if self.status == GenerationStatus.GENERATED and not self.candidates:
            raise ValueError("GENERATED requiere candidatos")
        if self.status in {GenerationStatus.BLOCKED, GenerationStatus.NOT_EVALUABLE, GenerationStatus.FAILED} and not self.reason:
            raise ValueError("El estado requiere causa")
        if self.status != GenerationStatus.GENERATED and self.candidates:
            raise ValueError("Solo GENERATED puede emitir candidatos")
        return self


def _matches_type(value: Any, value_type: str) -> bool:
    if value_type == "boolean":
        return type(value) is bool
    if value_type == "integer":
        return type(value) is int
    if value_type == "number":
        return type(value) in {int, float} and not isinstance(value, bool)
    return type(value) is str


def _canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=repr)


def _canonical_variables(variables: tuple[GenerationVariable, ...]) -> tuple[GenerationVariable, ...]:
    return tuple(sorted(variables, key=lambda item: item.variable_id))


def _valid_structure(variables: tuple[GenerationVariable, ...], policy: GenerationPolicy) -> str | None:
    if len({item.variable_id for item in variables}) != len(variables):
        return "variable_id duplicado"
    if len(variables) > policy.max_variables:
        return "max_variables excedido"
    for variable in variables:
        if len(variable.domain) > policy.max_cardinality_per_variable:
            return f"cardinalidad por variable excedida: {variable.variable_id}"
    return None


def _effective_domains(variables: tuple[GenerationVariable, ...]) -> tuple[tuple[Any, ...], ...]:
    return tuple(
        tuple(value for value in variable.domain if not any(_canonical(value) == _canonical(excluded) for excluded in variable.excluded_values))
        for variable in variables
    )


def generate_scenarios(
    context: DecisionContext,
    variables: tuple[GenerationVariable, ...],
    policy: GenerationPolicy,
    parent_scenario_id: str | None = None,
    depth: int = 0,
) -> GenerationResult:
    """Generate a finite Cartesian set of candidate changes without invoking O2/O3."""
    del context  # Context is validated by the caller and remains authority; O4 does not clone identity.

    try:
        if depth < 0:
            return GenerationResult(status=GenerationStatus.FAILED, policy_version=policy.policy_version, reason="depth inválida")
        if depth > policy.max_depth:
            return GenerationResult(status=GenerationStatus.BLOCKED, policy_version=policy.policy_version, reason="max_depth excedido")

        canonical_variables = _canonical_variables(variables)
        structural_error = _valid_structure(canonical_variables, policy)
        if structural_error:
            return GenerationResult(status=GenerationStatus.BLOCKED, policy_version=policy.policy_version, reason=structural_error)

        domains = _effective_domains(canonical_variables)
        if any(len(domain) == 0 for domain in domains):
            return GenerationResult(status=GenerationStatus.EMPTY, policy_version=policy.policy_version)

        cardinality = prod(len(domain) for domain in domains) if domains else 1
        if cardinality > policy.max_total_cardinality:
            return GenerationResult(status=GenerationStatus.BLOCKED, policy_version=policy.policy_version, reason="max_total_cardinality excedido")
        if depth >= policy.max_depth and canonical_variables:
            return GenerationResult(status=GenerationStatus.BLOCKED, policy_version=policy.policy_version, reason="max_depth impediría la derivación")
        if cardinality > policy.max_emitted_candidates:
            return GenerationResult(status=GenerationStatus.BLOCKED, policy_version=policy.policy_version, reason="max_emitted_candidates excedido")

        import itertools
        combinations = itertools.product(*domains) if domains else [()]
        candidates: list[CandidateScenario] = []
        seen: set[tuple[tuple[str, str], ...]] = set()
        for values in combinations:
            changes = []
            for variable, simulated_value in zip(canonical_variables, values):
                if _canonical(variable.base_value) == _canonical(simulated_value):
                    continue
                changes.append(
                    AuthorizedScenarioChange(
                        variable=variable.variable_id,
                        base_value=variable.base_value,
                        simulated_value=simulated_value,
                        unit=None,
                        authorization=True,
                        origin="O4",
                    )
                )
            canonical_changes = tuple(sorted(changes, key=lambda item: (item.variable, _canonical(item.simulated_value))))
            key = tuple((item.variable, _canonical(item.simulated_value)) for item in canonical_changes)
            if key in seen:
                continue
            seen.add(key)
            candidates.append(CandidateScenario(parent_scenario_id=parent_scenario_id, depth=depth + 1 if canonical_variables else depth, changes=canonical_changes))

        if not candidates:
            return GenerationResult(status=GenerationStatus.EMPTY, policy_version=policy.policy_version)
        return GenerationResult(status=GenerationStatus.GENERATED, policy_version=policy.policy_version, candidates=tuple(candidates))
    except (TypeError, ValueError, OverflowError) as exc:
        return GenerationResult(status=GenerationStatus.NOT_EVALUABLE, policy_version=policy.policy_version, reason=f"cardinalidad/espacio no determinable: {exc}")


__all__ = [
    "CandidateScenario",
    "GenerationPolicy",
    "GenerationResult",
    "GenerationStatus",
    "GenerationVariable",
    "generate_scenarios",
]
