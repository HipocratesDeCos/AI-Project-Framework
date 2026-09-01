"""Deterministic representativeness boundary for EIOS Price Intelligence."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Literal

RepresentativenessStatus = Literal["REPRESENTATIVE", "NON_REPRESENTATIVE", "INDETERMINATE"]

@dataclass(frozen=True)
class RepresentativenessObservation:
    """Observable, auditable facts used to assess ordinary-market representativeness."""
    ordinary_market_context: bool | None
    exceptional_condition: bool | None
    material_commercial_distortion: bool | None


def assess_representativeness(observation: RepresentativenessObservation) -> RepresentativenessStatus:
    """Assess representativeness without frequency, recency, supplier preference, score or PR feedback."""
    if observation.exceptional_condition is True or observation.material_commercial_distortion is True:
        return "NON_REPRESENTATIVE"
    if observation.ordinary_market_context is True and observation.exceptional_condition is False and observation.material_commercial_distortion is False:
        return "REPRESENTATIVE"
    return "INDETERMINATE"

__all__ = ["RepresentativenessObservation", "RepresentativenessStatus", "assess_representativeness"]
