"""Physical Stock & Demand contracts for EIOS STK v0.1.

Implements the closed STK Implementation Contract v0.17. This module owns
facts, inputs and deterministic analytical results only; Rules, CRC,
persistence and final purchase authority remain outside STK.
"""
from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal
from typing import Generic, Literal, TypeVar

from pydantic import BaseModel, ConfigDict, Field, model_validator

from eios.core.models import DecisionContext


StockDataState = Literal["KNOWN", "UNKNOWN", "NOT_EVIDENCED", "NOT_APPLICABLE", "CONFLICTING_DATA"]
CollectionState = Literal["KNOWN", "UNKNOWN", "NOT_EVIDENCED", "CONFLICTING_DATA"]
IssueType = Literal["MISSING_DATA", "CONTRADICTION"]
DemandMethod = Literal["HISTORICAL_CONSUMPTION", "AUTHORIZED_FORECAST"]
ThresholdPurpose = Literal["STOCK_MAXIMUM", "EXCESS_TOLERANCE"]
StockPolicyConcept = Literal["STOCK_MINIMUM", "SAFETY_STOCK"]
CoverageState = Literal["FINITE", "UNBOUNDED", "UNKNOWN", "NOT_EVIDENCED", "CONFLICTING_DATA"]
MovementDirection = Literal["INFLOW", "OUTFLOW"]
MovementSourceKind = Literal[
    "PENDING_ORDER",
    "IN_TRANSIT",
    "AUTHORIZED_DEMAND",
    "CONFIRMED_DEMAND",
    "RESERVATION",
    "OTHER_AUTHORIZED_NEED",
    "PROPOSED_PURCHASE",
]
StockReferenceKind = Literal["CURRENT_AVAILABLE", "PROJECTED"]
MaximumMode = Literal["DIRECT_QUANTITY", "COVERAGE_MAXIMUM"]
ToleranceMode = Literal["QUANTITY", "RATE"]
ExcessState = Literal[
    "NO_EXCESS",
    "WITHIN_TOLERANCE",
    "EXCESS",
    "UNKNOWN",
    "NOT_EVIDENCED",
    "CONFLICTING_DATA",
]
DemandApplicabilityState = Literal["NO_APLICABLE", "APLICABLE_Y_VALIDADA", "NO_VERIFICABLE"]
AbsorptionBusinessState = Literal["NO_EXISTE", "NO_APLICABLE", "APLICABLE_Y_VALIDADA", "NO_VERIFICABLE"]


def _finite(value: Decimal, field: str) -> Decimal:
    if not value.is_finite():
        raise ValueError(f"{field} debe ser finito")
    return value


def _non_negative(value: Decimal, field: str) -> Decimal:
    _finite(value, field)
    if value < 0:
        raise ValueError(f"{field} no puede ser negativo")
    return value


def _has_evidence(source_ref: str | None, trace_refs: tuple[str, ...]) -> bool:
    return bool(source_ref or trace_refs)


class FrozenModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True, frozen=True)


class DataIssueRef(FrozenModel):
    issue_id: str = Field(min_length=1, max_length=128)
    issue_type: IssueType
    issue_record_ref: str = Field(min_length=1, max_length=256)
    evidence_refs: tuple[str, ...] = ()
    trace_refs: tuple[str, ...] = ()

    @model_validator(mode="after")
    def validate_issue(self) -> "DataIssueRef":
        if len(set(self.evidence_refs)) != len(self.evidence_refs):
            raise ValueError("evidence_refs no puede contener duplicados")
        if self.issue_type == "CONTRADICTION" and len(self.evidence_refs) < 2:
            raise ValueError("CONTRADICTION requiere al menos dos evidencias distintas")
        return self


class StockScope(FrozenModel):
    company_id: str = Field(min_length=1, max_length=128)
    operational_scope_id: str = Field(min_length=1, max_length=128)


class StatefulModel(FrozenModel):
    issue_refs: tuple[DataIssueRef, ...] = ()
    trace_refs: tuple[str, ...] = ()

    def validate_conflict_state(self, state: str) -> None:
        if state == "CONFLICTING_DATA" and not any(i.issue_type == "CONTRADICTION" for i in self.issue_refs):
            raise ValueError("CONFLICTING_DATA requiere DataIssueRef CONTRADICTION")


class DemandMethodSelection(StatefulModel):
    method: DemandMethod | None = None
    state: StockDataState
    policy_ref: str | None = Field(default=None, max_length=256)
    policy_version: str | None = Field(default=None, max_length=128)
    applicable_reference_date: date
    source_ref: str | None = Field(default=None, max_length=256)

    @model_validator(mode="after")
    def validate_payload(self) -> "DemandMethodSelection":
        self.validate_conflict_state(self.state)
        if self.state == "KNOWN":
            if self.method is None or not self.policy_ref or not self.policy_version:
                raise ValueError("DemandMethodSelection KNOWN requiere método, política y versión")
            if not _has_evidence(self.source_ref, self.trace_refs):
                raise ValueError("DemandMethodSelection KNOWN requiere fuente o traza")
        elif self.method is not None:
            raise ValueError("Una selección no KNOWN no puede publicar método determinado")
        return self


