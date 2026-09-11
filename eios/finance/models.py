"""Physical Finance Basic contracts for the EIOS procurement MVP."""
from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from eios.core.models import DecisionContext

FlowType = Literal["PAYMENT", "COLLECTION"]
FinancialEvidenceState = Literal["DEMONSTRATED", "NOT_EVIDENCED", "CONFLICTING_DATA"]
CalculationStatus = Literal[
    "DETERMINED",
    "NOT_EVIDENCED",
    "NOT_EVALUABLE",
    "CONFLICTING_DATA",
]


def _normalize_currency(value: str | None) -> str | None:
    if value is None:
        return None
    return value.upper()


def _require_finite(value: Decimal | None) -> Decimal | None:
    if value is not None and not value.is_finite():
        raise ValueError("El valor decimal debe ser finito")
    return value


class ExternalLiquidityReference(BaseModel):
    """Externally supplied liquidity context; never calculated by Finance Basic."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True, frozen=True)

    value: Decimal
    unit: str = Field(min_length=1, max_length=32)
    source_ref: str = Field(min_length=1, max_length=256)

    _finite_value = field_validator("value")(_require_finite)


class FinancialSnapshot(BaseModel):
    """Financial position identified by company, date and data snapshot."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True, frozen=True)

    company_scope: str = Field(min_length=1, max_length=128)
    as_of_date: date
    data_snapshot_id: str = Field(min_length=1, max_length=64)
    currency: str = Field(min_length=3, max_length=3)
    available_treasury: Decimal | None = Field(default=None, ge=0)
    treasury_evidence_ref: str | None = Field(default=None, min_length=1, max_length=256)
    external_liquidity: ExternalLiquidityReference | None = None

    _normalize_currency = field_validator("currency")(_normalize_currency)
    _finite_treasury = field_validator("available_treasury")(_require_finite)

    @model_validator(mode="after")
    def validate_treasury_evidence(self) -> "FinancialSnapshot":
        if self.available_treasury is not None and self.treasury_evidence_ref is None:
            raise ValueError("available_treasury requiere treasury_evidence_ref")
        return self


class CashFlow(BaseModel):
    """One future payment or collection with explicit evidence semantics."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True, frozen=True)

    flow_id: str = Field(min_length=1, max_length=128)
    flow_type: FlowType
    amount: Decimal | None = Field(default=None, ge=0)
    currency: str | None = Field(default=None, min_length=3, max_length=3)
    due_date: date | None = None
    due_date_evidenced: bool = False
    source_ref: str | None = Field(default=None, min_length=1, max_length=256)
    evidence_state: FinancialEvidenceState

    _normalize_currency = field_validator("currency")(_normalize_currency)
    _finite_amount = field_validator("amount")(_require_finite)

    @model_validator(mode="after")
    def validate_evidence_semantics(self) -> "CashFlow":
        if self.due_date_evidenced:
            if self.due_date is None:
                raise ValueError("due_date_evidenced=True requiere due_date")
            if self.source_ref is None:
                raise ValueError("due_date_evidenced=True requiere source_ref")

        if self.evidence_state == "DEMONSTRATED":
            missing = [
                name
                for name, value in (
                    ("amount", self.amount),
                    ("currency", self.currency),
                    ("due_date", self.due_date),
                    ("source_ref", self.source_ref),
                )
                if value is None
            ]
            if missing:
                raise ValueError(
                    "Un flujo DEMONSTRATED requiere " + ", ".join(missing)
                )
        return self


class WorkingCapitalInput(BaseModel):
    """Accounting totals supplied by an authorized source."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True, frozen=True)

    company_scope: str = Field(min_length=1, max_length=128)
    as_of_date: date
    currency: str = Field(min_length=3, max_length=3)
    current_assets: Decimal | None = None
    current_liabilities: Decimal | None = None
    assets_source_ref: str | None = Field(default=None, min_length=1, max_length=256)
    liabilities_source_ref: str | None = Field(default=None, min_length=1, max_length=256)

    _normalize_currency = field_validator("currency")(_normalize_currency)
    _finite_assets = field_validator("current_assets")(_require_finite)
    _finite_liabilities = field_validator("current_liabilities")(_require_finite)

    @model_validator(mode="after")
    def validate_sources(self) -> "WorkingCapitalInput":
        if self.current_assets is not None and self.assets_source_ref is None:
            raise ValueError("current_assets requiere assets_source_ref")
        if self.current_liabilities is not None and self.liabilities_source_ref is None:
            raise ValueError("current_liabilities requiere liabilities_source_ref")
        return self


