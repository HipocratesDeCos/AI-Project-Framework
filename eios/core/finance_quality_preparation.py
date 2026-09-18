"""Preserve bound financial quality material; do not evaluate quality."""
import base64
from dataclasses import dataclass
from hashlib import sha256
import json

from pydantic import BaseModel, ConfigDict, Field, StrictBytes

from .documentary_payment_capture import DocumentaryPaymentCapture
from .documentary_payment_review import DocumentaryPaymentHumanReview, _reference, validate_review_for_capture
from .documentary_reviewer_designation import DocumentaryReviewerDesignationLink, validate_designation_link_for_review
from .required_installment_coverage import (
    RequiredInstallmentCalendar, RequiredInstallmentCoverage,
    check_required_installment_coverage, validate_coverage_for_material,
)


class PresentedQualityCriteria(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)
    reference: str = Field(min_length=1)
    version: str = Field(min_length=1)
    content: StrictBytes = Field(min_length=1)


@dataclass(frozen=True, init=False)
class FinanceQualityPreparation:
    _material: bytes

    def __init__(self):
        raise TypeError("Use build_finance_quality_preparation")

    def to_payload(self) -> dict:
        return json.loads(self._material)

    @property
    def fingerprint(self) -> str:
        return sha256(self._material).hexdigest()

    def criterion_bytes(self, reference: str, version: str) -> bytes:
        for criterion in self.to_payload()["presented_criteria"]:
            if (criterion["reference"], criterion["version"]) == (reference, version):
                return base64.b64decode(criterion["content_base64"], validate=True)
        raise KeyError((reference, version))


def build_finance_quality_preparation(
    *, capture: DocumentaryPaymentCapture, calendar: RequiredInstallmentCalendar,
    coverage: RequiredInstallmentCoverage, criteria: tuple[PresentedQualityCriteria, ...],
    review: DocumentaryPaymentHumanReview | None = None,
    designation: DocumentaryReviewerDesignationLink | None = None,
) -> FinanceQualityPreparation:
    """Check material binding and reproducible coverage, not business sufficiency."""
    if not isinstance(capture, DocumentaryPaymentCapture) or not isinstance(calendar, RequiredInstallmentCalendar) or not isinstance(coverage, RequiredInstallmentCoverage):
        raise TypeError("Expected constructed capture, declared calendar and coverage")
    calendar = RequiredInstallmentCalendar.model_validate(calendar.model_dump(mode="python"))
    validate_coverage_for_material(coverage, capture, calendar)
    recomputed = check_required_installment_coverage(capture=capture, calendar=calendar)
    if coverage.to_payload() != recomputed.to_payload() or coverage.fingerprint != recomputed.fingerprint:
        raise ValueError("Coverage is not reproducible from examined material")
    if review is not None:
        validate_review_for_capture(review, capture)
    if designation is not None:
        if review is None:
            raise ValueError("Designation requires its examined review")
        validate_designation_link_for_review(designation, review)
    if type(criteria) is not tuple or not criteria:
        raise ValueError("Explicit nonempty tuple of criterion material required")
    presented, seen = [], set()
    for criterion in criteria:
        if not isinstance(criterion, PresentedQualityCriteria):
            raise TypeError("Expected PresentedQualityCriteria")
        criterion = PresentedQualityCriteria.model_validate(criterion.model_dump(mode="python"))
        _reference(criterion.reference)
        _reference(criterion.version)
        key = (criterion.reference, criterion.version)
        if key in seen:
            raise ValueError("Duplicate criterion reference/version")
        seen.add(key)
        presented.append(dict(reference=criterion.reference, version=criterion.version,
            content_base64=base64.b64encode(criterion.content).decode("ascii"),
            sha256=sha256(criterion.content).hexdigest()))
    payload = dict(schema_version="QTG-FIN-PREP-01/v0.1", consumer="run_provenanced_finance_basic",
        capture=capture.to_payload(), capture_fingerprint=capture.fingerprint,
        calendar=calendar.model_dump(mode="json"), coverage=coverage.to_payload(),
        coverage_fingerprint=coverage.fingerprint, review=review.to_payload() if review else None,
        review_fingerprint=review.fingerprint if review else None,
        designation=designation.to_payload() if designation else None,
        designation_fingerprint=designation.fingerprint if designation else None,
        presented_criteria=presented, assurance_scope="BOUND_PRESENTED_MATERIAL_ONLY")
    result = object.__new__(FinanceQualityPreparation)
    object.__setattr__(result, "_material", json.dumps(payload, ensure_ascii=False, sort_keys=True,
        separators=(",", ":"), allow_nan=False).encode("utf-8"))
    return result
