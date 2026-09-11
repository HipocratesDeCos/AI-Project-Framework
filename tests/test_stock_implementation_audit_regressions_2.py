from datetime import date, timedelta
from decimal import Decimal

import pytest

from eios.core.models import DecisionContext
from eios.stock.engine import (
    build_projection_horizon,
    calculate_confirmed_demand_absorption,
    calculate_stock_availability,
    calculate_stock_projection,
)
from eios.stock.models import (
    AllocationLedgerSnapshot,
    AllocationScope,
    CollectionEnvelope,
    ConfiguredParameterValue,
    ConfirmedDemandRecord,
    DemandMethodSelection,
    DemandProjectionSchedule,
    DemandRateResult,
    ExcessResult,
    NormalizedQuantity,
    ProjectedDateMetric,
    ProjectedDecimalMetric,
    ProjectionHorizon,
    ProjectionMovement,
    StockAvailabilityInput,
    StockAvailabilityResult,
    StockComputationContext,
    StockProjectionInput,
    StockReferenceValue,
    StockResultIdentity,
    StockScope,
)


EVAL = date(2026, 9, 1)
SCOPE = StockScope(company_id="COMP-1", operational_scope_id="WH-1")


def _dc():
    return DecisionContext(
        decision_id="D-1",
        scenario_id="S-1",
        rules_version="R-1",
        parameters_version="P-1",
        data_snapshot_id="SNAP-1",
    )


def _selection():
    return DemandMethodSelection(
        method="AUTHORIZED_FORECAST",
        state="KNOWN",
        policy_ref="POL",
        policy_version="1",
        applicable_reference_date=EVAL,
        source_ref="SEL",
    )


def _context():
    return StockComputationContext(
        decision_context=_dc(),
        scope=SCOPE,
        article_id="A-1",
        evaluation_date=EVAL,
        base_unit="unit",
        methodology_version="STK-0.17",
        demand_selection=_selection(),
        forecast_version="F-1",
    )


def _identity():
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
        forecast_version="F-1",
    )


def _pye(days=3):
    return ConfiguredParameterValue(
        parameter_id="PYE-001",
        company_id="COMP-1",
        value=days,
        unit="days",
        state="KNOWN",
        parameters_version="P-1",
        applicable_reference_date=EVAL,
        configuration_ref="CFG",
        source_ref="SRC",
    )


def _q(value, effective=EVAL):
    return NormalizedQuantity(
        scope=SCOPE,
        article_id="A-1",
        value=Decimal(value),
        unit="unit",
        source_unit="unit",
        state="KNOWN",
        source_ref="Q",
        effective_date=effective,
    )


def _opening(ctx):
    return calculate_stock_availability(
        StockAvailabilityInput(
            context=ctx,
            stock_on_hand=_q("80"),
            stock_committed=_q("0"),
            committed_components=CollectionEnvelope(state="KNOWN", items=(), source_ref="COMMIT"),
        )
    )


def test_i1_not_applicable_schedule_prevents_known_projection():
    ctx = _context()
    opening = _opening(ctx)
    horizon = build_projection_horizon(ctx, _pye())
    demand = DemandRateResult(
        identity=_identity(),
        selection=ctx.demand_selection,
        method="AUTHORIZED_FORECAST",
        daily_demand=Decimal("1"),
        unit="unit",
        state="KNOWN",
        reference_date=EVAL,
        applicable_from=EVAL,
        applicable_to=horizon.horizon_end,
        forecast_version="F-1",
    )
    schedule = DemandProjectionSchedule(
        selection=ctx.demand_selection,
        demand=demand,
        state="NOT_APPLICABLE",
    )
    payload = StockProjectionInput(
        context=ctx,
        opening=opening,
        movements=CollectionEnvelope[ProjectionMovement](state="KNOWN", items=(), source_ref="MOV"),
        horizon=horizon,
        demand_schedule=schedule,
        scenario_id="S-1",
    )
    result = calculate_stock_projection(payload)
    assert result.state == "NOT_APPLICABLE"
    assert result.minimum_projected_stock.state == "NOT_APPLICABLE"
    assert result.depletion_date.state == "NOT_APPLICABLE"


def test_i3_validated_applicable_order_outside_horizon_is_structural_error():
    identity = _identity()
    ref = StockReferenceValue(
        identity=identity,
        reference_kind="CURRENT_AVAILABLE",
        reference_date=EVAL,
        value=Decimal("80"),
        unit="unit",
        state="KNOWN",
        source_ref="REF",
    )
    excess = ExcessResult(
        identity=identity,
        stock_reference=ref,
        stock_maximum=Decimal("50"),
        excess_tolerance_quantity=Decimal("5"),
        excess_threshold=Decimal("55"),
        excess_quantity=Decimal("25"),
        state="EXCESS",
        incorporated_confirmed_demand=(),
    )
    horizon = ProjectionHorizon(
        parameter=_pye(3),
        horizon_days=3,
        horizon_end=EVAL + timedelta(days=3),
        state="KNOWN",
    )
    scope = AllocationScope(
        identity=identity,
        scope=SCOPE,
        article_id="A-1",
        evaluation_date=EVAL,
        excess_reference_date=EVAL,
        horizon=horizon,
    )
    order = ConfirmedDemandRecord(
        confirmed_demand_id="O-1",
        order_id="SO-1",
        customer_id="C-1",
        scope=SCOPE,
        article_id="A-1",
        pending_quantity=_q("10"),
        order_date=EVAL - timedelta(days=2),
        confirmation_date=EVAL - timedelta(days=1),
        expected_delivery_date=EVAL + timedelta(days=5),
        business_status="CONFIRMED",
        applicability_state="APLICABLE_Y_VALIDADA",
        applicability_source_ref="APP",
        source_ref="ORDER",
    )
    ledger = AllocationLedgerSnapshot(
        reference_date=EVAL,
        scope=SCOPE,
        article_id="A-1",
        state="KNOWN",
        source_ref="LEDGER",
    )
    with pytest.raises(ValueError):
        calculate_confirmed_demand_absorption(
            excess,
            CollectionEnvelope[ConfirmedDemandRecord](state="KNOWN", items=(order,), source_ref="ORDERS"),
            ledger,
            scope,
        )
