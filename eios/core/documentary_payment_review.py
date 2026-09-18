"""Preserve supplied human findings; do not perform or authenticate the review."""
from dataclasses import dataclass
from datetime import datetime
from hashlib import sha256
import json
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from .documentary_payment_capture import DocumentaryLocator, DocumentaryPaymentCapture

GLOBAL_CONDITIONS = ("OPERATION_CORRESPONDENCE", "DOCUMENT_TERMS", "LISTED_DUPLICATION")
INSTALLMENT_CONDITIONS = ("INSTALLMENT_ASSOCIATION", "AMOUNT", "CURRENCY", "DUE_DATE", "SUPPORT_CONSISTENCY")
Condition = Literal["OPERATION_CORRESPONDENCE", "DOCUMENT_TERMS", "LISTED_DUPLICATION",
                    "INSTALLMENT_ASSOCIATION", "AMOUNT", "CURRENCY", "DUE_DATE", "SUPPORT_CONSISTENCY"]


class DocumentaryReviewFinding(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)
    condition: Condition
    installment_ref: str | None = None
    outcome: Literal["CONFIRMED_BY_REVIEW", "NOT_CONFIRMED", "CONFLICT_REPORTED"]
    note: str = Field(min_length=1)
    locators: tuple[DocumentaryLocator, ...] = ()


def _reference(value):
    if not isinstance(value, str) or not value or value != value.strip():
        raise ValueError("References and notes must be nonempty without outer whitespace")


@dataclass(frozen=True, init=False)
class DocumentaryPaymentHumanReview:
    _material: bytes

    def __init__(self):
        raise TypeError("Use build_documentary_payment_human_review")

    def to_payload(self) -> dict:
        return json.loads(self._material)

    @property
    def fingerprint(self) -> str:
        return sha256(self._material).hexdigest()

    @property
    def pending_controls(self) -> tuple[dict, ...]:
        return tuple(self.to_payload()["pending_controls"])


def build_documentary_payment_human_review(
    *, capture: DocumentaryPaymentCapture, review_ref: str, reviewer_ref: str,
    reviewed_at: datetime, findings: tuple[DocumentaryReviewFinding, ...],
    previous_review_ref: str | None = None,
) -> DocumentaryPaymentHumanReview:
    """Register explicit findings only; omitted controls remain pending."""
    if not isinstance(capture, DocumentaryPaymentCapture):
        raise TypeError("capture must be DocumentaryPaymentCapture")
    for reference in (review_ref, reviewer_ref):
        _reference(reference)
    if previous_review_ref is not None:
        _reference(previous_review_ref)
        if previous_review_ref == review_ref:
            raise ValueError("Review cannot reference itself as predecessor")
    if not isinstance(reviewed_at, datetime) or reviewed_at.utcoffset() is None:
        raise ValueError("reviewed_at requires an explicit timezone")
    if type(findings) is not tuple:
        raise TypeError("findings must be a tuple")
    source = capture.to_payload()
    if source["schema_version"] != "DOC-PAY-CAP-01/v0.1":
        raise ValueError("Unsupported documentary capture schema")
    bindings = {b["installment_ref"]: b for b in source["bindings"]}
    documents = {d["document_ref"] for d in source["documents"]}
    inventory = [(condition, None) for condition in GLOBAL_CONDITIONS]
    inventory += [(condition, installment) for installment in bindings for condition in INSTALLMENT_CONDITIONS]
    captured_findings, seen = [], set()
    for finding in findings:
        if not isinstance(finding, DocumentaryReviewFinding):
            raise TypeError("Expected DocumentaryReviewFinding")
        finding = DocumentaryReviewFinding.model_validate(finding.model_dump(mode="python"))
        _reference(finding.note)
        if finding.installment_ref is not None:
            _reference(finding.installment_ref)
        key = (finding.condition, finding.installment_ref)
        if key not in inventory:
            raise ValueError("Finding refers to a foreign target or mismatched scope")
        if key in seen:
            raise ValueError("Duplicate finding for condition/target")
        if finding.outcome == "CONFIRMED_BY_REVIEW" and not finding.locators:
            raise ValueError("Positive finding requires documentary support")
        for locator in finding.locators:
            _reference(locator.document_ref)
            _reference(locator.section)
            if locator.document_ref not in documents:
                raise ValueError("Foreign documentary locator")
            if finding.installment_ref is not None:
                if locator.model_dump(mode="json") not in bindings[finding.installment_ref]["locators"]:
                    raise ValueError("Locator is not part of the examined installment binding")
        seen.add(key)
        captured_findings.append(finding.model_dump(mode="json"))
    controls = lambda keys: [dict(condition=c, installment_ref=i) for c, i in keys]
    payload = dict(schema_version="DOC-PAY-REVIEW-01/v0.1", capture=source,
        capture_fingerprint=capture.fingerprint, review_ref=review_ref, reviewer_ref=reviewer_ref,
        reviewed_at=reviewed_at.isoformat(), previous_review_ref=previous_review_ref,
        findings=captured_findings, control_inventory=controls(inventory),
        pending_controls=controls(k for k in inventory if k not in seen))
    material = json.dumps(payload, ensure_ascii=False, sort_keys=True,
                          separators=(",", ":"), allow_nan=False).encode("utf-8")
    result = object.__new__(DocumentaryPaymentHumanReview)
    object.__setattr__(result, "_material", material)
    return result


def validate_review_for_capture(review: DocumentaryPaymentHumanReview, capture: DocumentaryPaymentCapture) -> None:
    """Reject reuse on different material; this does not validate human identity/truth."""
    if not isinstance(review, DocumentaryPaymentHumanReview) or not isinstance(capture, DocumentaryPaymentCapture):
        raise TypeError("Expected human review and documentary capture")
    payload = review.to_payload()
    if payload["capture_fingerprint"] != capture.fingerprint or payload["capture"] != capture.to_payload():
        raise ValueError("Review belongs to different examined material")
