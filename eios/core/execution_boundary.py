"""Controlled E2E execution boundary.

Coordinates explicitly authorized capability callables and returns their
contractual outcomes. It does not calculate, rank, select, recommend, or
execute a purchase.
"""
from __future__ import annotations

from collections.abc import Callable, Mapping
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, model_validator

from eios.kernel.execution import (
    KernelCapabilityResult,
    KernelContext,
    KernelOperation,
    KernelPlan,
    execute_kernel,
)

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
    """Compatibility adapter for EIOS purchases over the SINGLE neutral runtime.

    Keep the original PurchaseOperation/DecisionContext public API and legacy
    result types. Only the generic technical iteration is delegated; no new
    purchase, price, evidence or decision semantics are introduced here.
    """
    if purchase_operation.decision_id != context.decision_id:
        raise ExecutionBoundaryError("decision_id inconsistente")
    if purchase_operation.scenario_id != context.scenario_id:
        raise ExecutionBoundaryError("scenario_id inconsistente")

    neutral_context = KernelContext(
        project_id="EIOS_PURCHASES",
        decision_id=context.decision_id,
        scenario_id=context.scenario_id,
        rules_version=context.rules_version,
        parameters_version=context.parameters_version,
        data_snapshot_id=context.data_snapshot_id,
    )
    neutral_operation = KernelOperation(
        decision_id=purchase_operation.decision_id,
        scenario_id=purchase_operation.scenario_id,
        payload=purchase_operation,
    )
    neutral_plan = KernelPlan(
        capabilities=plan.capabilities, policy_version=plan.policy_version,
    )

    def adapt(invoker):
        def invoke(operation, execution_context):
            # Each caller receives independently copied original canonical
            # contracts. The generic kernel owns both copy and call order.
            legacy_context = DecisionContext(
                decision_id=execution_context.decision_id,
                scenario_id=execution_context.scenario_id,
                rules_version=execution_context.rules_version,
                parameters_version=execution_context.parameters_version,
                data_snapshot_id=execution_context.data_snapshot_id,
            )
            original = invoker(operation, legacy_context)
            if not isinstance(original, CapabilityExecution):
                raise ExecutionBoundaryError(
                    "capacidad no devolvió CapabilityExecution"
                )
            return KernelCapabilityResult.model_validate(
                original.model_dump(mode="python")
            )
        return invoke

    # Preserve the invoker references used at preflight (no dynamic imports,
    # no arbitrary adapter-specific capability authority).
    adapted_invokers = {
        name: adapt(invoker) if callable(invoker) else invoker
        for name, invoker in dict(invokers).items()
    }
    technical = execute_kernel(
        neutral_operation, neutral_context, neutral_plan, adapted_invokers,
    )
    return ExecutionOutcome(
        status=BoundaryStatus(technical.status.value),
        policy_version=technical.policy_version,
        capability_results=tuple(
            CapabilityExecution.model_validate(item.model_dump(mode="python"))
            for item in technical.capability_results
        ),
        unresolved_items=technical.unresolved_items,
        failure_reason=technical.failure_reason,
    )


__all__ = [
    "BoundaryStatus",
    "ExecutionBoundaryError",
    "ExecutionOutcome",
    "ExecutionPlan",
    "execute_plan",
]
