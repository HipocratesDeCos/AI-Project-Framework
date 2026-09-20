"""Provenance-safe reuse boundary for EIOS Profitability Core v0.1."""
from __future__ import annotations

from dataclasses import dataclass

from .engine import calculate_profitability
from .models import ProfitabilityInput, ProfitabilityResult


class ProfitabilityProvenanceError(ValueError):
    """Technical integrity failure at the Profitability reuse boundary."""


@dataclass(frozen=True)
class ProvenancedProfitabilityExecution:
    """Profitability input snapshot bound to its exact recomputed result."""

    profitability_input: ProfitabilityInput
    profitability_result: ProfitabilityResult


def _validated_snapshot(payload: ProfitabilityInput) -> ProfitabilityInput:
    if not isinstance(payload, ProfitabilityInput):
        raise TypeError("profitability_input debe ser ProfitabilityInput")
    try:
        # Reconstruct from primitive model data so nested-model mutations cannot
        # bypass ProfitabilityInput validators at the provenance boundary.
        return ProfitabilityInput.model_validate(
            payload.model_dump(mode="python")
        )
    except Exception as exc:
        raise ProfitabilityProvenanceError(
            "ProfitabilityInput no supera la revalidación de provenance"
        ) from exc


def run_provenanced_profitability(
    profitability_input: ProfitabilityInput,
) -> ProvenancedProfitabilityExecution:
    """Freeze, revalidate and execute Profitability Core from one complete input."""
    snapshot = _validated_snapshot(profitability_input)
    result = calculate_profitability(snapshot)
    return ProvenancedProfitabilityExecution(
        profitability_input=snapshot,
        profitability_result=result,
    )


def validate_provenanced_profitability_execution(
    execution: ProvenancedProfitabilityExecution,
) -> None:
    """Reject detached, forged or internally mutated Profitability executions."""
    if not isinstance(execution, ProvenancedProfitabilityExecution):
        raise TypeError(
            "execution debe ser ProvenancedProfitabilityExecution"
        )

    snapshot = _validated_snapshot(execution.profitability_input)
    expected = calculate_profitability(snapshot)
    if expected != execution.profitability_result:
        raise ProfitabilityProvenanceError(
            "ProfitabilityResult no coincide con la recomputación provenance-safe"
        )


__all__ = [
    "ProfitabilityProvenanceError",
    "ProvenancedProfitabilityExecution",
    "run_provenanced_profitability",
    "validate_provenanced_profitability_execution",
]
