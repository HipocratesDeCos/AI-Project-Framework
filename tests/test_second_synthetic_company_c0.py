"""C0 material for company 002 keeps unevidenced QTG-to-C0 coverage unresolved."""
from pathlib import Path

import pytest

from eios.core.c0_reproducibility import build_trace
from eios.core.case_provenance import classify_reference_operational_simulation
from eios.core.models import DecisionContext, Evidence, PurchaseOperation
from eios.core.projection_mock_dataset import load_projection_mock_dataset
from eios.core.projection_synthetic_adapter import build_projection_only_synthetic_material_bundle
from eios.data_sufficiency import (
    DECISION_EVIDENCE_SUFFICIENCY_EVIDENCE_SOURCE_TYPE,
    DecisionEvidenceRequirementSet, DecisionEvidenceSufficiencyProducer,
    RequirementEvidenceBinding, decision_evidence_purchase_ref,
    decision_evidence_sufficiency_ref,
)
from eios.rules import AssessmentTraceBinding
from eios.rules.catalog import authorized_rule
from eios.rules.data_quality import evaluate_r_dat_003
from eios.rules.provenance import build_reference_observed_rules_engine_c0_invoker


FIXTURE = Path(__file__).parent / "fixtures" / "reference_business_case_002_semantic"


def _sources():
    bundle = build_projection_only_synthetic_material_bundle(
        load_projection_mock_dataset(FIXTURE)
    )
    dip = bundle.envelope.to_payload()["preparation"]["payload"]["capture"][
        "finance_package"
    ]["decision_input_package"]
    purchase = PurchaseOperation.model_validate(dip["purchase"])
    context = DecisionContext.model_validate(dip["context"])
    authority = "AUTH-REF-BUSINESS-002-DATA"
    methodology = "METHOD-REF-BUSINESS-002-DATA"
    requirement_set = DecisionEvidenceRequirementSet(
        decision_id=context.decision_id, scenario_id=context.scenario_id,
        data_snapshot_id=context.data_snapshot_id,
        company_scope="COMPANY-MOCK-002",
        purchase_operation_ref=decision_evidence_purchase_ref(purchase),
        effective_date=purchase.operation_date,
        requirement_set_id="REQSET-REF-BUSINESS-002",
        requirement_set_version="1.0",
        requirement_ids=("REQ-PROJECTION-QUALITY",),
        authority_ref=authority, methodology_ref=methodology,
        trace_refs=("trace:reference:business:002:requirements",),
    )
    binding = RequirementEvidenceBinding(
        requirement_id="REQ-PROJECTION-QUALITY", classification="UNDETERMINED",
        authority_ref=authority,
        trace_refs=("trace:reference:business:002:requirement:qtg:undetermined",),
    )
    observation = DecisionEvidenceSufficiencyProducer(
        authority_ref=authority, methodology_ref=methodology,
    ).produce(
        purchase=purchase, context=context, company_scope="COMPANY-MOCK-002",
        state="AVAILABLE", requirement_set=requirement_set, bindings=(binding,),
        source_ref="reference:business:002:data-sufficiency",
        trace_refs=("trace:reference:business:002:data-sufficiency",),
    )
    sufficiency_evidence = Evidence(
        evidence_id="E-REF-002-DAT003",
        source_type=DECISION_EVIDENCE_SUFFICIENCY_EVIDENCE_SOURCE_TYPE,
        source_ref="reference:business:002:data-sufficiency:evidence",
        captured_at=purchase.operation_date, state="DEMONSTRATED",
        demonstration_ref=decision_evidence_sufficiency_ref(observation),
    )
    rule = authorized_rule("R-DAT-003", context.rules_version)
    assessment = evaluate_r_dat_003(
        purchase=purchase, context=context, rule=rule,
        observation=observation, sufficiency_evidence=sufficiency_evidence,
    )
    trace = build_trace(context, purchase, rule, tuple(assessment.evidence_ids), assessment)
    return bundle, purchase, context, observation, assessment, trace


def test_second_company_c0_preserves_undetermined_requirement():
    bundle, purchase, context, observation, assessment, trace = _sources()
    provenance = classify_reference_operational_simulation(
        bundle=bundle, reference_case_id="REF-BUSINESS-002"
    ).to_payload()
    assert (provenance["material_nature"], provenance["qtg_mode_policy"],
            provenance["operational_path"], provenance["effect_scope"],
            provenance["decision_authority"]) == (
                "SYNTHETIC", "SYNTHETIC_TEST_ONLY", "FORBIDDEN",
                "NO_OPERATIONAL_EFFECT", False,
            )
    assert observation.company_scope == "COMPANY-MOCK-002"
    assert observation.satisfied_requirement_ids == ()
    assert observation.undetermined_requirement_ids == ("REQ-PROJECTION-QUALITY",)
    assert (assessment.status, assessment.outcome) == ("EVALUABLE", "TRUE")
    invoker = build_reference_observed_rules_engine_c0_invoker(
        bindings=(AssessmentTraceBinding(assessment=assessment, trace=trace),),
        base_result="INFORMACIÓN INSUFICIENTE",
        reference_case_id=provenance["reference_case_id"],
    )
    capability = invoker(purchase, context)
    capture = invoker.capture()
    assert capture.capability == capability
    assert capture.result.assessments == (assessment,)
    assert capture.result.traces == (trace,)
    assert capture.result.crc_result.consolidated_result == "INFORMACIÓN INSUFICIENTE"
    assert capability.trace_references == (trace.trace_id,)
    with pytest.raises(ValueError, match="single-use"):
        invoker(purchase, context)


def test_second_company_c0_rejects_foreign_purchase():
    _, purchase, context, _, assessment, trace = _sources()
    invoker = build_reference_observed_rules_engine_c0_invoker(
        bindings=(AssessmentTraceBinding(assessment=assessment, trace=trace),),
        base_result="INFORMACIÓN INSUFICIENTE", reference_case_id="REF-BUSINESS-002",
    )
    with pytest.raises(ValueError, match="input_fingerprint"):
        invoker(purchase.model_copy(update={"supplier_id": "FOREIGN"}), context)
    with pytest.raises(ValueError, match="unavailable"):
        invoker.capture()
