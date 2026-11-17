"""F6.5 - Host-pinned provider registry and synthetic-only onboarding gate.

This is NOT an identity provider, a signature verifier, a remote connector,
a document authenticator, or permission to process real corporate data.
The caller supplies a trusted EXPECTATION and registry source independently
from the source document. SHA-256 only checks agreement with the supplied pin.
Do not use test-double registration as evidence of real authentication.

The gate validates an exact three-role snapshot before every delegated call,
then rechecks it after the preexisting F6.3 double review. A revoked, expired,
drifting, foreign, incomplete or version-mismatched registry rejects closed.
It leaves all canonical EIOS and F6.2/F6.3/F6.4 modules untouched.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
import json
import re
from typing import Callable, Mapping

from eios_company_adapter_example import PreparedExternalCase
from eios_evidence_boundary_example.review import (
    ReviewRequest, ReviewReceipt, review_synthetic_boundary,
)

ROLES = ("IDENTITY", "DOCUMENT", "REVIEW_PERMISSION")
API_VERSION = "1.0.0"
POLICY = "F6_5_SYNTHETIC_ONBOARDING_1"
ASSURANCE = "SYNTHETIC_TEST_DOUBLE"
_IDENT = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}\Z")
_HASH = re.compile(r"[0-9a-f]{64}\Z")
_METHOD = {
    "IDENTITY": "resolve_identity",
    "DOCUMENT": "load_document",
    "REVIEW_PERMISSION": "resolve_permission",
}


class OnboardingError(ValueError):
    """Provider scope, pin, expiry, revocation or contract failed closed."""


def _id(value: object, name: str) -> None:
    if type(value) is not str or not _IDENT.fullmatch(value):
        raise OnboardingError("INVALID_ONBOARDING_FIELD:" + name)


def _aware(value: object, name: str) -> None:
    if type(value) is not datetime or value.utcoffset() is None:
        raise OnboardingError("INVALID_ONBOARDING_TIME:" + name)


def _canonical(value: dict) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True,
        separators=(",", ":"), allow_nan=False,
    ).encode("utf-8")


@dataclass(frozen=True)
class ProviderRegistration:
    role: str
    provider_id: str
    project_id: str
    company_id: str
    integration_ref: str
    api_version: str
    valid_from: datetime
    valid_to: datetime
    enabled: bool
    assurance: str = ASSURANCE

    def __post_init__(self) -> None:
        if self.role not in ROLES:
            raise OnboardingError("UNKNOWN_PROVIDER_ROLE")
        for field in ("provider_id", "project_id", "company_id", "integration_ref"):
            _id(getattr(self, field), field)
        if self.api_version != API_VERSION:
            raise OnboardingError("UNSUPPORTED_PROVIDER_API_VERSION")
        if self.assurance != ASSURANCE:
            raise OnboardingError("REAL_AUTHENTICATION_CLAIM_NOT_SUPPORTED")
        if type(self.enabled) is not bool:
            raise OnboardingError("INVALID_PROVIDER_STATUS")
        _aware(self.valid_from, "valid_from")
        _aware(self.valid_to, "valid_to")
        if not self.valid_from < self.valid_to:
            raise OnboardingError("INVALID_PROVIDER_VALIDITY_RANGE")


@dataclass(frozen=True)
class OnboardingSnapshot:
    project_id: str
    company_id: str
    revision: int
    registrations: tuple[ProviderRegistration, ...]
    purpose: str = "SYNTHETIC_TEST_ONLY"
    policy_version: str = POLICY

    def __post_init__(self) -> None:
        _id(self.project_id, "project_id")
        _id(self.company_id, "company_id")
        if type(self.revision) is not int or self.revision < 1:
            raise OnboardingError("INVALID_PROVIDER_REGISTRY_REVISION")
        if self.purpose != "SYNTHETIC_TEST_ONLY" or self.policy_version != POLICY:
            raise OnboardingError("PROVIDER_REGISTRY_OPERATIONAL_PROMOTION")
        if type(self.registrations) is not tuple or len(self.registrations) != len(ROLES):
            raise OnboardingError("INCOMPLETE_PROVIDER_REGISTRY")
        if any(type(row) is not ProviderRegistration for row in self.registrations):
            raise OnboardingError("INVALID_PROVIDER_REGISTRATION")
        if tuple(row.role for row in self.registrations) != ROLES:
            raise OnboardingError("UNORDERED_DUPLICATE_OR_MISSING_PROVIDER_ROLE")
        if len({row.provider_id for row in self.registrations}) != len(ROLES):
            raise OnboardingError("NONINDEPENDENT_PROVIDER_IDENTIFIERS")
        if any(
            row.project_id != self.project_id or row.company_id != self.company_id
            for row in self.registrations
        ):
            raise OnboardingError("FOREIGN_PROVIDER_REGISTRATION")


@dataclass(frozen=True)
class PinnedOnboarding:
    """Host-controlled expected revision/digest, NOT the provider's own claim."""

    project_id: str
    company_id: str
    expected_revision: int
    expected_digest: str
    purpose: str = "SYNTHETIC_TEST_ONLY"

    def __post_init__(self) -> None:
        _id(self.project_id, "project_id")
        _id(self.company_id, "company_id")
        if type(self.expected_revision) is not int or self.expected_revision < 1:
            raise OnboardingError("INVALID_PINNED_REVISION")
        if type(self.expected_digest) is not str or not _HASH.fullmatch(self.expected_digest):
            raise OnboardingError("INVALID_PINNED_DIGEST")
        if self.purpose != "SYNTHETIC_TEST_ONLY":
            raise OnboardingError("UNSUPPORTED_PINNED_PURPOSE")


