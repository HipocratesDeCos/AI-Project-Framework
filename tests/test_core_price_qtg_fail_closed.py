"""Regression tests for fail-closed PRICE and QTG boundaries.

All fixtures are synthetic. No operational or decision authority is granted.
"""

from datetime import date
from decimal import Decimal

from eios.core.models import DecisionContext, EvidenceValidation, PurchaseOperation
from eios.pricing.engine import assess_economic_basis, run_price_intelligence
from eios.pricing.models import (
    EconomicBasisEvidence,
    NormalizationBasis,
    PriceIntelligenceAssessmentContext,
    PriceIntelligenceInput,
    PriceReference,
    PriceReferenceAssessment,
)
from eios.pricing.representativeness import RepresentativenessObservation
from eios.pricing.sufficiency import SufficiencyObservation
from eios.quality.gate import QualityCheck, evaluate_quality


def _price_payload(*, unit="EA", currency="EUR", economic=()):
    operation = PurchaseOperation(
        decision_id="DEC-1", scenario_id="SCN-1", article_id="SKU-1",
        supplier_id="SUP-1", quantity=Decimal("1"), unit_price=Decimal("10"),
        currency="EUR", operation_date=date(2026, 8, 1),
    )
    reference = PriceReference(
        source_transaction_id="REF-1", article_identity="SKU-1",
        supplier_identity="SUP-1", quantity=Decimal("1"), unit=unit,
        unit_price=Decimal("10.00"), currency=currency,
        operation_date=date(2026, 8, 1), evidence_refs=("E-1",),
    )
    return PriceIntelligenceInput(
        decision_context=DecisionContext(
            decision_id="DEC-1", scenario_id="SCN-1",
            rules_version="RULES-1", parameters_version="PARAMS-1",
            data_snapshot_id="SYNTHETIC-SNAPSHOT-1",
        ),
        purchase_operation=operation,
        references=(reference,),
        evidence_validations=(
            EvidenceValidation(evidence_id="E-1", status="VALID", reason="Fixture"),
        ),
        normalization_basis=NormalizationBasis(
            target_unit="EA", basis_reference="BASIS-1",
            rule_reference="RULE-NORM-1", trace_reference="TRACE-NORM-1",
        ),
        economic_basis_evidence=tuple(economic),
        methodology_version="8.5",
    )


def _economic(dimension, status="RESOLVED"):
    return EconomicBasisEvidence(
        reference_id="REF-1", dimension=dimension, status=status,
        evidence_refs=("E-1",), rule_reference="RULE-NORM-1",
        trace_reference="TRACE-NORM-1",
        justification="Unresolved component" if status == "PENDING" else None,
    )


def _assessment(payload):
    return assess_economic_basis(
        payload,
        payload.references[0],
        PriceReferenceAssessment(reference_id="REF-1", comparability="COMPARABLE"),
    )


def test_qtg_empty_control_set_is_no_apto_with_explicit_cause():
    result = evaluate_quality([])
    assert (result.status, result.confidence) == ("NO_APTO", "BAJA")
    assert len(result.checks) == 1
    assert result.checks[0].control == "APPLICABLE_CONTROLS_MISSING"
    assert result.checks[0].critical


def test_qtg_all_controls_not_applicable_is_no_apto():
    result = evaluate_quality(
        [QualityCheck("optional", True, applicable=False)]
    )
    assert (result.status, result.confidence) == ("NO_APTO", "BAJA")
    assert result.checks[0].control == "APPLICABLE_CONTROLS_MISSING"


def test_price_cross_currency_evidence_is_not_a_numeric_conversion():
    result = _assessment(_price_payload(currency="USD", economic=(_economic("CURRENCY"),)))
    assert result.normalization_status == "PENDING"
    assert result.normalized_unit_price is None
    assert "NORMALIZATION_TRANSFORMATION_NOT_EXECUTED" in result.limitation_refs


def test_price_cross_unit_evidence_is_not_a_numeric_conversion():
    result = _assessment(_price_payload(unit="BOX", economic=(_economic("UNIT"),)))
    assert result.normalization_status == "PENDING"
    assert result.normalized_unit_price is None
    assert "UNIT_CONVERSION_REQUIRED" in result.limitation_refs


def test_price_missing_required_dimension_is_incomplete():
    result = _assessment(
        _price_payload(unit="BOX", currency="USD", economic=(_economic("UNIT"),))
    )
    assert result.normalization_status == "PENDING"
    assert "ECONOMIC_BASIS_INCOMPLETE" in result.limitation_refs


def test_price_unresolved_economic_component_blocks_unchanged_unit_currency():
    result = _assessment(_price_payload(economic=(_economic("TAX", "PENDING"),)))
    assert result.normalization_status == "PENDING"
    assert result.normalized_unit_price is None
    assert "ECONOMIC_BASIS_INCOMPLETE" in result.limitation_refs


def test_price_same_unit_currency_without_unresolved_component_still_usable():
    result = _assessment(_price_payload())
    assert result.normalization_status == "NORMALIZED"
    assert result.normalized_unit_price == Decimal("10.00")


def test_price_pipeline_does_not_aggregate_unconverted_usd_as_eur():
    payload = _price_payload(currency="USD", economic=(_economic("CURRENCY"),))
    context = PriceIntelligenceAssessmentContext(
        temporal={"REF-1": ("ELIGIBLE", "RULE-T")},
        representativeness={
            "REF-1": RepresentativenessObservation(
                ordinary_market_context=True, exceptional_condition=False,
                material_commercial_distortion=False, evidence_refs=("E-1",),
                rule_reference="RULE-REP", trace_reference="TRACE-REP",
            ),
        },
        sufficiency=SufficiencyObservation(
            selected_reference_ids=(), evidence_refs=("E-1",),
            rule_reference="RULE-SUF", trace_reference="TRACE-SUF",
        ),
    )
    result = run_price_intelligence(payload, context)
    assert result.pr_value is None
    assert result.reference_set == ()
    assert result.pr_status == "PR_NOT_JUSTIFIABLE"
    assert "NORMALIZATION_TRANSFORMATION_NOT_EXECUTED" in result.pr_limitations
