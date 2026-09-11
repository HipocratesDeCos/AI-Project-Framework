"""Pure deterministic calculations for EIOS Stock & Demand v0.1."""
from __future__ import annotations

from collections import OrderedDict, defaultdict
from datetime import timedelta
from decimal import Decimal
from typing import Iterable, Sequence

from .models import (
    AllocationLedgerEntry,
    AllocationLedgerSnapshot,
    AllocationScope,
    AuthorizedForecastRate,
    CollectionEnvelope,
    ConfiguredParameterValue,
    ConfirmedDemandAbsorptionResult,
    ConfirmedDemandRecord,
    ConsumptionPeriod,
    CoverageResult,
    DataIssueRef,
    DemandAllocation,
    DemandRateResult,
    ExcessResult,
    ExcessToleranceBasis,
    HistoricalDemandPolicy,
    IncorporatedDemandQuantity,
    NormalizedQuantity,
    ProjectedDateMetric,
    ProjectedDecimalMetric,
    ProjectionHorizon,
    ProjectionMovement,
    ProjectionPoint,
    StockAvailabilityInput,
    StockAvailabilityResult,
    StockComputationContext,
    StockMaximumBasis,
    StockProjectionInput,
    StockProjectionResult,
    StockReferenceValue,
    StockResultIdentity,
)


_UNCERTAINTY_ORDER = {"UNKNOWN": 1, "NOT_EVIDENCED": 2, "CONFLICTING_DATA": 3}


def _decimal(value: Decimal | int | bool | None, field: str) -> Decimal:
    if value is None or isinstance(value, bool):
        raise ValueError(f"{field} requiere número no booleano")
    result = value if isinstance(value, Decimal) else Decimal(value)
    if not result.is_finite():
        raise ValueError(f"{field} debe ser finito")
    return result


def _unique(values: Iterable[str]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(values))


def _merge_traces(*groups: Iterable[str]) -> tuple[str, ...]:
    return _unique(item for group in groups for item in group)


def _merge_issues(*groups: Iterable[DataIssueRef]) -> tuple[DataIssueRef, ...]:
    seen: set[str] = set()
    result: list[DataIssueRef] = []
    for group in groups:
        for issue in group:
            if issue.issue_id not in seen:
                seen.add(issue.issue_id)
                result.append(issue)
    return tuple(result)


def _uncertainty_state(states: Iterable[str]) -> str:
    """Return the most specific M09/M10 uncertainty, ignoring KNOWN/NA.

    NOT_APPLICABLE is intentionally handled by each operation because some
    result contracts expose it while others do not.
    """
    uncertain = [state for state in states if state in _UNCERTAINTY_ORDER]
    if not uncertain:
        return "KNOWN"
    return max(uncertain, key=lambda state: _UNCERTAINTY_ORDER[state])


def _required_stock_state(states: Iterable[str]) -> str:
    """State for a required StockDataState dependency set."""
    material = tuple(states)
    uncertain = _uncertainty_state(material)
    if uncertain != "KNOWN":
        return uncertain
    if "NOT_APPLICABLE" in material:
        return "NOT_APPLICABLE"
    return "KNOWN"


def build_identity(context: StockComputationContext) -> StockResultIdentity:
    dc = context.decision_context
    return StockResultIdentity(
        decision_id=dc.decision_id,
        scenario_id=dc.scenario_id,
        rules_version=dc.rules_version,
        parameters_version=dc.parameters_version,
        data_snapshot_id=dc.data_snapshot_id,
        company_id=context.scope.company_id,
        operational_scope_id=context.scope.operational_scope_id,
        article_id=context.article_id,
        evaluation_date=context.evaluation_date,
        base_unit=context.base_unit,
        methodology_version=context.methodology_version,
        forecast_version=context.forecast_version,
    )


def _assert_quantity_context(quantity: NormalizedQuantity, context: StockComputationContext) -> None:
    if quantity.scope != context.scope or quantity.article_id != context.article_id or quantity.unit != context.base_unit:
        raise ValueError("Cantidad incompatible con scope/article/base_unit del contexto")


def _aggregate_confirmed_components(components: Sequence) -> tuple[IncorporatedDemandQuantity, ...]:
    grouped: OrderedDict[str, dict[str, object]] = OrderedDict()
    for component in components:
        if component.confirmed_demand_id is None:
            continue
        assert component.demand_segment_id is not None
        record = grouped.setdefault(
            component.confirmed_demand_id,
            {"quantity": Decimal("0"), "unit": component.unit, "segments": [], "traces": []},
        )
        if record["unit"] != component.unit:
            raise ValueError("Un pedido confirmado no puede mezclar unidades")
        segments = record["segments"]
        assert isinstance(segments, list)
        if component.demand_segment_id in segments:
            raise ValueError("demand_segment_id duplicado en opening")
        segments.append(component.demand_segment_id)
        record["quantity"] = record["quantity"] + component.quantity  # type: ignore[operator]
        traces = record["traces"]
        assert isinstance(traces, list)
        traces.extend(component.trace_refs)
    return tuple(
        IncorporatedDemandQuantity(
            confirmed_demand_id=confirmed_id,
            quantity=data["quantity"],  # type: ignore[arg-type]
            unit=data["unit"],  # type: ignore[arg-type]
            demand_segment_ids=tuple(data["segments"]),  # type: ignore[arg-type]
            trace_refs=_unique(data["traces"]),  # type: ignore[arg-type]
        )
        for confirmed_id, data in grouped.items()
    )


