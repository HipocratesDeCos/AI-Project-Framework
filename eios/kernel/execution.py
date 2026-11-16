"""EIOS F4.2 — domain-neutral, *technical-only* synchronous execution kernel.

One execution loop for all explicitly selected capabilities. The purchase
boundary in eios.core.execution_boundary is a compatibility adapter over
this kernel. The kernel does not select capabilities, infer provenance,
authenticate an enterprise, make decisions or authorize operations.
"""
from __future__ import annotations

from collections.abc import Callable, Mapping
from enum import Enum
from types import MappingProxyType
from typing import Literal

from pydantic import (
    BaseModel, ConfigDict, Field, InstanceOf, model_validator,
)


class KernelExecutionError(ValueError):
    """Preflight identity error, before invoking any supplied capability."""


class KernelStatus(str, Enum):
    READY = "READY"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    PARTIALLY_COMPLETED = "PARTIALLY_COMPLETED"
    NOT_EVALUABLE = "NOT_EVALUABLE"
    BLOCKED = "BLOCKED"
    FAILED = "FAILED"


class KernelCapabilityStatus(str, Enum):
    READY = "READY"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    BLOCKED = "BLOCKED"
    PARTIALLY_COMPLETED = "PARTIALLY_COMPLETED"
    NOT_EVALUABLE = "NOT_EVALUABLE"
    FAILED = "FAILED"


class KernelContext(BaseModel):
    """Execution identity independent of products, suppliers and verticals."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    project_id: str = Field(min_length=1, max_length=128)
    decision_id: str = Field(min_length=1, max_length=64)
    scenario_id: str = Field(min_length=1, max_length=64)
    rules_version: str = Field(min_length=1, max_length=64)
    parameters_version: str = Field(min_length=1, max_length=64)
    data_snapshot_id: str = Field(min_length=1, max_length=64)


class KernelOperation(BaseModel):
    """Opaque *typed* domain payload and explicit, independent case identity."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    decision_id: str = Field(min_length=1, max_length=64)
    scenario_id: str = Field(min_length=1, max_length=64)
    payload: InstanceOf[BaseModel]


class KernelPlan(BaseModel):
    """Only capabilities explicitly declared by this caller may be invoked."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    capabilities: tuple[str, ...] = Field(min_length=1)
    policy_version: str = Field(min_length=1, max_length=64)

    @model_validator(mode="after")
    def validate_unique(self) -> "KernelPlan":
        if any(not name.strip() or name != name.strip() for name in self.capabilities):
            raise ValueError("Los identificadores de capacidades deben ser válidos")
        if len(set(self.capabilities)) != len(self.capabilities):
            raise ValueError("capabilities deben ser únicas")
        return self


class KernelCapabilityResult(BaseModel):
    """Technical observation only; no business outcome/authority fields."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    capability: str = Field(min_length=1, max_length=64)
    status: KernelCapabilityStatus
    result_available: bool
    trace_references: tuple[str, ...] = ()
    unresolved_items: tuple[str, ...] = ()
    failure_reason: str | None = Field(default=None, max_length=512)

    @model_validator(mode="after")
    def validate_state(self) -> "KernelCapabilityResult":
        if self.status == KernelCapabilityStatus.FAILED and not self.failure_reason:
            raise ValueError("FAILED requiere failure_reason")
        if self.status != KernelCapabilityStatus.FAILED and self.failure_reason is not None:
            raise ValueError("failure_reason solo puede existir en FAILED")
        if self.result_available and self.status in {
            KernelCapabilityStatus.READY,
            KernelCapabilityStatus.RUNNING,
            KernelCapabilityStatus.NOT_EVALUABLE,
        }:
            raise ValueError("Estos estados no pueden declarar result_available")
        return self


