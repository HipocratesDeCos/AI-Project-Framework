"""F6.4 — illustrative write-once local document custody outside EIOS.

The host MUST provision and protect the directory, trusted digest and provider
wiring. This is a synthetic, single-host demonstration, NOT a secure enterprise
vault, encryption service, IdP, legal archive or production repository.

The file key contains only a digest of the explicitly scoped identifiers.
Each complete record is written with O_CREAT|O_EXCL and revalidated on load.
SHA-256 is a consistency check against a HOST-SUPPLIED expected digest;
it does not authenticate the issuer or prevent malicious rewrites by an
attacker who controls the host or the whole directory.
"""
from __future__ import annotations

import base64
from dataclasses import dataclass
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import stat

from eios_evidence_boundary_example.review import (
    ASSURANCE, DocumentRecord, MAX_DOCUMENT_BYTES,
)

_IDENTIFIER = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}\Z")
_HASH = re.compile(r"[0-9a-f]{64}\Z")
_FIELDS = frozenset({
    "format_version", "project_id", "company_id", "source_id",
    "data_snapshot_id", "document_ref", "sha256", "content_b64",
    "assurance",
})
MAX_RECORD_BYTES = 96_000


class CustodyError(ValueError):
    """The declared, write-once document does not match the trusted binding."""


def _identifier(value: object, name: str, limit: int = 128) -> None:
    if (
        type(value) is not str or len(value) > limit
        or not _IDENTIFIER.fullmatch(value)
    ):
        raise CustodyError("INVALID_CUSTODY_ID:" + name)


@dataclass(frozen=True)
class DocumentBinding:
    """Host-furnished expected scope. Never copied from stored JSON."""

    project_id: str
    company_id: str
    source_id: str
    data_snapshot_id: str
    document_ref: str
    expected_document_sha256: str
    purpose: str = "SYNTHETIC_TEST_ONLY"

    def __post_init__(self):
        for name in (
            "project_id", "company_id", "source_id",
            "data_snapshot_id", "document_ref",
        ):
            _identifier(getattr(self, name), name)
        if (
            type(self.expected_document_sha256) is not str
            or not _HASH.fullmatch(self.expected_document_sha256)
        ):
            raise CustodyError("INVALID_EXPECTED_DOCUMENT_DIGEST")
        if self.purpose != "SYNTHETIC_TEST_ONLY":
            raise CustodyError("NON_SYNTHETIC_CUSTODY_FORBIDDEN")


def _canonical(value: object) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True,
        separators=(",", ":"), allow_nan=False,
    ).encode("utf-8")


