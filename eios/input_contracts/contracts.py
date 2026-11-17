"""F5.6 — Explicit, technical-only input boundary for independent projects.

This optional module describes a domain payload's declared type and schema
identity without knowing its business fields. A project supplies its own
validated Pydantic model and invokers; this module verifies the declared
contract, versions, scope, operation identity and frozen input consistency
BEFORE any capability is invoked by the unchanged neutral kernel.

It does NOT authenticate sources, validate documentary provenance, choose
capabilities, calculate prices/costs, or grant operational decision authority.
"""
from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, InstanceOf

from eios.kernel.execution import (
    KernelCapabilityResult,
    KernelContext,
    KernelInvoker,
    KernelOperation,
    KernelPlan,
)

_RESERVED_CAPABILITIES = frozenset({"QTG", "O1"})
_CONTEXT_FIELDS = tuple(KernelContext.model_fields)


class InputContractError(ValueError):
    """A declared input/registration/runtime boundary does not match."""


@dataclass(frozen=True)
class CapabilityInputSpec:
    """Project-owned explicit registration; NOT a discovery/approval system.

    The payload_type must be the exact Pydantic model class supplied by the
    consuming vertical. It may be a SalesOffer, PurchaseOperation, or any other
    explicitly declared business input. No business schema is imported here.
    """

    project_id: str
    capability: str
    schema_id: str
    schema_version: str
    payload_type: type[BaseModel]

    def __post_init__(self) -> None:
        for name, limit in (
            ("project_id", 128),
            ("capability", 64),
            ("schema_id", 128),
            ("schema_version", 64),
        ):
            value = getattr(self, name)
            if not isinstance(value, str) or not value or value != value.strip() or len(value) > limit:
                raise InputContractError(f"INVALID_INPUT_SPEC:{name}")
        if self.capability in _RESERVED_CAPABILITIES:
            raise InputContractError("FORBIDDEN_BOUNDARY_CAPABILITY")
        if not isinstance(self.payload_type, type) or not issubclass(self.payload_type, BaseModel):
            raise InputContractError("INVALID_PAYLOAD_MODEL")


class CapabilityInputEnvelope(BaseModel):
    """Untrusted declaration carrying a typed payload and full case identity.

    Frozen metadata is a consistency guard, NOT provenance certification.
    The nested business model may be mutable; the binding copies its contents.
    """

    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)

    project_id: str = Field(min_length=1, max_length=128)
    capability: str = Field(min_length=1, max_length=64)
    schema_id: str = Field(min_length=1, max_length=128)
    schema_version: str = Field(min_length=1, max_length=64)
    decision_id: str = Field(min_length=1, max_length=64)
    scenario_id: str = Field(min_length=1, max_length=64)
    rules_version: str = Field(min_length=1, max_length=64)
    parameters_version: str = Field(min_length=1, max_length=64)
    data_snapshot_id: str = Field(min_length=1, max_length=64)
    payload: InstanceOf[BaseModel]
    provenance_status: Literal["UNVERIFIED_ADAPTER_RESPONSIBILITY"] = (
        "UNVERIFIED_ADAPTER_RESPONSIBILITY"
    )


@dataclass(frozen=True)
class CapabilityInputBinding:
    """One explicit invocation mapping registered schema to a domain producer."""

    spec: CapabilityInputSpec
    envelope: CapabilityInputEnvelope
    invoker: KernelInvoker


def _check_payload_identity(payload: BaseModel, context: KernelContext) -> None:
    """Check common identifiers if they exist; never infer missing business IDs."""
    for name in ("decision_id", "scenario_id"):
        if name in type(payload).model_fields:
            if getattr(payload, name) != getattr(context, name):
                raise InputContractError(f"PAYLOAD_CONTEXT_MISMATCH:{name}")


def _check_context(runtime: KernelContext, expected: KernelContext) -> None:
    if type(runtime) is not KernelContext:
        raise InputContractError("INVALID_KERNEL_CONTEXT")
    for name in _CONTEXT_FIELDS:
        if getattr(runtime, name) != getattr(expected, name):
            raise InputContractError(f"CONTEXT_DRIFT:{name}")


