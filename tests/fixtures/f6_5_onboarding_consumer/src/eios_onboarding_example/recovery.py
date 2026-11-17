"""F6.8 — explicit synthetic recovery after an F6.7 safe stop.

Recovery is not a continuation of stale state. A stopped chain can only
produce a new synthetic recovery receipt after a complete fresh F6.5/F6.3/F6.4
review and a fresh F6.6 rehearsal assessment.

This module remains external to canonical EIOS and never grants operational
authority, production access, QTG/O1 execution or a business decision.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json

from eios_evidence_boundary_example.review import ReviewRequest
from .onboarding import (
    OnboardingReceipt, PinnedOnboarding, review_with_onboarded_providers,
)
from .pilot import (
    PilotRehearsalResult, RehearsalManifest, assess_read_only_rehearsal,
)
from .safe_stop import SafeStopResult


class RecoveryError(ValueError):
    """Invalid recovery request or attempt to reuse stale authority."""


def _canonical(value: dict) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True,
        separators=(",", ":"), allow_nan=False,
    ).encode("utf-8")


def _failure_code(exc: Exception) -> str:
    value = str(exc).strip()
    if not value:
        return exc.__class__.__name__
    return value.splitlines()[0][:160]


@dataclass(frozen=True)
class RecoveryResult:
    status: str
    project_id: str
    company_id: str
    data_snapshot_id: str
    safe_stop_fingerprint: str
    stale_result_fingerprint: str
    fresh_result_fingerprint: str | None
    failure_stage: str | None
    failure_code: str | None
    reasons: tuple[str, ...]
    stale_result_reusable: bool
    fresh_chain_revalidated: bool
    supersedes_safe_stop: bool
    result_fingerprint: str
    real_pilot_admitted: bool = False
    real_company_authenticated: bool = False
    real_document_authenticated: bool = False
    real_human_authorized: bool = False
    decision_authority: bool = False
    production_authorized: bool = False
    operational_path: str = "FORBIDDEN"


def _result(
    *,
    stopped: SafeStopResult,
    stale: PilotRehearsalResult,
    request: ReviewRequest,
    status: str,
    fresh_result_fingerprint: str | None,
    failure_stage: str | None,
    failure_code: str | None,
    reasons: tuple[str, ...],
    fresh_chain_revalidated: bool,
    supersedes_safe_stop: bool,
) -> RecoveryResult:
    payload = {
        "status": status,
        "project_id": request.project_id,
        "company_id": request.company_id,
        "data_snapshot_id": request.data_snapshot_id,
        "safe_stop_fingerprint": stopped.result_fingerprint,
        "stale_result_fingerprint": stale.result_fingerprint,
        "fresh_result_fingerprint": fresh_result_fingerprint,
        "failure_stage": failure_stage,
        "failure_code": failure_code,
        "reasons": list(reasons),
        "stale_result_reusable": False,
        "fresh_chain_revalidated": fresh_chain_revalidated,
        "supersedes_safe_stop": supersedes_safe_stop,
        "real_pilot_admitted": False,
        "real_company_authenticated": False,
        "real_document_authenticated": False,
        "real_human_authorized": False,
        "decision_authority": False,
        "production_authorized": False,
        "operational_path": "FORBIDDEN",
    }
    return RecoveryResult(
        status=status,
        project_id=request.project_id,
        company_id=request.company_id,
        data_snapshot_id=request.data_snapshot_id,
        safe_stop_fingerprint=stopped.result_fingerprint,
        stale_result_fingerprint=stale.result_fingerprint,
        fresh_result_fingerprint=fresh_result_fingerprint,
        failure_stage=failure_stage,
        failure_code=failure_code,
        reasons=reasons,
        stale_result_reusable=False,
        fresh_chain_revalidated=fresh_chain_revalidated,
        supersedes_safe_stop=supersedes_safe_stop,
        result_fingerprint=sha256(_canonical(payload)).hexdigest(),
    )


def recover_after_safe_stop(
    *,
    stopped: SafeStopResult,
    stale: PilotRehearsalResult,
    manifest: RehearsalManifest,
    prepared: object,
    request: ReviewRequest,
    pin: PinnedOnboarding,
    registry_source: object,
    endpoints: object,
) -> RecoveryResult:
    """Attempt a fresh synthetic recovery after an F6.7 SAFE_STOPPED receipt.

    The stopped receipt and stale F6.6 result are historical inputs only.
    Neither can be reused as a current trust receipt.
    """
    if type(stopped) is not SafeStopResult or stopped.status != "SAFE_STOPPED":
        raise RecoveryError("F6_7_SAFE_STOP_REQUIRED")
    if type(stale) is not PilotRehearsalResult:
        raise RecoveryError("STALE_F6_6_RESULT_REQUIRED")
    if type(manifest) is not RehearsalManifest:
        raise RecoveryError("FRESH_F6_6_MANIFEST_REQUIRED")
    if type(request) is not ReviewRequest or type(pin) is not PinnedOnboarding:
        raise RecoveryError("FRESH_F6_5_CONTEXT_REQUIRED")
    if (
        stopped.previous_result_fingerprint != stale.result_fingerprint
        or stopped.previous_result_invalidated is not True
        or stopped.fresh_revalidation_passed is not False
        or stopped.production_authorized is not False
        or stopped.decision_authority is not False
        or stopped.operational_path != "FORBIDDEN"
    ):
        raise RecoveryError("SAFE_STOP_HISTORY_MISMATCH_OR_PROMOTION")
    if stopped.failure_stage == "CONTEXT_REBIND":
        return _result(
            stopped=stopped, stale=stale, request=request,
            status="RECOVERY_BLOCKED_NEW_CHAIN_REQUIRED",
            fresh_result_fingerprint=None,
            failure_stage="RECOVERY_SCOPE",
            failure_code="F6_8_CONTEXT_DRIFT_REQUIRES_NEW_CHAIN",
            reasons=("SAFE_STOP_CONTEXT_CHANGED",),
            fresh_chain_revalidated=False,
            supersedes_safe_stop=False,
        )
    if (
        stale.project_id != request.project_id
        or stale.company_id != request.company_id
        or manifest.project_id != request.project_id
        or manifest.company_id != request.company_id
        or manifest.data_snapshot_id != request.data_snapshot_id
        or manifest.registry_digest != pin.expected_digest
        or manifest.registry_revision != pin.expected_revision
    ):
        return _result(
            stopped=stopped, stale=stale, request=request,
            status="RECOVERY_BLOCKED",
            fresh_result_fingerprint=None,
            failure_stage="RECOVERY_SCOPE",
            failure_code="F6_8_FRESH_CONTEXT_MISMATCH",
            reasons=("FRESH_RECOVERY_CONTEXT_NOT_BOUND",),
            fresh_chain_revalidated=False,
            supersedes_safe_stop=False,
        )
    if (
        stale.synthetic_rehearsal_complete is not True
        or stale.real_pilot_admitted is not False
        or stale.production_authorized is not False
        or stale.decision_authority is not False
        or stale.operational_path != "FORBIDDEN"
    ):
        raise RecoveryError("STALE_RESULT_NOT_VALID_SYNTHETIC_HISTORY")

    try:
        fresh_review = review_with_onboarded_providers(
            prepared=prepared, request=request, pin=pin,
            registry_source=registry_source, endpoints=endpoints,
        )
    except Exception as exc:
        return _result(
            stopped=stopped, stale=stale, request=request,
            status="RECOVERY_BLOCKED",
            fresh_result_fingerprint=None,
            failure_stage="FRESH_EXTERNAL_REVALIDATION",
            failure_code=_failure_code(exc),
            reasons=("RECOVERY_REVALIDATION_FAILED",),
            fresh_chain_revalidated=False,
            supersedes_safe_stop=False,
        )
    if type(fresh_review) is not OnboardingReceipt:
        return _result(
            stopped=stopped, stale=stale, request=request,
            status="RECOVERY_BLOCKED",
            fresh_result_fingerprint=None,
            failure_stage="FRESH_F6_5_RECEIPT",
            failure_code="INVALID_FRESH_ONBOARDING_RECEIPT",
            reasons=("RECOVERY_REVALIDATION_FAILED",),
            fresh_chain_revalidated=False,
            supersedes_safe_stop=False,
        )
    try:
        fresh = assess_read_only_rehearsal(
            manifest=manifest, pin=pin, request=request,
            technical_review=fresh_review,
        )
    except Exception as exc:
        return _result(
            stopped=stopped, stale=stale, request=request,
            status="RECOVERY_BLOCKED",
            fresh_result_fingerprint=None,
            failure_stage="FRESH_F6_6_REASSESSMENT",
            failure_code=_failure_code(exc),
            reasons=("RECOVERY_REHEARSAL_REASSESSMENT_FAILED",),
            fresh_chain_revalidated=False,
            supersedes_safe_stop=False,
        )
    if (
        fresh.status != "SYNTHETIC_REHEARSAL_COMPLETE"
        or fresh.synthetic_rehearsal_complete is not True
        or fresh.real_pilot_admitted is not False
        or fresh.production_authorized is not False
        or fresh.decision_authority is not False
        or fresh.operational_path != "FORBIDDEN"
    ):
        return _result(
            stopped=stopped, stale=stale, request=request,
            status="RECOVERY_BLOCKED",
            fresh_result_fingerprint=fresh.result_fingerprint,
            failure_stage="FRESH_F6_6_REASSESSMENT",
            failure_code="F6_8_FRESH_REHEARSAL_NOT_COMPLETE",
            reasons=("RECOVERY_REHEARSAL_NOT_COMPLETE",),
            fresh_chain_revalidated=False,
            supersedes_safe_stop=False,
        )

    return _result(
        stopped=stopped, stale=stale, request=request,
        status="SYNTHETIC_RECOVERY_REVALIDATED",
        fresh_result_fingerprint=fresh.result_fingerprint,
        failure_stage=None, failure_code=None, reasons=(),
        fresh_chain_revalidated=True,
        supersedes_safe_stop=True,
    )


__all__ = ("RecoveryError", "RecoveryResult", "recover_after_safe_stop")
