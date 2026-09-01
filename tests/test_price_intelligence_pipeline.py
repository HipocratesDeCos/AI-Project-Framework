"""End-to-end contract tests for the C1 Price Intelligence pipeline."""
from datetime import date
from decimal import Decimal
import pytest
from eios.core.models import DecisionContext, EvidenceValidation, PurchaseOperation
from eios.pricing.engine import run_price_intelligence
from eios.pricing.models import PriceIntelligenceAssessmentContext, PriceIntelligenceInput, PriceReference, NormalizationBasis
from eios.pricing.representativeness import RepresentativenessObservation
from eios.pricing.sufficiency import SufficiencyObservation

def _context():
    return DecisionContext(decision_id="D1", scenario_id="S1", rules_version="R1", parameters_version="P1", data_snapshot_id="SNAP-1")
def _operation():
    return PurchaseOperation(decision_id="D1", scenario_id="S1", article_id="A1", supplier_id="SUP-1", quantity=Decimal("1"), unit_price=Decimal("10"), currency="EUR", operation_date=date(2026,8,1))
def _reference(ref_id="R1", price="10.00", evidence_id="E1"):
    return PriceReference(source_transaction_id=ref_id, article_identity="A1", supplier_identity="SUP-1", quantity=Decimal("1"), unit="EA", unit_price=Decimal(price), currency="EUR", operation_date=date(2026,8,1), evidence_refs=(evidence_id,))
def _evidence(evidence_id="E1"):
    return EvidenceValidation(evidence_id=evidence_id, status="VALID", source="TEST", trace_reference="TRACE-1")
def _basis():
    return NormalizationBasis(target_unit="EA", basis_reference="TEST-BASIS", rule_reference="RULE-NORM", trace_reference="TRACE-NORM")
def _repr(evidence_id="E1"):
    return RepresentativenessObservation(ordinary_market_context=True, exceptional_condition=False, material_commercial_distortion=False, evidence_refs=(evidence_id,), rule_reference="RULE-REP", trace_reference="TRACE-REP")
def _sufficiency(ids, evidence_id="E1"):
    return SufficiencyObservation(selected_reference_ids=tuple(ids), evidence_refs=(evidence_id,), rule_reference="RULE-SUF", trace_reference="TRACE-SUF", methodological_limitations=())
def _payload(references=()):
    evidence=tuple(_evidence(r.evidence_refs[0]) for r in references)
    return PriceIntelligenceInput(decision_context=_context(), purchase_operation=_operation(), references=tuple(references), evidence_validations=evidence, normalization_basis=_basis(), methodology_version="8.5")
def test_pipeline_with_no_references_returns_not_justifiable():
    result=run_price_intelligence(_payload(),PriceIntelligenceAssessmentContext(sufficiency=_sufficiency(())))
    assert result.pr_status=="PR_NOT_JUSTIFIABLE" and result.pr_value is None
def test_pipeline_rejects_context_reference_unknown_to_input():
    payload=_payload((_reference(),));context=PriceIntelligenceAssessmentContext(temporal={"R9":("ELIGIBLE","RULE-T")},sufficiency=_sufficiency(()))
    with pytest.raises(ValueError):run_price_intelligence(payload,context)
def test_pipeline_does_not_select_without_temporal_eligibility():
    payload=_payload((_reference(),));context=PriceIntelligenceAssessmentContext(temporal={"R1":("INELIGIBLE","RULE-T")},representativeness={"R1":_repr()},sufficiency=_sufficiency(()))
    result=run_price_intelligence(payload,context)
    assert result.reference_set==() and result.pr_value is None
def test_pipeline_propagates_snapshot_and_preserves_single_reference_as_limited():
    payload=_payload((_reference(),));context=PriceIntelligenceAssessmentContext(temporal={"R1":("ELIGIBLE","RULE-T")},representativeness={"R1":_repr()},sufficiency=_sufficiency(("R1",)))
    result=run_price_intelligence(payload,context)
    assert result.data_snapshot_id=="SNAP-1" and result.pr_status=="PR_LIMITED" and result.pr_value==Decimal("10.00")
def test_pipeline_rejects_sufficiency_observation_for_different_selected_set():
    refs=(_reference("R1"),_reference("R2","12.00","E2"));payload=_payload(refs);context=PriceIntelligenceAssessmentContext(temporal={"R1":("ELIGIBLE","RULE-T"),"R2":("ELIGIBLE","RULE-T")},representativeness={"R1":_repr(),"R2":_repr("E2")},sufficiency=_sufficiency(("R1",)))
    with pytest.raises(ValueError):run_price_intelligence(payload,context)
