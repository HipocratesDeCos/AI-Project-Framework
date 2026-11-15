"""Synthetic C1 regression tests for explicit, evidence-bound price conversions."""
from datetime import date
from decimal import Decimal

import pytest
from pydantic import ValidationError

from eios.core.models import DecisionContext, EvidenceValidation, PurchaseOperation
from eios.pricing.engine import assess_economic_basis, run_price_intelligence
from eios.pricing.models import (
    EconomicBasisEvidence,
    NormalizationBasis,
    PriceConversionInstruction,
    PriceIntelligenceAssessmentContext,
    PriceIntelligenceInput,
    PriceReference,
    PriceReferenceAssessment,
)
from eios.pricing.representativeness import RepresentativenessObservation
from eios.pricing.sufficiency import SufficiencyObservation


HISTORICAL_DATE = date(2026, 8, 1)


def conversion(dimension, *, factor, source=None, target=None, effective_date=HISTORICAL_DATE,
               evidence_refs=("E1",), rule_reference="RULE-CONVERT", trace_reference="TRACE-CONVERT"):
    source = source or ("BOX" if dimension == "UNIT" else "USD")
    target = target or ("EA" if dimension == "UNIT" else "EUR")
    return PriceConversionInstruction(
        reference_id="REF1", dimension=dimension, source_code=source,
        target_code=target, factor=Decimal(factor), effective_date=effective_date,
        source_ref="DOC-RATE-1", evidence_refs=evidence_refs,
        rule_reference=rule_reference, trace_reference=trace_reference,
    )


def economic(dimension, *, status="RESOLVED", evidence_refs=("E1",)):
    return EconomicBasisEvidence(
        reference_id="REF1", dimension=dimension, status=status,
        evidence_refs=evidence_refs, rule_reference="RULE-CONVERT",
        trace_reference="TRACE-CONVERT",
        justification="Unresolved" if status == "PENDING" else None,
    )


def payload(*, unit="BOX", currency="USD", price="120", conversions=(),
            economic_records=(), evidence_status="VALID", date_of_reference=HISTORICAL_DATE):
    operation = PurchaseOperation(
        decision_id="D1", scenario_id="S1", article_id="A1",
        supplier_id="SUP1", quantity=Decimal("1"), unit_price=Decimal("10"),
        operation_date=HISTORICAL_DATE, currency="EUR",
    )
    reference = PriceReference(
        source_transaction_id="REF1", article_identity="A1",
        supplier_identity="SUP1", quantity=Decimal("1"), unit=unit,
        unit_price=Decimal(price), currency=currency,
        operation_date=date_of_reference, evidence_refs=("E1",),
    )
    return PriceIntelligenceInput(
        decision_context=DecisionContext(
            decision_id="D1", scenario_id="S1", rules_version="RV1",
            parameters_version="PV1", data_snapshot_id="SYNTHETIC1",
        ),
        purchase_operation=operation,
        references=(reference,),
        evidence_validations=(
            EvidenceValidation(evidence_id="E1", status=evidence_status, reason="Synthetic fixture"),
        ),
        normalization_basis=NormalizationBasis(
            target_unit="EA", basis_reference="BASIS-1",
            rule_reference="RULE-CONVERT", trace_reference="TRACE-CONVERT",
        ),
        economic_basis_evidence=economic_records,
        price_conversion_instructions=conversions,
        methodology_version="8.5",
    )


def evaluated(input_data):
    return assess_economic_basis(
        input_data,
        input_data.references[0],
        PriceReferenceAssessment(reference_id="REF1", comparability="COMPARABLE"),
    )


def test_unit_conversion_records_applied_factor_and_trace():
    data = payload(
        currency="EUR", conversions=(conversion("UNIT", factor="0.1"),),
        economic_records=(economic("UNIT"),),
    )
    result = evaluated(data)
    assert result.normalization_status == "NORMALIZED"
    assert result.normalized_unit_price == Decimal("12.0000")
    assert len(result.normalization) == 1
    assert result.normalization[0].field == "UNIT"
    assert Decimal(result.normalization[0].normalized_value) == Decimal("12")


def test_currency_conversion_uses_historical_date_and_traces():
    data = payload(
        unit="EA", price="10", conversions=(conversion("CURRENCY", factor="0.9"),),
        economic_records=(economic("CURRENCY"),),
    )
    result = evaluated(data)
    assert result.normalized_unit_price == Decimal("9.0000")
    assert result.normalization[0].field == "CURRENCY"


def test_currency_and_unit_in_one_chain_are_applied_without_intermediate_rounding():
    data = payload(
        conversions=(
            conversion("CURRENCY", factor="0.9"),
            conversion("UNIT", factor="0.1"),
        ),
        economic_records=(economic("CURRENCY"), economic("UNIT")),
    )
    result = evaluated(data)
    assert result.normalized_unit_price == Decimal("10.8000")
    assert tuple(item.field for item in result.normalization) == ("UNIT", "CURRENCY")
    assert Decimal(result.normalization[0].normalized_value) == Decimal("12")
    assert Decimal(result.normalization[1].normalized_value) == Decimal("10.8")


