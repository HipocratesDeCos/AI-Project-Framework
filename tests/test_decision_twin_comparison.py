from copy import deepcopy

import pytest

from eios.core.decision_twin_comparison import AlternativeRepresentation, compare


def alt(ref, values, **kwargs):
    return AlternativeRepresentation(ref, values, **kwargs)


def test_ab_returns_descriptive_difference_without_preference():
    result = compare([alt("A", {"cost": 100}), alt("B", {"cost": 110})])
    assert result.differences["cost"] == (100, 110)
    assert not hasattr(result, "winner")
    assert not hasattr(result, "score")


def test_three_alternatives_do_not_create_ranking():
    result = compare([
        alt("A", {"cost": 100}),
        alt("B", {"cost": 110}),
        alt("C", {"cost": 105}),
    ])
    assert result.alternatives == ("A", "B", "C")
    assert not hasattr(result, "ranking")


def test_reverse_order_preserves_observations_and_difference_set():
    forward = compare([alt("A", {"cost": 100}), alt("B", {"cost": 110})])
    reverse = compare([alt("B", {"cost": 110}), alt("A", {"cost": 100})])
    assert forward.observations == reverse.observations
    assert set(map(repr, forward.differences["cost"])) == set(map(repr, reverse.differences["cost"]))


def test_missing_value_is_not_penalized():
    result = compare([alt("A", {"cost": 100}), alt("B", {})])
    assert result.missing["cost"] == ("B",)


def test_conflicting_dimensions_are_only_observed():
    result = compare([
        alt("A", {"cost": 100, "lead_time": 30}),
        alt("B", {"cost": 110, "lead_time": 20}),
    ])
    assert set(result.differences) == {"cost", "lead_time"}
    assert not hasattr(result, "winner")


def test_viability_is_preserved_without_selection():
    result = compare([
        alt("A", {"cost": 100}, viability="VIABLE"),
        alt("B", {"cost": 110}, viability="NOT_VIABLE"),
    ])
    assert result.viability == {"A": "VIABLE", "B": "NOT_VIABLE"}
    assert result.viability_differences == ("VIABLE", "NOT_VIABLE")
    assert not hasattr(result, "preferred_alternative")


def test_consequences_are_descriptive_without_priority():
    result = compare([
        alt("A", {}, consequences={"risk": "low"}),
        alt("B", {}, consequences={"risk": "high"}),
    ])
    assert result.consequence_observations["risk"] == {"A": "low", "B": "high"}
    assert result.consequence_differences["risk"] == ("low", "high")
    assert not hasattr(result, "winner")


def test_scenario_and_trace_references_are_preserved():
    result = compare([
        alt("A", {}, scenario_ref="S1", trace_refs=("T1",)),
        alt("B", {}, scenario_ref="S2", trace_refs=("T2",)),
    ])
    assert result.scenario_refs == {"A": "S1", "B": "S2"}
    assert result.traceability == {"A": ("T1",), "B": ("T2",)}
    assert not hasattr(result, "selected_scenario")


def test_redundant_trace_references_do_not_create_weight():
    result = compare([
        alt("A", {"cost": 100}, trace_refs=("T1", "T2", "T2")),
        alt("B", {"cost": 110}, trace_refs=("T3",)),
    ])
    assert result.traceability["A"] == ("T1", "T2", "T2")
    assert not hasattr(result, "weight")


def test_sources_are_not_mutated():
    values_a = {"cost": 100}
    values_b = {"cost": 110}
    before_a, before_b = deepcopy(values_a), deepcopy(values_b)
    compare([alt("A", values_a), alt("B", values_b)])
    assert values_a == before_a
    assert values_b == before_b


def test_requires_two_or_more_alternatives():
    with pytest.raises(ValueError):
        compare([alt("A", {"cost": 100})])


def test_duplicate_representation_refs_are_rejected():
    with pytest.raises(ValueError):
        compare([alt("A", {"cost": 100}), alt("A", {"cost": 110})])
