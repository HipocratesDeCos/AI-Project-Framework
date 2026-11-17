"""F6.7 — integral synthetic fail-closed revalidation and safe stop.

This module remains outside canonical EIOS. It proves that a previously
successful F6.6 rehearsal cannot be reused after the external trust state
changes. A fresh F6.5/F6.3/F6.4 validation is mandatory before reuse.

No result from this module authenticates a company, document, reviewer or
provider. No result authorizes QTG/O1, production, writes or a business
decision.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
import re

from eios_evidence_boundary_example.review import ReviewRequest
from .onboarding import (
    OnboardingReceipt, PinnedOnboarding, review_with_onboarded_providers,
)
from .pilot import (
    PilotRehearsalResult, RehearsalManifest, assess_read_only_rehearsal,
)

_IDENT = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}\Z")


class SafeStopError(ValueError):
    """Invalid F6.7 request or attempt to promote authority."""


def _id(value: object, field: str) -> None:
    if type(value) is not str or not _IDENT.fullmatch(value):
        raise SafeStopError("INVALID_SAFE_STOP_FIELD:" + field)


def _canonical(value: dict) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True,
        separators=(",", ":"), allow_nan=False,
    ).encode("utf-8")


@dataclass(frozen=True)
class SafeStopResult:
    status: str
    project_id: str
    company_id: str
    data_snapshot_id: str
    previous_result_fingerprint: str
    failure_stage: str | None
    failure_code: str | None
    reasons: tuple[str, ...]
    previous_result_invalidated: bool
    fresh_revalidation_passed: bool
    result_fingerprint: str
    real_pilot_admitted: bool = False
    real_company_authenticated: bool = False
    real_document_authenticated: bool = False
    real_human_authorized: bool = False
    decision_authority: bool = False
    production_authorized: bool = False
    operational_path: str = "FORBIDDEN"


def _failure_code(exc: Exception) -> str:
    value = str(exc).strip()
    if not value:
        return exc.__class__.__name__
    return value.splitlines()[0][:160]


def _result(
    *,
    previous: PilotRehearsalResult,
    request: ReviewRequest,
    status: str,
    failure_stage: str | None,
    failure_code: str | None,
    reasons: tuple[str, ...],
    invalidated: bool,
    fresh_passed: bool,
) -> SafeStopResult:
    canonical_payload = {
        "status": status,
        "project_id": request.project_id,
        "company_id": request.company_id,
        "data_snapshot_id": request.data_snapshot_id,
        "previous_result_fingerprint": previous.result_fingerprint,
        "failure_stage": failure_stage,
        "failure_code": failure_code,
        "reasons": list(reasons),
        "previous_result_invalidated": invalidated,
        "fresh_revalidation_passed": fresh_passed,
        "real_pilot_admitted": False,
        "real_company_authenticated": False,
        "real_document_authenticated": False,
        "real_human_authorized": False,
        "decision_authority": False,
        "production_authorized": False,
        "operational_path": "FORBIDDEN",
    }
    return SafeStopResult(
        status=status,
        project_id=request.project_id,
        company_id=request.company_id,
        data_snapshot_id=request.data_snapshot_id,
        previous_result_fingerprint=previous.result_fingerprint,
        failure_stage=failure_stage,
        failure_code=failure_code,
        reasons=reasons,
        previous_result_invalidated=invalidated,
        fresh_revalidation_passed=fresh_passed,
        result_fingerprint=sha256(_canonical(canonical_payload)).hexdigest(),
    )


def revalidate_before_rehearsal_reuse(
    *,
    previous: PilotRehearsalResult,
    manifest: RehearsalManifest,
    prepared: object,
    request: ReviewRequest,
    pin: PinnedOnboarding,
    registry_source: object,
    endpoints: object,
) -> SafeStopResult:
    """Recheck the whole external chain before reusing an F6.6 result.

    Any external exception is converted into a terminal synthetic safe-stop
    receipt. This is intentionally fail-closed: no fallback receipt is built,
    no stale F6.5 receipt is accepted and no prior F6.6 success survives.
    """
    if type(previous) is not PilotRehearsalResult:
        raise SafeStopError("F6_6_RESULT_REQUIRED")
    if type(manifest) is not RehearsalManifest:
        raise SafeStopError("F6_6_MANIFEST_REQUIRED")
    if type(request) is not ReviewRequest or type(pin) is not PinnedOnboarding:
        raise SafeStopError("F6_5_CONTEXT_REQUIRED")
    for field in ("project_id", "company_id", "data_snapshot_id"):
        _id(getattr(request, field), field)
    if (
        previous.project_id != request.project_id
        or previous.company_id != request.company_id
        or manifest.project_id != request.project_id
        or manifest.company_id != request.company_id
        or manifest.data_snapshot_id != request.data_snapshot_id
        or previous.registry_digest != pin.expected_digest
        or manifest.registry_digest != pin.expected_digest
        or manifest.registry_revision != pin.expected_revision
    ):
        return _result(
            previous=previous, request=request,
            status="SAFE_STOPPED", failure_stage="CONTEXT_REBIND",
            failure_code="F6_7_CONTEXT_OR_VERSION_CHANGED",
            reasons=("PREVIOUS_RESULT_CONTEXT_INVALIDATED",),
            invalidated=True, fresh_passed=False,
        )
    if (
        previous.synthetic_rehearsal_complete is not True
        or previous.real_pilot_admitted is not False
        or previous.production_authorized is not False
        or previous.decision_authority is not False
        or previous.operational_path != "FORBIDDEN"
    ):
        raise SafeStopError("PREVIOUS_RESULT_NOT_ELIGIBLE_FOR_SYNTHETIC_REVALIDATION")

    try:
        fresh_review = review_with_onboarded_providers(
            prepared=prepared, request=request, pin=pin,
            registry_source=registry_source, endpoints=endpoints,
        )
    except Exception as exc:
        return _result(
            previous=previous, request=request,
            status="SAFE_STOPPED", failure_stage="F6_5_F6_3_F6_4_REVALIDATION",
            failure_code=_failure_code(exc),
            reasons=("FRESH_EXTERNAL_REVALIDATION_FAILED",),
            invalidated=True, fresh_passed=False,
        )

    if type(fresh_review) is not OnboardingReceipt:
        return _result(
            previous=previous, request=request,
            status="SAFE_STOPPED", failure_stage="F6_5_RECEIPT",
            failure_code="INVALID_FRESH_ONBOARDING_RECEIPT",
            reasons=("FRESH_EXTERNAL_REVALIDATION_FAILED",),
            invalidated=True, fresh_passed=False,
        )

    try:
        fresh = assess_read_only_rehearsal(
            manifest=manifest, pin=pin, request=request,
            technical_review=fresh_review,
        )
    except Exception as exc:
        return _result(
            previous=previous, request=request,
            status="SAFE_STOPPED", failure_stage="F6_6_REBIND",
            failure_code=_failure_code(exc),
            reasons=("FRESH_REHEARSAL_BINDING_FAILED",),
            invalidated=True, fresh_passed=False,
        )

    if (
        fresh.synthetic_rehearsal_complete is not True
        or fresh.status != "SYNTHETIC_REHEARSAL_COMPLETE"
        or fresh.result_fingerprint != previous.result_fingerprint
    ):
        return _result(
            previous=previous, request=request,
            status="SAFE_STOPPED", failure_stage="F6_6_REBIND",
            failure_code="F6_7_REHEARSAL_RESULT_CHANGED",
            reasons=("PREVIOUS_RESULT_CONTEXT_INVALIDATED",),
            invalidated=True, fresh_passed=False,
        )

    return _result(
        previous=previous, request=request,
        status="SYNTHETIC_CHAIN_REVALIDATED", failure_stage=None,
        failure_code=None, reasons=(),
        invalidated=False, fresh_passed=True,
    )


__all__ = (
    "SafeStopError", "SafeStopResult", "revalidate_before_rehearsal_reuse",
)
