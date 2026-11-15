"""Synthetic source-recomputed PRICE/HIS003 identity and authority regressions."""
from datetime import date
from decimal import Decimal

import pytest
from pydantic import ValidationError

from eios.core.models import (
    DecisionContext, Evidence, EvidenceValidation, PurchaseOperation, Rule,
)
from eios.core.price_his003_reconciliation import (
    HistoricalReferenceSourceBundle, reconcile_price_and_his003,
)
from eios.pricing.company_coverage import PriceCompanyCoverageProfile, PriceCoverageError
from eios.pricing.historical_comparability import (
    HIS003_DIMENSION_EVIDENCE_SOURCE_TYPE, HIS003_REQUIRED_DIMENSIONS,
    HistoricalComparabilityDimensionAuthority,
    HistoricalComparabilityDimensionDetermination,
    historical_comparability_dimension_ref,
)
from eios.pricing.models import (
    EconomicBasisEvidence, NormalizationBasis, PriceEconomicBasisComparison,
    PriceIntelligenceAssessmentContext, PriceIntelligenceInput, PriceReference,
)
from eios.pricing.representativeness import RepresentativenessObservation
from eios.pricing.sufficiency import SufficiencyObservation
from eios.rules.history_comparability import R_HIS_003


ECONOMIC_DIMENSIONS = (
    "QUANTITY", "TAX", "TRANSPORT", "DISCOUNT", "SURCHARGE", "COMMERCIAL",
)
BASES = {
    "TAX": "SIN_IVA", "TRANSPORT": "SIN_PORTES", "DISCOUNT": "NETO",
    "SURCHARGE": "SIN_RECARGOS", "COMMERCIAL": "NO_APLICA",
}


def fixture(*, history_states=None):
    history_states = history_states or {}
    operation = PurchaseOperation(
        decision_id="D1", scenario_id="S1", article_id="SKU1",
        supplier_id="SUP1", quantity=Decimal("10"), unit_price=Decimal("20"),
        currency="EUR", operation_date=date(2026, 9, 22),
    )
    context = DecisionContext(
        decision_id="D1", scenario_id="S1", rules_version="RULES-v1",
        parameters_version="PARAMS-v1", data_snapshot_id="SNAP-v1",
    )
    reference = PriceReference(
        source_transaction_id="REF1", article_identity="SKU1",
        supplier_identity="SUP1", quantity=Decimal("10"), unit="EA",
        unit_price=Decimal("20.25"), currency="EUR",
        operation_date=date(2026, 8, 1), evidence_refs=("E1",),
    )
    comparisons = tuple(PriceEconomicBasisComparison(
        reference_id="REF1", dimension=dim,
        source_basis="10" if dim == "QUANTITY" else BASES[dim],
        target_basis="10" if dim == "QUANTITY" else BASES[dim],
        status="EQUIVALENT", source_ref="DOC-PRICE-" + dim,
        evidence_refs=("E1",), rule_reference="RULE-ECON",
        trace_reference="TRACE-ECON-" + dim,
    ) for dim in ECONOMIC_DIMENSIONS)
    economic = tuple(EconomicBasisEvidence(
        reference_id="REF1", dimension=dim, status="RESOLVED",
        evidence_refs=("E1",), rule_reference="RULE-ECON",
        trace_reference="TRACE-ECON-" + dim,
    ) for dim in ECONOMIC_DIMENSIONS)
    payload = PriceIntelligenceInput(
        decision_context=context, purchase_operation=operation,
        references=(reference,), evidence_validations=(
            EvidenceValidation(evidence_id="E1", status="VALID", reason="Synthetic"),
            EvidenceValidation(evidence_id="EP", status="VALID", reason="Synthetic"),
        ),
        normalization_basis=NormalizationBasis(
            target_unit="EA", target_tax_basis="SIN_IVA",
            target_transport_basis="SIN_PORTES", target_discount_basis="NETO",
            target_surcharge_basis="SIN_RECARGOS", target_commercial_basis="NO_APLICA",
            basis_reference="BASIS", rule_reference="RULE-ECON",
            trace_reference="TRACE-BASIS",
        ),
        economic_basis_evidence=economic,
        economic_basis_comparisons=comparisons,
        methodology_version="C1-v1",
    )
    assessment = PriceIntelligenceAssessmentContext(
        temporal={"REF1": ("ELIGIBLE", "RULE-TIME")},
        representativeness={
            "REF1": RepresentativenessObservation(
                ordinary_market_context=True, exceptional_condition=False,
                material_commercial_distortion=False, evidence_refs=("E1",),
                rule_reference="RULE-REP", trace_reference="TRACE-REP",
            ),
        },
        sufficiency=SufficiencyObservation(
            selected_reference_ids=("REF1",), evidence_refs=("E1",),
            rule_reference="RULE-SUFF", trace_reference="TRACE-SUFF",
            evidence_sufficient=True, contradictions_resolved=True,
        ),
    )
    profile = PriceCompanyCoverageProfile(
        profile_id="PROFILE1", company_id="COMPANY1",
        decision_id="D1", scenario_id="S1", parameters_version="PARAMS-v1",
        data_snapshot_id="SNAP-v1", source_ref="SOURCE-PROFILE",
        evidence_id="EP", rule_reference="RULE-PROFILE",
        trace_reference="TRACE-PROFILE",
    )
    determinations = []
    evidences = []
    for dim in HIS003_REQUIRED_DIMENSIONS:
        state = history_states.get(dim, "EQUIVALENT")
        selected_id = "E-HIS-" + dim
        determination = HistoricalComparabilityDimensionDetermination(
            dimension=dim, state=state,
            authority=HistoricalComparabilityDimensionAuthority(
                dimension=dim, authority_ref="AUTH-" + dim,
                methodology_ref="METHOD-" + dim, version="v0.1",
            ),
            evidence_ids=() if state == "NOT_DETERMINABLE" else (selected_id,),
            trace_refs=("TRACE-HIS-" + dim,),
            reason="No documentary conclusion" if state == "NOT_DETERMINABLE" else None,
        )
        determinations.append(determination)
        if determination.evidence_ids:
            evidences.append(Evidence(
                evidence_id=selected_id,
                source_type=HIS003_DIMENSION_EVIDENCE_SOURCE_TYPE,
                source_ref="SOURCE-HIS-" + dim,
                captured_at=operation.operation_date, state="DEMONSTRATED",
                demonstration_ref=historical_comparability_dimension_ref(determination),
            ))
    bundle = HistoricalReferenceSourceBundle(
        reference_id="REF1", dimension_determinations=tuple(determinations),
        dimension_evidences=tuple(evidences),
    )
    return {
        "payload": payload, "assessment_context": assessment, "profile": profile,
        "expected_company_id": "COMPANY1", "purchase": operation,
        "context": context, "rule": Rule(
            rule_id=R_HIS_003, version=context.rules_version, requires_evidence=True
        ), "historical_sources": (bundle,),
    }


