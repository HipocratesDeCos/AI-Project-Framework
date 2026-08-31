"""Deterministic Quality & Trust Gate for the EIOS MVP.

The gate evaluates supplied quality-control findings. It does not create or
modify C0, evidence, rules, parameters, versioning, or business decisions.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


QualityStatus = Literal["APTO", "APTO_CON_ADVERTENCIAS", "NO_APTO"]
QualityConfidence = Literal["ALTA", "MEDIA", "BAJA"]


@dataclass(frozen=True)
class QualityCheck:
    """Result of one applicable QTG control.

    ``satisfied`` is None when the control cannot be evaluated. A failed
    critical control blocks continuation; a failed non-critical control is a
    warning. ``material`` indicates a relevant limitation that lowers
    confidence without being a blocker.
    """

    control: str
    satisfied: bool | None
    critical: bool = False
    material: bool = False
    reason: str = ""
    evidence_refs: tuple[str, ...] = ()
    applicable: bool = True


@dataclass(frozen=True)
class QualityTrustResult:
    """Normative QTG result with deterministic state/confidence."""

    status: QualityStatus
    confidence: QualityConfidence
    checks: tuple[QualityCheck, ...]


def evaluate_quality(checks: list[QualityCheck] | tuple[QualityCheck, ...]) -> QualityTrustResult:
    """Evaluate QTG using the normative precedence matrix.

    Precedence:
    NO_APTO > APTO_CON_ADVERTENCIAS > APTO.

    Confidence combinations are deliberately constrained:
    APTO -> ALTA
    APTO_CON_ADVERTENCIAS -> MEDIA or BAJA
    NO_APTO -> BAJA
    """
    applicable = tuple(check for check in checks if check.applicable)

    if any(check.satisfied is not True and check.critical for check in applicable):
        return QualityTrustResult("NO_APTO", "BAJA", applicable)

    warnings = tuple(check for check in applicable if check.satisfied is not True)
    if warnings:
        confidence: QualityConfidence = (
            "BAJA" if any(check.material for check in warnings) else "MEDIA"
        )
        return QualityTrustResult("APTO_CON_ADVERTENCIAS", confidence, applicable)

    return QualityTrustResult("APTO", "ALTA", applicable)


__all__ = [
    "QualityCheck",
    "QualityConfidence",
    "QualityStatus",
    "QualityTrustResult",
    "evaluate_quality",
]