class StockComputationContext(FrozenModel):
    decision_context: DecisionContext
    scope: StockScope
    article_id: str = Field(min_length=1, max_length=128)
    evaluation_date: date
    base_unit: str = Field(min_length=1, max_length=64)
    methodology_version: str = Field(min_length=1, max_length=64)
    demand_selection: DemandMethodSelection
    forecast_version: str | None = Field(default=None, max_length=128)

    @model_validator(mode="after")
    def validate_context(self) -> "StockComputationContext":
        if self.demand_selection.applicable_reference_date != self.evaluation_date:
            raise ValueError("demand_selection debe aplicar a evaluation_date")
        if self.demand_selection.state == "KNOWN":
            if self.demand_selection.method == "HISTORICAL_CONSUMPTION" and self.forecast_version is not None:
                raise ValueError("Método histórico exige forecast_version nula")
            if self.demand_selection.method == "AUTHORIZED_FORECAST" and not self.forecast_version:
                raise ValueError("Forecast autorizado exige forecast_version")
        elif self.forecast_version is not None:
            raise ValueError("forecast_version no puede simular una selección de demanda no KNOWN")
        return self


class StockResultIdentity(FrozenModel):
    decision_id: str
    scenario_id: str
    rules_version: str
    parameters_version: str
    data_snapshot_id: str
    company_id: str
    operational_scope_id: str
    article_id: str
    evaluation_date: date
    base_unit: str
    methodology_version: str
    forecast_version: str | None = None


class NormalizedQuantity(StatefulModel):
    scope: StockScope
    article_id: str = Field(min_length=1, max_length=128)
    value: Decimal | None = None
    unit: str = Field(min_length=1, max_length=64)
    source_unit: str | None = Field(default=None, max_length=64)
    normalization_ref: str | None = Field(default=None, max_length=256)
    state: StockDataState
    source_ref: str | None = Field(default=None, max_length=256)
    effective_date: date | None = None

    @model_validator(mode="after")
    def validate_payload(self) -> "NormalizedQuantity":
        self.validate_conflict_state(self.state)
        if self.state == "KNOWN":
            if self.value is None:
                raise ValueError("NormalizedQuantity KNOWN requiere value")
            _non_negative(self.value, "value")
            if not self.source_unit:
                raise ValueError("NormalizedQuantity KNOWN requiere source_unit")
            if self.source_unit != self.unit and not self.normalization_ref:
                raise ValueError("Conversión de unidad requiere normalization_ref")
            if not _has_evidence(self.source_ref, self.trace_refs):
                raise ValueError("NormalizedQuantity KNOWN requiere fuente o traza")
        elif self.value is not None:
            raise ValueError("Cantidad no KNOWN no puede publicar value determinado")
        return self


class ConfiguredParameterValue(StatefulModel):
    parameter_id: str = Field(min_length=1, max_length=64)
    company_id: str = Field(min_length=1, max_length=128)
    value: Decimal | int | bool | None = None
    unit: str | None = Field(default=None, max_length=64)
    state: StockDataState
    parameters_version: str = Field(min_length=1, max_length=64)
    applicable_reference_date: date
    configuration_ref: str | None = Field(default=None, max_length=256)
    source_ref: str | None = Field(default=None, max_length=256)
    normalization_ref: str | None = Field(default=None, max_length=256)

    @model_validator(mode="after")
    def validate_payload(self) -> "ConfiguredParameterValue":
        self.validate_conflict_state(self.state)
        if self.parameter_id.startswith("P-STK-") or self.parameter_id.startswith("P-PYE-"):
            raise ValueError("Los alias documentales P-* no son IDs físicos")
        if self.state == "KNOWN":
            if self.value is None or not self.configuration_ref:
                raise ValueError("Parámetro KNOWN requiere value y configuration_ref")
            if isinstance(self.value, Decimal):
                _finite(self.value, "parameter.value")
            if not _has_evidence(self.source_ref, self.trace_refs):
                raise ValueError("Parámetro KNOWN requiere fuente o traza")
        elif self.value is not None:
            raise ValueError("Parámetro no KNOWN no puede publicar value determinado")
        return self


class AuthorizedQuantityThreshold(StatefulModel):
    scope: StockScope
    article_id: str
    purpose: ThresholdPurpose
    value: Decimal | None = None
    unit: str
    state: StockDataState
    applicable_reference_date: date
    authority_ref: str | None = None
    authority_version: str | None = None
    source_ref: str | None = None

    @model_validator(mode="after")
    def validate_payload(self) -> "AuthorizedQuantityThreshold":
        self.validate_conflict_state(self.state)
        if self.state == "KNOWN":
            if self.value is None:
                raise ValueError("Umbral KNOWN requiere value")
            _non_negative(self.value, "threshold.value")
            if not self.authority_ref or not self.authority_version:
                raise ValueError("Umbral KNOWN requiere authority_ref/version")
            if not _has_evidence(self.source_ref, self.trace_refs):
                raise ValueError("Umbral KNOWN requiere fuente o traza")
        elif self.value is not None:
            raise ValueError("Umbral no KNOWN no puede publicar value")
        return self


