from datetime import date, timedelta
from decimal import Decimal

import pytest
from pydantic import ValidationError

from eios.core.models import DecisionContext
from eios.stock.engine import calculate_confirmed_demand_absorption, calculate_stock_projection
from eios.stock.models import (
    AllocationLedgerEntry,
    AllocationLedgerSnapshot,
    AllocationScope,
    CollectionEnvelope,
    ConfiguredParameterValue,
    ConfirmedDemandAbsorptionResult,
    ConfirmedDemandRecord,
    DemandAllocation,
    DemandMethodSelection,
    DemandProjectionSchedule,
    DemandRateResult,
    ExcessResult,
    IncorporatedDemandQuantity,
    NormalizedQuantity,
    ProjectedDateMetric,
    ProjectedDecimalMetric,
    ProjectionHorizon,
    ProjectionMovement,
    ProjectionPoint,
    StockAvailabilityResult,
    StockComputationContext,
    StockProjectionInput,
    StockProjectionResult,
    StockReferenceValue,
    StockResultIdentity,
    StockScope,
)


EVAL = date(2026, 9, 1)
SCOPE = StockScope(company_id="COMP-1", operational_scope_id="WH-1")


def dc():
    return DecisionContext(
        decision_id="D-1",
        scenario_id="S-1",
        rules_version="R-1",
        parameters_version="P-1",
        data_snapshot_id="SNAP-1",
    )


def selection():
    return DemandMethodSelection(
        method="AUTHORIZED_FORECAST",
        state="KNOWN",
        policy_ref="POL",
        policy_version="1",
        applicable_reference_date=EVAL,
        source_ref="SEL-SRC",
    )


