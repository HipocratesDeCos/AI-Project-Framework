import eios.rules as rules
import eios.rules.scenario_integration as scenario_boundary


_QUARANTINED_STAGE2_SYMBOLS = (
    "ProvenancedScenarioAnalyticsInput",
    "build_authorized_scenario_analytics_from_provenanced_assessments",
    "complete_provenanced_o4_o2_o3_orchestration",
)


def test_assessment_scenario_public_stage2_boundary_is_quarantined() -> None:
    for symbol in _QUARANTINED_STAGE2_SYMBOLS:
        assert symbol not in rules.__all__
        assert not hasattr(rules, symbol)


def test_assessment_scenario_integration_module_exports_no_stage2_completion() -> None:
    assert scenario_boundary.__all__ == []
    for symbol in _QUARANTINED_STAGE2_SYMBOLS:
        assert not hasattr(scenario_boundary, symbol)


def test_c0_assessment_trace_provenance_remains_public() -> None:
    assert "AssessmentTraceBinding" in rules.__all__
    assert "validate_assessment_trace_binding" in rules.__all__
    assert rules.AssessmentTraceBinding is not None
    assert callable(rules.validate_assessment_trace_binding)
