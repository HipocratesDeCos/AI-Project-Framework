import eios.rules as rules
import eios.rules.decision_twin_integration as decision_twin_boundary
from eios.core.decision_twin_engine import compare_alternatives


_SAFE_PUBLIC_SYMBOLS = (
    "DecisionTwinInvoker",
    "ProvenancedDecisionTwinAlternativeInput",
    "build_provenanced_decision_twin_comparison",
    "build_provenanced_decision_twin_invoker",
)


def test_decision_twin_stage2_provenance_wrapper_is_public_and_safe() -> None:
    for symbol in _SAFE_PUBLIC_SYMBOLS:
        assert symbol in rules.__all__
        assert hasattr(rules, symbol)


def test_decision_twin_integration_exports_safe_wrapper_only() -> None:
    assert tuple(decision_twin_boundary.__all__) == _SAFE_PUBLIC_SYMBOLS
    for symbol in _SAFE_PUBLIC_SYMBOLS:
        assert hasattr(decision_twin_boundary, symbol)


def test_decision_twin_alternative_input_has_no_detached_results() -> None:
    fields = set(decision_twin_boundary.ProvenancedDecisionTwinAlternativeInput.model_fields)
    assert fields == {"representation_ref", "scenario_input"}
    assert "decision_twin_result" not in fields
    assert "viability_result" not in fields
    assert "scenario_evaluation_result" not in fields


def test_decision_twin_core_comparator_remains_available() -> None:
    assert callable(compare_alternatives)
