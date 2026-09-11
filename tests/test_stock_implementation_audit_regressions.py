from datetime import date, timedelta
from decimal import Decimal

import pytest
from pydantic import ValidationError

from eios.core.models import DecisionContext
from eios.stock.models import (
    AllocationLedgerEntry,
    AllocationLedgerSnapshot,
    AllocationScope,
    CollectionEnvelope,
    ConfiguredParameterValue,
    ConfirmedDemandAbsorptionResult,
    ConsumptionPeriod,
    DemandMethodSelection,
    DemandProjectionSchedule,
    DemandRateResult,
    ExcessResult,
    HistoricalDemandPolicy,
    IncorporatedDemandQuantity,
    NormalizedQuantity,
    ProjectionHorizon,
    ProjectedDateMetric,
    ProjectedDecimalMetric,
    RequiredPeriodSpec,
    StockComputationContext,
    StockProjectionInput,
    StockProjectionResult,
    StockReferenceValue,
    StockResultIdentity,
    StockScope,
)
from eios.stock.engine import (
    calculate_confirmed_demand_absorption,
    calculate_historical_demand,
)


EVAL = date(2026, 9, 1)
SCOPE = StockScope(company_id="COMP-1", operational_scope_id="WH-1")
OTHER_SCOPE = StockScope(company_id="COMP-1", operational_scope_id="WH-2")


def _dc() -> DecisionContext:
    return DecisionContext(
        decision_id="D-1",
        scenario_id="S-1",
        rules_version="R-1",
        parameters_version="P-1",
        data_snapshot_id="SNAP-1",
    )


def _selection(method="HISTORICAL_CONSUMPTION") -> DemandMethodSelection:
    return DemandMethodSelection(
        method=method,
        state="KNOWN",
        policy_ref="POL",
        policy_version="1",
        applicable_reference_date=EVAL,
        source_ref="SEL-SRC",
    )


def _context(method="HISTORICAL_CONSUMPTION", forecast_version=None) -> StockComputationContext:
    return StockComputationContext(
        decision_context=_dc(),
        scope=SCOPE,
        article_id="A-1",
        evaluation_date=EVAL,
        base_unit="unit",
        methodology_version="STK-0.17",
        demand_selection=_selection(method),
        forecast_version=forecast_version,
    )


def _identity(forecast_version=None) -> StockResultIdentity:
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
        forecast_version=forecast_version,
    )


def _pye001(days=3) -> ConfiguredParameterValue:
    return ConfiguredParameterValue(
        parameter_id="PYE-001",
        company_id="COMP-1",
        value=days,
        unit="days",
        state="KNOWN",
        parameters_version="P-1",
        applicable_reference_date=EVAL,
        configuration_ref="CFG-PYE-1",
        source_ref="PARAM-SRC",
    )


def _horizon(days=3) -> ProjectionHorizon:
    return ProjectionHorizon(
        parameter=_pye001(days),
        horizon_days=days,
        horizon_end=EVAL + timedelta(days=days),
        state="KNOWN",
    )


def _reference(state="KNOWN") -> StockReferenceValue:
    return StockReferenceValue(
        identity=_identity(),
        reference_kind="CURRENT_AVAILABLE",
        reference_date=EVAL,
        value=Decimal("80") if state == "KNOWN" else None,
        unit="unit",
        state=state,
        source_ref="REF-SRC",
    )


def _excess(state="EXCESS") -> ExcessResult:
    ref = _reference("KNOWN" if state in {"EXCESS", "NO_EXCESS", "WITHIN_TOLERANCE"} else state)
    if state in {"EXCESS", "NO_EXCESS", "WITHIN_TOLERANCE"}:
        values = dict(
            stock_maximum=Decimal("50"),
            excess_tolerance_quantity=Decimal("5"),
            excess_threshold=Decimal("55"),
            excess_quantity=Decimal("25") if state == "EXCESS" else Decimal("0"),
        )
    else:
        values = {}
    return ExcessResult(
        identity=_identity(),
        stock_reference=ref,
        state=state,
        incorporated_confirmed_demand=ref.incorporated_confirmed_demand,
        **values,
    )


def _scope(horizon=None) -> AllocationScope:
    return AllocationScope(
        identity=_identity(),
        scope=SCOPE,
        article_id="A-1",
        evaluation_date=EVAL,
        excess_reference_date=EVAL,
        horizon=horizon or _horizon(),
    )


def test_i1_required_historical_period_not_applicable_never_becomes_known():
    ctx = _context()
    parameter = ConfiguredParameterValue(
        parameter_id="STK-006",
        company_id="COMP-1",
        value=1,
        unit="months",
        state="KNOWN",
        parameters_version="P-1",
        applicable_reference_date=EVAL,
        configuration_ref="CFG-STK-006",
        source_ref="PARAM-SRC",
    )
    policy = HistoricalDemandPolicy(
        parameter=parameter,
        required_periods=(RequiredPeriodSpec(period_id="P1", period_start=date(2026, 8, 1), period_end=date(2026, 8, 31)),),
        period_calendar_ref="CAL",
        source_ref="POL-SRC",
        state="KNOWN",
    )
    period = ConsumptionPeriod(
        scope=SCOPE,
        article_id="A-1",
        period_id="P1",
        period_start=date(2026, 8, 1),
        period_end=date(2026, 8, 31),
        unit="unit",
        state="NOT_APPLICABLE",
        methodology_version="STK-0.17",
    )
    with pytest.raises(ValueError):
        calculate_historical_demand(
            ctx,
            policy,
            CollectionEnvelope[ConsumptionPeriod](state="KNOWN", items=(period,), source_ref="PERIODS"),
        )


