"""Strict PRICE company profile tests. Synthetic only; no operational authority."""

from datetime import date
from decimal import Decimal

import pytest

from eios.core.models import DecisionContext, EvidenceValidation, PurchaseOperation
from eios.core.price_integration import build_provenanced_company_price_invoker
from eios.core.orchestration import O1ExecutionStatus
from eios.core.mvp_execution import run_mvp_execution
from eios.pricing.company_coverage import (
    MATERIAL_DIMENSIONS,
    PriceCompanyCoverageProfile,
    PriceCoverageError,
    assess_price_company_coverage,
    run_price_intelligence_for_company,
)
from eios.pricing.engine import run_price_intelligence
from eios.pricing.models import (
    EconomicBasisEvidence,
    NormalizationBasis,
    PriceEconomicBasisComparison,
    PriceIntelligenceAssessmentContext,
    PriceIntelligenceInput,
    PriceReference,
)
from eios.pricing.representativeness import RepresentativenessObservation
from eios.pricing.sufficiency import SufficiencyObservation
from eios.pricing.historical_comparability import (
    HIS003_REQUIRED_DIMENSIONS,
    HistoricalComparabilityDimensionAuthority,
    HistoricalComparabilityDimensionDetermination,
    aggregate_historical_comparability,
)
from eios.quality.gate import QualityCheck, evaluate_quality


FIELDS = {
    "TAX": "SIN_IVA", "TRANSPORT": "SIN_PORTES", "DISCOUNT": "NETO",
    "SURCHARGE": "SIN_RECARGOS", "COMMERCIAL": "NO_APLICA",
}


def fixtures():
    reference = PriceReference(
        source_transaction_id="H1", article_identity="SKU1",
        supplier_identity="S1", quantity=Decimal("10"), unit="EA",
        unit_price=Decimal("20.25"), currency="EUR",
        operation_date=date(2026, 8, 1), evidence_refs=("E1",),
    )
    operation = PurchaseOperation(
        decision_id="D1", scenario_id="SC1", article_id="SKU1", supplier_id="S1",
        quantity=Decimal("10"), unit_price=Decimal("20"),
        currency="EUR", operation_date=date(2026, 8, 2),
    )
    coverage = []
    for dimension in MATERIAL_DIMENSIONS:
        source = "10" if dimension == "QUANTITY" else FIELDS[dimension]
        coverage.append(PriceEconomicBasisComparison(
            reference_id="H1", dimension=dimension,
            source_basis=source, target_basis=source,
            status="EQUIVALENT", source_ref=f"DOC-{dimension}",
            evidence_refs=("E1",), rule_reference="R-BASE",
            trace_reference=f"T-{dimension}",
        ))
    evidence = tuple(
        EconomicBasisEvidence(
            reference_id="H1", dimension=proof.dimension, status="RESOLVED",
            evidence_refs=("E1",), rule_reference="R-BASE",
            trace_reference=proof.trace_reference,
        )
        for proof in coverage
    )
    payload = PriceIntelligenceInput(
        decision_context=DecisionContext(
            decision_id="D1", scenario_id="SC1", rules_version="R1",
            parameters_version="P1", data_snapshot_id="SNAP1",
        ),
        purchase_operation=operation, references=(reference,),
        evidence_validations=(
            EvidenceValidation(evidence_id="E1", status="VALID", reason="Synthetic"),
            EvidenceValidation(evidence_id="E-PROFILE", status="VALID", reason="Synthetic"),
        ),
        normalization_basis=NormalizationBasis(
            target_unit="EA", basis_reference="B1",
            rule_reference="R-BASE", trace_reference="T-BASE",
            target_tax_basis="SIN_IVA", target_transport_basis="SIN_PORTES",
            target_discount_basis="NETO", target_surcharge_basis="SIN_RECARGOS",
            target_commercial_basis="NO_APLICA",
        ),
        economic_basis_evidence=evidence,
        economic_basis_comparisons=tuple(coverage),
        methodology_version="8.5",
    )
    profile = PriceCompanyCoverageProfile(
        profile_id="PROFILE-1", company_id="COMPANY-1",
        decision_id="D1", scenario_id="SC1",
        parameters_version="P1", data_snapshot_id="SNAP1",
        source_ref="DOC-PROFILE", evidence_id="E-PROFILE",
        rule_reference="RULE-PROFILE", trace_reference="TRACE-PROFILE",
    )
    context = PriceIntelligenceAssessmentContext(
        temporal={"H1": ("ELIGIBLE", "RULE-TEMP")},
        representativeness={
            "H1": RepresentativenessObservation(
                ordinary_market_context=True,
                exceptional_condition=False,
                material_commercial_distortion=False,
                evidence_refs=("E1",), rule_reference="RULE-REP",
                trace_reference="TRACE-REP",
            ),
        },
        sufficiency=SufficiencyObservation(
            selected_reference_ids=("H1",), evidence_refs=("E1",),
            rule_reference="RULE-SUFF", trace_reference="TRACE-SUFF",
            evidence_sufficient=True, contradictions_resolved=True,
        ),
    )
    return payload, profile, context


