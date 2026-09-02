"""O1 operational orchestration envelope for the EIOS MVP.

O1 coordinates execution state and references. It does not calculate, rank,
select, approve, reject, or execute a purchase and does not replace the
contracts of existing capabilities.
"""
from __future__ import annotations

from enum import Enum
from uuid import NAMESPACE_URL, uuid5

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .models import DecisionContext, PurchaseOperation


class O1ExecutionStatus(str, Enum):
    READY = "READY"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    BLOCKED = "BLOCKED"
    PARTIALLY_COMPLETED = "PARTIALLY_COMPLETED"
    NOT_EVALUABLE = "NOT_EVALUABLE"
    FAILED = "FAILED"


class CapabilityExecution(BaseModel):
    """Execution state and trace references for one existing capability."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    capability: str = Field(min_length=1, max_length=64)
    status: O1ExecutionStatus
    result_available: bool
    trace_references: tuple[str, ...] = ()
    unresolved_items: tuple[str, ...] = ()
    failure_reason: str | None = Field(default=None, max_length=512)

    @model_validator(mode="after")
    def validate_state(self) -> "CapabilityExecution":
        if self.status == O1ExecutionStatus.FAILED and not self.failure_reason:
            raise ValueError("FAILED requiere failure_reason")
        if self.status != O1ExecutionStatus.FAILED and self.failure_reason is not None:
            raise ValueError("failure_reason solo puede existir en FAILED")
        if self.result_available and self.status in {
            O1ExecutionStatus.READY,
            O1ExecutionStatus.RUNNING,
            O1ExecutionStatus.NOT_EVALUABLE,
        }:
            raise ValueError("Estos estados no pueden declarar result_available")
        return self


class O1ExecutionContext(BaseModel):
    """Common execution identity inherited from the canonical DecisionContext."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    execution_id: str = Field(min_length=1, max_length=128)
    decision_id: str = Field(min_length=1, max_length=64)
    scenario_id: str = Field(min_length=1, max_length=64)
    rules_version: str = Field(min_length=1, max_length=64)
    parameters_version: str = Field(min_length=1, max_length=64)
    data_snapshot_id: str = Field(min_length=1, max_length=64)

    @classmethod
    def from_context(cls, context: DecisionContext) -> "O1ExecutionContext":
        material = "|".join(
            (
                context.decision_id,
                context.scenario_id,
                context.rules_version,
                context.parameters_version,
                context.data_snapshot_id,
            )
        )
        execution_id = str(uuid5(NAMESPACE_URL, f"eios:o1:{material}"))
        return cls(execution_id=execution_id, **context.model_dump())


class DecisionSupportPackage(BaseModel):
    """Traceable O1 package; never a business decision."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    execution_context: O1ExecutionContext
    execution_status: O1ExecutionStatus
    capability_results: tuple[CapabilityExecution, ...] = ()
    evidence_status: tuple[str, ...] = ()
    version_context: tuple[str, ...] = ()
    trace_references: tuple[str, ...] = ()
    unresolved_items: tuple[str, ...] = ()

    @model_validator(mode="after")
    def validate_package(self) -> "DecisionSupportPackage":
        if self.execution_status == O1ExecutionStatus.COMPLETED:
            incomplete = {
                O1ExecutionStatus.READY,
                O1ExecutionStatus.RUNNING,
                O1ExecutionStatus.BLOCKED,
                O1ExecutionStatus.PARTIALLY_COMPLETED,
                O1ExecutionStatus.NOT_EVALUABLE,
                O1ExecutionStatus.FAILED,
            }
            if any(item.status in incomplete for item in self.capability_results):
                raise ValueError("COMPLETED no puede contener capacidades incompletas")
        if self.unresolved_items and self.execution_status == O1ExecutionStatus.COMPLETED:
            raise ValueError("COMPLETED no puede contener unresolved_items")
        return self


def build_execution_context(context: DecisionContext) -> O1ExecutionContext:
    """Create the O1 envelope without creating a parallel versioning system."""
    return O1ExecutionContext.from_context(context)


def build_support_package(
    purchase_operation: PurchaseOperation,
    context: DecisionContext,
    capability_results: tuple[CapabilityExecution, ...] = (),
    evidence_status: tuple[str, ...] = (),
) -> DecisionSupportPackage:
    """Build a support package from supplied capability outcomes only.

    No capability is invoked here; callers provide already-authorized results.
    """
    if purchase_operation.decision_id != context.decision_id:
        raise ValueError("PurchaseOperation y DecisionContext tienen decision_id distintos")
    if purchase_operation.scenario_id != context.scenario_id:
        raise ValueError("PurchaseOperation y DecisionContext tienen scenario_id distintos")

    context_o1 = build_execution_context(context)
    trace_refs = tuple(
        sorted({ref for result in capability_results for ref in result.trace_references})
    )
    unresolved = tuple(
        sorted({item for result in capability_results for item in result.unresolved_items})
    )

    statuses = {result.status for result in capability_results}
    if any(status == O1ExecutionStatus.FAILED for status in statuses):
        overall = O1ExecutionStatus.FAILED
    elif any(
        status in {
            O1ExecutionStatus.BLOCKED,
            O1ExecutionStatus.NOT_EVALUABLE,
            O1ExecutionStatus.PARTIALLY_COMPLETED,
        }
        for status in statuses
    ):
        overall = O1ExecutionStatus.PARTIALLY_COMPLETED
    elif capability_results and all(
        result.status == O1ExecutionStatus.COMPLETED for result in capability_results
    ):
        overall = O1ExecutionStatus.COMPLETED
    else:
        overall = O1ExecutionStatus.READY

    versions = (
        context.rules_version,
        context.parameters_version,
        context.data_snapshot_id,
    )
    return DecisionSupportPackage(
        execution_context=context_o1,
        execution_status=overall,
        capability_results=capability_results,
        evidence_status=evidence_status,
        version_context=versions,
        trace_references=trace_refs,
        unresolved_items=unresolved,
    )


__all__ = [
    "CapabilityExecution",
    "DecisionSupportPackage",
    "O1ExecutionContext",
    "O1ExecutionStatus",
    "build_execution_context",
    "build_support_package",
]