class KernelOutcome(BaseModel):
    """Terminal runtime result; a completed invocation is NOT a decision."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    status: KernelStatus
    project_id: str = Field(min_length=1, max_length=128)
    decision_id: str = Field(min_length=1, max_length=64)
    scenario_id: str = Field(min_length=1, max_length=64)
    policy_version: str = Field(min_length=1, max_length=64)
    capability_results: tuple[KernelCapabilityResult, ...] = ()
    unresolved_items: tuple[str, ...] = ()
    failure_reason: str | None = Field(default=None, max_length=512)
    provenance_status: Literal["UNVERIFIED_ADAPTER_RESPONSIBILITY"] = (
        "UNVERIFIED_ADAPTER_RESPONSIBILITY"
    )
    decision_authority: Literal[False] = False
    operational_path: Literal["FORBIDDEN"] = "FORBIDDEN"

    @model_validator(mode="after")
    def validate_terminal_state(self) -> "KernelOutcome":
        if self.status in {
            KernelStatus.READY, KernelStatus.RUNNING, KernelStatus.NOT_EVALUABLE,
        }:
            raise ValueError("KernelOutcome síncrono requiere un estado terminal")
        if self.status == KernelStatus.FAILED and not self.failure_reason:
            raise ValueError("FAILED requiere failure_reason")
        if self.status != KernelStatus.FAILED and self.failure_reason is not None:
            raise ValueError("failure_reason solo puede existir en FAILED")
        if self.status == KernelStatus.COMPLETED:
            if self.unresolved_items:
                raise ValueError("COMPLETED no puede contener unresolved_items")
            if any(
                item.status != KernelCapabilityStatus.COMPLETED
                or not item.result_available
                for item in self.capability_results
            ):
                raise ValueError(
                    "COMPLETED requiere capacidades COMPLETED con resultado disponible"
                )
        if self.status == KernelStatus.BLOCKED and not self.unresolved_items:
            raise ValueError("BLOCKED requiere unresolved_items")
        return self


KernelInvoker = Callable[[BaseModel, KernelContext], KernelCapabilityResult]


def execute_kernel(
    operation: KernelOperation,
    context: KernelContext,
    plan: KernelPlan,
    invokers: Mapping[str, KernelInvoker],
) -> KernelOutcome:
    """Execute a plan using ONE neutral, synchronous, fail-closed runtime.

    No default invokers, no dynamic imports or business authorities exist.
    Each invoker receives an independent deep copy of the typed domain payload
    and versioned context. Application adapters own input/document verification.
    """
    if operation.decision_id != context.decision_id:
        raise KernelExecutionError("decision_id inconsistente")
    if operation.scenario_id != context.scenario_id:
        raise KernelExecutionError("scenario_id inconsistente")

    identity = dict(
        project_id=context.project_id,
        decision_id=context.decision_id,
        scenario_id=context.scenario_id,
        policy_version=plan.policy_version,
    )
    catalog = MappingProxyType(dict(invokers))

    # O1 is a separate controlled support-package boundary, not an invoker.
    # QTG requires its separate provenance-safe Decision Input Package producer.
    forbidden = tuple(
        name for name in plan.capabilities if name in ("O1", "QTG")
    )
    if forbidden:
        return KernelOutcome(
            status=KernelStatus.BLOCKED, **identity,
            unresolved_items=tuple(
                f"{name}:FORBIDDEN_BOUNDARY_CAPABILITY" for name in forbidden
            ),
        )
    missing = tuple(name for name in plan.capabilities if name not in catalog)
    if missing:
        return KernelOutcome(
            status=KernelStatus.BLOCKED, **identity, unresolved_items=missing,
        )
    invalid = tuple(name for name in plan.capabilities if not callable(catalog[name]))
    if invalid:
        return KernelOutcome(
            status=KernelStatus.BLOCKED, **identity,
            unresolved_items=tuple(f"{name}:INVALID_INVOKER" for name in invalid),
        )

    canonical_operation = operation.model_copy(deep=True)
    canonical_context = context.model_copy(deep=True)
    results: list[KernelCapabilityResult] = []
    for name in plan.capabilities:
        try:
            result = catalog[name](
                canonical_operation.payload.model_copy(deep=True),
                canonical_context.model_copy(deep=True),
            )
            if not isinstance(result, KernelCapabilityResult):
                raise KernelExecutionError(
                    f"capacidad {name} no devolvió KernelCapabilityResult"
                )
            if result.capability != name:
                raise KernelExecutionError(
                    f"capacidad {name} devolvió identidad {result.capability}"
                )
            if (
                result.status == KernelCapabilityStatus.COMPLETED
                and not result.result_available
            ):
                raise KernelExecutionError(
                    f"capacidad {name} declaró COMPLETED sin resultado disponible"
                )
            results.append(result)
        except Exception as exc:
            reason = str(exc).strip() or exc.__class__.__name__
            return KernelOutcome(
                status=KernelStatus.FAILED, **identity,
                capability_results=tuple(results),
                failure_reason=f"{name}: {reason}"[:512],
            )

    unresolved = tuple(
        sorted({item for result in results for item in result.unresolved_items})
    )
    failed = next(
        (item for item in results if item.status == KernelCapabilityStatus.FAILED),
        None,
    )
    if failed is not None:
        status = KernelStatus.FAILED
        failure_reason = f"{failed.capability}: {failed.failure_reason}"[:512]
    elif any(
        item.status in {
            KernelCapabilityStatus.READY,
            KernelCapabilityStatus.RUNNING,
            KernelCapabilityStatus.BLOCKED,
            KernelCapabilityStatus.NOT_EVALUABLE,
            KernelCapabilityStatus.PARTIALLY_COMPLETED,
        }
        for item in results
    ):
        status = KernelStatus.PARTIALLY_COMPLETED
        failure_reason = None
    else:
        status = KernelStatus.COMPLETED
        failure_reason = None

    return KernelOutcome(
        status=status, **identity, capability_results=tuple(results),
        unresolved_items=unresolved, failure_reason=failure_reason,
    )


__all__ = [
    "KernelCapabilityResult", "KernelCapabilityStatus", "KernelContext",
    "KernelExecutionError", "KernelInvoker", "KernelOperation", "KernelOutcome",
    "KernelPlan", "KernelStatus", "execute_kernel",
]
