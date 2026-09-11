from datetime import date, timedelta
from decimal import Decimal

import pytest

from eios.stock.engine import calculate_confirmed_demand_absorption
from eios.stock.models import (
    AllocationLedgerSnapshot,
    AllocationScope,
    CollectionEnvelope,
    ConfiguredParameterValue,
    ConfirmedDemandRecord,
    ExcessResult,
    NormalizedQuantity,
    ProjectionHorizon,
    StockReferenceValue,
    StockResultIdentity,
    StockScope,
)


EVAL = date(2026, 9, 1)
SCOPE = StockScope(company_id="COMP-1", operational_scope_id="WH-1")
OTHER_SCOPE = StockScope(company_id="COMP-1", operational_scope_id="WH-X")


def identity():
    return StockResultIdentity(
        decision_id="D-1",
        scenario_id="S-1",
        rules_version="R-1",
        parameters_version="P-1",
        data_snapshot_id="SNAP-1",
        company_id="COMP-1",
        operational_scope_id="WH-1",
        article_id="A-1",
        evaluation_date=EVAL,
        base_unit="unit",
        methodology_version="STK-0.17",
    )


def pye():
    return ConfiguredParameterValue(
        parameter_id="PYE-001",
        company_id="COMP-1",
        value=3,
        unit="days",
        state="KNOWN",
        parameters_version="P-1",
        applicable_reference_date=EVAL,
        configuration_ref="CFG",
        source_ref="SRC",
    )


def scope():
    return AllocationScope(
        identity=identity(),
        scope=SCOPE,
        article_id="A-1",
        evaluation_date=EVAL,
        excess_reference_date=EVAL,
        horizon=ProjectionHorizon(
            parameter=pye(),
            horizon_days=3,
            horizon_end=EVAL + timedelta(days=3),
            state="KNOWN",
        ),
    )


def reference(value="80"):
    return StockReferenceValue(
        identity=identity(),
        reference_kind="CURRENT_AVAILABLE",
        reference_date=EVAL,
        value=Decimal(value),
        unit="unit",
        state="KNOWN",
        source_ref="REF",
    )


def excess(state="EXCESS"):
    ref = reference()
    return ExcessResult(
        identity=identity(),
        stock_reference=ref,
        stock_maximum=Decimal("50"),
        excess_tolerance_quantity=Decimal("5"),
        excess_threshold=Decimal("55"),
        excess_quantity=Decimal("25") if state == "EXCESS" else Decimal("0"),
        state=state,
        incorporated_confirmed_demand=(),
    )


def ledger(state="NOT_EVIDENCED", scope_value=SCOPE):
    return AllocationLedgerSnapshot(
        reference_date=EVAL,
        scope=scope_value,
        article_id="A-1",
        state=state,
        source_ref="LEDGER" if state == "KNOWN" else None,
    )


def pending():
    return NormalizedQuantity(
        scope=SCOPE,
        article_id="A-1",
        value=Decimal("10"),
        unit="unit",
        source_unit="unit",
        state="KNOWN",
        source_ref="PENDING",
        effective_date=EVAL,
    )


def no_applicable_order():
    return ConfirmedDemandRecord(
        confirmed_demand_id="O-NA",
        scope=SCOPE,
        article_id="A-1",
        pending_quantity=pending(),
        applicability_state="NO_APLICABLE",
        applicability_source_ref="EXCLUSION-POLICY",
        source_ref="ORDER-SRC",
    )


def applicable_order():
    return ConfirmedDemandRecord(
        confirmed_demand_id="O-A",
        order_id="SO-1",
        customer_id="C-1",
        scope=SCOPE,
        article_id="A-1",
        pending_quantity=pending(),
        order_date=EVAL - timedelta(days=2),
        confirmation_date=EVAL - timedelta(days=1),
        expected_delivery_date=EVAL + timedelta(days=2),
        business_status="CONFIRMED",
        applicability_state="APLICABLE_Y_VALIDADA",
        applicability_source_ref="APP",
        source_ref="ORDER-SRC",
    )


def test_no_excess_preserves_input_ledger_without_requiring_it_known():
    input_ledger = ledger("NOT_EVIDENCED")
    result = calculate_confirmed_demand_absorption(
        excess("NO_EXCESS"),
        CollectionEnvelope[ConfirmedDemandRecord](state="NOT_EVIDENCED"),
        input_ledger,
        scope(),
    )
    assert result.business_state == "NO_APLICABLE"
    assert result.resulting_ledger == input_ledger
    assert result.issue_refs == ()


def test_all_orders_explicitly_excluded_do_not_make_ledger_material():
    input_ledger = ledger("NOT_EVIDENCED")
    result = calculate_confirmed_demand_absorption(
        excess("EXCESS"),
        CollectionEnvelope[ConfirmedDemandRecord](state="KNOWN", items=(no_applicable_order(),), source_ref="ORDERS"),
        input_ledger,
        scope(),
    )
    assert result.business_state == "NO_APLICABLE"
    assert result.absorbed_excess == Decimal("0")
    assert result.residual_excess == Decimal("25")
    assert result.resulting_ledger == input_ledger
    assert result.issue_refs == ()


def test_ledger_scope_mismatch_is_structural_even_when_no_excess():
    with pytest.raises(ValueError, match="Ledger incompatible"):
        calculate_confirmed_demand_absorption(
            excess("NO_EXCESS"),
            CollectionEnvelope[ConfirmedDemandRecord](state="NOT_EVIDENCED"),
            ledger("NOT_EVIDENCED", OTHER_SCOPE),
            scope(),
        )


def test_applicable_order_is_incompatible_with_non_excess_result():
    with pytest.raises(ValueError, match="requiere ExcessResult EXCESS"):
        calculate_confirmed_demand_absorption(
            excess("NO_EXCESS"),
            CollectionEnvelope[ConfirmedDemandRecord](state="KNOWN", items=(applicable_order(),), source_ref="ORDERS"),
            ledger("NOT_EVIDENCED"),
            scope(),
        )