class AuthorizedStockPolicyQuantity(StatefulModel):
    concept: StockPolicyConcept
    scope: StockScope
    article_id: str
    quantity: Decimal | None = None
    unit: str
    state: StockDataState
    policy_ref: str | None = None
    policy_version: str | None = None
    derivation_ref: str | None = None
    valid_from: date | None = None
    valid_to: date | None = None
    source_ref: str | None = None

    @model_validator(mode="after")
    def validate_payload(self) -> "AuthorizedStockPolicyQuantity":
        self.validate_conflict_state(self.state)
        if self.valid_from and self.valid_to and self.valid_to < self.valid_from:
            raise ValueError("valid_to no puede ser anterior a valid_from")
        if self.state == "KNOWN":
            if self.quantity is None:
                raise ValueError("Política de stock KNOWN requiere quantity")
            _non_negative(self.quantity, "quantity")
            if not all((self.policy_ref, self.policy_version, self.derivation_ref, self.valid_from)):
                raise ValueError("Política KNOWN requiere política, versión, derivación y vigencia")
            if not _has_evidence(self.source_ref, self.trace_refs):
                raise ValueError("Política KNOWN requiere fuente o traza")
        elif self.quantity is not None:
            raise ValueError("Política no KNOWN no puede publicar quantity")
        return self


T = TypeVar("T")


class CollectionEnvelope(FrozenModel, Generic[T]):
    state: CollectionState
    items: tuple[T, ...] = ()
    source_ref: str | None = None
    issue_refs: tuple[DataIssueRef, ...] = ()
    trace_refs: tuple[str, ...] = ()

    @model_validator(mode="after")
    def validate_collection(self) -> "CollectionEnvelope[T]":
        if self.state == "KNOWN" and not _has_evidence(self.source_ref, self.trace_refs):
            raise ValueError("Colección KNOWN requiere fuente o traza")
        if self.state == "CONFLICTING_DATA" and not any(i.issue_type == "CONTRADICTION" for i in self.issue_refs):
            raise ValueError("Colección CONFLICTING_DATA requiere incidencia")
        return self


class ProjectionHorizon(StatefulModel):
    parameter: ConfiguredParameterValue
    horizon_days: int | None = None
    horizon_end: date | None = None
    state: StockDataState

    @model_validator(mode="after")
    def validate_payload(self) -> "ProjectionHorizon":
        self.validate_conflict_state(self.state)
        if self.state == "KNOWN":
            if self.parameter.parameter_id != "PYE-001" or self.parameter.state != "KNOWN":
                raise ValueError("Horizon KNOWN requiere PYE-001 KNOWN")
            if self.horizon_days is None or isinstance(self.horizon_days, bool) or self.horizon_days <= 0:
                raise ValueError("horizon_days debe ser entero positivo no booleano")
            if isinstance(self.parameter.value, bool) or not isinstance(self.parameter.value, int) or self.parameter.value <= 0:
                raise ValueError("PYE-001 KNOWN requiere entero positivo no booleano")
            if self.horizon_days != self.parameter.value:
                raise ValueError("horizon_days debe coincidir exactamente con PYE-001")
            expected_end = self.parameter.applicable_reference_date + timedelta(days=self.horizon_days)
            if self.horizon_end != expected_end:
                raise ValueError("horizon_end debe derivar exactamente de PYE-001 y su fecha aplicable")
        elif self.horizon_days is not None or self.horizon_end is not None:
            raise ValueError("Horizon no KNOWN no publica horizonte determinado")
        return self


class StockCommitmentComponent(FrozenModel):
    commitment_id: str
    demand_segment_id: str | None = None
    confirmed_demand_id: str | None = None
    scope: StockScope
    article_id: str
    quantity: Decimal
    unit: str
    source_unit: str | None = None
    normalization_ref: str | None = None
    effective_date: date
    source_ref: str
    trace_refs: tuple[str, ...] = ()

    @model_validator(mode="after")
    def validate_component(self) -> "StockCommitmentComponent":
        _non_negative(self.quantity, "commitment.quantity")
        if self.source_unit and self.source_unit != self.unit and not self.normalization_ref:
            raise ValueError("Conversión commitment requiere normalization_ref")
        if (self.confirmed_demand_id is None) != (self.demand_segment_id is None):
            raise ValueError("confirmed_demand_id y demand_segment_id deben coexistir")
        return self


class IncorporatedDemandQuantity(FrozenModel):
    confirmed_demand_id: str
    quantity: Decimal
    unit: str
    demand_segment_ids: tuple[str, ...]
    trace_refs: tuple[str, ...] = ()

    @model_validator(mode="after")
    def validate_item(self) -> "IncorporatedDemandQuantity":
        _non_negative(self.quantity, "incorporated.quantity")
        if not self.demand_segment_ids or len(set(self.demand_segment_ids)) != len(self.demand_segment_ids):
            raise ValueError("demand_segment_ids deben ser no vacíos y únicos")
        return self


class StockAvailabilityInput(FrozenModel):
    context: StockComputationContext
    stock_on_hand: NormalizedQuantity
    stock_committed: NormalizedQuantity
    committed_components: CollectionEnvelope[StockCommitmentComponent]


class StockAvailabilityResult(StatefulModel):
    identity: StockResultIdentity
    stock_available: Decimal | None = None
    availability_deficit: Decimal | None = None
    unit: str
    state: StockDataState
    committed_components: tuple[StockCommitmentComponent, ...] = ()
    incorporated_confirmed_demand: tuple[IncorporatedDemandQuantity, ...] = ()

    @model_validator(mode="after")
    def validate_result(self) -> "StockAvailabilityResult":
        self.validate_conflict_state(self.state)
        if self.state == "KNOWN":
            if self.stock_available is None or self.availability_deficit is None:
                raise ValueError("Availability KNOWN requiere available y deficit")
            _non_negative(self.stock_available, "stock_available")
            _non_negative(self.availability_deficit, "availability_deficit")
        elif self.stock_available is not None or self.availability_deficit is not None:
            raise ValueError("Availability no KNOWN no publica cantidades determinadas")
        return self