def validate(payload, profile, company="COMPANY-1"):
    return assess_price_company_coverage(
        payload, profile, expected_company_id=company,
    )


def test_all_economic_dimensions_covered_and_proven():
    payload, profile, _ = fixtures()
    result = validate(payload, profile)
    assert result.complete and result.issues == ()
    assert result.reference_count == 1


def test_strict_run_retains_original_price_and_records_profile():
    payload, profile, context = fixtures()
    result = run_price_intelligence_for_company(
        payload, context, profile, expected_company_id="COMPANY-1",
    )
    assert result.pr_value == Decimal("20.25")
    assert result.pr_status == "PR_LIMITED"
    for trace in ("PROFILE-1", "DOC-PROFILE", "E-PROFILE", "RULE-PROFILE", "TRACE-PROFILE"):
        assert trace in result.trace_references


@pytest.mark.parametrize("dimension", MATERIAL_DIMENSIONS)
def test_each_missing_material_dimension_blocks_strict_intake(dimension):
    payload, profile, context = fixtures()
    payload.economic_basis_comparisons = tuple(
        item for item in payload.economic_basis_comparisons if item.dimension != dimension
    )
    report = validate(payload, profile)
    assert not report.complete
    assert f"MATERIAL_COMPARISON_MISSING:H1:{dimension}" in report.issues
    with pytest.raises(PriceCoverageError):
        run_price_intelligence_for_company(
            payload, context, profile, expected_company_id="COMPANY-1",
        )


def test_altered_company_does_not_pass_for_another_tenant():
    payload, profile, _ = fixtures()
    result = validate(payload, profile, company="COMPANY-OTHER")
    assert not result.complete and "COMPANY_SCOPE_MISMATCH" in result.issues


@pytest.mark.parametrize("field,value", [
    ("decision_id", "D-OTHER"),
    ("scenario_id", "SC-OTHER"),
    ("parameters_version", "P-OTHER"),
    ("data_snapshot_id", "SNAP-OTHER"),
])
def test_profile_context_must_match_execution(field, value):
    payload, profile, _ = fixtures()
    forged = profile.model_copy(update={field: value})
    result = validate(payload, forged)
    assert not result.complete
    assert f"PROFILE_CONTEXT_MISMATCH:{field}" in result.issues


def test_missing_profile_evidence_fails_even_if_article_evidence_valid():
    payload, profile, _ = fixtures()
    payload.evidence_validations = tuple(
        item for item in payload.evidence_validations if item.evidence_id != "E-PROFILE"
    )
    report = validate(payload, profile)
    assert not report.complete
    assert "PROFILE_EVIDENCE_UNVALIDATED" in report.issues


def test_missing_declared_target_fails():
    payload, profile, _ = fixtures()
    payload.normalization_basis = payload.normalization_basis.model_copy(
        update={"target_tax_basis": None}
    )
    report = validate(payload, profile)
    assert not report.complete and "MATERIAL_TARGET_MISSING:TAX" in report.issues


def test_unproven_same_basis_fails_on_missing_economic_evidence():
    payload, profile, _ = fixtures()
    payload.economic_basis_evidence = tuple(
        item for item in payload.economic_basis_evidence if item.dimension != "TAX"
    )
    report = validate(payload, profile)
    assert not report.complete
    assert "MATERIAL_EVIDENCE_MISSING:H1:TAX" in report.issues


def test_unknown_rejected_material_dimension_cannot_be_made_equivalent():
    payload, profile, _ = fixtures()
    original = next(
        item for item in payload.economic_basis_comparisons if item.dimension == "DISCOUNT"
    )
    payload.economic_basis_comparisons = tuple(
        item.model_copy(update={"status": "INDETERMINATE", "justification": "Unknown"})
        if item == original else item
        for item in payload.economic_basis_comparisons
    )
    report = validate(payload, profile)
    assert not report.complete
    assert "MATERIAL_EQUIVALENCE_UNRESOLVED:H1:DISCOUNT" in report.issues


