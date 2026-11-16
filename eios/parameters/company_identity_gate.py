"""F3.5 — authenticated company/issuer authorization boundary for F2.4.

An EIOS document, user-supplied company_id, role label, or signature cannot
authenticate a company. This fail-closed application boundary requires trusted
host-owned identity, permission and governance-root services. Such services
are NOT implemented, configured or simulated as real in this repository.

No operational admission, identity creation, grants, key storage, persistence
or business decisions. Test doubles remain synthetic and test-only.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Mapping, Protocol

from eios.core.models import DecisionContext, Evidence

from .center import ParameterConfigurationCenter
from .key_lifecycle import (
    GovernanceVerificationKey, GovernedParameterVersionSource,
    KeyLifecycleHistoryRepository, TrustedLifecycleCheckpointSource,
)
from .signed_version_source import SignedVersionRecordRepository
from .version_binding import (
    ParameterVersionBindingError, VersionBoundParameterSelection,
    read_version_bound_parameter_selection,
)

READ_PERMISSION = "PARAMETER_VERSION_READ"


@dataclass(frozen=True, slots=True)
class AuthenticatedCompanyIdentity:
    """Verified *externally by the trusted host*, never client-supplied.

    The caller cannot create an identity merely by constructing this dataclass.
    Its provenance is only as strong as the independently configured provider.
    """

    company_id: str
    subject_id: str
    identity_provider_id: str
    identity_ref: str
    valid_from: datetime
    valid_to: datetime


class AuthenticatedCompanyIdentitySource(Protocol):
    """External IdP-backed session verifier; MUST reject unauthenticated refs."""

    def resolve_authenticated_identity(
        self, session_ref: str, verification_at: datetime,
    ) -> AuthenticatedCompanyIdentity | None: ...


@dataclass(frozen=True, slots=True)
class CompanyIssuerReadGrant:
    """External tenant-scoped authorization to read issuer-signed versions.

    This is NOT an EIOS grant-creation API or a user-asserted role.
    """

    company_id: str
    subject_id: str
    permission: str
    issuer_id: str
    key_id: str
    grant_ref: str
    valid_from: datetime
    valid_to: datetime


class CompanyIssuerAuthorizationSource(Protocol):
    """Host-owned permission service, distinct from identity and EIOS files."""

    def resolve_parameter_read_grant(
        self, company_id: str, subject_id: str, verification_at: datetime,
    ) -> CompanyIssuerReadGrant | None: ...


class TrustedCompanyGovernanceKeySource(Protocol):
    """Out-of-band trust store; MUST NOT read issuer key from signed payload."""

    def get_trusted_governance_key(
        self, company_id: str, verification_at: datetime,
    ) -> GovernanceVerificationKey | None: ...


@dataclass(frozen=True, slots=True)
class CompanyScopedVersionSelection:
    """Receipt for host-supplied identity+permission matching and F2.4 checks."""

    selection: VersionBoundParameterSelection
    company_id: str
    subject_id: str
    identity_ref: str
    grant_ref: str
    status: str = "HOST_IDENTITY_GRANT_AND_VERSION_MATCHED"
    authentication_boundary: str = "EXTERNAL_PROVIDER_RESPONSIBILITY"
    decision_authority: bool = False
    operational_path: str = "FORBIDDEN"


def _fail(code: str, message: str) -> None:
    raise ParameterVersionBindingError(code, message)


def _id(value: object, label: str) -> str:
    if (
        not isinstance(value, str) or not value
        or value != value.strip() or len(value) > 256
    ):
        _fail("INVALID_IDENTITY_SCOPE", label + " is not a canonical identity")
    return value


def _valid_window(start: datetime, end: datetime, now: datetime, label: str) -> None:
    if any(
        not isinstance(item, datetime) or item.utcoffset() is None
        for item in (start, end, now)
    ):
        _fail("INVALID_IDENTITY_WINDOW", label + " must use timezone-aware timestamps")
    if not start < end:
        _fail("INVALID_IDENTITY_WINDOW", label + " validity interval is invalid")
    if not start <= now < end:
        _fail("IDENTITY_OR_PERMISSION_EXPIRED", label + " is not active at verification time")


def _identity(
    identity_source: AuthenticatedCompanyIdentitySource,
    session_ref: str,
    expected_company_id: str,
    verification_at: datetime,
) -> AuthenticatedCompanyIdentity:
    record = identity_source.resolve_authenticated_identity(session_ref, verification_at)
    if not isinstance(record, AuthenticatedCompanyIdentity):
        _fail("IDENTITY_UNVERIFIED", "Trusted identity provider did not verify the session")
    for name in ("company_id", "subject_id", "identity_provider_id", "identity_ref"):
        _id(getattr(record, name), name)
    if record.company_id != expected_company_id:
        _fail("IDENTITY_COMPANY_MISMATCH", "Authenticated company differs from requested company")
    _valid_window(record.valid_from, record.valid_to, verification_at, "identity")
    return record


def _grant(
    grant_source: CompanyIssuerAuthorizationSource,
    identity: AuthenticatedCompanyIdentity,
    verification_at: datetime,
) -> CompanyIssuerReadGrant:
    record = grant_source.resolve_parameter_read_grant(
        identity.company_id, identity.subject_id, verification_at,
    )
    if not isinstance(record, CompanyIssuerReadGrant):
        _fail("COMPANY_GRANT_MISSING", "External company authorization was not provided")
    for name in ("company_id", "subject_id", "permission",
                 "issuer_id", "key_id", "grant_ref"):
        _id(getattr(record, name), name)
    if record.company_id != identity.company_id or record.subject_id != identity.subject_id:
        _fail("COMPANY_GRANT_SCOPE_MISMATCH", "Issuer permission belongs to another company/principal")
    if record.permission != READ_PERMISSION:
        _fail("COMPANY_PERMISSION_DENIED", "Issuer permission does not authorize parameter-version reads")
    _valid_window(record.valid_from, record.valid_to, verification_at, "grant")
    return record


def _root(
    root_source: TrustedCompanyGovernanceKeySource,
    company_id: str,
    verification_at: datetime,
) -> GovernanceVerificationKey:
    record = root_source.get_trusted_governance_key(company_id, verification_at)
    if not isinstance(record, GovernanceVerificationKey):
        _fail("COMPANY_TRUST_ROOT_MISSING", "Independent company governance root is unavailable")
    if record.company_id != company_id:
        _fail("COMPANY_TRUST_SCOPE_MISMATCH", "Governance root belongs to another company")
    # The F3.4 adapter validates key format and full time range.
    return record


def read_authenticated_company_parameter_selection(
    *,
    session_ref: str,
    requested_company_id: str,
    identity_source: AuthenticatedCompanyIdentitySource,
    authorization_source: CompanyIssuerAuthorizationSource,
    root_source: TrustedCompanyGovernanceKeySource,
    history_repository: KeyLifecycleHistoryRepository,
    checkpoint_source: TrustedLifecycleCheckpointSource,
    record_repository: SignedVersionRecordRepository,
    center: ParameterConfigurationCenter,
    context: DecisionContext,
    effective_at: datetime,
    verification_at: datetime,
    parameter_ids: tuple[str, ...],
    evidence_by_parameter: Mapping[str, Evidence],
) -> CompanyScopedVersionSelection:
    """Read company versions with external IdP+grant+key governance gates.

    session_ref is an opaque host session reference, NOT the client company's
    declared name. The external IdP authenticates it independently.
    requested_company_id is only an expected tenant; it never grants access.
    There is no bypass if identity, grant, root, history or evidence is absent.

    Identity, permission and root are re-read after F2.4. The F3.4 source
    independently validates the lifecycle history/checkpoint on each read.
    """
    _id(session_ref, "session_ref")
    _id(requested_company_id, "requested_company_id")
    if not isinstance(verification_at, datetime) or verification_at.utcoffset() is None:
        _fail("INVALID_IDENTITY_WINDOW", "Verification requires a trusted aware clock")
    if not isinstance(center, ParameterConfigurationCenter):
        _fail("INVALID_PARAMETER_CENTRE", "Canonical ParameterConfigurationCenter required")
    for source, method, code in (
        (identity_source, "resolve_authenticated_identity", "IDENTITY_SOURCE_MISSING"),
        (authorization_source, "resolve_parameter_read_grant", "AUTHORIZATION_SOURCE_MISSING"),
        (root_source, "get_trusted_governance_key", "COMPANY_TRUST_SOURCE_MISSING"),
    ):
        if not callable(getattr(source, method, None)):
            _fail(code, "External trusted provider is not configured")

    before_identity = _identity(
        identity_source, session_ref, requested_company_id, verification_at,
    )
    before_grant = _grant(authorization_source, before_identity, verification_at)
    before_root = _root(root_source, before_identity.company_id, verification_at)

    governed_source = GovernedParameterVersionSource(
        company_id=before_identity.company_id,
        issuer_id=before_grant.issuer_id,
        key_id=before_grant.key_id,
        governance_key=before_root,
        history_repository=history_repository,
        checkpoint_source=checkpoint_source,
        record_repository=record_repository,
        verification_at=verification_at,
    )
    selected = read_version_bound_parameter_selection(
        center=center,
        version_source=governed_source,
        company_id=before_identity.company_id,
        expected_company_id=before_identity.company_id,
        context=context,
        effective_at=effective_at,
        parameter_ids=parameter_ids,
        evidence_by_parameter=evidence_by_parameter,
    )

    after_identity = _identity(
        identity_source, session_ref, requested_company_id, verification_at,
    )
    after_grant = _grant(authorization_source, after_identity, verification_at)
    after_root = _root(root_source, after_identity.company_id, verification_at)
    if (
        before_identity != after_identity
        or before_grant != after_grant
        or before_root != after_root
    ):
        _fail(
            "COMPANY_AUTHORIZATION_CHANGED",
            "Identity, issuer permission or trusted governance root changed during selection",
        )
    return CompanyScopedVersionSelection(
        selection=selected, company_id=before_identity.company_id,
        subject_id=before_identity.subject_id,
        identity_ref=before_identity.identity_ref,
        grant_ref=before_grant.grant_ref,
    )


__all__ = [
    "READ_PERMISSION",
    "AuthenticatedCompanyIdentity", "AuthenticatedCompanyIdentitySource",
    "CompanyIssuerReadGrant", "CompanyIssuerAuthorizationSource",
    "TrustedCompanyGovernanceKeySource", "CompanyScopedVersionSelection",
    "read_authenticated_company_parameter_selection",
]
