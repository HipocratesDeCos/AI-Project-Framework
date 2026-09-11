from datetime import date
from decimal import Decimal

import pytest

from eios.core.models import DecisionContext, PurchaseOperation
from eios.core.o2 import O2ScenarioStatus
from eios.core.o2_o3_integration import adapt_o3_result_for_o2, build_o2_support_from_o3
from eios.core.scenario_evaluation import ScenarioEvaluationResult, ScenarioEvaluationStatus


def _context(**changes) -> DecisionContext:
    data = dict(
        decision_id="D-O2-O3",
        scenario_id="BASE",
        rules_version="R1",
        parameters_version="P1",
        data_snapshot_id="S1",
    )
    data.update(changes)
    return DecisionContext(**data)


def _purchase(**changes) -> PurchaseOperation:
    data = dict(
        decision_id="D-O2-O3",
        scenario_id="BASE",
        article_id="A1",
        supplier_id="SUP1",
        quantity=Decimal("10"),
        unit_price=Decimal("5"),
        currency="EUR",
        operation_date=date(2026, 9, 11),
    )
    data.update(changes)
    return PurchaseOperation(**data)


def _completed(scenario_id: str) -> ScenarioEvaluationResult:
    return ScenarioEvaluationResult(
        scenario_id=scenario_id,
        decision_id="D-O2-O3",
        rules_version="R1",
        parameters_version="P1",
        data_snapshot_id="S1",
        status=ScenarioEvaluationStatus.COMPLETED,
        assessments=(f"assessment-{scenario_id}",),
        viability_result={"state": f"viable-{scenario_id}"},
        trace_references=(f"trace-{scenario_id}",),
    )


def _not_evaluable(scenario_id: str) -> ScenarioEvaluationResult:
    return ScenarioEvaluationResult(
        scenario_id=scenario_id,
        decision_id="D-O2-O3",
        rules_version="R1",
        parameters_version="P1",
        data_snapshot_id="S1",
        status=ScenarioEvaluationStatus.NOT_EVALUABLE,
        limitations=("missing-evidence",),
        trace_references=(f"trace-{scenario_id}",),
    )


def test_adapter_copies_o3_result_without_recalculation():
    result = _completed("ALT-A")

    adapted = adapt_o3_result_for_o2(result, _context())

    assert adapted.scenario_id == "ALT-A"
    assert adapted.status == O2ScenarioStatus.COMPLETED
    assert adapted.values["assessments"] == result.assessments
    assert adapted.values["viability_result"] == result.viability_result
    assert adapted.trace_references == result.trace_references
    assert adapted.unresolved_items == ()
    assert adapted.failure_reason is None


def test_adapter_preserves_absence_and_unresolved_items():
    adapted = adapt_o3_result_for_o2(_not_evaluable("ALT-B"), _context())

    assert adapted.status == O2ScenarioStatus.NOT_EVALUABLE
    assert "assessments" not in adapted.values
    assert "viability_result" not in adapted.values
    assert adapted.unresolved_items == ("missing-evidence",)


def test_not_started_fails_closed_instead_of_becoming_ready():
    result = ScenarioEvaluationResult(
        scenario_id="ALT-A",
        decision_id="D-O2-O3",
        rules_version="R1",
        parameters_version="P1",
        data_snapshot_id="S1",
        status=ScenarioEvaluationStatus.NOT_STARTED,
    )

    with pytest.raises(ValueError, match="no tiene equivalencia O2 literal"):
        adapt_o3_result_for_o2(result, _context())


def test_context_versions_and_snapshot_must_match_o3_result():
    result = _completed("ALT-A")

    with pytest.raises(ValueError, match="rules_version"):
        adapt_o3_result_for_o2(result, _context(rules_version="R2"))
    with pytest.raises(ValueError, match="parameters_version"):
        adapt_o3_result_for_o2(result, _context(parameters_version="P2"))
    with pytest.raises(ValueError, match="data_snapshot_id"):
        adapt_o3_result_for_o2(result, _context(data_snapshot_id="S2"))


def test_integration_requires_purchase_and_context_identity_coherence():
    result = _completed("ALT-A")

    with pytest.raises(ValueError, match="decision_id"):
        build_o2_support_from_o3(_purchase(decision_id="OTHER"), _context(), [result])
    with pytest.raises(ValueError, match="scenario_id"):
        build_o2_support_from_o3(_purchase(scenario_id="OTHER"), _context(), [result])


def test_o3_order_does_not_change_o2_support_package():
    a = _completed("ALT-A")
    b = _not_evaluable("ALT-B")

    first = build_o2_support_from_o3(_purchase(), _context(), [b, a])
    second = build_o2_support_from_o3(_purchase(), _context(), [a, b])

    assert first == second
    assert first.comparison is not None
    assert first.comparison.scenario_ids == ("ALT-A", "ALT-B")
    assert first.comparison.missing["assessments"] == ("ALT-B",)
    assert first.comparison.missing["viability_result"] == ("ALT-B",)
    assert first.comparison.unresolved_items["ALT-B"] == ("missing-evidence",)
    assert first.comparison.traceability["ALT-A"] == ("trace-ALT-A",)


def test_integration_does_not_mutate_inputs():
    purchase = _purchase()
    context = _context()
    results = [_completed("ALT-A"), _not_evaluable("ALT-B")]
    purchase_before = purchase.model_copy(deep=True)
    context_before = context.model_copy(deep=True)
    results_before = [result.model_copy(deep=True) for result in results]

    build_o2_support_from_o3(purchase, context, results)

    assert purchase == purchase_before
    assert context == context_before
    assert results == results_before


def test_duplicate_scenarios_remain_rejected_by_o2():
    duplicate = _completed("ALT-A")

    with pytest.raises(ValueError, match="único"):
        build_o2_support_from_o3(_purchase(), _context(), [duplicate, duplicate])
