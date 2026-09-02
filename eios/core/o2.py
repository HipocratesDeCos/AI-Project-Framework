"""O2 coordinated scenario support envelope.

O2 coordinates already-produced capability outputs. It does not calculate,
rank, select, approve, reject, optimize, or recommend a business decision.
"""
from __future__ import annotations

from hashlib import sha256
import json
from enum import Enum
from typing import Any, Mapping, Sequence

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .models import DecisionContext, PurchaseOperation


class O2ScenarioStatus(str, Enum):
    READY = "READY"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    BLOCKED = "BLOCKED"
    PARTIALLY_COMPLETED = "PARTIALLY_COMPLETED"
    NOT_EVALUABLE = "NOT_EVALUABLE"
    FAILED = "FAILED"


class O2ScenarioResult(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    scenario_id: str = Field(min_length=1, max_length=64)
    status: O2ScenarioStatus
    values: Mapping[str, Any] = {}
    trace_references: tuple[str, ...] = ()
    unresolved_items: tuple[str, ...] = ()
    failure_reason: str | None = Field(default=None, max_length=512)

    @model_validator(mode="after")
    def validate_state(self) -> "O2ScenarioResult":
        if self.status == O2ScenarioStatus.FAILED and not self.failure_reason:
            raise ValueError("FAILED requiere failure_reason")
        if self.status != O2ScenarioStatus.FAILED and self.failure_reason is not None:
            raise ValueError("failure_reason solo puede existir en FAILED")
        return self


class O2ExecutionContext(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    execution_id: str = Field(min_length=1, max_length=128)
    decision_id: str = Field(min_length=1, max_length=64)
    rules_version: str = Field(min_length=1, max_length=64)
    parameters_version: str = Field(min_length=1, max_length=64)
    data_snapshot_id: str = Field(min_length=1, max_length=64)


class O2Comparison(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    scenario_ids: tuple[str, ...]
    observations: Mapping[str, Mapping[str, Any]]
    differences: Mapping[str, tuple[Any, ...]]
    missing: Mapping[str, tuple[str, ...]]
    statuses: Mapping[str, O2ScenarioStatus]
    unresolved_items: Mapping[str, tuple[str, ...]]
    traceability: Mapping[str, tuple[str, ...]]


class O2SupportPackage(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    execution_context: O2ExecutionContext
    scenarios: tuple[O2ScenarioResult, ...]
    comparison: O2Comparison | None = None


def build_execution_context(context: DecisionContext, scenario_ids: Sequence[str]) -> O2ExecutionContext:
    normalized = sorted(set(scenario_ids))
    if not normalized or any(not value for value in normalized):
        raise ValueError("O2 requiere al menos un scenario_id")
    material = "|".join((context.decision_id, context.rules_version,
                          context.parameters_version, context.data_snapshot_id,
                          *normalized))
    execution_id = sha256(f"eios:o2:{material}".encode()).hexdigest()
    return O2ExecutionContext(execution_id=execution_id, decision_id=context.decision_id,
                              rules_version=context.rules_version,
                              parameters_version=context.parameters_version,
                              data_snapshot_id=context.data_snapshot_id)


def compare_scenarios(results: Sequence[O2ScenarioResult]) -> O2Comparison:
    if len(results) < 2:
        raise ValueError("comparison requires at least two scenarios")
    ids = tuple(result.scenario_id for result in results)
    if len(set(ids)) != len(ids):
        raise ValueError("scenario_id debe ser único")
    keys = sorted({key for result in results for key in result.values})
    observations: dict[str, dict[str, Any]] = {}
    differences: dict[str, tuple[Any, ...]] = {}
    missing: dict[str, tuple[str, ...]] = {}
    for key in keys:
        row = {r.scenario_id: r.values[key] for r in results if key in r.values}
        absent = tuple(r.scenario_id for r in results if key not in r.values)
        observations[key] = row
        if absent:
            missing[key] = absent
        vals = tuple(row.values())
        if len(vals) >= 2 and any(value != vals[0] for value in vals[1:]):
            differences[key] = vals
    return O2Comparison(
        scenario_ids=ids,
        observations=observations,
        differences=differences,
        missing=missing,
        statuses={r.scenario_id: r.status for r in results},
        unresolved_items={r.scenario_id: r.unresolved_items for r in results},
        traceability={r.scenario_id: r.trace_references for r in results},
    )


def build_support_package(purchase_operation: PurchaseOperation,
                          context: DecisionContext,
                          scenarios: Sequence[O2ScenarioResult]) -> O2SupportPackage:
    if purchase_operation.decision_id != context.decision_id:
        raise ValueError("decision_id incompatible")
    results = tuple(scenarios)
    if not results:
        raise ValueError("O2 requiere escenarios")
    if any(result.scenario_id != purchase_operation.scenario_id and
           result.scenario_id == "" for result in results):
        raise ValueError("scenario_id inválido")
    execution = build_execution_context(context, [r.scenario_id for r in results])
    comparison = compare_scenarios(results) if len(results) >= 2 else None
    return O2SupportPackage(execution_context=execution, scenarios=results, comparison=comparison)


__all__ = ["O2Comparison", "O2ExecutionContext", "O2ScenarioResult",
           "O2ScenarioStatus", "O2SupportPackage", "build_execution_context",
           "build_support_package", "compare_scenarios"]