class ConsumptionPeriod(StatefulModel):
    scope: StockScope
    article_id: str
    period_id: str
    period_start: date
    period_end: date
    evidenced_days: int | None = None
    quantity: Decimal | None = None
    unit: str
    state: StockDataState
    methodology_version: str
    aggregation_ref: str | None = None
    source_ref: str | None = None

    @model_validator(mode="after")
    def validate_period(self) -> "ConsumptionPeriod":
        self.validate_conflict_state(self.state)
        if self.period_end < self.period_start:
            raise ValueError("Periodo inválido")
        if self.state == "KNOWN":
            if self.quantity is None or self.evidenced_days is None:
                raise ValueError("Consumption KNOWN requiere cantidad y días")
            _non_negative(self.quantity, "consumption.quantity")
            days = (self.period_end - self.period_start).days + 1
            if self.evidenced_days != days:
                raise ValueError("Periodo KNOWN debe estar completamente evidenciado")
            if not self.aggregation_ref or not _has_evidence(self.source_ref, self.trace_refs):
                raise ValueError("Consumption KNOWN requiere agregación y fuente/traza")
        elif self.quantity is not None:
            raise ValueError("Consumption no KNOWN no publica cantidad")
        return self


class RequiredPeriodSpec(FrozenModel):
    period_id: str
    period_start: date
    period_end: date

    @model_validator(mode="after")
    def validate_period(self) -> "RequiredPeriodSpec":
        if self.period_end < self.period_start:
            raise ValueError("RequiredPeriodSpec inválido")
        return self


class HistoricalDemandPolicy(StatefulModel):
    parameter: ConfiguredParameterValue
    required_periods: tuple[RequiredPeriodSpec, ...] = ()
    period_calendar_ref: str | None = None
    extended_applicable_to: date | None = None
    applicability_source_ref: str | None = None
    source_ref: str | None = None
    state: StockDataState

    @model_validator(mode="after")
    def validate_policy(self) -> "HistoricalDemandPolicy":
        self.validate_conflict_state(self.state)
        if self.state == "KNOWN":
            if self.parameter.parameter_id != "STK-006" or self.parameter.state != "KNOWN":
                raise ValueError("Historical policy KNOWN requiere STK-006 KNOWN")
            if not self.period_calendar_ref or not _has_evidence(self.source_ref, self.trace_refs):
                raise ValueError("Historical policy KNOWN requiere calendario y fuente/traza")
            ids = [p.period_id for p in self.required_periods]
            if len(ids) != len(set(ids)) or not ids:
                raise ValueError("Periodos requeridos deben ser no vacíos y únicos")
            ordered = sorted(self.required_periods, key=lambda p: (p.period_start, p.period_end, p.period_id))
            for left, right in zip(ordered, ordered[1:]):
                if right.period_start <= left.period_end:
                    raise ValueError("Periodos requeridos no pueden solaparse")
            if self.extended_applicable_to and not self.applicability_source_ref:
                raise ValueError("Extensión temporal requiere applicability_source_ref")
        return self


class AuthorizedForecastRate(StatefulModel):
    scope: StockScope
    article_id: str
    daily_demand: Decimal | None = None
    unit: str
    state: StockDataState
    forecast_version: str | None = None
    reference_date: date | None = None
    applicable_from: date | None = None
    applicable_to: date | None = None
    horizon_ref: str | None = None
    source_ref: str | None = None

    @model_validator(mode="after")
    def validate_forecast(self) -> "AuthorizedForecastRate":
        self.validate_conflict_state(self.state)
        if self.state == "KNOWN":
            if self.daily_demand is None:
                raise ValueError("Forecast KNOWN requiere daily_demand")
            _non_negative(self.daily_demand, "daily_demand")
            if not all((self.forecast_version, self.reference_date, self.applicable_from, self.applicable_to, self.horizon_ref)):
                raise ValueError("Forecast KNOWN requiere versión e intervalo/horizonte")
            assert self.applicable_from is not None and self.reference_date is not None and self.applicable_to is not None
            if not (self.applicable_from <= self.reference_date <= self.applicable_to):
                raise ValueError("reference_date fuera de aplicabilidad forecast")
            if not _has_evidence(self.source_ref, self.trace_refs):
                raise ValueError("Forecast KNOWN requiere fuente/traza")
        elif self.daily_demand is not None:
            raise ValueError("Forecast no KNOWN no publica daily_demand")
        return self


