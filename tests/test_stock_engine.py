from datetime import date, timedelta
from decimal import Decimal

import pytest
from pydantic import ValidationError

from eios.core.models import DecisionContext
from eios.stock import (
    AllocationLedgerSnapshot,
    AllocationScope,
    AuthorizedForecastRate,
    AuthorizedQuantityThreshold,
    CollectionEnvelope,
    ConfiguredParameterValue,
    ConfirmedDemandRecord,
    ConsumptionPeriod,
    DataIssueRef,
    DemandAllocation,
    DemandMethodSelection,
    DemandProjectionSchedule,
    DemandRateResult,
    ExcessToleranceBasis,
    HistoricalDemandPolicy,
    NormalizedQuantity,
    ProjectionMovement,
    RequiredPeriodSpec,
    StockAvailabilityInput,
    StockComputationContext,
    StockCommitmentComponent,
    StockMaximumBasis,
    StockProjectionInput,
    StockScope,
    build_current_stock_reference,
    build_projected_stock_reference,
    build_projection_horizon,
    calculate_confirmed_demand_absorption,
    calculate_coverage,
    calculate_excess,
    calculate_historical_demand,
    calculate_stock_availability,
    calculate_stock_projection,
    use_authorized_forecast,
)


EVAL = date(2026, 9, 1)
SCOPE = StockScope(company_id="COMP-1", operational_scope_id="WH-1")


def dc(**overrides):
    data = dict(
        decision_id="D-1",
        scenario_id="S-1",
        rules_version="R-1",
        parameters_version="P-1",
        data_snapshot_id="SNAP-1",
    )
    data.update(overrides)
    return DecisionContext(**data)


def selection(method="HISTORICAL_CONSUMPTION", state="KNOWN"):
    if state == "KNOWN":
        return DemandMethodSelection(
            method=method,
            state="KNOWN",
            policy_ref="POL-DEMAND",
            policy_version="1",
            applicable_reference_date=EVAL,
            source_ref="SRC-POL",
        )
    return DemandMethodSelection(
        state=state,
        applicable_reference_date=EVAL,
        issue_refs=(DataIssueRef(issue_id="MISS-SEL", issue_type="MISSING_DATA", issue_record_ref="ISSUE-SEL"),),
    )


def context(method="HISTORICAL_CONSUMPTION", forecast_version=None):
    return StockComputationContext(
        decision_context=dc(),
        scope=SCOPE,
        article_id="A-1",
        evaluation_date=EVAL,
        base_unit="unit",
        methodology_version="STK-0.17",
        demand_selection=selection(method),
        forecast_version=forecast_version,
    )


def q(value, *, state="KNOWN", effective=EVAL, source="Q-SRC"):
    return NormalizedQuantity(
        scope=SCOPE,
        article_id="A-1",
        value=Decimal(value) if value is not None else None,
        unit="unit",
        source_unit="unit" if state == "KNOWN" else None,
        state=state,
        source_ref=source if state == "KNOWN" else None,
        effective_date=effective,
    )


def empty_components(state="KNOWN"):
    return CollectionEnvelope[StockCommitmentComponent](state=state, items=(), source_ref="COMMIT-SRC" if state == "KNOWN" else None)


def availability(ctx=None, on="100", committed="20", components=None):
    ctx = ctx or context()
    if components is None:
        components = (
            StockCommitmentComponent(
                commitment_id="C-ORDER",
                confirmed_demand_id="O-1",
                demand_segment_id="SEG-OPEN",
                scope=SCOPE,
                article_id="A-1",
                quantity=Decimal("10"),
                unit="unit",
                source_unit="unit",
                effective_date=EVAL,
                source_ref="COM-1",
            ),
            StockCommitmentComponent(
                commitment_id="C-OTHER",
                scope=SCOPE,
                article_id="A-1",
                quantity=Decimal("10"),
                unit="unit",
                source_unit="unit",
                effective_date=EVAL,
                source_ref="COM-2",
            ),
        )
    envelope = CollectionEnvelope[StockCommitmentComponent](state="KNOWN", items=components, source_ref="COMMIT-SRC")
    return calculate_stock_availability(
        StockAvailabilityInput(
            context=ctx,
            stock_on_hand=q(on),
            stock_committed=q(committed),
            committed_components=envelope,
        )
    )


