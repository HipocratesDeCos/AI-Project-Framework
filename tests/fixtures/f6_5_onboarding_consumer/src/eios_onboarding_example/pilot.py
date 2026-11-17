"""F6.6 — non-authoritative supervised read-only rehearsal preflight.

This CHECKLIST is not a second operational-intake or admission framework.
It audits whether a synthetic external integration REHEARSAL was described
completely and bound to the existing F6.5/F6.3 review receipt. It does NOT
admit any operational expediente, issue real credentials, authenticate
evidence, or authorize QTG, purchases, writes, or financial decisions.

Every "complete" outcome means only that synthetic cases exercised declared
items. A trusted real enterprise must be authenticated OUTSIDE this code.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
import json
import re

from eios_evidence_boundary_example.review import ReviewRequest
from .onboarding import OnboardingReceipt, PinnedOnboarding

REQUIREMENTS: tuple[str, ...] = (
    "COMPANY_AND_PROJECT_MANDATE",
    "HOST_IDENTITY_SCOPE",
    "PINNED_THREE_PROVIDER_REGISTRY",
    "READ_ONLY_BOUNDARY",
    "DOCUMENT_SOURCE_AND_DIGEST",
    "CUSTODY_AND_RETENTION_POLICY",
    "REVIEWER_PERMISSION_SCOPE",
    "TRACE_AND_TRUSTED_TIME",
    "ACCESS_REVOCATION_REHEARSAL",
    "STOP_AND_INCIDENT_PLAN",
    "PRIVACY_AND_MINIMUM_DATA",
    "OPERATIONAL_ROUTE_FORBIDDEN",
)
STATUS = ("SYNTHETIC_REHEARSED", "MISSING", "UNVERIFIED")
IDENTIFIER = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}\Z")
DIGEST = re.compile(r"[0-9a-f]{64}\Z")


class PilotReadinessError(ValueError):
    """An input or claimed authority crossed the rehearsal boundary."""


def _id(value: object, field: str) -> None:
    if type(value) is not str or not IDENTIFIER.fullmatch(value):
        raise PilotReadinessError("INVALID_PILOT_FIELD:" + field)


def _canonical(payload: dict) -> bytes:
    return json.dumps(
        payload, ensure_ascii=False, sort_keys=True,
        separators=(",", ":"), allow_nan=False,
    ).encode("utf-8")


@dataclass(frozen=True)
class RehearsalChecklistItem:
    requirement_id: str
    status: str
    support_ref: str | None = None

    def __post_init__(self) -> None:
        if self.requirement_id not in REQUIREMENTS:
            raise PilotReadinessError("UNKNOWN_PILOT_REQUIREMENT")
        if type(self.status) is not str or self.status not in STATUS:
            raise PilotReadinessError("INVALID_PILOT_EVIDENCE_STATUS")
        if self.status == "SYNTHETIC_REHEARSED":
            _id(self.support_ref, "support_ref")
            if not self.support_ref.startswith("SYNTHETIC_"):
                raise PilotReadinessError("REAL_EVIDENCE_CLAIM_FORBIDDEN")
        elif self.support_ref is not None:
            raise PilotReadinessError("UNVERIFIED_OR_MISSING_SUPPORT_CANNOT_BE_REFERENCED")


@dataclass(frozen=True)
class RehearsalManifest:
    project_id: str
    company_id: str
    data_snapshot_id: str
    registry_digest: str
    registry_revision: int
    rehearsal_ref: str
    observer_ref: str
    reviewed_at: datetime
    checks: tuple[RehearsalChecklistItem, ...]
    purpose: str = "SYNTHETIC_TEST_ONLY"
    mode: str = "READ_ONLY_SYNTHETIC_REHEARSAL"

    def __post_init__(self) -> None:
        for name in (
            "project_id", "company_id", "data_snapshot_id",
            "rehearsal_ref", "observer_ref",
        ):
            _id(getattr(self, name), name)
        if not self.rehearsal_ref.startswith("SYNTHETIC_") or not self.observer_ref.startswith("SYNTHETIC_"):
            raise PilotReadinessError("REAL_OBSERVER_OR_REHEARSAL_CLAIM_FORBIDDEN")
        if type(self.registry_digest) is not str or not DIGEST.fullmatch(self.registry_digest):
            raise PilotReadinessError("INVALID_PILOT_PIN")
        if type(self.registry_revision) is not int or self.registry_revision < 1:
            raise PilotReadinessError("INVALID_PILOT_REVISION")
        if type(self.reviewed_at) is not datetime or self.reviewed_at.utcoffset() is None:
            raise PilotReadinessError("TRUSTED_AWARE_TIME_REQUIRED")
        if self.purpose != "SYNTHETIC_TEST_ONLY" or self.mode != "READ_ONLY_SYNTHETIC_REHEARSAL":
            raise PilotReadinessError("OPERATIONAL_PILOT_PROMOTION_FORBIDDEN")
        if type(self.checks) is not tuple or tuple(
            item.requirement_id if type(item) is RehearsalChecklistItem else None
            for item in self.checks
        ) != REQUIREMENTS:
            raise PilotReadinessError("INCOMPLETE_OR_DUPLICATE_PILOT_CHECKLIST")
        refs = [x.support_ref for x in self.checks if x.support_ref is not None]
        if len(set(refs)) != len(refs):
            raise PilotReadinessError("DUPLICATE_PILOT_SUPPORT_REF")


@dataclass(frozen=True)
class PilotRehearsalResult:
    status: str
    project_id: str
    company_id: str
    missing: tuple[str, ...]
    unverified: tuple[str, ...]
    observed: tuple[str, ...]
    registry_digest: str
    technical_receipt_digest: str
    manifest_digest: str
    result_fingerprint: str
    synthetic_rehearsal_complete: bool
    real_pilot_admitted: bool = False
    real_company_authenticated: bool = False
    real_document_authenticated: bool = False
    real_human_authorized: bool = False
    decision_authority: bool = False
    production_authorized: bool = False
    operational_path: str = "FORBIDDEN"


def assess_read_only_rehearsal(
    *,
    manifest: RehearsalManifest,
    pin: PinnedOnboarding,
    request: ReviewRequest,
    technical_review: OnboardingReceipt,
) -> PilotRehearsalResult:
    """Bind only synthetic procedural status to the existing F6.5 receipt.

    Does not call underlying providers, execute or authorize any operation.
    A receipt can be manufactured by untrusted code; the result is therefore
    strictly a TEST PREPARATION indicator, not an access or trust token.
    """
    if (
        type(manifest) is not RehearsalManifest
        or type(pin) is not PinnedOnboarding
        or type(request) is not ReviewRequest
        or type(technical_review) is not OnboardingReceipt
    ):
        raise PilotReadinessError("REQUIRES_EXISTING_SYNTHETIC_TECHNICAL_REVIEW")
    if any(
        x != y for x, y in (
            (manifest.project_id, pin.project_id),
            (manifest.company_id, pin.company_id),
            (manifest.project_id, request.project_id),
            (manifest.company_id, request.company_id),
            (manifest.data_snapshot_id, request.data_snapshot_id),
            (manifest.registry_digest, pin.expected_digest),
            (manifest.registry_revision, pin.expected_revision),
            (manifest.reviewed_at, request.reviewed_at),
            (technical_review.project_id, pin.project_id),
            (technical_review.company_id, pin.company_id),
            (technical_review.registry_digest, pin.expected_digest),
            (technical_review.expected_revision, pin.expected_revision),
        )
    ):
        raise PilotReadinessError("REHEARSAL_TENANT_SNAPSHOT_OR_PIN_MISMATCH")

    review = technical_review.review_receipt
    if (
        technical_review.status != "SYNTHETIC_PROVIDER_ONBOARDING_READY"
        or technical_review.operational_path != "FORBIDDEN"
        or technical_review.production_authorized is not False
        or technical_review.decision_authority is not False
        or technical_review.real_provider_connected is not False
        or technical_review.real_enterprise_authenticated is not False
        or technical_review.real_document_authenticated is not False
        or technical_review.real_reviewer_authorized is not False
        or review.status != "SYNTHETIC_BOUNDARY_CHECKS_PASSED"
        or review.project_id != manifest.project_id
        or review.company_id != manifest.company_id
        or review.source_sha256 != request.expected_source_sha256
        or review.document_sha256 != request.expected_document_sha256
        or review.document_ref != request.document_ref
        or review.operational_path != "FORBIDDEN"
        or review.production_authorized is not False
        or review.decision_authority is not False
        or review.real_company_authenticated is not False
        or review.real_document_authenticated is not False
        or review.real_human_authorized is not False
    ):
        raise PilotReadinessError("F6_5_OR_F6_3_AUTHORITY_PROMOTION_OR_MISMATCH")

    missing = tuple(x.requirement_id for x in manifest.checks if x.status == "MISSING")
    unverified = tuple(x.requirement_id for x in manifest.checks if x.status == "UNVERIFIED")
    observed = tuple(x.requirement_id for x in manifest.checks if x.status == "SYNTHETIC_REHEARSED")
    complete = not missing and not unverified
    record = {
        "schema": "F6_6_READ_ONLY_REHEARSAL_01/v0.1",
        "project_id": manifest.project_id,
        "company_id": manifest.company_id,
        "data_snapshot_id": manifest.data_snapshot_id,
        "rehearsal_ref": manifest.rehearsal_ref,
        "observer_ref": manifest.observer_ref,
        "reviewed_at": manifest.reviewed_at.astimezone(timezone.utc).isoformat(),
        "registry_digest": manifest.registry_digest,
        "registry_revision": manifest.registry_revision,
        "checklist": [(x.requirement_id, x.status, x.support_ref) for x in manifest.checks],
        "source_sha256": request.expected_source_sha256,
        "document_sha256": request.expected_document_sha256,
        "document_ref": request.document_ref,
        "technical_receipt": {
            "providers": [list(x) for x in technical_review.providers],
            "identity_ref": review.identity_ref,
            "grant_ref": review.grant_ref,
            "subject_id": review.subject_id,
        },
    }
    manifest_only = _canonical({key: value for key, value in record.items() if key != "technical_receipt"})
    technical_only = _canonical(record["technical_receipt"])
    result_fingerprint = sha256(_canonical(record)).hexdigest()
    return PilotRehearsalResult(
        status=("SYNTHETIC_REHEARSAL_COMPLETE" if complete else "REHEARSAL_INCOMPLETE"),
        project_id=manifest.project_id,
        company_id=manifest.company_id,
        missing=missing,
        unverified=unverified,
        observed=observed,
        registry_digest=manifest.registry_digest,
        technical_receipt_digest=sha256(technical_only).hexdigest(),
        manifest_digest=sha256(manifest_only).hexdigest(),
        result_fingerprint=result_fingerprint,
        synthetic_rehearsal_complete=complete,
    )


__all__ = [
    "REQUIREMENTS", "RehearsalChecklistItem", "RehearsalManifest",
    "PilotReadinessError", "PilotRehearsalResult", "assess_read_only_rehearsal",
]