def test_empty_reference_set_cannot_be_complete():
    payload, profile, _ = fixtures()
    payload.references = ()
    report = validate(payload, profile)
    assert not report.complete
    assert "PRICE_REFERENCES_MISSING" in report.issues


def test_legacy_C1_still_runs_without_company_coverage_profile():
    payload, profile, context = fixtures()
    payload.economic_basis_comparisons = ()
    payload.economic_basis_evidence = ()
    payload.normalization_basis = None
    # Backward compatibility is explicit: legacy C1 remains a separate
    # entrypoint, not a substitute for tenant admission.
    result = run_price_intelligence(payload, context)
    assert result.pr_value == Decimal("20.25")
    assert result.pr_status == "PR_LIMITED"
    assert not validate(payload, profile).complete


def test_conflicting_duplicate_documentary_reference_is_rejected():
    payload, profile, _ = fixtures()
    second = payload.references[0].model_copy(
        update={"unit_price": Decimal("999")}
    )
    payload.references = (*payload.references, second)
    report = validate(payload, profile)
    assert not report.complete
    assert "CONFLICTING_REFERENCE_ID:H1" in report.issues


def test_reference_without_evidence_does_not_count_as_validated():
    payload, profile, _ = fixtures()
    payload.references = (
        payload.references[0].model_copy(update={"evidence_refs": ()}),
    )
    report = validate(payload, profile)
    assert not report.complete
    assert "REFERENCE_EVIDENCE_UNVALIDATED:H1" in report.issues


def test_price_unit_mismatch_without_authorized_conversion_fails():
    payload, profile, _ = fixtures()
    payload.references = (
        payload.references[0].model_copy(update={"unit": "BOX"}),
    )
    report = validate(payload, profile)
    assert not report.complete
    assert "PRICE_NOT_NORMALIZED:H1" in report.issues


def test_qtg_apto_does_not_replace_price_economic_coverage():
    payload, profile, _ = fixtures()
    qtg = evaluate_quality([QualityCheck("existencia", True, critical=True)])
    assert qtg.status == "APTO"
    payload.economic_basis_comparisons = tuple(
        proof for proof in payload.economic_basis_comparisons
        if proof.dimension != "TAX"
    )
    report = validate(payload, profile)
    assert not report.complete
    assert "MATERIAL_COMPARISON_MISSING:H1:TAX" in report.issues


def test_his003_comparable_does_not_replace_price_economic_coverage():
    determinations = tuple(
        HistoricalComparabilityDimensionDetermination(
            dimension=dimension,
            state="EQUIVALENT",
            authority=HistoricalComparabilityDimensionAuthority(
                dimension=dimension, authority_ref="AUTH-HIS",
                methodology_ref="METHOD-HIS", version="v0.1",
            ),
            evidence_ids=("E-HIS",), trace_refs=("TRACE-HIS",),
        ) for dimension in HIS003_REQUIRED_DIMENSIONS
    )
    assert aggregate_historical_comparability(determinations) == "COMPARABLE"
    payload, profile, _ = fixtures()
    payload.economic_basis_comparisons = tuple(
        proof for proof in payload.economic_basis_comparisons
        if proof.dimension != "TRANSPORT"
    )
    report = validate(payload, profile)
    assert not report.complete
    assert "MATERIAL_COMPARISON_MISSING:H1:TRANSPORT" in report.issues


def _strict_invoker(payload=None, profile=None, assessment_context=None,
                    company="COMPANY-1"):
    default_payload, default_profile, default_assessment = fixtures()
    return build_provenanced_company_price_invoker(
        payload=payload if payload is not None else default_payload,
        assessment_context=assessment_context if assessment_context is not None
                           else default_assessment,
        profile=profile if profile is not None else default_profile,
        expected_company_id=company,
    )


def test_strict_o1_invoker_returns_price_capability_with_profile_trace():
    payload, profile, context = fixtures()
    result = _strict_invoker(payload, profile, context)(
        payload.purchase_operation, payload.decision_context
    )
    assert result.capability == "PRICE"
    assert result.status == O1ExecutionStatus.COMPLETED
    assert result.result_available is True
    assert "PROFILE-1" in result.trace_references
    assert "DOC-PROFILE" in result.trace_references


