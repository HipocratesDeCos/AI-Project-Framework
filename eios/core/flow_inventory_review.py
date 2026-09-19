"""Preserve personal flow-inventory findings without evaluating quality."""
from dataclasses import dataclass
from datetime import datetime
from hashlib import sha256
import json
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from .documentary_payment_review import _reference
from .finance_flow_completeness import FinanceFlowCompletenessRecord, FlowInventoryLocator
from .flow_inventory_mandate import FlowInventoryMandateVerification, validate_flow_mandate_for_target

CONDITIONS = ("PERIMETER_COVERAGE", "SOURCE_COVERAGE", "CAPTURED_FLOW_COVERAGE",
    "UNMATCHED_CANDIDATES", "HORIZON_CLASSIFICATION", "FLOW_ATTRIBUTE_SUPPORT",
    "ECONOMIC_DUPLICATION", "PURCHASE_PAYMENT_COHERENCE", "CONFLICTS_AND_LIMITATIONS")
Condition = Literal["PERIMETER_COVERAGE", "SOURCE_COVERAGE", "CAPTURED_FLOW_COVERAGE",
    "UNMATCHED_CANDIDATES", "HORIZON_CLASSIFICATION", "FLOW_ATTRIBUTE_SUPPORT",
    "ECONOMIC_DUPLICATION", "PURCHASE_PAYMENT_COHERENCE", "CONFLICTS_AND_LIMITATIONS"]


class FlowInstallmentReviewFinding(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)
    installment_ref: str = Field(min_length=1)
    outcome: Literal["CONFIRMED_BY_REVIEW", "NOT_CONFIRMED", "CONFLICT_REPORTED"]
    note: str = Field(min_length=1)
    locators: tuple[FlowInventoryLocator, ...] = ()
    flow_ids: tuple[str, ...] = ()


class FlowInventoryReviewFinding(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)
    condition: Condition
    outcome: Literal["CONFIRMED_BY_REVIEW", "NOT_CONFIRMED", "CONFLICT_REPORTED"]
    note: str = Field(min_length=1)
    locators: tuple[FlowInventoryLocator, ...] = ()
    perimeter_refs: tuple[str, ...] = ()
    candidate_refs: tuple[str, ...] = ()
    flow_ids: tuple[str, ...] = ()
    installment_findings: tuple[FlowInstallmentReviewFinding, ...] = ()


@dataclass(frozen=True, init=False)
class FlowInventoryPersonalReview:
    _material: bytes
    def __init__(self): raise TypeError("Use build_flow_inventory_personal_review")
    def to_payload(self) -> dict: return json.loads(self._material)
    @property
    def fingerprint(self) -> str: return sha256(self._material).hexdigest()


