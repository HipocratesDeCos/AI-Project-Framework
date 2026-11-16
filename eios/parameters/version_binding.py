"""Phase 2.4: bind a full company parameter selection to its version source.

This is a read-only *correspondence check*, not a new version catalogue,
transaction manager, external authentication mechanism, or rule authority.
The trusted adapter must supply the authoritative manifest source.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from hashlib import sha256
from hmac import compare_digest
import json
from typing import Literal, Mapping, Protocol

from eios.core.models import DecisionContext, Evidence

from .center import Configuration, ParameterConfigurationCenter
from .company_resolution_api import (
    CompanyParameterLookup,
    ParameterLookupError,
    read_company_parameters_for_context,
)


SELECTION_SCHEMA = "EIOS-PARAMETER-SELECTION-CONTENT/v0.1"


class ParameterVersionBindingError(ValueError):
    """Stable, fail-closed contract error for incomplete/foreign version material."""

    def __init__(self, code: str, message: str) -> None:
        self.code = code
        super().__init__(message)


@dataclass(frozen=True, slots=True)
class ParameterVersionManifest:
    """Reference returned by a version authority port, not self-authentication.

    The existing DecisionContext.parameters_version is authoritative *only
    relative to the configured source*. No new version ID is generated.
    """

    company_id: str
    parameters_version: str
    effective_at: datetime
    parameter_ids: tuple[str, ...]
    selection_fingerprint: str
    source_ref: str


class ParameterVersionSource(Protocol):
    """Read-only port: the adapter resolves the EXISTING version authority."""

    def get_version_manifest(
        self, company_id: str, parameters_version: str, effective_at: datetime,
    ) -> ParameterVersionManifest | None: ...


@dataclass(frozen=True, slots=True)
class VersionBoundParameterSelection:
    """A matched version/reference, with rule and external trust still withheld."""

    lookup: CompanyParameterLookup
    manifest: ParameterVersionManifest
    selection_fingerprint: str
    status: Literal["SOURCE_MANIFEST_MATCHED"] = "SOURCE_MANIFEST_MATCHED"
    version_attestation: Literal["MATCHED_SUPPLIED_VERSION_SOURCE"] = (
        "MATCHED_SUPPLIED_VERSION_SOURCE"
    )
    source_authentication: Literal["ADAPTER_RESPONSIBILITY"] = (
        "ADAPTER_RESPONSIBILITY"
    )
    atomicity: Literal["MANIFEST_CONSISTENCY_NOT_DB_TRANSACTION"] = (
        "MANIFEST_CONSISTENCY_NOT_DB_TRANSACTION"
    )
    decision_authority: Literal[False] = False
    operational_path: Literal["FORBIDDEN"] = "FORBIDDEN"


def _timestamp(value: datetime) -> str:
    if not isinstance(value, datetime) or value.utcoffset() is None:
        raise ParameterVersionBindingError(
            "INVALID_EFFECTIVE_AT", "Time values require explicit timezone",
        )
    return value.astimezone(timezone.utc).isoformat()


def _identifier(value: str, label: str) -> None:
    if not isinstance(value, str) or not value or value != value.strip():
        raise ParameterVersionBindingError(
            "INVALID_IDENTITY", label + " must be a canonical nonempty string",
        )


def _manifest_check(
    raw: object, *, company_id: str, context: DecisionContext,
    effective_at: datetime, parameter_ids: tuple[str, ...],
) -> ParameterVersionManifest:
    if raw is None:
        raise ParameterVersionBindingError(
            "VERSION_SOURCE_UNAVAILABLE", "No source manifest for the selected version",
        )
    if not isinstance(raw, ParameterVersionManifest):
        raise ParameterVersionBindingError(
            "INVALID_VERSION_MANIFEST", "Source returned an untyped version manifest",
        )
    manifest = deepcopy(raw)
    if manifest.company_id != company_id:
        raise ParameterVersionBindingError(
            "MANIFEST_COMPANY_MISMATCH", "Version manifest belongs to another company",
        )
    if manifest.parameters_version != context.parameters_version:
        raise ParameterVersionBindingError(
            "MANIFEST_VERSION_MISMATCH", "Manifest does not match DecisionContext",
        )
    if _timestamp(manifest.effective_at) != _timestamp(effective_at):
        raise ParameterVersionBindingError(
            "MANIFEST_CUTOFF_MISMATCH", "Manifest belongs to another instant",
        )
    if (
        not isinstance(manifest.parameter_ids, tuple)
        or not manifest.parameter_ids
        or any(not isinstance(pid, str) or not pid or pid != pid.strip()
               for pid in manifest.parameter_ids)
        or len(manifest.parameter_ids) != len(set(manifest.parameter_ids))
    ):
        raise ParameterVersionBindingError(
            "INVALID_VERSION_MANIFEST", "Manifest parameter selection is invalid",
        )
    if set(manifest.parameter_ids) != set(parameter_ids):
        raise ParameterVersionBindingError(
            "MANIFEST_SELECTION_MISMATCH",
            "The selected parameter set differs from the authoritative manifest",
        )
    if (
        not isinstance(manifest.selection_fingerprint, str)
        or len(manifest.selection_fingerprint) != 64
        or any(ch not in "0123456789abcdef" for ch in manifest.selection_fingerprint)
    ):
        raise ParameterVersionBindingError(
            "INVALID_VERSION_MANIFEST", "Manifest fingerprint must be canonical sha256",
        )
    _identifier(manifest.source_ref, "source_ref")
    return manifest


def _fingerprint_configuration_records(
    *, company_id: str, parameters_version: str, effective_at: datetime,
    records: list[dict],
) -> str:
    """One canonical content checksum used by live and saved configurations.

    The digest is only a correspondence checksum, NOT an authenticated
    parameters_version or a signature of its source.
    """
    _identifier(company_id, "company_id")
    _identifier(parameters_version, "parameters_version")
    effective = _timestamp(effective_at)
    if not records or any(not isinstance(r, dict) for r in records):
        raise ParameterVersionBindingError(
            "INVALID_SELECTION", "Canonical records are required",
        )
    ordered = sorted(records, key=lambda r: r["parameter_id"])
    if len({r["parameter_id"] for r in ordered}) != len(ordered):
        raise ParameterVersionBindingError(
            "DUPLICATE_PARAMETER", "Duplicate configuration in selection",
        )
    payload = {
        "schema": SELECTION_SCHEMA,
        "company_id": company_id,
        "parameters_version": parameters_version,
        "effective_at": effective,
        "parameter_ids": [r["parameter_id"] for r in ordered],
        "configurations": ordered,
    }
    return sha256(json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")).hexdigest()


def fingerprint_historical_parameter_configurations(
    *, company_id: str, parameters_version: str, effective_at: datetime,
    configurations: tuple[Configuration, ...],
) -> str:
    """Checksum of an *already saved* configuration selection.

    This function has no Centre or evidence inputs. A version-source adapter
    must read these configurations from its original historical record,
    never from the Centre whose live selection is being checked.
    """
    _identifier(company_id, "company_id")
    _identifier(parameters_version, "parameters_version")
    _timestamp(effective_at)
    if not isinstance(configurations, tuple) or not configurations:
        raise ParameterVersionBindingError(
            "INVALID_SELECTION", "An explicit historical selection is required",
        )
    records: list[dict] = []
    for item in configurations:
        if not isinstance(item, Configuration):
            raise ParameterVersionBindingError(
                "INVALID_VERSION_CONFIGURATION", "Historical record is not Configuration",
            )
        if (
            item.company_id != company_id
            or type(item.configuration_id) is not int or item.configuration_id < 0
            or not isinstance(item.parameter_id, str) or not item.parameter_id
            or item.parameter_id != item.parameter_id.strip()
            or not isinstance(item.value, str)
            or item.value_type is not None and not isinstance(item.value_type, str)
            or item.unit is not None and not isinstance(item.unit, str)
        ):
            raise ParameterVersionBindingError(
                "INVALID_VERSION_CONFIGURATION", "Historical configuration identity or type is invalid",
            )
        raw = asdict(item)
        for field in ("valid_from", "valid_to", "created_at", "updated_at"):
            stamp = raw[field]
            raw[field] = _timestamp(stamp) if stamp is not None else None
        if (
            item.valid_to is not None and item.valid_from >= item.valid_to
            or not (item.valid_from <= effective_at and (
                item.valid_to is None or effective_at < item.valid_to
            ))
        ):
            raise ParameterVersionBindingError(
                "INVALID_VERSION_CONFIGURATION", "Historical configuration is not valid at cutoff",
            )
        records.append(raw)
    return _fingerprint_configuration_records(
        company_id=company_id, parameters_version=parameters_version,
        effective_at=effective_at, records=records,
    )


def fingerprint_parameter_selection(lookup: CompanyParameterLookup) -> str:
    """Hash *exact selected configuration contents*, not C0 or DIP identities.

    This is a comparison checksum for a version-authority manifest. It does
    not become a new parameters_version, C0 input_fingerprint, or evidence.
    """
    if not isinstance(lookup, CompanyParameterLookup):
        raise TypeError("lookup must be CompanyParameterLookup")
    _identifier(lookup.company_id, "company_id")
    _identifier(lookup.parameters_version, "parameters_version")
    effective = _timestamp(lookup.effective_at)
    if not lookup.complete_documentary_coverage:
        raise ParameterVersionBindingError(
            "INCOMPLETE_DOCUMENTARY_COVERAGE",
            "A version can only be checked against a complete evidenced selection",
        )
    if len({e.parameter_id for e in lookup.entries}) != len(lookup.entries):
        raise ParameterVersionBindingError(
            "DUPLICATE_PARAMETER", "Duplicate parameter in selected configurations",
        )
    selected = []
    for entry in sorted(lookup.entries, key=lambda item: item.parameter_id):
        resolution = entry.resolution
        proof = entry.evidence
        if resolution is None or proof is None:
            raise ParameterVersionBindingError(
                "INCOMPLETE_DOCUMENTARY_COVERAGE", "Missing resolved configuration",
            )
        if (
            resolution.company_id != lookup.company_id
            or resolution.parameter_id != entry.parameter_id
            or resolution.parameters_version != lookup.parameters_version
            or _timestamp(resolution.effective_at) != effective
        ):
            raise ParameterVersionBindingError(
                "SELECTION_CONTEXT_MISMATCH", "Resolution differs from selection scope",
            )
        config = resolution.configuration
        if (
            config.company_id != lookup.company_id
            or config.parameter_id != entry.parameter_id
            or type(config.configuration_id) is not int
            or config.configuration_id < 0
        ):
            raise ParameterVersionBindingError(
                "SELECTION_CONFIGURATION_INVALID", "Foreign or invalid configuration",
            )
        record = asdict(config)
        for field in ("valid_from", "valid_to", "created_at", "updated_at"):
            record[field] = (
                _timestamp(record[field]) if record[field] is not None else None
            )
        selected.append(record)
    return _fingerprint_configuration_records(
        company_id=lookup.company_id,
        parameters_version=lookup.parameters_version,
        effective_at=lookup.effective_at,
        records=selected,
    )


def read_version_bound_parameter_selection(
    *,
    center: ParameterConfigurationCenter,
    version_source: ParameterVersionSource,
    company_id: str,
    expected_company_id: str,
    context: DecisionContext,
    effective_at: datetime,
    parameter_ids: tuple[str, ...],
    evidence_by_parameter: Mapping[str, Evidence],
) -> VersionBoundParameterSelection:
    """Fail closed unless all selected values match the source's exact version.

    Manifest reads are repeated around Centre queries to catch basic source
    drift; this is NOT a transaction or a guarantee of external authenticity.
    """
    if not isinstance(context, DecisionContext):
        raise TypeError("context must be DecisionContext")
    if not isinstance(center, ParameterConfigurationCenter):
        raise TypeError("center must be ParameterConfigurationCenter")
    _identifier(company_id, "company_id")
    _identifier(expected_company_id, "expected_company_id")
    if company_id != expected_company_id:
        raise ParameterVersionBindingError(
            "COMPANY_SCOPE_MISMATCH", "Expected company differs from request",
        )
    _timestamp(effective_at)
    if (
        not isinstance(parameter_ids, tuple) or not parameter_ids
        or any(not isinstance(pid, str) or not pid or pid != pid.strip()
               for pid in parameter_ids)
        or len(parameter_ids) != len(set(parameter_ids))
    ):
        raise ParameterVersionBindingError(
            "INVALID_SELECTION", "Requested parameter IDs are invalid or duplicated",
        )
    if not isinstance(evidence_by_parameter, Mapping):
        raise TypeError("evidence_by_parameter must be a Mapping")

    # Freeze the request BEFORE invoking even the supplied version-source port.
    frozen_context = DecisionContext.model_validate(
        deepcopy(context.model_dump(mode="python")),
    )
    frozen_evidence: dict[str, Evidence] = {}
    for pid, proof in evidence_by_parameter.items():
        if not isinstance(pid, str) or not isinstance(proof, Evidence):
            raise TypeError("Evidence requires string parameter IDs and Evidence objects")
        frozen_evidence[pid] = proof.model_copy(deep=True)

    getter = getattr(version_source, "get_version_manifest", None)
    if not callable(getter):
        raise ParameterVersionBindingError(
            "VERSION_SOURCE_UNAVAILABLE", "No version-authority source was provided",
        )
    manifest = _manifest_check(
        getter(company_id, frozen_context.parameters_version, effective_at),
        company_id=company_id, context=frozen_context,
        effective_at=effective_at, parameter_ids=parameter_ids,
    )
    # The existing Centre and evidence-aware F2.3 lookup remain the only
    # configuration selection path. No defaults or second Centre.
    lookup = read_company_parameters_for_context(
        center=center, company_id=company_id,
        expected_company_id=expected_company_id, context=frozen_context,
        effective_at=effective_at, parameter_ids=parameter_ids,
        evidence_by_parameter=frozen_evidence,
    )
    digest = fingerprint_parameter_selection(lookup)
    if not compare_digest(digest, manifest.selection_fingerprint):
        raise ParameterVersionBindingError(
            "VERSION_CONTENT_MISMATCH",
            "The selected values do not match the manifest for parameters_version",
        )
    after = _manifest_check(
        getter(company_id, frozen_context.parameters_version, effective_at),
        company_id=company_id, context=frozen_context,
        effective_at=effective_at, parameter_ids=parameter_ids,
    )
    if manifest != after:
        raise ParameterVersionBindingError(
            "VERSION_SOURCE_CHANGED",
            "Version source changed during the Centre selection",
        )
    return VersionBoundParameterSelection(
        lookup=lookup,
        manifest=manifest,
        selection_fingerprint=digest,
    )


__all__ = [
    "SELECTION_SCHEMA", "ParameterVersionBindingError",
    "ParameterVersionManifest", "ParameterVersionSource",
    "VersionBoundParameterSelection", "fingerprint_parameter_selection",
    "fingerprint_historical_parameter_configurations",
    "read_version_bound_parameter_selection",
]
