"""Fail-closed correspondence of a company parameter lookup to one canonical DIP.

This verifies a *captured selection*, not historical registration of
DecisionContext.parameters_version. A DIP fingerprint is a content identity,
not a signature, an authenticated data source, or an authorization.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from eios.core.decision_input_package import DecisionInputPackage
from eios.core.models import DecisionContext, Evidence

from .company_resolution_api import (
    EVIDENCE_SOURCE_TYPE, CompanyParameterLookup, ParameterLookupEntry,
)


class ParameterCaptureVerificationError(ValueError):
    """A stable fail-closed code for incomplete or inconsistent captures."""

    def __init__(self, code: str, message: str) -> None:
        self.code = code
        super().__init__(message)


@dataclass(frozen=True, slots=True)
class ParameterCaptureVerification:
    """A matched selection only; never proof of historical version authority."""

    company_id: str
    decision_id: str
    scenario_id: str
    data_snapshot_id: str
    parameters_version: str
    parameter_ids: tuple[str, ...]
    dip_fingerprint: str
    capture_status: Literal["MATCHED_DIP_CAPTURE_ONLY"] = "MATCHED_DIP_CAPTURE_ONLY"
    version_attestation: Literal["HISTORICAL_VERSION_NOT_ATTESTED"] = (
        "HISTORICAL_VERSION_NOT_ATTESTED"
    )
    origin_attestation: Literal["NOT_EXTERNALLY_AUTHENTICATED"] = (
        "NOT_EXTERNALLY_AUTHENTICATED"
    )
    decision_authority: Literal[False] = False
    operational_path: Literal["FORBIDDEN"] = "FORBIDDEN"


def _fail(code: str, message: str) -> None:
    raise ParameterCaptureVerificationError(code, message)


def _evidence_material(evidence: Evidence) -> dict:
    """Revalidate before matching, including objects built by model_construct."""
    return Evidence.model_validate(evidence.model_dump(mode="python")).model_dump(
        mode="json"
    )


def verify_company_parameter_capture(
    *,
    lookup: CompanyParameterLookup,
    package: DecisionInputPackage,
    context: DecisionContext,
) -> ParameterCaptureVerification:
    """Compare the *entire* documented lookup with a factory-built DIP capture.

    The caller is responsible for authenticating the producer, tenant and
    historical parameters_version. This read-only check does not query a second
    repository, activate settings, or authorize rule evaluation.
    """
    if not isinstance(lookup, CompanyParameterLookup):
        raise TypeError("lookup must be CompanyParameterLookup")
    if not isinstance(package, DecisionInputPackage):
        raise TypeError("package must be DecisionInputPackage")
    if not isinstance(context, DecisionContext):
        raise TypeError("context must be DecisionContext")

    context_copy = DecisionContext.model_validate(context.model_dump(mode="python"))
    if (
        lookup.decision_id != context_copy.decision_id
        or lookup.scenario_id != context_copy.scenario_id
        or lookup.parameters_version != context_copy.parameters_version
        or lookup.data_snapshot_id != context_copy.data_snapshot_id
    ):
        _fail("LOOKUP_CONTEXT_MISMATCH", "Lookup differs from the expected decision context")
    # DIP stores rules_version too; a fresh caller-supplied context is necessary
    # because the F2.3 lookup did not expose that field.
    if package.context != context_copy:
        _fail("DIP_CONTEXT_MISMATCH", "DIP context differs from the expected full context")
    if package.company_id != lookup.company_id:
        _fail("DIP_COMPANY_MISMATCH", "DIP belongs to another company")
    if package.effective_at != lookup.effective_at:
        _fail("DIP_EFFECTIVE_AT_MISMATCH", "DIP and lookup use different cutoffs")

    requested = tuple(item.parameter_id for item in lookup.entries)
    if not requested or len(requested) != len(set(requested)):
        _fail("INVALID_LOOKUP_SELECTION", "The lookup selection is empty or duplicated")
    if package.requested_parameter_ids != requested:
        _fail("DIP_SELECTION_MISMATCH", "DIP must capture exactly the lookup selection")
    if package.missing_parameter_ids:
        _fail("DIP_INCOMPLETE", "DIP has unresolved requested configurations")
    if not lookup.complete_documentary_coverage:
        _fail("LOOKUP_INCOMPLETE", "Every requested parameter must have checked evidence")

    captured = package.configurations
    if len(captured) != len(requested):
        _fail("DIP_INCOMPLETE", "DIP configuration count is not complete")
    if tuple(item.parameter_id for item in captured) != requested:
        _fail("DIP_CONFIGURATION_MISMATCH", "DIP configuration order or identity differs")

    supplied = package.evidence
    evidence_ids = [item.evidence_id for item in supplied]
    if len(evidence_ids) != len(set(evidence_ids)):
        _fail("DIP_EVIDENCE_REUSED", "DIP reuses evidence identifiers")
    parameter_evidence = [
        item for item in supplied if item.source_type == EVIDENCE_SOURCE_TYPE
    ]
    if len(parameter_evidence) != len(requested):
        _fail("DIP_EVIDENCE_SELECTION_MISMATCH", "DIP must contain exactly one proof per selected parameter")
    evidence_by_id = {item.evidence_id: item for item in parameter_evidence}

    used_evidence_ids: set[str] = set()
    for pid, entry, dip_resolution in zip(requested, lookup.entries, captured):
        if not isinstance(entry, ParameterLookupEntry) or not entry.ready_for_consumer_checks:
            _fail("LOOKUP_INCOMPLETE", "A selected parameter is not documented")
        if entry.resolution is None or entry.evidence is None:
            _fail("LOOKUP_INCOMPLETE", "A selected parameter lacks resolution or evidence")
        resolved = entry.resolution
        if (
            resolved.company_id != lookup.company_id
            or resolved.parameter_id != pid
            or resolved.parameters_version != lookup.parameters_version
            or resolved.effective_at != lookup.effective_at
            or resolved != dip_resolution
        ):
            _fail("DIP_CONFIGURATION_MISMATCH", "A captured configuration differs from the lookup")
        proof = entry.evidence
        if proof.evidence_id in used_evidence_ids:
            _fail("DIP_EVIDENCE_REUSED", "An evidence identifier is reused")
        used_evidence_ids.add(proof.evidence_id)
        captured_proof = evidence_by_id.get(proof.evidence_id)
        if captured_proof is None or _evidence_material(proof) != _evidence_material(captured_proof):
            _fail("DIP_EVIDENCE_MISMATCH", "A selected proof differs from the DIP capture")

    if used_evidence_ids != set(evidence_by_id):
        _fail("DIP_EVIDENCE_SELECTION_MISMATCH", "DIP contains an unselected parameter proof")
    return ParameterCaptureVerification(
        company_id=lookup.company_id,
        decision_id=lookup.decision_id,
        scenario_id=lookup.scenario_id,
        data_snapshot_id=lookup.data_snapshot_id,
        parameters_version=lookup.parameters_version,
        parameter_ids=requested,
        dip_fingerprint=package.fingerprint,
    )


__all__ = [
    "ParameterCaptureVerification",
    "ParameterCaptureVerificationError",
    "verify_company_parameter_capture",
]
