from eios.core.models import DecisionContext
from eios.core.o4_o2_o3_orchestration import prepare_o4_o2_o3_orchestration
from eios.core.scenario_generation import GenerationPolicy, GenerationVariable
import eios.rules as rules


def _context() -> DecisionContext:
    return DecisionContext(
        decision_id="D-E2E-SCENARIO",
        scenario_id="BASE",
        rules_version="RULES-E2E-1",
        parameters_version="PARAMS-E2E-1",
        data_snapshot_id="SNAP-E2E-1",
    )


def _preparation():
    return prepare_o4_o2_o3_orchestration(
        context=_context(),
        variables=(
            GenerationVariable(
                variable_id="quantity_delta",
                value_type="integer",
                base_value=0,
                domain=(1, 2),
            ),
        ),
        policy=GenerationPolicy(policy_version="O4-E2E-1"),
    )


def test_scenario_e2e_reaches_stage1_but_stops_before_unproven_vf_stage2() -> None:
    preparation = _preparation()

    assert preparation.materialization.scenarios
    assert all(
        scenario.decision_id == preparation.context.decision_id
        for scenario in preparation.materialization.scenarios
    )
    assert not hasattr(rules, "complete_provenanced_o4_o2_o3_orchestration")


def test_e2e_does_not_expose_caller_constructed_vf_as_provenance_safe_input() -> None:
    assert not hasattr(rules, "ProvenancedScenarioAnalyticsInput")
    assert not hasattr(
        rules,
        "build_authorized_scenario_analytics_from_provenanced_assessments",
    )


def test_quarantine_does_not_remove_c0_provenance_or_stage1_scenario_generation() -> None:
    preparation = _preparation()

    assert "AssessmentTraceBinding" in rules.__all__
    assert "validate_assessment_trace_binding" in rules.__all__
    assert callable(rules.validate_assessment_trace_binding)
    assert len(preparation.materialization.scenarios) == 2
