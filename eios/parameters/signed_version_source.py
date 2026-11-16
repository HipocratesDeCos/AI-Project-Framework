"""F3.3: externally signed parameter-version manifest source (fail closed).

This is a verification adapter for the EXISTING F2.4 ParameterVersionSource
port, not a version store, a key registry, a document admission service or a
business decision authority. The host must provide a previously trusted,
company-scoped Ed25519 public key through a channel independent of the
signed record. No trust anchors, secrets or example production issuers ship.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
from typing import Protocol

from .version_binding import (
    ParameterVersionBindingError,
    ParameterVersionManifest,
)

SCHEMA = "EIOS-SIGNED-PARAMETER-VERSION/v0.1"
_MAX_PAYLOAD_BYTES = 16_384
_FIELDS = frozenset({
    "schema", "company_id", "issuer_id", "key_id",
    "parameters_version", "effective_at", "parameter_ids",
    "selection_fingerprint", "source_ref", "issued_at", "expires_at",
})


@dataclass(frozen=True, slots=True)
class SignedParameterVersionRecord:
    """Detached Ed25519 signature and its exact canonical signed payload."""

    payload: bytes
    signature: bytes


class SignedVersionRecordRepository(Protocol):
    """Host-owned read-only version-artifact retrieval; no writes or fallback."""

    def get_signed_record(
        self, company_id: str, parameters_version: str, effective_at: datetime,
    ) -> SignedParameterVersionRecord | None: ...


@dataclass(frozen=True, slots=True)
class TrustedIssuerPublicKey:
    """Out-of-band approved trust anchor for exactly one company and issuer.

    This MUST originate in a trusted deployment/key-management configuration,
    not in a user-uploaded file, an editable EIOS decision payload or a key
    embedded alongside a signed version record.
    """

    company_id: str
    issuer_id: str
    key_id: str
    public_key_bytes: bytes
    valid_from: datetime
    valid_to: datetime


def _fail(code: str, message: str) -> None:
    raise ParameterVersionBindingError(code, message)


def _id(value: object, label: str) -> str:
    if (
        not isinstance(value, str) or not value
        or value != value.strip() or len(value) > 256
    ):
        _fail("INVALID_SIGNED_RECORD", label + " is not a canonical identifier")
    return value


def _stamp(value: datetime, label: str) -> str:
    if not isinstance(value, datetime) or value.utcoffset() is None:
        _fail("INVALID_TRUST_SCOPE", label + " requires an aware datetime")
    return value.astimezone(timezone.utc).isoformat()


def _signed_stamp(raw: object, label: str) -> datetime:
    if not isinstance(raw, str):
        _fail("INVALID_SIGNED_RECORD", label + " must be canonical UTC")
    try:
        value = datetime.fromisoformat(raw)
    except (ValueError, OverflowError):
        _fail("INVALID_SIGNED_RECORD", label + " is not ISO timestamp")
    if value.utcoffset() is None or raw != value.astimezone(timezone.utc).isoformat():
        _fail("INVALID_SIGNED_RECORD", label + " must be canonical UTC")
    return value


def _unique_pairs(pairs: list[tuple[str, object]]) -> dict:
    out: dict = {}
    for key, value in pairs:
        if key in out:
            _fail("INVALID_SIGNED_RECORD", "Duplicate JSON member")
        out[key] = value
    return out


def _reject_constant(value: str) -> None:
    _fail("INVALID_SIGNED_RECORD", "Nonstandard JSON numeric value: " + value)


class Ed25519VerifiedParameterVersionSource:
    """Read-only F2.4 manifest source backed by a pre-signed external record.

    Signature verification proves the payload was signed by the configured
    public key's private counterpart. The host still owns key enrolment,
    issuer authorization, revocation, tenant authentication and document
    admission. A verified signature does NOT enable an operational decision.
    """

    decision_authority = False
    operational_path = "FORBIDDEN"
    source_authentication = "SIGNATURE_VERIFIED_AGAINST_SUPPLIED_TRUST_ANCHOR"

    def __init__(
        self, *,
        record_repository: SignedVersionRecordRepository,
        trusted_key: TrustedIssuerPublicKey,
        expected_company_id: str,
        verification_at: datetime,
    ) -> None:
        if not callable(getattr(record_repository, "get_signed_record", None)):
            _fail("REPOSITORY_UNAVAILABLE", "Signed record provider is required")
        if not isinstance(trusted_key, TrustedIssuerPublicKey):
            _fail("TRUST_ANCHOR_MISSING", "TrustedIssuerPublicKey must be provided by host")
        _id(expected_company_id, "expected_company_id")
        for name in ("company_id", "issuer_id", "key_id"):
            _id(getattr(trusted_key, name), name)
        if trusted_key.company_id != expected_company_id:
            _fail("TRUST_SCOPE_MISMATCH", "Trust key is bound to another company")
        if (
            not isinstance(trusted_key.public_key_bytes, bytes)
            or len(trusted_key.public_key_bytes) != 32
        ):
            _fail("INVALID_TRUST_ANCHOR", "Expected raw Ed25519 public key bytes")
        if _stamp(trusted_key.valid_from, "valid_from") >= _stamp(
            trusted_key.valid_to, "valid_to"
        ):
            _fail("INVALID_TRUST_ANCHOR", "Trust-key validity interval is invalid")
        _stamp(verification_at, "verification_at")
        self._repository = record_repository
        self._trusted = trusted_key
        self._company = expected_company_id
        self._verification_at = verification_at

    def get_version_manifest(
        self, company_id: str, parameters_version: str, effective_at: datetime,
    ) -> ParameterVersionManifest | None:
        _id(company_id, "company_id")
        _id(parameters_version, "parameters_version")
        if company_id != self._company:
            _fail("COMPANY_SCOPE_MISMATCH", "Requested company is not the trusted company")
        _stamp(effective_at, "effective_at")

        # Retrieval is from the independent host-owned repository, NEVER
        # from current ParameterConfigurationCenter reads or unsigned inputs.
        record = self._repository.get_signed_record(
            company_id, parameters_version, effective_at,
        )
        if record is None:
            return None
        if (
            not isinstance(record, SignedParameterVersionRecord)
            or not isinstance(record.payload, bytes)
            or not isinstance(record.signature, bytes)
            or not 1 <= len(record.payload) <= _MAX_PAYLOAD_BYTES
            or len(record.signature) != 64
        ):
            _fail("INVALID_SIGNED_RECORD", "Signed version record is malformed")

        # Import only when an explicit signed adapter is selected; the default
        # EIOS app remains usable without this optional security dependency.
        from cryptography.exceptions import InvalidSignature
        from cryptography.hazmat.primitives.asymmetric.ed25519 import (
            Ed25519PublicKey,
        )

        try:
            Ed25519PublicKey.from_public_bytes(
                self._trusted.public_key_bytes
            ).verify(record.signature, record.payload)
        except (InvalidSignature, ValueError) as exc:
            raise ParameterVersionBindingError(
                "SIGNATURE_INVALID", "Signed record did not verify against trusted key",
            ) from exc

        try:
            content = json.loads(
                record.payload.decode("utf-8"),
                object_pairs_hook=_unique_pairs,
                parse_constant=_reject_constant,
            )
        except (ValueError, UnicodeDecodeError) as exc:
            raise ParameterVersionBindingError(
                "INVALID_SIGNED_RECORD", "Signed JSON is not valid",
            ) from exc
        if not isinstance(content, dict) or set(content) != _FIELDS:
            _fail("INVALID_SIGNED_RECORD", "Signed record has missing or extra fields")
        try:
            canon = json.dumps(
                content, ensure_ascii=False, sort_keys=True, separators=(",", ":"),
                allow_nan=False,
            ).encode("utf-8")
        except (ValueError, TypeError, OverflowError) as exc:
            raise ParameterVersionBindingError(
                "INVALID_SIGNED_RECORD", "Signed record cannot be canonicalized",
            ) from exc
        if canon != record.payload or content["schema"] != SCHEMA:
            _fail("INVALID_SIGNED_RECORD", "Noncanonical or unexpected signed schema")

        if (
            _id(content["company_id"], "company_id") != company_id
            or _id(content["issuer_id"], "issuer_id") != self._trusted.issuer_id
            or _id(content["key_id"], "key_id") != self._trusted.key_id
            or _id(content["parameters_version"], "parameters_version")
                != parameters_version
        ):
            _fail("SIGNED_SCOPE_MISMATCH", "Signed identity differs from trusted scope")
        if _signed_stamp(content["effective_at"], "effective_at") != effective_at:
            _fail("SIGNED_CUTOFF_MISMATCH", "Signed cutoff differs from request")
        issued_at = _signed_stamp(content["issued_at"], "issued_at")
        expires_at = _signed_stamp(content["expires_at"], "expires_at")
        if (
            issued_at >= expires_at
            or issued_at > self._verification_at
            or not self._verification_at < expires_at
        ):
            _fail("SIGNED_RECORD_EXPIRED", "Signed record is not current at trusted verification time")
        if not (self._trusted.valid_from <= issued_at < self._trusted.valid_to):
            _fail("SIGNING_KEY_NOT_VALID", "Issuer key was not valid when record was signed")
        if (
            not isinstance(content["parameter_ids"], list)
            or not content["parameter_ids"]
            or any(not _id(v, "parameter_id") for v in content["parameter_ids"])
            or content["parameter_ids"] != sorted(set(content["parameter_ids"]))
        ):
            _fail("INVALID_SIGNED_RECORD", "Parameters must be a canonical sorted unique selection")
        digest = content["selection_fingerprint"]
        if (
            not isinstance(digest, str) or len(digest) != 64
            or any(ch not in "0123456789abcdef" for ch in digest)
        ):
            _fail("INVALID_SIGNED_RECORD", "Selection digest must be canonical SHA-256")
        _id(content["source_ref"], "source_ref")
        return ParameterVersionManifest(
            company_id=company_id,
            parameters_version=parameters_version,
            effective_at=effective_at,
            parameter_ids=tuple(content["parameter_ids"]),
            selection_fingerprint=digest,
            source_ref=content["source_ref"],
        )


__all__ = [
    "SCHEMA", "Ed25519VerifiedParameterVersionSource", "SignedParameterVersionRecord",
    "SignedVersionRecordRepository", "TrustedIssuerPublicKey",
]
