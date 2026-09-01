from decimal import Decimal

from pydantic import ValidationError

from eios.core.models import PurchaseOperation
from eios.tco import CostComponent, TCOInput, calculate_tco


def operation(**overrides):
    data = {
        "decision_id": "D-1",
        "scenario_id": "S-1",
        "article_id": "A-1",
        "supplier_id": "SUP-1",
        "quantity": Decimal("10"),
        "unit_price": Decimal("100.00"),
        "currency": "EUR",
        "operation_date": "2026-09-01",
    }
    data.update(overrides)
    return PurchaseOperation(**data)


def cost(component="TRANSPORT", amount="50.00", currency="EUR", attribution_ref="P-1", rule_reference="R-TCO-TRANSPORT"):
    return CostComponent(
        component=component,
        amount=Decimal(amount) if amount is not None else None,
        currency=currency,
        attribution_ref=attribution_ref,
        rule_reference=rule_reference,
    )


def test_tco_determinable_with_valid_attributable_costs():
    result = calculate_tco(TCOInput(purchase_operation=operation(), attributable_costs=(cost(),)))
    assert result.value == Decimal("1050.00")
    assert result.complete is True
    assert result.contributing_components == ("ACQUISITION", "TRANSPORT")


def test_missing_applicable_cost_is_preserved_as_unresolved():
    item = cost(amount=None)
    result = calculate_tco(TCOInput(purchase_operation=operation(), attributable_costs=(item,)))
    assert result.value is None
    assert result.complete is False
    assert result.unresolved_components == ("TRANSPORT",)
    assert "MISSING_AMOUNT:TRANSPORT" in result.limitations


def test_not_applicable_cost_does_not_contribute():
    item = CostComponent(
        component="INSURANCE",
        currency="EUR",
        applicability="NOT_APPLICABLE",
    )
    result = calculate_tco(TCOInput(purchase_operation=operation(), attributable_costs=(item,)))
    assert result.value == Decimal("1000.00")
    assert result.complete is True
    assert result.contributing_components == ("ACQUISITION",)


def test_incompatible_currency_does_not_aggregate_silently():
    result = calculate_tco(
        TCOInput(purchase_operation=operation(), attributable_costs=(cost(currency="USD"),))
    )
    assert result.value is None
    assert result.complete is False
    assert result.unresolved_components == ("TRANSPORT",)
    assert "CURRENCY_INCOMPATIBLE:TRANSPORT" in result.limitations


def test_non_attributable_cost_is_rejected():
    try:
        CostComponent(component="HANDLING", amount=Decimal("20"), currency="EUR", rule_reference="R-1")
    except ValidationError:
        return
    raise AssertionError("Un componente aplicable sin attribution_ref debe rechazarse")


def test_purchase_operation_is_not_modified():
    purchase = operation()
    before = purchase.model_dump()
    calculate_tco(TCOInput(purchase_operation=purchase, attributable_costs=(cost(),)))
    assert purchase.model_dump() == before


def test_financial_terms_are_not_automatically_added_as_tco_cost():
    result = calculate_tco(TCOInput(purchase_operation=operation(), attributable_costs=()))
    assert result.value == Decimal("1000.00")
    assert "FINANCING" not in result.contributing_components