def test_missing_conversion_never_normalizes_a_different_currency():
    data = payload(unit="EA", economic_records=(economic("CURRENCY"),))
    result = evaluated(data)
    assert result.normalized_unit_price is None
    assert "NORMALIZATION_TRANSFORMATION_NOT_EXECUTED" in result.limitation_refs


def test_missing_economic_dim_never_normalizes():
    data = payload(
        unit="EA", conversions=(conversion("CURRENCY", factor="0.9"),),
    )
    result = evaluated(data)
    assert result.normalized_unit_price is None
    assert "ECONOMIC_BASIS_INCOMPLETE" in result.limitation_refs


def test_unvalidated_currency_evidence_never_normalizes():
    data = payload(
        unit="EA", conversions=(conversion("CURRENCY", factor="0.9"),),
        economic_records=(economic("CURRENCY"),), evidence_status="INVALID",
    )
    result = evaluated(data)
    assert result.normalization_status == "PENDING"
    assert result.normalized_unit_price is None
    assert "CONVERSION_EVIDENCE_MISMATCH" in result.limitation_refs


def test_wrong_source_currency_or_rate_date_fails_closed():
    data = payload(
        unit="EA", conversions=(conversion("CURRENCY", factor="0.9", source="GBP"),),
        economic_records=(economic("CURRENCY"),),
    )
    assert "CONVERSION_CONTEXT_MISMATCH" in evaluated(data).limitation_refs
    other = payload(
        unit="EA",
        conversions=(conversion("CURRENCY", factor="0.9", effective_date=date(2026, 8, 2)),),
        economic_records=(economic("CURRENCY"),),
    )
    result = evaluated(other)
    assert result.normalization_status == "PENDING"
    assert result.normalized_unit_price is None


def test_unnecessary_instruction_never_changes_original_price_silently():
    data = payload(
        unit="EA", currency="EUR",
        conversions=(conversion("CURRENCY", factor="0.9"),),
        economic_records=(economic("CURRENCY"),),
    )
    result = evaluated(data)
    assert result.normalization_status == "PENDING"
    assert "UNNECESSARY_CONVERSION_INSTRUCTION" in result.limitation_refs


def test_zero_negative_and_non_finite_rates_are_invalid_contracts():
    for rate in ("0", "-1", "NaN", "Infinity"):
        with pytest.raises(ValidationError):
            conversion("CURRENCY", factor=rate)


def test_duplicate_conversion_dimension_rejected():
    with pytest.raises(ValidationError, match="duplicadas"):
        payload(
            unit="EA",
            conversions=(
                conversion("CURRENCY", factor="0.9"),
                conversion("CURRENCY", factor="0.8"),
            ),
            economic_records=(economic("CURRENCY"),),
        )


def test_conversion_unknown_evidence_reference_rejected():
    with pytest.raises(ValidationError, match="evidencia desconocida"):
        payload(
            unit="EA",
            conversions=(conversion("CURRENCY", factor="0.9", evidence_refs=("UNKNOWN",)),),
            economic_records=(economic("CURRENCY"),),
        )


def test_resolved_economic_dimension_without_matching_rule_fails_closed():
    data = payload(
        unit="EA",
        conversions=(conversion("CURRENCY", factor="0.9", rule_reference="OTHER-RULE"),),
        economic_records=(economic("CURRENCY"),),
    )
    result = evaluated(data)
    assert result.normalized_unit_price is None
    assert "CONVERSION_EVIDENCE_MISMATCH" in result.limitation_refs


def test_numeric_rounding_is_deterministic_at_four_decimal_places():
    data = payload(
        unit="EA", currency="USD", price="1",
        conversions=(conversion("CURRENCY", factor="0.123456"),),
        economic_records=(economic("CURRENCY"),),
    )
    result = evaluated(data)
    assert result.normalized_unit_price == Decimal("0.1235")


def test_pipeline_aggregates_converted_eur_and_exposes_source_traces():
    data = payload(
        unit="EA", price="10",
        conversions=(conversion("CURRENCY", factor="0.9"),),
        economic_records=(economic("CURRENCY"),),
    )
    context = PriceIntelligenceAssessmentContext(
        temporal={"REF1": ("ELIGIBLE", "RULE-T")},
        representativeness={
            "REF1": RepresentativenessObservation(
                ordinary_market_context=True, exceptional_condition=False,
                material_commercial_distortion=False, evidence_refs=("E1",),
                rule_reference="RULE-REP", trace_reference="TRACE-REP",
            ),
        },
        sufficiency=SufficiencyObservation(
            selected_reference_ids=("REF1",), evidence_refs=("E1",),
            rule_reference="RULE-SUF", trace_reference="TRACE-SUF",
            evidence_sufficient=True, contradictions_resolved=True,
        ),
    )
    result = run_price_intelligence(data, context)
    assert result.pr_value == Decimal("9.0000")
    assert result.currency == "EUR"
    assert result.reference_set == ("REF1",)
    assert "TRACE-CONVERT" in result.trace_references
    assert "DOC-RATE-1" in result.trace_references


def test_same_unit_currency_legacy_paths_still_work_without_instructions():
    result = evaluated(payload(unit="EA", currency="EUR", price="7.2"))
    assert result.normalization_status == "NORMALIZED"
    assert result.normalized_unit_price == Decimal("7.2000")
