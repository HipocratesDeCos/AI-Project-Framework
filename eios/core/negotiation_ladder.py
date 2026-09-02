"""Deterministic domain contract for EIOS Negotiation Ladder.

Ladder only structures, represents, and orders previously determined
negotiation content. It does not create or modify substantive negotiation
content, limits, scenarios, viability, Decision Twin, strategy, decisions,
approvals, or execution.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


StepType = Literal[
    "OBJECTIVE", "OPENING_REQUEST", "MOVE", "CONCESSION", "COUNTERPART_CONSIDERATION",
    "CONDITION", "ALTERNATIVE", "FALLBACK", "LIMIT", "WALK_AWAY",
]


class LadderContextReferences(BaseModel):
    """Reference-only upstream context; Ladder does not own those authorities."""

    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)

    negotiation_result_id: str = Field(min_length=1, max_length=128)
    decision_id: str = Field(min_length=1, max_length=64)
    scenario_id: str | None = Field(default=None, max_length=64)
    source_references: tuple[str, ...] = ()


class LadderStep(BaseModel):
    """One structural representation of previously determined content."""

    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)

    step_id: str = Field(min_length=1, max_length=128)
    step_type: StepType
    source_content_reference: str = Field(min_length=1, max_length=256)
    position: int = Field(ge=1)
    representation_metadata: tuple[str, ...] = ()


class LadderTransition(BaseModel):
    """Structural transition between existing ladder steps."""

    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)

    transition_id: str = Field(min_length=1, max_length=128)
    from_step_id: str = Field(min_length=1, max_length=128)
    to_step_id: str = Field(min_length=1, max_length=128)
    trigger_reference: str | None = Field(default=None, max_length=256)


class LadderRoute(BaseModel):
    """Alternative structural route through existing ladder steps."""

    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)

    route_id: str = Field(min_length=1, max_length=128)
    step_references: tuple[str, ...] = ()


class NegotiationLadderResult(BaseModel):
    """Immutable structural Ladder result."""

    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)

    ladder_id: str = Field(min_length=1, max_length=128)
    context_references: LadderContextReferences
    steps: tuple[LadderStep, ...]
    transitions: tuple[LadderTransition, ...] = ()
    routes: tuple[LadderRoute, ...] = ()
    traceability_references: tuple[str, ...] = ()

    @model_validator(mode="after")
    def validate_structure(self) -> "NegotiationLadderResult":
        if not self.steps:
            raise ValueError("Ladder result requiere al menos un step")
        if not self.traceability_references:
            raise ValueError("Ladder result requiere traceability_references")

        step_ids = [step.step_id for step in self.steps]
        if len(step_ids) != len(set(step_ids)):
            raise ValueError("step_id debe ser unico")

        positions = [step.position for step in self.steps]
        if len(positions) != len(set(positions)):
            raise ValueError("position debe ser unica")

        step_id_set = set(step_ids)
        transition_ids = [item.transition_id for item in self.transitions]
        if len(transition_ids) != len(set(transition_ids)):
            raise ValueError("transition_id debe ser unico")
        for transition in self.transitions:
            if transition.from_step_id not in step_id_set or transition.to_step_id not in step_id_set:
                raise ValueError("transition referencia un step inexistente")

        route_ids = [route.route_id for route in self.routes]
        if len(route_ids) != len(set(route_ids)):
            raise ValueError("route_id debe ser unico")
        for route in self.routes:
            if any(step_id not in step_id_set for step_id in route.step_references):
                raise ValueError("route referencia un step inexistente")

        return self


__all__ = [
    "LadderContextReferences", "LadderRoute", "LadderStep", "LadderTransition",
    "NegotiationLadderResult", "StepType",
]
