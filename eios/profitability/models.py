"""Physical contracts for EIOS Profitability Core v0.1."""
from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from eios.core.models import DecisionContext, PurchaseOperation


EconomicBasisState = Literal[
    "KNOWN",
    "NOT_EVIDENCED",
    "CONFLICTING_DATA",
    "NOT_DETERMINABLE",
]
ProfitabilityCalculationState = Literal[
    "DETERMINED",
    "NOT_EVIDENCED",
    "CONFLICTING_DATA",
    "NOT_DETERMINABLE",
]


def _require_finite(value: Decimal | None) -> Decimal | None:
    if value is not None and not value.is_finite():
        raise ValueError("El valor decimal debe ser finito")
    return value


class _AuthorizedBasisBase(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        str_strip_whitespace=True,
    )

    state: EconomicBasisState
    decision_id: str = Field(min_length=1, max_length=64)
    scenario_id: str = Field(min_length=1, max_length=64)
    data_snapshot_id: str = Field(min_length=1, max_length=64)
    company_scope: str = Field(min_length=1, max_length=128)
    article_id: str = Field(min_length=1, max_length=64)
    evaluation_date: date
    value: Decimal | None = Field(default=None, ge=0, decimal_places=4)
    currency: str | None = Field(default=None, min_length=3, max_length=3)
    economic_basis_ref: str | None = Field(default=None, min_length=1, max_length=256)
    authority_ref: str | None = Field(default=None, min_length=1, max_length=256)
    source_ref: str | None = Field(default=None, min_length=1, max_length=256)
    transformation_ref: str | None = Field(default=None, min_length=1, max_length=256)
    trace_refs: tuple[str, ...] = ()

    _finite_value = field_validator("value")(_require_finite)

    @model_validator(mode="after")
    def validate_state(self) -> "_AuthorizedBasisBase":
        if self.state == "KNOWN":
            missing = [
                name
                for name, value in (
                    ("value", self.value),
                    ("currency", self.currency),
                    ("economic_basis_ref", self.economic_basis_ref),
                    ("authority_ref", self.authority_ref),
                    ("source_ref", self.source_ref),
                )
                if value is None
            ]
            if missing:
                raise ValueError(
                    "Una base KNOWN requiere: " + ", ".join(missing)
                )
            if not self.trace_refs:
                raise ValueError("Una base KNOWN requiere al menos un trace_ref")
        elif self.value is not None:
            raise ValueError("Una base no KNOWN no puede publicar value")
        return self


class AuthorizedSaleBasis(_AuthorizedBasisBase):
    """Pre-authorized economic sale basis. The core never selects its source."""


class AuthorizedCostBasis(_AuthorizedBasisBase):
    """Pre-authorized economic cost basis. The core never selects its source."""


class ProfitabilityInput(BaseModel):
    """Complete deterministic input envelope for Profitability Core."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        str_strip_whitespace=True,
    )

    context: DecisionContext
    purchase_operation: PurchaseOperation
    company_scope: str = Field(min_length=1, max_length=128)
    evaluation_date: date
    sale_basis: AuthorizedSaleBasis
    cost_basis: AuthorizedCostBasis
    methodology_version: str = Field(min_length=1, max_length=64)

    @model_validator(mode="after")
    def validate_identity(self) -> "ProfitabilityInput":
        if self.purchase_operation.decision_id != self.context.decision_id:
            raise ValueError("purchase_operation.decision_id no coincide con DecisionContext")
        if self.purchase_operation.scenario_id != self.context.scenario_id:
            raise ValueError("purchase_operation.scenario_id no coincide con DecisionContext")

        expected = {
            "decision_id": self.context.decision_id,
            "scenario_id": self.context.scenario_id,
            "data_snapshot_id": self.context.data_snapshot_id,
            "company_scope": self.company_scope,
            "article_id": self.purchase_operation.article_id,
            "evaluation_date": self.evaluation_date,
        }
        for label, basis in (
            ("sale_basis", self.sale_basis),
            ("cost_basis", self.cost_basis),
        ):
            mismatches = [
                field
                for field, expected_value in expected.items()
                if getattr(basis, field) != expected_value
            ]
            if mismatches:
                raise ValueError(
                    f"{label} no coincide con la identidad de ProfitabilityInput: "
                    + ", ".join(mismatches)
                )
        return self


class ProfitabilityResult(BaseModel):
    """Analytical profitability result; deliberately non-decisional."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        str_strip_whitespace=True,
    )

    decision_id: str = Field(min_length=1, max_length=64)
    scenario_id: str = Field(min_length=1, max_length=64)
    data_snapshot_id: str = Field(min_length=1, max_length=64)
    parameters_version: str = Field(min_length=1, max_length=64)
    company_scope: str = Field(min_length=1, max_length=128)
    article_id: str = Field(min_length=1, max_length=64)
    evaluation_date: date
    methodology_version: str = Field(min_length=1, max_length=64)
    sale_basis: AuthorizedSaleBasis
    cost_basis: AuthorizedCostBasis
    calculation_state: ProfitabilityCalculationState
    currency: str | None = Field(default=None, min_length=3, max_length=3)
    economic_basis_ref: str | None = Field(default=None, min_length=1, max_length=256)
    margin_amount: Decimal | None = None
    margin_percentage: Decimal | None = None
    limitations: tuple[str, ...] = ()
    trace_refs: tuple[str, ...] = ()

    _finite_amount = field_validator("margin_amount")(_require_finite)
    _finite_percentage = field_validator("margin_percentage")(_require_finite)

    @model_validator(mode="after")
    def validate_result(self) -> "ProfitabilityResult":
        if self.calculation_state == "DETERMINED":
            if (
                self.margin_amount is None
                or self.margin_percentage is None
                or self.currency is None
                or self.economic_basis_ref is None
            ):
                raise ValueError(
                    "DETERMINED requiere amount, percentage, currency y economic_basis_ref"
                )
            return self

        if self.calculation_state in {"NOT_EVIDENCED", "CONFLICTING_DATA"}:
            if self.margin_amount is not None or self.margin_percentage is not None:
                raise ValueError(
                    "NOT_EVIDENCED/CONFLICTING_DATA no pueden publicar márgenes"
                )
            return self

        # NOT_DETERMINABLE
        if self.margin_percentage is not None:
            raise ValueError("NOT_DETERMINABLE no puede publicar margin_percentage")
        if self.margin_amount is not None and "SALE_BASIS_ZERO" not in self.limitations:
            raise ValueError(
                "Solo SALE_BASIS_ZERO permite amount bajo NOT_DETERMINABLE"
            )
        return self


__all__ = [
    "AuthorizedCostBasis",
    "AuthorizedSaleBasis",
    "EconomicBasisState",
    "ProfitabilityCalculationState",
    "ProfitabilityInput",
    "ProfitabilityResult",
]
