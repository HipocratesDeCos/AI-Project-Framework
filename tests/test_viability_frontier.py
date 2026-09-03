import pytest

from eios.core.viability_frontier import (
    FrontierAssessment,
    FrontierClass,
    FrontierInputError,
    ViabilityStatus,
    evaluate_viability,
)


def a(aid, cls, *, evaluated=True, satisfied=None, solvable=None, rule="R", trace="T"):
    return FrontierAssessment(aid, "D1", "S1", cls, evaluated, satisfied, solvable, rule, trace)


def test_viable_and_order_independent():
    x = [a("2", FrontierClass.S), a("1", FrontierClass.S)]
    r1 = evaluate_viability("D1", "S1", x)
    r2 = evaluate_viability("D1", "S1", reversed(x))
    assert r1 == r2
    assert r1.status is ViabilityStatus.VIABLE


def test_hard_constraint_is_not_compensated():
    r = evaluate_viability("D1", "S1", [a("h", FrontierClass.H, satisfied=False), a("s", FrontierClass.S)])
    assert r.status is ViabilityStatus.NOT_VIABLE


def test_material_insufficiency_is_not_negative():
    r = evaluate_viability("D1", "S1", [a("u", FrontierClass.U)])
    assert r.status is ViabilityStatus.NOT_EVALUABLE


def test_condition_is_conditional():
    r = evaluate_viability("D1", "S1", [a("k", FrontierClass.K, satisfied=False, solvable=True)])
    assert r.status is ViabilityStatus.VIABLE_CON_CONDICIONES


def test_unresolved_k_does_not_create_condition():
    r = evaluate_viability("D1", "S1", [a("k", FrontierClass.K, evaluated=False, satisfied=None, solvable=None)])
    assert r.status is ViabilityStatus.VIABLE


def test_severity_or_rule_code_cannot_create_frontier_without_authorized_class():
    r = evaluate_viability("D1", "S1", [a("r3", FrontierClass.S, rule="R3")])
    assert r.status is ViabilityStatus.VIABLE


def test_context_mismatch_rejected():
    item = FrontierAssessment("a", "OTHER", "S1", FrontierClass.H, True, False, None, "R", "T")
    with pytest.raises(FrontierInputError):
        evaluate_viability("D1", "S1", [item])


def test_duplicate_assessment_rejected():
    item = a("a", FrontierClass.S)
    with pytest.raises(FrontierInputError):
        evaluate_viability("D1", "S1", [item, item])


def test_inputs_are_not_mutated():
    items = [a("b", FrontierClass.S), a("a", FrontierClass.S)]
    before = tuple(items)
    evaluate_viability("D1", "S1", items)
    assert tuple(items) == before


def test_invalid_h_input_rejected():
    with pytest.raises(FrontierInputError):
        evaluate_viability("D1", "S1", [a("h", FrontierClass.H, satisfied=None)])
