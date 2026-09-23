import inspect

import eios.core._projection_synthetic_foundation as synthetic_foundation
import eios.core.mvp_execution as mvp_execution
import eios.core.projection_synthetic_adapter as synthetic_adapter
import eios.mvp as vertical_mvp
import eios.rules.decision_twin_integration as decision_twin_integration
import eios.rules.scenario_integration as scenario_integration


RAW_RESULT_ALIASES = {
    "price_result",
    "tco_result",
    "quality_result",
    "qtg_result",
    "decision_twin_result",
    "scenario_coordination_result",
    "negotiation_intelligence_result",
    "negotiation_ladder_result",
}

GENERIC_QTG_INPUTS = {
    "quality_invoker",
    "qtg_invoker",
    "projection_quality_receipt",
    "projection_quality_consumption",
    "projection_material_envelope",
}


def _parameters(callable_):
    return set(inspect.signature(callable_).parameters)


def test_o1_keeps_qtg_canonical_but_out_of_generic_invocation_boundary():
    parameters = _parameters(mvp_execution.run_mvp_execution)
    assert mvp_execution.MVP_CAPABILITY_ORDER[0] == "QTG"
    assert "QTG" in mvp_execution.MVP_CAPABILITY_ORDER
    assert parameters.isdisjoint(GENERIC_QTG_INPUTS)


def test_o1_does_not_reintroduce_detached_capability_results():
    parameters = _parameters(mvp_execution.run_mvp_execution)
    assert parameters.isdisjoint(RAW_RESULT_ALIASES)
    assert {
        "price_invoker", "tco_invoker", "rules_invoker",
        "decision_twin_invoker", "scenario_coordination_invoker",
        "negotiation_intelligence_invoker", "negotiation_ladder_invoker",
    } <= parameters


def test_vertical_facade_preserves_qtg_and_raw_result_quarantines():
    parameters = _parameters(vertical_mvp.run_vertical_mvp_support)
    assert parameters.isdisjoint(GENERIC_QTG_INPUTS)
    assert parameters.isdisjoint(RAW_RESULT_ALIASES)


def test_scenario_stage2_public_completion_is_reopened_only_through_safe_boundary():
    assert set(scenario_integration.__all__) == {
        "ProvenancedScenarioAnalyticsInput",
        "build_authorized_scenario_analytics_from_provenanced_assessments",
        "complete_provenanced_o4_o2_o3_orchestration",
    }
    assert "viability_result" not in scenario_integration.ProvenancedScenarioAnalyticsInput.model_fields


def test_decision_twin_wrapper_is_reopened_only_through_safe_stage2_boundary():
    assert set(decision_twin_integration.__all__) == {
        "DecisionTwinInvoker",
        "ProvenancedDecisionTwinAlternativeInput",
        "build_provenanced_decision_twin_comparison",
        "build_provenanced_decision_twin_invoker",
    }
    fields = set(decision_twin_integration.ProvenancedDecisionTwinAlternativeInput.model_fields)
    assert fields == {"representation_ref", "scenario_input"}


def test_synthetic_foundation_stages_remain_private():
    assert synthetic_foundation.__all__ == ()


def test_synthetic_s7_public_surface_remains_atomic():
    assert set(synthetic_adapter.__all__) == {
        "ProjectionOnlySyntheticMaterialBundle",
        "SCHEMA_VERSION",
        "SyntheticSemanticAdapterError",
        "build_projection_only_synthetic_material_bundle",
    }
