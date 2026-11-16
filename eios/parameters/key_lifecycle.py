"""F3.4: verify external governance of issuer keys before F3.3 manifests.

No private keys, enrolment decisions, registry database, approval authority, or
operational decisions are created here. A host MUST supply separately:
(1) a pretrusted company governance verification key,
(2) a host-owned signed lifecycle-history repository,
(3) an INDEPENDENT durable revision+digest checkpoint.
Fail closed when any source is absent, inconsistent, stale or revoked.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from hashlib import sha256
from hmac import compare_digest
import json
from typing import Literal, Protocol

from .signed_version_source import (
    Ed25519VerifiedParameterVersionSource,
    SignedVersionRecordRepository,
    TrustedIssuerPublicKey,
    _id, _signed_stamp, _stamp, _unique_pairs, _reject_constant,
)
from .version_binding import ParameterVersionBindingError, ParameterVersionManifest

SCHEMA = "EIOS-ISSUER-KEY-LIFECYCLE/v0.1"
_MAX_BYTES = 65536
_MAX_EVENTS = 512
_ACTIONS = frozenset({"ENROLL", "AUTHORIZE", "RENEW", "SUSPEND", "REVOKE"})
_ENVELOPE = frozenset({
    "schema", "company_id", "issuer_id", "governance_key_id",
    "revision", "issued_at", "expires_at", "events",
})
_EVENT_FIELDS = frozenset({
    "sequence", "action", "key_id", "at", "approval_ref",
    "public_key_hex", "valid_from", "valid_to",
})


def _fail(code: str, reason: str) -> None:
    raise ParameterVersionBindingError(code, reason)


@dataclass(frozen=True, slots=True)
class GovernanceVerificationKey:
    """Provisioned outside all EIOS files and version documents."""

    company_id: str
    governance_key_id: str
    public_key_bytes: bytes
    valid_from: datetime
    valid_to: datetime


@dataclass(frozen=True, slots=True)
class SignedKeyLifecycleHistory:
    """Exact, canonical serialized event history and detached Ed25519 signature."""

    payload: bytes
    signature: bytes


@dataclass(frozen=True, slots=True)
class IndependentLifecycleCheckpoint:
    """Trusted independently held latest revision AND payload commitment."""

    company_id: str
    issuer_id: str
    revision: int
    payload_sha256: str


class KeyLifecycleHistoryRepository(Protocol):
    """External read-only history store, not EIOS parameter storage."""

    def get_signed_history(
        self, company_id: str, issuer_id: str,
    ) -> SignedKeyLifecycleHistory | None: ...


class TrustedLifecycleCheckpointSource(Protocol):
    """External monotonic checkpoint distinct from history and user payload."""

    def get_checkpoint(
        self, company_id: str, issuer_id: str,
    ) -> IndependentLifecycleCheckpoint | None: ...


@dataclass(frozen=True, slots=True)
class _KeyState:
    key_id: str
    public_key_bytes: bytes
    valid_from: datetime
    valid_to: datetime
    status: Literal["PENDING", "ACTIVE", "SUSPENDED", "REVOKED"]


@dataclass(frozen=True, slots=True)
class _Admission:
    trusted_key: TrustedIssuerPublicKey
    revision: int
    payload_sha256: str


class GovernedParameterVersionSource:
    """F2.4 version-source port using an independently checkpointed key history.

    Each manifest read revalidates the signed governance history and current
    checkpoint before AND after F3.3's Ed25519 content-signature verification.
    F2.4 itself reads the manifest twice around Centre selection. No cache.
    """

    decision_authority = False
    operational_path = "FORBIDDEN"
    source_authentication = "UNATTESTED_UNTIL_MANIFEST_RETURNED"

    def __init__(
        self, *,
        company_id: str,
        issuer_id: str,
        key_id: str,
        governance_key: GovernanceVerificationKey,
        history_repository: KeyLifecycleHistoryRepository,
        checkpoint_source: TrustedLifecycleCheckpointSource,
        record_repository: SignedVersionRecordRepository,
        verification_at: datetime,
    ) -> None:
        self._company = _id(company_id, "company_id")
        self._issuer = _id(issuer_id, "issuer_id")
        self._key_id = _id(key_id, "key_id")
        if not isinstance(governance_key, GovernanceVerificationKey):
            _fail("GOVERNANCE_TRUST_MISSING", "Independent governance trust anchor is required")
        if governance_key.company_id != company_id:
            _fail("GOVERNANCE_COMPANY_MISMATCH", "Governance key belongs to another company")
        _id(governance_key.governance_key_id, "governance_key_id")
        if (
            type(governance_key.public_key_bytes) is not bytes
            or len(governance_key.public_key_bytes) != 32
        ):
            _fail("INVALID_GOVERNANCE_TRUST", "Governance Ed25519 public key must be 32 bytes")
        _stamp(governance_key.valid_from, "valid_from")
        _stamp(governance_key.valid_to, "valid_to")
        if governance_key.valid_from >= governance_key.valid_to:
            _fail("INVALID_GOVERNANCE_TRUST", "Governance validity interval invalid")
        _stamp(verification_at, "verification_at")
        if not callable(getattr(history_repository, "get_signed_history", None)):
            _fail("HISTORY_SOURCE_MISSING", "Independent signed history repository missing")
        if not callable(getattr(checkpoint_source, "get_checkpoint", None)):
            _fail("CHECKPOINT_SOURCE_MISSING", "Trusted high-watermark checkpoint missing")
        if not callable(getattr(record_repository, "get_signed_record", None)):
            _fail("VERSION_SOURCE_UNAVAILABLE", "Signed manifest repository missing")
        self._root = governance_key
        self._history = history_repository
        self._checkpoint = checkpoint_source
        self._records = record_repository
        self._now = verification_at

    def _read_admission(self) -> _Admission:
        if not self._root.valid_from <= self._now < self._root.valid_to:
            _fail("GOVERNANCE_KEY_INACTIVE", "Governance verification key is not currently valid")
        checkpoint = self._checkpoint.get_checkpoint(self._company, self._issuer)
        if not isinstance(checkpoint, IndependentLifecycleCheckpoint):
            _fail("CHECKPOINT_UNAVAILABLE", "Independent latest-revision checkpoint required")
        if checkpoint.company_id != self._company or checkpoint.issuer_id != self._issuer:
            _fail("CHECKPOINT_SCOPE_MISMATCH", "Checkpoint belongs to another company/issuer")
        if (
            type(checkpoint.revision) is not int or checkpoint.revision < 1
            or not isinstance(checkpoint.payload_sha256, str)
            or len(checkpoint.payload_sha256) != 64
            or any(ch not in "0123456789abcdef" for ch in checkpoint.payload_sha256)
        ):
            _fail("INVALID_CHECKPOINT", "Checkpoint revision and digest must be canonical")

        signed = self._history.get_signed_history(self._company, self._issuer)
        if signed is None:
            _fail("LIFECYCLE_HISTORY_UNAVAILABLE", "Signed lifecycle history missing")
        if (
            not isinstance(signed, SignedKeyLifecycleHistory)
            or type(signed.payload) is not bytes
            or type(signed.signature) is not bytes
            or not 1 <= len(signed.payload) <= _MAX_BYTES
            or len(signed.signature) != 64
        ):
            _fail("INVALID_LIFECYCLE_HISTORY", "Signed lifecycle envelope is malformed")
        actual_digest = sha256(signed.payload).hexdigest()
        if not compare_digest(actual_digest, checkpoint.payload_sha256):
            _fail("CHECKPOINT_MISMATCH", "Signed history not identical to trusted checkpoint")

        # Do not parse or trust a governance history before signature verification.
        from cryptography.exceptions import InvalidSignature
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
        try:
            Ed25519PublicKey.from_public_bytes(
                self._root.public_key_bytes
            ).verify(signed.signature, signed.payload)
        except (InvalidSignature, ValueError) as exc:
            raise ParameterVersionBindingError(
                "LIFECYCLE_SIGNATURE_INVALID", "History signature did not verify",
            ) from exc

        try:
            content = json.loads(
                signed.payload.decode("utf-8"),
                object_pairs_hook=_unique_pairs, parse_constant=_reject_constant,
            )
            if not isinstance(content, dict) or set(content) != _ENVELOPE:
                _fail("INVALID_LIFECYCLE_HISTORY", "Missing or additional lifecycle fields")
            if (
                json.dumps(
                    content, sort_keys=True, separators=(",", ":"),
                    ensure_ascii=False, allow_nan=False,
                ).encode("utf-8") != signed.payload
            ):
                _fail("INVALID_LIFECYCLE_HISTORY", "Lifecycle JSON must be canonical")
        except ParameterVersionBindingError:
            # Preserve precise fail-closed codes (e.g. duplicate JSON keys).
            raise
        except (UnicodeDecodeError, ValueError, TypeError, OverflowError) as exc:
            raise ParameterVersionBindingError(
                "INVALID_LIFECYCLE_HISTORY", "Canonical signed JSON invalid",
            ) from exc

        if (
            content["schema"] != SCHEMA
            or _id(content["company_id"], "company_id") != self._company
            or _id(content["issuer_id"], "issuer_id") != self._issuer
            or _id(content["governance_key_id"], "governance_key_id")
                != self._root.governance_key_id
        ):
            _fail("LIFECYCLE_SCOPE_MISMATCH", "History not bound to selected governance authority")
        issued_at = _signed_stamp(content["issued_at"], "issued_at")
        expires_at = _signed_stamp(content["expires_at"], "expires_at")
        if (
            not self._root.valid_from <= issued_at < self._root.valid_to
            or issued_at > self._now
            or not issued_at < expires_at
            or not self._now < expires_at
        ):
            _fail("LIFECYCLE_STALE", "History expired, future-dated or outside governance validity")
        events = content["events"]
        if (
            type(content["revision"]) is not int
            or not isinstance(events, list) or not 1 <= len(events) <= _MAX_EVENTS
            or content["revision"] != len(events)
        ):
            _fail("INVALID_LIFECYCLE_HISTORY", "Revision must equal complete event count")
        if content["revision"] != checkpoint.revision:
            _fail("CHECKPOINT_REVISION_MISMATCH", "Signed revision is not the trusted latest revision")

        state: dict[str, _KeyState] = {}
        last_at: datetime | None = None
        for index, event in enumerate(events, start=1):
            if not isinstance(event, dict) or set(event) != _EVENT_FIELDS:
                _fail("INVALID_LIFECYCLE_EVENT", "Event fields are incomplete/extra")
            if type(event["sequence"]) is not int or event["sequence"] != index:
                _fail("INVALID_LIFECYCLE_EVENT", "Events must have consecutive sequence numbers")
            action = event["action"]
            if not isinstance(action, str) or action not in _ACTIONS:
                _fail("INVALID_LIFECYCLE_EVENT", "Unknown lifecycle action")
            key_id = _id(event["key_id"], "key_id")
            at = _signed_stamp(event["at"], "event.at")
            if at > issued_at or (last_at is not None and at < last_at):
                _fail("INVALID_LIFECYCLE_EVENT", "Event clock is future-dated or out of sequence")
            last_at = at
            approval = event["approval_ref"]
            public = event["public_key_hex"]
            valid_from = event["valid_from"]
            valid_to = event["valid_to"]
            previous = state.get(key_id)
            if action == "ENROLL":
                if previous is not None or approval is not None:
                    _fail("INVALID_LIFECYCLE_TRANSITION", "Enrollment must be new and pending approval")
                if (
                    not isinstance(public, str) or len(public) != 64
                    or any(ch not in "0123456789abcdef" for ch in public)
                ):
                    _fail("INVALID_LIFECYCLE_EVENT", "Enrollment public key must be canonical Ed25519 hex")
                start = _signed_stamp(valid_from, "valid_from")
                end = _signed_stamp(valid_to, "valid_to")
                if start >= end or at > end:
                    _fail("INVALID_LIFECYCLE_EVENT", "Enrollment validity must be nonempty")
                state[key_id] = _KeyState(
                    key_id, bytes.fromhex(public), start, end, "PENDING",
                )
                continue
            if previous is None or public is not None or valid_from is not None:
                _fail("INVALID_LIFECYCLE_TRANSITION", "Key must be enrolled and immutable")
            _id(approval, "approval_ref")
            if action == "AUTHORIZE":
                if previous.status not in ("PENDING", "SUSPENDED") or valid_to is not None:
                    _fail("INVALID_LIFECYCLE_TRANSITION", "Authorization requires pending/suspended key")
                if at >= previous.valid_to:
                    _fail("INVALID_LIFECYCLE_TRANSITION", "Expired key cannot be authorized")
                state[key_id] = _KeyState(
                    key_id, previous.public_key_bytes, previous.valid_from,
                    previous.valid_to, "ACTIVE",
                )
            elif action == "RENEW":
                if previous.status != "ACTIVE":
                    _fail("INVALID_LIFECYCLE_TRANSITION", "Only active key may be renewed")
                end = _signed_stamp(valid_to, "valid_to")
                if at >= previous.valid_to or end <= previous.valid_to:
                    _fail("INVALID_LIFECYCLE_TRANSITION", "Renewal must extend an unexpired active key")
                state[key_id] = _KeyState(
                    key_id, previous.public_key_bytes, previous.valid_from, end,
                    "ACTIVE",
                )
            elif action == "SUSPEND":
                if previous.status != "ACTIVE" or valid_to is not None:
                    _fail("INVALID_LIFECYCLE_TRANSITION", "Only an active key may be suspended")
                state[key_id] = _KeyState(
                    key_id, previous.public_key_bytes, previous.valid_from,
                    previous.valid_to, "SUSPENDED",
                )
            elif action == "REVOKE":
                if previous.status == "REVOKED" or valid_to is not None:
                    _fail("INVALID_LIFECYCLE_TRANSITION", "Revocation is terminal and irreversible")
                state[key_id] = _KeyState(
                    key_id, previous.public_key_bytes, previous.valid_from,
                    previous.valid_to, "REVOKED",
                )

        key = state.get(self._key_id)
        if key is None:
            _fail("KEY_NOT_ENROLLED", "Requested key absent from signed governance history")
        if key.status == "REVOKED":
            _fail("KEY_REVOKED", "Key has been revoked; historical signatures no longer admitted")
        if key.status != "ACTIVE":
            _fail("KEY_NOT_AUTHORIZED", "Key is not currently approved and active")
        if not key.valid_from <= self._now < key.valid_to:
            _fail("KEY_NOT_VALID_NOW", "Approved key is not valid at verification time")
        return _Admission(
            trusted_key=TrustedIssuerPublicKey(
                company_id=self._company,
                issuer_id=self._issuer,
                key_id=self._key_id,
                public_key_bytes=key.public_key_bytes,
                valid_from=key.valid_from,
                valid_to=key.valid_to,
            ),
            revision=checkpoint.revision,
            payload_sha256=actual_digest,
        )

    def get_version_manifest(
        self, company_id: str, parameters_version: str, effective_at: datetime,
    ) -> ParameterVersionManifest | None:
        if company_id != self._company:
            _fail("COMPANY_SCOPE_MISMATCH", "Caller requested a different company")
        first = self._read_admission()
        source = Ed25519VerifiedParameterVersionSource(
            record_repository=self._records, trusted_key=first.trusted_key,
            expected_company_id=self._company, verification_at=self._now,
        )
        # F3.3 checks the exact signed manifest, not a self-declared source.
        result = source.get_version_manifest(company_id, parameters_version, effective_at)
        second = self._read_admission()
        if first != second:
            _fail("KEY_LIFECYCLE_CHANGED", "Key trust status changed during manifest read")
        return result


__all__ = [
    "SCHEMA", "GovernanceVerificationKey", "SignedKeyLifecycleHistory",
    "IndependentLifecycleCheckpoint", "KeyLifecycleHistoryRepository",
    "TrustedLifecycleCheckpointSource", "GovernedParameterVersionSource",
]