def calculate_stock_availability(payload: StockAvailabilityInput) -> StockAvailabilityResult:
    context = payload.context
    identity = build_identity(context)
    on_hand = payload.stock_on_hand
    committed = payload.stock_committed
    _assert_quantity_context(on_hand, context)
    _assert_quantity_context(committed, context)

    if on_hand.state == "NOT_APPLICABLE" or committed.state == "NOT_APPLICABLE":
        raise ValueError("Stock físico/comprometido no admite NOT_APPLICABLE para disponibilidad")
    if on_hand.effective_date not in {None, context.evaluation_date} and on_hand.state != "KNOWN":
        raise ValueError("Stock on hand refiere a otra fecha")
    if committed.effective_date not in {None, context.evaluation_date} and committed.state != "KNOWN":
        raise ValueError("Stock committed refiere a otra fecha")

    components = payload.committed_components.items
    issues = _merge_issues(on_hand.issue_refs, committed.issue_refs, payload.committed_components.issue_refs)
    traces = _merge_traces(on_hand.trace_refs, committed.trace_refs, payload.committed_components.trace_refs)
    state = _uncertainty_state((on_hand.state, committed.state, payload.committed_components.state))
    if state != "KNOWN":
        return StockAvailabilityResult(
            identity=identity,
            unit=context.base_unit,
            state=state,  # type: ignore[arg-type]
            committed_components=tuple(components),
            issue_refs=issues,
            trace_refs=traces,
        )

    if on_hand.effective_date != context.evaluation_date or committed.effective_date != context.evaluation_date:
        raise ValueError("Stock KNOWN debe pertenecer exactamente a evaluation_date")
    assert on_hand.value is not None and committed.value is not None

    commitments: set[str] = set()
    segments: set[str] = set()
    total = Decimal("0")
    for component in components:
        if component.scope != context.scope or component.article_id != context.article_id:
            raise ValueError("Componente committed incompatible con scope/article")
        if component.unit != context.base_unit or component.effective_date != context.evaluation_date:
            raise ValueError("Componente committed incompatible con unidad/fecha")
        if component.commitment_id in commitments:
            raise ValueError("commitment_id duplicado")
        commitments.add(component.commitment_id)
        if component.demand_segment_id:
            if component.demand_segment_id in segments:
                raise ValueError("demand_segment_id duplicado")
            segments.add(component.demand_segment_id)
        total += component.quantity
    if total != committed.value:
        raise ValueError("La composición committed debe sumar exactamente stock_committed")

    available = max(Decimal("0"), on_hand.value - committed.value)
    deficit = max(Decimal("0"), committed.value - on_hand.value)
    return StockAvailabilityResult(
        identity=identity,
        stock_available=available,
        availability_deficit=deficit,
        unit=context.base_unit,
        state="KNOWN",
        committed_components=tuple(components),
        incorporated_confirmed_demand=_aggregate_confirmed_components(components),
        issue_refs=issues,
        trace_refs=traces,
    )


def _assert_parameter_context(parameter: ConfiguredParameterValue, context: StockComputationContext) -> None:
    if parameter.company_id != context.scope.company_id:
        raise ValueError("Parámetro de otra compañía")
    if parameter.parameters_version != context.decision_context.parameters_version:
        raise ValueError("parameters_version incompatible")
    if parameter.applicable_reference_date != context.evaluation_date:
        raise ValueError("Parámetro no aplicable a evaluation_date")


def build_projection_horizon(context: StockComputationContext, parameter: ConfiguredParameterValue) -> ProjectionHorizon:
    _assert_parameter_context(parameter, context)
    if parameter.state == "NOT_APPLICABLE":
        return ProjectionHorizon(
            parameter=parameter,
            state="NOT_APPLICABLE",
            issue_refs=parameter.issue_refs,
            trace_refs=parameter.trace_refs,
        )
    if parameter.state != "KNOWN":
        state = _uncertainty_state((parameter.state,))
        if state == "KNOWN":
            state = "UNKNOWN"
        return ProjectionHorizon(
            parameter=parameter,
            state=state,  # type: ignore[arg-type]
            issue_refs=parameter.issue_refs,
            trace_refs=parameter.trace_refs,
        )
    if parameter.parameter_id != "PYE-001":
        raise ValueError("ProjectionHorizon requiere PYE-001")
    if isinstance(parameter.value, bool) or not isinstance(parameter.value, int) or parameter.value <= 0:
        raise ValueError("PYE-001 requiere entero positivo no booleano")
    if parameter.unit not in {"days", "day", "días", "dias", "día", "dia"} and not parameter.normalization_ref:
        raise ValueError("PYE-001 debe estar normalizado a días")
    return ProjectionHorizon(
        parameter=parameter,
        horizon_days=parameter.value,
        horizon_end=context.evaluation_date + timedelta(days=parameter.value),
        state="KNOWN",
        issue_refs=parameter.issue_refs,
        trace_refs=parameter.trace_refs,
    )


def _demand_nondetermined_result(
    context: StockComputationContext,
    states: Iterable[str],
    issues: Iterable[DataIssueRef],
    traces: Iterable[str],
    source_ref: str | None = None,
) -> DemandRateResult:
    state = _required_stock_state(states)
    if state == "KNOWN":
        state = "UNKNOWN"
    return DemandRateResult(
        identity=build_identity(context),
        selection=context.demand_selection,
        unit=context.base_unit,
        state=state,  # type: ignore[arg-type]
        source_ref=source_ref,
        issue_refs=tuple(issues),
        trace_refs=tuple(traces),
    )


