"""F6.2: independent, synthetic-only company adapter over existing EIOS APIs.

A company/project integrator owns this code, its source-specific mapping and
its real-world authentication. Hashes here prove equality of supplied bytes,
not provenance or document authenticity. This sample accepts no real operation.
It NEVER supplies grants or changes the canonical EIOS kernel.
"""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
import hashlib
import json
import re
from types import MappingProxyType

from pydantic import BaseModel, ConfigDict, Field

from eios.kernel.execution import (
    KernelCapabilityResult, KernelContext, KernelOperation, KernelPlan,
)
from eios.input_contracts import (
    CapabilityInputBinding, CapabilityInputEnvelope, CapabilityInputSpec,
)
from eios.capability_catalog import CapabilityCatalog, CapabilityRelease


MAX_JSON_BYTES = 32_768
SCHEMA_ID = "synthetic.equipment_company_record"
SCHEMA_VERSION = "v1"
POLICY_VERSION = "EXTERNAL_SYNTHETIC_POLICY_1"
CAPABILITIES = ("SERVICE_HOURS_CHECK", "INSPECTION_REFERENCE_CHECK")
_SHA256 = re.compile(r"[0-9a-f]{64}\Z")


class AdapterError(ValueError):
    """An external record failed preflight before any EIOS invocation."""


class ExternalSourceScope(BaseModel):
    """Caller-controlled SYNTHETIC scope, never read from the untrusted row.

    The digest is a consistency anchor only. A real integration MUST obtain
    authority and documentary provenance through separately verified systems.
    """

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    project_id: str = Field(min_length=1, max_length=128)
    company_id: str = Field(min_length=1, max_length=128)
    source_id: str = Field(min_length=1, max_length=128)
    expected_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    data_snapshot_id: str = Field(min_length=1, max_length=64)
    rules_version: str = Field(min_length=1, max_length=64)
    parameters_version: str = Field(min_length=1, max_length=64)
    schema_version: str = Field(pattern=r"^v1$")
    purpose: str = Field(pattern=r"^SYNTHETIC_TEST_ONLY$")


