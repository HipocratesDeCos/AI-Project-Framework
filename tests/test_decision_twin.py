from eios.core.decision_twin import (
    AlternativeRepresentation,
    DecisionTwinComparisonInput,
)
from eios.core.decision_twin_engine import compare_alternatives


def test_compare_two_alternatives_is_descriptive_only():
    result = compare_alternatives(
        DecisionTwinComparisonInput(
            alternatives=(
                AlternativeRepresentation(
                    representation_ref="B",
                    viability="NOT_VIABLE",
                    results={"price": 110},
                    consequences={"lead_time": 4},
                    trace_refs=("trace-b",),
                ),
                AlternativeRepresentation(
                    representation_ref="A",
                    viability="VIABLE",
                    results={"price": 100},
                    consequences={"lead_time": 7},
                    trace_refs=("trace-a",),
                ),
            )
        )
    )

    assert result.alternatives == ("A", "B")
    assert "viability" in result.differences
    assert "results" in result.differences
    assert "consequences" in result.differences
    assert not hasattr(result, "score")
    assert not hasattr(result, "ranking")
    assert not hasattr(result, "winner")
    assert not hasattr(result, "preferred_alternative")


def test_missing_value_is_asymmetry_not_penalty():
    result = compare_alternatives(
        DecisionTwinComparisonInput(
            alternatives=(
                AlternativeRepresentation(
                    representation_ref="A",
                    results={"price": 100},
                ),
                AlternativeRepresentation(
                    representation_ref="B",
                    results={},
                ),
            )
        )
    )

    assert "B:results" in result.missing_attributes
    assert any(
        observation.attribute == "results" and not observation.comparable
        for observation in result.observations
    )
    assert "results" not in result.differences


def test_reordering_inputs_preserves_semantic_content():
    a = AlternativeRepresentation(
        representation_ref="A", results={"price": 100}, trace_refs=("ta",)
    )
    b = AlternativeRepresentation(
        representation_ref="B", results={"price": 120}, trace_refs=("tb",)
    )

    first = compare_alternatives(DecisionTwinComparisonInput(alternatives=(a, b)))
    second = compare_alternatives(DecisionTwinComparisonInput(alternatives=(b, a)))

    assert first == second


def test_conflicting_dimensions_do_not_create_preference():
    result = compare_alternatives(
        DecisionTwinComparisonInput(
            alternatives=(
                AlternativeRepresentation(
                    representation_ref="A", results={"cost": 10, "lead_time": 8}
                ),
                AlternativeRepresentation(
                    representation_ref="B", results={"cost": 12, "lead_time": 5}
                ),
            )
        )
    )

    assert "results" in result.differences
    assert not hasattr(result, "winner")
    assert not hasattr(result, "preferred_alternative")


def test_at_least_two_and_unique_representation_refs_are_required():
    try:
        DecisionTwinComparisonInput(
            alternatives=(AlternativeRepresentation(representation_ref="A"),)
        )
    except ValueError:
        pass
    else:
        raise AssertionError("Se requiere al menos dos alternativas")

    try:
        DecisionTwinComparisonInput(
            alternatives=(
                AlternativeRepresentation(representation_ref="A"),
                AlternativeRepresentation(representation_ref="A"),
            )
        )
    except ValueError:
        pass
    else:
        raise AssertionError("Las referencias deben ser únicas")