def test_i2_no_verificable_does_not_require_invented_issue_reference():
    result = ConfirmedDemandAbsorptionResult(
        identity=_identity(),
        excess_result=_excess("UNKNOWN"),
        business_state="NO_VERIFICABLE",
    )
    assert result.issue_refs == ()
    assert result.absorbed_excess is None


def test_i4_allocation_scope_rejects_horizon_with_wrong_parameter_version():
    bad_parameter = _pye001().model_copy(update={"parameters_version": "P-X"})
    bad_horizon = _horizon().model_copy(update={"parameter": bad_parameter})
    with pytest.raises(ValueError):
        calculate_confirmed_demand_absorption(
            _excess("NO_EXCESS"),
            CollectionEnvelope(state="KNOWN", items=(), source_ref="ORDERS"),
            AllocationLedgerSnapshot(reference_date=EVAL, scope=SCOPE, article_id="A-1", state="KNOWN", source_ref="LEDGER"),
            _scope(bad_horizon),
        )


def test_i5_demand_rate_rejects_method_selection_mismatch():
    with pytest.raises(ValidationError):
        DemandRateResult(
            identity=_identity(),
            selection=_selection("HISTORICAL_CONSUMPTION"),
            method="AUTHORIZED_FORECAST",
            daily_demand=Decimal("1"),
            unit="unit",
            state="KNOWN",
            reference_date=EVAL,
            applicable_from=EVAL,
            applicable_to=EVAL,
            forecast_version=None,
        )


def test_i5_historical_rate_rejects_forecast_version():
    with pytest.raises(ValidationError):
        DemandRateResult(
            identity=_identity("F-1"),
            selection=_selection("HISTORICAL_CONSUMPTION"),
            method="HISTORICAL_CONSUMPTION",
            daily_demand=Decimal("1"),
            unit="unit",
            state="KNOWN",
            reference_date=EVAL,
            applicable_from=EVAL,
            applicable_to=EVAL,
            forecast_version="F-1",
        )


def test_i6_schedule_requires_same_selection_as_demand():
    historical = _selection("HISTORICAL_CONSUMPTION")
    forecast = _selection("AUTHORIZED_FORECAST")
    demand = DemandRateResult(
        identity=_identity(),
        selection=historical,
        method="HISTORICAL_CONSUMPTION",
        daily_demand=Decimal("1"),
        unit="unit",
        state="KNOWN",
        reference_date=EVAL,
        applicable_from=EVAL,
        applicable_to=EVAL + timedelta(days=3),
    )
    with pytest.raises(ValidationError):
        DemandProjectionSchedule(
            selection=forecast,
            demand=demand,
            state="KNOWN",
            schedule_from=EVAL + timedelta(days=1),
            schedule_to=EVAL + timedelta(days=3),
            transformation_ref="TRANS",
            reconciliation_ref="RECON",
            source_ref="SCHEDULE",
        )


def test_i7_excess_result_rejects_divergent_confirmed_composition():
    ref = _reference()
    divergent = (
        IncorporatedDemandQuantity(
            confirmed_demand_id="O-X",
            quantity=Decimal("1"),
            unit="unit",
            demand_segment_ids=("SEG-X",),
        ),
    )
    with pytest.raises(ValidationError):
        ExcessResult(
            identity=_identity(),
            stock_reference=ref,
            stock_maximum=Decimal("50"),
            excess_tolerance_quantity=Decimal("5"),
            excess_threshold=Decimal("55"),
            excess_quantity=Decimal("25"),
            state="EXCESS",
            incorporated_confirmed_demand=divergent,
        )


def test_i8_known_ledger_rejects_entry_from_other_scope():
    wrong_entry = AllocationLedgerEntry(
        allocation_entry_id="AL-1",
        confirmed_demand_id="O-1",
        scope=OTHER_SCOPE,
        article_id="A-1",
        allocated_quantity=Decimal("1"),
        unit="unit",
        decision_id="D-1",
        scenario_id="S-1",
        excess_reference_date=EVAL,
        allocation_result_ref="RES-1",
    )
    with pytest.raises(ValidationError):
        AllocationLedgerSnapshot(
            reference_date=EVAL,
            scope=SCOPE,
            article_id="A-1",
            state="KNOWN",
            entries=(wrong_entry,),
            source_ref="LEDGER",
        )


def test_projection_result_can_represent_not_applicable_dependency_without_fake_values():
    result = StockProjectionResult(
        identity=_identity(),
        horizon=_horizon(),
        minimum_projected_stock=ProjectedDecimalMetric(state="NOT_APPLICABLE"),
        depletion_date=ProjectedDateMetric(state="NOT_APPLICABLE"),
        state="NOT_APPLICABLE",
    )
    assert result.state == "NOT_APPLICABLE"
