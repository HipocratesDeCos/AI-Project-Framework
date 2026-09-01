"""End-to-end contract tests for the C1 Price Intelligence pipeline."""
from datetime import date
from decimal import Decimal
import pytest
from eios.core.models import DecisionContext, EvidenceValidation, PurchaseOperation
from eios.pricing.engine import run_price_intelligence
from eios.pricing.models import PriceIntelligenceAssessmentContext, PriceReference, SufficiencyStatus
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
    from eios.pricing.models import NormalizationBasis
    return NormalizationBasis(target_unit="EA", basis_reference="TEST-BASIS", rule_reference="RULE-NORM", trace_reference="TRACE-NORM")


def _repr():
    return RepresentativenessObservation(ordinary_market_context=True, exceptional_condition=False, material_commercial_distortion=False, evidence_refs=("E1",), rule_reference="RULE-REP", trace_reference="TRACE-REP")


def _sufficiency(ids, status="LIMITED"):
    return SufficiencyObservation(selected_reference_ids=tuple(ids), evidence_refs=("E1",), rule_reference="RULE-SUF", trace_reference="TRACE-SUF", methodological_limitations=(), status=status)


def test_pipeline_with_no_references_returns_not_justifiable():
    payload = __import__("eios.pricing.models", fromlist=["PriceIntelligenceInput"]).PriceIntelligenceInput(decision_context=_context(), purchase_operation=_operation(), references=(), evidence_validations=(), normalization_basis=_basis(), methodology_version="8.5")
    result = run_price_intelligence(payload, PriceIntelligenceAssessmentContext(sufficiency=_sufficiency((), "NOT_JUSTIFIABLE")))
    assert result.pr_status == "PR_NOT_JUSTIFIABLE"
    assert result.pr_value is None


def test_pipeline_rejects_context_reference_unknown_to_input():
    payload = __import__("eios.pricing.models", fromlist=["PriceIntelligenceInput"]).PriceIntelligenceInput(decision_context=_context(), purchase_operation=_operation(), references=(_reference(),), evidence_validations=(_evidence(),), normalization_basis=_basis(), methodology_version="8.5")
    context = PriceIntelligenceAssessmentContext(temporal={"R9": ("ELIGIBLE", "RULE-T")}, sufficiency=_sufficiency((), "NOT_JUSTIFIABLE"))
    with pytest.raises(ValueError):
        run_price_intelligence(payload, context)


def test_pipeline_does_not_select_without_temporal_eligibility():
    payload = __import__("eios.pricing.models", fromlist=["PriceIntelligenceInput"]).PriceIntelligenceInput(decision_context=_context(), purchase_operation=_operation(), references=(_reference(),), evidence_validations=(_evidence(),), normalization_basis=_basis(), methodology_version="8.5")
    context = PriceIntelligenceAssessmentContext(temporal={"R1": ("INELIGIBLE", "RULE-T")}, representativeness={"R1": _repr()}, sufficiency=_sufficiency((), "NOT_JUSTIFIABLE"))
    result = run_price_intelligence(payload, context)
    assert result.reference_set == ()
    assert result.pr_value is None
