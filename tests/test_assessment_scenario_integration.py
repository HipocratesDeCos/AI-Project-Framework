import eios.rules as rules
import eios.rules.scenario_integration as scenario_boundary


_SAFE_STAGE2_SYMBOLS = (
    "ProvenancedScenarioAnalyticsInput",
    "build_authorized_scenario_analytics_from_provenanced_assessments",
    "complete_provenanced_o4_o2_o3_orchestration",
)


def test_assessment_scenario_public_stage2_boundary_is_provenance_safe() -> None:
    for symbol in _SAFE_STAGE2_SYMBOLS:
        assert symbol in rules.__all__
        assert hasattr(rules, symbol)


def test_assessment_scenario_integration_exports_safe_stage2_completion() -> None:
    assert tuple(scenario_boundary.__all__) == _SAFE_STAGE2_SYMBOLS
    for symbol in _SAFE_STAGE2_SYMBOLS:
        assert hasattr(scenario_boundary, symbol)


def test_c0_assessment_trace_provenance_remains_public() -> None:
    assert "AssessmentTraceBinding" in rules.__all__
    assert "validate_assessment_trace_binding" in rules.__all__
    assert rules.AssessmentTraceBinding is not None
    assert callable(rules.validate_assessment_trace_binding)
