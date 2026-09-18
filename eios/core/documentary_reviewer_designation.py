"""Preserve presented designation declarations, not verified authorization."""
import base64
from dataclasses import dataclass
from hashlib import sha256
import json
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from .documentary_payment_capture import DocumentaryLocator, DocumentaryMaterial
from .documentary_payment_review import DocumentaryPaymentHumanReview, _reference

CONDITIONS = ("PERSON_CORRESPONDENCE", "COMPANY_CORRESPONDENCE", "ROLE_AND_SCOPE",
              "VALIDITY", "DOCUMENT_CONDITIONS", "ISSUER_AUTHORITY_SUPPORT", "KNOWN_CHANGES")
Condition = Literal["PERSON_CORRESPONDENCE", "COMPANY_CORRESPONDENCE", "ROLE_AND_SCOPE",
                    "VALIDITY", "DOCUMENT_CONDITIONS", "ISSUER_AUTHORITY_SUPPORT", "KNOWN_CHANGES"]


class DesignationDeclaration(BaseModel):
    """A supplied transcription with support; never an authenticated extraction."""
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)
    field: Literal["PERSON", "COMPANY", "ROLE_AND_SCOPE", "VALIDITY", "CONDITIONS", "ISSUER", "CHANGE"]
    text: str = Field(min_length=1)
    locators: tuple[DocumentaryLocator, ...] = Field(min_length=1)


class DesignationObservation(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)
    condition: Condition
    outcome: Literal["DECLARED_CONSISTENT", "DECLARED_INCONSISTENT", "NOT_ESTABLISHED"]
    note: str = Field(min_length=1)
    locators: tuple[DocumentaryLocator, ...] = ()


@dataclass(frozen=True, init=False)
class DocumentaryReviewerDesignationLink:
    _material: bytes

    def __init__(self):
        raise TypeError("Use build_documentary_reviewer_designation_link")

    def to_payload(self) -> dict:
        return json.loads(self._material)

    @property
    def fingerprint(self) -> str:
        return sha256(self._material).hexdigest()

    @property
    def pending_controls(self) -> tuple[str, ...]:
        return tuple(self.to_payload()["pending_controls"])

    def document_bytes(self, document_ref: str) -> bytes:
        for document in self.to_payload()["documents"]:
            if document["document_ref"] == document_ref:
                return base64.b64decode(document["content_base64"], validate=True)
        raise KeyError(document_ref)


def build_documentary_reviewer_designation_link(
    *, review: DocumentaryPaymentHumanReview, link_ref: str, designation_ref: str,
    designation_kind: Literal["SYNTHETIC", "PRESENTED_OPERATIONAL"],
    reviewer_ref: str, company_scope: str, documents: tuple[DocumentaryMaterial, ...],
    declarations: tuple[DesignationDeclaration, ...], observations: tuple[DesignationObservation, ...],
) -> DocumentaryReviewerDesignationLink:
    """Check structure and exact declared targets only; perform no business review."""
    if not isinstance(review, DocumentaryPaymentHumanReview):
        raise TypeError("review must be a constructed human review")
    for value in (link_ref, designation_ref, reviewer_ref, company_scope):
        _reference(value)
    if designation_kind not in ("SYNTHETIC", "PRESENTED_OPERATIONAL"):
        raise ValueError("Explicit designation nature required")
    if any(type(value) is not tuple for value in (documents, declarations, observations)):
        raise TypeError("Collections must be tuples")
    source = review.to_payload()
    if source["schema_version"] != "DOC-PAY-REVIEW-01/v0.1":
        raise ValueError("Unsupported review schema")
    snapshot = source["capture"]["finance_package"]["finance_input"]["snapshot"]
    if source["reviewer_ref"] != reviewer_ref or snapshot["company_scope"] != company_scope:
        raise ValueError("Declared correspondence targets differ from examined material")
    conserved, document_refs = [], set()
    for document in documents:
        if not isinstance(document, DocumentaryMaterial):
            raise TypeError("Expected DocumentaryMaterial")
        document = DocumentaryMaterial.model_validate(document.model_dump(mode="python"))
        _reference(document.document_ref)
        if document.document_ref in document_refs:
            raise ValueError("Duplicate document reference")
        document_refs.add(document.document_ref)
        conserved.append(dict(document_ref=document.document_ref,
            content_base64=base64.b64encode(document.content).decode("ascii"),
            sha256=sha256(document.content).hexdigest()))
    if designation_ref not in document_refs:
        raise ValueError("Designation document must be conserved")

    def check_locators(locators):
        for locator in locators:
            _reference(locator.document_ref)
            _reference(locator.section)
            if locator.document_ref not in document_refs:
                raise ValueError("Foreign documentary locator")

    supplied_declarations = []
    for declaration in declarations:
        if not isinstance(declaration, DesignationDeclaration):
            raise TypeError("Expected DesignationDeclaration")
        declaration = DesignationDeclaration.model_validate(declaration.model_dump(mode="python"))
        _reference(declaration.text)
        check_locators(declaration.locators)
        supplied_declarations.append(declaration.model_dump(mode="json"))
    supplied_observations, seen = [], set()
    for observation in observations:
        if not isinstance(observation, DesignationObservation):
            raise TypeError("Expected DesignationObservation")
        observation = DesignationObservation.model_validate(observation.model_dump(mode="python"))
        _reference(observation.note)
        if observation.condition in seen:
            raise ValueError("Duplicate condition observation")
        if observation.outcome == "DECLARED_CONSISTENT" and not observation.locators:
            raise ValueError("Consistent declaration requires supplied support")
        check_locators(observation.locators)
        seen.add(observation.condition)
        supplied_observations.append(observation.model_dump(mode="json"))
    payload = dict(schema_version="DOC-PAY-DESIG-01/v0.1", link_ref=link_ref,
        review=source, review_fingerprint=review.fingerprint, designation_ref=designation_ref,
        designation_kind=designation_kind, reviewer_ref=reviewer_ref, company_scope=company_scope,
        documents=conserved, declarations=supplied_declarations, observations=supplied_observations,
        control_inventory=list(CONDITIONS), pending_controls=[c for c in CONDITIONS if c not in seen],
        assurance_scope="PRESENTED_DECLARATIONS_ONLY")
    result = object.__new__(DocumentaryReviewerDesignationLink)
    object.__setattr__(result, "_material", json.dumps(payload, ensure_ascii=False, sort_keys=True,
        separators=(",", ":"), allow_nan=False).encode("utf-8"))
    return result


def validate_designation_link_for_review(
    link: DocumentaryReviewerDesignationLink, review: DocumentaryPaymentHumanReview,
) -> None:
    """Reject reuse on changed review; do not validate identity or mandate."""
    if not isinstance(link, DocumentaryReviewerDesignationLink) or not isinstance(review, DocumentaryPaymentHumanReview):
        raise TypeError("Expected designation link and human review")
    source = link.to_payload()
    if source["review"] != review.to_payload() or source["review_fingerprint"] != review.fingerprint:
        raise ValueError("Designation link belongs to different examined review")