class DemandRateResult(StatefulModel):
    identity: StockResultIdentity
    selection: DemandMethodSelection
    method: DemandMethod | None = None
    daily_demand: Decimal | None = None
    unit: str
    state: StockDataState
    reference_date: date | None = None
    applicable_from: date | None = None
    applicable_to: date | None = None
    applicability_source_ref: str | None = None
    window_or_horizon: str | None = None
    source_ref: str | None = None
    forecast_version: str | None = None

    @model_validator(mode="after")
    def validate_result(self) -> "DemandRateResult":
        self.validate_conflict_state(self.state)
        if self.state == "KNOWN":
            if self.selection.state != "KNOWN" or self.method is None or self.daily_demand is None or self.reference_date is None:
                raise ValueError("DemandRate KNOWN requiere selección, método, tasa y fecha")
            if self.method != self.selection.method:
                raise ValueError("DemandRate.method debe coincidir con selection.method")
            _non_negative(self.daily_demand, "daily_demand")
            if self.applicable_from is None or self.applicable_to is None or self.applicable_to < self.applicable_from:
                raise ValueError("DemandRate KNOWN requiere intervalo válido")
            if self.method == "HISTORICAL_CONSUMPTION":
                if self.forecast_version is not None or self.identity.forecast_version is not None:
                    raise ValueError("Demanda histórica no puede portar forecast_version")
            elif not self.forecast_version or self.identity.forecast_version != self.forecast_version:
                raise ValueError("Forecast KNOWN exige versión exacta en identidad y resultado")
        elif self.daily_demand is not None:
            raise ValueError("DemandRate no KNOWN no publica tasa")
        return self


class CoverageResult(StatefulModel):
    identity: StockResultIdentity
    coverage_days: Decimal | None = None
    state: CoverageState
    demand: DemandRateResult

    @model_validator(mode="after")
    def validate_coverage(self) -> "CoverageResult":
        self.validate_conflict_state(self.state)
        if self.state == "FINITE":
            if self.coverage_days is None:
                raise ValueError("Coverage FINITE requiere coverage_days")
            _non_negative(self.coverage_days, "coverage_days")
        elif self.coverage_days is not None:
            raise ValueError("Coverage no FINITE no publica coverage_days")
        return self


class ProjectionMovement(StatefulModel):
    movement_id: str
    commitment_id: str | None = None
    opening_reconciliation_ref: str | None = None
    supply_identity: str | None = None
    supplier_id: str | None = None
    supply_document_ref: str | None = None
    confirmed_demand_id: str | None = None
    demand_segment_id: str | None = None
    scenario_id: str | None = None
    scope: StockScope
    article_id: str
    direction: MovementDirection
    quantity: Decimal | None = None
    unit: str | None = None
    source_unit: str | None = None
    normalization_ref: str | None = None
    effective_date: date | None = None
    state: StockDataState
    source_kind: MovementSourceKind
    source_ref: str | None = None

    @model_validator(mode="after")
    def validate_movement(self) -> "ProjectionMovement":
        self.validate_conflict_state(self.state)
        expected_direction: MovementDirection = "INFLOW" if self.source_kind in {"PENDING_ORDER", "IN_TRANSIT", "PROPOSED_PURCHASE"} else "OUTFLOW"
        if self.direction != expected_direction:
            raise ValueError("source_kind y direction incompatibles")
        if self.state == "KNOWN":
            if self.quantity is None or self.unit is None or self.effective_date is None:
                raise ValueError("Movimiento KNOWN requiere cantidad, unidad y fecha")
            _non_negative(self.quantity, "movement.quantity")
            if self.source_unit and self.source_unit != self.unit and not self.normalization_ref:
                raise ValueError("Movimiento normalizado requiere normalization_ref")
            if not _has_evidence(self.source_ref, self.trace_refs):
                raise ValueError("Movimiento KNOWN requiere fuente/traza")
            if self.source_kind in {"PENDING_ORDER", "IN_TRANSIT"} and not all((self.supply_identity, self.supplier_id, self.supply_document_ref)):
                raise ValueError("M06 KNOWN requiere supply identity, proveedor y documento")
            if self.source_kind == "AUTHORIZED_DEMAND" and (self.confirmed_demand_id is not None or self.demand_segment_id is not None):
                raise ValueError("AUTHORIZED_DEMAND genérica no porta IDs comerciales")
            if self.source_kind == "CONFIRMED_DEMAND" and (not self.confirmed_demand_id or not self.demand_segment_id):
                raise ValueError("CONFIRMED_DEMAND requiere pedido y segmento")
            if self.source_kind == "RESERVATION" and (not self.commitment_id or not self.opening_reconciliation_ref):
                raise ValueError("RESERVATION requiere commitment_id y reconciliation_ref")
            if self.source_kind == "OTHER_AUTHORIZED_NEED" and not self.opening_reconciliation_ref:
                raise ValueError("OTHER_AUTHORIZED_NEED requiere reconciliation_ref")
            if self.source_kind == "PROPOSED_PURCHASE" and not self.scenario_id:
                raise ValueError("PROPOSED_PURCHASE requiere scenario_id")
        elif self.quantity is not None:
            raise ValueError("Movimiento no KNOWN no publica quantity")
        return self


