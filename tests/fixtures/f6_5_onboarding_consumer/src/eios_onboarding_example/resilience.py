"""F6.10 — idempotent retry safety for the synthetic lifecycle journal.

This module sits outside the canonical EIOS engine. It adds retry semantics on
top of F6.4 write-once custody and F6.9 lifecycle events without weakening
either contract.

A retry of the exact same lifecycle event may safely reconstruct the same
receipt from already-custodied bytes. Any conflict, tamper, scope drift or
different digest fails closed. No existing record is overwritten or repaired.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256

from eios_custody_example.custody import (
    CustodyError,
    DocumentBinding,
    SyntheticCustodyVault,
)
from eios_evidence_boundary_example.review import ReviewRequest

from .lifecycle import (
    LifecycleError,
    LifecycleEventReceipt,
    _SOURCE_ID,
    _canonical,
    _stage_payload,
)
from .pilot import RehearsalManifest


class RetrySafetyError(ValueError):
    """Retry cannot be proven identical to the already-custodied event."""


@dataclass(frozen=True)
class RetrySafeLifecycleResult:
    disposition: str
    receipt: LifecycleEventReceipt
    source_result_fingerprint: str
    event_sha256: str
    production_authorized: bool = False
    decision_authority: bool = False
    real_pilot_admitted: bool = False
    operational_path: str = "FORBIDDEN"


def _receipt_from_payload(
    *,
    request: ReviewRequest,
    payload: dict,
    document_ref: str,
    digest: str,
) -> LifecycleEventReceipt:
    return LifecycleEventReceipt(
        stage=payload["stage"],
        event_type=payload["event_type"],
        document_ref=document_ref,
        event_sha256=digest,
        previous_event_sha256=payload["previous_event_sha256"],
        source_result_fingerprint=payload["source_result_fingerprint"],
        baseline_result_fingerprint=payload["baseline_result_fingerprint"],
        project_id=request.project_id,
        company_id=request.company_id,
        data_snapshot_id=request.data_snapshot_id,
    )


def record_lifecycle_event_retry_safe(
    *,
    vault: SyntheticCustodyVault,
    request: ReviewRequest,
    source: object,
    previous: LifecycleEventReceipt | None = None,
    baseline_manifest: RehearsalManifest | None = None,
) -> RetrySafeLifecycleResult:
    """Create once or safely reuse an exact already-custodied lifecycle event.

    CREATED:
        No record existed and F6.4 stored the exact expected bytes.
    REUSED_IDENTICAL:
        F6.4 rejected the duplicate write, then the same expected binding loaded
        and verified exact bytes already stored under that identity.

    Any other F6.4 failure is propagated as a retry safety failure. This keeps
    partial, conflicting, corrupt or different-digest states fail-closed.
    """
    if type(vault) is not SyntheticCustodyVault:
        raise RetrySafetyError("F6_4_SYNTHETIC_CUSTODY_REQUIRED")
    try:
        payload, document_ref = _stage_payload(
            request=request,
            source=source,
            previous=previous,
            baseline_manifest=baseline_manifest,
        )
    except LifecycleError as exc:
        raise RetrySafetyError("INVALID_LIFECYCLE_RETRY_INPUT:" + str(exc)) from exc

    content = _canonical(payload)
    digest = sha256(content).hexdigest()
    binding = DocumentBinding(
        project_id=request.project_id,
        company_id=request.company_id,
        source_id=_SOURCE_ID,
        data_snapshot_id=request.data_snapshot_id,
        document_ref=document_ref,
        expected_document_sha256=digest,
    )

    disposition = "CREATED"
    try:
        vault.store_once(binding, content)
    except CustodyError as exc:
        if str(exc) != "CUSTODY_RECORD_ALREADY_EXISTS":
            raise RetrySafetyError("LIFECYCLE_RETRY_WRITE_FAILED:" + str(exc)) from exc
        try:
            stored = vault.load_verified(binding)
        except CustodyError as load_exc:
            raise RetrySafetyError(
                "LIFECYCLE_RETRY_CONFLICT_OR_TAMPER:" + str(load_exc)
            ) from load_exc
        if stored.content != content:
            raise RetrySafetyError("LIFECYCLE_RETRY_BYTES_DIFFER")
        disposition = "REUSED_IDENTICAL"

    receipt = _receipt_from_payload(
        request=request,
        payload=payload,
        document_ref=document_ref,
        digest=digest,
    )
    return RetrySafeLifecycleResult(
        disposition=disposition,
        receipt=receipt,
        source_result_fingerprint=payload["source_result_fingerprint"],
        event_sha256=digest,
    )


__all__ = (
    "RetrySafetyError",
    "RetrySafeLifecycleResult",
    "record_lifecycle_event_retry_safe",
)