def build_flow_inventory_personal_review(*, target: FinanceFlowCompletenessRecord,
    mandate: FlowInventoryMandateVerification, review_ref: str, reviewer_ref: str,
    reviewed_at: datetime, findings: tuple[FlowInventoryReviewFinding, ...],
    previous_review_ref: str | None = None) -> FlowInventoryPersonalReview:
    validate_flow_mandate_for_target(mandate, target)
    for value in (review_ref, reviewer_ref): _reference(value)
    if previous_review_ref is not None:
        _reference(previous_review_ref)
        if previous_review_ref == review_ref: raise ValueError("Previous review cannot be itself")
    if not isinstance(reviewed_at, datetime) or reviewed_at.utcoffset() is None:
        raise ValueError("Aware review time required")
    mandate_payload, target_payload = mandate.to_payload(), target.to_payload()
    if mandate_payload["reviewer_ref"] != reviewer_ref: raise ValueError("Reviewer differs from mandate")
    if mandate_payload["target_review_ref"] != review_ref: raise ValueError("Review reference differs from mandate")
    perimeter_refs = {item["perimeter_ref"] for item in target_payload["perimeters"]}
    candidate_refs = {item["candidate_ref"] for item in target_payload["candidates"]}
    finance = target_payload["preparation"]["capture"]["finance_package"]["finance_input"]
    flow_ids = {item["flow_id"] for item in finance["cash_flows"]}
    required_installments = {item["installment_ref"]
        for item in target_payload["preparation"]["calendar"]["installments"]}
    inventory_docs = {item["document_ref"] for item in target_payload["documents"]}
    payment_docs = {item["document_ref"] for item in target_payload["preparation"]["capture"]["documents"]}
    if type(findings) is not tuple: raise TypeError("Explicit finding tuple required")
    entries, seen = [], set()
    for finding in findings:
        if not isinstance(finding, FlowInventoryReviewFinding): raise TypeError("Expected flow review finding")
        finding = FlowInventoryReviewFinding.model_validate(finding.model_dump(mode="python"))
        _reference(finding.note)
        if finding.condition in seen: raise ValueError("Duplicate condition")
        seen.add(finding.condition)
        references = (finding.perimeter_refs, finding.candidate_refs, finding.flow_ids)
        if any(len(set(items)) != len(items) for items in references): raise ValueError("Duplicate structural reference")
        if not set(finding.perimeter_refs) <= perimeter_refs or not set(finding.candidate_refs) <= candidate_refs \
            or not set(finding.flow_ids) <= flow_ids: raise ValueError("Finding references foreign target material")
        if finding.outcome != "CONFLICT_REPORTED" and not (
            finding.locators or any(references) or finding.installment_findings):
            raise ValueError("Confirmed or not-confirmed finding requires support")
        for locator in finding.locators:
            _reference(locator.document_ref); _reference(locator.section)
            refs = inventory_docs if locator.origin == "FLOW_INVENTORY_MATERIAL" else payment_docs
            if locator.document_ref not in refs: raise ValueError("Review locator is outside target material")
        if finding.condition != "PURCHASE_PAYMENT_COHERENCE":
            if finding.installment_findings:
                raise ValueError("Installment findings belong only to purchase-payment coherence")
        else:
            installment_entries, installment_seen, installment_outcomes = [], set(), set()
            for item in finding.installment_findings:
                if not isinstance(item, FlowInstallmentReviewFinding):
                    raise TypeError("Expected installment review finding")
                item = FlowInstallmentReviewFinding.model_validate(item.model_dump(mode="python"))
                _reference(item.installment_ref); _reference(item.note)
                if item.installment_ref in installment_seen: raise ValueError("Duplicate installment finding")
                installment_seen.add(item.installment_ref); installment_outcomes.add(item.outcome)
                if len(set(item.flow_ids)) != len(item.flow_ids) or not set(item.flow_ids) <= flow_ids:
                    raise ValueError("Installment finding references foreign or duplicate flow")
                if item.outcome != "CONFLICT_REPORTED" and not (item.locators or item.flow_ids):
                    raise ValueError("Confirmed or not-confirmed installment requires support")
                for locator in item.locators:
                    _reference(locator.document_ref); _reference(locator.section)
                    refs = inventory_docs if locator.origin == "FLOW_INVENTORY_MATERIAL" else payment_docs
                    if locator.document_ref not in refs:
                        raise ValueError("Installment locator is outside target material")
                installment_entries.append(item.model_dump(mode="json"))
            if installment_seen != required_installments:
                raise ValueError("Purchase-payment coherence requires every required installment")
            derived = ("NOT_CONFIRMED" if "NOT_CONFIRMED" in installment_outcomes else
                "CONFLICT_REPORTED" if "CONFLICT_REPORTED" in installment_outcomes else
                "CONFIRMED_BY_REVIEW")
            if finding.outcome != derived:
                raise ValueError("Purchase-payment outcome contradicts installment findings")
            data = finding.model_dump(mode="json")
            data["installment_findings"] = installment_entries
            entries.append(data)
            continue
        entries.append(finding.model_dump(mode="json"))
    authorized = mandate_payload["verification_outcome"] == "ACREDITADO_POR_CONTRASTE"
    payload = dict(schema_version="FLOW-INVENTORY-REVIEW-01/v0.2", target=target_payload,
        target_fingerprint=target.fingerprint, mandate=mandate_payload,
        mandate_fingerprint=mandate.fingerprint, review_ref=review_ref, reviewer_ref=reviewer_ref,
        reviewed_at=reviewed_at.isoformat(), previous_review_ref=previous_review_ref,
        findings=entries, condition_inventory=list(CONDITIONS),
        pending_conditions=[condition for condition in CONDITIONS if condition not in seen],
        assurance_scope="AUTHORIZED_REVIEWER_PRESENTED_FLOW_FINDINGS" if authorized
            else "PRESENTED_UNAUTHORIZED_OR_UNRESOLVED_FLOW_FINDINGS")
    record = object.__new__(FlowInventoryPersonalReview)
    object.__setattr__(record, "_material", json.dumps(payload, ensure_ascii=False,
        sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8"))
    return record


def validate_flow_review_for_material(review: FlowInventoryPersonalReview,
    target: FinanceFlowCompletenessRecord, mandate: FlowInventoryMandateVerification) -> None:
    if not isinstance(review, FlowInventoryPersonalReview): raise TypeError("Expected constructed flow review")
    validate_flow_mandate_for_target(mandate, target)
    payload = review.to_payload()
    if (payload["target"] != target.to_payload() or payload["target_fingerprint"] != target.fingerprint
        or payload["mandate"] != mandate.to_payload() or payload["mandate_fingerprint"] != mandate.fingerprint):
        raise ValueError("Flow review belongs to different material")