def calculate_historical_demand(
    context: StockComputationContext,
    policy: HistoricalDemandPolicy,
    periods: CollectionEnvelope[ConsumptionPeriod],
) -> DemandRateResult:
    identity = build_identity(context)
    selection = context.demand_selection
    if selection.state != "KNOWN":
        return _demand_nondetermined_result(
            context, (selection.state,), selection.issue_refs, selection.trace_refs, selection.source_ref
        )
    if selection.method != "HISTORICAL_CONSUMPTION" or context.forecast_version is not None:
        raise ValueError("Contexto no autorizado para demanda histórica")
    _assert_parameter_context(policy.parameter, context)
    if policy.state == "NOT_APPLICABLE" or policy.parameter.state == "NOT_APPLICABLE":
        raise ValueError("Una selección histórica KNOWN no puede consumir política/parámetro NOT_APPLICABLE")

    issues = _merge_issues(selection.issue_refs, policy.issue_refs, policy.parameter.issue_refs, periods.issue_refs)
    traces = _merge_traces(selection.trace_refs, policy.trace_refs, policy.parameter.trace_refs, periods.trace_refs)
    preliminary = _uncertainty_state((policy.state, policy.parameter.state, periods.state))
    if preliminary != "KNOWN":
        return DemandRateResult(
            identity=identity,
            selection=selection,
            unit=context.base_unit,
            state=preliminary,  # type: ignore[arg-type]
            issue_refs=issues,
            trace_refs=traces,
        )

    parameter = policy.parameter
    if parameter.parameter_id != "STK-006":
        raise ValueError("HistoricalDemandPolicy requiere STK-006")
    if isinstance(parameter.value, bool) or not isinstance(parameter.value, int) or parameter.value <= 0:
        raise ValueError("STK-006 requiere entero positivo no booleano")
    if parameter.unit not in {"months", "month", "meses", "mes"} and not parameter.normalization_ref:
        raise ValueError("STK-006 debe expresar periodos mensuales")
    if len(policy.required_periods) != parameter.value:
        raise ValueError("Número de periodos no coincide con STK-006")
    if policy.extended_applicable_to and policy.extended_applicable_to < context.evaluation_date:
        raise ValueError("extended_applicable_to no puede preceder evaluation_date")

    expected = {spec.period_id: spec for spec in policy.required_periods}
    if len(periods.items) != len(expected):
        raise ValueError("La ventana histórica debe coincidir exactamente con periodos requeridos")
    total_quantity = Decimal("0")
    total_days = 0
    child_states: list[str] = []
    child_issues: list[DataIssueRef] = []
    child_traces: list[str] = []
    for period in periods.items:
        spec = expected.get(period.period_id)
        if spec is None or period.period_start != spec.period_start or period.period_end != spec.period_end:
            raise ValueError("Periodo histórico no coincide con RequiredPeriodSpec")
        if period.scope != context.scope or period.article_id != context.article_id or period.unit != context.base_unit:
            raise ValueError("Periodo histórico incompatible con contexto")
        if period.methodology_version != context.methodology_version:
            raise ValueError("methodology_version histórica incompatible")
        if period.state == "NOT_APPLICABLE":
            raise ValueError("Un periodo requerido no puede ser NOT_APPLICABLE sin invalidar la política seleccionada")
        child_states.append(period.state)
        child_issues.extend(period.issue_refs)
        child_traces.extend(period.trace_refs)
        if period.state == "KNOWN":
            assert period.quantity is not None and period.evidenced_days is not None
            total_quantity += period.quantity
            total_days += period.evidenced_days
    state = _uncertainty_state(child_states)
    if state != "KNOWN":
        return DemandRateResult(
            identity=identity,
            selection=selection,
            unit=context.base_unit,
            state=state,  # type: ignore[arg-type]
            issue_refs=_merge_issues(issues, child_issues),
            trace_refs=_merge_traces(traces, child_traces),
        )
    if total_days <= 0:
        raise ValueError("La ventana histórica debe contener días evidenciados")

    applicable_to = policy.extended_applicable_to or context.evaluation_date
    return DemandRateResult(
        identity=identity,
        selection=selection,
        method="HISTORICAL_CONSUMPTION",
        daily_demand=total_quantity / Decimal(total_days),
        unit=context.base_unit,
        state="KNOWN",
        reference_date=context.evaluation_date,
        applicable_from=context.evaluation_date,
        applicable_to=applicable_to,
        applicability_source_ref=policy.applicability_source_ref or policy.source_ref,
        window_or_horizon=f"STK-006:{parameter.value}",
        source_ref=policy.source_ref,
        forecast_version=None,
        issue_refs=_merge_issues(issues, child_issues),
        trace_refs=_merge_traces(traces, child_traces),
    )


def use_authorized_forecast(context: StockComputationContext, forecast: AuthorizedForecastRate) -> DemandRateResult:
    identity = build_identity(context)
    selection = context.demand_selection
    issues = _merge_issues(selection.issue_refs, forecast.issue_refs)
    traces = _merge_traces(selection.trace_refs, forecast.trace_refs)
    if selection.state != "KNOWN":
        return _demand_nondetermined_result(context, (selection.state,), issues, traces, forecast.source_ref)
    if selection.method != "AUTHORIZED_FORECAST" or not context.forecast_version:
        raise ValueError("Contexto no autorizado para forecast")
    if forecast.scope != context.scope or forecast.article_id != context.article_id or forecast.unit != context.base_unit:
        raise ValueError("Forecast incompatible con contexto")
    if forecast.state == "NOT_APPLICABLE":
        raise ValueError("Una selección forecast KNOWN no puede consumir forecast NOT_APPLICABLE")
    if forecast.state != "KNOWN":
        return _demand_nondetermined_result(context, (forecast.state,), issues, traces, forecast.source_ref)
    if forecast.forecast_version != context.forecast_version:
        raise ValueError("forecast_version incompatible")
    assert forecast.daily_demand is not None and forecast.reference_date is not None
    assert forecast.applicable_from is not None and forecast.applicable_to is not None
    if not (forecast.applicable_from <= context.evaluation_date <= forecast.applicable_to):
        raise ValueError("Forecast no aplicable a evaluation_date")
    return DemandRateResult(
        identity=identity,
        selection=selection,
        method="AUTHORIZED_FORECAST",
        daily_demand=forecast.daily_demand,
        unit=context.base_unit,
        state="KNOWN",
        reference_date=forecast.reference_date,
        applicable_from=forecast.applicable_from,
        applicable_to=forecast.applicable_to,
        applicability_source_ref=forecast.horizon_ref,
        window_or_horizon=forecast.horizon_ref,
        source_ref=forecast.source_ref,
        forecast_version=forecast.forecast_version,
        issue_refs=issues,
        trace_refs=traces,
    )


def calculate_coverage(availability: StockAvailabilityResult, demand: DemandRateResult) -> CoverageResult:
    if availability.identity != demand.identity:
        raise ValueError("Availability y demand pertenecen a identidades distintas")
    if demand.state == "NOT_APPLICABLE":
        raise ValueError("Coverage requiere una demanda aplicable al método seleccionado")
    issues = _merge_issues(availability.issue_refs, demand.issue_refs)
    traces = _merge_traces(availability.trace_refs, demand.trace_refs)
    state = _uncertainty_state((availability.state, demand.state))
    if state != "KNOWN":
        return CoverageResult(
            identity=availability.identity,
            state=state,  # type: ignore[arg-type]
            demand=demand,
            issue_refs=issues,
            trace_refs=traces,
        )
    assert availability.stock_available is not None and demand.daily_demand is not None
    assert demand.applicable_from is not None and demand.applicable_to is not None
    reference = availability.identity.evaluation_date
    if not (demand.applicable_from <= reference <= demand.applicable_to):
        raise ValueError("Demanda no aplicable a evaluation_date")
    if demand.daily_demand == 0:
        return CoverageResult(
            identity=availability.identity,
            state="UNBOUNDED",
            demand=demand,
            issue_refs=issues,
            trace_refs=traces,
        )
    return CoverageResult(
        identity=availability.identity,
        coverage_days=availability.stock_available / demand.daily_demand,
        state="FINITE",
        demand=demand,
        issue_refs=issues,
        trace_refs=traces,
    )


