import eios.core.o4_o2_o3_orchestration as raw_stage2
import eios.rules as rules
import eios.rules.scenario_integration as stage2_boundary
from eios.core.viability_frontier import evaluate_viability


_QUARANTINED_PUBLIC_SYMBOLS = (
    "ProvenancedScenarioAnalyticsInput",
    "build_authorized_scenario_analytics_from_provenanced_assessments",
    "complete_provenanced_o4_o2_o3_orchestration",
)


def test_raw_stage2_completion_is_not_public_api() -> None:
    assert "complete_o4_o2_o3_orchestration" not in raw_stage2.__all__
    assert "AuthorizedScenarioAnalytics" not in raw_stage2.__all__
    assert "_complete_o4_o2_o3_orchestration" not in raw_stage2.__all__


def test_stage2_vf_provenance_completion_is_quarantined_from_rules_api() -> None:
    for symbol in _QUARANTINED_PUBLIC_SYMBOLS:
        assert symbol not in rules.__all__
        assert not hasattr(rules, symbol)


def test_scenario_integration_module_exports_no_provenance_safe_completion() -> None:
    assert stage2_boundary.__all__ == []
    for symbol in _QUARANTINED_PUBLIC_SYMBOLS:
        assert not hasattr(stage2_boundary, symbol)


def test_c0_provenance_boundary_remains_public_and_unchanged() -> None:
    assert "AssessmentTraceBinding" in rules.__all__
    assert "validate_assessment_trace_binding" in rules.__all__
    assert rules.AssessmentTraceBinding is not None
    assert callable(rules.validate_assessment_trace_binding)


def test_viability_frontier_evaluator_remains_available_in_its_closed_domain() -> None:
    assert callable(evaluate_viability)
