"""Deterministic sufficiency gate for EIOS Price Intelligence."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Literal

SufficiencyStatus = Literal["SUFFICIENT", "LIMITED", "NOT_JUSTIFIABLE"]

@dataclass(frozen=True)
class SufficiencyObservation:
    evidence_sufficient: bool | None = None
    contradictions_resolved: bool | None = None
    temporal_context_satisfied: bool | None = None
    methodological_limitations: tuple[str, ...] = ()


def assess_sufficiency(n_selected: int, observation: SufficiencyObservation) -> SufficiencyStatus:
    if n_selected < 0:
        raise ValueError("n_selected no puede ser negativo")
    if n_selected == 0:
        return "NOT_JUSTIFIABLE"
    if n_selected == 1:
        return "LIMITED"
    if observation.evidence_sufficient is not True:
        return "LIMITED"
    if observation.contradictions_resolved is not True:
        return "LIMITED"
    if observation.temporal_context_satisfied is not True:
        return "LIMITED"
    if observation.methodological_limitations:
        return "LIMITED"
    return "SUFFICIENT"

__all__ = ["SufficiencyObservation", "SufficiencyStatus", "assess_sufficiency"]
