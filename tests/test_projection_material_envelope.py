from dataclasses import FrozenInstanceError
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from hashlib import sha256

import pytest

from test_finance_decision_input_package import capture  # noqa: F401
from test_required_installment_coverage import material  # noqa: F401
from test_finance_quality_preparation import prepared_args  # noqa: F401
from eios.core.documentary_payment_capture import DocumentaryLocator, DocumentaryMaterial
from eios.core.finance_flow_completeness import (
    FinanceFlowCompletenessRecord, FlowInventoryPerimeter,
    build_finance_flow_completeness_record,
)
from eios.core.finance_quality_preparation import (
    PresentedQualityCriteria, build_finance_quality_preparation,
)
from eios.core.flow_inventory_mandate import (
    CONDITIONS as FLOW_MANDATE_CONDITIONS, FlowMandateLocator,
    FlowMandateObservation, build_flow_inventory_mandate_verification,
)
from eios.core.flow_inventory_review import build_flow_inventory_personal_review
from eios.core.projection_criteria_manifest import (
    AuthorizedProjectionCriterion, REQUIRED_FUNCTIONS,
    build_projection_criteria_manifest,
)
from eios.core.projection_material_envelope import (
    ProjectionMaterialEnvelope, build_projection_material_envelope,
)
from eios.core.treasury_contextual_assessment import build_treasury_contextual_assessment
from eios.core.treasury_documentary_support import (
    TreasuryDeclaration, build_treasury_documentary_support,
)
from eios.core.treasury_mandate_verification import (
    CONDITIONS as TREASURY_MANDATE_CONDITIONS, MandateVerificationLocator,
    MandateVerificationObservation, build_treasury_mandate_verification,
)
from eios.core.treasury_personal_review import build_treasury_personal_review


NOW = datetime(2026, 9, 19, 12, tzinfo=timezone.utc)


