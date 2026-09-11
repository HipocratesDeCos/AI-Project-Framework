from datetime import date
from decimal import Decimal

import pytest
from pydantic import ValidationError

from eios.core.models import DecisionContext
from eios.finance import (
    CashFlow,
    ExternalLiquidityReference,
    FinanceBasicInput,
    FinancialSnapshot,
    WorkingCapitalInput,
    calculate_finance_basic,
)


def context(**overrides):
    data = {
        "decision_id": "D-1",
        "scenario_id": "S-1",
        "rules_version": "rules-v1",
        "parameters_version": "params-v1",
        "data_snapshot_id": "snap-1",
    }
    data.update(overrides)
    return DecisionContext(**data)


def snapshot(**overrides):
    data = {
        "company_scope": "COMPANY-1",
        "as_of_date": date(2026, 9, 1),
        "data_snapshot_id": "snap-1",
        "currency": "EUR",
        "available_treasury": Decimal("1000"),
        "treasury_evidence_ref": "BANK-1",
    }
    data.update(overrides)
    return FinancialSnapshot(**data)


def flow(flow_id="F-1", **overrides):
    data = {
        "flow_id": flow_id,
        "flow_type": "PAYMENT",
        "amount": Decimal("100"),
        "currency": "EUR",
        "due_date": date(2026, 9, 10),
        "source_ref": f"SRC-{flow_id}",
        "evidence_state": "DEMONSTRATED",
    }
    data.update(overrides)
    return CashFlow(**data)


def payload(**overrides):
    data = {
        "context": context(),
        "snapshot": snapshot(),
        "cash_flows": (),
        "horizon_days": 30,
        "treasury_minimum": Decimal("500"),
    }
    data.update(overrides)
    return FinanceBasicInput(**data)


def test_simple_projection_and_financial_capacity():
    result = calculate_finance_basic(
        payload(
            cash_flows=(
                flow(
                    "C-1",
                    flow_type="COLLECTION",
                    amount=Decimal("200"),
                    due_date=date(2026, 9, 5),
                ),
                flow("P-1", amount=Decimal("500"), due_date=date(2026, 9, 10)),
            )
        )
    )

    assert result.projection.status == "DETERMINED"
    assert [point.treasury_after for point in result.projection.points] == [
        Decimal("1200"),
        Decimal("700"),
    ]
    assert result.projection.financial_capacity_forecast == Decimal("700")


def test_same_day_flows_are_aggregated_before_capacity_and_order_is_irrelevant():
    payment = flow("P-1", amount=Decimal("800"), due_date=date(2026, 9, 10))
    collection = flow(
        "C-1",
        flow_type="COLLECTION",
        amount=Decimal("700"),
        due_date=date(2026, 9, 10),
    )

    first = calculate_finance_basic(payload(cash_flows=(payment, collection)))
    second = calculate_finance_basic(payload(cash_flows=(collection, payment)))

    assert first.projection == second.projection
    assert len(first.projection.points) == 1
    assert first.projection.points[0].treasury_after == Decimal("900")
    assert first.projection.financial_capacity_forecast == Decimal("900")


def test_duplicate_flow_ids_are_rejected():
    with pytest.raises(ValidationError):
        payload(cash_flows=(flow("F-1"), flow("F-1")))


def test_demonstrated_flow_after_horizon_is_excluded_without_gap():
    result = calculate_finance_basic(
        payload(cash_flows=(flow("F-OUT", due_date=date(2026, 10, 15), amount=Decimal("9999")),))
    )
    assert result.projection.status == "DETERMINED"
    assert result.projection.points == ()
    assert result.projection.financial_capacity_forecast == Decimal("1000")


def test_not_evidenced_flow_with_evidenced_date_after_horizon_does_not_contaminate():
    unresolved_outside = CashFlow(
        flow_id="F-OUT",
        flow_type="PAYMENT",
        amount=None,
        currency=None,
        due_date=date(2026, 10, 15),
        due_date_evidenced=True,
        source_ref="DATE-SRC-F-OUT",
        evidence_state="NOT_EVIDENCED",
    )
    result = calculate_finance_basic(payload(cash_flows=(unresolved_outside,)))
    assert result.projection.status == "DETERMINED"
    assert result.projection.financial_capacity_forecast == Decimal("1000")


def test_not_evidenced_flow_with_unevidenced_date_after_horizon_remains_incomplete():
    unresolved = CashFlow(
        flow_id="F-OUT-UNPROVEN",
        flow_type="PAYMENT",
        amount=None,
        currency=None,
        due_date=date(2026, 10, 15),
        due_date_evidenced=False,
        source_ref=None,
        evidence_state="NOT_EVIDENCED",
    )
    result = calculate_finance_basic(payload(cash_flows=(unresolved,)))
    assert result.projection.status == "NOT_EVIDENCED"
    assert result.projection.unresolved_flow_ids == ("F-OUT-UNPROVEN",)


