"""Deterministic validation primitives for the EIOS C0 pipeline."""

from __future__ import annotations

from datetime import date

from .models import Evidence, EvidenceValidation, PurchaseOperation, QualityStatus


def validate_purchase_operation(
    purchase: PurchaseOperation,
    *,
    as_of: date | None = None,
) -> QualityStatus:
    """Retain the pre-C0 input-quality gate for backward compatibility."""
    reference_date = as_of or date.today()
    reasons: list[str] = []

    if purchase.operation_date > reference_date:
        reasons.append("La fecha de operación no puede ser futura")

    if purchase.quantity <= 0:
        reasons.append("La cantidad debe ser mayor que cero")

    if purchase.unit_price < 0:
        reasons.append("El precio unitario no puede ser negativo")

    if reasons:
        return QualityStatus(status="FAIL", reasons=reasons)

    return QualityStatus(status="PASS", score=1)


def validate_evidence(evidence: Evidence) -> EvidenceValidation:
    """Validate whether an evidence item can support a C0 rule assessment.

    GAP is intentionally valid as a representation of missing evidence, but
    it is not valid evidence for an assessment that requires demonstrated
    support. This distinction is what prevents absence of evidence from being
    converted into FALSE.
    """
    if evidence.state == "DEMONSTRATED":
        return EvidenceValidation(
            evidence_id=evidence.evidence_id,
            status="VALID",
            reason="Evidencia demostrada y trazable",
        )

    return EvidenceValidation(
        evidence_id=evidence.evidence_id,
        status="INVALID",
        reason="Evidencia en GAP; no demuestra el requisito",
    )


__all__ = ["validate_evidence", "validate_purchase_operation"]
