"""Controlled E2E execution boundary.

Coordinates explicitly authorized capability callables and returns their
contractual outcomes. It does not calculate, rank, select, recommend, or
execute a purchase.
"""
from __future__ import annotations

from collections.abc import Callable, Mapping
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .models import DecisionContext, PurchaseOperation
from .orchestration import CapabilityExecution


class ExecutionBoundaryError(ValueError):
    """Raised when the controlled execution plan is invalid."""


class BoundaryStatus(str, Enum):
    READY = "READY"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    PARTIALLY_COMPLETED = "PARTIALLY_COMPLETED"
    NOT_EVALUABLE = "NOT_EVALUABLE"
    BLOCKED = "BLOCKED"
    FAILED = "FAILED"


class ExecutionPlan(BaseModel):
    """Explicit, immutable list of authorized capabilities and policy version."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    capabilities: tuple[str, ...] = Field(min_length=1)
    policy_version: str = Field(min_length=1, max_length=64)

    @model_validator(mode="after")
    def validate_unique(self) -> "ExecutionPlan":
        if len(set(self.capabilities)) != len(self.capabilities):
            raise ValueError("capabilities deben ser únicas")
        return self


class ExecutionOutcome(BaseModel):
    """Technical outcome returned by the boundary."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    status: BoundaryStatus
    policy_version: str = Field(min_length=1, max_length=64)
    capability_results: tuple[CapabilityExecution, ...] = ()
    unresolved_items: tuple[str, ...] = ()
    failure_reason: str | None = Field(default=None, max_length=512)


def execute_plan(
    purchase_operation: PurchaseOperation,
    context: DecisionContext,
    plan: ExecutionPlan,
    invokers: Mapping[str, Callable[[PurchaseOperation, DecisionContext], CapabilityExecution]],
) -> ExecutionOutcome:
    """Execute only explicitly declared invokers after complete preflight validation."""
    if purchase_operation.decision_id != context.decision_id:
        raise ExecutionBoundaryError("decision_id inconsistente")
    if purchase_operation.scenario_id != context.scenario_id:
        raise ExecutionBoundaryError("scenario_id inconsistente")

    # Complete preflight: every declared capability must be present before any call.
    missing = tuple(name for name in plan.capabilities if name not in invokers)
    if missing:
        return ExecutionOutcome(
            status=BoundaryStatus.BLOCKED,
            policy_version=plan.policy_version,
            unresolved_items=missing,
        )

    results: list[CapabilityExecution] = []
    for name in plan.capabilities:
        try:
            result = invokers[name](purchase_operation, context)
            if not isinstance(result, CapabilityExecution):
                raise ExecutionBoundaryError(
                    f"capacidad {name} no devolvió CapabilityExecution"
                )
            results.append(result)
        except Exception as exc:
            reason = str(exc).strip() or exc.__class__.__name__
            return ExecutionOutcome(
                status=BoundaryStatus.FAILED,
                policy_version=plan.policy_version,
                capability_results=tuple(results),
                failure_reason=f"{name}: {reason}"[:512],
            )

    unresolved = tuple(
        sorted({item for result in results for item in result.unresolved_items})
    )
    if any(result.status.name == "FAILED" for result in results):
        status = BoundaryStatus.FAILED
    elif any(
        result.status.name in {"BLOCKED", "NOT_EVALUABLE", "PARTIALLY_COMPLETED"}
        for result in results
    ):
        status = BoundaryStatus.PARTIALLY_COMPLETED
    else:
        status = BoundaryStatus.COMPLETED

    return ExecutionOutcome(
        status=status,
        policy_version=plan.policy_version,
        capability_results=tuple(results),
        unresolved_items=unresolved,
    )


__all__ = [
    "BoundaryStatus",
    "ExecutionBoundaryError",
    "ExecutionOutcome",
    "ExecutionPlan",
    "execute_plan",
]