class DemandProjectionSchedule(StatefulModel):
    selection: DemandMethodSelection
    demand: DemandRateResult
    state: StockDataState
    schedule_from: date | None = None
    schedule_to: date | None = None
    demand_movement_ids: tuple[str, ...] = ()
    transformation_ref: str | None = None
    reconciliation_ref: str | None = None
    source_ref: str | None = None

    @model_validator(mode="after")
    def validate_schedule(self) -> "DemandProjectionSchedule":
        self.validate_conflict_state(self.state)
        if len(self.demand_movement_ids) != len(set(self.demand_movement_ids)):
            raise ValueError("demand_movement_ids no puede contener duplicados")
        if self.state == "KNOWN":
            if self.selection.state != "KNOWN" or self.demand.state != "KNOWN":
                raise ValueError("Schedule KNOWN requiere selección y demanda KNOWN")
            if self.selection != self.demand.selection or self.demand.method != self.selection.method:
                raise ValueError("Schedule KNOWN requiere selección idéntica a DemandRateResult")
            if self.schedule_from is None or self.schedule_to is None or self.schedule_to < self.schedule_from:
                raise ValueError("Schedule KNOWN requiere intervalo válido")
            if not self.transformation_ref or not self.reconciliation_ref:
                raise ValueError("Schedule KNOWN requiere transformación y reconciliación")
            if not _has_evidence(self.source_ref, self.trace_refs):
                raise ValueError("Schedule KNOWN requiere fuente/traza")
        return self


class StockProjectionInput(FrozenModel):
    context: StockComputationContext
    opening: StockAvailabilityResult
    movements: CollectionEnvelope[ProjectionMovement]
    horizon: ProjectionHorizon
    demand_schedule: DemandProjectionSchedule
    scenario_id: str


class ProjectionPoint(StatefulModel):
    reference_date: date
    projected_stock: Decimal | None = None
    state: StockDataState
    incorporated_confirmed_demand: tuple[IncorporatedDemandQuantity, ...] = ()

    @model_validator(mode="after")
    def validate_point(self) -> "ProjectionPoint":
        self.validate_conflict_state(self.state)
        if self.state == "KNOWN":
            if self.projected_stock is None:
                raise ValueError("ProjectionPoint KNOWN requiere projected_stock")
            _finite(self.projected_stock, "projected_stock")
        elif self.projected_stock is not None:
            raise ValueError("ProjectionPoint no KNOWN no publica saldo")
        return self


class ProjectedDecimalMetric(StatefulModel):
    value: Decimal | None = None
    state: StockDataState

    @model_validator(mode="after")
    def validate_metric(self) -> "ProjectedDecimalMetric":
        self.validate_conflict_state(self.state)
        if self.state == "KNOWN":
            if self.value is None:
                raise ValueError("Métrica KNOWN requiere value")
            _finite(self.value, "metric.value")
        elif self.value is not None:
            raise ValueError("Métrica no KNOWN no publica value")
        return self


class ProjectedDateMetric(StatefulModel):
    value: date | None = None
    state: StockDataState

    @model_validator(mode="after")
    def validate_metric(self) -> "ProjectedDateMetric":
        self.validate_conflict_state(self.state)
        if self.state == "KNOWN" and self.value is None:
            raise ValueError("Métrica fecha KNOWN requiere value")
        if self.state != "KNOWN" and self.value is not None:
            raise ValueError("Métrica fecha no KNOWN no publica value")
        return self


class StockProjectionResult(StatefulModel):
    identity: StockResultIdentity
    horizon: ProjectionHorizon
    points: tuple[ProjectionPoint, ...] = ()
    minimum_projected_stock: ProjectedDecimalMetric
    depletion_date: ProjectedDateMetric
    incorporated_confirmed_demand_at_horizon: tuple[IncorporatedDemandQuantity, ...] = ()
    state: StockDataState

    @model_validator(mode="after")
    def validate_projection_result(self) -> "StockProjectionResult":
        self.validate_conflict_state(self.state)
        if self.points:
            expected = self.points[-1].incorporated_confirmed_demand
            if self.incorporated_confirmed_demand_at_horizon != expected:
                raise ValueError("La composición de horizonte debe coincidir exactamente con el último point")
        elif self.incorporated_confirmed_demand_at_horizon:
            raise ValueError("Sin points no puede publicarse composición de horizonte")
        return self


class StockReferenceValue(StatefulModel):
    identity: StockResultIdentity
    reference_kind: StockReferenceKind
    reference_date: date
    value: Decimal | None = None
    unit: str
    state: StockDataState
    incorporated_confirmed_demand: tuple[IncorporatedDemandQuantity, ...] = ()
    source_ref: str | None = None

    @model_validator(mode="after")
    def validate_reference(self) -> "StockReferenceValue":
        self.validate_conflict_state(self.state)
        if self.state == "KNOWN":
            if self.value is None:
                raise ValueError("StockReference KNOWN requiere value")
            _finite(self.value, "reference.value")
        elif self.value is not None:
            raise ValueError("StockReference no KNOWN no publica value")
        return self


class StockMaximumBasis(FrozenModel):
    mode: MaximumMode
    direct_threshold: AuthorizedQuantityThreshold | None = None
    coverage_parameter: ConfiguredParameterValue | None = None
    demand: DemandRateResult | None = None
    trace_refs: tuple[str, ...] = ()

    @model_validator(mode="after")
    def validate_branch(self) -> "StockMaximumBasis":
        if self.mode == "DIRECT_QUANTITY":
            if self.direct_threshold is None or self.coverage_parameter is not None or self.demand is not None:
                raise ValueError("DIRECT_QUANTITY requiere solo direct_threshold")
        elif self.direct_threshold is not None or self.coverage_parameter is None or self.demand is None:
            raise ValueError("COVERAGE_MAXIMUM requiere parameter + demand")
        return self


