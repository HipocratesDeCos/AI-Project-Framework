"""Preserve bound contextual declarations; never produce quality checks."""
import base64
from dataclasses import dataclass
from datetime import datetime
from hashlib import sha256
import json
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, StrictInt

from .documentary_payment_capture import DocumentaryMaterial
from .documentary_payment_review import _reference
from .finance_quality_preparation import FinanceQualityPreparation
from .treasury_documentary_support import (
    CONDITIONS, TreasuryDocumentarySupport, validate_treasury_support_for_preparation,
)

Condition = Literal["SOURCE_CORRESPONDENCE", "ECONOMIC_CUTOFF", "AMOUNT_SUPPORT",
                    "AVAILABILITY", "RESTRICTIONS", "SOURCE_SUFFICIENCY"]


class ContextualSupportLocator(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)
    origin: Literal["TREASURY_SUPPORT", "ADDITIONAL_ASSESSMENT_MATERIAL"]
    document_ref: str = Field(min_length=1)
    page: StrictInt = Field(gt=0)
    section: str = Field(min_length=1)


class TreasuryContextualDeclaration(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)
    condition: Condition
    criterion_reference: str = Field(min_length=1)
    criterion_version: str = Field(min_length=1)
    applicability: Literal["APPLIES", "DOES_NOT_APPLY", "NOT_DETERMINED"]
    applicability_reason: str = Field(min_length=1)
    necessity: Literal["NECESSARY_FOR_DETERMINED_PROJECTION", "RELEVANT_NOT_NECESSARY", "NOT_DETERMINED"]
    necessity_reason: str = Field(min_length=1)
    impact_reason: str = Field(min_length=1)
    support_assessment: Literal["DECLARED_SUFFICIENT", "DECLARED_INSUFFICIENT", "NOT_ESTABLISHED"]
    support_reason: str = Field(min_length=1)
    observation_conditions: tuple[Condition, ...] = ()
    support_locators: tuple[ContextualSupportLocator, ...] = ()


@dataclass(frozen=True, init=False)
class TreasuryContextualAssessment:
    _material: bytes

    def __init__(self):
        raise TypeError("Use build_treasury_contextual_assessment")

    def to_payload(self) -> dict:
        return json.loads(self._material)

    @property
    def fingerprint(self) -> str:
        return sha256(self._material).hexdigest()

    def additional_document_bytes(self, reference: str) -> bytes:
        for document in self.to_payload()["additional_documents"]:
            if document["document_ref"] == reference:
                return base64.b64decode(document["content_base64"], validate=True)
        raise KeyError(reference)