def test_conflicting_flow_with_evidenced_date_after_horizon_does_not_contaminate():
    conflicting_outside = CashFlow(
        flow_id="F-CON-OUT",
        flow_type="PAYMENT",
        amount=None,
        currency=None,
        due_date=date(2026, 10, 15),
        due_date_evidenced=True,
        source_ref="DATE-SRC-F-CON-OUT",
        evidence_state="CONFLICTING_DATA",
    )
    result = calculate_finance_basic(payload(cash_flows=(conflicting_outside,)))
    assert result.projection.status == "DETERMINED"
    assert "OUT_OF_HORIZON_CONFLICT:F-CON-OUT" in result.projection.limitations


def test_conflicting_flow_with_unevidenced_date_after_horizon_stays_conflicting():
    conflicting = CashFlow(
        flow_id="F-CON-UNPROVEN",
        flow_type="PAYMENT",
        amount=None,
        currency=None,
        due_date=date(2026, 10, 15),
        due_date_evidenced=False,
        source_ref=None,
        evidence_state="CONFLICTING_DATA",
    )
    result = calculate_finance_basic(payload(cash_flows=(conflicting,)))
    assert result.projection.status == "CONFLICTING_DATA"


def test_due_date_evidenced_requires_due_date():
    with pytest.raises(ValidationError):
        CashFlow(
            flow_id="F-NODATE",
            flow_type="PAYMENT",
            amount=None,
            currency=None,
            due_date=None,
            due_date_evidenced=True,
            source_ref="DATE-SRC",
            evidence_state="NOT_EVIDENCED",
        )


def test_due_date_evidenced_requires_source_ref():
    with pytest.raises(ValidationError):
        CashFlow(
            flow_id="F-NOSOURCE",
            flow_type="PAYMENT",
            amount=None,
            currency=None,
            due_date=date(2026, 10, 15),
            due_date_evidenced=True,
            source_ref=None,
            evidence_state="NOT_EVIDENCED",
        )


def test_not_evidenced_flow_with_unknown_date_makes_projection_incomplete():
    unresolved = CashFlow(
        flow_id="F-UNK",
        flow_type="PAYMENT",
        amount=None,
        currency=None,
        due_date=None,
        source_ref=None,
        evidence_state="NOT_EVIDENCED",
    )
    result = calculate_finance_basic(payload(cash_flows=(unresolved,)))
    assert result.projection.status == "NOT_EVIDENCED"
    assert result.projection.financial_capacity_forecast is None
    assert result.projection.points == ()
    assert result.projection.unresolved_flow_ids == ("F-UNK",)


def test_relevant_conflicting_flow_preserves_conflict():
    conflicting = CashFlow(
        flow_id="F-CONFLICT",
        flow_type="PAYMENT",
        amount=Decimal("100"),
        currency=None,
        due_date=date(2026, 9, 10),
        source_ref="SRC-X",
        evidence_state="CONFLICTING_DATA",
    )
    result = calculate_finance_basic(payload(cash_flows=(conflicting,)))
    assert result.projection.status == "CONFLICTING_DATA"
    assert result.projection.financial_capacity_forecast is None


def test_incompatible_currency_is_not_converted():
    usd = flow("USD-1", currency="usd")
    result = calculate_finance_basic(payload(cash_flows=(usd,)))
    assert usd.currency == "USD"
    assert result.projection.status == "NOT_EVALUABLE"
    assert "CURRENCY_INCOMPATIBLE:USD-1" in result.projection.limitations


def test_non_future_demonstrated_flow_is_not_reinterpreted():
    past = flow("PAST-1", due_date=date(2026, 9, 1))
    result = calculate_finance_basic(payload(cash_flows=(past,)))
    assert result.projection.status == "NOT_EVALUABLE"
    assert "NON_FUTURE_FLOW:PAST-1" in result.projection.limitations


def test_missing_opening_treasury_is_not_zero():
    result = calculate_finance_basic(
        payload(snapshot=snapshot(available_treasury=None, treasury_evidence_ref=None))
    )
    assert result.projection.status == "NOT_EVIDENCED"
    assert result.projection.opening_treasury is None
    assert result.projection.financial_capacity_forecast is None


def test_negative_available_treasury_is_rejected():
    with pytest.raises(ValidationError):
        snapshot(available_treasury=Decimal("-1"))


def test_demonstrated_flow_requires_currency_amount_date_and_source():
    with pytest.raises(ValidationError):
        CashFlow(
            flow_id="F-X",
            flow_type="PAYMENT",
            amount=Decimal("1"),
            currency=None,
            due_date=date(2026, 9, 2),
            source_ref="SRC",
            evidence_state="DEMONSTRATED",
        )


