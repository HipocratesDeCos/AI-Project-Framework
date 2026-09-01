"""Deterministic C1 pipeline skeleton for EIOS Price Intelligence."""

from __future__ import annotations

from collections.abc import Sequence

from .models import PriceIntelligenceInput, PriceReferenceAssessment


def identify_references(
    payload: PriceIntelligenceInput,
) -> tuple[tuple[str, object], ...]:
    """Expose deterministic reference identities without creating new business identity."""
    return tuple((reference.source_transaction_id, reference) for reference in payload.references)


def deduplicate_references(
    references: Sequence[tuple[str, object]],
) -> tuple[tuple[str, object], ...]:
    """Remove repeated representations of the same source transaction deterministically."""
    seen: set[str] = set()
    unique: list[tuple[str, object]] = []
    for reference_id, reference in references:
        if reference_id in seen:
            continue
        seen.add(reference_id)
        unique.append((reference_id, reference))
    return tuple(unique)


def assess_comparability(
    references: Sequence[tuple[str, object]],
) -> tuple[PriceReferenceAssessment, ...]:
    """Placeholder boundary: comparability rules must be implemented from the methodology."""
    raise NotImplementedError("Comparability rules are not yet materialized")


__all__ = [
    "assess_comparability",
    "deduplicate_references",
    "identify_references",
]
