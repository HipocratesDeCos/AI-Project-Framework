"""End-to-end contract tests for the C1 Price Intelligence pipeline."""
from datetime import date
from decimal import Decimal
import pytest
from eios.core.models import DecisionContext, EvidenceValidation, PurchaseOperation
from eios.pricing.engine import run_price_intelligence
from eios.pricing.models import PriceIntelligenceAssessmentContext, PriceIntelligenceInput, PriceReference, NormalizationBasis
from eios.pricing.representativeness import RepresentativenessObservation
from eios.pricing.sufficiency import SufficiencyObservation

def _context(): return DecisionContext(decision_id="D1", scenario_id="S1", rules_version="R1", parameters_version="P1", data_snapshot_id="SNAP-1")
def _operation(): return PurchaseOperation(decision_id="D1", scenario_id="S1", article_id="A1", supplier_id="SUP-1", quantity=Decimal("1"), unit_price=Decimal("10"), currency="EUR", operation_date=date(2026,8,1))
def _reference(ref_id="R1", price="10.00", evidence_id="E1"): return PriceReference(source_transaction_id=ref_id, article_identity="A1", supplier_identity="SUP-1", quantity=Decimal("1"), unit="EA", unit_price=Decimal(price), currency="EUR", operation_date=date(2026,8,1), evidence_refs=(evidence_id,))
def _evidence(evidence_id): return EvidenceValidation(evidence_id=evidence_id, status="VALID", reason="Validated test evidence")
def _basis(): return NormalizationBasis(target_unit="EA", basis_reference="TEST-BASIS", rule_reference="RULE-NORM", trace_reference="TRACE-NORM")
def _repr(evidence_id): return RepresentativenessObservation(ordinary_market_context=True, exceptional_condition=False, material_commercial_distortion=False, evidence_refs=(evidence_id,), rule_reference="RULE-REP", trace_reference="TRACE-REP")
def _sufficiency(ids, **kwargs): return SufficiencyObservation(selected_reference_ids=tuple(ids), evidence_refs=kwargs.get("evidence_refs", ("E1",)), rule_reference=kwargs.get("rule_reference", "RULE-SUF"), trace_reference=kwargs.get("trace_reference", "TRACE-SUF"), methodological_limitations=kwargs.get("methodological_limitations", ()), evidence_sufficient=kwargs.get("evidence_sufficient"), contradictions_resolved=kwargs.get("contradictions_resolved"), justification=kwargs.get("justification"))
def _payload(references=()): return PriceIntelligenceInput(decision_context=_context(), purchase_operation=_operation(), references=tuple(references), evidence_validations=tuple(_evidence(r.evidence_refs[0]) for r in references), normalization_basis=_basis(), methodology_version="8.5")
def _ready_context(ids, **kwargs): return PriceIntelligenceAssessmentContext(temporal={rid:("ELIGIBLE","RULE-T") for rid in ids}, representativeness={rid:_repr(rid.replace("R","E")) for rid in ids}, sufficiency=_sufficiency(ids, **kwargs))

def test_pipeline_with_no_references_returns_not_justifiable():
    result=run_price_intelligence(_payload(),PriceIntelligenceAssessmentContext(sufficiency=_sufficiency(())))
    assert result.pr_status=="PR_NOT_JUSTIFIABLE" and result.pr_value is None

def test_pipeline_rejects_context_reference_unknown_to_input():
    with pytest.raises(ValueError): run_price_intelligence(_payload((_reference(),)),PriceIntelligenceAssessmentContext(temporal={"R9":("ELIGIBLE","RULE-T")},sufficiency=_sufficiency(())))

def test_pipeline_does_not_select_without_temporal_eligibility():
    result=run_price_intelligence(_payload((_reference(),)),PriceIntelligenceAssessmentContext(temporal={"R1":("INELIGIBLE","RULE-T")},representativeness={"R1":_repr("E1")},sufficiency=_sufficiency(())))
    assert result.reference_set==() and result.pr_value is None

def test_pipeline_propagates_snapshot_and_preserves_single_reference_as_limited():
    result=run_price_intelligence(_payload((_reference(),)),_ready_context(("R1",),evidence_sufficient=True,contradictions_resolved=True))
    assert result.data_snapshot_id=="SNAP-1" and result.pr_status=="PR_LIMITED" and result.pr_value==Decimal("10.00")

def test_pipeline_two_selected_references_can_produce_available_price():
    refs=(_reference("R1","10.00","E1"),_reference("R2","12.00","E2"));result=run_price_intelligence(_payload(refs),_ready_context(("R1","R2"),evidence_sufficient=True,contradictions_resolved=True))
    assert result.pr_status=="PR_AVAILABLE" and result.pr_value==Decimal("11.00") and result.counts.n_selected==2

def test_pipeline_rejects_sufficiency_observation_for_different_selected_set():
    refs=(_reference("R1"),_reference("R2","12.00","E2"))
    with pytest.raises(ValueError): run_price_intelligence(_payload(refs),_ready_context(("R1","R2"),evidence_sufficient=True,contradictions_resolved=True).model_copy(update={"sufficiency":_sufficiency(("R1",),evidence_sufficient=True,contradictions_resolved=True)}))