def test_horizon_must_be_representable_from_snapshot_date():
    with pytest.raises(ValidationError):
        payload(horizon_days=10**12)


def test_working_capital_is_calculated_from_supplied_accounting_totals():
    wc = WorkingCapitalInput(
        company_scope="COMPANY-1",
        as_of_date=date(2026, 9, 1),
        currency="EUR",
        current_assets=Decimal("500"),
        current_liabilities=Decimal("300"),
        assets_source_ref="BAL-A",
        liabilities_source_ref="BAL-L",
    )
    result = calculate_finance_basic(payload(working_capital_input=wc))
    assert result.working_capital.status == "DETERMINED"
    assert result.working_capital.value == Decimal("200")


def test_partial_working_capital_is_not_evidenced():
    wc = WorkingCapitalInput(
        company_scope="COMPANY-1",
        as_of_date=date(2026, 9, 1),
        currency="EUR",
        current_assets=Decimal("500"),
        current_liabilities=None,
        assets_source_ref="BAL-A",
        liabilities_source_ref=None,
    )
    result = calculate_finance_basic(payload(working_capital_input=wc))
    assert result.working_capital.status == "NOT_EVIDENCED"
    assert result.working_capital.value is None


def test_working_capital_incompatibility_does_not_break_cash_projection():
    wc = WorkingCapitalInput(
        company_scope="OTHER-COMPANY",
        as_of_date=date(2026, 9, 1),
        currency="EUR",
        current_assets=Decimal("500"),
        current_liabilities=Decimal("300"),
        assets_source_ref="BAL-A",
        liabilities_source_ref="BAL-L",
    )
    result = calculate_finance_basic(payload(working_capital_input=wc))
    assert result.projection.status == "DETERMINED"
    assert result.working_capital.status == "NOT_EVALUABLE"
    assert "WORKING_CAPITAL_SCOPE_INCOMPATIBLE" in result.working_capital.limitations


def test_safety_margin_is_calculated_without_business_rounding():
    result = calculate_finance_basic(payload(treasury_minimum=Decimal("300")))
    assert result.projection.financial_capacity_forecast == Decimal("1000")
    assert result.safety_margin.status == "DETERMINED"
    assert result.safety_margin.value_pct == (Decimal("700") / Decimal("300") * Decimal("100"))


def test_missing_treasury_minimum_is_not_evidenced():
    result = calculate_finance_basic(payload(treasury_minimum=None))
    assert result.safety_margin.status == "NOT_EVIDENCED"
    assert result.safety_margin.value_pct is None


def test_non_positive_treasury_minimum_is_not_evaluable():
    for minimum in (Decimal("0"), Decimal("-1")):
        result = calculate_finance_basic(payload(treasury_minimum=minimum))
        assert result.safety_margin.status == "NOT_EVALUABLE"
        assert result.safety_margin.value_pct is None


def test_projection_status_precedence_is_independent_of_flow_order():
    incompatible = flow("USD-1", currency="USD")
    missing = CashFlow(
        flow_id="MISS-1",
        flow_type="PAYMENT",
        evidence_state="NOT_EVIDENCED",
        amount=None,
        currency=None,
        due_date=None,
        source_ref=None,
    )
    conflict = CashFlow(
        flow_id="CON-1",
        flow_type="COLLECTION",
        evidence_state="CONFLICTING_DATA",
        amount=None,
        currency=None,
        due_date=date(2026, 9, 12),
        source_ref=None,
    )

    first = calculate_finance_basic(payload(cash_flows=(incompatible, missing, conflict)))
    second = calculate_finance_basic(payload(cash_flows=(conflict, missing, incompatible)))
    assert first.projection.status == "CONFLICTING_DATA"
    assert second.projection.status == "CONFLICTING_DATA"
    assert set(first.projection.limitations) == set(second.projection.limitations)


def test_external_liquidity_is_preserved_but_does_not_change_projection():
    liquidity = ExternalLiquidityReference(
        value=Decimal("1.50"),
        unit="ratio",
        source_ref="ERP-LIQ-1",
    )
    result = calculate_finance_basic(
        payload(snapshot=snapshot(external_liquidity=liquidity))
    )
    assert result.external_liquidity == liquidity
    assert result.projection.financial_capacity_forecast == Decimal("1000")


def test_snapshot_and_context_identity_must_match():
    with pytest.raises(ValidationError):
        payload(snapshot=snapshot(data_snapshot_id="other-snapshot"))


def test_engine_does_not_mutate_inputs():
    item = payload(cash_flows=(flow("F-1"),))
    before = item.model_dump()
    calculate_finance_basic(item)
    assert item.model_dump() == before


def test_result_has_no_decisional_fields():
    result = calculate_finance_basic(payload())
    serialized = result.model_dump()
    for forbidden in ("recommendation", "assessment", "effect", "severity", "crc_result"):
        assert forbidden not in serialized