class FinanceBasicInput(BaseModel):
    """Complete input envelope for deterministic Finance Basic analysis."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    context: DecisionContext
    snapshot: FinancialSnapshot
    cash_flows: tuple[CashFlow, ...] = ()
    horizon_days: int = Field(gt=0)
    treasury_minimum: Decimal | None = None
    working_capital_input: WorkingCapitalInput | None = None

    _finite_treasury_minimum = field_validator("treasury_minimum")(_require_finite)

    @model_validator(mode="after")
    def validate_identity_and_flows(self) -> "FinanceBasicInput":
        if self.snapshot.data_snapshot_id != self.context.data_snapshot_id:
            raise ValueError("snapshot.data_snapshot_id debe coincidir con DecisionContext")

        flow_ids = [flow.flow_id for flow in self.cash_flows]
        if len(flow_ids) != len(set(flow_ids)):
            raise ValueError("flow_id duplicado en FinanceBasicInput")

        try:
            self.snapshot.as_of_date + timedelta(days=self.horizon_days)
        except OverflowError as exc:
            raise ValueError("horizon_days no es representable desde as_of_date") from exc
        return self


class ProjectionPoint(BaseModel):
    """Treasury position after all demonstrated flows for one due date."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    date: date
    collections: Decimal = Field(ge=0)
    payments: Decimal = Field(ge=0)
    treasury_after: Decimal

    _finite_collections = field_validator("collections")(_require_finite)
    _finite_payments = field_validator("payments")(_require_finite)
    _finite_treasury = field_validator("treasury_after")(_require_finite)


class ProjectionResult(BaseModel):
    """Cash projection with explicit completeness semantics."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    status: CalculationStatus
    horizon_end: date
    opening_treasury: Decimal | None = None
    points: tuple[ProjectionPoint, ...] = ()
    financial_capacity_forecast: Decimal | None = None
    unresolved_flow_ids: tuple[str, ...] = ()
    limitations: tuple[str, ...] = ()

    _finite_opening = field_validator("opening_treasury")(_require_finite)
    _finite_capacity = field_validator("financial_capacity_forecast")(_require_finite)

    @model_validator(mode="after")
    def validate_completeness(self) -> "ProjectionResult":
        if self.status == "DETERMINED":
            if self.opening_treasury is None or self.financial_capacity_forecast is None:
                raise ValueError("ProjectionResult DETERMINED requiere apertura y capacidad")
        elif self.financial_capacity_forecast is not None or self.points:
            raise ValueError("Una proyección no determinada no publica capacidad ni puntos parciales")
        return self


class WorkingCapitalResult(BaseModel):
    """Independent working-capital calculation result."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    status: CalculationStatus
    value: Decimal | None = None
    limitations: tuple[str, ...] = ()

    _finite_value = field_validator("value")(_require_finite)

    @model_validator(mode="after")
    def validate_value_status(self) -> "WorkingCapitalResult":
        if self.status == "DETERMINED" and self.value is None:
            raise ValueError("WorkingCapitalResult DETERMINED requiere value")
        if self.status != "DETERMINED" and self.value is not None:
            raise ValueError("WorkingCapitalResult no determinado no puede publicar value")
        return self


class SafetyMarginResult(BaseModel):
    """Financial safety margin result derived from projected capacity."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    status: CalculationStatus
    value_pct: Decimal | None = None
    limitations: tuple[str, ...] = ()

    _finite_value = field_validator("value_pct")(_require_finite)

    @model_validator(mode="after")
    def validate_value_status(self) -> "SafetyMarginResult":
        if self.status == "DETERMINED" and self.value_pct is None:
            raise ValueError("SafetyMarginResult DETERMINED requiere value_pct")
        if self.status != "DETERMINED" and self.value_pct is not None:
            raise ValueError("SafetyMarginResult no determinado no puede publicar value_pct")
        return self


class FinanceBasicResult(BaseModel):
    """Analytical Finance Basic output; deliberately non-decisional."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    decision_id: str = Field(min_length=1, max_length=64)
    scenario_id: str = Field(min_length=1, max_length=64)
    data_snapshot_id: str = Field(min_length=1, max_length=64)
    parameters_version: str = Field(min_length=1, max_length=64)
    currency: str = Field(min_length=3, max_length=3)
    projection: ProjectionResult
    working_capital: WorkingCapitalResult
    safety_margin: SafetyMarginResult
    external_liquidity: ExternalLiquidityReference | None = None

    _normalize_currency = field_validator("currency")(_normalize_currency)


__all__ = [
    "CalculationStatus",
    "CashFlow",
    "ExternalLiquidityReference",
    "FinanceBasicInput",
    "FinanceBasicResult",
    "FinancialEvidenceState",
    "FinancialSnapshot",
    "FlowType",
    "ProjectionPoint",
    "ProjectionResult",
    "SafetyMarginResult",
    "WorkingCapitalInput",
    "WorkingCapitalResult",
]
