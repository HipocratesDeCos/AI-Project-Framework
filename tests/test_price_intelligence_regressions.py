"""Regression tests for Price Intelligence contract corrections."""
from datetime import date
from decimal import Decimal

from eios.core.models import DecisionContext, EvidenceValidation, PurchaseOperation
from eios.pricing.engine import run_price_intelligence
from eios.pricing.models import PriceIntelligenceAssessmentContext, PriceIntelligenceInput, PriceReference
from eios.pricing.representativeness import RepresentativenessObservation, assess_representativeness
from eios.pricing.sufficiency import SufficiencyObservation


def _operation() -> PurchaseOperation:
    return PurchaseOperation(
        decision_id="D1", scenario_id="S1", article_id="A1", supplier_id="SUP-1",
        quantity=Decimal("1"), unit_price=Decimal("10"), currency="EUR",
        operation_date=date(2026, 8, 1),
    )


def _reference() -> PriceReference:
    return PriceReference(
        source_transaction_id="R1", article_identity="A1", supplier_identity="SUP-1",
        quantity=Decimal("1"), unit="EA", unit_price=Decimal("10.00"), currency="EUR",
        operation_date=date(2026, 8, 1), evidence_refs=("E1",),
    )


def _context() -> DecisionContext:
    return DecisionContext(
        decision_id="D1", scenario_id="S1", rules_version="R1",
        parameters_version="P1", data_snapshot_id="SNAP-1",
    )


def _sufficiency() -> SufficiencyObservation:
    return SufficiencyObservation(
        selected_reference_ids=("R1",), evidence_refs=("E1",),
        rule_reference="RULE-SUF", trace_reference="TRACE-SUF",
        evidence_sufficient=True, contradictions_resolved=True,
    )


def _repr() -> RepresentativenessObservation:
    return RepresentativenessObservation(
        ordinary_market_context=True, exceptional_condition=False,
        material_commercial_distortion=False, evidence_refs=("E1",),
        rule_reference="RULE-REP", trace_reference="TRACE-REP",
    )


def test_same_unit_and_currency_do_not_require_normalization_basis():
    payload = PriceIntelligenceInput(
        decision_context=_context(), purchase_operation=_operation(),
        references=(_reference(),),
        evidence_validations=(EvidenceValidation(evidence_id="E1", status="VALID", reason="validated"),),
        normalization_basis=None, economic_basis_evidence=(), methodology_version="8.5",
    )
    context = PriceIntelligenceAssessmentContext(
        temporal={"R1": ("ELIGIBLE", "RULE-T")},
        representativeness={"R1": _repr()},
        sufficiency=_sufficiency(),
    )
    result = run_price_intelligence(payload, context)
    assert result.pr_status == "PR_LIMITED"
    assert result.pr_value == Decimal("10.00")
    assert result.reference_set == ("R1",)


def test_material_unresolved_contradiction_prevents_representative_classification():
    observation = RepresentativenessObservation(
        ordinary_market_context=True, exceptional_condition=False,
        material_commercial_distortion=False, contradiction_material_unresolved=True,
        evidence_refs=("E1",), rule_reference="RULE-REP", trace_reference="TRACE-REP",
        justification="Material contradiction remains unresolved",
    )
    assert assess_representativeness(observation) == "INDETERMINATE"


def test_no_known_unresolved_contradiction_preserves_representative_classification():
    assert assess_representativeness(_repr()) == "REPRESENTATIVE"
