"""Synthetic PRICE economic-basis gating; no business/operational authority."""
from datetime import date
from decimal import Decimal

import pytest
from pydantic import ValidationError

from eios.core.models import DecisionContext, EvidenceValidation, PurchaseOperation
from eios.pricing.engine import assess_economic_basis, run_price_intelligence
from eios.pricing.models import (
    EconomicBasisEvidence,
    NormalizationBasis,
    PriceEconomicBasisComparison,
    PriceIntelligenceAssessmentContext,
    PriceIntelligenceInput,
    PriceReference,
    PriceReferenceAssessment,
)
from eios.pricing.representativeness import RepresentativenessObservation
from eios.pricing.sufficiency import SufficiencyObservation


def proof(dimension, source="SIN_IVA", target="SIN_IVA", status="EQUIVALENT",
          evidence_refs=("E1",), justification=None, **overrides):
    values = dict(
        reference_id="REF1", dimension=dimension, source_basis=source,
        target_basis=target, status=status, source_ref="DOC-ECON-1",
        evidence_refs=evidence_refs, rule_reference="R-ECON-1",
        trace_reference="T-ECON-1", justification=justification,
    )
    return PriceEconomicBasisComparison(**(values | overrides))


def evidence(dimension, status="RESOLVED", **overrides):
    values = dict(
        reference_id="REF1", dimension=dimension, status=status,
        evidence_refs=("E1",), rule_reference="R-ECON-1",
        trace_reference="T-ECON-1",
        justification="Still pending" if status == "PENDING" else None,
    )
    return EconomicBasisEvidence(**(values | overrides))


def price_data(*, basis=None, comparisons=(), economic_records=(),
               commercial=None, quantity="10", evidence_status="VALID"):
    reference = PriceReference(
        source_transaction_id="REF1", article_identity="SKU1",
        supplier_identity="SUP1", quantity=Decimal(quantity),
        unit="EA", unit_price=Decimal("20.25"), currency="EUR",
        operation_date=date(2026, 8, 1), commercial_conditions=commercial,
        evidence_refs=("E1",),
    )
    return PriceIntelligenceInput(
        purchase_operation=PurchaseOperation(
            decision_id="D1", scenario_id="S1", article_id="SKU1",
            supplier_id="SUP1", quantity=Decimal("10"), unit_price=Decimal("22"),
            currency="EUR", operation_date=date(2026, 8, 1),
        ),
        decision_context=DecisionContext(
            decision_id="D1", scenario_id="S1", rules_version="R1",
            parameters_version="P1", data_snapshot_id="SYNTHETIC-1",
        ),
        references=(reference,),
        evidence_validations=(EvidenceValidation(
            evidence_id="E1", status=evidence_status, reason="Fixture",
        ),),
        normalization_basis=basis,
        economic_basis_evidence=economic_records,
        economic_basis_comparisons=comparisons,
        methodology_version="8.5",
    )


def target(**targets):
    return NormalizationBasis(
        target_unit="EA", basis_reference="BASIS-1",
        rule_reference="R-ECON-1", trace_reference="T-ECON-1",
        **targets,
    )


def assess(data):
    return assess_economic_basis(
        data, data.references[0],
        PriceReferenceAssessment(reference_id="REF1", comparability="COMPARABLE"),
    )


@pytest.mark.parametrize("field,dimension,price_basis", [
    ("target_tax_basis", "TAX", "SIN_IVA"),
    ("target_transport_basis", "TRANSPORT", "SIN_PORTES"),
    ("target_discount_basis", "DISCOUNT", "NETO"),
    ("target_surcharge_basis", "SURCHARGE", "SIN_RECARGOS"),
    ("target_commercial_basis", "COMMERCIAL", "CONTADO"),
])
def test_declared_material_basis_without_evidence_blocks(field, dimension, price_basis):
    result = assess(price_data(basis=target(**{field: price_basis})))
    assert result.normalization_status == "PENDING"
    assert result.normalized_unit_price is None
    assert "ECONOMIC_DIMENSION_UNVERIFIED:" + dimension in result.limitation_refs