def _validate_horizon(payload: StockProjectionInput) -> None:
    horizon = payload.horizon
    context = payload.context
    parameter = horizon.parameter
    if parameter.company_id != context.scope.company_id:
        raise ValueError("Horizon de otra compañía")
    if parameter.parameters_version != context.decision_context.parameters_version:
        raise ValueError("Horizon con parameters_version incompatible")
    if parameter.applicable_reference_date != context.evaluation_date:
        raise ValueError("Horizon no aplicable a evaluation_date")
    if horizon.state == "KNOWN":
        if parameter.parameter_id != "PYE-001" or parameter.state != "KNOWN":
            raise ValueError("Horizon KNOWN requiere PYE-001 KNOWN")
        assert horizon.horizon_days is not None and horizon.horizon_end is not None
        if isinstance(parameter.value, bool) or parameter.value != horizon.horizon_days:
            raise ValueError("horizon_days no coincide con PYE-001")
        if horizon.horizon_end != context.evaluation_date + timedelta(days=horizon.horizon_days):
            raise ValueError("horizon_end no coincide con PYE-001")


def _validate_schedule(payload: StockProjectionInput) -> None:
    schedule = payload.demand_schedule
    context = payload.context
    horizon = payload.horizon
    if schedule.selection != context.demand_selection:
        raise ValueError("Schedule usa otra selección de demanda")
    if schedule.demand.identity != build_identity(context):
        raise ValueError("Schedule usa demanda de otra identidad")
    if payload.movements.state == "KNOWN":
        expected_ids = tuple(
            movement.movement_id
            for movement in payload.movements.items
            if movement.source_kind in {"AUTHORIZED_DEMAND", "CONFIRMED_DEMAND"}
        )
        if len(expected_ids) != len(set(expected_ids)):
            raise ValueError("Movimientos de demanda contienen IDs duplicados")
        if set(schedule.demand_movement_ids) != set(expected_ids) or len(schedule.demand_movement_ids) != len(expected_ids):
            raise ValueError("Schedule IDs debe coincidir exactamente con demanda presente")
    if schedule.state == "KNOWN":
        if horizon.state != "KNOWN":
            raise ValueError("Schedule KNOWN requiere horizon KNOWN")
        assert horizon.horizon_end is not None
        if schedule.schedule_from != context.evaluation_date + timedelta(days=1):
            raise ValueError("schedule_from inválido")
        if schedule.schedule_to != horizon.horizon_end:
            raise ValueError("schedule_to inválido")
        demand = schedule.demand
        if demand.applicable_from is None or demand.applicable_to is None:
            raise ValueError("Demanda de schedule sin aplicabilidad")
        if demand.applicable_from > schedule.schedule_from or demand.applicable_to < schedule.schedule_to:
            raise ValueError("Demanda no cubre todo el horizonte del schedule")
        for movement in payload.movements.items:
            if movement.source_kind == "AUTHORIZED_DEMAND" and schedule.transformation_ref not in movement.trace_refs:
                raise ValueError("AUTHORIZED_DEMAND debe trazar transformation_ref")


def _validate_movements(payload: StockProjectionInput) -> None:
    context = payload.context
    horizon = payload.horizon
    if payload.movements.state != "KNOWN" or horizon.state != "KNOWN":
        return
    assert horizon.horizon_end is not None
    seen_ids: set[str] = set()
    seen_segments = {
        segment
        for item in payload.opening.incorporated_confirmed_demand
        for segment in item.demand_segment_ids
    }
    opening_commitments = {component.commitment_id for component in payload.opening.committed_components}
    seen_supply: set[str] = set()
    for movement in payload.movements.items:
        if movement.movement_id in seen_ids:
            raise ValueError("movement_id duplicado")
        seen_ids.add(movement.movement_id)
        if movement.scope != context.scope or movement.article_id != context.article_id:
            raise ValueError("Movimiento de otro scope/article")
        if movement.unit is not None and movement.unit != context.base_unit:
            raise ValueError("Movimiento con unidad incompatible")
        if movement.state != "KNOWN" or movement.effective_date is None:
            continue
        if not (context.evaluation_date < movement.effective_date <= horizon.horizon_end):
            continue
        if movement.source_kind == "CONFIRMED_DEMAND":
            assert movement.demand_segment_id is not None
            if movement.demand_segment_id in seen_segments:
                raise ValueError("Segmento de demanda duplicado opening/M05")
            seen_segments.add(movement.demand_segment_id)
        if movement.source_kind in {"RESERVATION", "OTHER_AUTHORIZED_NEED"} and movement.commitment_id:
            if movement.commitment_id in opening_commitments:
                continue
        if movement.source_kind in {"PENDING_ORDER", "IN_TRANSIT"}:
            assert movement.supply_identity is not None
            if movement.supply_identity in seen_supply:
                raise ValueError("supply_identity duplicada o pending/transit simultáneo")
            seen_supply.add(movement.supply_identity)


def _composition_to_mutable(items: Sequence[IncorporatedDemandQuantity]) -> OrderedDict[str, dict[str, object]]:
    result: OrderedDict[str, dict[str, object]] = OrderedDict()
    for item in items:
        result[item.confirmed_demand_id] = {
            "quantity": item.quantity,
            "unit": item.unit,
            "segments": list(item.demand_segment_ids),
            "traces": list(item.trace_refs),
        }
    return result


def _composition_snapshot(data: OrderedDict[str, dict[str, object]]) -> tuple[IncorporatedDemandQuantity, ...]:
    return tuple(
        IncorporatedDemandQuantity(
            confirmed_demand_id=confirmed_id,
            quantity=values["quantity"],  # type: ignore[arg-type]
            unit=values["unit"],  # type: ignore[arg-type]
            demand_segment_ids=tuple(values["segments"]),  # type: ignore[arg-type]
            trace_refs=_unique(values["traces"]),  # type: ignore[arg-type]
        )
        for confirmed_id, values in data.items()
    )


def _add_confirmed_movement(composition: OrderedDict[str, dict[str, object]], movement: ProjectionMovement) -> None:
    assert movement.confirmed_demand_id is not None and movement.demand_segment_id is not None
    assert movement.quantity is not None and movement.unit is not None
    record = composition.setdefault(
        movement.confirmed_demand_id,
        {"quantity": Decimal("0"), "unit": movement.unit, "segments": [], "traces": []},
    )
    if record["unit"] != movement.unit:
        raise ValueError("Pedido confirmado mezcla unidades")
    segments = record["segments"]
    assert isinstance(segments, list)
    if movement.demand_segment_id in segments:
        raise ValueError("demand_segment_id duplicado")
    segments.append(movement.demand_segment_id)
    record["quantity"] = record["quantity"] + movement.quantity  # type: ignore[operator]
    traces = record["traces"]
    assert isinstance(traces, list)
    traces.extend(movement.trace_refs)