def pye001(days=3, *, state="KNOWN"):
    return ConfiguredParameterValue(
        parameter_id="PYE-001",
        company_id="COMP-1",
        value=days if state == "KNOWN" else None,
        unit="days",
        state=state,
        parameters_version="P-1",
        applicable_reference_date=EVAL,
        configuration_ref="CFG-PYE-001" if state == "KNOWN" else None,
        source_ref="PARAM-SRC" if state == "KNOWN" else None,
    )


def stk006(months=2):
    return ConfiguredParameterValue(
        parameter_id="STK-006",
        company_id="COMP-1",
        value=months,
        unit="months",
        state="KNOWN",
        parameters_version="P-1",
        applicable_reference_date=EVAL,
        configuration_ref="CFG-STK-006",
        source_ref="PARAM-SRC",
    )


def forecast_context():
    return context("AUTHORIZED_FORECAST", forecast_version="F-1")


def forecast_demand(ctx=None, end=None):
    ctx = ctx or forecast_context()
    end = end or EVAL + timedelta(days=3)
    forecast = AuthorizedForecastRate(
        scope=SCOPE,
        article_id="A-1",
        daily_demand=Decimal("4"),
        unit="unit",
        state="KNOWN",
        forecast_version="F-1",
        reference_date=EVAL,
        applicable_from=EVAL,
        applicable_to=end,
        horizon_ref="FC-H",
        source_ref="FC-SRC",
    )
    return use_authorized_forecast(ctx, forecast)


def schedule(ctx, horizon, demand, movements):
    ids = tuple(m.movement_id for m in movements if m.source_kind in {"AUTHORIZED_DEMAND", "CONFIRMED_DEMAND"})
    return DemandProjectionSchedule(
        selection=ctx.demand_selection,
        demand=demand,
        state="KNOWN",
        schedule_from=EVAL + timedelta(days=1),
        schedule_to=horizon.horizon_end,
        demand_movement_ids=ids,
        transformation_ref="TRANS-1",
        reconciliation_ref="RECON-1",
        source_ref="SCH-SRC",
    )


def movement(mid, day, quantity, kind="AUTHORIZED_DEMAND", **overrides):
    data = dict(
        movement_id=mid,
        scope=SCOPE,
        article_id="A-1",
        direction="OUTFLOW" if kind not in {"PENDING_ORDER", "IN_TRANSIT", "PROPOSED_PURCHASE"} else "INFLOW",
        quantity=Decimal(quantity) if quantity is not None else None,
        unit="unit" if quantity is not None else None,
        source_unit="unit" if quantity is not None else None,
        effective_date=day,
        state="KNOWN" if quantity is not None else "UNKNOWN",
        source_kind=kind,
        source_ref="MOV-SRC" if quantity is not None else None,
        trace_refs=("TRANS-1",) if kind == "AUTHORIZED_DEMAND" and quantity is not None else (),
    )
    data.update(overrides)
    return ProjectionMovement(**data)


def projection_payload(movements=(), ctx=None):
    ctx = ctx or forecast_context()
    opening = availability(ctx)
    horizon = build_projection_horizon(ctx, pye001())
    demand = forecast_demand(ctx, horizon.horizon_end)
    sch = schedule(ctx, horizon, demand, movements)
    return StockProjectionInput(
        context=ctx,
        opening=opening,
        movements=CollectionEnvelope[ProjectionMovement](state="KNOWN", items=tuple(movements), source_ref="MOV-COL"),
        horizon=horizon,
        demand_schedule=sch,
        scenario_id="S-1",
    )


def threshold(purpose, value, ref_date=EVAL):
    return AuthorizedQuantityThreshold(
        scope=SCOPE,
        article_id="A-1",
        purpose=purpose,
        value=Decimal(value),
        unit="unit",
        state="KNOWN",
        applicable_reference_date=ref_date,
        authority_ref="AUTH-STK",
        authority_version="1",
        source_ref="TH-SRC",
    )


def test_unknown_quantity_is_representable_without_fake_value():
    item = q(None, state="UNKNOWN", effective=None)
    assert item.value is None
    assert item.state == "UNKNOWN"


