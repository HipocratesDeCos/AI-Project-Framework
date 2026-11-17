"""F5.7 — Explicit project capability release catalog, no automatic discovery.

A release is permitted only by an explicitly provided immutable project
catalog. Compatibility means *exact* selected release version and explicitly
allowed input schema versions; SemVer numbering never implies compatibility.

Only the existing F5.6 input binder may produce invokers for the unchanged
F4 technical kernel. This module authenticates neither software nor data,
registers no default capabilities and grants no operational authority.
"""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
import re
from types import MappingProxyType

from pydantic import BaseModel

from eios.input_contracts import (
    CapabilityInputBinding, CapabilityInputSpec, InputContractError, bind_capability_inputs,
)
from eios.kernel.execution import (
    KernelContext, KernelInvoker, KernelOperation, KernelPlan,
)

# Physical wheel metadata pins these versions independently; constants express
# exactly which public APIs this catalog implementation has been tested against.
KERNEL_API_VERSION = "0.1.0"
INPUT_CONTRACT_API_VERSION = "0.1.0"
_RESERVED = frozenset({"O1", "QTG"})
_SEMVER = re.compile(r"(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\Z")


class CapabilityCatalogError(InputContractError):
    """A capability was undeclared, disabled, or incompatible with the plan."""


def _identifier(value: str, field: str, limit: int = 128) -> None:
    if (
        type(value) is not str or not value or value != value.strip()
        or len(value) > limit
    ):
        raise CapabilityCatalogError(f"INVALID_CATALOG_IDENTIFIER:{field}")


def _version(value: str, field: str) -> None:
    _identifier(value, field, 64)
    if not _SEMVER.fullmatch(value):
        raise CapabilityCatalogError(f"INVALID_CATALOG_VERSION:{field}")


@dataclass(frozen=True)
class CapabilityRelease:
    """Exactly one release explicitly permitted for a single project.

    The payload_type is a Pydantic class supplied by the consuming project.
    Any number of schema versions may be compatible only if listed literally.
    """

    project_id: str
    capability: str
    release_version: str
    schema_id: str
    compatible_schema_versions: tuple[str, ...]
    payload_type: type[BaseModel]
    policy_version: str
    required_kernel_api: str = KERNEL_API_VERSION
    required_input_contract_api: str = INPUT_CONTRACT_API_VERSION
    enabled: bool = True

    def __post_init__(self) -> None:
        _identifier(self.project_id, "project_id")
        _identifier(self.capability, "capability", 64)
        _identifier(self.schema_id, "schema_id")
        _identifier(self.policy_version, "policy_version", 64)
        _version(self.release_version, "release_version")
        _version(self.required_kernel_api, "required_kernel_api")
        _version(self.required_input_contract_api, "required_input_contract_api")
        if self.capability in _RESERVED:
            raise CapabilityCatalogError("FORBIDDEN_BOUNDARY_CAPABILITY")
        if type(self.compatible_schema_versions) is not tuple or not self.compatible_schema_versions:
            raise CapabilityCatalogError("INVALID_COMPATIBLE_SCHEMA_VERSIONS")
        for schema_version in self.compatible_schema_versions:
            _identifier(schema_version, "schema_version", 64)
        if len(self.compatible_schema_versions) != len(set(self.compatible_schema_versions)):
            raise CapabilityCatalogError("DUPLICATE_COMPATIBLE_SCHEMA_VERSION")
        if not isinstance(self.payload_type, type) or not issubclass(self.payload_type, BaseModel):
            raise CapabilityCatalogError("INVALID_CATALOG_PAYLOAD_TYPE")
        if type(self.enabled) is not bool:
            raise CapabilityCatalogError("INVALID_CATALOG_ENABLED_FLAG")


@dataclass(frozen=True)
class CapabilityCatalog:
    """Immutable snapshot; separate catalogs may represent staged migrations."""

    project_id: str
    catalog_version: str
    releases: tuple[CapabilityRelease, ...]

    def __post_init__(self) -> None:
        _identifier(self.project_id, "catalog_project_id")
        _version(self.catalog_version, "catalog_version")
        if type(self.releases) is not tuple or not self.releases:
            raise CapabilityCatalogError("EMPTY_OR_MUTABLE_CAPABILITY_CATALOG")
        seen: set[tuple[str, str]] = set()
        for item in self.releases:
            if type(item) is not CapabilityRelease:
                raise CapabilityCatalogError("INVALID_CATALOG_ENTRY")
            if item.project_id != self.project_id:
                raise CapabilityCatalogError("FOREIGN_PROJECT_IN_CATALOG")
            key = (item.capability, item.release_version)
            if key in seen:
                raise CapabilityCatalogError("DUPLICATE_CAPABILITY_RELEASE")
            seen.add(key)