class ExcessToleranceBasis(FrozenModel):
    mode: ToleranceMode
    quantity_threshold: AuthorizedQuantityThreshold | None = None
    rate_parameter: ConfiguredParameterValue | None = None
    trace_refs: tuple[str, ...] = ()

    @model_validator(mode="after")
    def validate_branch(self) -> "ExcessToleranceBasis":
        if self.mode == "QUANTITY":
            if self.quantity_threshold is None or self.rate_parameter is not None:
                raise ValueError("QUANTITY requiere solo quantity_threshold")
        elif self.quantity_threshold is not None or self.rate_parameter is None:
            raise ValueError("RATE requiere solo rate_parameter")
        return self


class ExcessResult(StatefulModel):
    identity: StockResultIdentity
    stock_reference: StockReferenceValue
    stock_maximum: Decimal | None = None
    excess_tolerance_quantity: Decimal | None = None
    excess_threshold: Decimal | None = None
    excess_quantity: Decimal | None = None
    state: ExcessState
    incorporated_confirmed_demand: tuple[IncorporatedDemandQuantity, ...] = ()

    @model_validator(mode="after")
    def validate_result(self) -> "ExcessResult":
        self.validate_conflict_state(self.state)
        if self.identity != self.stock_reference.identity:
            raise ValueError("ExcessResult.identity debe coincidir con stock_reference.identity")
        if self.incorporated_confirmed_demand != self.stock_reference.incorporated_confirmed_demand:
            raise ValueError("ExcessResult debe copiar exactamente la composición de stock_reference")
        determined = self.state in {"NO_EXCESS", "WITHIN_TOLERANCE", "EXCESS"}
        values = (self.stock_maximum, self.excess_tolerance_quantity, self.excess_threshold, self.excess_quantity)
        if determined:
            if any(v is None for v in values):
                raise ValueError("Excess determinado requiere todas las cantidades")
            for name, value in zip(("maximum", "tolerance", "threshold", "excess"), values):
                assert value is not None
                _non_negative(value, name)
        elif any(v is not None for v in values):
            raise ValueError("Excess incierto no publica cantidades determinadas")
        return self


class ConfirmedDemandRecord(StatefulModel):
    confirmed_demand_id: str
    order_id: str | None = None
    customer_id: str | None = None
    scope: StockScope
    article_id: str
    pending_quantity: NormalizedQuantity
    order_date: date | None = None
    confirmation_date: date | None = None
    expected_delivery_date: date | None = None
    business_status: str | None = None
    applicability_state: DemandApplicabilityState
    applicability_source_ref: str | None = None
    source_ref: str | None = None

    @model_validator(mode="after")
    def validate_record(self) -> "ConfirmedDemandRecord":
        if self.applicability_state == "APLICABLE_Y_VALIDADA":
            if not all((self.order_id, self.customer_id, self.order_date, self.confirmation_date, self.expected_delivery_date, self.business_status, self.applicability_source_ref)):
                raise ValueError("Pedido aplicable requiere atributos comerciales completos")
            if self.pending_quantity.state != "KNOWN":
                raise ValueError("Pedido aplicable requiere pending KNOWN")
            if not _has_evidence(self.source_ref, self.trace_refs):
                raise ValueError("Pedido aplicable requiere fuente/traza")
        elif self.applicability_state == "NO_APLICABLE":
            if not self.applicability_source_ref or not _has_evidence(self.source_ref, self.trace_refs):
                raise ValueError("NO_APLICABLE requiere exclusión demostrada y fuente/traza")
        return self


class AllocationLedgerEntry(FrozenModel):
    allocation_entry_id: str
    confirmed_demand_id: str
    scope: StockScope
    article_id: str
    allocated_quantity: Decimal
    unit: str
    decision_id: str
    scenario_id: str
    excess_reference_date: date
    allocation_result_ref: str
    trace_refs: tuple[str, ...] = ()

    @model_validator(mode="after")
    def validate_entry(self) -> "AllocationLedgerEntry":
        _finite(self.allocated_quantity, "allocated_quantity")
        if self.allocated_quantity <= 0:
            raise ValueError("allocated_quantity debe ser >0")
        return self


class AllocationLedgerSnapshot(FrozenModel):
    reference_date: date
    scope: StockScope
    article_id: str
    state: CollectionState
    entries: tuple[AllocationLedgerEntry, ...] = ()
    source_ref: str | None = None
    issue_refs: tuple[DataIssueRef, ...] = ()
    trace_refs: tuple[str, ...] = ()

    @model_validator(mode="after")
    def validate_snapshot(self) -> "AllocationLedgerSnapshot":
        if self.state == "KNOWN":
            if not _has_evidence(self.source_ref, self.trace_refs):
                raise ValueError("Ledger KNOWN requiere fuente/traza")
            ids = [e.allocation_entry_id for e in self.entries]
            if len(ids) != len(set(ids)):
                raise ValueError("Ledger no admite allocation_entry_id duplicado")
            for entry in self.entries:
                if entry.scope != self.scope or entry.article_id != self.article_id:
                    raise ValueError("Ledger KNOWN no admite entries de otro scope/article")
        if self.state == "CONFLICTING_DATA" and not any(i.issue_type == "CONTRADICTION" for i in self.issue_refs):
            raise ValueError("Ledger conflictivo requiere incidencia")
        return self


