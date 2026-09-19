"""Preserve bound flow-inventory declarations; never evaluate quality."""
import base64
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from hashlib import sha256
import json
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, StrictInt

from eios.finance.models import FinanceBasicInput

from .documentary_payment_capture import DocumentaryMaterial
from .documentary_payment_review import _reference
from .finance_quality_preparation import FinanceQualityPreparation

AssessmentState = Literal["ESTABLISHED", "NOT_ESTABLISHED", "CONFLICTING"]
HorizonRelevance = Literal[
    "WITHIN_HORIZON", "AFTER_HORIZON", "NON_FUTURE", "NOT_ESTABLISHED", "CONFLICTING"
]


class FlowInventoryLocator(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)
    origin: Literal["FLOW_INVENTORY_MATERIAL", "PAYMENT_CAPTURE"]
    document_ref: str = Field(min_length=1)
    page: StrictInt = Field(gt=0)
    section: str = Field(min_length=1)


class FlowInventoryPerimeter(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)
    perimeter_ref: str = Field(min_length=1)
    description: str = Field(min_length=1)
    company_scope: str = Field(min_length=1)
    as_of_date: date
    horizon_end: date
    currency: str = Field(min_length=3, max_length=3)
    source_refs: tuple[str, ...] = Field(min_length=1)
    coverage_declaration: Literal["DECLARED_COMPLETE", "DECLARED_INCOMPLETE", "NOT_ESTABLISHED"]
    coverage_reason: str = Field(min_length=1)
    limitations: tuple[str, ...] = ()


class FlowInventoryCandidate(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)
    candidate_ref: str = Field(min_length=1)
    perimeter_ref: str = Field(min_length=1)
    declared_flow_type: Literal["PAYMENT", "COLLECTION", "NOT_ESTABLISHED"]
    captured_flow_id: str | None = None
    amount_assessment: AssessmentState
    currency_assessment: AssessmentState
    due_date_assessment: AssessmentState
    economic_membership_assessment: AssessmentState
    horizon_relevance: HorizonRelevance
    economic_identity_ref: str | None = None
    locators: tuple[FlowInventoryLocator, ...] = Field(min_length=1)
    note: str = Field(min_length=1)


class CapturedFlowAssessment(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)
    flow_id: str = Field(min_length=1)
    candidate_refs: tuple[str, ...] = ()
    amount_assessment: AssessmentState
    currency_assessment: AssessmentState
    due_date_assessment: AssessmentState
    economic_membership_assessment: AssessmentState
    duplication_assessment: Literal[
        "DECLARED_UNIQUE", "POSSIBLE_DUPLICATE", "CONFLICTING", "NOT_ESTABLISHED"
    ]
    horizon_relevance: HorizonRelevance
    criterion_reference: str = Field(min_length=1)
    criterion_version: str = Field(min_length=1)
    reason: str = Field(min_length=1)
    locators: tuple[FlowInventoryLocator, ...] = Field(min_length=1)


@dataclass(frozen=True, init=False)
class FinanceFlowCompletenessRecord:
    _material: bytes

    def __init__(self):
        raise TypeError("Use build_finance_flow_completeness_record")

    def to_payload(self) -> dict:
        return json.loads(self._material)

    @property
    def fingerprint(self) -> str:
        return sha256(self._material).hexdigest()

    def document_bytes(self, reference: str) -> bytes:
        for document in self.to_payload()["documents"]:
            if document["document_ref"] == reference:
                return base64.b64decode(document["content_base64"], validate=True)
        raise KeyError(reference)


def _check_relevance(relevance: HorizonRelevance, due_state: AssessmentState,
    due_date: date | None, as_of_date: date, horizon_end: date) -> None:
    if due_state in ("NOT_ESTABLISHED", "CONFLICTING"):
        allowed = "NOT_ESTABLISHED" if due_state == "NOT_ESTABLISHED" else "CONFLICTING"
        if relevance != allowed:
            raise ValueError("Uncertain due date cannot establish horizon position")
        return
    if relevance in ("NOT_ESTABLISHED", "CONFLICTING"):
        return
    if due_date is None:
        return  # Documentary declaration is preserved, not interpreted.
    expected = ("NON_FUTURE" if due_date <= as_of_date else
        "AFTER_HORIZON" if due_date > horizon_end else "WITHIN_HORIZON")
    if relevance != expected:
        raise ValueError("Horizon declaration contradicts captured due date")


def _validate_locator(locator: FlowInventoryLocator, inventory_refs: set[str],
    capture_refs: set[str]) -> None:
    _reference(locator.document_ref); _reference(locator.section)
    refs = inventory_refs if locator.origin == "FLOW_INVENTORY_MATERIAL" else capture_refs
    if locator.document_ref not in refs:
        raise ValueError("Locator is outside its declared material origin")