def test_known_quantity_without_value_is_rejected():
    with pytest.raises(ValidationError):
        NormalizedQuantity(
            scope=SCOPE,
            article_id="A-1",
            unit="unit",
            source_unit="unit",
            state="KNOWN",
            source_ref="SRC",
            effective_date=EVAL,
        )


def test_conflicting_state_requires_contradiction_reference():
    with pytest.raises(ValidationError):
        NormalizedQuantity(scope=SCOPE, article_id="A-1", unit="unit", state="CONFLICTING_DATA")


def test_availability_preserves_deficit_and_confirmed_composition():
    result = availability(on="15", committed="20")
    assert result.stock_available == Decimal("0")
    assert result.availability_deficit == Decimal("5")
    assert result.incorporated_confirmed_demand[0].confirmed_demand_id == "O-1"
    assert result.incorporated_confirmed_demand[0].quantity == Decimal("10")


def test_committed_components_must_sum_exactly():
    with pytest.raises(ValueError):
        availability(committed="21")


def test_missing_committed_is_not_zero():
    ctx = context()
    result = calculate_stock_availability(
        StockAvailabilityInput(
            context=ctx,
            stock_on_hand=q("100"),
            stock_committed=q(None, state="NOT_EVIDENCED"),
            committed_components=CollectionEnvelope[StockCommitmentComponent](state="NOT_EVIDENCED"),
        )
    )
    assert result.state == "NOT_EVIDENCED"
    assert result.stock_available is None


def test_horizon_uses_effective_pye001_without_default():
    result = build_projection_horizon(context(), pye001(3))
    assert result.horizon_days == 3
    assert result.horizon_end == EVAL + timedelta(days=3)


def test_horizon_rejects_bool_as_days():
    with pytest.raises(ValueError):
        build_projection_horizon(context(), pye001(True))


def test_historical_demand_requires_exact_complete_window():
    ctx = context()
    policy = HistoricalDemandPolicy(
        parameter=stk006(2),
        required_periods=(
            RequiredPeriodSpec(period_id="2026-07", period_start=date(2026, 7, 1), period_end=date(2026, 7, 31)),
            RequiredPeriodSpec(period_id="2026-08", period_start=date(2026, 8, 1), period_end=date(2026, 8, 31)),
        ),
        period_calendar_ref="CAL-1",
        source_ref="POL-HIST",
        state="KNOWN",
    )
    periods = (
        ConsumptionPeriod(
            scope=SCOPE,
            article_id="A-1",
            period_id="2026-07",
            period_start=date(2026, 7, 1),
            period_end=date(2026, 7, 31),
            evidenced_days=31,
            quantity=Decimal("31"),
            unit="unit",
            state="KNOWN",
            methodology_version="STK-0.17",
            aggregation_ref="AGG-JUL",
            source_ref="CONS-JUL",
        ),
        ConsumptionPeriod(
            scope=SCOPE,
            article_id="A-1",
            period_id="2026-08",
            period_start=date(2026, 8, 1),
            period_end=date(2026, 8, 31),
            evidenced_days=31,
            quantity=Decimal("62"),
            unit="unit",
            state="KNOWN",
            methodology_version="STK-0.17",
            aggregation_ref="AGG-AUG",
            source_ref="CONS-AUG",
        ),
    )
    result = calculate_historical_demand(
        ctx,
        policy,
        CollectionEnvelope[ConsumptionPeriod](state="KNOWN", items=periods, source_ref="CONS-COL"),
    )
    assert result.daily_demand == Decimal("1.5")


def test_historical_window_does_not_shrink_silently():
    ctx = context()
    policy = HistoricalDemandPolicy(
        parameter=stk006(2),
        required_periods=(
            RequiredPeriodSpec(period_id="P1", period_start=date(2026, 7, 1), period_end=date(2026, 7, 31)),
            RequiredPeriodSpec(period_id="P2", period_start=date(2026, 8, 1), period_end=date(2026, 8, 31)),
        ),
        period_calendar_ref="CAL",
        source_ref="POL",
        state="KNOWN",
    )
    p1 = ConsumptionPeriod(
        scope=SCOPE,
        article_id="A-1",
        period_id="P1",
        period_start=date(2026, 7, 1),
        period_end=date(2026, 7, 31),
        evidenced_days=31,
        quantity=Decimal("31"),
        unit="unit",
        state="KNOWN",
        methodology_version="STK-0.17",
        aggregation_ref="AGG",
        source_ref="SRC",
    )
    with pytest.raises(ValueError):
        calculate_historical_demand(
            ctx,
            policy,
            CollectionEnvelope[ConsumptionPeriod](state="KNOWN", items=(p1,), source_ref="COL"),
        )


