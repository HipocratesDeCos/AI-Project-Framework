import pytest

from eios.core.viability_frontier import (
    FrontierAssessment,
    FrontierClass,
    FrontierInputError,
    ViabilityStatus,
    evaluate_viability,
)


def a(
    aid,
    cls,
    *,
    evaluated=True,
    satisfied=None,
    solvable=None,
    rule="R",
    trace="T",
    materially_insufficient=False,
    authority_conflict=False,
):
    return FrontierAssessment(
        aid,
        "D1",
        "S1",
        cls,
        evaluated,
        satisfied,
        solvable,
        rule,
        trace,
        materially_insufficient,
        authority_conflict,
    )


def test_viable_and_order_independent():
    x = [a("2", FrontierClass.S), a("1", FrontierClass.S)]
    r1 = evaluate_viability("D1", "S1", x)
    r2 = evaluate_viability("D1", "S1", reversed(x))
    assert r1 == r2
    assert r1.status is ViabilityStatus.VIABLE


def test_hard_constraint_is_not_compensated():
    r = evaluate_viability("D1", "S1", [a("h", FrontierClass.H, satisfied=False), a("s", FrontierClass.S)])
    assert r.status is ViabilityStatus.NOT_VIABLE


def test_material_insufficiency_requires_explicit_material_signal():
    with pytest.raises(FrontierInputError):
        evaluate_viability("D1", "S1", [a("u", FrontierClass.U)])

    r = evaluate_viability(
        "D1", "S1", [a("u", FrontierClass.U, materially_insufficient=True)]
    )
    assert r.status is ViabilityStatus.NOT_EVALUABLE
    assert r.limitation == "MATERIAL_INSUFFICIENCY"


def test_condition_is_conditional():
    r = evaluate_viability("D1", "S1", [a("k", FrontierClass.K, satisfied=False, solvable=True)])
    assert r.status is ViabilityStatus.VIABLE_CON_CONDICIONES


def test_unresolved_k_can_preserve_material_insufficiency():
    r = evaluate_viability(
        "D1",
        "S1",
        [a("k", FrontierClass.K, evaluated=False, materially_insufficient=True)],
    )
    assert r.status is ViabilityStatus.NOT_EVALUABLE
    assert r.limitation == "MATERIAL_UNEVALUATED_FRONTIER_CONSEQUENCE"


def test_unresolved_k_without_material_signal_does_not_create_condition():
    r = evaluate_viability(
        "D1",
        "S1",
        [a("k", FrontierClass.K, evaluated=False)],
    )
    assert r.status is ViabilityStatus.VIABLE


def test_unresolved_h_does_not_create_not_viable():
    r = evaluate_viability(
        "D1",
        "S1",
        [a("h", FrontierClass.H, evaluated=False)],
    )
    assert r.status is ViabilityStatus.VIABLE


def test_unresolved_h_with_material_signal_is_not_evaluable():
    r = evaluate_viability(
        "D1",
        "S1",
        [a("h", FrontierClass.H, evaluated=False, materially_insufficient=True)],
    )
    assert r.status is ViabilityStatus.NOT_EVALUABLE


def test_unresolved_authority_conflict_is_structured():
    r = evaluate_viability(
        "D1", "S1", [a("c", FrontierClass.S, authority_conflict=True)]
    )
    assert r.status is ViabilityStatus.NOT_EVALUABLE
    assert r.limitation == "UNRESOLVED_AUTHORITY_CONFLICT"


def test_versions_and_snapshot_are_preserved():
    r = evaluate_viability(
        "D1",
        "S1",
        [a("s", FrontierClass.S)],
        rules_version="R-2",
        parameters_version="P-3",
        data_snapshot_id="DS-4",
    )
    assert r.rules_version == "R-2"
    assert r.parameters_version == "P-3"
    assert r.data_snapshot_id == "DS-4"


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


def test_invalid_k_input_rejected_when_evaluated():
    with pytest.raises(FrontierInputError):
        evaluate_viability("D1", "S1", [a("k", FrontierClass.K, satisfied=None, solvable=True)])
