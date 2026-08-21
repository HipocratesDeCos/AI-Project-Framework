from datetime import date, timedelta

from eios.core.models import PurchaseOperation
from eios.core.validation import validate_purchase_operation


def make_purchase(**overrides):
    data = {
        "decision_id": "DEC-0001",
        "scenario_id": "SCN-0001",
        "article_id": "ART-001",
        "supplier_id": "PROV-001",
        "quantity": 100,
        "unit_price": 12.50,
        "currency": "EUR",
        "operation_date": date(2026, 8, 21),
    }
    data.update(overrides)
    return PurchaseOperation(**data)


def test_valid_purchase_passes():
    result = validate_purchase_operation(make_purchase(), as_of=date(2026, 8, 21))
    assert result.status == "PASS"


def test_future_operation_fails():
    result = validate_purchase_operation(
        make_purchase(operation_date=date(2026, 8, 22)),
        as_of=date(2026, 8, 21),
    )
    assert result.status == "FAIL"
    assert "futura" in result.reasons[0]


def test_non_positive_quantity_fails():
    result = validate_purchase_operation(
        make_purchase(quantity=0), as_of=date(2026, 8, 21)
    )
    assert result.status == "FAIL"


def test_negative_price_fails():
    result = validate_purchase_operation(
        make_purchase(unit_price=-1), as_of=date(2026, 8, 21)
    )
    assert result.status == "FAIL"
