from datetime import date
from decimal import Decimal

import pytest

from eios.core.models import DecisionContext, PurchaseOperation
from eios.core.o2 import (
    O2ScenarioResult,
    O2ScenarioStatus,
    build_execution_context,
    build_support_package,
    compare_scenarios,
)


def context() -> DecisionContext:
    return DecisionContext(
        decision_id="D-O2",
        scenario_id="BASE",
        rules_version="R1",
        parameters_version="P1",
        data_snapshot_id="S1",
    )


def purchase() -> PurchaseOperation:
    return PurchaseOperation(
        decision_id="D-O2",
        scenario_id="BASE",
        article_id="A1",
        supplier_id="SUP1",
        quantity=Decimal("10"),
        unit_price=Decimal("5"),
        currency="EUR",
        operation_date=date(2026, 9, 2),
    )


def test_execution_identity_is_order_independent():
    first = build_execution_context(context(), ["B", "A"])
    second = build_execution_context(context(), ["A", "B"])
    assert first.execution_id == second.execution_id


def test_duplicate_scenarios_rejected():
    a = O2ScenarioResult(scenario_id="A", status=O2ScenarioStatus.COMPLETED)
    with pytest.raises(ValueError, match="único"):
        build_support_package(purchase(), context(), [a, a])


def test_comparison_preserves_missing_and_status():
    a = O2ScenarioResult(
        scenario_id="A", status=O2ScenarioStatus.COMPLETED,
        values={"price": 10}, trace_references=("t-a",),
    )
    b = O2ScenarioResult(
        scenario_id="B", status=O2ScenarioStatus.NOT_EVALUABLE,
        values={}, unresolved_items=("price unavailable",), trace_references=("t-b",),
    )
    result = compare_scenarios([b, a])
    assert result.scenario_ids == ("A", "B")
    assert result.missing["price"] == ("B",)
    assert result.statuses["B"] == O2ScenarioStatus.NOT_EVALUABLE
    assert result.unresolved_items["B"] == ("price unavailable",)
    assert result.traceability["A"] == ("t-a",)


def test_support_package_is_scenario_order_stable():
    a = O2ScenarioResult(scenario_id="A", status=O2ScenarioStatus.COMPLETED, values={"x": 1})
    b = O2ScenarioResult(scenario_id="B", status=O2ScenarioStatus.COMPLETED, values={"x": 2})
    one = build_support_package(purchase(), context(), [b, a])
    two = build_support_package(purchase(), context(), [a, b])
    assert one == two


def test_failed_requires_reason():
    with pytest.raises(ValueError, match="failure_reason"):
        O2ScenarioResult(scenario_id="A", status=O2ScenarioStatus.FAILED)


def test_no_automatic_decision_field_exists():
    fields = set(O2SupportPackage.model_fields)
    forbidden = {"decision", "recommendation", "ranking", "score", "selection", "approval", "rejection"}
    assert fields.isdisjoint(forbidden)
