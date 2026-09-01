"""Deterministic C1 pipeline boundaries for EIOS Price Intelligence."""
from __future__ import annotations
from collections.abc import Sequence
from .models import ComparabilityStatus, EconomicBasisAssessment, EconomicBasisEvidence, EconomicBasisStatus, EconomicDimension, PriceIntelligenceInput, PriceReference, PriceReferenceAssessment, TemporalStatus

_EXPECTED_DIMENSIONS: tuple[EconomicDimension,...]=("UNIT","QUANTITY","CURRENCY","TAX","TRANSPORT","DISCOUNT","SURCHARGE","COMMERCIAL")

def identify_references(payload: PriceIntelligenceInput): return tuple((r.source_transaction_id,r) for r in payload.references)

def deduplicate_references(references: Sequence[tuple[str,PriceReference]]):
    seen:set[str]=set();unique=[]
    for reference_id,reference in references:
        if reference_id not in seen:seen.add(reference_id);unique.append((reference_id,reference))
    return tuple(unique)

def assess_comparability(payload: PriceIntelligenceInput,references: Sequence[tuple[str,PriceReference]]):
    validation_status={v.evidence_id:v.status for v in payload.evidence_validations};out=[]
    for reference_id,reference in references:
        if reference.article_identity!=payload.purchase_operation.article_id:status:ComparabilityStatus="NO_COMPARABLE";limits=("ARTICLE_IDENTITY_MISMATCH",)
        elif not reference.evidence_refs:status="PENDING";limits=("MISSING_EVIDENCE_REFERENCE",)
        elif any(validation_status[e]!="VALID" for e in reference.evidence_refs):status="PENDING";limits=("EVIDENCE_NOT_VALIDATED",)
        else:status="COMPARABLE";limits=()
        out.append(PriceReferenceAssessment(reference_id=reference_id,comparability=status,limitation_refs=limits))
    return tuple(out)

def _economic_records(payload: PriceIntelligenceInput, reference_id: str) -> tuple[EconomicBasisEvidence,...]:
    records=tuple(r for r in payload.economic_basis_evidence if r.reference_id==reference_id)
    by_dimension={r.dimension for r in records}
    missing=tuple(d for d in _EXPECTED_DIMENSIONS if d not in by_dimension)
    return records+tuple(EconomicBasisEvidence(reference_id=reference_id,dimension=d,status="PENDING",justification="ECONOMIC_BASIS_EVIDENCE_MISSING") for d in missing)

def assess_economic_basis(payload: PriceIntelligenceInput,reference: PriceReference,assessment: PriceReferenceAssessment):
    if assessment.comparability!="COMPARABLE":return assessment
    basis=payload.normalization_basis
    if basis is None:return assessment.model_copy(update={"economic_basis":EconomicBasisAssessment(records=_economic_records(payload,reference.source_transaction_id)),"normalization_status":"PENDING","limitation_refs":assessment.limitation_refs+("NORMALIZATION_BASIS_MISSING",)})
    records=_economic_records(payload,reference.source_transaction_id)
    # Duplicate dimension records are treated as unresolved rather than selecting one silently.
    counts={d:sum(r.dimension==d for r in records) for d in _EXPECTED_DIMENSIONS}
    if any(n>1 for n in counts.values()):
        records=tuple(r.model_copy(update={"status":"PENDING","justification":"DUPLICATE_ECONOMIC_DIMENSION_RECORDS"}) if counts[r.dimension]>1 else r for r in records)
    eb=EconomicBasisAssessment(records=records);limits=assessment.limitation_refs
    status="NORMALIZED" if eb.all_resolved else "PENDING"
    if reference.unit!=basis.target_unit and not any(r.dimension=="UNIT" and r.status=="RESOLVED" for r in records):limits+=("UNIT_CONVERSION_REQUIRED",)
    if reference.currency!=payload.purchase_operation.currency and not any(r.dimension=="CURRENCY" and r.status=="RESOLVED" for r in records):limits+=("CURRENCY_CONVERSION_REQUIRED",)
    if not eb.all_resolved:limits+=("ECONOMIC_BASIS_INCOMPLETE",)
    return assessment.model_copy(update={"economic_basis":eb,"normalization_status":status,"normalized_unit_price":reference.unit_price if status=="NORMALIZED" else None,"limitation_refs":limits})

def normalize_reference(payload: PriceIntelligenceInput,reference: PriceReference,assessment: PriceReferenceAssessment):return assess_economic_basis(payload,reference,assessment)

def assess_temporality(assessment: PriceReferenceAssessment,*,temporal_rule_reference:str|None=None,eligible:bool|None=None):
    if assessment.normalization_status!="NORMALIZED":return assessment.model_copy(update={"temporal_status":"INDETERMINATE"})
    if temporal_rule_reference is None or eligible is None:return assessment.model_copy(update={"temporal_status":"INDETERMINATE","temporal_rule_reference":temporal_rule_reference,"limitation_refs":assessment.limitation_refs+("TEMPORAL_RULE_UNAVAILABLE",)})
    status:TemporalStatus="ELIGIBLE" if eligible else "INELIGIBLE"
    return assessment.model_copy(update={"temporal_status":status,"temporal_rule_reference":temporal_rule_reference})

def select_references(assessments: Sequence[PriceReferenceAssessment])->tuple[str,...]:return tuple(a.reference_id for a in assessments if a.comparability=="COMPARABLE" and a.normalization_status=="NORMALIZED" and a.temporal_status=="ELIGIBLE" and a.representativeness=="REPRESENTATIVE")

__all__=["assess_comparability","assess_economic_basis","assess_temporality","deduplicate_references","identify_references","normalize_reference","select_references"]