def _unique_pairs(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise CustodyError("DUPLICATE_CUSTODY_KEY")
        result[key] = value
    return result


class SyntheticCustodyVault:
    """Write-once local record storage; external host owns folder permissions.

    Each file is keyed by the full record identity (not by user-supplied paths).
    The expected digest is NOT part of the key: a different digest cannot
    silently create a new version under the same document reference.
    """

    def __init__(self, root: Path):
        if not isinstance(root, Path):
            raise CustodyError("EXPLICIT_EXISTING_CUSTODY_ROOT_REQUIRED")
        if root.is_symlink() or not root.is_dir():
            raise CustodyError("UNTRUSTED_CUSTODY_ROOT")
        self.root = root.resolve(strict=True)

    def _path(self, binding: DocumentBinding) -> Path:
        if type(binding) is not DocumentBinding:
            raise CustodyError("INVALID_CUSTODY_BINDING")
        scope = {
            key: getattr(binding, key)
            for key in (
                "project_id", "company_id", "source_id",
                "data_snapshot_id", "document_ref",
            )
        }
        digest = sha256(_canonical(scope)).hexdigest()
        return self.root / (digest + ".json")

    def record_path_for_tests(self, binding: DocumentBinding) -> Path:
        """Expose test locator only; no caller-specified paths accepted."""
        return self._path(binding)

    def store_once(self, binding: DocumentBinding, content: bytes) -> None:
        """Persist a single scoped record; duplicate write is always rejected."""
        path = self._path(binding)
        if type(content) is not bytes or not (0 < len(content) <= MAX_DOCUMENT_BYTES):
            raise CustodyError("INVALID_CUSTODY_DOCUMENT_BYTES")
        if sha256(content).hexdigest() != binding.expected_document_sha256:
            raise CustodyError("CUSTODY_SOURCE_DIGEST_MISMATCH")
        record = {
            "format_version": 1,
            "project_id": binding.project_id,
            "company_id": binding.company_id,
            "source_id": binding.source_id,
            "data_snapshot_id": binding.data_snapshot_id,
            "document_ref": binding.document_ref,
            "sha256": binding.expected_document_sha256,
            "content_b64": base64.b64encode(content).decode("ascii"),
            "assurance": ASSURANCE,
        }
        encoded = _canonical(record)
        if len(encoded) > MAX_RECORD_BYTES:
            raise CustodyError("CUSTODY_RECORD_TOO_LARGE")
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_BINARY", 0)
        # A same-name write (even with identical bytes) is never an update.
        try:
            descriptor = os.open(path, flags, 0o600)
        except FileExistsError as exc:
            raise CustodyError("CUSTODY_RECORD_ALREADY_EXISTS") from exc
        try:
            with os.fdopen(descriptor, "wb") as stream:
                descriptor = -1
                stream.write(encoded)
                stream.flush()
                os.fsync(stream.fileno())
        except Exception:
            if descriptor >= 0:
                os.close(descriptor)
            # Partial writes remain unusable. A trusted host must handle crash
            # recovery and ensure no other writers can exploit the directory.
            try:
                path.unlink()
            except OSError:
                pass
            raise

    def load_verified(self, binding: DocumentBinding) -> DocumentRecord:
        """Read record with anti-symlink checks and verify pinned exact bytes."""
        path = self._path(binding)
        if path.is_symlink():
            raise CustodyError("CUSTODY_SYMLINK_NOT_ALLOWED")
        flags = os.O_RDONLY | getattr(os, "O_BINARY", 0)
        flags |= getattr(os, "O_NOFOLLOW", 0)
        try:
            fd = os.open(path, flags)
        except OSError as exc:
            raise CustodyError("CUSTODY_RECORD_NOT_AVAILABLE") from exc
        with os.fdopen(fd, "rb") as stream:
            metadata = os.fstat(stream.fileno())
            if not stat.S_ISREG(metadata.st_mode) or metadata.st_nlink != 1:
                raise CustodyError("CUSTODY_UNSAFE_RECORD_TYPE")
            if not (0 < metadata.st_size <= MAX_RECORD_BYTES):
                raise CustodyError("CUSTODY_RECORD_SIZE_INVALID")
            raw = stream.read(MAX_RECORD_BYTES + 1)
        if len(raw) > MAX_RECORD_BYTES:
            raise CustodyError("CUSTODY_RECORD_SIZE_INVALID")
        try:
            record = json.loads(raw.decode("utf-8"), object_pairs_hook=_unique_pairs)
        except (ValueError, UnicodeError) as exc:
            raise CustodyError("CUSTODY_INVALID_RECORD") from exc
        if type(record) is not dict or set(record) != _FIELDS:
            raise CustodyError("CUSTODY_SCHEMA_MISMATCH")
        if type(record["format_version"]) is not int or record["format_version"] != 1:
            raise CustodyError("CUSTODY_FORMAT_MISMATCH")
        if record["assurance"] != ASSURANCE:
            raise CustodyError("CUSTODY_PROVENANCE_PROMOTION")
        for name in (
            "project_id", "company_id", "source_id",
            "data_snapshot_id", "document_ref",
        ):
            if record[name] != getattr(binding, name):
                raise CustodyError("CUSTODY_SCOPE_MISMATCH:" + name)
        if record["sha256"] != binding.expected_document_sha256:
            raise CustodyError("CUSTODY_PINNED_DIGEST_MISMATCH")
        if type(record["content_b64"]) is not str or len(record["content_b64"]) > MAX_RECORD_BYTES:
            raise CustodyError("CUSTODY_INVALID_ENCODING")
        try:
            content = base64.b64decode(record["content_b64"], validate=True)
        except (ValueError, base64.binascii.Error) as exc:
            raise CustodyError("CUSTODY_INVALID_ENCODING") from exc
        if not (0 < len(content) <= MAX_DOCUMENT_BYTES):
            raise CustodyError("CUSTODY_INVALID_DOCUMENT_SIZE")
        if sha256(content).hexdigest() != binding.expected_document_sha256:
            raise CustodyError("CUSTODY_CONTENT_TAMPERED")
        return DocumentRecord(
            project_id=binding.project_id, company_id=binding.company_id,
            source_id=binding.source_id,
            data_snapshot_id=binding.data_snapshot_id,
            document_ref=binding.document_ref,
            document_sha256=binding.expected_document_sha256,
            content=content,
        )


@dataclass(frozen=True)
class VaultDocumentProvider:
    """F6.3 `load_document` port backed by F6.4 synthetic local custody."""

    vault: SyntheticCustodyVault
    binding: DocumentBinding

    def load_document(
        self, project_id: str, company_id: str,
        document_ref: str, reviewed_at: object,
    ) -> DocumentRecord:
        if type(self.vault) is not SyntheticCustodyVault or type(self.binding) is not DocumentBinding:
            raise CustodyError("INVALID_VAULT_PROVIDER")
        if (
            project_id != self.binding.project_id
            or company_id != self.binding.company_id
            or document_ref != self.binding.document_ref
        ):
            raise CustodyError("CUSTODY_PROVIDER_SCOPE_MISMATCH")
        # No clock trust is conferred by this provider; F6.3 checks the host
        # request timestamp and the external identity/permission validity.
        return self.vault.load_verified(self.binding)


__all__ = (
    "CustodyError", "DocumentBinding", "SyntheticCustodyVault",
    "VaultDocumentProvider",
)
