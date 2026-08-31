"""Deterministic domain contract for EIOS Negotiation Intelligence.

This module materializes only the NI contract. It does not generate scenarios,
recalculate Decision Twin, modify limits, structure Negotiation Ladder, resolve
conflicts, approve, decide, or execute.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


EpistemicType = Literal[
    "FACT",
    "OBSERVATION",
    "INFERENCE",
    "ESTIMATE",
    "HYPOTHESIS",
    "RECOMMENDATION",
]


class NIContextReferences(BaseModel):
    """Reference-only upstream context; NI does not own these authorities."""

    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)

    decision_id: str = Field(min_length=1, max_length=64)
    decision_version: str = Field(min_length=1, max_length=64)
    scenario_id: str | None = Field(default=None, max_length=64)
    rules_version: str | None = Field(default=None, max_length=64)
    parameters_version: str | None = Field(default=None, max_length=64)
    data_snapshot_id: str | None = Field(default=None, max_length=64)
    viability_reference: str | None = Field(default=None, max_length=128)
    decision_twin_reference: str | None = Field(default=None, max_length=128)
    evidence_references: tuple[str, ...] = ()


class NIAssertion(BaseModel):
    """One material NI assertion with epistemic qualification."""

    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)

    content: str = Field(min_length=1, max_length=2048)
    epistemic_type: EpistemicType
    confidence: float | None = Field(default=None, ge=0, le=1)
    source_references: tuple[str, ...] = ()

    @model_validator(mode="after")
    def validate_grounding(self) -> "NIAssertion":
        if self.epistemic_type in {"FACT", "OBSERVATION"} and not self.source_references:
            raise ValueError("FACT/OBSERVATION requiere al menos una source_reference")
        return self


class NegotiationContent(BaseModel):
    """Substantive negotiation content; no Ladder structure is represented."""

    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)

    objective: str | None = Field(default=None, max_length=2048)
    opening_request: str | None = Field(default=None, max_length=2048)
    moves: tuple[str, ...] = ()
    concessions: tuple[str, ...] = ()
    counterpart_requirements: tuple[str, ...] = ()
    tradeoffs: tuple[str, ...] = ()
    packages: tuple[str, ...] = ()
    alternatives: tuple[str, ...] = ()
    fallback: str | None = Field(default=None, max_length=2048)
    conditions: tuple[str, ...] = ()
    convenience_analysis: tuple[str, ...] = ()


class NegotiationIntelligenceResult(BaseModel):
    """Immutable NI result envelope."""

    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)

    negotiation_result_id: str = Field(min_length=1, max_length=128)
    context_references: NIContextReferences
    negotiation_content: NegotiationContent
    justification: tuple[NIAssertion, ...] = ()
    epistemic_qualifications: tuple[NIAssertion, ...] = ()
    confidence_uncertainty: tuple[NIAssertion, ...] = ()
    source_references: tuple[str, ...] = ()
    traceability_references: tuple[str, ...] = ()
    version_identity: str = Field(min_length=1, max_length=128)

    @model_validator(mode="after")
    def validate_traceability(self) -> "NegotiationIntelligenceResult":
        if not self.traceability_references:
            raise ValueError("NI result requiere traceability_references")
        return self


__all__ = [
    "EpistemicType",
    "NIAssertion",
    "NIContextReferences",
    "NegotiationContent",
    "NegotiationIntelligenceResult",
]
