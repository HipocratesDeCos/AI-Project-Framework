"""C1 structural comparison for EIOS Decision Twin."""
from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


ViabilityStatus = Literal[
    "VIABLE",
    "VIABLE_CON_CONDICIONES",
    "NOT_VIABLE",
    "NOT_EVALUABLE",
]


class AlternativeRepresentation(BaseModel):
    """Transient representation of an available alternative; not a persisted identity."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    representation_ref: str = Field(min_length=1, max_length=256)
    scenario_id: str | None = Field(default=None, max_length=128)
    viability: ViabilityStatus | None = None
    results: dict[str, Any] = Field(default_factory=dict)
    conditions: dict[str, Any] = Field(default_factory=dict)
    consequences: dict[str, Any] = Field(default_factory=dict)
    risk_refs: tuple[str, ...] = ()
    trace_refs: tuple[str, ...] = ()


class ComparisonObservation(BaseModel):
    """One descriptive observation across the represented alternatives."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    attribute: str = Field(min_length=1, max_length=256)
    values: tuple[tuple[str, Any], ...]
    comparable: bool
    difference: bool
    trace_refs: tuple[str, ...] = ()


class DecisionTwinComparison(BaseModel):
    """Descriptive comparison; deliberately contains no preference or selection output."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    alternatives: tuple[str, ...]
    observations: tuple[ComparisonObservation, ...]
    common_values: tuple[str, ...] = ()
    differences: tuple[str, ...] = ()
    missing_attributes: tuple[str, ...] = ()
    viability_differences: tuple[str, ...] = ()
    consequence_differences: tuple[str, ...] = ()
    trace_refs: tuple[str, ...] = ()

    @model_validator(mode="after")
    def validate_output(self) -> "DecisionTwinComparison":
        if len(self.alternatives) < 2:
            raise ValueError("La comparación requiere al menos dos alternativas")
        if len(set(self.alternatives)) != len(self.alternatives):
            raise ValueError("Las referencias de representación deben ser únicas")
        if set(self.common_values) & set(self.differences):
            raise ValueError("Un atributo no puede ser simultáneamente común y diferente")
        return self


class DecisionTwinComparisonInput(BaseModel):
    """Input boundary for structural comparison."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    alternatives: tuple[AlternativeRepresentation, ...]

    @model_validator(mode="after")
    def validate_input(self) -> "DecisionTwinComparisonInput":
        if len(self.alternatives) < 2:
            raise ValueError("La comparación requiere al menos dos alternativas")
        refs = [item.representation_ref for item in self.alternatives]
        if len(refs) != len(set(refs)):
            raise ValueError("Las referencias de representación deben ser únicas")
        return self


__all__ = [
    "AlternativeRepresentation",
    "ComparisonObservation",
    "DecisionTwinComparison",
    "DecisionTwinComparisonInput",
    "ViabilityStatus",
]
