"""O3 controlled scenario evaluation.

This module represents derived evaluation results only. It does not execute
rules or viability logic and never mutates the scenario or historical inputs.
"""
from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .models import DecisionContext
from .scenario_engine import ScenarioStatus, ScenarioVersion


class ScenarioEvaluationStatus(str, Enum):
    NOT_STARTED = "NOT_STARTED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    PARTIALLY_COMPLETED = "PARTIALLY_COMPLETED"
    NOT_EVALUABLE = "NOT_EVALUABLE"
    FAILED = "FAILED"


class ScenarioEvaluationResult(BaseModel):
    """Immutable, derived result of evaluating one valid scenario."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    scenario_id: str = Field(min_length=1, max_length=64)
    decision_id: str = Field(min_length=1, max_length=64)
    rules_version: str = Field(min_length=1, max_length=64)
    parameters_version: str = Field(min_length=1, max_length=64)
    data_snapshot_id: str = Field(min_length=1, max_length=64)
    status: ScenarioEvaluationStatus
    assessments: tuple[Any, ...] = ()
    viability_result: Any | None = None
    limitations: tuple[str, ...] = ()
    trace_references: tuple[str, ...] = ()
    failure_reason: str | None = None

    @model_validator(mode="after")
    def validate_result(self) -> "ScenarioEvaluationResult":
        if self.status == ScenarioEvaluationStatus.FAILED and not self.failure_reason:
            raise ValueError("FAILED requiere failure_reason")
        if self.status != ScenarioEvaluationStatus.FAILED and self.failure_reason is not None:
            raise ValueError("failure_reason solo es válido para FAILED")
        if self.status == ScenarioEvaluationStatus.COMPLETED and self.limitations:
            raise ValueError("COMPLETED no puede conservar limitaciones pendientes")
        return self


def evaluate_scenario(
    scenario: ScenarioVersion,
    context: DecisionContext,
    *,
    assessments: tuple[Any, ...] = (),
    viability_result: Any | None = None,
    limitations: tuple[str, ...] = (),
    trace_references: tuple[str, ...] = (),
    status: ScenarioEvaluationStatus = ScenarioEvaluationStatus.COMPLETED,
    failure_reason: str | None = None,
) -> ScenarioEvaluationResult:
    """Build a derived evaluation result without executing or mutating inputs."""
    if scenario.status != ScenarioStatus.VALID:
        raise ValueError("O3 requiere un ScenarioVersion VALID")
    if scenario.decision_id != context.decision_id:
        raise ValueError("scenario.decision_id debe coincidir con DecisionContext")
    if scenario.rules_version != context.rules_version:
        raise ValueError("rules_version incoherente con ScenarioVersion")
    if scenario.parameters_version != context.parameters_version:
        raise ValueError("parameters_version incoherente con ScenarioVersion")
    if scenario.data_snapshot_id != context.data_snapshot_id:
        raise ValueError("data_snapshot_id incoherente con ScenarioVersion")

    return ScenarioEvaluationResult(
        scenario_id=scenario.scenario_id,
        decision_id=context.decision_id,
        rules_version=context.rules_version,
        parameters_version=context.parameters_version,
        data_snapshot_id=context.data_snapshot_id,
        status=status,
        assessments=tuple(assessments),
        viability_result=viability_result,
        limitations=tuple(limitations),
        trace_references=tuple(trace_references),
        failure_reason=failure_reason,
    )


__all__ = ["ScenarioEvaluationResult", "ScenarioEvaluationStatus", "evaluate_scenario"]