@pytest.mark.parametrize("field,dimension,basis_name", [
    ("target_tax_basis", "TAX", "SIN_IVA"),
    ("target_transport_basis", "TRANSPORT", "SIN_PORTES"),
    ("target_discount_basis", "DISCOUNT", "NETO"),
    ("target_surcharge_basis", "SURCHARGE", "SIN_RECARGOS"),
    ("target_commercial_basis", "COMMERCIAL", "CONTADO"),
])
def test_matching_documented_equivalence_keeps_original_price(field, dimension, basis_name):
    result = assess(price_data(
        basis=target(**{field: basis_name}),
        comparisons=(proof(dimension, basis_name, basis_name),),
        economic_records=(evidence(dimension),),
    ))
    assert result.normalization_status == "NORMALIZED"
    assert result.normalized_unit_price == Decimal("20.25")
    assert result.normalization == ()


def test_different_tax_bases_are_not_silently_converted():
    result = assess(price_data(
        basis=target(target_tax_basis="SIN_IVA"),
        comparisons=(proof("TAX", "CON_IVA", "SIN_IVA",
                           status="DIFFERENT", justification="Tax included in historical price"),),
        economic_records=(evidence("TAX"),),
    ))
    assert result.normalization_status == "PENDING"
    assert result.normalized_unit_price is None
    assert "ECONOMIC_DIMENSION_UNRESOLVED:TAX" in result.limitation_refs


def test_false_equivalence_with_different_material_bases_is_invalid_contract():
    with pytest.raises(ValidationError, match="Bases económicas distintas"):
        proof("TRANSPORT", "CON_PORTES", "SIN_PORTES")


def test_mismatch_between_claimed_target_and_normalization_target_blocks():
    result = assess(price_data(
        basis=target(target_discount_basis="NETO"),
        comparisons=(proof("DISCOUNT", "BRUTO", "BRUTO"),),
        economic_records=(evidence("DISCOUNT"),),
    ))
    assert result.normalized_unit_price is None
    assert "ECONOMIC_DIMENSION_CONTEXT_MISMATCH:DISCOUNT" in result.limitation_refs


def test_missing_economic_evidence_blocks_even_if_equivalence_is_declared():
    result = assess(price_data(
        basis=target(target_tax_basis="SIN_IVA"),
        comparisons=(proof("TAX"),),
    ))
    assert result.normalized_unit_price is None
    assert "ECONOMIC_DIMENSION_EVIDENCE_MISMATCH:TAX" in result.limitation_refs


def test_bad_quality_evidence_blocks_equivalence():
    result = assess(price_data(
        basis=target(target_tax_basis="SIN_IVA"),
        comparisons=(proof("TAX"),), economic_records=(evidence("TAX"),),
        evidence_status="INVALID",
    ))
    assert result.normalized_unit_price is None
    assert "ECONOMIC_DIMENSION_EVIDENCE_MISMATCH:TAX" in result.limitation_refs


def test_unbound_material_comparison_without_target_is_pending():
    result = assess(price_data(
        comparisons=(proof("TAX"),), economic_records=(evidence("TAX"),),
    ))
    assert result.normalized_unit_price is None
    assert "ECONOMIC_DIMENSION_TARGET_MISSING:TAX" in result.limitation_refs


def test_commercial_conditions_are_not_ignored_without_target_basis():
    result = assess(price_data(commercial="PAGO 90 DIAS"))
    assert result.normalized_unit_price is None
    assert "ECONOMIC_DIMENSION_UNVERIFIED:COMMERCIAL" in result.limitation_refs


def test_commercial_description_must_match_the_observed_source():
    result = assess(price_data(
        commercial="PAGO 90 DIAS",
        basis=target(target_commercial_basis="CONTADO"),
        comparisons=(proof("COMMERCIAL", "CONTADO", "CONTADO"),),
        economic_records=(evidence("COMMERCIAL"),),
    ))
    assert result.normalized_unit_price is None
    assert "ECONOMIC_DIMENSION_CONTEXT_MISMATCH:COMMERCIAL" in result.limitation_refs


def test_quantity_difference_requires_documented_price_equivalence():
    result = assess(price_data(
        quantity="8",
        comparisons=(proof("QUANTITY", "8", "10",
                           justification="Unit price unchanged across declared quantity tiers"),),
        economic_records=(evidence("QUANTITY"),),
    ))
    assert result.normalized_unit_price == Decimal("20.25")


def test_quantity_comparison_must_match_actual_purchase_quantity():
    result = assess(price_data(
        quantity="8",
        comparisons=(proof("QUANTITY", "8", "20",
                           justification="A documented volume price comparison"),),
        economic_records=(evidence("QUANTITY"),),
    ))
    assert result.normalized_unit_price is None
    assert "ECONOMIC_DIMENSION_CONTEXT_MISMATCH:QUANTITY" in result.limitation_refs