def calculate_stock_projection(payload: StockProjectionInput) -> StockProjectionResult:
    context = payload.context
    identity = build_identity(context)
    if payload.scenario_id != context.decision_context.scenario_id:
        raise ValueError("scenario_id de proyección incompatible")
    if payload.opening.identity != identity:
        raise ValueError("Opening pertenece a otra identidad")
    _validate_horizon(payload)
    _validate_schedule(payload)
    _validate_movements(payload)

    issues = _merge_issues(
        payload.opening.issue_refs,
        payload.horizon.issue_refs,
        payload.movements.issue_refs,
        payload.demand_schedule.issue_refs,
    )
    traces = _merge_traces(
        payload.opening.trace_refs,
        payload.horizon.trace_refs,
        payload.movements.trace_refs,
        payload.demand_schedule.trace_refs,
    )
    primary_state = _required_stock_state(
        (payload.opening.state, payload.horizon.state, payload.movements.state, payload.demand_schedule.state)
    )
    if primary_state != "KNOWN" or payload.opening.stock_available is None or payload.horizon.horizon_end is None:
        state = primary_state if primary_state != "KNOWN" else "UNKNOWN"
        return StockProjectionResult(
            identity=identity,
            horizon=payload.horizon,
            minimum_projected_stock=ProjectedDecimalMetric(
                state=state, issue_refs=issues, trace_refs=traces  # type: ignore[arg-type]
            ),
            depletion_date=ProjectedDateMetric(
                state=state, issue_refs=issues, trace_refs=traces  # type: ignore[arg-type]
            ),
            state=state,  # type: ignore[arg-type]
            issue_refs=issues,
            trace_refs=traces,
        )

    evaluation_date = context.evaluation_date
    horizon_end = payload.horizon.horizon_end
    known_by_date: dict = defaultdict(list)
    uncertainty_starts: list[tuple] = []
    opening_ids = {component.commitment_id for component in payload.opening.committed_components}
    for movement in payload.movements.items:
        if movement.effective_date is not None and not (evaluation_date < movement.effective_date <= horizon_end):
            continue
        if movement.state == "NOT_APPLICABLE":
            continue
        if movement.state == "KNOWN":
            assert movement.effective_date is not None
            if movement.source_kind in {"RESERVATION", "OTHER_AUTHORIZED_NEED"} and movement.commitment_id in opening_ids:
                continue
            known_by_date[movement.effective_date].append(movement)
        else:
            uncertainty_starts.append(
                (movement.effective_date or evaluation_date, movement.state, movement.issue_refs, movement.trace_refs)
            )

    current = payload.opening.stock_available
    composition = _composition_to_mutable(payload.opening.incorporated_confirmed_demand)
    points: list[ProjectionPoint] = []
    running_uncertainty: list[tuple] = []
    day = evaluation_date + timedelta(days=1)
    while day <= horizon_end:
        for uncertainty in uncertainty_starts:
            if uncertainty[0] == day or (uncertainty[0] <= evaluation_date and day == evaluation_date + timedelta(days=1)):
                running_uncertainty.append(uncertainty)
        movements_today = sorted(known_by_date.get(day, ()), key=lambda movement: movement.movement_id)
        if not running_uncertainty:
            for movement in movements_today:
                assert movement.quantity is not None
                current = current + movement.quantity if movement.direction == "INFLOW" else current - movement.quantity
                if movement.source_kind == "CONFIRMED_DEMAND":
                    _add_confirmed_movement(composition, movement)
            points.append(
                ProjectionPoint(
                    reference_date=day,
                    projected_stock=current,
                    state="KNOWN",
                    incorporated_confirmed_demand=_composition_snapshot(composition),
                    trace_refs=_merge_traces(traces, *(movement.trace_refs for movement in movements_today)),
                )
            )
        else:
            for movement in movements_today:
                if movement.source_kind == "CONFIRMED_DEMAND":
                    _add_confirmed_movement(composition, movement)
            state = _uncertainty_state(item[1] for item in running_uncertainty)
            points.append(
                ProjectionPoint(
                    reference_date=day,
                    state=state,  # type: ignore[arg-type]
                    incorporated_confirmed_demand=_composition_snapshot(composition),
                    issue_refs=_merge_issues(*(item[2] for item in running_uncertainty)),
                    trace_refs=_merge_traces(traces, *(item[3] for item in running_uncertainty)),
                )
            )
        day += timedelta(days=1)

    all_known = all(point.state == "KNOWN" for point in points)
    if all_known:
        values = [payload.opening.stock_available] + [point.projected_stock for point in points]
        minimum = ProjectedDecimalMetric(
            value=min(value for value in values if value is not None),
            state="KNOWN",
            trace_refs=traces,
        )
    else:
        uncertain = [point for point in points if point.state != "KNOWN"]
        state = _uncertainty_state(point.state for point in uncertain)
        minimum = ProjectedDecimalMetric(
            state=state,  # type: ignore[arg-type]
            issue_refs=_merge_issues(*(point.issue_refs for point in uncertain)),
            trace_refs=_merge_traces(traces, *(point.trace_refs for point in uncertain)),
        )

    if payload.opening.stock_available == 0:
        depletion = ProjectedDateMetric(value=evaluation_date, state="KNOWN", trace_refs=traces)
    else:
        depletion: ProjectedDateMetric | None = None
        first_uncertain: ProjectionPoint | None = None
        for point in points:
            if point.state != "KNOWN":
                first_uncertain = point
                break
            assert point.projected_stock is not None
            if point.projected_stock <= 0:
                depletion = ProjectedDateMetric(value=point.reference_date, state="KNOWN", trace_refs=point.trace_refs)
                break
        if depletion is None and first_uncertain is not None:
            depletion = ProjectedDateMetric(
                state=first_uncertain.state,
                issue_refs=first_uncertain.issue_refs,
                trace_refs=first_uncertain.trace_refs,
            )
        elif depletion is None:
            depletion = ProjectedDateMetric(state="NOT_APPLICABLE", trace_refs=traces)

    result_state = "KNOWN" if all_known else _uncertainty_state(point.state for point in points if point.state != "KNOWN")
    last_composition = points[-1].incorporated_confirmed_demand if points else payload.opening.incorporated_confirmed_demand
    return StockProjectionResult(
        identity=identity,
        horizon=payload.horizon,
        points=tuple(points),
        minimum_projected_stock=minimum,
        depletion_date=depletion,
        incorporated_confirmed_demand_at_horizon=last_composition,
        state=result_state,  # type: ignore[arg-type]
        issue_refs=_merge_issues(issues, *(point.issue_refs for point in points)),
        trace_refs=_merge_traces(traces, *(point.trace_refs for point in points)),
    )


