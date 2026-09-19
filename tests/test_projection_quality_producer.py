from dataclasses import FrozenInstanceError

import pytest

from test_finance_decision_input_package import capture  # noqa: F401
from test_finance_quality_preparation import prepared_args  # noqa: F401
from test_required_installment_coverage import material  # noqa: F401
from test_projection_material_envelope import envelope_parts  # noqa: F401
from eios.core.finance_flow_completeness import (
    CapturedFlowAssessment, FlowInventoryCandidate, build_finance_flow_completeness_record,
)
from eios.core.flow_inventory_mandate import build_flow_inventory_mandate_verification
from eios.core.flow_inventory_review import (
    CONDITIONS as FLOW_CONDITIONS, FlowInstallmentReviewFinding,
    FlowInventoryReviewFinding, build_flow_inventory_personal_review,
)
from eios.core.projection_material_envelope import build_projection_material_envelope
from eios.core.projection_quality_producer import (
    ProjectionQualityReceipt, produce_projection_quality,
    validate_projection_quality_receipt,
)
from eios.core.treasury_contextual_assessment import (
    ContextualSupportLocator, TreasuryContextualDeclaration,
    build_treasury_contextual_assessment,
)
from eios.core.treasury_documentary_support import (
    CONDITIONS as TREASURY_CONDITIONS, TreasuryObservation,
    build_treasury_documentary_support,
)
from eios.core.treasury_mandate_verification import build_treasury_mandate_verification
from eios.core.treasury_personal_review import (
    TreasuryReviewFinding, build_treasury_personal_review,
)


