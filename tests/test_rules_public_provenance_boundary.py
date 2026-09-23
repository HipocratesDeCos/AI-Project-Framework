import eios.rules as rules


def test_public_rules_namespace_exposes_only_provenance_safe_reuse_entrypoints() -> None:
    safe_names = {
        "AssessmentTraceBinding",
        "RulesEngineInput",
        "run_rules_engine",
        "validate_assessment_trace_binding",
        "run_provenanced_assessments_vertical",
        "build_rules_engine_c0_invoker",
        "build_provenanced_rules_engine_c0_invoker",
        "VF_MINIMAL_CATALOG",
        "produce_frontier_assessments",
        "evaluate_provenanced_viability",
        "ProvenancedScenarioAnalyticsInput",
        "build_authorized_scenario_analytics_from_provenanced_assessments",
        "complete_provenanced_o4_o2_o3_orchestration",
    }
    for name in safe_names:
        assert hasattr(rules, name), name
        assert name in rules.__all__

    quarantined_internal_names = {
        "RuleAssessmentBinding",
        "bind_authorized_assessment",
        "run_assessment_set_vertical",
        "run_assessment_vertical",
        "run_authorized_assessments_vertical",
    }
    for name in quarantined_internal_names:
        assert not hasattr(rules, name), name

    still_quarantined_dependent_names = {
        "DecisionTwinInvoker",
        "ProvenancedDecisionTwinAlternativeInput",
        "build_provenanced_decision_twin_comparison",
        "build_provenanced_decision_twin_invoker",
    }
    for name in still_quarantined_dependent_names:
        assert not hasattr(rules, name), name
        assert name not in rules.__all__


def test_public_rules_engine_input_schema_contains_bindings_not_assessments() -> None:
    fields = set(rules.RulesEngineInput.model_fields)
    assert fields == {"purchase", "context", "bindings", "base_result"}
    assert "assessments" not in fields