def bind_catalog_plan(
    *,
    catalog: CapabilityCatalog,
    requested_releases: Mapping[str, str],
    operation: KernelOperation,
    context: KernelContext,
    plan: KernelPlan,
    bindings: Mapping[str, CapabilityInputBinding],
) -> Mapping[str, KernelInvoker]:
    """Resolve exact releases and schema compatibility BEFORE any execution.

    Returns only the immutable mapping from the F5.6 binder. No fallback to
    a latest release, no automatic SemVer ranges, no environment discovery.
    """
    if type(catalog) is not CapabilityCatalog:
        raise CapabilityCatalogError("INVALID_CATALOG")
    if type(context) is not KernelContext or type(plan) is not KernelPlan:
        raise CapabilityCatalogError("INVALID_CATALOG_CONTEXT_OR_PLAN")
    if not isinstance(requested_releases, Mapping) or not isinstance(bindings, Mapping):
        raise CapabilityCatalogError("INVALID_CATALOG_REQUEST")
    if context.project_id != catalog.project_id:
        raise CapabilityCatalogError("CATALOG_PROJECT_MISMATCH")
    if any(item in _RESERVED for item in plan.capabilities):
        raise CapabilityCatalogError("FORBIDDEN_BOUNDARY_CAPABILITY")
    selected = set(plan.capabilities)
    if set(requested_releases) != selected:
        raise CapabilityCatalogError("RELEASE_SELECTION_SET_MISMATCH")
    if set(bindings) != selected:
        raise CapabilityCatalogError("CATALOG_BINDINGS_SET_MISMATCH")

    available = {
        (item.capability, item.release_version): item for item in catalog.releases
    }
    for name in plan.capabilities:
        requested_version = requested_releases[name]
        _version(requested_version, "requested_release_version")
        release = available.get((name, requested_version))
        if release is None:
            raise CapabilityCatalogError(f"RELEASE_NOT_REGISTERED:{name}")
        if not release.enabled:
            raise CapabilityCatalogError(f"RELEASE_DISABLED:{name}")
        if release.required_kernel_api != KERNEL_API_VERSION:
            raise CapabilityCatalogError(f"KERNEL_API_INCOMPATIBLE:{name}")
        if release.required_input_contract_api != INPUT_CONTRACT_API_VERSION:
            raise CapabilityCatalogError(f"INPUT_API_INCOMPATIBLE:{name}")
        if release.policy_version != plan.policy_version:
            raise CapabilityCatalogError(f"POLICY_VERSION_INCOMPATIBLE:{name}")
        binding = bindings[name]
        if type(binding) is not CapabilityInputBinding:
            raise CapabilityCatalogError(f"INVALID_CATALOG_BINDING:{name}")
        spec = binding.spec
        if type(spec) is not CapabilityInputSpec:
            raise CapabilityCatalogError(f"INVALID_CAPABILITY_SPEC:{name}")
        if (
            spec.project_id != catalog.project_id or spec.capability != name
            or spec.schema_id != release.schema_id
            or spec.payload_type is not release.payload_type
        ):
            raise CapabilityCatalogError(f"RELEASE_SCHEMA_INCOMPATIBLE:{name}")
        if spec.schema_version not in release.compatible_schema_versions:
            raise CapabilityCatalogError(f"SCHEMA_VERSION_INCOMPATIBLE:{name}")

    # The existing binder independently checks all envelope/context details,
    # exact payload model, case identity, producer, QTG/O1 and runtime drift.
    return bind_capability_inputs(
        operation=operation, context=context, plan=plan, bindings=bindings,
    )


__all__ = [
    "CapabilityCatalog", "CapabilityCatalogError", "CapabilityRelease",
    "INPUT_CONTRACT_API_VERSION", "KERNEL_API_VERSION", "bind_catalog_plan",
]
