"""Gate-level contract tests for Price Intelligence C1."""
from decimal import Decimal
import pytest
from eios.pricing.models import PriceReferenceAssessment
from eios.pricing.sufficiency import SufficiencyObservation, assess_sufficiency

def _observation(ids, **kwargs):
    return SufficiencyObservation(selected_reference_ids=tuple(ids), evidence_refs=kwargs.pop("evidence_refs", ("E1",)), rule_reference=kwargs.pop("rule_reference", "RULE"), trace_reference=kwargs.pop("trace_reference", "TRACE"), methodological_limitations=kwargs.pop("methodological_limitations", ()), evidence_sufficient=kwargs.pop("evidence_sufficient", None), contradictions_resolved=kwargs.pop("contradictions_resolved", None), justification=kwargs.pop("justification", None))

def test_sufficiency_zero_is_not_justifiable():
    assert assess_sufficiency(0, _observation(())) == "NOT_JUSTIFIABLE"
def test_sufficiency_one_is_limited():
    assert assess_sufficiency(1, _observation(("R1",))) == "LIMITED"
def test_sufficiency_two_requires_positive_qualitative_observation():
    assert assess_sufficiency(2, _observation(("R1", "R2"), evidence_sufficient=True, contradictions_resolved=True)) == "SUFFICIENT"
def test_sufficiency_two_with_methodological_limitation_is_not_sufficient():
    assert assess_sufficiency(2, _observation(("R1", "R2"), evidence_sufficient=True, contradictions_resolved=True, methodological_limitations=("LIMIT",))) == "LIMITED"
def test_sufficiency_two_without_evidence_is_not_sufficient():
    assert assess_sufficiency(2, _observation(("R1", "R2"), evidence_sufficient=True, contradictions_resolved=True, evidence_refs=())) == "LIMITED"
def test_sufficiency_two_without_rule_is_not_sufficient():
    assert assess_sufficiency(2, _observation(("R1", "R2"), evidence_sufficient=True, contradictions_resolved=True, rule_reference=None)) == "LIMITED"
def test_sufficiency_two_without_trace_is_not_sufficient():
    assert assess_sufficiency(2, _observation(("R1", "R2"), evidence_sufficient=True, contradictions_resolved=True, trace_reference=None)) == "LIMITED"
def test_assessment_normalized_requires_value():
    with pytest.raises(ValueError):
        PriceReferenceAssessment(reference_id="R1", comparability="COMPARABLE", normalization_status="NORMALIZED")
def test_assessment_pending_cannot_carry_normalized_value():
    with pytest.raises(ValueError):
        PriceReferenceAssessment(reference_id="R1", comparability="COMPARABLE", normalization_status="PENDING", normalized_unit_price=Decimal("10"))
