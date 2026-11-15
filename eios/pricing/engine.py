"""Deterministic C1 pipeline for EIOS Price Intelligence."""
from __future__ import annotations
from collections.abc import Sequence
from decimal import Decimal, InvalidOperation, ROUND_HALF_EVEN, localcontext
from .aggregation import aggregate_selected_prices
from .models import (ComparabilityStatus,EconomicBasisAssessment,EconomicBasisEvidence,NormalizationRecord,PriceCounts,PriceIntelligenceAssessmentContext,PriceIntelligenceInput,PriceIntelligenceResult,PriceReference,PriceReferenceAssessment)
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
def assess_economic_basis(
    payload: PriceIntelligenceInput,
    reference: PriceReference,
    assessment: PriceReferenceAssessment,
) -> PriceReferenceAssessment:
    if assessment.comparability != "COMPARABLE":
        return assessment

    basis = payload.normalization_basis
    records = _economic_records(payload, reference.source_transaction_id)
    economic_basis = EconomicBasisAssessment(records=records)
    limitations = list(assessment.limitation_refs)

    target_unit = basis.target_unit if basis is not None else reference.unit
    required = {}
    if reference.unit != target_unit:
        required["UNIT"] = (reference.unit, target_unit)
        limitations.append("UNIT_CONVERSION_REQUIRED")
    if reference.currency != payload.purchase_operation.currency:
        required["CURRENCY"] = (
            reference.currency, payload.purchase_operation.currency
        )
        limitations.append("CURRENCY_CONVERSION_REQUIRED")
    if required and basis is None:
        limitations.append("NORMALIZATION_BASIS_MISSING")

    # Evidence declarations never perform a numeric conversion by themselves.
    # The underlying records may document additional economic dimensions.
    if records and not economic_basis.all_resolved:
        limitations.append("ECONOMIC_BASIS_INCOMPLETE")

    dimension_records = {
        item.dimension: item for item in records
    }
    instructions = {
        item.dimension: item
        for item in payload.price_conversion_instructions
        if item.reference_id == reference.source_transaction_id
    }
    validation_status = {
        item.evidence_id: item.status for item in payload.evidence_validations
    }

    # Material commercial dimensions require explicit documentary equivalence.
    # Numeric adjustments for these dimensions are NOT implemented by this gate.
    target_fields = {
        "TAX": "target_tax_basis",
        "TRANSPORT": "target_transport_basis",
        "DISCOUNT": "target_discount_basis",
        "SURCHARGE": "target_surcharge_basis",
        "COMMERCIAL": "target_commercial_basis",
    }
    declared_targets = {
        dimension: getattr(basis, field)
        for dimension, field in target_fields.items()
        if basis is not None and getattr(basis, field) is not None
    }
    material_dimensions = {"QUANTITY", *target_fields.keys()}
    comparisons = {
        item.dimension: item
        for item in payload.economic_basis_comparisons
        if item.reference_id == reference.source_transaction_id
    }
    material_required = (
        set(declared_targets)
        | set(comparisons)
        | {item.dimension for item in records if item.dimension in material_dimensions}
    )
    if reference.commercial_conditions is not None:
        material_required.add("COMMERCIAL")

    for dimension in sorted(material_required):
        proof = comparisons.get(dimension)
        evidence = dimension_records.get(dimension)
        if proof is None:
            limitations.append("ECONOMIC_DIMENSION_UNVERIFIED:" + dimension)
            continue
        if dimension == "QUANTITY":
            if (
                proof.source_basis != format(reference.quantity, "f")
                or proof.target_basis != format(payload.purchase_operation.quantity, "f")
            ):
                limitations.append("ECONOMIC_DIMENSION_CONTEXT_MISMATCH:QUANTITY")
        elif dimension in declared_targets:
            if proof.target_basis != declared_targets[dimension]:
                limitations.append("ECONOMIC_DIMENSION_CONTEXT_MISMATCH:" + dimension)
        else:
            # A comparison lacking an operation target is not independently
            # anchored to the intended economic price basis.
            limitations.append("ECONOMIC_DIMENSION_TARGET_MISSING:" + dimension)
        if dimension == "COMMERCIAL" and reference.commercial_conditions is not None:
            if proof.source_basis != reference.commercial_conditions:
                limitations.append("ECONOMIC_DIMENSION_CONTEXT_MISMATCH:COMMERCIAL")

        if proof.status not in {"EQUIVALENT", "NOT_APPLICABLE"}:
            limitations.append("ECONOMIC_DIMENSION_UNRESOLVED:" + dimension)
        if proof.status == "NOT_APPLICABLE" and dimension in declared_targets:
            limitations.append("ECONOMIC_DIMENSION_INAPPLICABLE_CONFLICT:" + dimension)

        expected_evidence_state = (
            "RESOLVED" if proof.status == "EQUIVALENT" else "NOT_APPLICABLE"
        )
        if (
            evidence is None
            or evidence.status != expected_evidence_state
            or proof.rule_reference != evidence.rule_reference
            or proof.trace_reference != evidence.trace_reference
            or not set(proof.evidence_refs).issubset(evidence.evidence_refs)
            or any(validation_status[ref] != "VALID" for ref in proof.evidence_refs)
            or any(validation_status[ref] != "VALID" for ref in evidence.evidence_refs)
        ):
            limitations.append("ECONOMIC_DIMENSION_EVIDENCE_MISMATCH:" + dimension)

    if set(instructions) - set(required):
        limitations.append("UNNECESSARY_CONVERSION_INSTRUCTION")
    if required and not set(required).issubset(dimension_records):
        limitations.append("ECONOMIC_BASIS_INCOMPLETE")
    if required and not set(required).issubset(instructions):
        limitations.append("NORMALIZATION_TRANSFORMATION_NOT_EXECUTED")

    # Each numerical instruction must match its source, target, historical date
    # and the same RESOLVED economic evidence that authorizes its dimension.
    accepted = {}
    for dimension, (source_code, target_code) in required.items():
        instruction = instructions.get(dimension)
        evidence = dimension_records.get(dimension)
        if instruction is None:
            continue
        if (
            instruction.source_code != source_code
            or instruction.target_code != target_code
            or instruction.effective_date != reference.operation_date
        ):
            limitations.append("CONVERSION_CONTEXT_MISMATCH")
            continue
        if evidence is None or evidence.status != "RESOLVED":
            limitations.append("ECONOMIC_BASIS_INCOMPLETE")
            continue
        if (
            instruction.rule_reference != evidence.rule_reference
            or instruction.trace_reference != evidence.trace_reference
            or not set(instruction.evidence_refs).issubset(evidence.evidence_refs)
            or any(validation_status[ref] != "VALID" for ref in instruction.evidence_refs)
            or any(validation_status[ref] != "VALID" for ref in evidence.evidence_refs)
        ):
            limitations.append("CONVERSION_EVIDENCE_MISMATCH")
            continue
        accepted[dimension] = instruction

    if required and set(accepted) != set(required):
        limitations.append("NORMALIZATION_TRANSFORMATION_NOT_EXECUTED")

    blocking = (
        (required and basis is None)
        or "ECONOMIC_BASIS_INCOMPLETE" in limitations
        or "UNNECESSARY_CONVERSION_INSTRUCTION" in limitations
        or "CONVERSION_CONTEXT_MISMATCH" in limitations
        or "CONVERSION_EVIDENCE_MISMATCH" in limitations
        or "NORMALIZATION_TRANSFORMATION_NOT_EXECUTED" in limitations
        or any(value.startswith("ECONOMIC_DIMENSION_") for value in limitations)
    )
    normalization = []
    normalized_price = None
    if not blocking:
        try:
            with localcontext() as decimal_context:
                decimal_context.prec = 50
                value = reference.unit_price
                for dimension in ("UNIT", "CURRENCY"):
                    instruction = accepted.get(dimension)
                    if instruction is None:
                        continue
                    converted = value * instruction.factor
                    normalization.append(
                        NormalizationRecord(
                            field=dimension,
                            original_value=format(value, "f"),
                            normalized_value=format(converted, "f"),
                            rule_reference=instruction.rule_reference,
                            trace_reference=instruction.trace_reference,
                        )
                    )
                    value = converted
                # Unchanged, already-comparable prices preserve their exact
                # numeric representation for reference-demo reproducibility.
                # Only performed conversions need a new four-decimal result.
                normalized_price = (
                    value.quantize(Decimal("0.0001"), rounding=ROUND_HALF_EVEN)
                    if normalization else value
                )
        except InvalidOperation:
            normalization = []
            limitations.append("CONVERSION_NUMERIC_LIMIT")

    status = "NORMALIZED" if normalized_price is not None else "PENDING"
    return assessment.model_copy(
        update={
            "economic_basis": economic_basis,
            "normalization_status": status,
            "normalized_unit_price": normalized_price,
            "normalization": tuple(normalization),
            "limitation_refs": tuple(dict.fromkeys(limitations)),
        }
    )
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
    # Preserve the exact authority and source trail of executed conversions.
    for item in ordered:
        for record in item.normalization:
            for ref in (record.rule_reference, record.trace_reference):
                if ref not in traces:
                    traces.append(ref)
    for instruction in payload.price_conversion_instructions:
        if instruction.reference_id not in selected:
            continue
        for ref in (instruction.source_ref,) + instruction.evidence_refs:
            if ref not in traces:
                traces.append(ref)
    for proof in payload.economic_basis_comparisons:
        if proof.reference_id not in selected:
            continue
        for ref in (proof.source_ref, proof.rule_reference, proof.trace_reference) + proof.evidence_refs:
            if ref not in traces:
                traces.append(ref)
    return PriceIntelligenceResult(decision_id=payload.decision_context.decision_id,scenario_id=payload.decision_context.scenario_id,data_snapshot_id=payload.decision_context.data_snapshot_id,methodology_version=payload.methodology_version,pr_value=pr_value,currency=payload.purchase_operation.currency if pr_value is not None else None,sufficiency_status=status,pr_status={"SUFFICIENT":"PR_AVAILABLE","LIMITED":"PR_LIMITED","NOT_JUSTIFIABLE":"PR_NOT_JUSTIFIABLE"}[status],pr_limitations=tuple(limitations),reference_set=selected,counts=PriceCounts(n_raw=len(identified),n_unique=len(unique),n_comparable=sum(a.comparability=="COMPARABLE" for a in ordered),n_representative=sum(a.comparability=="COMPARABLE" and a.representativeness=="REPRESENTATIVE" for a in ordered),n_selected=len(selected)),aggregation_method=method,trace_references=tuple(traces))
__all__=["assess_comparability","assess_economic_basis","assess_representativeness_for_reference","assess_temporality","deduplicate_references","identify_references","normalize_reference","run_price_intelligence","select_references"]