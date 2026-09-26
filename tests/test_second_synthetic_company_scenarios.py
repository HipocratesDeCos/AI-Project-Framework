"""Two company 002 children each carry their own C0 purchase and trace."""

import pytest
from decimal import Decimal
from eios.core.case_provenance import classify_reference_operational_simulation
from eios.rules.decision_twin_integration import (
    ProvenancedDecisionTwinAlternativeInput,
    build_reference_observed_decision_twin_invoker,
)
from eios.rules.scenario_integration import build_reference_observed_scenario_coordination_invoker
from examples.reference_business_case_002_material import scenario_material as _material


def test_second_company_child_trace_payloads_are_reproducible():
    first = _material()[4]
    second = _material()[4]
    assert tuple(item.model_dump(mode="json") for item in first) == tuple(
        item.model_dump(mode="json") for item in second
    )


def test_second_company_scenario_coordination_uses_distinct_child_c0():
    bundle, purchase, context, preparation, inputs = _material()
    provenance = classify_reference_operational_simulation(
        bundle=bundle, reference_case_id="REF-BUSINESS-002"
    ).to_payload()
    assert (provenance["material_nature"], provenance["qtg_mode_policy"],
            provenance["operational_path"], provenance["effect_scope"],
            provenance["decision_authority"]) == (
                "SYNTHETIC", "SYNTHETIC_TEST_ONLY", "FORBIDDEN",
                "NO_OPERATIONAL_EFFECT", False,
            )
    assert tuple(item.purchase.quantity for item in inputs) == (
        Decimal("16"), Decimal("17"),
    )
    child_traces = tuple(item.assessment_bindings[0].trace.trace_id for item in inputs)
    assert len(set(child_traces)) == 2
    assert all(item.purchase.scenario_id != purchase.scenario_id for item in inputs)
    invoker = build_reference_observed_scenario_coordination_invoker(
        purchase=purchase, preparation=preparation, inputs=inputs,
        reference_case_id="REF-BUSINESS-002",
    )
    capability = invoker(purchase, context)
    capture = invoker.capture()
    assert capture.capability == capability
    assert capability.capability == "SCENARIO_COORDINATION"
    assert len(capture.result.scenarios) == 2
    with pytest.raises(ValueError, match="single-use"):
        invoker(purchase, context)


def test_second_company_twin_compares_children_without_selection():
    _, purchase, context, preparation, inputs = _material()
    alternatives = tuple(ProvenancedDecisionTwinAlternativeInput(
        representation_ref=f"REF-BUSINESS-002-ALT-{index}", scenario_input=item,
    ) for index, item in enumerate(inputs, start=1))
    invoker = build_reference_observed_decision_twin_invoker(
        purchase=purchase, preparation=preparation, alternatives=alternatives,
        reference_case_id="REF-BUSINESS-002",
    )
    capability = invoker(purchase, context)
    capture = invoker.capture()
    assert capture.capability == capability
    assert capability.capability == "DECISION_TWIN"
    assert capture.result.alternatives == (
        "REF-BUSINESS-002-ALT-1", "REF-BUSINESS-002-ALT-2",
    )
    assert "selected_alternative" not in type(capture.result).model_fields


def test_second_company_scenarios_reject_reused_sibling_trace():
    _, purchase, context, preparation, inputs = _material()
    broken = inputs[1].model_copy(update={
        "assessment_bindings": (inputs[1].assessment_bindings[0].model_copy(
            update={"trace": inputs[0].assessment_bindings[0].trace}
        ),),
    })
    invoker = build_reference_observed_scenario_coordination_invoker(
        purchase=purchase, preparation=preparation, inputs=(inputs[0], broken),
        reference_case_id="REF-BUSINESS-002",
    )
    with pytest.raises(ValueError, match="Trace.scenario_id"):
        invoker(purchase, context)
    with pytest.raises(ValueError, match="unavailable"):
        invoker.capture()