class SyntheticEquipmentRecord(BaseModel):
    """Strict, business-specific sample schema owned outside EIOS."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    project_id: str = Field(min_length=1, max_length=128)
    company_id: str = Field(min_length=1, max_length=128)
    source_id: str = Field(min_length=1, max_length=128)
    data_snapshot_id: str = Field(min_length=1, max_length=64)
    schema_version: str = Field(pattern=r"^v1$")
    evidence_class: str = Field(pattern=r"^SYNTHETIC_TEST$")
    documentary_status: str = Field(pattern=r"^UNVERIFIED$")
    decision_id: str = Field(min_length=1, max_length=64)
    scenario_id: str = Field(min_length=1, max_length=64)
    facility_id: str = Field(min_length=1, max_length=128)
    equipment_id: str = Field(min_length=1, max_length=128)
    hours_since_service: int = Field(ge=0)
    service_interval_hours: int = Field(gt=0)
    inspection_reference: str | None = Field(default=None, max_length=128)


@dataclass(frozen=True)
class PreparedExternalCase:
    """Technical preflight output; NOT a document or operational admission."""

    company_id: str
    source_id: str
    raw_sha256: str
    context: KernelContext
    operation: KernelOperation
    plan: KernelPlan
    catalog: CapabilityCatalog
    bindings: Mapping[str, CapabilityInputBinding]
    provenance_status: str = "UNVERIFIED_ADAPTER_RESPONSIBILITY"
    production_authorized: bool = False
    operational_path: str = "FORBIDDEN"


def _unique_keys(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise AdapterError("DUPLICATE_SOURCE_KEY:" + key)
        result[key] = value
    return result


def _invalid_constant(name: str) -> None:
    raise AdapterError("NONFINITE_SOURCE_NUMBER:" + name)


def prepare_external_case(
    *,
    scope: ExternalSourceScope,
    source_bytes: bytes,
    producers: Mapping[str, object],
) -> PreparedExternalCase:
    """Fail closed on integrity, tenant, data version and provenance claims.

    Selection/version governance remains with the existing F5.7/F5.8 APIs.
    No producer is called by this method; it only prepares explicit bindings.
    """
    if type(scope) is not ExternalSourceScope:
        raise AdapterError("INVALID_EXTERNAL_SCOPE")
    if type(source_bytes) is not bytes or not (0 < len(source_bytes) <= MAX_JSON_BYTES):
        raise AdapterError("INVALID_SOURCE_BYTES_OR_SIZE")
    if not isinstance(producers, Mapping) or set(producers) != set(CAPABILITIES):
        raise AdapterError("EXTERNAL_CAPABILITY_SET_MISMATCH")
    if any(not callable(producers[name]) for name in CAPABILITIES):
        raise AdapterError("NONCALLABLE_EXTERNAL_PRODUCER")
    digest = hashlib.sha256(source_bytes).hexdigest()
    if not _SHA256.fullmatch(scope.expected_sha256) or digest != scope.expected_sha256:
        raise AdapterError("SOURCE_HASH_MISMATCH")
    try:
        raw = json.loads(
            source_bytes.decode("utf-8"), object_pairs_hook=_unique_keys,
            parse_constant=_invalid_constant,
        )
    except (UnicodeError, ValueError) as exc:
        raise AdapterError("INVALID_EXTERNAL_JSON") from exc
    if type(raw) is not dict:
        raise AdapterError("SOURCE_MUST_BE_JSON_OBJECT")
    try:
        record = SyntheticEquipmentRecord.model_validate(raw)
    except ValueError as exc:
        raise AdapterError("EXTERNAL_RECORD_SCHEMA_REJECTED") from exc
    for field in (
        "project_id", "company_id", "source_id", "data_snapshot_id",
        "schema_version",
    ):
        if getattr(record, field) != getattr(scope, field):
            raise AdapterError("EXTERNAL_SCOPE_MISMATCH:" + field)
    if record.evidence_class != "SYNTHETIC_TEST" or record.documentary_status != "UNVERIFIED":
        raise AdapterError("OPERATIONAL_SOURCE_CLAIM_FORBIDDEN")

    context = KernelContext(
        project_id=scope.project_id,
        decision_id=record.decision_id,
        scenario_id=record.scenario_id,
        rules_version=scope.rules_version,
        parameters_version=scope.parameters_version,
        data_snapshot_id=scope.data_snapshot_id,
    )
    operation = KernelOperation(
        decision_id=context.decision_id,
        scenario_id=context.scenario_id,
        payload=record,
    )
    plan = KernelPlan(capabilities=CAPABILITIES, policy_version=POLICY_VERSION)
    catalog = CapabilityCatalog(
        project_id=scope.project_id, catalog_version="1.0.0",
        releases=tuple(
            CapabilityRelease(
                project_id=scope.project_id, capability=name,
                release_version="1.0.0", schema_id=SCHEMA_ID,
                compatible_schema_versions=(SCHEMA_VERSION,),
                payload_type=SyntheticEquipmentRecord,
                policy_version=POLICY_VERSION,
            )
            for name in CAPABILITIES
        ),
    )
    bindings = MappingProxyType({
        name: CapabilityInputBinding(
            spec=CapabilityInputSpec(
                project_id=scope.project_id, capability=name,
                schema_id=SCHEMA_ID, schema_version=SCHEMA_VERSION,
                payload_type=SyntheticEquipmentRecord,
            ),
            envelope=CapabilityInputEnvelope(
                **{key: getattr(context, key) for key in KernelContext.model_fields},
                capability=name, schema_id=SCHEMA_ID,
                schema_version=SCHEMA_VERSION, payload=record,
            ),
            invoker=producers[name],
        )
        for name in CAPABILITIES
    })
    return PreparedExternalCase(
        company_id=scope.company_id,
        source_id=scope.source_id,
        raw_sha256=digest,
        context=context, operation=operation,
        plan=plan, catalog=catalog, bindings=bindings,
    )


__all__ = [
    "AdapterError", "CAPABILITIES", "ExternalSourceScope", "PreparedExternalCase",
    "SyntheticEquipmentRecord", "prepare_external_case",
]
