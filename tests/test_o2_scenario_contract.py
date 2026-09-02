from datetime import date
from decimal import Decimal

import pytest

from eios.core.models import DecisionContext, PurchaseOperation
from eios.core.o2 import O2ScenarioResult, O2ScenarioStatus, build_support_package


def test_scenario_ids_are_independent_of_purchase_context_scenario():
    context = DecisionContext(
        decision_id="D1", scenario_id="BASE", rules_version="R1",
        parameters_version="P1", data_snapshot_id="S1",
    )
    purchase = PurchaseOperation(
        decision_id="D1", scenario_id="BASE", article_id="A1", supplier_id="S1",
        quantity=Decimal("1"), unit_price=Decimal("2"), currency="EUR",
        operation_date=date(2026, 9, 2),
    )
    results = [
        O2ScenarioResult(scenario_id="ALT-A", status=O2ScenarioStatus.COMPLETED),
        O2ScenarioResult(scenario_id="ALT-B", status=O2ScenarioStatus.COMPLETED),
    ]
    package = build_support_package(purchase, context, results)
    assert package.comparison is not None
    assert package.comparison.scenario_ids == ("ALT-A", "ALT-B")


def test_invalid_empty_scenario_rejected():
    with pytest.raises(ValueError):
        O2ScenarioResult(scenario_id="", status=O2ScenarioStatus.READY)


def test_failed_scenario_does_not_become_business_negative():
    failed = O2ScenarioResult(
        scenario_id="A", status=O2ScenarioStatus.FAILED, failure_reason="technical failure"
    )
    assert failed.status == O2ScenarioStatus.FAILED
    assert "outcome" not in failed.model_fields


def test_comparison_retains_incomplete_scenario_without_fabricating_value():
    complete = O2ScenarioResult(
        scenario_id="A", status=O2ScenarioStatus.COMPLETED, values={"tco": 100}
    )
    incomplete = O2ScenarioResult(
        scenario_id="B", status=O2ScenarioStatus.PARTIALLY_COMPLETED,
        unresolved_items=("tco unavailable",)
    )
    package = build_support_package(
        PurchaseOperation(
            decision_id="D1", scenario_id="BASE", article_id="A1", supplier_id="S1",
            quantity=Decimal("1"), unit_price=Decimal("2"), currency="EUR",
            operation_date=date(2026, 9, 2),
        ),
        DecisionContext(
            decision_id="D1", scenario_id="BASE", rules_version="R1",
            parameters_version="P1", data_snapshot_id="S1",
        ),
        [complete, incomplete],
    )
    assert package.comparison is not None
    assert package.comparison.missing["tco"] == ("B",)
    assert package.comparison.unresolved_items["B"] == ("tco unavailable",)