def positive_envelope(parts):
    envelope_args = dict(parts["envelope_args"])
    support_args = dict(parts["treasury_support_args"])
    locator = support_args["declaration"].locators[0]
    support_args["observations"] = tuple(TreasuryObservation(condition=condition,
        outcome="DECLARED_CONSISTENT", note="Synthetic positive test only",
        locators=(locator,)) for condition in TREASURY_CONDITIONS)
    support = build_treasury_documentary_support(**support_args)
    contextual_locator = ContextualSupportLocator(origin="TREASURY_SUPPORT",
        document_ref=locator.document_ref, page=locator.page, section=locator.section)
    declarations = tuple(TreasuryContextualDeclaration(condition=condition,
        criterion_reference="criterion-5", criterion_version="1.0",
        applicability="APPLIES", applicability_reason="Required by projection profile",
        necessity="NECESSARY_FOR_DETERMINED_PROJECTION",
        necessity_reason="Opening treasury is required", impact_reason="Affects projection",
        support_assessment="DECLARED_SUFFICIENT", support_reason="Synthetic positive test",
        observation_conditions=(condition,), support_locators=(contextual_locator,))
        for condition in TREASURY_CONDITIONS)
    assessment_args = dict(parts["treasury_assessment_args"], treasury_support=support,
        declarations=declarations)
    assessment = build_treasury_contextual_assessment(**assessment_args)
    mandate_args = dict(parts["treasury_mandate_args"], target=assessment)
    mandate = build_treasury_mandate_verification(**mandate_args)
    review_args = dict(parts["treasury_review_args"], assessment=assessment, mandate=mandate,
        findings=tuple(TreasuryReviewFinding(condition=condition,
            outcome="CONFIRMED_BY_REVIEW", note="Synthetic positive test only",
            locators=(locator,)) for condition in TREASURY_CONDITIONS))
    review = build_treasury_personal_review(**review_args)

    flow_args = dict(parts["flow_record_args"])
    preparation = flow_args["preparation"].to_payload()
    cash_flows = preparation["capture"]["finance_package"]["finance_input"]["cash_flows"]
    as_of = flow_args["perimeters"][0].as_of_date
    horizon_end = flow_args["perimeters"][0].horizon_end
    perimeter = flow_args["perimeters"][0].model_copy(update={
        "coverage_declaration": "DECLARED_COMPLETE",
        "coverage_reason": "Synthetic positive test coverage", "limitations": ()})
    inventory_locator = {"origin": "FLOW_INVENTORY_MATERIAL", "document_ref": "flow-source",
        "page": 1, "section": "Synthetic inventory"}
    candidates, assessments = [], []
    for number, flow in enumerate(cash_flows, start=1):
        relevance = "NON_FUTURE" if flow["due_date"] <= as_of.isoformat() else \
            "AFTER_HORIZON" if flow["due_date"] > horizon_end.isoformat() else "WITHIN_HORIZON"
        candidate_ref = f"candidate-{number}"
        candidates.append(FlowInventoryCandidate(candidate_ref=candidate_ref,
            perimeter_ref=perimeter.perimeter_ref, declared_flow_type=flow["flow_type"],
            captured_flow_id=flow["flow_id"], amount_assessment="ESTABLISHED",
            currency_assessment="ESTABLISHED", due_date_assessment="ESTABLISHED",
            economic_membership_assessment="ESTABLISHED", horizon_relevance=relevance,
            economic_identity_ref=f"economic-{number}", locators=(inventory_locator,),
            note="Synthetic positive candidate"))
        assessments.append(CapturedFlowAssessment(flow_id=flow["flow_id"],
            candidate_refs=(candidate_ref,), amount_assessment="ESTABLISHED",
            currency_assessment="ESTABLISHED", due_date_assessment="ESTABLISHED",
            economic_membership_assessment="ESTABLISHED", duplication_assessment="DECLARED_UNIQUE",
            horizon_relevance=relevance, criterion_reference="criterion-1",
            criterion_version="1.0", reason="Synthetic positive assessment",
            locators=(inventory_locator,)))
    flow_args.update(perimeters=(perimeter,), candidates=tuple(candidates),
        flow_assessments=tuple(assessments))
    flow_record = build_finance_flow_completeness_record(**flow_args)
    flow_mandate_args = dict(parts["flow_mandate_args"], target=flow_record)
    flow_mandate = build_flow_inventory_mandate_verification(**flow_mandate_args)
    flow_ids = tuple(flow["flow_id"] for flow in cash_flows)
    findings = []
    for condition in FLOW_CONDITIONS:
        kwargs = dict(condition=condition, outcome="CONFIRMED_BY_REVIEW",
            note="Synthetic positive review", perimeter_refs=(perimeter.perimeter_ref,))
        if condition in ("HORIZON_CLASSIFICATION", "FLOW_ATTRIBUTE_SUPPORT",
                "ECONOMIC_DUPLICATION"):
            kwargs["flow_ids"] = flow_ids
        if condition == "PURCHASE_PAYMENT_COHERENCE":
            kwargs["installment_findings"] = tuple(FlowInstallmentReviewFinding(
                installment_ref=item["installment_ref"], outcome="CONFIRMED_BY_REVIEW",
                note="Synthetic installment review", flow_ids=(flow_ids[index],))
                for index, item in enumerate(preparation["calendar"]["installments"]))
        findings.append(FlowInventoryReviewFinding(**kwargs))
    flow_review_args = dict(parts["flow_review_args"], target=flow_record,
        mandate=flow_mandate, findings=tuple(findings))
    flow_review = build_flow_inventory_personal_review(**flow_review_args)
    envelope_args.update(treasury_support=support, treasury_assessment=assessment,
        treasury_mandate=mandate, treasury_review=review, flow_record=flow_record,
        flow_mandate=flow_mandate, flow_review=flow_review)
    return build_projection_material_envelope(**envelope_args)


def test_incomplete_synthetic_material_produces_recomputable_no_apto(envelope_parts):
    envelope = build_projection_material_envelope(**envelope_parts["envelope_args"])
    receipt = produce_projection_quality(envelope=envelope, execution_mode="SYNTHETIC_TEST")
    payload = receipt.to_payload()
    assert payload["quality_result"]["status"] == "NO_APTO"
    assert payload["quality_result"]["confidence"] == "BAJA"
    assert payload["operational_effect"] is False
    assert len(payload["control_inventory"]) == 17
    assert payload["gate_checks"] == [item["check"] for item in payload["control_inventory"]]
    validate_projection_quality_receipt(receipt=receipt, envelope=envelope,
        execution_mode="SYNTHETIC_TEST")


