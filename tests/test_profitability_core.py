from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest
from pydantic import ValidationError

from eios.core.models import DecisionContext, PurchaseOperation
from eios.profitability import (
    AuthorizedCostBasis,
    AuthorizedSaleBasis,
    ProfitabilityInput,
    calculate_profitability,
)


EVAL_DATE = date(2026, 9, 20)


def _context():
    return DecisionContext(
        decision_id="DEC-MGE-001",
        scenario_id="SCN-MGE-001",
        rules_version="rules-v1",
        parameters_version="params-v1",
        data_snapshot_id="snap-v1",
    )


def _purchase():
    return PurchaseOperation(
        decision_id="DEC-MGE-001",
        scenario_id="SCN-MGE-001",
        article_id="ART-001",
        supplier_id="SUP-001",
        quantity=Decimal("10"),
        unit_price=Decimal("5.0000"),
        currency="EUR",
        operation_date=EVAL_DATE,
    )


def _basis_kwargs():
    return dict(
        state="KNOWN",
        decision_id="DEC-MGE-001",
        scenario_id="SCN-MGE-001",
        data_snapshot_id="snap-v1",
        company_scope="COMPANY-A",
        article_id="ART-001",
        evaluation_date=EVAL_DATE,
        currency="EUR",
        economic_basis_ref="BASIS:UNIT",
        authority_ref="MGE-AUTH-v0.1",
        source_ref="SRC-001",
        trace_refs=("TRACE-001",),
    )


def _sale(value="100.0000", **overrides):
    data = _basis_kwargs()
    data["value"] = Decimal(value) if value is not None else None
    data.update(overrides)
    return AuthorizedSaleBasis(**data)


def _cost(value="70.0000", **overrides):
    data = _basis_kwargs()
    data["value"] = Decimal(value) if value is not None else None
    data["source_ref"] = "SRC-002"
    data["trace_refs"] = ("TRACE-002",)
    data.update(overrides)
    return AuthorizedCostBasis(**data)


def _payload(*, sale=None, cost=None, context=None, purchase=None, **overrides):
    data = dict(
        context=context or _context(),
        purchase_operation=purchase or _purchase(),
        company_scope="COMPANY-A",
        evaluation_date=EVAL_DATE,
        sale_basis=sale or _sale(),
        cost_basis=cost or _cost(),
        methodology_version="MGE-AUTH-v0.1",
    )
    data.update(overrides)
    return ProfitabilityInput(**data)


def test_happy_path_calculates_amount_and_margin_percentage():
    result = calculate_profitability(_payload())

    assert result.calculation_state == "DETERMINED"
    assert result.margin_amount == Decimal("30.0000")
    assert result.margin_percentage == Decimal("30.0")
    assert result.currency == "EUR"
    assert result.economic_basis_ref == "BASIS:UNIT"
    assert result.trace_refs == ("TRACE-001", "TRACE-002")


def test_negative_margin_is_not_clamped():
    result = calculate_profitability(
        _payload(sale=_sale("80"), cost=_cost("100"))
    )

    assert result.calculation_state == "DETERMINED"
    assert result.margin_amount == Decimal("-20")
    assert result.margin_percentage == Decimal("-25.00")


def test_zero_margin_is_determined():
    result = calculate_profitability(
        _payload(sale=_sale("100"), cost=_cost("100"))
    )

    assert result.margin_amount == Decimal("0")
    assert result.margin_percentage == Decimal("0")


def test_zero_sale_keeps_amount_but_percentage_is_not_determinable():
    result = calculate_profitability(
        _payload(sale=_sale("0"), cost=_cost("70"))
    )

    assert result.calculation_state == "NOT_DETERMINABLE"
    assert result.margin_amount == Decimal("-70")
    assert result.margin_percentage is None
    assert result.limitations == ("SALE_BASIS_ZERO",)


@pytest.mark.parametrize(
    "sale_state,cost_state,expected",
    [
        ("NOT_EVIDENCED", "KNOWN", "NOT_EVIDENCED"),
        ("KNOWN", "NOT_EVIDENCED", "NOT_EVIDENCED"),
        ("NOT_DETERMINABLE", "KNOWN", "NOT_DETERMINABLE"),
        ("KNOWN", "NOT_DETERMINABLE", "NOT_DETERMINABLE"),
        ("CONFLICTING_DATA", "KNOWN", "CONFLICTING_DATA"),
        ("KNOWN", "CONFLICTING_DATA", "CONFLICTING_DATA"),
        ("NOT_EVIDENCED", "CONFLICTING_DATA", "CONFLICTING_DATA"),
    ],
)
def test_non_known_states_fail_closed(sale_state, cost_state, expected):
    sale = (
        _sale()
        if sale_state == "KNOWN"
        else _sale(None, state=sale_state, source_ref=None, trace_refs=())
    )
    cost = (
        _cost()
        if cost_state == "KNOWN"
        else _cost(None, state=cost_state, source_ref=None, trace_refs=())
    )

    result = calculate_profitability(_payload(sale=sale, cost=cost))

    assert result.calculation_state == expected
    assert result.margin_amount is None
    assert result.margin_percentage is None