def test_authorized_forecast_requires_matching_version():
    ctx = forecast_context()
    bad = AuthorizedForecastRate(
        scope=SCOPE,
        article_id="A-1",
        daily_demand=Decimal("1"),
        unit="unit",
        state="KNOWN",
        forecast_version="F-X",
        reference_date=EVAL,
        applicable_from=EVAL,
        applicable_to=EVAL + timedelta(days=3),
        horizon_ref="H",
        source_ref="F",
    )
    with pytest.raises(ValueError):
        use_authorized_forecast(ctx, bad)


def test_coverage_finite_and_zero_demand_unbounded():
    ctx = forecast_context()
    available = availability(ctx, on="100", committed="20")
    demand = forecast_demand(ctx)
    finite = calculate_coverage(available, demand)
    assert finite.coverage_days == Decimal("20")

    zero_forecast = AuthorizedForecastRate(
        scope=SCOPE,
        article_id="A-1",
        daily_demand=Decimal("0"),
        unit="unit",
        state="KNOWN",
        forecast_version="F-1",
        reference_date=EVAL,
        applicable_from=EVAL,
        applicable_to=EVAL + timedelta(days=3),
        horizon_ref="H",
        source_ref="F",
    )
    zero = calculate_coverage(available, use_authorized_forecast(ctx, zero_forecast))
    assert zero.state == "UNBOUNDED"
    assert zero.coverage_days is None


def test_projection_schedule_must_cover_authorized_and_confirmed_demand_exactly():
    ctx = forecast_context()
    confirmed = movement(
        "M-C",
        EVAL + timedelta(days=1),
        "3",
        kind="CONFIRMED_DEMAND",
        confirmed_demand_id="O-2",
        demand_segment_id="SEG-2",
        trace_refs=("RECON-1",),
    )
    generic = movement("M-A", EVAL + timedelta(days=2), "4")
    payload = projection_payload((confirmed, generic), ctx)
    result = calculate_stock_projection(payload)
    assert result.state == "KNOWN"
    assert result.points[0].projected_stock == Decimal("77")
    assert result.points[1].projected_stock == Decimal("73")
    assert result.points[0].incorporated_confirmed_demand[-1].confirmed_demand_id == "O-2"


def test_projection_rejects_schedule_missing_confirmed_demand_id():
    ctx = forecast_context()
    confirmed = movement(
        "M-C",
        EVAL + timedelta(days=1),
        "3",
        kind="CONFIRMED_DEMAND",
        confirmed_demand_id="O-2",
        demand_segment_id="SEG-2",
        trace_refs=("RECON-1",),
    )
    payload = projection_payload((confirmed,), ctx)
    bad_schedule = payload.demand_schedule.model_copy(update={"demand_movement_ids": ()})
    bad = payload.model_copy(update={"demand_schedule": bad_schedule})
    with pytest.raises(ValueError):
        calculate_stock_projection(bad)


def test_unknown_movement_inside_horizon_contaminates_from_its_date():
    ctx = forecast_context()
    unknown = movement("M-U", EVAL + timedelta(days=2), None, kind="OTHER_AUTHORIZED_NEED")
    payload = projection_payload((unknown,), ctx)
    result = calculate_stock_projection(payload)
    assert result.points[0].state == "KNOWN"
    assert result.points[1].state == "UNKNOWN"
    assert result.points[2].state == "UNKNOWN"
    assert result.minimum_projected_stock.state == "UNKNOWN"


def test_unknown_movement_outside_horizon_does_not_contaminate():
    ctx = forecast_context()
    unknown = movement("M-U", EVAL + timedelta(days=10), None, kind="OTHER_AUTHORIZED_NEED")
    result = calculate_stock_projection(projection_payload((unknown,), ctx))
    assert result.state == "KNOWN"


