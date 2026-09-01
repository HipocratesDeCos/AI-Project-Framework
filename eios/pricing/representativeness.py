"""Deterministic representativeness boundary for EIOS Price Intelligence."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Literal

RepresentativenessStatus = Literal["REPRESENTATIVE", "NON_REPRESENTATIVE", "INDETERMINATE"]

@dataclass(frozen=True)
class RepresentativenessObservation:
    """Observable facts plus their evidence/rule trace."""
    ordinary_market_context: bool | None
    exceptional_condition: bool | None
    material_commercial_distortion: bool | None
    contradiction_material_unresolved: bool | None = False
    evidence_refs: tuple[str, ...] = ()
    rule_reference: str | None = None
    trace_reference: str | None = None
    justification: str | None = None


def assess_representativeness(observation: RepresentativenessObservation) -> RepresentativenessStatus:
    """Assess representativeness without frequency, recency, supplier preference, score or PR feedback."""
    if observation.contradiction_material_unresolved is not False:
        return "INDETERMINATE"
    if observation.exceptional_condition is True or observation.material_commercial_distortion is True:
        status="NON_REPRESENTATIVE"
    elif observation.ordinary_market_context is True and observation.exceptional_condition is False and observation.material_commercial_distortion is False:
        status="REPRESENTATIVE"
    else:
        status="INDETERMINATE"
    if status in {"REPRESENTATIVE","NON_REPRESENTATIVE"} and (not observation.evidence_refs or not observation.rule_reference or not observation.trace_reference):
        return "INDETERMINATE"
    if status=="INDETERMINATE" and not observation.justification:
        return "INDETERMINATE"
    return status

__all__=["RepresentativenessObservation","RepresentativenessStatus","assess_representativeness"]