def run(data):
    return reconcile_price_and_his003(**data)


def test_matching_sources_reexecute_both_domains_without_decision_authority():
    result = run(fixture())
    assert result.price_result.pr_value == Decimal("20.25")
    assert result.price_result.pr_status == "PR_LIMITED"
    assert len(result.historical_references) == 1
    history = result.historical_references[0]
    assert history.transaction_id == "REF1"
    assert history.reference_fingerprint.startswith("his003_reference:")
    assert history.assessment.rule_id == R_HIS_003
    assert history.assessment.status == "EVALUABLE"
    assert history.assessment.outcome == "FALSE"
    assert len(history.evidence_ids) == len(HIS003_REQUIRED_DIMENSIONS)
    assert len(history.trace_refs) == len(HIS003_REQUIRED_DIMENSIONS)
    assert result.qtg_status == "NOT_ASSESSED"
    assert result.decision_authority is False


def test_material_commercial_difference_preserves_independent_price_result():
    data = fixture(history_states={"PAYMENT_TERM": "MATERIALLY_DIFFERENT"})
    result = run(data)
    assert result.price_result.pr_value == Decimal("20.25")
    assert result.historical_references[0].assessment.outcome == "TRUE"
    assert result.qtg_status == "NOT_ASSESSED"
    assert result.decision_authority is False


def test_historical_missing_dimension_remains_not_evaluable_not_fake_apto():
    data = fixture(history_states={"RAPPELS": "NOT_DETERMINABLE"})
    result = run(data)
    assert result.historical_references[0].assessment.status == "NOT_EVALUABLE"
    assert result.historical_references[0].assessment.outcome is None
    assert result.qtg_status == "NOT_ASSESSED"


def test_mismatched_snapshot_is_rejected_before_execution():
    data = fixture()
    data["context"] = data["context"].model_copy(
        update={"data_snapshot_id": "FOREIGN-SNAPSHOT"}
    )
    with pytest.raises(ValueError, match="DecisionContext"):
        run(data)