def _bound_invoker(
    expected_payload: BaseModel,
    expected_context: KernelContext,
    payload_type: type[BaseModel],
    producer: KernelInvoker,
) -> KernelInvoker:
    frozen_payload = expected_payload.model_copy(deep=True)
    frozen_context = expected_context.model_copy(deep=True)

    def invoke(runtime_payload: BaseModel, runtime_context: KernelContext) -> KernelCapabilityResult:
        _check_context(runtime_context, frozen_context)
        if type(runtime_payload) is not payload_type or runtime_payload != frozen_payload:
            raise InputContractError("INPUT_PAYLOAD_DRIFT")
        _check_payload_identity(runtime_payload, runtime_context)
        # The original kernel also deep-copies; this boundary independently
        # protects the registered input against a mutating consumer producer.
        return producer(
            runtime_payload.model_copy(deep=True),
            runtime_context.model_copy(deep=True),
        )

    return invoke


def bind_capability_inputs(
    *,
    operation: KernelOperation,
    context: KernelContext,
    plan: KernelPlan,
    bindings: Mapping[str, CapabilityInputBinding],
) -> Mapping[str, KernelInvoker]:
    """Validate *all* selected capability inputs upfront, then bind to kernel.

    Every envelope declares a project, full context, capability name, schema
    identity/version and exact Pydantic payload class. All must match the
    caller-supplied operation. No partial binding or default invoker exists.

    Returns immutable capability-to-invoker mapping for execute_kernel(...).
    Does not itself execute the kernel or confer documentary/decision authority.
    """
    if type(operation) is not KernelOperation:
        raise InputContractError("INVALID_KERNEL_OPERATION")
    if type(context) is not KernelContext:
        raise InputContractError("INVALID_KERNEL_CONTEXT")
    if type(plan) is not KernelPlan:
        raise InputContractError("INVALID_KERNEL_PLAN")
    if not isinstance(bindings, Mapping):
        raise InputContractError("INVALID_INPUT_BINDINGS")
    if operation.decision_id != context.decision_id:
        raise InputContractError("OPERATION_CONTEXT_MISMATCH:decision_id")
    if operation.scenario_id != context.scenario_id:
        raise InputContractError("OPERATION_CONTEXT_MISMATCH:scenario_id")
    if any(name in _RESERVED_CAPABILITIES for name in plan.capabilities):
        raise InputContractError("FORBIDDEN_BOUNDARY_CAPABILITY")
    if set(bindings) != set(plan.capabilities):
        raise InputContractError("CAPABILITY_BINDING_SET_MISMATCH")

    registered: dict[str, KernelInvoker] = {}
    for name in plan.capabilities:
        entry = bindings[name]
        if type(entry) is not CapabilityInputBinding:
            raise InputContractError(f"INVALID_CAPABILITY_BINDING:{name}")
        spec, envelope = entry.spec, entry.envelope
        if type(spec) is not CapabilityInputSpec or type(envelope) is not CapabilityInputEnvelope:
            raise InputContractError(f"INVALID_INPUT_CONTRACT:{name}")
        if not callable(entry.invoker):
            raise InputContractError(f"INVALID_CAPABILITY_INVOKER:{name}")
        for attr in ("project_id", "capability", "schema_id", "schema_version"):
            if getattr(spec, attr) != getattr(envelope, attr):
                raise InputContractError(f"SPEC_ENVELOPE_MISMATCH:{name}:{attr}")
        if spec.capability != name:
            raise InputContractError(f"CAPABILITY_ID_MISMATCH:{name}")
        if envelope.project_id != context.project_id:
            raise InputContractError(f"PROJECT_SCOPE_MISMATCH:{name}")
        for attr in _CONTEXT_FIELDS:
            if getattr(envelope, attr) != getattr(context, attr):
                raise InputContractError(f"ENVELOPE_CONTEXT_MISMATCH:{name}:{attr}")
        if type(envelope.payload) is not spec.payload_type:
            raise InputContractError(f"INPUT_SCHEMA_TYPE_MISMATCH:{name}")
        if type(operation.payload) is not spec.payload_type or operation.payload != envelope.payload:
            raise InputContractError(f"OPERATION_PAYLOAD_MISMATCH:{name}")
        _check_payload_identity(envelope.payload, context)
        registered[name] = _bound_invoker(
            envelope.payload, context, spec.payload_type, entry.invoker
        )
    return MappingProxyType(registered)


__all__ = [
    "CapabilityInputBinding",
    "CapabilityInputEnvelope",
    "CapabilityInputSpec",
    "InputContractError",
    "bind_capability_inputs",
]
