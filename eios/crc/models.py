"""Minimal CRC-MVP runtime contracts.

CRC consumes individual Assessment results plus normative rule metadata.
Normative metadata is deliberately separate from the canonical C0 Rule model:
CRC must not mutate or extend C0 authority merely to consolidate results.
"""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from eios.core.models import Assessment, DecisionContext


RuleEffect = Literal["R0", "R1", "R2", "R3"]
RuleSeverity = Literal["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFORMATIVE"]
ConsolidatedResult = Literal[
    "COMPRAR",
    "NEGOCIAR",
    "COMPRAR CONDICIONADO",
    "NO COMPRAR",
    "INFORMACIÓN INSUFICIENTE",
]


class CRCRuleMetadata(BaseModel):
    """Normative metadata resolved for one Assessment.rule_id."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    rule_id: str = Field(min_length=1, max_length=64)
    version: str = Field(min_length=1, max_length=64)
    effect: RuleEffect
    severity: RuleSeverity


class CRCConflict(BaseModel):
    """Traceable coexistence of incompatible effects."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    effects: tuple[RuleEffect, ...]
    rule_ids: tuple[str, ...]


class CRCResult(BaseModel):
    """Consolidated non-executable CRC recommendation."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    consolidated_result: ConsolidatedResult
    dominant_reason: str = Field(min_length=1, max_length=256)
    relevant_factors: tuple[str, ...] = ()
    conflicts: tuple[CRCConflict, ...] = ()
    traceability: tuple[str, ...] = ()


class CRCInput(BaseModel):
    """Minimum input required by the CRC-MVP contract."""

    model_config = ConfigDict(extra="forbid")

    assessments: tuple[Assessment, ...]
    decision_context: DecisionContext
    rule_metadata: tuple[CRCRuleMetadata, ...]


__all__ = [
    "CRCConflict",
    "CRCInput",
    "CRCResult",
    "CRCRuleMetadata",
    "ConsolidatedResult",
    "RuleEffect",
    "RuleSeverity",
]
