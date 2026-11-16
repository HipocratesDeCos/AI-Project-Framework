"""Read-only company-scoped parameter lookup over the existing EIOS Centre.

A documented, context-bound resolution is *not* a rule assessment, a verified
parameter-version history, or proof of external origin. The Centre retains
ownership of configurations and temporal resolution.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime
from typing import Literal, Mapping

from eios.core.models import DecisionContext, Evidence
from eios.core.validation import validate_evidence

from .center import Configuration, ParameterConfigurationCenter, ParameterConfigurationError
from .resolution import ResolvedConfiguration, resolve_configuration_for_context


EvidenceStatus = Literal[
    "DOCUMENTARY_CHECK_PASSED", "CONFIGURATION_ABSENT",
    "EVIDENCE_MISSING", "EVIDENCE_INVALID",
]
EVIDENCE_SOURCE_TYPE = "ParameterConfigurationEvidence"


class ParameterLookupError(ValueError):
    """Stable, non-operational error for a malformed or foreign query."""

    def __init__(self, code: str, message: str):
        self.code = code
        super().__init__(message)


@dataclass(frozen=True, slots=True)
class ParameterLookupEntry:
    parameter_id: str
    status: EvidenceStatus
    resolution: ResolvedConfiguration | None
    evidence: Evidence | None
    reason: str

    @property
    def ready_for_consumer_checks(self) -> bool:
        return self.status == "DOCUMENTARY_CHECK_PASSED"


@dataclass(frozen=True, slots=True)
class CompanyParameterLookup:
    company_id: str
    decision_id: str
    scenario_id: str
    data_snapshot_id: str
    parameters_version: str
    effective_at: datetime
    entries: tuple[ParameterLookupEntry, ...]
    version_attestation: Literal["CALLER_CONTEXT_ONLY"] = "CALLER_CONTEXT_ONLY"
    origin_attestation: Literal["NOT_EXTERNALLY_AUTHENTICATED"] = (
        "NOT_EXTERNALLY_AUTHENTICATED"
    )
    decision_authority: Literal[False] = False
    operational_path: Literal["FORBIDDEN"] = "FORBIDDEN"

    @property
    def complete_documentary_coverage(self) -> bool:
        return bool(self.entries) and all(
            entry.ready_for_consumer_checks for entry in self.entries
        )


def configuration_evidence_source_ref(
    *, company_id: str, parameter_id: str, configuration_id: int,
) -> str:
    """New API's *local binding format*, not a signature of external origin."""
    for field, value in (("company", company_id), ("parameter", parameter_id)):
        if not isinstance(value, str) or not value or value != value.strip():
            raise ParameterLookupError("INVALID_SCOPE", field + " is not canonical")
    if type(configuration_id) is not int or configuration_id < 0:
        raise ParameterLookupError("INVALID_CONFIGURATION", "Invalid configuration_id")
    return f"company_parameter:{company_id}:{parameter_id}:{configuration_id}"


def _scope(value: str, field: str) -> None:
    if not isinstance(value, str) or not value or value != value.strip():
        raise ParameterLookupError("INVALID_SCOPE", field + " is not canonical")


def _snapshot_configuration(
    value: Configuration, *, company_id: str, parameter_id: str,
) -> Configuration:
    if not isinstance(value, Configuration):
        raise ParameterLookupError("INVALID_CONFIGURATION", "Centre returned an untyped configuration")
    config = deepcopy(value)
    if config.company_id != company_id or config.parameter_id != parameter_id:
        raise ParameterLookupError("CONFIGURATION_SCOPE_MISMATCH", "Centre returned a foreign configuration")
    if type(config.configuration_id) is not int or config.configuration_id < 0:
        raise ParameterLookupError("INVALID_CONFIGURATION", "Invalid configuration id")
    if not isinstance(config.value, str):
        raise ParameterLookupError("INVALID_CONFIGURATION", "Configuration value must be a string")
    if not all(isinstance(getattr(config, name), datetime) for name in (
        "valid_from", "created_at", "updated_at",
    )):
        raise ParameterLookupError("INVALID_CONFIGURATION", "Configuration timestamps are invalid")
    if config.valid_to is not None and not isinstance(config.valid_to, datetime):
        raise ParameterLookupError("INVALID_CONFIGURATION", "Configuration end timestamp is invalid")
    if (
        config.valid_from.utcoffset() is None
        or config.created_at.utcoffset() is None
        or config.updated_at.utcoffset() is None
        or (
            config.valid_to is not None and config.valid_to.utcoffset() is None
        )
    ):
        raise ParameterLookupError("INVALID_VALIDITY", "Configuration timestamps must have offsets")
    return config


def _evidence_matches(
    evidence: Evidence,
    resolved: ResolvedConfiguration,
    company_id: str,
) -> bool:
    if not isinstance(evidence, Evidence):
        return False
    expected_ref = configuration_evidence_source_ref(
        company_id=company_id,
        parameter_id=resolved.parameter_id,
        configuration_id=resolved.configuration.configuration_id,
    )
    return (
        evidence.source_type == EVIDENCE_SOURCE_TYPE
        and evidence.source_ref == expected_ref
        and evidence.captured_at == resolved.effective_at.date()
        and evidence.state == "DEMONSTRATED"
        and evidence.demonstration_ref == resolved.configuration_ref
        and validate_evidence(evidence).status == "VALID"
    )


