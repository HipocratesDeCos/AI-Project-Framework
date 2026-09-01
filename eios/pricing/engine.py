"""Deterministic C1 pipeline boundaries for EIOS Price Intelligence."""
from __future__ import annotations
from collections.abc import Sequence
from .models import ComparabilityStatus, EconomicBasisAssessment, EconomicBasisStatus, PriceIntelligenceInput, PriceReference, PriceReferenceAssessment

def identify_references(payload: PriceIntelligenceInput):
    return tuple((r.source_transaction_id, r) for r in payload.references)

def deduplicate_references(references: Sequence[tuple[str, PriceReference]]):
    seen:set[str]=set(); unique=[]
    for reference_id, reference in references:
        if reference_id not in seen: seen.add(reference_id); unique.append((reference_id,reference))
    return tuple(unique)

def assess_comparability(payload: PriceIntelligenceInput, references: Sequence[tuple[str, PriceReference]]):
    validation_status={v.evidence_id:v.status for v in payload.evidence_validations}; out=[]
    for reference_id,reference in references:
        if reference.article_identity != payload.purchase_operation.article_id: status:ComparabilityStatus="NO_COMPARABLE"; limits=("ARTICLE_IDENTITY_MISMATCH",)
        elif not reference.evidence_refs: status="PENDING"; limits=("MISSING_EVIDENCE_REFERENCE",)
        elif any(validation_status[e] != "VALID" for e in reference.evidence_refs): status="PENDING"; limits=("EVIDENCE_NOT_VALIDATED",)
        else: status="COMPARABLE"; limits=()
        out.append(PriceReferenceAssessment(reference_id=reference_id,comparability=status,normalization_status="PENDING",representativeness="INDETERMINATE",limitation_refs=limits))
    return tuple(out)

def assess_economic_basis(payload: PriceIntelligenceInput, reference: PriceReference, assessment: PriceReferenceAssessment):
    if assessment.comparability != "COMPARABLE": return assessment
    basis=payload.normalization_basis
    if basis is None:
        return assessment.model_copy(update={"economic_basis":EconomicBasisAssessment(),"normalization_status":"PENDING","limitation_refs":assessment.limitation_refs+("NORMALIZATION_BASIS_MISSING",)})
    unit:EconomicBasisStatus="RESOLVED" if reference.unit==basis.target_unit else "PENDING"
    currency:EconomicBasisStatus="RESOLVED" if reference.currency==payload.purchase_operation.currency else "PENDING"
    eb=EconomicBasisAssessment(unit=unit,currency=currency)
    limits=assessment.limitation_refs
    if unit=="PENDING": limits+=("UNIT_CONVERSION_REQUIRED",)
    if currency=="PENDING": limits+=("CURRENCY_CONVERSION_REQUIRED",)
    limits+=(("ECONOMIC_BASIS_INCOMPLETE",) if not eb.all_resolved else ())
    status="NORMALIZED" if eb.all_resolved else "PENDING"
    return assessment.model_copy(update={"economic_basis":eb,"normalization_status":status,"normalized_unit_price":reference.unit_price if status=="NORMALIZED" else None,"limitation_refs":limits})

def normalize_reference(payload: PriceIntelligenceInput, reference: PriceReference, assessment: PriceReferenceAssessment):
    return assess_economic_basis(payload,reference,assessment)

__all__=["assess_comparability","assess_economic_basis","deduplicate_references","identify_references","normalize_reference"]