def test_mismatched_purchase_is_rejected_before_execution():
    data = fixture()
    data["purchase"] = data["purchase"].model_copy(
        update={"unit_price": Decimal("12")}
    )
    with pytest.raises(ValueError, match="purchase"):
        run(data)


def test_mismatched_his003_rule_version_rejected():
    data = fixture()
    data["rule"] = data["rule"].model_copy(update={"version": "RULES-OTHER"})
    with pytest.raises(ValueError, match="rule identity"):
        run(data)


def test_mismatched_his003_rule_id_rejected():
    data = fixture()
    data["rule"] = data["rule"].model_copy(update={"rule_id": "R-HIS-002"})
    with pytest.raises(ValueError, match="rule identity"):
        run(data)


def test_foreign_company_blocked_by_strict_price_admission():
    data = fixture()
    data["expected_company_id"] = "OTHER-COMPANY"
    with pytest.raises(PriceCoverageError):
        run(data)


@pytest.mark.parametrize("reference_id", ["OTHER-REF", "REF2"])
def test_foreign_historical_source_set_rejected(reference_id):
    data = fixture()
    source = data["historical_sources"][0]
    data["historical_sources"] = (
        source.model_copy(update={"reference_id": reference_id}),
    )
    with pytest.raises(ValueError, match="reference set mismatch"):
        run(data)


def test_missing_historical_source_rejected():
    data = fixture()
    data["historical_sources"] = ()
    with pytest.raises(ValueError, match="reference set mismatch"):
        run(data)


def test_duplicate_historical_source_rejected():
    data = fixture()
    data["historical_sources"] *= 2
    with pytest.raises(ValueError, match="Duplicate HIS003"):
        run(data)


def test_forged_historical_evidence_rejected_by_his003_producer():
    data = fixture()
    source = data["historical_sources"][0]
    forged_first = source.dimension_evidences[0].model_copy(
        update={"demonstration_ref": "his003_dimension:forged"}
    )
    data["historical_sources"] = (
        source.model_copy(update={
            "dimension_evidences": (forged_first, *source.dimension_evidences[1:]),
        }),
    )
    with pytest.raises(ValueError, match="determinación exacta"):
        run(data)


def test_wrong_historical_evidence_date_rejected():
    data = fixture()
    source = data["historical_sources"][0]
    wrong_first = source.dimension_evidences[0].model_copy(
        update={"captured_at": date(2026, 9, 21)}
    )
    data["historical_sources"] = (
        source.model_copy(update={
            "dimension_evidences": (wrong_first, *source.dimension_evidences[1:]),
        }),
    )
    with pytest.raises(ValueError, match="evaluation_date"):
        run(data)


def test_wrong_historical_evidence_type_rejected():
    data = fixture()
    source = data["historical_sources"][0]
    wrong_first = source.dimension_evidences[0].model_copy(
        update={"source_type": "UNKNOWN"}
    )
    data["historical_sources"] = (
        source.model_copy(update={
            "dimension_evidences": (wrong_first, *source.dimension_evidences[1:]),
        }),
    )
    with pytest.raises(ValueError, match="source_type"):
        run(data)


def test_reference_article_mismatch_rejected():
    data = fixture()
    bad_reference = data["payload"].references[0].model_copy(
        update={"article_identity": "OTHER-SKU"}
    )
    data["payload"].references = (bad_reference,)
    with pytest.raises(ValueError, match="reference article"):
        run(data)


def test_untyped_historical_bundle_rejected():
    data = fixture()
    data["historical_sources"] = (object(),)
    with pytest.raises(TypeError, match="HistoricalReferenceSourceBundle"):
        run(data)


def test_historical_source_is_not_a_detached_result():
    data = fixture()
    source = data["historical_sources"][0]
    with pytest.raises(ValidationError):
        HistoricalReferenceSourceBundle(
            reference_id=source.reference_id,
            dimension_determinations=source.dimension_determinations,
            dimension_evidences=source.dimension_evidences,
            computed_result="EVALUABLE",
        )


def test_strict_price_missing_economic_basis_fails_with_historical_inputs_present():
    data = fixture()
    data["payload"].economic_basis_comparisons = (
        data["payload"].economic_basis_comparisons[:-1]
    )
    with pytest.raises(PriceCoverageError):
        run(data)


def test_reconciliation_does_not_mutate_source_payload():
    data = fixture()
    before = data["payload"].model_dump(mode="json")
    run(data)
    assert data["payload"].model_dump(mode="json") == before