def read_company_parameters_for_context(
    *,
    center: ParameterConfigurationCenter,
    company_id: str,
    expected_company_id: str,
    context: DecisionContext,
    effective_at: datetime,
    parameter_ids: tuple[str, ...],
    evidence_by_parameter: Mapping[str, Evidence],
) -> CompanyParameterLookup:
    """Inspect canonical configurations, requiring bound documentary evidence.

    expected_company_id MUST originate with an authenticated application
    adapter, not the editable payload. A valid evidence object still cannot
    authenticate its own source or prove a historical parameters_version.
    Rules must independently revalidate every returned resolution/evidence.
    """
    if not isinstance(center, ParameterConfigurationCenter):
        raise TypeError("center must be ParameterConfigurationCenter")
    if not isinstance(context, DecisionContext):
        raise TypeError("context must be DecisionContext")
    _scope(company_id, "company_id")
    _scope(expected_company_id, "expected_company_id")
    if company_id != expected_company_id:
        raise ParameterLookupError("COMPANY_SCOPE_MISMATCH", "Company differs from trusted caller")
    if not isinstance(effective_at, datetime) or effective_at.utcoffset() is None:
        raise ParameterLookupError("INVALID_EFFECTIVE_AT", "effective_at needs a timezone offset")
    if not isinstance(parameter_ids, tuple) or not parameter_ids:
        raise ParameterLookupError("INVALID_SELECTION", "Select at least one parameter in a tuple")
    for pid in parameter_ids:
        _scope(pid, "parameter_id")
    if len(set(parameter_ids)) != len(parameter_ids):
        raise ParameterLookupError("DUPLICATE_PARAMETER", "Duplicate parameter IDs")
    if not isinstance(evidence_by_parameter, Mapping):
        raise TypeError("evidence_by_parameter must be a mapping")
    if set(evidence_by_parameter) - set(parameter_ids):
        raise ParameterLookupError("EXTRANEOUS_EVIDENCE", "Evidence contains unrequested parameters")

    source_evidence_ids: list[str] = []
    for supplied in evidence_by_parameter.values():
        if not isinstance(supplied, Evidence):
            raise TypeError("evidence_by_parameter must contain Evidence")
        source_evidence_ids.append(supplied.evidence_id)
    if len(source_evidence_ids) != len(set(source_evidence_ids)):
        raise ParameterLookupError("EVIDENCE_REUSED", "One evidence_id cannot support multiple parameters")

    # Capture a single version/context and evidence view before Centre reads.
    # No late caller mutations can silently relabel the same configuration.
    context_snapshot = DecisionContext.model_validate(context.model_dump(mode="python"))
    evidence_snapshot = {
        pid: item.model_copy(deep=True)
        for pid, item in evidence_by_parameter.items()
    }

    entries: list[ParameterLookupEntry] = []
    configuration_ids: set[int] = set()
    for pid in parameter_ids:
        definition = center.get_parameter(pid)
        if definition.parameter_id != pid:
            raise ParameterLookupError("CATALOGUE_MISMATCH", "Catalogue returned the wrong parameter")
        config_raw = center.get_configuration_at(company_id, pid, effective_at)
        if config_raw is None:
            entries.append(ParameterLookupEntry(pid, "CONFIGURATION_ABSENT", None, None, "No effective configuration"))
            continue
        config = _snapshot_configuration(config_raw, company_id=company_id, parameter_id=pid)
        if config.configuration_id in configuration_ids:
            raise ParameterLookupError("CONFIGURATION_REUSED", "One configuration_id maps to multiple parameters")
        configuration_ids.add(config.configuration_id)
        if definition.unit is not None and config.unit != definition.unit:
            raise ParameterLookupError("CONFIGURATION_UNIT_MISMATCH", "Configuration unit differs from catalogue")
        if definition.value_type is not None and config.value_type != definition.value_type:
            raise ParameterLookupError("CONFIGURATION_TYPE_MISMATCH", "Configuration type differs from catalogue")
        if definition.validate_value is not None and definition.validate_value(config.value) is not None:
            raise ParameterLookupError("CONFIGURATION_VALUE_INVALID", "Configuration violates catalogue validation")
        resolved = resolve_configuration_for_context(config, context_snapshot, effective_at)
        if not isinstance(resolved, ResolvedConfiguration):
            raise ParameterLookupError("INVALID_CONFIGURATION", "Resolution unexpectedly absent")

        original_evidence = evidence_snapshot.get(pid)
        if original_evidence is None:
            entries.append(ParameterLookupEntry(pid, "EVIDENCE_MISSING", None, None, "No documentary evidence"))
        else:
            proof = original_evidence.model_copy(deep=True)
            if _evidence_matches(proof, resolved, company_id):
                entries.append(ParameterLookupEntry(pid, "DOCUMENTARY_CHECK_PASSED", resolved, proof, "Rule checks still required"))
            else:
                entries.append(ParameterLookupEntry(pid, "EVIDENCE_INVALID", None, None, "Evidence does not bind to this configuration"))
    return CompanyParameterLookup(
        company_id=company_id,
        decision_id=context_snapshot.decision_id,
        scenario_id=context_snapshot.scenario_id,
        data_snapshot_id=context_snapshot.data_snapshot_id,
        parameters_version=context_snapshot.parameters_version,
        effective_at=effective_at,
        entries=tuple(entries),
    )


__all__ = [
    "EVIDENCE_SOURCE_TYPE", "ParameterLookupError",
    "ParameterLookupEntry", "CompanyParameterLookup",
    "configuration_evidence_source_ref", "read_company_parameters_for_context",
]