@pytest.fixture
def envelope_parts(prepared_args):
    materials = {function: f"Authorized synthetic criterion {n}".encode()
        for n, function in enumerate(REQUIRED_FUNCTIONS, start=1)}
    presented = tuple(PresentedQualityCriteria(reference=f"criterion-{n}", version="1.0",
        content=materials[function]) for n, function in enumerate(REQUIRED_FUNCTIONS, start=1))
    prepared_args["criteria"] = presented
    preparation = build_finance_quality_preparation(**prepared_args)
    manifest = build_projection_criteria_manifest(manifest_ref="projection-only-manifest",
        manifest_version="1.0", authority_ref="owner-approved-criteria", authorized_at=NOW,
        criteria=tuple(AuthorizedProjectionCriterion(function=function,
            reference=f"criterion-{n}", version="1.0",
            content_sha256=sha256(materials[function]).hexdigest())
            for n, function in enumerate(REQUIRED_FUNCTIONS, start=1)))

    finance = preparation.to_payload()["capture"]["finance_package"]["finance_input"]
    snapshot = finance["snapshot"]
    treasury_document = DocumentaryMaterial(document_ref="treasury-source", content=b"Synthetic treasury")
    treasury_support_args = dict(preparation=preparation, record_ref="treasury-support",
        target_company_scope=snapshot["company_scope"], case_kind="SYNTHETIC",
        documents=(treasury_document,), declaration=TreasuryDeclaration(
            documentary_company=snapshot["company_scope"], currency=snapshot["currency"],
            economic_date=date.fromisoformat(snapshot["as_of_date"]),
            available_amount=Decimal(snapshot["available_treasury"]), locators=(DocumentaryLocator(
                document_ref="treasury-source", page=1, section="Balance"),)))
    treasury_support = build_treasury_documentary_support(**treasury_support_args)
    treasury_assessment_args = dict(preparation=preparation,
        treasury_support=treasury_support, assessment_ref="treasury-context", declarations=())
    treasury_assessment = build_treasury_contextual_assessment(**treasury_assessment_args)
    treasury_mandate_args = dict(target=treasury_assessment,
        verification_ref="treasury-mandate-check", company_scope=snapshot["company_scope"],
        reviewer_ref="reviewer", mandate_ref="treasury-mandate", target_review_ref="treasury-review",
        verifier_ref="verifier", verified_at=NOW, channel_ref="channel", channel_kind="SYNTHETIC",
        recognition_basis="INDEPENDENTLY_SUPPORTED", mandate_kind="SYNTHETIC",
        mandate_documents=(DocumentaryMaterial(document_ref="t-mandate", content=b"Synthetic"),),
        channel_recognition_documents=(DocumentaryMaterial(document_ref="t-channel", content=b"Synthetic"),),
        contrast_documents=(DocumentaryMaterial(document_ref="t-contrast", content=b"Synthetic"),),
        observations=tuple(MandateVerificationObservation(condition=condition,
            outcome="CONFIRMED_BY_CONTRAST", note="Synthetic only", locators=(
                MandateVerificationLocator(origin="CONTRAST_SUPPORT", document_ref="t-contrast",
                    page=1, section="Mock"),)) for condition in TREASURY_MANDATE_CONDITIONS))
    treasury_mandate = build_treasury_mandate_verification(**treasury_mandate_args)
    treasury_review_args = dict(assessment=treasury_assessment, mandate=treasury_mandate,
        review_ref="treasury-review", reviewer_ref="reviewer", reviewed_at=NOW, findings=())
    treasury_review = build_treasury_personal_review(**treasury_review_args)

    as_of = date.fromisoformat(snapshot["as_of_date"])
    perimeter = FlowInventoryPerimeter(perimeter_ref="all-ledgers", description="Synthetic inventory",
        company_scope=snapshot["company_scope"], as_of_date=as_of,
        horizon_end=as_of + timedelta(days=finance["horizon_days"]), currency=snapshot["currency"],
        source_refs=("flow-source",), coverage_declaration="DECLARED_INCOMPLETE",
        coverage_reason="Synthetic empty assessment")
    flow_record_args = dict(preparation=preparation, record_ref="flow-record",
        perimeters=(perimeter,), documents=(DocumentaryMaterial(
            document_ref="flow-source", content=b"Synthetic flow inventory"),),
        candidates=(), flow_assessments=(), case_kind="SYNTHETIC")
    flow_record = build_finance_flow_completeness_record(**flow_record_args)
    flow_mandate_args = dict(target=flow_record, verification_ref="flow-mandate-check",
        company_scope=snapshot["company_scope"], reviewer_ref="reviewer",
        mandate_ref="flow-mandate", target_review_ref="flow-review", verifier_ref="verifier",
        verified_at=NOW, channel_ref="channel", channel_kind="SYNTHETIC",
        recognition_basis="INDEPENDENTLY_SUPPORTED", mandate_kind="SYNTHETIC",
        mandate_documents=(DocumentaryMaterial(document_ref="f-mandate", content=b"Synthetic"),),
        channel_recognition_documents=(DocumentaryMaterial(document_ref="f-channel", content=b"Synthetic"),),
        contrast_documents=(DocumentaryMaterial(document_ref="f-contrast", content=b"Synthetic"),),
        observations=tuple(FlowMandateObservation(condition=condition,
            outcome="CONFIRMED_BY_CONTRAST", note="Synthetic only", locators=(FlowMandateLocator(
                origin="CONTRAST_SUPPORT", document_ref="f-contrast", page=1, section="Mock"),))
            for condition in FLOW_MANDATE_CONDITIONS))
    flow_mandate = build_flow_inventory_mandate_verification(**flow_mandate_args)
    flow_review_args = dict(target=flow_record, mandate=flow_mandate, review_ref="flow-review",
        reviewer_ref="reviewer", reviewed_at=NOW, findings=())
    flow_review = build_flow_inventory_personal_review(**flow_review_args)
    envelope_args = dict(preparation=preparation, criteria_manifest=manifest,
        treasury_support=treasury_support, treasury_assessment=treasury_assessment,
        treasury_mandate=treasury_mandate, treasury_review=treasury_review,
        flow_record=flow_record, flow_mandate=flow_mandate, flow_review=flow_review)
    return dict(envelope_args=envelope_args, materials=materials,
        treasury_support_args=treasury_support_args,
        treasury_assessment_args=treasury_assessment_args,
        treasury_mandate_args=treasury_mandate_args,
        treasury_review_args=treasury_review_args, flow_record_args=flow_record_args,
        flow_mandate_args=flow_mandate_args, flow_review_args=flow_review_args)


