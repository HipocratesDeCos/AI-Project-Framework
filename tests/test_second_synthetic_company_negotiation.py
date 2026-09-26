"""Synthetic information request for company 002, bound to its unresolved C0 trace."""

import pytest
from eios.core.case_provenance import classify_reference_operational_simulation
from eios.rules.negotiation_provenance import (
    build_reference_observed_c0_bound_ni_invoker,
    build_reference_observed_c0_bound_ladder_invoker,
)
from examples.reference_business_case_002_material import negotiation_material as _material


def test_second_company_ni_and_ladder_request_information_only():
    bundle, purchase, context, content, evidences, bindings = _material()
    provenance = classify_reference_operational_simulation(
        bundle=bundle, reference_case_id="REF-BUSINESS-002"
    ).to_payload()
    assert (provenance["material_nature"], provenance["qtg_mode_policy"],
            provenance["operational_path"], provenance["effect_scope"],
            provenance["decision_authority"]) == (
                "SYNTHETIC", "SYNTHETIC_TEST_ONLY", "FORBIDDEN",
                "NO_OPERATIONAL_EFFECT", False,
            )
    kwargs = dict(
        purchase=purchase, content_evidence=content, evidences=evidences,
        bindings=bindings, reference_case_id=provenance["reference_case_id"],
    )
    ni = build_reference_observed_c0_bound_ni_invoker(**kwargs)
    ladder = build_reference_observed_c0_bound_ladder_invoker(**kwargs)
    ni_execution = ni(purchase, context)
    ladder_execution = ladder(purchase, context)
    ni_result = ni.capture().result
    ladder_result = ladder.capture().result
    assert ni.capture().capability == ni_execution
    assert ladder.capture().capability == ladder_execution
    assert ni_result.negotiation_content == content.negotiation_content
    assert ni_result.traceability_references == content.trace_refs
    assert tuple(step.step_type for step in ladder_result.steps) == (
        "OBJECTIVE", "OPENING_REQUEST", "FALLBACK",
    )
    assert all("purchase" not in value.lower() for value in (
        content.negotiation_content.objective,
        content.negotiation_content.opening_request,
        content.negotiation_content.fallback,
    ))
    with pytest.raises(ValueError, match="single-use"):
        ni(purchase, context)


def test_second_company_ni_rejects_unbound_c0_trace():
    _, purchase, context, content, evidences, bindings = _material()
    bad = bindings[0].model_copy(update={
        "assessment": bindings[0].assessment.model_copy(update={"reason": "tampered"})
    })
    invoker = build_reference_observed_c0_bound_ni_invoker(
        purchase=purchase, content_evidence=content, evidences=evidences,
        bindings=(bad,), reference_case_id="REF-BUSINESS-002",
    )
    with pytest.raises(ValueError, match="assessment_fingerprint"):
        invoker(purchase, context)
    with pytest.raises(ValueError, match="unavailable"):
        invoker.capture()