def test_complete_positive_synthetic_material_produces_nonoperational_apto(envelope_parts):
    envelope = positive_envelope(envelope_parts)
    receipt = produce_projection_quality(envelope=envelope, execution_mode="SYNTHETIC_TEST")
    payload = receipt.to_payload()
    assert payload["quality_result"]["status"] == "APTO"
    assert payload["quality_result"]["confidence"] == "ALTA"
    assert payload["assurance_scope"] == "SYNTHETIC_TEST_RESULT_ONLY"
    assert any(not item["check"]["applicable"] for item in payload["control_inventory"])
    assert len(payload["quality_result"]["checks"]) < len(payload["control_inventory"])


def test_operational_mode_rejects_any_synthetic_material(envelope_parts):
    with pytest.raises(ValueError, match="rejects synthetic"):
        produce_projection_quality(envelope=positive_envelope(envelope_parts),
            execution_mode="OPERATIONAL")


def test_receipt_identity_immutability_and_mode_recomputation(envelope_parts):
    envelope = build_projection_material_envelope(**envelope_parts["envelope_args"])
    receipt = produce_projection_quality(envelope=envelope, execution_mode="SYNTHETIC_TEST")
    exported = receipt.to_payload(); exported["control_inventory"].clear()
    assert receipt.to_payload()["control_inventory"]
    with pytest.raises(FrozenInstanceError): receipt._material = b"changed"
    with pytest.raises(TypeError): ProjectionQualityReceipt()
    with pytest.raises(ValueError):
        validate_projection_quality_receipt(receipt=receipt, envelope=positive_envelope(envelope_parts),
            execution_mode="SYNTHETIC_TEST")
    with pytest.raises(ValueError):
        validate_projection_quality_receipt(receipt=receipt, envelope=envelope,
            execution_mode="OPERATIONAL")


def test_detached_or_altered_result_is_rejected(envelope_parts):
    envelope = build_projection_material_envelope(**envelope_parts["envelope_args"])
    receipt = produce_projection_quality(envelope=envelope, execution_mode="SYNTHETIC_TEST")
    payload = receipt.to_payload(); payload["quality_result"]["status"] = "APTO"
    forged = object.__new__(ProjectionQualityReceipt)
    object.__setattr__(forged, "_material", __import__("json").dumps(payload).encode())
    with pytest.raises(ValueError, match="not reproducible"):
        validate_projection_quality_receipt(receipt=forged, envelope=envelope,
            execution_mode="SYNTHETIC_TEST")


def test_forged_envelope_and_invalid_mode_are_rejected(envelope_parts):
    envelope = build_projection_material_envelope(**envelope_parts["envelope_args"])
    payload = envelope.to_payload()
    payload["flow_chain"]["record"]["fingerprint"] = "0" * 64
    forged = object.__new__(type(envelope))
    object.__setattr__(forged, "_material", __import__("json").dumps(payload).encode())
    with pytest.raises(ValueError, match="fingerprint"):
        produce_projection_quality(envelope=forged, execution_mode="SYNTHETIC_TEST")
    payload = envelope.to_payload()
    payload["recomputed_membership"]["contains_synthetic_material"] = False
    forged = object.__new__(type(envelope))
    object.__setattr__(forged, "_material", __import__("json").dumps(payload).encode())
    with pytest.raises(ValueError, match="membership"):
        produce_projection_quality(envelope=forged, execution_mode="OPERATIONAL")
    with pytest.raises(ValueError, match="mode"):
        produce_projection_quality(envelope=envelope, execution_mode="OTHER")
    with pytest.raises(TypeError): produce_projection_quality(
        envelope=object(), execution_mode="SYNTHETIC_TEST")


def test_producer_calls_gate_once_and_never_finance(envelope_parts, monkeypatch):
    import eios.core.projection_quality_producer as producer
    calls = []
    real_gate = producer.evaluate_quality
    monkeypatch.setattr(producer, "evaluate_quality",
        lambda checks: (calls.append(checks), real_gate(checks))[1])
    monkeypatch.setattr("eios.finance.provenance.run_provenanced_finance_basic",
        lambda *a, **kw: (_ for _ in ()).throw(AssertionError("Finance invoked")))
    produce_projection_quality(envelope=build_projection_material_envelope(
        **envelope_parts["envelope_args"]), execution_mode="SYNTHETIC_TEST")
    assert len(calls) == 1
