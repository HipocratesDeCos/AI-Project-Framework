"""Deterministic C1 pipeline boundaries for EIOS Price Intelligence."""

from __future__ import annotations

from collections.abc import Sequence

from .models import (
    ComparabilityStatus,
    PriceIntelligenceInput,
    PriceReference,
    PriceReferenceAssessment,
)


def identify_references(
    payload: PriceIntelligenceInput,
) -> tuple[tuple[str, PriceReference], ...]:
    """Expose source transaction identity without creating new business identity."""
    return tuple((reference.source_transaction_id, reference) for reference in payload.references)


def deduplicate_references(
    references: Sequence[tuple[str, PriceReference]],
) -> tuple[tuple[str, PriceReference], ...]:
    """Remove repeated representations of the same source transaction deterministically."""
    seen: set[str] = set()
    unique: list[tuple[str, PriceReference]] = []
    for reference_id, reference in references:
        if reference_id in seen:
            continue
        seen.add(reference_id)
        unique.append((reference_id, reference))
    return tuple(unique)


def assess_comparability(
    payload: PriceIntelligenceInput,
    references: Sequence[tuple[str, PriceReference]],
) -> tuple[PriceReferenceAssessment, ...]:
    """Apply only the closed MVP identity/evidence gate for comparability.

    A VALID EvidenceValidation is required before this gate can return
    COMPARABLE. Unit, quantity basis, currency and commercial-condition
    transformations remain the responsibility of the subsequent authorized
    normalization stage.
    """
    assessments: list[PriceReferenceAssessment] = []
    target_article_id = payload.purchase_operation.article_id
    validation_status = {
        item.evidence_id: item.status for item in payload.evidence_validations
    }

    for reference_id, reference in references:
        if reference.article_identity != target_article_id:
            status: ComparabilityStatus = "NO_COMPARABLE"
            limitation_refs = ("ARTICLE_IDENTITY_MISMATCH",)
        elif not reference.evidence_refs:
            status = "PENDING"
            limitation_refs = ("MISSING_EVIDENCE_REFERENCE",)
        elif any(validation_status[evidence_id] != "VALID" for evidence_id in reference.evidence_refs):
            status = "PENDING"
            limitation_refs = ("EVIDENCE_NOT_VALIDATED",)
        else:
            status = "COMPARABLE"
            limitation_refs = ()

        assessments.append(
            PriceReferenceAssessment(
                reference_id=reference_id,
                comparability=status,
                representativeness="INDETERMINATE",
                limitation_refs=limitation_refs,
            )
        )

    return tuple(assessments)


__all__ = [
    "assess_comparability",
    "deduplicate_references",
    "identify_references",
]
