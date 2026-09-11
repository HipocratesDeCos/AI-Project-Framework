"""Controlled E2E execution boundary.

Coordinates explicitly authorized capability callables and returns their
contractual outcomes. It does not calculate, rank, select, recommend, or
execute a purchase.
"""
from __future__ import annotations

from collections.abc import Callable, Mapping
from enum import Enum
from types import MappingProxyType

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .models import DecisionContext, PurchaseOperation
from .orchestration import CapabilityExecution, O1ExecutionStatus


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
    """Terminal technical outcome returned by the synchronous boundary."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    status: BoundaryStatus
    policy_version: str = Field(min_length=1, max_length=64)
    capability_results: tuple[CapabilityExecution, ...] = ()
    unresolved_items: tuple[str, ...] = ()
    failure_reason: str | None = Field(default=None, max_length=512)

    @model_validator(mode="after")
    def validate_terminal_state(self) -> "ExecutionOutcome":
        if self.status in {
            BoundaryStatus.READY,
            BoundaryStatus.RUNNING,
            BoundaryStatus.NOT_EVALUABLE,
        }:
            raise ValueError("ExecutionOutcome síncrono requiere un estado terminal")

        if self.status == BoundaryStatus.FAILED and not self.failure_reason:
            raise ValueError("FAILED requiere failure_reason")
        if self.status != BoundaryStatus.FAILED and self.failure_reason is not None:
            raise ValueError("failure_reason solo puede existir en FAILED")

        if self.status == BoundaryStatus.COMPLETED:
            if self.unresolved_items:
                raise ValueError("COMPLETED no puede contener unresolved_items")
            if any(
                result.status != O1ExecutionStatus.COMPLETED
                or not result.result_available
                for result in self.capability_results
            ):
                raise ValueError(
                    "COMPLETED requiere capacidades COMPLETED con resultado disponible"
                )

        if self.status == BoundaryStatus.BLOCKED and not self.unresolved_items:
            raise ValueError("BLOCKED requiere unresolved_items")

        return self


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

    # Freeze the catalog view used by this execution so external mutation cannot
    # alter which invoker is selected after preflight.
    catalog = MappingProxyType(dict(invokers))

    # Complete preflight: every declared capability must exist and be callable
    # before the first capability is invoked.
    missing = tuple(name for name in plan.capabilities if name not in catalog)
    if missing:
        return ExecutionOutcome(
            status=BoundaryStatus.BLOCKED,
            policy_version=plan.policy_version,
            unresolved_items=missing,
        )

    invalid = tuple(name for name in plan.capabilities if not callable(catalog[name]))
    if invalid:
        return ExecutionOutcome(
            status=BoundaryStatus.BLOCKED,
            policy_version=plan.policy_version,
            unresolved_items=tuple(f"{name}:INVALID_INVOKER" for name in invalid),
        )

    # Keep canonical snapshots owned by the boundary. Each invoker receives a
    # fresh deep copy so one capability cannot mutate the input seen by another
    # capability or the caller's original objects.
    canonical_purchase = purchase_operation.model_copy(deep=True)
    canonical_context = context.model_copy(deep=True)

    results: list[CapabilityExecution] = []
    for name in plan.capabilities:
        try:
            result = catalog[name](
                canonical_purchase.model_copy(deep=True),
                canonical_context.model_copy(deep=True),
            )
            if not isinstance(result, CapabilityExecution):
                raise ExecutionBoundaryError(
                    f"capacidad {name} no devolvió CapabilityExecution"
                )
            if result.capability != name:
                raise ExecutionBoundaryError(
                    f"capacidad {name} devolvió identidad {result.capability}"
                )
            if (
                result.status == O1ExecutionStatus.COMPLETED
                and not result.result_available
            ):
                raise ExecutionBoundaryError(
                    f"capacidad {name} declaró COMPLETED sin resultado disponible"
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
    failed = next(
        (result for result in results if result.status == O1ExecutionStatus.FAILED),
        None,
    )
    if failed is not None:
        status = BoundaryStatus.FAILED
        failure_reason = f"{failed.capability}: {failed.failure_reason}"[:512]
    elif any(
        result.status in {
            O1ExecutionStatus.READY,
            O1ExecutionStatus.RUNNING,
            O1ExecutionStatus.BLOCKED,
            O1ExecutionStatus.NOT_EVALUABLE,
            O1ExecutionStatus.PARTIALLY_COMPLETED,
        }
        for result in results
    ):
        status = BoundaryStatus.PARTIALLY_COMPLETED
        failure_reason = None
    else:
        status = BoundaryStatus.COMPLETED
        failure_reason = None

    return ExecutionOutcome(
        status=status,
        policy_version=plan.policy_version,
        capability_results=tuple(results),
        unresolved_items=unresolved,
        failure_reason=failure_reason,
    )


__all__ = [
    "BoundaryStatus",
    "ExecutionBoundaryError",
    "ExecutionOutcome",
    "ExecutionPlan",
    "execute_plan",
]
