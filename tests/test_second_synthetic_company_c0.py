"""C0 material for company 002 keeps unevidenced QTG-to-C0 coverage unresolved."""

import pytest
from eios.core.case_provenance import classify_reference_operational_simulation
from eios.rules import AssessmentTraceBinding
from eios.rules.provenance import build_reference_observed_rules_engine_c0_invoker
from examples.reference_business_case_002_material import c0_sources as _sources


def test_second_company_root_trace_payload_is_reproducible():
    first = _sources()[-1]
    second = _sources()[-1]
    assert first.model_dump(mode="json") == second.model_dump(mode="json")


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