def test_pending_and_transit_same_supply_identity_are_rejected():
    ctx = forecast_context()
    pending = movement(
        "M-P",
        EVAL + timedelta(days=1),
        "5",
        kind="PENDING_ORDER",
        supply_identity="SUPPLY-1",
        supplier_id="SUP-1",
        supply_document_ref="PO-1",
    )
    transit = movement(
        "M-T",
        EVAL + timedelta(days=2),
        "5",
        kind="IN_TRANSIT",
        supply_identity="SUPPLY-1",
        supplier_id="SUP-1",
        supply_document_ref="PO-1",
    )
    with pytest.raises(ValueError):
        calculate_stock_projection(projection_payload((pending, transit), ctx))


def test_opening_confirmed_segment_cannot_be_counted_again_in_m05():
    ctx = forecast_context()
    duplicate = movement(
        "M-C",
        EVAL + timedelta(days=1),
        "3",
        kind="CONFIRMED_DEMAND",
        confirmed_demand_id="O-1",
        demand_segment_id="SEG-OPEN",
        trace_refs=("RECON-1",),
    )
    with pytest.raises(ValueError):
        calculate_stock_projection(projection_payload((duplicate,), ctx))


def test_projection_preserves_negative_stock_and_known_depletion():
    ctx = forecast_context()
    outflow = movement("M-A", EVAL + timedelta(days=1), "100")
    result = calculate_stock_projection(projection_payload((outflow,), ctx))
    assert result.points[0].projected_stock == Decimal("-20")
    assert result.depletion_date.value == EVAL + timedelta(days=1)
    assert result.minimum_projected_stock.value == Decimal("-20")


def test_excess_direct_quantity_is_calculated_without_defaults():
    ref = build_current_stock_reference(availability(on="100", committed="20"))
    result = calculate_excess(
        ref,
        StockMaximumBasis(mode="DIRECT_QUANTITY", direct_threshold=threshold("STOCK_MAXIMUM", "50")),
        ExcessToleranceBasis(mode="QUANTITY", quantity_threshold=threshold("EXCESS_TOLERANCE", "5")),
    )
    assert result.state == "EXCESS"
    assert result.excess_quantity == Decimal("25")


def test_excess_rate_never_interprets_10_as_ten_percent_without_normalization():
    ref = build_current_stock_reference(availability(on="100", committed="20"))
    rate = ConfiguredParameterValue(
        parameter_id="STK-005",
        company_id="COMP-1",
        value=Decimal("10"),
        unit="%",
        state="KNOWN",
        parameters_version="P-1",
        applicable_reference_date=EVAL,
        configuration_ref="CFG",
        source_ref="SRC",
    )
    with pytest.raises(ValueError):
        calculate_excess(
            ref,
            StockMaximumBasis(mode="DIRECT_QUANTITY", direct_threshold=threshold("STOCK_MAXIMUM", "50")),
            ExcessToleranceBasis(mode="RATE", rate_parameter=rate),
        )


def make_excess(value="25"):
    ref = build_current_stock_reference(availability(on="100", committed="20"))
    maximum = Decimal("80") - Decimal(value) - Decimal("5")
    return calculate_excess(
        ref,
        StockMaximumBasis(mode="DIRECT_QUANTITY", direct_threshold=threshold("STOCK_MAXIMUM", str(maximum))),
        ExcessToleranceBasis(mode="QUANTITY", quantity_threshold=threshold("EXCESS_TOLERANCE", "5")),
    )


def allocation_scope(excess):
    ctx = context()
    return AllocationScope(
        identity=excess.identity,
        scope=SCOPE,
        article_id="A-1",
        evaluation_date=EVAL,
        excess_reference_date=excess.stock_reference.reference_date,
        horizon=build_projection_horizon(ctx, pye001(3)),
    )


def confirmed_order(pending="30", order_id="O-1"):
    return ConfirmedDemandRecord(
        confirmed_demand_id=order_id,
        order_id="SO-1",
        customer_id="CUST-1",
        scope=SCOPE,
        article_id="A-1",
        pending_quantity=q(pending),
        order_date=EVAL - timedelta(days=2),
        confirmation_date=EVAL - timedelta(days=1),
        expected_delivery_date=EVAL + timedelta(days=2),
        business_status="CONFIRMED",
        applicability_state="APLICABLE_Y_VALIDADA",
        applicability_source_ref="APP-1",
        source_ref="ORDER-SRC",
    )


