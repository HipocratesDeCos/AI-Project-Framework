"""Deterministic C1 pipeline boundaries for EIOS Price Intelligence."""

from __future__ import annotations

from collections.abc import Sequence
from decimal import Decimal

from .models import (
    ComparabilityStatus,
    NormalizationStatus,
    PriceIntelligenceInput,
    PriceReference,
    PriceReferenceAssessment,
)


def identify_references(payload: PriceIntelligenceInput) -> tuple[tuple[str, PriceReference], ...]:
    return tuple((reference.source_transaction_id, reference) for reference in payload.references)


def deduplicate_references(references: Sequence[tuple[str, PriceReference]]) -> tuple[tuple[str, PriceReference], ...]:
    seen: set[str] = set()
    unique: list[tuple[str, PriceReference]] = []
    for reference_id, reference in references:
        if reference_id in seen:
            continue
        seen.add(reference_id)
        unique.append((reference_id, reference))
    return tuple(unique)


def assess_comparability(payload: PriceIntelligenceInput, references: Sequence[tuple[str, PriceReference]]) -> tuple[PriceReferenceAssessment, ...]:
    assessments: list[PriceReferenceAssessment] = []
    target_article_id = payload.purchase_operation.article_id
    validation_status = {item.evidence_id: item.status for item in payload.evidence_validations}
    for reference_id, reference in references:
        if reference.article_identity != target_article_id:
            status: ComparabilityStatus = "NO_COMPARABLE"
            limitations = ("ARTICLE_IDENTITY_MISMATCH",)
        elif not reference.evidence_refs:
            status = "PENDING"
            limitations = ("MISSING_EVIDENCE_REFERENCE",)
        elif any(validation_status[evidence_id] != "VALID" for evidence_id in reference.evidence_refs):
            status = "PENDING"
            limitations = ("EVIDENCE_NOT_VALIDATED",)
        else:
            status = "COMPARABLE"
            limitations = ()
        assessments.append(PriceReferenceAssessment(reference_id=reference_id, comparability=status, normalization_status="PENDING", representativeness="INDETERMINATE", limitation_refs=limitations))
    return tuple(assessments)


def normalize_reference(payload: PriceIntelligenceInput, reference: PriceReference, assessment: PriceReferenceAssessment) -> PriceReferenceAssessment:
    """Normalize only the directly proven EUR/target-unit path; never infer conversions."""
    if assessment.comparability != "COMPARABLE":
        return assessment.model_copy(update={"normalization_status": "PENDING", "normalized_unit_price": None})
    basis = payload.normalization_basis
    if basis is None:
        return assessment.model_copy(update={"normalization_status": "PENDING", "normalized_unit_price": None, "limitation_refs": assessment.limitation_refs + ("NORMALIZATION_BASIS_MISSING",)})
    if reference.currency != payload.purchase_operation.currency:
        return assessment.model_copy(update={"normalization_status": "PENDING", "normalized_unit_price": None, "limitation_refs": assessment.limitation_refs + ("CURRENCY_CONVERSION_REQUIRED",)})
    if reference.unit != basis.target_unit:
        return assessment.model_copy(update={"normalization_status": "PENDING", "normalized_unit_price": None, "limitation_refs": assessment.limitation_refs + ("UNIT_CONVERSION_REQUIRED",)})
    return assessment.model_copy(update={"normalization_status": "NORMALIZED", "normalized_unit_price": Decimal(reference.unit_price)})


__all__ = ["assess_comparability", "deduplicate_references", "identify_references", "normalize_reference"]