def identity(scenario_id="S-1"):
    return StockResultIdentity(
        decision_id="D-1",
        scenario_id=scenario_id,
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


def context():
    return StockComputationContext(
        decision_context=dc(),
        scope=SCOPE,
        article_id="A-1",
        evaluation_date=EVAL,
        base_unit="unit",
        methodology_version="STK-0.17",
        demand_selection=selection(),
        forecast_version="F-1",
    )


def parameter(days=3):
    return ConfiguredParameterValue(
        parameter_id="PYE-001",
        company_id="COMP-1",
        value=days,
        unit="days",
        state="KNOWN",
        parameters_version="P-1",
        applicable_reference_date=EVAL,
        configuration_ref="CFG",
        source_ref="PARAM-SRC",
    )


def horizon(days=3):
    return ProjectionHorizon(
        parameter=parameter(days),
        horizon_days=days,
        horizon_end=EVAL + timedelta(days=days),
        state="KNOWN",
    )


def opening():
    return StockAvailabilityResult(
        identity=identity(),
        stock_available=Decimal("80"),
        availability_deficit=Decimal("0"),
        unit="unit",
        state="KNOWN",
    )


def non_applicable_schedule():
    sel = selection()
    demand = DemandRateResult(
        identity=identity(),
        selection=sel,
        unit="unit",
        state="UNKNOWN",
    )
    return DemandProjectionSchedule(selection=sel, demand=demand, state="NOT_APPLICABLE")


def projection_payload(*movements):
    return StockProjectionInput(
        context=context(),
        opening=opening(),
        movements=CollectionEnvelope[ProjectionMovement](state="KNOWN", items=movements, source_ref="MOV-COL"),
        horizon=horizon(),
        demand_schedule=non_applicable_schedule(),
        scenario_id="S-1",
    )


def m06(mid, kind, when, supply="SUPPLY-1"):
    return ProjectionMovement(
        movement_id=mid,
        supply_identity=supply,
        supplier_id="SUP-1",
        supply_document_ref="PO-1",
        scope=SCOPE,
        article_id="A-1",
        direction="INFLOW",
        quantity=Decimal("5"),
        unit="unit",
        source_unit="unit",
        effective_date=when,
        state="KNOWN",
        source_kind=kind,
        source_ref="M06-SRC",
    )


def proposed(mid, when, scenario_id):
    return ProjectionMovement(
        movement_id=mid,
        scenario_id=scenario_id,
        scope=SCOPE,
        article_id="A-1",
        direction="INFLOW",
        quantity=Decimal("5"),
        unit="unit",
        source_unit="unit",
        effective_date=when,
        state="KNOWN",
        source_kind="PROPOSED_PURCHASE",
        source_ref="PROP-SRC",
    )


def reference():
    return StockReferenceValue(
        identity=identity(),
        reference_kind="CURRENT_AVAILABLE",
        reference_date=EVAL,
        value=Decimal("80"),
        unit="unit",
        state="KNOWN",
        source_ref="REF",
    )


def excess():
    ref = reference()
    return ExcessResult(
        identity=identity(),
        stock_reference=ref,
        stock_maximum=Decimal("50"),
        excess_tolerance_quantity=Decimal("5"),
        excess_threshold=Decimal("55"),
        excess_quantity=Decimal("25"),
        state="EXCESS",
        incorporated_confirmed_demand=(),
    )


def pending(value="30"):
    return NormalizedQuantity(
        scope=SCOPE,
        article_id="A-1",
        value=Decimal(value),
        unit="unit",
        source_unit="unit",
        state="KNOWN",
        source_ref="PENDING",
        effective_date=EVAL,
    )


def order():
    return ConfirmedDemandRecord(
        confirmed_demand_id="O-1",
        order_id="SO-1",
        customer_id="CUST-1",
        scope=SCOPE,
        article_id="A-1",
        pending_quantity=pending(),
        order_date=EVAL - timedelta(days=2),
        confirmation_date=EVAL - timedelta(days=1),
        expected_delivery_date=EVAL + timedelta(days=2),
        business_status="CONFIRMED",
        applicability_state="APLICABLE_Y_VALIDADA",
        applicability_source_ref="APP",
        source_ref="ORDER",
    )


def allocation_scope():
    return AllocationScope(
        identity=identity(),
        scope=SCOPE,
        article_id="A-1",
        evaluation_date=EVAL,
        excess_reference_date=EVAL,
        horizon=horizon(),
    )


def test_j1_m06_duplicate_identity_is_rejected_even_if_one_record_is_outside_horizon():
    inside = m06("M-IN", "PENDING_ORDER", EVAL + timedelta(days=1))
    outside = m06("M-OUT", "IN_TRANSIT", EVAL + timedelta(days=10))
    with pytest.raises(ValueError, match="supply_identity"):
        calculate_stock_projection(projection_payload(inside, outside))


def test_j2_proposed_purchase_from_other_scenario_is_rejected_before_time_gate():
    outside = proposed("PROP-1", EVAL + timedelta(days=10), "S-OTHER")
    with pytest.raises(ValueError, match="scenario_id"):
        calculate_stock_projection(projection_payload(outside))


def test_j3_no_aplicable_requires_demonstrated_exclusion():
    with pytest.raises(ValidationError):
        ConfirmedDemandRecord(
            confirmed_demand_id="O-NA",
            scope=SCOPE,
            article_id="A-1",
            pending_quantity=pending(),
            applicability_state="NO_APLICABLE",
        )


def test_j4_ledger_unit_mismatch_is_rejected_before_aggregation():
    wrong_unit_entry = AllocationLedgerEntry(
        allocation_entry_id="AL-OLD",
        confirmed_demand_id="O-1",
        scope=SCOPE,
        article_id="A-1",
        allocated_quantity=Decimal("1"),
        unit="kg",
        decision_id="D-1",
        scenario_id="S-1",
        excess_reference_date=EVAL,
        allocation_result_ref="OLD",
    )
    ledger = AllocationLedgerSnapshot(
        reference_date=EVAL,
        scope=SCOPE,
        article_id="A-1",
        state="KNOWN",
        entries=(wrong_unit_entry,),
        source_ref="LEDGER",
    )
    with pytest.raises(ValueError, match="unidad incompatible"):
        calculate_confirmed_demand_absorption(
            excess(),
            CollectionEnvelope[ConfirmedDemandRecord](state="KNOWN", items=(order(),), source_ref="ORDERS"),
            ledger,
            allocation_scope(),
        )


def test_j5_excess_identity_must_equal_reference_identity():
    ref = reference()
    with pytest.raises(ValidationError):
        ExcessResult(
            identity=identity("S-OTHER"),
            stock_reference=ref,
            stock_maximum=Decimal("50"),
            excess_tolerance_quantity=Decimal("5"),
            excess_threshold=Decimal("55"),
            excess_quantity=Decimal("25"),
            state="EXCESS",
            incorporated_confirmed_demand=(),
        )


def test_j5_projection_horizon_composition_must_equal_last_point():
    comp = IncorporatedDemandQuantity(
        confirmed_demand_id="O-1",
        quantity=Decimal("1"),
        unit="unit",
        demand_segment_ids=("SEG-1",),
    )
    point = ProjectionPoint(
        reference_date=EVAL + timedelta(days=1),
        projected_stock=Decimal("79"),
        state="KNOWN",
        incorporated_confirmed_demand=(comp,),
    )
    with pytest.raises(ValidationError):
        StockProjectionResult(
            identity=identity(),
            horizon=horizon(),
            points=(point,),
            minimum_projected_stock=ProjectedDecimalMetric(value=Decimal("79"), state="KNOWN"),
            depletion_date=ProjectedDateMetric(state="NOT_APPLICABLE"),
            incorporated_confirmed_demand_at_horizon=(),
            state="KNOWN",
        )


def test_j6_applicable_absorption_requires_positive_exact_plan_and_known_ledger():
    with pytest.raises(ValidationError):
        ConfirmedDemandAbsorptionResult(
            identity=identity(),
            excess_result=excess(),
            business_state="APLICABLE_Y_VALIDADA",
            total_remaining_applicable=Decimal("25"),
            absorbed_excess=Decimal("0"),
            residual_excess=Decimal("25"),
            allocation_plan=(),
            resulting_ledger=None,
        )


def test_j6_no_aplicable_cannot_carry_allocation_plan():
    plan = DemandAllocation(
        allocation_entry_id="AL-NEW",
        confirmed_demand_id="O-1",
        quantity_to_apply=Decimal("1"),
        unit="unit",
        allocation_source_ref="ALLOC",
    )
    with pytest.raises(ValidationError):
        ConfirmedDemandAbsorptionResult(
            identity=identity(),
            excess_result=excess(),
            business_state="NO_APLICABLE",
            total_remaining_applicable=Decimal("0"),
            absorbed_excess=Decimal("0"),
            residual_excess=Decimal("25"),
            allocation_plan=(plan,),
        )


def test_j7_projection_horizon_rejects_parameter_days_mismatch():
    with pytest.raises(ValidationError):
        ProjectionHorizon(
            parameter=parameter(3),
            horizon_days=2,
            horizon_end=EVAL + timedelta(days=2),
            state="KNOWN",
        )


def test_j7_projection_horizon_rejects_inconsistent_end_date():
    with pytest.raises(ValidationError):
        ProjectionHorizon(
            parameter=parameter(3),
            horizon_days=3,
            horizon_end=EVAL + timedelta(days=4),
            state="KNOWN",
        )
