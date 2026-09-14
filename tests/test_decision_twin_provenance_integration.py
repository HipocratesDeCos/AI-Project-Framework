import eios.rules as rules
import eios.rules.decision_twin_integration as decision_twin_boundary
from eios.core.decision_twin_engine import compare_alternatives


_QUARANTINED_PUBLIC_SYMBOLS = (
    "DecisionTwinInvoker",
    "ProvenancedDecisionTwinAlternativeInput",
    "build_provenanced_decision_twin_comparison",
    "build_provenanced_decision_twin_invoker",
)


def test_decision_twin_stage2_provenance_wrapper_is_quarantined_from_rules_api() -> None:
    for symbol in _QUARANTINED_PUBLIC_SYMBOLS:
        assert symbol not in rules.__all__
        assert not hasattr(rules, symbol)


def test_decision_twin_integration_module_exports_no_provenance_safe_wrapper() -> None:
    assert decision_twin_boundary.__all__ == []
    for symbol in _QUARANTINED_PUBLIC_SYMBOLS:
        assert not hasattr(decision_twin_boundary, symbol)


def test_decision_twin_core_comparator_remains_available() -> None:
    assert callable(compare_alternatives)