def test_envelope_binds_both_exact_chains_and_recomputes_membership(envelope_parts):
    result = build_projection_material_envelope(**envelope_parts["envelope_args"])
    payload = result.to_payload(); membership = payload["recomputed_membership"]
    assert payload["profile"] == "PROJECTION_ONLY"
    assert len(membership["treasury_pending_conditions"]) == 6
    assert len(membership["flow_pending_conditions"]) == 9
    assert membership["unassessed_captured_flow_ids"] == ["payment-1", "payment-2"]
    assert membership["unreviewed_required_installment_refs"] == [
        "PED-2026-015 / cuota 1", "PED-2026-015 / cuota 2"]
    assert membership["contains_synthetic_material"] is True
    assert payload["assurance_scope"] == "EXACT_BOUND_PROJECTION_MATERIAL_ONLY"
    assert not {"quality_checks", "quality_result", "status", "authorized"} & payload.keys()


@pytest.mark.parametrize("foreign", ["manifest", "treasury_support", "treasury_assessment",
    "treasury_mandate", "treasury_review", "flow_record", "flow_mandate", "flow_review"])
def test_any_foreign_component_is_rejected(envelope_parts, foreign):
    parts, args = envelope_parts, dict(envelope_parts["envelope_args"])
    if foreign == "manifest":
        materials = dict(parts["materials"]); materials[REQUIRED_FUNCTIONS[0]] = b"changed"
        args["criteria_manifest"] = build_projection_criteria_manifest(
            manifest_ref="other", manifest_version="1.0", authority_ref="other", authorized_at=NOW,
            criteria=tuple(AuthorizedProjectionCriterion(function=function,
                reference=f"criterion-{n}", version="1.0",
                content_sha256=sha256(materials[function]).hexdigest())
                for n, function in enumerate(REQUIRED_FUNCTIONS, start=1)))
    elif foreign == "treasury_support":
        changed = dict(parts["treasury_support_args"], record_ref="other")
        args[foreign] = build_treasury_documentary_support(**changed)
    elif foreign == "treasury_assessment":
        changed = dict(parts["treasury_assessment_args"], assessment_ref="other")
        args[foreign] = build_treasury_contextual_assessment(**changed)
    elif foreign == "treasury_mandate":
        changed = dict(parts["treasury_mandate_args"], channel_ref="other")
        args[foreign] = build_treasury_mandate_verification(**changed)
    elif foreign == "treasury_review":
        other_mandate = build_treasury_mandate_verification(
            **dict(parts["treasury_mandate_args"], channel_ref="other"))
        changed = dict(parts["treasury_review_args"], mandate=other_mandate)
        args[foreign] = build_treasury_personal_review(**changed)
    elif foreign == "flow_record":
        changed = dict(parts["flow_record_args"], record_ref="other")
        args[foreign] = build_finance_flow_completeness_record(**changed)
    elif foreign == "flow_mandate":
        changed = dict(parts["flow_mandate_args"], channel_ref="other")
        args[foreign] = build_flow_inventory_mandate_verification(**changed)
    else:
        other_mandate = build_flow_inventory_mandate_verification(
            **dict(parts["flow_mandate_args"], channel_ref="other"))
        changed = dict(parts["flow_review_args"], mandate=other_mandate)
        args[foreign] = build_flow_inventory_personal_review(**changed)
    with pytest.raises(ValueError): build_projection_material_envelope(**args)


def test_envelope_identity_and_immutable_exports(envelope_parts):
    result = build_projection_material_envelope(**envelope_parts["envelope_args"])
    payload = result.to_payload(); payload["flow_chain"].clear()
    assert result.to_payload()["flow_chain"]
    with pytest.raises(FrozenInstanceError): result._material = b"changed"
    with pytest.raises(TypeError): ProjectionMaterialEnvelope()
    changed = dict(envelope_parts["flow_review_args"], reviewed_at=NOW + timedelta(seconds=1))
    envelope_parts["envelope_args"]["flow_review"] = build_flow_inventory_personal_review(**changed)
    assert build_projection_material_envelope(
        **envelope_parts["envelope_args"]).fingerprint != result.fingerprint


def test_no_finance_or_quality_execution(envelope_parts, monkeypatch):
    def forbidden(*args, **kwargs): raise AssertionError("Engine invoked")
    monkeypatch.setattr("eios.finance.provenance.run_provenanced_finance_basic", forbidden)
    monkeypatch.setattr("eios.quality.gate.evaluate_quality", forbidden)
    build_projection_material_envelope(**envelope_parts["envelope_args"])


def test_unconstructed_inputs_are_rejected(envelope_parts):
    for name in envelope_parts["envelope_args"]:
        args = dict(envelope_parts["envelope_args"]); args[name] = object()
        with pytest.raises(TypeError): build_projection_material_envelope(**args)