@dataclass(frozen=True)
class ProviderEndpoint:
    """Host-selected client. Its provider_id is DECLARED, never authenticated."""

    provider_id: str
    role: str
    api_version: str
    client: object
    assurance: str = ASSURANCE

    def __post_init__(self) -> None:
        _id(self.provider_id, "provider_id")
        if self.role not in ROLES:
            raise OnboardingError("INVALID_ENDPOINT_ROLE")
        if self.api_version != API_VERSION or self.assurance != ASSURANCE:
            raise OnboardingError("UNSUPPORTED_ENDPOINT_CONTRACT")
        if not callable(getattr(self.client, _METHOD[self.role], None)):
            raise OnboardingError("ENDPOINT_METHOD_NOT_IMPLEMENTED")


@dataclass(frozen=True)
class OnboardingReceipt:
    status: str
    project_id: str
    company_id: str
    expected_revision: int
    registry_digest: str
    providers: tuple[tuple[str, str], ...]
    review_receipt: ReviewReceipt
    real_provider_connected: bool = False
    real_enterprise_authenticated: bool = False
    real_document_authenticated: bool = False
    real_reviewer_authorized: bool = False
    decision_authority: bool = False
    production_authorized: bool = False
    operational_path: str = "FORBIDDEN"


def fingerprint_provider_snapshot(snapshot: OnboardingSnapshot) -> str:
    """Configuration digest, not a cryptographic trust anchor or signature."""
    if type(snapshot) is not OnboardingSnapshot:
        raise OnboardingError("INVALID_PROVIDER_SNAPSHOT")
    payload = {
        "purpose": snapshot.purpose,
        "policy_version": snapshot.policy_version,
        "project_id": snapshot.project_id,
        "company_id": snapshot.company_id,
        "revision": snapshot.revision,
        "registrations": [
            {
                "role": row.role,
                "provider_id": row.provider_id,
                "project_id": row.project_id,
                "company_id": row.company_id,
                "integration_ref": row.integration_ref,
                "api_version": row.api_version,
                "valid_from": row.valid_from.astimezone(timezone.utc).isoformat(),
                "valid_to": row.valid_to.astimezone(timezone.utc).isoformat(),
                "enabled": row.enabled,
                "assurance": row.assurance,
            }
            for row in snapshot.registrations
        ],
    }
    return sha256(_canonical(payload)).hexdigest()


def _get_snapshot(
    *, pin: PinnedOnboarding, request: ReviewRequest,
    source: object, endpoints: Mapping[str, ProviderEndpoint],
) -> OnboardingSnapshot:
    lookup = getattr(source, "get_provider_snapshot", None)
    if not callable(lookup):
        raise OnboardingError("REGISTRY_SOURCE_REQUIRED")
    snapshot = lookup(pin.project_id, pin.company_id, request.reviewed_at)
    if type(snapshot) is not OnboardingSnapshot:
        raise OnboardingError("INVALID_PROVIDER_REGISTRY_RESPONSE")
    if (
        snapshot.project_id != pin.project_id
        or snapshot.company_id != pin.company_id
        or snapshot.project_id != request.project_id
        or snapshot.company_id != request.company_id
    ):
        raise OnboardingError("ONBOARDING_TENANT_MISMATCH")
    if snapshot.revision != pin.expected_revision:
        raise OnboardingError("ONBOARDING_STALE_OR_REVOKED_REVISION")
    if fingerprint_provider_snapshot(snapshot) != pin.expected_digest:
        raise OnboardingError("ONBOARDING_REGISTRY_DIGEST_CHANGED")
    for row in snapshot.registrations:
        if not row.enabled:
            raise OnboardingError("ONBOARDING_PROVIDER_DISABLED:" + row.role)
        if not (row.valid_from <= request.reviewed_at < row.valid_to):
            raise OnboardingError("ONBOARDING_PROVIDER_EXPIRED:" + row.role)
        endpoint = endpoints[row.role]
        if (
            endpoint.provider_id != row.provider_id
            or endpoint.role != row.role
            or endpoint.api_version != row.api_version
            or endpoint.assurance != row.assurance
        ):
            raise OnboardingError("ONBOARDING_PROVIDER_ENDPOINT_MISMATCH:" + row.role)
    return snapshot