def build_current_stock_reference(availability: StockAvailabilityResult) -> StockReferenceValue:
    return StockReferenceValue(
        identity=availability.identity,
        reference_kind="CURRENT_AVAILABLE",
        reference_date=availability.identity.evaluation_date,
        value=availability.stock_available if availability.state == "KNOWN" else None,
        unit=availability.unit,
        state=availability.state,
        incorporated_confirmed_demand=availability.incorporated_confirmed_demand,
        source_ref=f"stock-availability:{availability.identity.decision_id}:{availability.identity.scenario_id}",
        issue_refs=availability.issue_refs,
        trace_refs=availability.trace_refs,
    )


def build_projected_stock_reference(projection: StockProjectionResult, reference_date) -> StockReferenceValue:
    point = next((item for item in projection.points if item.reference_date == reference_date), None)
    if point is None:
        raise ValueError("reference_date no existe en la proyección")
    return StockReferenceValue(
        identity=projection.identity,
        reference_kind="PROJECTED",
        reference_date=reference_date,
        value=point.projected_stock if point.state == "KNOWN" else None,
        unit=projection.identity.base_unit,
        state=point.state,
        incorporated_confirmed_demand=point.incorporated_confirmed_demand,
        source_ref=f"stock-projection:{projection.identity.decision_id}:{projection.identity.scenario_id}:{reference_date.isoformat()}",
        issue_refs=point.issue_refs,
        trace_refs=point.trace_refs,
    )


def _parameter_at_reference(parameter: ConfiguredParameterValue, reference: StockReferenceValue, expected_id: str) -> Decimal:
    if parameter.parameter_id != expected_id or parameter.state != "KNOWN":
        raise ValueError(f"Se requiere {expected_id} KNOWN")
    if parameter.company_id != reference.identity.company_id:
        raise ValueError("Parámetro de otra compañía")
    if parameter.parameters_version != reference.identity.parameters_version:
        raise ValueError("Versión de parámetro incompatible")
    if parameter.applicable_reference_date != reference.reference_date:
        raise ValueError("Parámetro no vigente en reference_date")
    value = _decimal(parameter.value, expected_id)
    if value < 0:
        raise ValueError(f"{expected_id} no puede ser negativo")
    return value


def calculate_excess(
    stock_reference: StockReferenceValue,
    maximum_basis: StockMaximumBasis,
    tolerance_basis: ExcessToleranceBasis,
) -> ExcessResult:
    identity = stock_reference.identity
    issues = stock_reference.issue_refs
    traces = stock_reference.trace_refs
    states: list[str] = [stock_reference.state]
    maximum: Decimal | None = None

    if maximum_basis.mode == "DIRECT_QUANTITY":
        threshold = maximum_basis.direct_threshold
        assert threshold is not None
        if threshold.scope.company_id != identity.company_id or threshold.scope.operational_scope_id != identity.operational_scope_id:
            raise ValueError("Threshold maximum de otro scope")
        if threshold.article_id != identity.article_id or threshold.unit != identity.base_unit:
            raise ValueError("Threshold maximum incompatible")
        if threshold.applicable_reference_date != stock_reference.reference_date:
            raise ValueError("Threshold maximum no vigente")
        states.append(threshold.state)
        issues = _merge_issues(issues, threshold.issue_refs)
        traces = _merge_traces(traces, threshold.trace_refs)
        if threshold.state == "KNOWN":
            if threshold.purpose != "STOCK_MAXIMUM":
                raise ValueError("Threshold purpose incorrecto")
            maximum = threshold.value
    else:
        parameter = maximum_basis.coverage_parameter
        demand = maximum_basis.demand
        assert parameter is not None and demand is not None
        states.extend((parameter.state, demand.state))
        issues = _merge_issues(issues, parameter.issue_refs, demand.issue_refs)
        traces = _merge_traces(traces, parameter.trace_refs, demand.trace_refs)
        if parameter.state == "KNOWN" and demand.state == "KNOWN":
            days = _parameter_at_reference(parameter, stock_reference, "STK-004")
            if parameter.unit not in {"days", "day", "días", "dias", "día", "dia"} and not parameter.normalization_ref:
                raise ValueError("STK-004 debe estar normalizado a días")
            if demand.identity != identity:
                raise ValueError("Demanda maximum de otra identidad")
            if demand.daily_demand is None or demand.daily_demand <= 0:
                raise ValueError("COVERAGE_MAXIMUM requiere demanda >0")
            if demand.applicable_from is None or demand.applicable_to is None or not (
                demand.applicable_from <= stock_reference.reference_date <= demand.applicable_to
            ):
                raise ValueError("Demanda no aplicable a reference_date")
            maximum = days * demand.daily_demand

    tolerance: Decimal | None = None
    if tolerance_basis.mode == "QUANTITY":
        threshold = tolerance_basis.quantity_threshold
        assert threshold is not None
        if threshold.scope.company_id != identity.company_id or threshold.scope.operational_scope_id != identity.operational_scope_id:
            raise ValueError("Threshold tolerance de otro scope")
        if threshold.article_id != identity.article_id or threshold.unit != identity.base_unit:
            raise ValueError("Threshold tolerance incompatible")
        if threshold.applicable_reference_date != stock_reference.reference_date:
            raise ValueError("Threshold tolerance no vigente")
        states.append(threshold.state)
        issues = _merge_issues(issues, threshold.issue_refs)
        traces = _merge_traces(traces, threshold.trace_refs)
        if threshold.state == "KNOWN":
            if threshold.purpose != "EXCESS_TOLERANCE":
                raise ValueError("Threshold purpose incorrecto")
            tolerance = threshold.value
    else:
        parameter = tolerance_basis.rate_parameter
        assert parameter is not None
        states.append(parameter.state)
        issues = _merge_issues(issues, parameter.issue_refs)
        traces = _merge_traces(traces, parameter.trace_refs)
        if parameter.state == "KNOWN":
            rate = _parameter_at_reference(parameter, stock_reference, "STK-005")
            if not parameter.normalization_ref:
                raise ValueError("STK-005 RATE requiere normalización explícita a proporción")
            if maximum is not None:
                tolerance = maximum * rate

    result_state = _uncertainty_state(states)
    if result_state != "KNOWN" or stock_reference.value is None or maximum is None or tolerance is None:
        if result_state == "KNOWN":
            result_state = "UNKNOWN"
        return ExcessResult(
            identity=identity,
            stock_reference=stock_reference,
            state=result_state,  # type: ignore[arg-type]
            incorporated_confirmed_demand=stock_reference.incorporated_confirmed_demand,
            issue_refs=issues,
            trace_refs=traces,
        )

    threshold_value = maximum + tolerance
    excess = max(Decimal("0"), stock_reference.value - threshold_value)
    state = (
        "NO_EXCESS"
        if stock_reference.value <= maximum
        else "WITHIN_TOLERANCE"
        if stock_reference.value <= threshold_value
        else "EXCESS"
    )
    return ExcessResult(
        identity=identity,
        stock_reference=stock_reference,
        stock_maximum=maximum,
        excess_tolerance_quantity=tolerance,
        excess_threshold=threshold_value,
        excess_quantity=excess,
        state=state,
        incorporated_confirmed_demand=stock_reference.incorporated_confirmed_demand,
        issue_refs=issues,
        trace_refs=traces,
    )


