"""Deterministic C1 pipeline for EIOS Price Intelligence."""
from __future__ import annotations
from collections.abc import Sequence
from .aggregation import aggregate_selected_prices
from .models import (ComparabilityStatus,EconomicBasisAssessment,EconomicBasisEvidence,PriceCounts,PriceIntelligenceAssessmentContext,PriceIntelligenceInput,PriceIntelligenceResult,PriceReference,PriceReferenceAssessment)
from .representativeness import RepresentativenessObservation, assess_representativeness
from .sufficiency import assess_sufficiency

def identify_references(payload:PriceIntelligenceInput): return tuple((r.source_transaction_id,r) for r in payload.references)
def deduplicate_references(references:Sequence[tuple[str,PriceReference]]):
    seen:set[str]=set();unique=[]
    for reference_id,reference in references:
        if reference_id not in seen:seen.add(reference_id);unique.append((reference_id,reference))
    return tuple(unique)
def _validate_context(context:PriceIntelligenceAssessmentContext,reference_ids:set[str])->None:
    unknown=(set(context.temporal)|set(context.representativeness))-reference_ids
    if unknown:raise ValueError("AssessmentContext contiene referencias inexistentes")
def assess_comparability(payload:PriceIntelligenceInput,references:Sequence[tuple[str,PriceReference]]):
    validation_status={v.evidence_id:v.status for v in payload.evidence_validations};out=[]
    for reference_id,reference in references:
        if reference.article_identity!=payload.purchase_operation.article_id:status:ComparabilityStatus="NO_COMPARABLE";limits=("ARTICLE_IDENTITY_MISMATCH",)
        elif not reference.evidence_refs:status="PENDING";limits=("MISSING_EVIDENCE_REFERENCE",)
        elif any(validation_status[e]!="VALID" for e in reference.evidence_refs):status="PENDING";limits=("EVIDENCE_NOT_VALIDATED",)
        else:status="COMPARABLE";limits=()
        out.append(PriceReferenceAssessment(reference_id=reference_id,comparability=status,limitation_refs=limits))
    return tuple(out)
def _economic_records(payload:PriceIntelligenceInput,reference_id:str)->tuple[EconomicBasisEvidence,...]: return tuple(r for r in payload.economic_basis_evidence if r.reference_id==reference_id)
def assess_economic_basis(payload:PriceIntelligenceInput,reference:PriceReference,assessment:PriceReferenceAssessment):
    if assessment.comparability!="COMPARABLE":return assessment
    basis=payload.normalization_basis;records=_economic_records(payload,reference.source_transaction_id);eb=EconomicBasisAssessment(records=records);limits=assessment.limitation_refs
    if basis is None:limits+=("NORMALIZATION_BASIS_MISSING",)
    unit_ok=basis is not None and reference.unit==basis.target_unit;currency_ok=basis is not None and reference.currency==payload.purchase_operation.currency
    if not unit_ok:limits+=("UNIT_CONVERSION_REQUIRED",)
    if not currency_ok:limits+=("CURRENCY_CONVERSION_REQUIRED",)
    if not eb.all_resolved:limits+=("ECONOMIC_BASIS_INCOMPLETE",)
    status="NORMALIZED" if basis is not None and eb.all_resolved and unit_ok and currency_ok else "PENDING"
    return assessment.model_copy(update={"economic_basis":eb,"normalization_status":status,"normalized_unit_price":reference.unit_price if status=="NORMALIZED" else None,"limitation_refs":limits})
def normalize_reference(payload:PriceIntelligenceInput,reference:PriceReference,assessment:PriceReferenceAssessment): return assess_economic_basis(payload,reference,assessment)
def assess_temporality(assessment:PriceReferenceAssessment,*,temporal_rule_reference:str|None=None,eligible:bool|None=None):
    if assessment.normalization_status!="NORMALIZED":return assessment.model_copy(update={"temporal_status":"INDETERMINATE"})
    if temporal_rule_reference is None or eligible is None:return assessment.model_copy(update={"temporal_status":"INDETERMINATE","temporal_rule_reference":temporal_rule_reference,"limitation_refs":assessment.limitation_refs+("TEMPORAL_RULE_UNAVAILABLE",)})
    return assessment.model_copy(update={"temporal_status":"ELIGIBLE" if eligible else "INELIGIBLE","temporal_rule_reference":temporal_rule_reference})