def empty_ledger(state="KNOWN"):
    if state == "KNOWN":
        return AllocationLedgerSnapshot(
            reference_date=EVAL,
            scope=SCOPE,
            article_id="A-1",
            state="KNOWN",
            entries=(),
            source_ref="LEDGER-SRC",
        )
    issue = DataIssueRef(issue_id="MISS-LEDGER", issue_type="MISSING_DATA", issue_record_ref="ISSUE-LEDGER")
    return AllocationLedgerSnapshot(
        reference_date=EVAL,
        scope=SCOPE,
        article_id="A-1",
        state="NOT_EVIDENCED",
        issue_refs=(issue,),
    )


def test_m08_no_excess_does_not_require_known_ledger():
    ref = build_current_stock_reference(availability(on="30", committed="20"))
    no_excess = calculate_excess(
        ref,
        StockMaximumBasis(mode="DIRECT_QUANTITY", direct_threshold=threshold("STOCK_MAXIMUM", "20")),
        ExcessToleranceBasis(mode="QUANTITY", quantity_threshold=threshold("EXCESS_TOLERANCE", "0")),
    )
    assert no_excess.state == "NO_EXCESS"
    result = calculate_confirmed_demand_absorption(
        no_excess,
        CollectionEnvelope[ConfirmedDemandRecord](state="NOT_EVIDENCED"),
        empty_ledger("NOT_EVIDENCED"),
        allocation_scope(no_excess),
    )
    assert result.business_state == "NO_APLICABLE"
    assert result.absorbed_excess == Decimal("0")


def test_m08_excess_with_unknown_ledger_is_not_verifiable():
    excess = make_excess("25")
    orders = CollectionEnvelope[ConfirmedDemandRecord](state="KNOWN", items=(confirmed_order(),), source_ref="ORD-COL")
    result = calculate_confirmed_demand_absorption(
        excess,
        orders,
        empty_ledger("NOT_EVIDENCED"),
        allocation_scope(excess),
    )
    assert result.business_state == "NO_VERIFICABLE"
    assert result.absorbed_excess is None


def test_m08_reconciles_opening_quantity_and_preserves_ledger():
    excess = make_excess("25")
    orders = CollectionEnvelope[ConfirmedDemandRecord](state="KNOWN", items=(confirmed_order("30", "O-1"),), source_ref="ORD-COL")
    ledger = empty_ledger()
    plan = (
        DemandAllocation(
            allocation_entry_id="ALLOC-1",
            confirmed_demand_id="O-1",
            quantity_to_apply=Decimal("20"),
            unit="unit",
            allocation_source_ref="ALLOC-RESULT-1",
        ),
    )
    result = calculate_confirmed_demand_absorption(excess, orders, ledger, allocation_scope(excess), plan)
    # Opening already incorporated 10 units of O-1, so only 20 of pending 30 remain.
    assert result.total_remaining_applicable == Decimal("20")
    assert result.absorbed_excess == Decimal("20")
    assert result.residual_excess == Decimal("5")
    assert result.resulting_ledger is not None
    assert result.resulting_ledger.entries[-1].allocation_entry_id == "ALLOC-1"


def test_m08_rejects_plan_above_remaining_for_order():
    excess = make_excess("25")
    orders = CollectionEnvelope[ConfirmedDemandRecord](state="KNOWN", items=(confirmed_order("30", "O-1"),), source_ref="ORD-COL")
    plan = (
        DemandAllocation(
            allocation_entry_id="ALLOC-1",
            confirmed_demand_id="O-1",
            quantity_to_apply=Decimal("25"),
            unit="unit",
            allocation_source_ref="ALLOC-RESULT-1",
        ),
    )
    with pytest.raises(ValueError):
        calculate_confirmed_demand_absorption(excess, orders, empty_ledger(), allocation_scope(excess), plan)


def test_c0_context_is_not_mutated_by_stock_calculation():
    ctx = context()
    before = ctx.decision_context.model_dump()
    availability(ctx)
    assert ctx.decision_context.model_dump() == before