def build_finance_flow_completeness_record(*, preparation: FinanceQualityPreparation,
    record_ref: str, perimeters: tuple[FlowInventoryPerimeter, ...],
    documents: tuple[DocumentaryMaterial, ...], candidates: tuple[FlowInventoryCandidate, ...],
    flow_assessments: tuple[CapturedFlowAssessment, ...],
    case_kind: Literal["SYNTHETIC", "PRESENTED_OPERATIONAL"],
    presenter_ref: str | None = None, presented_at: datetime | None = None,
) -> FinanceFlowCompletenessRecord:
    if not isinstance(preparation, FinanceQualityPreparation):
        raise TypeError("Expected constructed FinanceQualityPreparation")
    _reference(record_ref)
    if type(perimeters) is not tuple or type(documents) is not tuple \
        or type(candidates) is not tuple or type(flow_assessments) is not tuple:
        raise TypeError("Explicit tuples required")
    if not perimeters:
        raise ValueError("At least one examined perimeter is required")
    if case_kind not in ("SYNTHETIC", "PRESENTED_OPERATIONAL"):
        raise ValueError("Explicit case nature required")
    if (presenter_ref is None) != (presented_at is None):
        raise ValueError("Presenter and time must be supplied together")
    if presenter_ref is not None:
        _reference(presenter_ref)
        if not isinstance(presented_at, datetime) or presented_at.utcoffset() is None:
            raise ValueError("Aware presentation time required")

    prepared = preparation.to_payload()
    finance = FinanceBasicInput.model_validate(
        prepared["capture"]["finance_package"]["finance_input"])
    as_of_date = finance.snapshot.as_of_date
    horizon_end = as_of_date + timedelta(days=finance.horizon_days)
    flows = {flow.flow_id: flow for flow in finance.cash_flows}
    criteria = {(item["reference"], item["version"])
                for item in prepared["presented_criteria"]}
    capture_documents = prepared["capture"]["documents"]
    capture_refs = {item["document_ref"] for item in capture_documents}

    preserved_documents, inventory_refs = [], set()
    for document in documents:
        if not isinstance(document, DocumentaryMaterial):
            raise TypeError("Expected DocumentaryMaterial")
        document = DocumentaryMaterial.model_validate(document.model_dump(mode="python"))
        _reference(document.document_ref)
        if document.document_ref in inventory_refs or document.document_ref in capture_refs:
            raise ValueError("Duplicate or colliding document reference")
        inventory_refs.add(document.document_ref)
        preserved_documents.append(dict(document_ref=document.document_ref,
            content_base64=base64.b64encode(document.content).decode("ascii"),
            sha256=sha256(document.content).hexdigest()))

    perimeter_entries, perimeter_refs = [], set()
    for perimeter in perimeters:
        if not isinstance(perimeter, FlowInventoryPerimeter):
            raise TypeError("Expected FlowInventoryPerimeter")
        perimeter = FlowInventoryPerimeter.model_validate(perimeter.model_dump(mode="python"))
        for value in (perimeter.perimeter_ref, perimeter.description, perimeter.coverage_reason,
                      *perimeter.source_refs, *perimeter.limitations): _reference(value)
        if perimeter.perimeter_ref in perimeter_refs:
            raise ValueError("Duplicate perimeter")
        if len(set(perimeter.source_refs)) != len(perimeter.source_refs):
            raise ValueError("Duplicate perimeter source")
        if not set(perimeter.source_refs) <= inventory_refs:
            raise ValueError("Perimeter source is not preserved")
        if (perimeter.company_scope != finance.snapshot.company_scope
            or perimeter.as_of_date != as_of_date or perimeter.horizon_end != horizon_end
            or perimeter.currency != finance.snapshot.currency):
            raise ValueError("Perimeter differs from prepared financial scope")
        perimeter_refs.add(perimeter.perimeter_ref)
        perimeter_entries.append(perimeter.model_dump(mode="json"))

    candidate_entries, candidate_map = [], {}
    for candidate in candidates:
        if not isinstance(candidate, FlowInventoryCandidate):
            raise TypeError("Expected FlowInventoryCandidate")
        candidate = FlowInventoryCandidate.model_validate(candidate.model_dump(mode="python"))
        for value in (candidate.candidate_ref, candidate.perimeter_ref, candidate.note,
                      candidate.economic_identity_ref):
            if value is not None: _reference(value)
        if candidate.candidate_ref in candidate_map:
            raise ValueError("Duplicate candidate")
        if candidate.perimeter_ref not in perimeter_refs:
            raise ValueError("Candidate belongs to unknown perimeter")
        flow = flows.get(candidate.captured_flow_id) if candidate.captured_flow_id else None
        if candidate.captured_flow_id is not None and flow is None:
            raise ValueError("Candidate references unknown captured flow")
        for locator in candidate.locators:
            _validate_locator(locator, inventory_refs, capture_refs)
        _check_relevance(candidate.horizon_relevance, candidate.due_date_assessment,
            flow.due_date if flow else None, as_of_date, horizon_end)
        candidate_map[candidate.candidate_ref] = candidate
        candidate_entries.append(candidate.model_dump(mode="json"))

    assessment_entries, assessed_flows, linked_candidates = [], set(), set()
    assessment_map = {}
    for assessment in flow_assessments:
        if not isinstance(assessment, CapturedFlowAssessment):
            raise TypeError("Expected CapturedFlowAssessment")
        assessment = CapturedFlowAssessment.model_validate(assessment.model_dump(mode="python"))
        for value in (assessment.flow_id, assessment.criterion_reference,
                      assessment.criterion_version, assessment.reason): _reference(value)
        if assessment.flow_id in assessed_flows:
            raise ValueError("Duplicate captured-flow assessment")
        flow = flows.get(assessment.flow_id)
        if flow is None:
            raise ValueError("Assessment references unknown captured flow")
        if len(set(assessment.candidate_refs)) != len(assessment.candidate_refs):
            raise ValueError("Duplicate candidate link")
        if not set(assessment.candidate_refs) <= candidate_map.keys():
            raise ValueError("Assessment references unknown candidate")
        for ref in assessment.candidate_refs:
            linked = candidate_map[ref].captured_flow_id
            if linked is not None and linked != assessment.flow_id:
                raise ValueError("Candidate is linked to another captured flow")
        if (assessment.criterion_reference, assessment.criterion_version) not in criteria:
            raise ValueError("Criterion not preserved in preparation")
        if assessment.duplication_assessment == "DECLARED_UNIQUE" and not assessment.candidate_refs:
            raise ValueError("Declared uniqueness requires a candidate")
        for locator in assessment.locators:
            _validate_locator(locator, inventory_refs, capture_refs)
        _check_relevance(assessment.horizon_relevance, assessment.due_date_assessment,
            flow.due_date, as_of_date, horizon_end)
        assessed_flows.add(assessment.flow_id); linked_candidates.update(assessment.candidate_refs)
        assessment_map[assessment.flow_id] = assessment
        assessment_entries.append(assessment.model_dump(mode="json"))

    identities: dict[str, set[str]] = {}
    for ref, candidate in candidate_map.items():
        if candidate.economic_identity_ref is None:
            continue
        related = ({candidate.captured_flow_id} if candidate.captured_flow_id else set())
        related |= {flow_id for flow_id, item in assessment_map.items() if ref in item.candidate_refs}
        identities.setdefault(candidate.economic_identity_ref, set()).update(related)
    for related in identities.values():
        if len(related) > 1 and any(assessment_map[flow_id].duplication_assessment == "DECLARED_UNIQUE"
                                    for flow_id in related if flow_id in assessment_map):
            raise ValueError("Shared economic identity contradicts declared uniqueness")

    unmatched = [ref for ref, item in candidate_map.items()
                 if item.captured_flow_id is None and ref not in linked_candidates]
    payload = dict(schema_version="FIN-FLOW-COMP-01/v0.1", preparation=prepared,
        preparation_fingerprint=preparation.fingerprint, record_ref=record_ref,
        case_kind=case_kind, perimeters=perimeter_entries, documents=preserved_documents,
        candidates=candidate_entries, flow_assessments=assessment_entries,
        pending_flow_ids=[flow_id for flow_id in flows if flow_id not in assessed_flows],
        unmatched_candidate_refs=unmatched, presenter_ref=presenter_ref,
        presented_at=presented_at.isoformat() if presented_at else None,
        assurance_scope="BOUND_PRESENTED_FLOW_INVENTORY_DECLARATIONS_ONLY")
    result = object.__new__(FinanceFlowCompletenessRecord)
    object.__setattr__(result, "_material", json.dumps(payload, ensure_ascii=False,
        sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8"))
    return result


def validate_flow_completeness_for_preparation(record: FinanceFlowCompletenessRecord,
    preparation: FinanceQualityPreparation) -> None:
    if not isinstance(record, FinanceFlowCompletenessRecord):
        raise TypeError("Expected constructed FinanceFlowCompletenessRecord")
    payload = record.to_payload()
    if (payload["preparation"] != preparation.to_payload()
        or payload["preparation_fingerprint"] != preparation.fingerprint):
        raise ValueError("Flow completeness record belongs to different preparation")


__all__ = ["AssessmentState", "CapturedFlowAssessment", "FinanceFlowCompletenessRecord",
    "FlowInventoryCandidate", "FlowInventoryLocator", "FlowInventoryPerimeter",
    "HorizonRelevance", "build_finance_flow_completeness_record",
    "validate_flow_completeness_for_preparation"]
