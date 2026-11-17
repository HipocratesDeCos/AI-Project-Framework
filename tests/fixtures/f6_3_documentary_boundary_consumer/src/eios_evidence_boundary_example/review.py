"""F6.3 — independently owned *synthetic* documentary trust boundary.

The external host is responsible for real enterprise authentication, document
verification, access control, trusted clock and custody; NONE is implemented
here. Every returned proof is deliberately marked SYNTHETIC_TEST_DOUBLE.
A matched hash or response from a fake provider does not prove authenticity.
Never use this function to admit operational material or change EIOS authority.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from hashlib import sha256
import re
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from eios_company_adapter_example import PreparedExternalCase, SyntheticEquipmentRecord


MAX_DOCUMENT_BYTES = 65_536
SHA_RE = re.compile(r"[0-9a-f]{64}\Z")
PERMISSION = "SYNTHETIC_DOCUMENTARY_SCOPE_REVIEW"
ASSURANCE = "SYNTHETIC_TEST_DOUBLE"


class DocumentaryBoundaryError(ValueError):
    """A separate evidence/identity/permission gate failed closed."""


class ReviewRequest(BaseModel):
    """Host-controlled expectations; not sourced from the business payload."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    session_ref: str = Field(min_length=1, max_length=128)
    project_id: str = Field(min_length=1, max_length=128)
    company_id: str = Field(min_length=1, max_length=128)
    source_id: str = Field(min_length=1, max_length=128)
    data_snapshot_id: str = Field(min_length=1, max_length=64)
    expected_source_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    document_ref: str = Field(min_length=1, max_length=128)
    expected_document_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    reviewed_at: datetime
    purpose: Literal["SYNTHETIC_TEST_ONLY"] = "SYNTHETIC_TEST_ONLY"

    @model_validator(mode="after")
    def aware(self):
        if self.reviewed_at.utcoffset() is None:
            raise ValueError("A trusted timezone-aware clock is required")
        return self


@dataclass(frozen=True)
class IdentityRecord:
    project_id: str
    company_id: str
    session_ref: str
    subject_id: str
    identity_ref: str
    valid_from: datetime
    valid_to: datetime
    assurance: str = ASSURANCE


@dataclass(frozen=True)
class DocumentRecord:
    project_id: str
    company_id: str
    source_id: str
    data_snapshot_id: str
    document_ref: str
    document_sha256: str
    content: bytes
    assurance: str = ASSURANCE


@dataclass(frozen=True)
class PermissionRecord:
    project_id: str
    company_id: str
    subject_id: str
    document_ref: str
    permission: str
    grant_ref: str
    valid_from: datetime
    valid_to: datetime
    assurance: str = ASSURANCE


@dataclass(frozen=True)
class ReviewReceipt:
    status: str
    project_id: str
    company_id: str
    source_sha256: str
    document_sha256: str
    document_ref: str
    subject_id: str
    identity_ref: str
    grant_ref: str
    technical_input_validated: bool = True
    real_company_authenticated: bool = False
    real_document_authenticated: bool = False
    real_human_authorized: bool = False
    production_authorized: bool = False
    decision_authority: bool = False
    operational_path: str = "FORBIDDEN"
    provenance_status: str = "UNVERIFIED_ADAPTER_RESPONSIBILITY"


def _text(value: object, name: str) -> None:
    if type(value) is not str or not value or value != value.strip() or len(value) > 128:
        raise DocumentaryBoundaryError("INVALID_TRUST_FIELD:" + name)


def _period(begin: object, end: object, reviewed_at: datetime) -> None:
    if (
        type(begin) is not datetime or type(end) is not datetime
        or begin.utcoffset() is None or end.utcoffset() is None
        or not (begin <= reviewed_at < end)
    ):
        raise DocumentaryBoundaryError("TRUST_WINDOW_NOT_VALID")


def _identity(source: object, request: ReviewRequest) -> IdentityRecord:
    provider = getattr(source, "resolve_identity", None)
    if not callable(provider):
        raise DocumentaryBoundaryError("IDENTITY_PROVIDER_REQUIRED")
    record = provider(request.session_ref, request.reviewed_at)
    if type(record) is not IdentityRecord or record.assurance != ASSURANCE:
        raise DocumentaryBoundaryError("IDENTITY_NOT_IN_SYNTHETIC_SCOPE")
    for name in ("subject_id", "identity_ref"):
        _text(getattr(record, name), name)
    if (
        record.project_id != request.project_id
        or record.company_id != request.company_id
        or record.session_ref != request.session_ref
    ):
        raise DocumentaryBoundaryError("IDENTITY_SCOPE_MISMATCH")
    _period(record.valid_from, record.valid_to, request.reviewed_at)
    return record


