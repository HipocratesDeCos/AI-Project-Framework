"""Controlled O4 -> O2 -> O3 scenario orchestration.

This module does not produce analytical evidence. O3 is invoked only when an
explicit analytical package containing pre-produced Assessments and a
Viability Frontier result is supplied for every VALID O2 scenario.
"""
from __future__ import annotations

from copy import deepcopy
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .models import DecisionContext
from .o4_o2_integration import O4O2MaterializationResult, run_o4_o2_materialization
from .scenario_engine import ScenarioStatus
from .scenario_evaluation import (
    ScenarioEvaluationResult,
    ScenarioEvaluationStatus,
    evaluate_scenario,
)
from .scenario_generation import GenerationPolicy, GenerationVariable


class AuthorizedScenarioAnalytics(BaseModel):
    """Externally produced analytical inputs explicitly bound to one scenario."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    scenario_id: str = Field(min_length=1, max_length=64)
    assessments: tuple[Any, ...]
    viability_result: Any
    limitations: tuple[str, ...] = ()
    trace_references: tuple[str, ...] = ()
    status: ScenarioEvaluationStatus = ScenarioEvaluationStatus.COMPLETED
    failure_reason: str | None = None

    @model_validator(mode="after")
    def validate_authorized_analytics(self) -> "AuthorizedScenarioAnalytics":
        if not self.assessments:
            raise ValueError("La orquestación requiere Assessment explícito y no vacío")
        if self.viability_result is None:
            raise ValueError("La orquestación requiere Viability Frontier explícito")
        return self


class O4O2O3OrchestrationResult(BaseModel):
    """Immutable chain output preserving O4/O2 materialization and O3 results."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    materialization: O4O2MaterializationResult
    evaluations: tuple[ScenarioEvaluationResult, ...] = ()

    @model_validator(mode="after")
    def validate_chain(self) -> "O4O2O3OrchestrationResult":
        valid_ids = tuple(
            scenario.scenario_id
            for scenario in self.materialization.scenarios
            if scenario.status == ScenarioStatus.VALID
        )
        evaluation_ids = tuple(item.scenario_id for item in self.evaluations)
        if evaluation_ids != valid_ids:
            raise ValueError(
                "Las evaluaciones O3 deben corresponder exactamente y en orden a los escenarios O2 VALID"
            )
        return self


def run_o4_o2_o3_orchestration(
    *,
    context: DecisionContext,
    variables: tuple[GenerationVariable, ...],
    policy: GenerationPolicy,
    analytics: tuple[AuthorizedScenarioAnalytics, ...] = (),
    parent_scenario_id: str | None = None,
    depth: int = 0,
) -> O4O2O3OrchestrationResult:
    """Run O4/O2 and invoke O3 only with complete explicit analytical inputs."""
    context_snapshot = context.model_copy(deep=True)
    variables_snapshot = tuple(item.model_copy(deep=True) for item in variables)
    policy_snapshot = policy.model_copy(deep=True)
    analytics_snapshot = tuple(item.model_copy(deep=True) for item in analytics)

    materialization = run_o4_o2_materialization(
        context=context_snapshot.model_copy(deep=True),
        variables=variables_snapshot,
        policy=policy_snapshot,
        parent_scenario_id=parent_scenario_id,
        depth=depth,
    )
    materialization_snapshot = materialization.model_copy(deep=True)

    valid_scenarios = tuple(
        scenario
        for scenario in materialization_snapshot.scenarios
        if scenario.status == ScenarioStatus.VALID
    )
    supplied_ids = tuple(item.scenario_id for item in analytics_snapshot)

    if len(set(supplied_ids)) != len(supplied_ids):
        raise ValueError("scenario_id analítico duplicado")

    expected_ids = tuple(scenario.scenario_id for scenario in valid_scenarios)
    expected_set = set(expected_ids)
    supplied_set = set(supplied_ids)
    if supplied_set != expected_set:
        missing = sorted(expected_set - supplied_set)
        unexpected = sorted(supplied_set - expected_set)
        details: list[str] = []
        if missing:
            details.append(f"faltan paquetes analíticos para: {', '.join(missing)}")
        if unexpected:
            details.append(f"paquetes analíticos no autorizados/sobrantes: {', '.join(unexpected)}")
        raise ValueError("; ".join(details) or "correspondencia analítica inválida")

    analytics_by_id = {item.scenario_id: item for item in analytics_snapshot}
    evaluations: list[ScenarioEvaluationResult] = []
    for scenario in valid_scenarios:
        analytical_input = analytics_by_id[scenario.scenario_id]
        evaluations.append(
            evaluate_scenario(
                scenario.model_copy(deep=True),
                context_snapshot.model_copy(deep=True),
                assessments=deepcopy(tuple(analytical_input.assessments)),
                viability_result=deepcopy(analytical_input.viability_result),
                limitations=tuple(analytical_input.limitations),
                trace_references=tuple(analytical_input.trace_references),
                status=analytical_input.status,
                failure_reason=analytical_input.failure_reason,
            )
        )

    return O4O2O3OrchestrationResult(
        materialization=materialization_snapshot,
        evaluations=tuple(evaluations),
    )


__all__ = [
    "AuthorizedScenarioAnalytics",
    "O4O2O3OrchestrationResult",
    "run_o4_o2_o3_orchestration",
]