def test_strict_invoker_connects_to_existing_mvp_execution_without_new_authority():
    payload, profile, context = fixtures()
    execution = run_mvp_execution(
        purchase=payload.purchase_operation,
        context=payload.decision_context,
        policy_version="COMPANY-PRICE-SYNTHETIC-1",
        price_invoker=_strict_invoker(payload, profile, context),
    )
    result = execution.capability_results[0]
    assert result.capability == "PRICE"
    assert result.status == O1ExecutionStatus.COMPLETED
    assert "TRACE-PROFILE" in result.trace_references


@pytest.mark.parametrize("field,foreign", [
    ("decision_id", "FOREIGN-D"),
    ("scenario_id", "FOREIGN-S"),
    ("rules_version", "FOREIGN-R"),
    ("parameters_version", "FOREIGN-P"),
    ("data_snapshot_id", "FOREIGN-SNAPSHOT"),
])
def test_strict_invoker_rejects_foreign_execution_context(field, foreign):
    payload, profile, context = fixtures()
    invoker = _strict_invoker(payload, profile, context)
    tampered = payload.decision_context.model_copy(update={field: foreign})
    with pytest.raises(ValueError, match=field):
        invoker(payload.purchase_operation, tampered)


@pytest.mark.parametrize("field,foreign", [
    ("article_id", "FOREIGN-SKU"),
    ("supplier_id", "FOREIGN-SUPPLIER"),
    ("quantity", Decimal("11")),
    ("unit_price", Decimal("999")),
    ("operation_date", date(2026, 8, 3)),
])
def test_strict_invoker_rejects_altered_purchase(field, foreign):
    payload, profile, context = fixtures()
    invoker = _strict_invoker(payload, profile, context)
    tampered = payload.purchase_operation.model_copy(update={field: foreign})
    with pytest.raises(ValueError, match=field):
        invoker(tampered, payload.decision_context)


def test_strict_invoker_blocks_foreign_company_before_calculating():
    payload, profile, context = fixtures()
    invoker = _strict_invoker(payload, profile, context, company="COMPANY-2")
    with pytest.raises(PriceCoverageError) as exc:
        invoker(payload.purchase_operation, payload.decision_context)
    assert "COMPANY_SCOPE_MISMATCH" in exc.value.report.issues


def test_strict_invoker_blocks_missing_material_without_legacy_fallback(monkeypatch):
    import eios.pricing.company_coverage as strict_boundary

    payload, profile, context = fixtures()
    payload.economic_basis_comparisons = tuple(
        item for item in payload.economic_basis_comparisons
        if item.dimension != "DISCOUNT"
    )
    invoker = _strict_invoker(payload, profile, context)

    def unexpected_legacy_run(*args, **kwargs):
        raise AssertionError("C1 no debe ejecutarse sin cobertura estricta")

    monkeypatch.setattr(strict_boundary, "run_price_intelligence", unexpected_legacy_run)
    with pytest.raises(PriceCoverageError) as exc:
        invoker(payload.purchase_operation, payload.decision_context)
    assert "MATERIAL_COMPARISON_MISSING:H1:DISCOUNT" in exc.value.report.issues


def test_strict_invoker_freezes_inputs_before_late_mutation():
    payload, profile, context = fixtures()
    original_purchase = payload.purchase_operation.model_copy(deep=True)
    original_context = payload.decision_context.model_copy(deep=True)
    invoker = _strict_invoker(payload, profile, context)

    payload.references = ()
    payload.economic_basis_comparisons = ()
    payload.purchase_operation.article_id = "MUTATED-ARTICLE"
    payload.decision_context.rules_version = "MUTATED-RULES"

    result = invoker(original_purchase, original_context)
    assert result.status == O1ExecutionStatus.COMPLETED
    assert result.result_available is True


def test_strict_invoker_cannot_be_repaired_after_construction_by_mutating_caller():
    payload, profile, context = fixtures()
    incomplete = tuple(
        item for item in payload.economic_basis_comparisons
        if item.dimension != "TAX"
    )
    complete = payload.economic_basis_comparisons
    payload.economic_basis_comparisons = incomplete
    invoker = _strict_invoker(payload, profile, context)
    payload.economic_basis_comparisons = complete
    with pytest.raises(PriceCoverageError):
        invoker(payload.purchase_operation, payload.decision_context)


def test_strict_invoker_rejects_untyped_or_untrusted_builder_context():
    payload, profile, context = fixtures()
    with pytest.raises(TypeError, match="PriceCompanyCoverageProfile"):
        _strict_invoker(payload, object(), context)
    with pytest.raises(ValueError, match="expected_company_id"):
        _strict_invoker(payload, profile, context, company="  ")
    with pytest.raises(TypeError, match="PriceIntelligenceInput"):
        _strict_invoker(object(), profile, context)
