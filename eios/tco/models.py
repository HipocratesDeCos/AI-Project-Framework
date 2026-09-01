"""Physical TCO Core contracts for the EIOS procurement MVP."""
from __future__ import annotations

from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from eios.core.models import PurchaseOperation

CostKind = Literal[
    "TRANSPORT",
    "INSURANCE",
    "TARIFF",
    "NON_RECOVERABLE_TAX",
    "HANDLING",
    "INSPECTION",
    "LOSS",
]
CostApplicability = Literal["APPLICABLE", "NOT_APPLICABLE"]


class CostComponent(BaseModel):
    """One directly attributable cost supplied to TCO."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True, frozen=True)

    component: CostKind
    amount: Decimal | None = Field(default=None, ge=0, decimal_places=4)
    currency: str = Field(min_length=3, max_length=3)
    applicability: CostApplicability = "APPLICABLE"
    attribution_ref: str | None = Field(default=None, min_length=1, max_length=256)
    rule_reference: str | None = Field(default=None, min_length=1, max_length=128)

    @model_validator(mode="after")
    def validate_component(self) -> "CostComponent":
        if self.applicability == "APPLICABLE":
            if self.amount is None:
                raise ValueError("Un componente aplicable requiere amount")
            if self.attribution_ref is None:
                raise ValueError("Un componente aplicable requiere attribution_ref")
            if self.rule_reference is None:
                raise ValueError("Un componente aplicable requiere rule_reference")
        elif self.amount is not None:
            raise ValueError("Un componente NOT_APPLICABLE no puede aportar amount")
        return self


class TCOInput(BaseModel):
    """TCO input using the canonical C0 purchase operation."""

    model_config = ConfigDict(extra="forbid")

    purchase_operation: PurchaseOperation
    attributable_costs: tuple[CostComponent, ...] = ()


class TCOResult(BaseModel):
    """Deterministic TCO result with explicit completeness semantics."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    decision_id: str
    scenario_id: str
    currency: str
    value: Decimal | None = Field(default=None, ge=0, decimal_places=4)
    contributing_components: tuple[str, ...] = ()
    unresolved_components: tuple[str, ...] = ()
    limitations: tuple[str, ...] = ()

    @property
    def complete(self) -> bool:
        return not self.unresolved_components and self.value is not None