def assess_representativeness_for_reference(assessment:PriceReferenceAssessment,observation:RepresentativenessObservation)->PriceReferenceAssessment:return assessment.model_copy(update={"representativeness":assess_representativeness(observation)})
def select_references(assessments:Sequence[PriceReferenceAssessment])->tuple[str,...]: return tuple(a.reference_id for a in assessments if a.comparability=="COMPARABLE" and a.normalization_status=="NORMALIZED" and a.temporal_status=="ELIGIBLE" and a.representativeness=="REPRESENTATIVE")
def run_price_intelligence(payload:PriceIntelligenceInput,context:PriceIntelligenceAssessmentContext)->PriceIntelligenceResult:
    identified=identify_references(payload);unique=deduplicate_references(identified);_validate_context(context,{rid for rid,_ in unique});assessments={a.reference_id:a for a in assess_comparability(payload,unique)}
    for rid,ref in unique:
        assessments[rid]=normalize_reference(payload,ref,assessments[rid]);temporal=context.temporal.get(rid)
        if temporal is None: assessments[rid]=assess_temporality(assessments[rid])
        elif temporal[0]=="ELIGIBLE": assessments[rid]=assess_temporality(assessments[rid],temporal_rule_reference=temporal[1],eligible=True)
        elif temporal[0]=="INELIGIBLE": assessments[rid]=assess_temporality(assessments[rid],temporal_rule_reference=temporal[1],eligible=False)
        else: assessments[rid]=assess_temporality(assessments[rid],temporal_rule_reference=temporal[1],eligible=None)
        observation=context.representativeness.get(rid)
        if observation is not None: assessments[rid]=assess_representativeness_for_reference(assessments[rid],observation)
    ordered=tuple(assessments[rid] for rid,_ in unique);selected=select_references(ordered);obs_ids=tuple(context.sufficiency.selected_reference_ids)
    if set(obs_ids)!=set(selected):raise ValueError("SufficiencyObservation no corresponde al conjunto seleccionado")
    values=tuple(assessments[rid].normalized_unit_price for rid in selected if assessments[rid].normalized_unit_price is not None);status=assess_sufficiency(len(selected),context.sufficiency);pr_value,method=aggregate_selected_prices(values) if selected else (None,"MEDIAN_UNWEIGHTED");limitations=list(dict.fromkeys(x for a in ordered for x in a.limitation_refs));limitations.extend(x for x in context.sufficiency.methodological_limitations if x not in limitations);traces=list(dict.fromkeys(x for a in ordered for x in (a.temporal_rule_reference,) if x));traces.extend(x for x in context.sufficiency.evidence_refs+(context.sufficiency.rule_reference,context.sufficiency.trace_reference) if x and x not in traces)
    return PriceIntelligenceResult(decision_id=payload.decision_context.decision_id,scenario_id=payload.decision_context.scenario_id,data_snapshot_id=payload.decision_context.data_snapshot_id,methodology_version=payload.methodology_version,pr_value=pr_value,currency=payload.purchase_operation.currency if pr_value is not None else None,sufficiency_status=status,pr_status={"SUFFICIENT":"PR_AVAILABLE","LIMITED":"PR_LIMITED","NOT_JUSTIFIABLE":"PR_NOT_JUSTIFIABLE"}[status],pr_limitations=tuple(limitations),reference_set=selected,counts=PriceCounts(n_raw=len(identified),n_unique=len(unique),n_comparable=sum(a.comparability=="COMPARABLE" for a in ordered),n_representative=sum(a.comparability=="COMPARABLE" and a.representativeness=="REPRESENTATIVE" for a in ordered),n_selected=len(selected)),aggregation_method=method,trace_references=tuple(traces))
__all__=["assess_comparability","assess_economic_basis","assess_representativeness_for_reference","assess_temporality","deduplicate_references","identify_references","normalize_reference","run_price_intelligence","select_references"]