def review_with_onboarded_providers(
    *,
    prepared: PreparedExternalCase,
    request: ReviewRequest,
    pin: PinnedOnboarding,
    registry_source: object,
    endpoints: Mapping[str, ProviderEndpoint],
) -> OnboardingReceipt:
    """Check pinned configuration before/after every F6.3 provider call.

    The caller must obtain the pin and provider registry from independent,
    authenticated external sources in any real deployment. There is NO such
    source in this synthetic-only example. F6.3 continues to own the
    documentary double-read checks and all downstream authority stays denied.
    """
    if type(prepared) is not PreparedExternalCase or type(request) is not ReviewRequest:
        raise OnboardingError("INVALID_ONBOARDING_CASE")
    if type(pin) is not PinnedOnboarding:
        raise OnboardingError("PINNED_PROVIDER_CONFIGURATION_REQUIRED")
    if pin.project_id != request.project_id or pin.company_id != request.company_id:
        raise OnboardingError("PINNED_PROVIDER_TENANT_MISMATCH")
    if not isinstance(endpoints, Mapping) or set(endpoints) != set(ROLES):
        raise OnboardingError("MISSING_OR_UNDECLARED_PROVIDER_ENDPOINT")
    if any(type(endpoints[role]) is not ProviderEndpoint for role in ROLES):
        raise OnboardingError("INVALID_PROVIDER_ENDPOINT")
    for role in ROLES:
        if endpoints[role].role != role:
            raise OnboardingError("ONBOARDING_ROLE_CONFUSION")
    if not callable(getattr(registry_source, "get_provider_snapshot", None)):
        raise OnboardingError("REGISTRY_SOURCE_REQUIRED")
    baseline = _get_snapshot(
        pin=pin, request=request, source=registry_source, endpoints=endpoints,
    )
    def guard(role: str, call: Callable[[], object]) -> object:
        current = _get_snapshot(
            pin=pin, request=request, source=registry_source, endpoints=endpoints,
        )
        if current != baseline:
            raise OnboardingError("ONBOARDING_CONFIG_CHANGED_DURING_REVIEW")
        result = call()
        current = _get_snapshot(
            pin=pin, request=request, source=registry_source, endpoints=endpoints,
        )
        if current != baseline:
            raise OnboardingError("ONBOARDING_CONFIG_CHANGED_DURING_REVIEW")
        return result

    class IdentityAdapter:
        def resolve_identity(self, session_ref, at):
            return guard("IDENTITY", lambda: endpoints["IDENTITY"].client.resolve_identity(session_ref, at))

    class DocumentAdapter:
        def load_document(self, project_id, company_id, document_ref, at):
            return guard("DOCUMENT", lambda: endpoints["DOCUMENT"].client.load_document(
                project_id, company_id, document_ref, at,
            ))

    class PermissionAdapter:
        def resolve_permission(self, project_id, company_id, subject_id, document_ref, at):
            return guard("REVIEW_PERMISSION", lambda: endpoints["REVIEW_PERMISSION"].client.resolve_permission(
                project_id, company_id, subject_id, document_ref, at,
            ))

    checked = review_synthetic_boundary(
        prepared=prepared, request=request,
        identity_source=IdentityAdapter(),
        document_source=DocumentAdapter(),
        permission_source=PermissionAdapter(),
    )
    final = _get_snapshot(
        pin=pin, request=request, source=registry_source, endpoints=endpoints,
    )
    if final != baseline:
        raise OnboardingError("ONBOARDING_CONFIG_CHANGED_AFTER_REVIEW")
    if (
        checked.status != "SYNTHETIC_BOUNDARY_CHECKS_PASSED"
        or checked.production_authorized is not False
        or checked.operational_path != "FORBIDDEN"
        or checked.decision_authority is not False
    ):
        raise OnboardingError("ONBOARDING_REVIEW_IS_NOT_SYNTHETIC")
    return OnboardingReceipt(
        status="SYNTHETIC_PROVIDER_ONBOARDING_READY",
        project_id=pin.project_id,
        company_id=pin.company_id,
        expected_revision=pin.expected_revision,
        registry_digest=pin.expected_digest,
        providers=tuple((row.role, row.provider_id) for row in baseline.registrations),
        review_receipt=checked,
    )


__all__ = (
    "OnboardingError", "ProviderRegistration", "OnboardingSnapshot",
    "PinnedOnboarding", "ProviderEndpoint", "OnboardingReceipt",
    "fingerprint_provider_snapshot", "review_with_onboarded_providers",
)