class DemandAllocation(FrozenModel):
    allocation_entry_id: str
    confirmed_demand_id: str
    quantity_to_apply: Decimal
    unit: str
    allocation_source_ref: str
    trace_refs: tuple[str, ...] = ()

    @model_validator(mode="after")
    def validate_allocation(self) -> "DemandAllocation":
        _finite(self.quantity_to_apply, "quantity_to_apply")
        if self.quantity_to_apply <= 0:
            raise ValueError("quantity_to_apply debe ser >0")
        return self


class AllocationScope(FrozenModel):
    identity: StockResultIdentity
    scope: StockScope
    article_id: str
    evaluation_date: date
    excess_reference_date: date
    horizon: ProjectionHorizon
    trace_refs: tuple[str, ...] = ()


class ConfirmedDemandAbsorptionResult(StatefulModel):
    identity: StockResultIdentity
    excess_result: ExcessResult
    business_state: AbsorptionBusinessState
    total_remaining_applicable: Decimal | None = None
    absorbed_excess: Decimal | None = None
    residual_excess: Decimal | None = None
    allocation_plan: tuple[DemandAllocation, ...] = ()
    resulting_ledger: AllocationLedgerSnapshot | None = None

    @model_validator(mode="after")
    def validate_result(self) -> "ConfirmedDemandAbsorptionResult":
        if self.identity != self.excess_result.identity:
            raise ValueError("AbsorptionResult.identity debe coincidir con ExcessResult.identity")
        determined_excess = self.excess_result.excess_quantity
        if self.business_state in {"NO_EXISTE", "NO_APLICABLE", "APLICABLE_Y_VALIDADA"}:
            for name, value in (
                ("total_remaining_applicable", self.total_remaining_applicable),
                ("absorbed_excess", self.absorbed_excess),
                ("residual_excess", self.residual_excess),
            ):
                if value is None:
                    raise ValueError(f"{self.business_state} requiere {name}")
                _non_negative(value, name)
            if determined_excess is None:
                raise ValueError("Un estado M08 determinado requiere ExcessResult determinado")
            assert self.total_remaining_applicable is not None
            assert self.absorbed_excess is not None
            assert self.residual_excess is not None
            if self.total_remaining_applicable < self.absorbed_excess:
                raise ValueError("total_remaining_applicable no puede ser menor que absorbed_excess")
            if self.absorbed_excess + self.residual_excess != determined_excess:
                raise ValueError("absorbed_excess + residual_excess debe igualar excess_quantity")
        if self.business_state in {"NO_EXISTE", "NO_APLICABLE"}:
            if self.absorbed_excess != Decimal("0"):
                raise ValueError(f"{self.business_state} exige absorbed_excess=0")
            if self.allocation_plan:
                raise ValueError(f"{self.business_state} exige allocation_plan vacío")
            if determined_excess is not None and self.residual_excess != determined_excess:
                raise ValueError(f"{self.business_state} debe preservar todo el exceso como residual")
        elif self.business_state == "APLICABLE_Y_VALIDADA":
            assert self.absorbed_excess is not None
            if self.absorbed_excess <= 0:
                raise ValueError("APLICABLE_Y_VALIDADA exige absorción positiva")
            if not self.allocation_plan:
                raise ValueError("APLICABLE_Y_VALIDADA exige allocation_plan no vacío")
            plan_total = sum((item.quantity_to_apply for item in self.allocation_plan), Decimal("0"))
            if plan_total != self.absorbed_excess:
                raise ValueError("allocation_plan debe sumar exactamente absorbed_excess")
            if self.resulting_ledger is None or self.resulting_ledger.state != "KNOWN":
                raise ValueError("APLICABLE_Y_VALIDADA exige resulting_ledger KNOWN")
        elif self.business_state == "NO_VERIFICABLE":
            if any(v is not None for v in (self.absorbed_excess, self.residual_excess)):
                raise ValueError("NO_VERIFICABLE no publica absorción/residual")
        return self


__all__ = [
    "AbsorptionBusinessState", "AllocationLedgerEntry", "AllocationLedgerSnapshot",
    "AllocationScope", "AuthorizedForecastRate", "AuthorizedQuantityThreshold",
    "AuthorizedStockPolicyQuantity", "CollectionEnvelope", "ConfiguredParameterValue",
    "ConfirmedDemandAbsorptionResult", "ConfirmedDemandRecord", "ConsumptionPeriod",
    "CoverageResult", "CoverageState", "DataIssueRef", "DemandAllocation",
    "DemandApplicabilityState", "DemandMethod", "DemandMethodSelection",
    "DemandProjectionSchedule", "DemandRateResult", "ExcessResult", "ExcessState",
    "ExcessToleranceBasis", "HistoricalDemandPolicy", "IncorporatedDemandQuantity",
    "MaximumMode", "MovementDirection", "MovementSourceKind", "NormalizedQuantity",
    "ProjectedDateMetric", "ProjectedDecimalMetric", "ProjectionHorizon",
    "ProjectionMovement", "ProjectionPoint", "RequiredPeriodSpec", "StockAvailabilityInput",
    "StockAvailabilityResult", "StockComputationContext", "StockCommitmentComponent",
    "StockDataState", "StockMaximumBasis", "StockPolicyConcept", "StockProjectionInput",
    "StockProjectionResult", "StockReferenceKind", "StockReferenceValue", "StockResultIdentity",
    "StockScope", "ThresholdPurpose", "ToleranceMode",
]