def test_quantity_difference_without_justification_is_rejected_by_contract():
    with pytest.raises(ValidationError, match="justificación"):
        proof("QUANTITY", "8", "10")


def test_quantity_difference_cannot_be_called_not_applicable():
    result = assess(price_data(
        quantity="8",
        comparisons=(proof("QUANTITY", "8", "10", status="NOT_APPLICABLE"),),
        economic_records=(evidence("QUANTITY", status="NOT_APPLICABLE"),),
    ))
    assert result.normalized_unit_price is None
    assert "ECONOMIC_DIMENSION_INAPPLICABLE_CONFLICT:QUANTITY" in result.limitation_refs


def test_duplicate_material_proofs_rejected():
    with pytest.raises(ValidationError, match="duplicadas"):
        price_data(
            basis=target(target_tax_basis="SIN_IVA"),
            comparisons=(proof("TAX"), proof("TAX")),
            economic_records=(evidence("TAX"),),
        )


def test_proof_unknown_evidence_reference_rejected():
    with pytest.raises(ValidationError, match="evidencia desconocida"):
        price_data(
            basis=target(target_tax_basis="SIN_IVA"),
            comparisons=(proof("TAX", evidence_refs=("NO-EXISTE",)),),
            economic_records=(evidence("TAX"),),
        )


def test_material_evidence_without_equivalence_proof_is_not_ignored():
    result = assess(price_data(economic_records=(evidence("DISCOUNT"),)))
    assert result.normalized_unit_price is None
    assert "ECONOMIC_DIMENSION_UNVERIFIED:DISCOUNT" in result.limitation_refs


def test_not_applicable_cannot_override_an_explicit_target_basis():
    result = assess(price_data(
        basis=target(target_tax_basis="SIN_IVA"),
        comparisons=(proof("TAX", "NINGUNO", "SIN_IVA",
                           status="NOT_APPLICABLE"),),
        economic_records=(evidence("TAX", status="NOT_APPLICABLE"),),
    ))
    assert result.normalized_unit_price is None
    assert "ECONOMIC_DIMENSION_INAPPLICABLE_CONFLICT:TAX" in result.limitation_refs


def test_pipeline_fails_closed_and_does_not_aggregate_unsupported_tax_basis():
    data = price_data(basis=target(target_tax_basis="SIN_IVA"))
    context = PriceIntelligenceAssessmentContext(
        temporal={"REF1": ("ELIGIBLE", "R-T")},
        representativeness={
            "REF1": RepresentativenessObservation(
                ordinary_market_context=True, exceptional_condition=False,
                material_commercial_distortion=False, evidence_refs=("E1",),
                rule_reference="R-REP", trace_reference="T-REP",
            ),
        },
        sufficiency=SufficiencyObservation(
            selected_reference_ids=(), evidence_refs=("E1",),
            rule_reference="R-SUF", trace_reference="T-SUF",
        ),
    )
    result = run_price_intelligence(data, context)
    assert result.pr_value is None
    assert result.reference_set == ()
    assert "ECONOMIC_DIMENSION_UNVERIFIED:TAX" in result.pr_limitations


def test_pipeline_traces_documented_basis_equivalence():
    data = price_data(
        basis=target(target_tax_basis="SIN_IVA"),
        comparisons=(proof("TAX"),),
        economic_records=(evidence("TAX"),),
    )
    context = PriceIntelligenceAssessmentContext(
        temporal={"REF1": ("ELIGIBLE", "R-T")},
        representativeness={
            "REF1": RepresentativenessObservation(
                ordinary_market_context=True, exceptional_condition=False,
                material_commercial_distortion=False, evidence_refs=("E1",),
                rule_reference="R-REP", trace_reference="T-REP",
            ),
        },
        sufficiency=SufficiencyObservation(
            selected_reference_ids=("REF1",), evidence_refs=("E1",),
            rule_reference="R-SUF", trace_reference="T-SUF",
            evidence_sufficient=True, contradictions_resolved=True,
        ),
    )
    result = run_price_intelligence(data, context)
    assert result.pr_value == Decimal("20.25")
    assert result.reference_set == ("REF1",)
    for part in ("DOC-ECON-1", "R-ECON-1", "T-ECON-1"):
        assert part in result.trace_references
