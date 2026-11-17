"""F6.9 — synthetic lifecycle integrity journal for F6.6→F6.7→F6.8.

The journal adds lifecycle semantics only. It reuses the F6.4 write-once
synthetic custody vault as its storage primitive and never claims enterprise
immutability, trusted time, authentication, production access or decision
authority.

A complete history is exactly:
1. successful synthetic F6.6 rehearsal baseline;
2. F6.7 SAFE_STOPPED bound to that baseline;
3. F6.8 SYNTHETIC_RECOVERY_REVALIDATED bound to both prior results.

Each event is written once under a deterministic stage reference and links to
the SHA-256 digest of the preceding event. Stored bytes are verified through
F6.4 custody against host-held expected digests.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json

from eios_custody_example.custody import (
    DocumentBinding, SyntheticCustodyVault,
)
from eios_evidence_boundary_example.review import ReviewRequest
from .pilot import PilotRehearsalResult, RehearsalManifest
from .safe_stop import SafeStopResult
from .recovery import RecoveryResult

_SCHEMA = "F6_9_LIFECYCLE_EVENT_01/v0.1"
_SOURCE_ID = "F6_9_LIFECYCLE_JOURNAL"
_STAGES = (
    (1, "F6_6_BASELINE", "SYNTHETIC_REHEARSAL_COMPLETE"),
    (2, "F6_7_SAFE_STOP", "SAFE_STOPPED"),
    (3, "F6_8_RECOVERY", "SYNTHETIC_RECOVERY_REVALIDATED"),
)
_FIELDS = frozenset({
    "schema", "stage", "event_type", "status",
    "project_id", "company_id", "data_snapshot_id",
    "source_result_fingerprint", "previous_event_sha256",
    "baseline_result_fingerprint", "safe_stop_result_fingerprint",
    "fresh_result_fingerprint",
    "production_authorized", "decision_authority",
    "real_pilot_admitted", "operational_path",
})


class LifecycleError(ValueError):
    """Lifecycle history is incomplete, inconsistent, forged or unavailable."""


def _canonical(value: object) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True,
        separators=(",", ":"), allow_nan=False,
    ).encode("utf-8")


def _pairs(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise LifecycleError("DUPLICATE_LIFECYCLE_KEY")
        result[key] = value
    return result


@dataclass(frozen=True)
class LifecycleEventReceipt:
    stage: int
    event_type: str
    document_ref: str
    event_sha256: str
    previous_event_sha256: str | None
    source_result_fingerprint: str
    project_id: str
    company_id: str
    data_snapshot_id: str
    production_authorized: bool = False
    decision_authority: bool = False
    real_pilot_admitted: bool = False
    operational_path: str = "FORBIDDEN"


@dataclass(frozen=True)
class LifecycleVerification:
    status: str
    project_id: str
    company_id: str
    data_snapshot_id: str
    event_count: int
    baseline_event_sha256: str
    safe_stop_event_sha256: str
    recovery_event_sha256: str
    head_sha256: str
    production_authorized: bool = False
    decision_authority: bool = False
    real_pilot_admitted: bool = False
    operational_path: str = "FORBIDDEN"


def _authority_forbidden(value: object) -> bool:
    return (
        getattr(value, "production_authorized", None) is False
        and getattr(value, "decision_authority", None) is False
        and getattr(value, "real_pilot_admitted", None) is False
        and getattr(value, "operational_path", None) == "FORBIDDEN"
    )


def _stage_payload(
    *,
    request: ReviewRequest,
    source: object,
    previous: LifecycleEventReceipt | None,
    baseline_manifest: RehearsalManifest | None,
) -> tuple[dict, str]:
    if type(request) is not ReviewRequest:
        raise LifecycleError("F6_3_REVIEW_SCOPE_REQUIRED")
    if source.__class__ is PilotRehearsalResult:
        stage, event_type, status = _STAGES[0]
        if previous is not None:
            raise LifecycleError("BASELINE_MUST_BE_FIRST")
        if (
            type(baseline_manifest) is not RehearsalManifest
            or baseline_manifest.project_id != request.project_id
            or baseline_manifest.company_id != request.company_id
            or baseline_manifest.data_snapshot_id != request.data_snapshot_id
            or baseline_manifest.registry_digest != source.registry_digest
            or source.status != status
            or source.synthetic_rehearsal_complete is not True
            or source.project_id != request.project_id
            or source.company_id != request.company_id
            or not _authority_forbidden(source)
        ):
            raise LifecycleError("INVALID_F6_6_BASELINE")
        baseline = source.result_fingerprint
        stop_fp = None
        fresh_fp = None
        previous_sha = None
    elif source.__class__ is SafeStopResult:
        if baseline_manifest is not None:
            raise LifecycleError("BASELINE_MANIFEST_ONLY_ALLOWED_FOR_STAGE_1")
        stage, event_type, status = _STAGES[1]
        if (
            type(previous) is not LifecycleEventReceipt
            or previous.stage != 1
            or previous.event_type != "F6_6_BASELINE"
            or source.status != status
            or source.previous_result_invalidated is not True
            or source.fresh_revalidation_passed is not False
            or source.project_id != request.project_id
            or source.company_id != request.company_id
            or source.data_snapshot_id != request.data_snapshot_id
            or source.previous_result_fingerprint != previous.source_result_fingerprint
            or not _authority_forbidden(source)
        ):
            raise LifecycleError("INVALID_F6_7_SAFE_STOP_LINK")
        baseline = source.previous_result_fingerprint
        stop_fp = source.result_fingerprint
        fresh_fp = None
        previous_sha = previous.event_sha256
    elif source.__class__ is RecoveryResult:
        if baseline_manifest is not None:
            raise LifecycleError("BASELINE_MANIFEST_ONLY_ALLOWED_FOR_STAGE_1")
        stage, event_type, status = _STAGES[2]
        if (
            type(previous) is not LifecycleEventReceipt
            or previous.stage != 2
            or previous.event_type != "F6_7_SAFE_STOP"
            or source.status != status
            or source.stale_result_reusable is not False
            or source.fresh_chain_revalidated is not True
            or source.supersedes_safe_stop is not True
            or source.project_id != request.project_id
            or source.company_id != request.company_id
            or source.data_snapshot_id != request.data_snapshot_id
            or source.safe_stop_fingerprint != previous.source_result_fingerprint
            or source.stale_result_fingerprint is None
            or source.fresh_result_fingerprint is None
            or not _authority_forbidden(source)
        ):
            raise LifecycleError("INVALID_F6_8_RECOVERY_LINK")
        baseline = source.stale_result_fingerprint
        stop_fp = source.safe_stop_fingerprint
        fresh_fp = source.fresh_result_fingerprint
        previous_sha = previous.event_sha256
    else:
        raise LifecycleError("UNSUPPORTED_LIFECYCLE_SOURCE")

    payload = {
        "schema": _SCHEMA,
        "stage": stage,
        "event_type": event_type,
        "status": status,
        "project_id": request.project_id,
        "company_id": request.company_id,
        "data_snapshot_id": request.data_snapshot_id,
        "source_result_fingerprint": source.result_fingerprint,
        "previous_event_sha256": previous_sha,
        "baseline_result_fingerprint": baseline,
        "safe_stop_result_fingerprint": stop_fp,
        "fresh_result_fingerprint": fresh_fp,
        "production_authorized": False,
        "decision_authority": False,
        "real_pilot_admitted": False,
        "operational_path": "FORBIDDEN",
    }
    document_ref = f"F6_9_{stage:02d}_{event_type}"
    return payload, document_ref


def record_lifecycle_event(
    *,
    vault: SyntheticCustodyVault,
    request: ReviewRequest,
    source: object,
    previous: LifecycleEventReceipt | None = None,
    baseline_manifest: RehearsalManifest | None = None,
) -> LifecycleEventReceipt:
    """Write one deterministic lifecycle event via the existing F6.4 vault."""
    if type(vault) is not SyntheticCustodyVault:
        raise LifecycleError("F6_4_SYNTHETIC_CUSTODY_REQUIRED")
    payload, document_ref = _stage_payload(
        request=request, source=source, previous=previous,
        baseline_manifest=baseline_manifest,
    )
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
    vault.store_once(binding, content)
    return LifecycleEventReceipt(
        stage=payload["stage"],
        event_type=payload["event_type"],
        document_ref=document_ref,
        event_sha256=digest,
        previous_event_sha256=payload["previous_event_sha256"],
        source_result_fingerprint=payload["source_result_fingerprint"],
        project_id=request.project_id,
        company_id=request.company_id,
        data_snapshot_id=request.data_snapshot_id,
    )


def _load_event(
    vault: SyntheticCustodyVault,
    request: ReviewRequest,
    receipt: LifecycleEventReceipt,
) -> dict:
    if type(receipt) is not LifecycleEventReceipt:
        raise LifecycleError("INVALID_LIFECYCLE_RECEIPT")
    if (
        receipt.project_id != request.project_id
        or receipt.company_id != request.company_id
        or receipt.data_snapshot_id != request.data_snapshot_id
        or receipt.production_authorized is not False
        or receipt.decision_authority is not False
        or receipt.real_pilot_admitted is not False
        or receipt.operational_path != "FORBIDDEN"
    ):
        raise LifecycleError("LIFECYCLE_RECEIPT_SCOPE_OR_AUTHORITY_MISMATCH")
    binding = DocumentBinding(
        project_id=receipt.project_id,
        company_id=receipt.company_id,
        source_id=_SOURCE_ID,
        data_snapshot_id=receipt.data_snapshot_id,
        document_ref=receipt.document_ref,
        expected_document_sha256=receipt.event_sha256,
    )
    try:
        record = vault.load_verified(binding)
    except Exception as exc:
        raise LifecycleError("LIFECYCLE_EVENT_NOT_VERIFIABLE:" + str(exc)) from exc
    if sha256(record.content).hexdigest() != receipt.event_sha256:
        raise LifecycleError("LIFECYCLE_EVENT_DIGEST_MISMATCH")
    try:
        payload = json.loads(record.content.decode("utf-8"), object_pairs_hook=_pairs)
    except LifecycleError:
        raise
    except (ValueError, UnicodeError) as exc:
        raise LifecycleError("INVALID_LIFECYCLE_EVENT_JSON") from exc
    if type(payload) is not dict or set(payload) != _FIELDS:
        raise LifecycleError("LIFECYCLE_EVENT_SCHEMA_MISMATCH")
    return payload


def verify_lifecycle_history(
    *,
    vault: SyntheticCustodyVault,
    request: ReviewRequest,
    receipts: tuple[LifecycleEventReceipt, ...],
) -> LifecycleVerification:
    """Verify exact 3-stage history, tenant scope, hashes, order and authority."""
    if type(vault) is not SyntheticCustodyVault:
        raise LifecycleError("F6_4_SYNTHETIC_CUSTODY_REQUIRED")
    if type(request) is not ReviewRequest:
        raise LifecycleError("F6_3_REVIEW_SCOPE_REQUIRED")
    if type(receipts) is not tuple or len(receipts) != 3:
        raise LifecycleError("COMPLETE_THREE_STAGE_HISTORY_REQUIRED")

    payloads = tuple(_load_event(vault, request, receipt) for receipt in receipts)
    for index, (receipt, payload, expected) in enumerate(zip(receipts, payloads, _STAGES)):
        stage, event_type, status = expected
        if (
            receipt.stage != stage
            or receipt.event_type != event_type
            or receipt.document_ref != f"F6_9_{stage:02d}_{event_type}"
            or payload["stage"] != stage
            or payload["event_type"] != event_type
            or payload["status"] != status
            or payload["source_result_fingerprint"] != receipt.source_result_fingerprint
            or payload["project_id"] != request.project_id
            or payload["company_id"] != request.company_id
            or payload["data_snapshot_id"] != request.data_snapshot_id
            or payload["production_authorized"] is not False
            or payload["decision_authority"] is not False
            or payload["real_pilot_admitted"] is not False
            or payload["operational_path"] != "FORBIDDEN"
        ):
            raise LifecycleError("LIFECYCLE_STAGE_CONTENT_MISMATCH")
        expected_previous = None if index == 0 else receipts[index - 1].event_sha256
        if (
            receipt.previous_event_sha256 != expected_previous
            or payload["previous_event_sha256"] != expected_previous
        ):
            raise LifecycleError("LIFECYCLE_HASH_CHAIN_BROKEN")

    baseline, stopped, recovered = payloads
    if (
        stopped["baseline_result_fingerprint"] != baseline["source_result_fingerprint"]
        or stopped["safe_stop_result_fingerprint"] != stopped["source_result_fingerprint"]
        or recovered["baseline_result_fingerprint"] != baseline["source_result_fingerprint"]
        or recovered["safe_stop_result_fingerprint"] != stopped["source_result_fingerprint"]
        or recovered["fresh_result_fingerprint"] is None
    ):
        raise LifecycleError("LIFECYCLE_RESULT_LINEAGE_BROKEN")

    return LifecycleVerification(
        status="SYNTHETIC_LIFECYCLE_HISTORY_VERIFIED",
        project_id=request.project_id,
        company_id=request.company_id,
        data_snapshot_id=request.data_snapshot_id,
        event_count=3,
        baseline_event_sha256=receipts[0].event_sha256,
        safe_stop_event_sha256=receipts[1].event_sha256,
        recovery_event_sha256=receipts[2].event_sha256,
        head_sha256=receipts[2].event_sha256,
    )


__all__ = (
    "LifecycleError", "LifecycleEventReceipt", "LifecycleVerification",
    "record_lifecycle_event", "verify_lifecycle_history",
)
