"""Gate-level contract tests for Price Intelligence C1."""
from decimal import Decimal
import pytest
from eios.pricing.models import PriceReferenceAssessment
from eios.pricing.sufficiency import SufficiencyObservation, assess_sufficiency


def test_sufficiency_zero_is_not_justifiable():
    observation = SufficiencyObservation(selected_reference_ids=(), evidence_refs=("E1",), rule_reference="RULE", trace_reference="TRACE", methodological_limitations=(), status="NOT_JUSTIFIABLE")
    assert assess_sufficiency(0, observation) == "NOT_JUSTIFIABLE"


def test_sufficiency_one_is_limited():
    observation = SufficiencyObservation(selected_reference_ids=("R1",), evidence_refs=("E1",), rule_reference="RULE", trace_reference="TRACE", methodological_limitations=(), status="LIMITED")
    assert assess_sufficiency(1, observation) == "LIMITED"


def test_sufficiency_two_requires_positive_qualitative_observation():
    observation = SufficiencyObservation(selected_reference_ids=("R1", "R2"), evidence_refs=("E1",), rule_reference="RULE", trace_reference="TRACE", methodological_limitations=(), status="SUFFICIENT")
    assert assess_sufficiency(2, observation) == "SUFFICIENT"


def test_assessment_normalized_requires_value():
    with pytest.raises(ValueError):
        PriceReferenceAssessment(reference_id="R1", comparability="COMPARABLE", normalization_status="NORMALIZED")


def test_assessment_pending_cannot_carry_normalized_value():
    with pytest.raises(ValueError):
        PriceReferenceAssessment(reference_id="R1", comparability="COMPARABLE", normalization_status="PENDING", normalized_unit_price=Decimal("10"))
