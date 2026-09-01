"""Deterministic C1 pipeline boundaries for EIOS Price Intelligence."""
from __future__ import annotations
from collections.abc import Sequence
from decimal import Decimal
from .models import ComparabilityStatus, EconomicBasisAssessment, EconomicBasisStatus, PriceIntelligenceInput, PriceReference, PriceReferenceAssessment

def identify_references(payload: PriceIntelligenceInput) -> tuple[tuple[str, PriceReference], ...]:
    return tuple((r.source_transaction_id, r) for r in payload.references)

def deduplicate_references(references: Sequence[tuple[str, PriceReference]]) -> tuple[tuple[str, PriceReference], ...]:
    seen:set[str]=set(); unique:list[tuple[str,PriceReference]]=[]
    for reference_id,reference in references:
        if reference_id in seen: continue
        seen.add(reference_id); unique.append((reference_id,reference))
    return tuple(unique)

def assess_comparability(payload: PriceIntelligenceInput, references: Sequence[tuple[str, PriceReference]]) -> tuple[PriceReferenceAssessment, ...]:
    validation_status={v.evidence_id:v.status for v in payload.evidence_validations}; out=[]
    for reference_id,reference in references:
        if reference.article_identity != payload.purchase_operation.article_id: status:ComparabilityStatus="NO_COMPARABLE"; limits=("ARTICLE_IDENTITY_MISMATCH",)
        elif not reference.evidence_refs: status="PENDING"; limits=("MISSING_EVIDENCE_REFERENCE",)
        elif any(validation_status[e] != "VALID" for e in reference.evidence_refs): status="PENDING"; limits=("EVIDENCE_NOT_VALIDATED",)
        else: status="COMPARABLE"; limits=()
        out.append(PriceReferenceAssessment(reference_id=reference_id,comparability=status,normalization_status="PENDING",representativeness="INDETERMINATE",limitation_refs=limits))
    return tuple(out)

def assess_economic_basis(payload: PriceIntelligenceInput, reference: PriceReference, assessment: PriceReferenceAssessment) -> PriceReferenceAssessment:
    if assessment.comparability != "COMPARABLE": return assessment
    basis=payload.normalization_basis
    if basis is None:
        eb=EconomicBasisAssessment(); return assessment.model_copy(update={"economic_basis":eb,"normalization_status":"PENDING","limitation_refs":assessment.limitation_refs+("NORMALIZATION_BASIS_MISSING",)})
    unit:EconomicBasisStatus="RESOLVED" if reference.unit==basis.target_unit else "PENDING"
    currency:EconomicBasisStatus="RESOLVED" if reference.currency==payload.purchase_operation.currency else "PENDING"
    # No transformation is inferred for dimensions not explicitly evidenced by the current C1 basis.
    quantity:EconomicBasisStatus="PENDING"
    tax:EconomicBasisStatus="PENDING" if basis.target_tax_basis is None else "PENDING"
    transport:EconomicBasisStatus="PENDING" if basis.target_transport_basis is None else "PENDING"
    discount:EconomicBasisStatus="PENDING" if basis.target_discount_basis is None else "PENDING"
    surcharge:EconomicBasisStatus="PENDING" if basis.target_surcharge_basis is None else "PENDING"
    commercial:EconomicBasisStatus="PENDING" if basis.target_commercial_basis is None else "PENDING"
    eb=EconomicBasisAssessment(unit=unit,quantity=quantity,currency=currency,tax=tax,transport=transport,discount=discount,surcharge=surcharge,commercial=commercial)
    status="NORMALIZED" if eb.all_resolved else "PENDING"
    limits=assessment.limitation_refs
    if unit=="PENDING": limits+=(("UNIT_CONVERSION_REQUIRED",) if reference.unit!=basis.target_unit else ("UNIT_BASIS_UNRESOLVED",))
    if currency=="PENDING": limits+=("CURRENCY_CONVERSION_REQUIRED",)
    if not eb.all_resolved: limits+=("ECONOMIC_BASIS_INCOMPLETE",)
    return assessment.model_copy(update={"economic_basis":eb,"normalization_status":status,"normalized_unit_price":Decimal(reference.unit_price) if status=="NORMALIZED" else None,"limitation_refs":limits})

def normalize_reference(payload: PriceIntelligenceInput, reference: PriceReference, assessment: PriceReferenceAssessment) -> PriceReferenceAssessment:
    return assess_economic_basis(payload,reference,assessment)

__all__=["assess_comparability","assess_economic_basis","deduplicate_references","identify_references","normalize_reference"]