def _document(source: object, request: ReviewRequest) -> DocumentRecord:
    provider = getattr(source, "load_document", None)
    if not callable(provider):
        raise DocumentaryBoundaryError("DOCUMENT_PROVIDER_REQUIRED")
    record = provider(
        request.project_id, request.company_id,
        request.document_ref, request.reviewed_at,
    )
    if type(record) is not DocumentRecord or record.assurance != ASSURANCE:
        raise DocumentaryBoundaryError("DOCUMENT_NOT_IN_SYNTHETIC_SCOPE")
    for field in (
        "project_id", "company_id", "source_id", "data_snapshot_id", "document_ref",
    ):
        if getattr(record, field) != getattr(request, field):
            raise DocumentaryBoundaryError("DOCUMENT_SCOPE_MISMATCH:" + field)
    if (
        type(record.content) is not bytes
        or not (0 < len(record.content) <= MAX_DOCUMENT_BYTES)
        or type(record.document_sha256) is not str
        or not SHA_RE.fullmatch(record.document_sha256)
    ):
        raise DocumentaryBoundaryError("INVALID_DOCUMENT_CONTENT_OR_DIGEST")
    if (
        sha256(record.content).hexdigest() != record.document_sha256
        or record.document_sha256 != request.expected_document_sha256
    ):
        raise DocumentaryBoundaryError("DOCUMENT_DIGEST_MISMATCH")
    return record


def _permission(source: object, request: ReviewRequest, identity: IdentityRecord) -> PermissionRecord:
    provider = getattr(source, "resolve_permission", None)
    if not callable(provider):
        raise DocumentaryBoundaryError("PERMISSION_PROVIDER_REQUIRED")
    record = provider(
        request.project_id, request.company_id, identity.subject_id,
        request.document_ref, request.reviewed_at,
    )
    if type(record) is not PermissionRecord or record.assurance != ASSURANCE:
        raise DocumentaryBoundaryError("REVIEW_PERMISSION_NOT_IN_SYNTHETIC_SCOPE")
    _text(record.grant_ref, "grant_ref")
    if (
        record.project_id != request.project_id
        or record.company_id != request.company_id
        or record.subject_id != identity.subject_id
        or record.document_ref != request.document_ref
        or record.permission != PERMISSION
    ):
        raise DocumentaryBoundaryError("REVIEW_PERMISSION_SCOPE_MISMATCH")
    _period(record.valid_from, record.valid_to, request.reviewed_at)
    return record


def review_synthetic_boundary(
    *,
    prepared: PreparedExternalCase,
    request: ReviewRequest,
    identity_source: object,
    document_source: object,
    permission_source: object,
) -> ReviewReceipt:
    """Two-pass fail-closed conformance; test doubles never confer actual trust.

    This code deliberately does NOT call operational admission, QTG, PRICE,
    catalog authorization, network services or a real identity provider.
    """
    if type(prepared) is not PreparedExternalCase or type(request) is not ReviewRequest:
        raise DocumentaryBoundaryError("INVALID_BOUNDARY_INPUT")
    payload = prepared.operation.payload
    if type(payload) is not SyntheticEquipmentRecord:
        raise DocumentaryBoundaryError("UNSUPPORTED_DOCUMENTARY_PAYLOAD")
    expected = (
        (request.project_id, prepared.context.project_id),
        (request.project_id, payload.project_id),
        (request.company_id, prepared.company_id),
        (request.company_id, payload.company_id),
        (request.source_id, prepared.source_id),
        (request.source_id, payload.source_id),
        (request.data_snapshot_id, prepared.context.data_snapshot_id),
        (request.data_snapshot_id, payload.data_snapshot_id),
        (request.expected_source_sha256, prepared.raw_sha256),
        (request.document_ref, payload.inspection_reference),
    )
    if any(a != b for a, b in expected):
        raise DocumentaryBoundaryError("PREPARED_EXTERNAL_SCOPE_MISMATCH")
    if (
        prepared.production_authorized is not False
        or prepared.operational_path != "FORBIDDEN"
        or prepared.provenance_status != "UNVERIFIED_ADAPTER_RESPONSIBILITY"
        or payload.evidence_class != "SYNTHETIC_TEST"
        or payload.documentary_status != "UNVERIFIED"
    ):
        raise DocumentaryBoundaryError("UNTRUSTED_PROVENANCE_PROMOTION")
    for provider, method, code in (
        (identity_source, "resolve_identity", "IDENTITY_PROVIDER_REQUIRED"),
        (document_source, "load_document", "DOCUMENT_PROVIDER_REQUIRED"),
        (permission_source, "resolve_permission", "PERMISSION_PROVIDER_REQUIRED"),
    ):
        if not callable(getattr(provider, method, None)):
            raise DocumentaryBoundaryError(code)

    before_identity = _identity(identity_source, request)
    before_doc = _document(document_source, request)
    before_grant = _permission(permission_source, request, before_identity)
    after_identity = _identity(identity_source, request)
    after_doc = _document(document_source, request)
    after_grant = _permission(permission_source, request, after_identity)
    if (
        before_identity != after_identity
        or before_doc != after_doc
        or before_grant != after_grant
    ):
        raise DocumentaryBoundaryError("SYNTHETIC_TRUST_STATE_CHANGED")

    return ReviewReceipt(
        status="SYNTHETIC_BOUNDARY_CHECKS_PASSED",
        project_id=request.project_id,
        company_id=request.company_id,
        source_sha256=request.expected_source_sha256,
        document_sha256=request.expected_document_sha256,
        document_ref=request.document_ref,
        subject_id=before_identity.subject_id,
        identity_ref=before_identity.identity_ref,
        grant_ref=before_grant.grant_ref,
    )


__all__ = [
    "DocumentaryBoundaryError", "ReviewRequest", "IdentityRecord",
    "DocumentRecord", "PermissionRecord", "ReviewReceipt",
    "review_synthetic_boundary",
]