def build_treasury_contextual_assessment(
    *, preparation: FinanceQualityPreparation, treasury_support: TreasuryDocumentarySupport,
    assessment_ref: str, declarations: tuple[TreasuryContextualDeclaration, ...],
    additional_documents: tuple[DocumentaryMaterial, ...] = (),
    additional_case_kind: Literal["SYNTHETIC", "PRESENTED_OPERATIONAL"] | None = None,
    reviewer_ref: str | None = None, reviewed_at: datetime | None = None,
) -> TreasuryContextualAssessment:
    validate_treasury_support_for_preparation(treasury_support, preparation)
    _reference(assessment_ref)
    if (reviewer_ref is None) != (reviewed_at is None):
        raise ValueError("Reviewer and time must be presented together")
    if reviewer_ref is not None:
        _reference(reviewer_ref)
        if not isinstance(reviewed_at, datetime) or reviewed_at.utcoffset() is None:
            raise ValueError("Aware review time required")
    if type(additional_documents) is not tuple or type(declarations) is not tuple:
        raise TypeError("Explicit document and declaration tuples required")
    if additional_documents:
        if additional_case_kind not in ("SYNTHETIC", "PRESENTED_OPERATIONAL"):
            raise ValueError("Explicit additional material nature required")
    elif additional_case_kind is not None:
        raise ValueError("Additional nature requires additional material")
    source = treasury_support.to_payload()
    prepared = preparation.to_payload()
    treasury_refs = {d["document_ref"] for d in source["documents"]}
    additional_refs, preserved = set(), []
    for document in additional_documents:
        if not isinstance(document, DocumentaryMaterial):
            raise TypeError("Expected documentary material")
        document = DocumentaryMaterial.model_validate(document.model_dump(mode="python"))
        _reference(document.document_ref)
        if document.document_ref in additional_refs | treasury_refs:
            raise ValueError("Duplicate or colliding document reference")
        additional_refs.add(document.document_ref)
        preserved.append(dict(document_ref=document.document_ref,
            content_base64=base64.b64encode(document.content).decode("ascii"),
            sha256=sha256(document.content).hexdigest()))
    criteria = {(c["reference"], c["version"]) for c in prepared["presented_criteria"]}
    observed = {o["condition"] for o in source["observations"]}
    entries, seen = [], set()
    for declaration in declarations:
        if not isinstance(declaration, TreasuryContextualDeclaration):
            raise TypeError("Expected contextual declaration")
        declaration = TreasuryContextualDeclaration.model_validate(declaration.model_dump(mode="python"))
        for value in (declaration.criterion_reference, declaration.criterion_version,
            declaration.applicability_reason, declaration.necessity_reason,
            declaration.impact_reason, declaration.support_reason):
            _reference(value)
        if declaration.condition in seen:
            raise ValueError("Duplicate condition")
        seen.add(declaration.condition)
        if (declaration.criterion_reference, declaration.criterion_version) not in criteria:
            raise ValueError("Criterion not preserved in preparation")
        if declaration.applicability != "APPLIES" and declaration.necessity != "NOT_DETERMINED":
            raise ValueError("Necessity requires declared applicability")
        if len(set(declaration.observation_conditions)) != len(declaration.observation_conditions):
            raise ValueError("Duplicate observation link")
        if not set(declaration.observation_conditions) <= observed:
            raise ValueError("Observation not present in treasury support")
        if declaration.support_assessment == "DECLARED_SUFFICIENT" and not declaration.support_locators:
            raise ValueError("Declared sufficiency requires support locators")
        for locator in declaration.support_locators:
            _reference(locator.document_ref)
            _reference(locator.section)
            refs = treasury_refs if locator.origin == "TREASURY_SUPPORT" else additional_refs
            if locator.document_ref not in refs:
                raise ValueError("Locator not preserved in declared origin")
        entries.append(declaration.model_dump(mode="json"))
    payload = dict(schema_version="FIN-TREASURY-CONTEXT-01/v0.1",
        preparation=prepared, preparation_fingerprint=preparation.fingerprint,
        treasury_support=source, treasury_support_fingerprint=treasury_support.fingerprint,
        assessment_ref=assessment_ref, declarations=entries,
        additional_documents=preserved, additional_case_kind=additional_case_kind,
        reviewer_ref=reviewer_ref, reviewed_at=reviewed_at.isoformat() if reviewed_at else None,
        condition_inventory=list(CONDITIONS),
        pending_conditions=[c for c in CONDITIONS if c not in seen],
        assurance_scope="BOUND_PRESENTED_CONTEXTUAL_DECLARATIONS_ONLY")
    result = object.__new__(TreasuryContextualAssessment)
    object.__setattr__(result, "_material", json.dumps(payload, ensure_ascii=False,
        sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8"))
    return result


def validate_contextual_assessment_for_material(
    assessment: TreasuryContextualAssessment, preparation: FinanceQualityPreparation,
    treasury_support: TreasuryDocumentarySupport,
) -> None:
    if not isinstance(assessment, TreasuryContextualAssessment):
        raise TypeError("Expected constructed contextual assessment")
    validate_treasury_support_for_preparation(treasury_support, preparation)
    payload = assessment.to_payload()
    if (payload["preparation"] != preparation.to_payload()
        or payload["preparation_fingerprint"] != preparation.fingerprint
        or payload["treasury_support"] != treasury_support.to_payload()
        or payload["treasury_support_fingerprint"] != treasury_support.fingerprint):
        raise ValueError("Contextual assessment belongs to different material")