def _validate_allocation_scope(excess: ExcessResult, scope: AllocationScope) -> None:
    if scope.identity != excess.identity:
        raise ValueError("AllocationScope de otra identidad")
    if scope.scope.company_id != excess.identity.company_id or scope.scope.operational_scope_id != excess.identity.operational_scope_id:
        raise ValueError("AllocationScope de otro scope")
    if scope.article_id != excess.identity.article_id or scope.evaluation_date != excess.identity.evaluation_date:
        raise ValueError("AllocationScope incompatible")
    if scope.excess_reference_date != excess.stock_reference.reference_date:
        raise ValueError("AllocationScope usa otra fecha de exceso")
    horizon = scope.horizon
    parameter = horizon.parameter
    if horizon.state != "KNOWN" or horizon.horizon_days is None or horizon.horizon_end is None:
        raise ValueError("AllocationScope requiere horizon KNOWN")
    if parameter.parameter_id != "PYE-001" or parameter.state != "KNOWN":
        raise ValueError("AllocationScope requiere PYE-001 KNOWN")
    if parameter.company_id != scope.identity.company_id or parameter.parameters_version != scope.identity.parameters_version:
        raise ValueError("PYE-001 incompatible con identidad")
    if parameter.applicable_reference_date != scope.evaluation_date:
        raise ValueError("PYE-001 no vigente en evaluation_date")
    if isinstance(parameter.value, bool) or parameter.value != horizon.horizon_days:
        raise ValueError("horizon_days no coincide con PYE-001")
    if horizon.horizon_end != scope.evaluation_date + timedelta(days=horizon.horizon_days):
        raise ValueError("horizon_end incompatible con PYE-001")


def _not_verifiable_absorption(
    excess: ExcessResult,
    issues: tuple[DataIssueRef, ...],
    traces: tuple[str, ...],
) -> ConfirmedDemandAbsorptionResult:
    return ConfirmedDemandAbsorptionResult(
        identity=excess.identity,
        excess_result=excess,
        business_state="NO_VERIFICABLE",
        issue_refs=issues,
        trace_refs=traces,
    )