def test_currency_incompatibility_is_not_determinable():
    result = calculate_profitability(
        _payload(cost=_cost(currency="USD"))
    )

    assert result.calculation_state == "NOT_DETERMINABLE"
    assert result.margin_amount is None
    assert result.margin_percentage is None
    assert result.limitations == ("CURRENCY_INCOMPATIBLE",)


def test_economic_basis_incompatibility_is_not_determinable():
    result = calculate_profitability(
        _payload(cost=_cost(economic_basis_ref="BASIS:ORDER"))
    )

    assert result.calculation_state == "NOT_DETERMINABLE"
    assert result.margin_amount is None
    assert result.margin_percentage is None
    assert result.limitations == ("ECONOMIC_BASIS_INCOMPATIBLE",)


def test_both_compatibility_failures_are_reported():
    result = calculate_profitability(
        _payload(cost=_cost(currency="USD", economic_basis_ref="BASIS:ORDER"))
    )

    assert result.limitations == (
        "CURRENCY_INCOMPATIBLE",
        "ECONOMIC_BASIS_INCOMPATIBLE",
    )


@pytest.mark.parametrize(
    "field,value",
    [
        ("decision_id", "DEC-OTHER"),
        ("scenario_id", "SCN-OTHER"),
        ("data_snapshot_id", "snap-other"),
        ("company_scope", "COMPANY-B"),
        ("article_id", "ART-OTHER"),
        ("evaluation_date", date(2026, 9, 19)),
    ],
)
def test_sale_identity_mismatch_is_structural_error(field, value):
    sale = _sale(**{field: value})
    with pytest.raises(ValidationError, match="sale_basis"):
        _payload(sale=sale)


@pytest.mark.parametrize(
    "field,value",
    [
        ("decision_id", "DEC-OTHER"),
        ("scenario_id", "SCN-OTHER"),
        ("data_snapshot_id", "snap-other"),
        ("company_scope", "COMPANY-B"),
        ("article_id", "ART-OTHER"),
        ("evaluation_date", date(2026, 9, 19)),
    ],
)
def test_cost_identity_mismatch_is_structural_error(field, value):
    cost = _cost(**{field: value})
    with pytest.raises(ValidationError, match="cost_basis"):
        _payload(cost=cost)


def test_purchase_identity_must_match_context():
    purchase = _purchase().model_copy(update={"decision_id": "DEC-OTHER"})
    with pytest.raises(ValidationError, match="decision_id"):
        _payload(purchase=purchase)


@pytest.mark.parametrize(
    "field",
    ["value", "currency", "economic_basis_ref", "authority_ref", "source_ref"],
)
def test_known_sale_requires_authorized_material(field):
    kwargs = {field: None}
    if field == "value":
        kwargs["value"] = None
    with pytest.raises(ValidationError, match="KNOWN requiere"):
        _sale(**kwargs)


def test_known_basis_requires_trace():
    with pytest.raises(ValidationError, match="trace_ref"):
        _sale(trace_refs=())


def test_non_known_basis_cannot_publish_value():
    with pytest.raises(ValidationError, match="no KNOWN"):
        _sale("10", state="NOT_EVIDENCED")


@pytest.mark.parametrize("factory", [_sale, _cost])
def test_negative_basis_is_rejected_in_v01(factory):
    with pytest.raises(ValidationError):
        factory("-1")


def test_non_finite_basis_is_rejected():
    with pytest.raises(ValidationError):
        _sale("NaN")


def test_input_is_frozen():
    payload = _payload()
    with pytest.raises(ValidationError):
        payload.company_scope = "OTHER"


def test_bases_are_frozen():
    basis = _sale()
    with pytest.raises(ValidationError):
        basis.value = Decimal("1")


def test_extra_fields_are_forbidden():
    data = _basis_kwargs()
    data["value"] = Decimal("100")
    data["extra_field"] = "x"
    with pytest.raises(ValidationError):
        AuthorizedSaleBasis(**data)


def test_engine_rejects_non_profitability_input():
    with pytest.raises(TypeError, match="ProfitabilityInput"):
        calculate_profitability(object())


def test_result_retains_exact_authorized_bases():
    payload = _payload()
    result = calculate_profitability(payload)

    assert result.sale_basis is payload.sale_basis
    assert result.cost_basis is payload.cost_basis


def test_trace_refs_are_ordered_and_deduplicated():
    sale = _sale(trace_refs=("T1", "T2"))
    cost = _cost(trace_refs=("T2", "T3"))

    result = calculate_profitability(_payload(sale=sale, cost=cost))

    assert result.trace_refs == ("T1", "T2", "T3")


def test_core_does_not_depend_on_price_tco_rules_crc_or_io():
    root = Path(__file__).parents[1]
    source = (
        root / "eios" / "profitability" / "engine.py"
    ).read_text(encoding="utf-8")

    forbidden = (
        "eios.pricing",
        "eios.tco",
        "eios.rules",
        "crc",
        "requests",
        "httpx",
        "socket",
        "open(",
        "Path(",
        "date.today",
        "datetime.now",
    )
    for token in forbidden:
        assert token not in source


def test_core_does_not_expose_decisional_outputs():
    result = calculate_profitability(_payload())
    public = {name for name in dir(result) if not name.startswith("_")}

    assert "assessment" not in public
    assert "outcome" not in public
    assert "recommendation" not in public
    assert "decision" not in public
    assert "crc" not in public
