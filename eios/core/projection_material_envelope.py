"""Aggregate exact PROJECTION_ONLY material without producing quality checks."""
from dataclasses import dataclass
from hashlib import sha256
import json

from .finance_flow_completeness import (
    FinanceFlowCompletenessRecord, validate_flow_completeness_for_preparation,
)
from .finance_quality_preparation import FinanceQualityPreparation
from .flow_inventory_mandate import (
    FlowInventoryMandateVerification, validate_flow_mandate_for_target,
)
from .flow_inventory_review import (
    CONDITIONS as FLOW_CONDITIONS, FlowInventoryPersonalReview,
    validate_flow_review_for_material,
)
from .projection_criteria_manifest import (
    ProjectionCriteriaManifest, validate_preparation_criteria_against_manifest,
)
from .treasury_contextual_assessment import (
    TreasuryContextualAssessment, validate_contextual_assessment_for_material,
)
from .treasury_documentary_support import (
    TreasuryDocumentarySupport, validate_treasury_support_for_preparation,
)
from .treasury_mandate_verification import (
    TreasuryMandateVerification, validate_mandate_verification_for_target,
)
from .treasury_personal_review import (
    CONDITIONS as TREASURY_CONDITIONS, TreasuryPersonalReview,
    validate_treasury_review_for_material,
)


@dataclass(frozen=True, init=False)
class ProjectionMaterialEnvelope:
    _material: bytes

    def __init__(self):
        raise TypeError("Use build_projection_material_envelope")

    def to_payload(self) -> dict:
        return json.loads(self._material)

    @property
    def fingerprint(self) -> str:
        return sha256(self._material).hexdigest()


def _bound(record) -> dict:
    return {"payload": record.to_payload(), "fingerprint": record.fingerprint}


def build_projection_material_envelope(*, preparation: FinanceQualityPreparation,
    criteria_manifest: ProjectionCriteriaManifest,
    treasury_support: TreasuryDocumentarySupport,
    treasury_assessment: TreasuryContextualAssessment,
    treasury_mandate: TreasuryMandateVerification,
    treasury_review: TreasuryPersonalReview,
    flow_record: FinanceFlowCompletenessRecord,
    flow_mandate: FlowInventoryMandateVerification,
    flow_review: FlowInventoryPersonalReview) -> ProjectionMaterialEnvelope:
    """Validate exact chain membership and preserve a deterministic envelope."""
    if not isinstance(preparation, FinanceQualityPreparation):
        raise TypeError("Expected constructed FinanceQualityPreparation")
    if not isinstance(criteria_manifest, ProjectionCriteriaManifest):
        raise TypeError("Expected constructed ProjectionCriteriaManifest")
    validate_preparation_criteria_against_manifest(preparation, criteria_manifest)

    validate_treasury_support_for_preparation(treasury_support, preparation)
    validate_contextual_assessment_for_material(
        treasury_assessment, preparation, treasury_support)
    validate_mandate_verification_for_target(treasury_mandate, treasury_assessment)
    validate_treasury_review_for_material(
        treasury_review, treasury_assessment, treasury_mandate)

    validate_flow_completeness_for_preparation(flow_record, preparation)
    validate_flow_mandate_for_target(flow_mandate, flow_record)
    validate_flow_review_for_material(flow_review, flow_record, flow_mandate)

    prepared = preparation.to_payload()
    treasury_support_payload = treasury_support.to_payload()
    treasury_assessment_payload = treasury_assessment.to_payload()
    treasury_mandate_payload = treasury_mandate.to_payload()
    treasury_review_payload = treasury_review.to_payload()
    flow_payload = flow_record.to_payload()
    flow_mandate_payload = flow_mandate.to_payload()
    flow_review_payload = flow_review.to_payload()

    if treasury_mandate_payload["purpose_scope"] != \
            "TREASURY_REVIEW_FOR_DOCUMENTARY_CUTOFF_PILOT":
        raise ValueError("Treasury mandate has foreign purpose scope")
    if flow_mandate_payload["purpose_scope"] != \
            "FLOW_INVENTORY_REVIEW_FOR_PROJECTION_ONLY":
        raise ValueError("Flow mandate has foreign purpose scope")

    treasury_seen = {item["condition"] for item in treasury_review_payload["findings"]}
    flow_seen = {item["condition"] for item in flow_review_payload["findings"]}
    assessed_flow_ids = {item["flow_id"] for item in flow_payload["flow_assessments"]}
    captured_flow_ids = {item["flow_id"] for item in prepared["capture"][
        "finance_package"]["finance_input"]["cash_flows"]}
    candidate_refs = {item["candidate_ref"] for item in flow_payload["candidates"]}
    linked_candidate_refs = {ref for item in flow_payload["flow_assessments"]
                             for ref in item["candidate_refs"]}
    captured_candidate_refs = {item["candidate_ref"] for item in flow_payload["candidates"]
                               if item["captured_flow_id"] is not None}
    required_installments = {item["installment_ref"]
        for item in prepared["calendar"]["installments"]}
    reviewed_installments = {item["installment_ref"]
        for finding in flow_review_payload["findings"]
        if finding["condition"] == "PURCHASE_PAYMENT_COHERENCE"
        for item in finding["installment_findings"]}

    natures = {
        "payment_capture": prepared["capture"]["case_kind"],
        "required_calendar": prepared["calendar"]["case_kind"],
        "treasury_support": treasury_support_payload["case_kind"],
        "treasury_additional_material": treasury_assessment_payload["additional_case_kind"],
        "treasury_mandate": treasury_mandate_payload["mandate_kind"],
        "flow_inventory": flow_payload["case_kind"],
        "flow_mandate": flow_mandate_payload["mandate_kind"],
    }
    membership = dict(
        treasury_pending_conditions=[c for c in TREASURY_CONDITIONS if c not in treasury_seen],
        flow_pending_conditions=[c for c in FLOW_CONDITIONS if c not in flow_seen],
        unassessed_captured_flow_ids=sorted(captured_flow_ids - assessed_flow_ids),
        unmatched_candidate_refs=sorted(candidate_refs - linked_candidate_refs - captured_candidate_refs),
        unreviewed_required_installment_refs=sorted(required_installments - reviewed_installments),
        material_natures=natures,
        contains_synthetic_material=any(value == "SYNTHETIC" for value in natures.values()),
    )
    payload = dict(schema_version="QTG-PROJECTION-MATERIAL-01/v0.1",
        profile="PROJECTION_ONLY", preparation=_bound(preparation),
        criteria_manifest=_bound(criteria_manifest),
        treasury_chain=dict(support=_bound(treasury_support),
            assessment=_bound(treasury_assessment), mandate=_bound(treasury_mandate),
            review=_bound(treasury_review)),
        flow_chain=dict(record=_bound(flow_record), mandate=_bound(flow_mandate),
            review=_bound(flow_review)), recomputed_membership=membership,
        assurance_scope="EXACT_BOUND_PROJECTION_MATERIAL_ONLY")
    result = object.__new__(ProjectionMaterialEnvelope)
    object.__setattr__(result, "_material", json.dumps(payload, ensure_ascii=False,
        sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8"))
    return result


__all__ = ["ProjectionMaterialEnvelope", "build_projection_material_envelope"]