def calculate_confirmed_demand_absorption(
    excess: ExcessResult,
    orders: CollectionEnvelope[ConfirmedDemandRecord],
    ledger: AllocationLedgerSnapshot,
    allocation_scope: AllocationScope,
    allocation_plan: Sequence[DemandAllocation] = (),
) -> ConfirmedDemandAbsorptionResult:
    _validate_allocation_scope(excess, allocation_scope)
    base_issues = _merge_issues(excess.issue_refs, orders.issue_refs, ledger.issue_refs)
    base_traces = _merge_traces(excess.trace_refs, orders.trace_refs, ledger.trace_refs, allocation_scope.trace_refs)

    if excess.state in {"UNKNOWN", "NOT_EVIDENCED", "CONFLICTING_DATA"}:
        return _not_verifiable_absorption(excess, base_issues, base_traces)
    assert excess.excess_quantity is not None

    if excess.state in {"NO_EXCESS", "WITHIN_TOLERANCE"}:
        if allocation_plan:
            raise ValueError("No puede existir allocation_plan sin EXCESS")
        return ConfirmedDemandAbsorptionResult(
            identity=excess.identity,
            excess_result=excess,
            business_state="NO_APLICABLE",
            total_remaining_applicable=Decimal("0"),
            absorbed_excess=Decimal("0"),
            residual_excess=excess.excess_quantity,
            allocation_plan=(),
            resulting_ledger=None,
            issue_refs=excess.issue_refs,
            trace_refs=excess.trace_refs,
        )

    if orders.state != "KNOWN":
        return _not_verifiable_absorption(excess, base_issues, base_traces)
    if not orders.items:
        if allocation_plan:
            raise ValueError("NO_EXISTE no admite allocation_plan")
        return ConfirmedDemandAbsorptionResult(
            identity=excess.identity,
            excess_result=excess,
            business_state="NO_EXISTE",
            total_remaining_applicable=Decimal("0"),
            absorbed_excess=Decimal("0"),
            residual_excess=excess.excess_quantity,
            allocation_plan=(),
            resulting_ledger=None,
            issue_refs=orders.issue_refs,
            trace_refs=base_traces,
        )

    horizon_end = allocation_scope.horizon.horizon_end
    assert horizon_end is not None
    order_ids = [order.confirmed_demand_id for order in orders.items]
    if len(order_ids) != len(set(order_ids)):
        raise ValueError("confirmed_demand_id duplicado en colección")

    potentially_applicable: list[ConfirmedDemandRecord] = []
    order_issue_groups: list[Iterable[DataIssueRef]] = [base_issues]
    for order in orders.items:
        if order.scope != allocation_scope.scope or order.article_id != allocation_scope.article_id:
            raise ValueError("Pedido de otro scope/article")
        order_issue_groups.append(order.issue_refs)
        if order.applicability_state == "NO_VERIFICABLE":
            return _not_verifiable_absorption(excess, _merge_issues(*order_issue_groups), base_traces)
        if order.applicability_state == "NO_APLICABLE":
            continue
        pq = order.pending_quantity
        if pq.scope != allocation_scope.scope or pq.article_id != allocation_scope.article_id:
            raise ValueError("Pending quantity incompatible")
        if pq.state != "KNOWN" or pq.value is None:
            return _not_verifiable_absorption(excess, _merge_issues(*order_issue_groups, pq.issue_refs), base_traces)
        if pq.effective_date != allocation_scope.evaluation_date:
            raise ValueError("Pending quantity no vigente en evaluation_date")
        if pq.unit != excess.stock_reference.unit:
            raise ValueError("Pending quantity con unidad incompatible")
        if order.order_date is None or order.confirmation_date is None or order.expected_delivery_date is None:
            raise ValueError("Pedido APLICABLE_Y_VALIDADA sin fechas obligatorias")
        if not (order.order_date <= order.confirmation_date <= allocation_scope.evaluation_date):
            raise ValueError("Fechas comerciales incompatibles")
        if not (allocation_scope.excess_reference_date < order.expected_delivery_date <= horizon_end):
            raise ValueError("Pedido APLICABLE_Y_VALIDADA fuera de la ventana M08")
        potentially_applicable.append(order)

    if not potentially_applicable:
        if allocation_plan:
            raise ValueError("NO_APLICABLE no admite allocation_plan")
        return ConfirmedDemandAbsorptionResult(
            identity=excess.identity,
            excess_result=excess,
            business_state="NO_APLICABLE",
            total_remaining_applicable=Decimal("0"),
            absorbed_excess=Decimal("0"),
            residual_excess=excess.excess_quantity,
            allocation_plan=(),
            resulting_ledger=None,
            issue_refs=_merge_issues(*order_issue_groups),
            trace_refs=base_traces,
        )

    if ledger.state != "KNOWN":
        return _not_verifiable_absorption(excess, base_issues, base_traces)
    if ledger.reference_date != allocation_scope.evaluation_date or ledger.scope != allocation_scope.scope or ledger.article_id != allocation_scope.article_id:
        raise ValueError("Ledger incompatible con AllocationScope")

    incorporated = {item.confirmed_demand_id: item.quantity for item in excess.incorporated_confirmed_demand}
    allocated: dict[str, Decimal] = defaultdict(lambda: Decimal("0"))
    for entry in ledger.entries:
        allocated[entry.confirmed_demand_id] += entry.allocated_quantity

    remaining: dict[str, Decimal] = {}
    applicable: dict[str, ConfirmedDemandRecord] = {}
    for order in potentially_applicable:
        pq = order.pending_quantity
        assert pq.value is not None
        prior = incorporated.get(order.confirmed_demand_id, Decimal("0")) + allocated[order.confirmed_demand_id]
        if prior > pq.value:
            raise ValueError("incorporated + allocated supera pending")
        value = pq.value - prior
        remaining[order.confirmed_demand_id] = value
        if value > 0:
            applicable[order.confirmed_demand_id] = order

    total = sum(remaining.values(), Decimal("0"))
    if total == 0:
        if allocation_plan:
            raise ValueError("No hay saldo asignable para allocation_plan")
        return ConfirmedDemandAbsorptionResult(
            identity=excess.identity,
            excess_result=excess,
            business_state="NO_APLICABLE",
            total_remaining_applicable=Decimal("0"),
            absorbed_excess=Decimal("0"),
            residual_excess=excess.excess_quantity,
            allocation_plan=(),
            resulting_ledger=ledger,
            issue_refs=base_issues,
            trace_refs=base_traces,
        )

    absorbed = min(excess.excess_quantity, total)
    residual = max(Decimal("0"), excess.excess_quantity - absorbed)
    if absorbed <= 0:
        raise ValueError("EXCESS aplicable debe producir absorción positiva")
    if not allocation_plan:
        return _not_verifiable_absorption(excess, base_issues, base_traces)

    plan_ids = [allocation.allocation_entry_id for allocation in allocation_plan]
    if len(plan_ids) != len(set(plan_ids)):
        raise ValueError("allocation_entry_id duplicado en plan")
    existing_ids = {entry.allocation_entry_id for entry in ledger.entries}
    if existing_ids.intersection(plan_ids):
        raise ValueError("allocation_entry_id colisiona con ledger")

    by_order: dict[str, Decimal] = defaultdict(lambda: Decimal("0"))
    for allocation in allocation_plan:
        if allocation.confirmed_demand_id not in applicable:
            raise ValueError("Plan contiene pedido no aplicable")
        if allocation.unit != excess.stock_reference.unit:
            raise ValueError("Plan con unidad incompatible")
        by_order[allocation.confirmed_demand_id] += allocation.quantity_to_apply
    for confirmed_id, quantity in by_order.items():
        if quantity > remaining[confirmed_id]:
            raise ValueError("Plan supera remaining_allocatable del pedido")
    if sum((allocation.quantity_to_apply for allocation in allocation_plan), Decimal("0")) != absorbed:
        raise ValueError("allocation_plan debe sumar exactamente absorbed_excess")

    new_entries = tuple(
        AllocationLedgerEntry(
            allocation_entry_id=allocation.allocation_entry_id,
            confirmed_demand_id=allocation.confirmed_demand_id,
            scope=allocation_scope.scope,
            article_id=allocation_scope.article_id,
            allocated_quantity=allocation.quantity_to_apply,
            unit=allocation.unit,
            decision_id=allocation_scope.identity.decision_id,
            scenario_id=allocation_scope.identity.scenario_id,
            excess_reference_date=allocation_scope.excess_reference_date,
            allocation_result_ref=allocation.allocation_source_ref,
            trace_refs=allocation.trace_refs,
        )
        for allocation in allocation_plan
    )
    resulting = AllocationLedgerSnapshot(
        reference_date=ledger.reference_date,
        scope=ledger.scope,
        article_id=ledger.article_id,
        state="KNOWN",
        entries=ledger.entries + new_entries,
        source_ref=ledger.source_ref,
        trace_refs=_merge_traces(ledger.trace_refs, *(allocation.trace_refs for allocation in allocation_plan)),
    )
    return ConfirmedDemandAbsorptionResult(
        identity=excess.identity,
        excess_result=excess,
        business_state="APLICABLE_Y_VALIDADA",
        total_remaining_applicable=total,
        absorbed_excess=absorbed,
        residual_excess=residual,
        allocation_plan=tuple(allocation_plan),
        resulting_ledger=resulting,
        issue_refs=base_issues,
        trace_refs=_merge_traces(base_traces, *(allocation.trace_refs for allocation in allocation_plan)),
    )


__all__ = [
    "build_current_stock_reference",
    "build_identity",
    "build_projected_stock_reference",
    "build_projection_horizon",
    "calculate_confirmed_demand_absorption",
    "calculate_coverage",
    "calculate_excess",
    "calculate_historical_demand",
    "calculate_stock_availability",
    "calculate_stock_projection",
    "use_authorized_forecast",
]
