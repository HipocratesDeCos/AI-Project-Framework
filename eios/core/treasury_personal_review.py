"""Preserve personal treasury-review findings without evaluating quality."""
from dataclasses import dataclass
from datetime import datetime
from hashlib import sha256
import json
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from .documentary_payment_capture import DocumentaryLocator
from .documentary_payment_review import _reference
from .treasury_contextual_assessment import TreasuryContextualAssessment
from .treasury_mandate_verification import (
    TreasuryMandateVerification, validate_mandate_verification_for_target,
)

CONDITIONS = ("SOURCE_CORRESPONDENCE", "ECONOMIC_CUTOFF", "AMOUNT_SUPPORT",
              "AVAILABILITY", "RESTRICTIONS", "SOURCE_SUFFICIENCY")


class TreasuryReviewFinding(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)
    condition: Literal["SOURCE_CORRESPONDENCE", "ECONOMIC_CUTOFF", "AMOUNT_SUPPORT",
                       "AVAILABILITY", "RESTRICTIONS", "SOURCE_SUFFICIENCY"]
    outcome: Literal["CONFIRMED_BY_REVIEW", "NOT_CONFIRMED", "CONFLICT_REPORTED"]
    note: str = Field(min_length=1)
    locators: tuple[DocumentaryLocator, ...] = ()


@dataclass(frozen=True, init=False)
class TreasuryPersonalReview:
    _material: bytes

    def __init__(self):
        raise TypeError("Use build_treasury_personal_review")

    def to_payload(self) -> dict:
        return json.loads(self._material)

    @property
    def fingerprint(self) -> str:
        return sha256(self._material).hexdigest()

    @property
    def pending_controls(self) -> tuple[str, ...]:
        return tuple(self.to_payload()["pending_controls"])


def build_treasury_personal_review(*, assessment: TreasuryContextualAssessment,
    mandate: TreasuryMandateVerification, review_ref: str, reviewer_ref: str,
    reviewed_at: datetime, findings: tuple[TreasuryReviewFinding, ...],
    previous_review_ref: str | None = None) -> TreasuryPersonalReview:
    validate_mandate_verification_for_target(mandate, assessment)
    for value in (review_ref, reviewer_ref): _reference(value)
    if previous_review_ref is not None:
        _reference(previous_review_ref)
        if previous_review_ref == review_ref:
            raise ValueError("Previous review cannot be itself")
    if not isinstance(reviewed_at, datetime) or reviewed_at.utcoffset() is None:
        raise ValueError("Aware review time required")
    mandate_payload = mandate.to_payload()
    if mandate_payload["reviewer_ref"] != reviewer_ref:
        raise ValueError("Reviewer differs from mandate")
    if mandate_payload["target_review_ref"] != review_ref:
        raise ValueError("Review reference differs from mandate target")
    support = assessment.to_payload()["treasury_support"]
    document_refs = {document["document_ref"] for document in support["documents"]}
    if type(findings) is not tuple:
        raise TypeError("Explicit finding tuple required")
    entries, seen = [], set()
    for finding in findings:
        if not isinstance(finding, TreasuryReviewFinding):
            raise TypeError("Expected treasury review finding")
        finding = TreasuryReviewFinding.model_validate(finding.model_dump(mode="python"))
        _reference(finding.note)
        if finding.condition in seen:
            raise ValueError("Duplicate condition")
        seen.add(finding.condition)
        if finding.outcome != "CONFLICT_REPORTED" and not finding.locators:
            raise ValueError("Confirmed or not-confirmed finding requires locators")
        for locator in finding.locators:
            _reference(locator.document_ref); _reference(locator.section)
            if locator.document_ref not in document_refs:
                raise ValueError("Finding locator is outside treasury support")
        entries.append(finding.model_dump(mode="json"))
    authorized = mandate_payload["verification_outcome"] == "ACREDITADO_POR_CONTRASTE"
    payload = dict(schema_version="TREASURY-PERSONAL-REVIEW-01/v0.1",
        assessment=assessment.to_payload(), assessment_fingerprint=assessment.fingerprint,
        mandate=mandate_payload, mandate_fingerprint=mandate.fingerprint,
        review_ref=review_ref, reviewer_ref=reviewer_ref, reviewed_at=reviewed_at.isoformat(),
        previous_review_ref=previous_review_ref, findings=entries,
        condition_inventory=list(CONDITIONS),
        pending_controls=[condition for condition in CONDITIONS if condition not in seen],
        assurance_scope="AUTHORIZED_REVIEWER_PRESENTED_FINDINGS" if authorized
            else "PRESENTED_UNAUTHORIZED_OR_UNRESOLVED_FINDINGS")
    result = object.__new__(TreasuryPersonalReview)
    object.__setattr__(result, "_material", json.dumps(payload, ensure_ascii=False,
        sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8"))
    return result


def validate_treasury_review_for_material(review: TreasuryPersonalReview,
    assessment: TreasuryContextualAssessment, mandate: TreasuryMandateVerification) -> None:
    if not isinstance(review, TreasuryPersonalReview):
        raise TypeError("Expected constructed treasury review")
    validate_mandate_verification_for_target(mandate, assessment)
    payload = review.to_payload()
    if (payload["assessment"] != assessment.to_payload()
        or payload["assessment_fingerprint"] != assessment.fingerprint
        or payload["mandate"] != mandate.to_payload()
        or payload["mandate_fingerprint"] != mandate.fingerprint):
        raise ValueError("Treasury review belongs to different material")
