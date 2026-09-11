"""Supplier Evidence Core factual contracts and deterministic evaluation."""
from .engine import evaluate_supplier_evidence
from .models import (
    CandidateResolution,
    ExternalSupplierMetric,
    StructuralComparisonRequest,
    StructuralComparisonResult,
    SupplierCandidateEvidence,
    SupplierDataIssueRef,
    SupplierEvidenceInput,
    SupplierEvidenceResult,
    SupplierHistoricalFact,
    SupplierItemRef,
    SupplierObservation,
    SupplierResultIdentity,
    SupplierSignal,
    SUPPLIER_EVIDENCE_METHODOLOGY_VERSION,
)

__all__ = [
    "CandidateResolution",
    "ExternalSupplierMetric",
    "StructuralComparisonRequest",
    "StructuralComparisonResult",
    "SupplierCandidateEvidence",
    "SupplierDataIssueRef",
    "SupplierEvidenceInput",
    "SupplierEvidenceResult",
    "SupplierHistoricalFact",
    "SupplierItemRef",
    "SupplierObservation",
    "SupplierResultIdentity",
    "SupplierSignal",
    "SUPPLIER_EVIDENCE_METHODOLOGY_VERSION",
    "evaluate_supplier_evidence",
]
