from datetime import date
from decimal import Decimal
from inspect import signature

import pytest

from eios.core.models import DecisionContext, Evidence, PurchaseOperation
from eios.rules import (
    R_PROV_001,
    R_PROV_002,
    SupplierAlternativeComparisonRuleInputs,
    SupplierAlternativeOpportunityRuleInputs,
    authorized_rule,
    authorized_rule_metadata,
    evaluate_r_prov_001,
    evaluate_r_prov_002,
    run_domain_rules,
)
from eios.supplier import (
    PROV_COMPARABILITY_EVIDENCE_SOURCE_TYPE,
    PROV_COVERAGE_EVIDENCE_SOURCE_TYPE,
    PROV_OPPORTUNITY_EVIDENCE_SOURCE_TYPE,
    PROV_SIGNIFICANT_IMPROVEMENT_EVIDENCE_SOURCE_TYPE,
    SupplierAlternativeComparabilityDetermination,
    SupplierAlternativeOpportunityDetermination,
    SupplierAlternativeSetCoverage,
    SupplierAlternativeSignificantImprovementDetermination,
    SupplierCandidateEvidence,
    SupplierEvidenceInput,
    evaluate_supplier_evidence,
    supplier_alternative_comparability_ref,
    supplier_alternative_coverage_ref,
    supplier_alternative_opportunity_ref,
    supplier_alternative_purchase_operation_ref,
    supplier_alternative_significant_improvement_ref,
    supplier_evidence_result_ref,
)


EVAL_DATE = date(2026, 9, 22)


def _context() -> DecisionContext:
    return DecisionContext(
        decision_id="D-PROV",
        scenario_id="S-PROV",
        rules_version="rules-v1",
        parameters_version="params-v1",
        data_snapshot_id="snapshot-v1",
    )


def _purchase() -> PurchaseOperation:
    return PurchaseOperation(
        decision_id="D-PROV",
        scenario_id="S-PROV",
        article_id="ART-1",
        supplier_id="SUP-CURRENT",
        quantity=Decimal("10"),
        unit_price=Decimal("12"),
        currency="EUR",
        operation_date=EVAL_DATE,
    )


def _candidate(
    *,
    state: str = "CURRENT_OPERATION_DEMONSTRATED",
) -> SupplierCandidateEvidence:
    kwargs = dict(
        candidate_id="CAND-1",
        supplier_id="SUP-ALT",
        object_id="ART-1",
        state=state,
        trace_refs=("TRACE-CAND-1",),
    )
    if state == "CURRENT_OPERATION_DEMONSTRATED":
        kwargs.update(
            evidence_id="EV-CAND-1",
            source_ref="supplier-source:CAND-1",
            captured_at=EVAL_DATE,
            applicability_ref="supplier-applicability:CAND-1",
        )
    elif state == "REFERENCE_ONLY":
        kwargs.update(
            evidence_id="EV-CAND-1",
            source_ref="supplier-source:CAND-1",
            captured_at=EVAL_DATE,
        )
    return SupplierCandidateEvidence(**kwargs)


def _supplier_input(
    *,
    candidate_state: str = "CURRENT_OPERATION_DEMONSTRATED",
    with_candidate: bool = True,
) -> SupplierEvidenceInput:
    return SupplierEvidenceInput(
        context=_context(),
        purchase_operation=_purchase(),
        company_scope="COMPANY-1",
        evaluation_date=EVAL_DATE,
        candidates=(
            (_candidate(state=candidate_state),)
            if with_candidate
            else ()
        ),
    )


def _binding_refs(supplier_input: SupplierEvidenceInput):
    supplier_result = evaluate_supplier_evidence(supplier_input)
    return (
        supplier_alternative_purchase_operation_ref(supplier_input.purchase_operation),
        supplier_evidence_result_ref(supplier_result),
    )


def _coverage(
    supplier_input: SupplierEvidenceInput,
    state: str,
) -> SupplierAlternativeSetCoverage:
    purchase_ref, supplier_ref = _binding_refs(supplier_input)
    evidence_ids = ("EV-COVERAGE",) if state == "COMPLETE" else ()
    return SupplierAlternativeSetCoverage(
        decision_id=supplier_input.context.decision_id,
        scenario_id=supplier_input.context.scenario_id,
        data_snapshot_id=supplier_input.context.data_snapshot_id,
        parameters_version=supplier_input.context.parameters_version,
        article_id=supplier_input.purchase_operation.article_id,
        purchase_operation_ref=purchase_ref,
        supplier_evidence_ref=supplier_ref,
        state=state,
        authority_ref="authority:prov:coverage",
        methodology_ref="methodology:prov:coverage",
        evidence_ids=evidence_ids,
        trace_refs=("TRACE-COVERAGE",),
    )


def _opportunity(
    supplier_input: SupplierEvidenceInput,
    state: str,
) -> SupplierAlternativeOpportunityDetermination:
    purchase_ref, supplier_ref = _binding_refs(supplier_input)
    evidence_ids = ("EV-OPPORTUNITY",) if state != "NOT_DETERMINABLE" else ()
    return SupplierAlternativeOpportunityDetermination(
        decision_id=supplier_input.context.decision_id,
        scenario_id=supplier_input.context.scenario_id,
        data_snapshot_id=supplier_input.context.data_snapshot_id,
        parameters_version=supplier_input.context.parameters_version,
        article_id=supplier_input.purchase_operation.article_id,
        purchase_operation_ref=purchase_ref,
        candidate_id="CAND-1",
        supplier_id="SUP-ALT",
        supplier_evidence_ref=supplier_ref,
        authority_ref="authority:prov:opportunity",
        methodology_ref="methodology:prov:opportunity",
        state=state,
        evidence_ids=evidence_ids,
        trace_refs=("TRACE-OPPORTUNITY",),
    )


def _comparability(
    supplier_input: SupplierEvidenceInput,
    state: str,
) -> SupplierAlternativeComparabilityDetermination:
    purchase_ref, supplier_ref = _binding_refs(supplier_input)
    evidence_ids = ("EV-COMPARABILITY",) if state != "NOT_DETERMINABLE" else ()
    return SupplierAlternativeComparabilityDetermination(
        decision_id=supplier_input.context.decision_id,
        scenario_id=supplier_input.context.scenario_id,
        data_snapshot_id=supplier_input.context.data_snapshot_id,
        parameters_version=supplier_input.context.parameters_version,
        article_id=supplier_input.purchase_operation.article_id,
        purchase_operation_ref=purchase_ref,
        candidate_id="CAND-1",
        supplier_id="SUP-ALT",
        supplier_evidence_ref=supplier_ref,
        authority_ref="authority:prov:comparability",
        methodology_ref="methodology:prov:comparability",
        state=state,
        evidence_ids=evidence_ids,
        trace_refs=("TRACE-COMPARABILITY",),
    )


def _significant(
    supplier_input: SupplierEvidenceInput,
    state: str,
) -> SupplierAlternativeSignificantImprovementDetermination:
    purchase_ref, supplier_ref = _binding_refs(supplier_input)
    evidence_ids = ("EV-SIGNIFICANT",) if state != "NOT_DETERMINABLE" else ()
    return SupplierAlternativeSignificantImprovementDetermination(
        decision_id=supplier_input.context.decision_id,
        scenario_id=supplier_input.context.scenario_id,
        data_snapshot_id=supplier_input.context.data_snapshot_id,
        parameters_version=supplier_input.context.parameters_version,
        article_id=supplier_input.purchase_operation.article_id,
        purchase_operation_ref=purchase_ref,
        candidate_id="CAND-1",
        supplier_id="SUP-ALT",
        supplier_evidence_ref=supplier_ref,
        authority_ref="authority:prov:significant",
        methodology_ref="methodology:prov:significant",
        state=state,
        dimensions=("PRICE",),
        evidence_ids=evidence_ids,
        trace_refs=("TRACE-SIGNIFICANT",),
    )


def _evidence(
    *,
    evidence_id: str,
    source_type: str,
    demonstration_ref: str,
) -> Evidence:
    return Evidence(
        evidence_id=evidence_id,
        source_type=source_type,
        source_ref=f"source:{evidence_id}",
        captured_at=EVAL_DATE,
        state="DEMONSTRATED",
        demonstration_ref=demonstration_ref,
    )


def _coverage_evidence(coverage: SupplierAlternativeSetCoverage) -> Evidence:
    return _evidence(
        evidence_id="EV-COVERAGE",
        source_type=PROV_COVERAGE_EVIDENCE_SOURCE_TYPE,
        demonstration_ref=supplier_alternative_coverage_ref(coverage),
    )


def _opportunity_evidence(
    determination: SupplierAlternativeOpportunityDetermination,
) -> Evidence:
    return _evidence(
        evidence_id="EV-OPPORTUNITY",
        source_type=PROV_OPPORTUNITY_EVIDENCE_SOURCE_TYPE,
        demonstration_ref=supplier_alternative_opportunity_ref(determination),
    )


def _comparability_evidence(
    determination: SupplierAlternativeComparabilityDetermination,
) -> Evidence:
    return _evidence(
        evidence_id="EV-COMPARABILITY",
        source_type=PROV_COMPARABILITY_EVIDENCE_SOURCE_TYPE,
        demonstration_ref=supplier_alternative_comparability_ref(determination),
    )


def _significant_evidence(
    determination: SupplierAlternativeSignificantImprovementDetermination,
) -> Evidence:
    return _evidence(
        evidence_id="EV-SIGNIFICANT",
        source_type=PROV_SIGNIFICANT_IMPROVEMENT_EVIDENCE_SOURCE_TYPE,
        demonstration_ref=supplier_alternative_significant_improvement_ref(
            determination
        ),
    )


def test_r_prov_001_true_does_not_require_complete_coverage():
    supplier_input = _supplier_input()
    coverage = _coverage(supplier_input, "PARTIAL")
    opportunity = _opportunity(supplier_input, "POTENTIALLY_BETTER")

    result = evaluate_r_prov_001(
        purchase=supplier_input.purchase_operation,
        context=supplier_input.context,
        rule=authorized_rule(R_PROV_001, "rules-v1"),
        supplier_input=supplier_input,
        coverage=coverage,
        opportunity_determinations=(opportunity,),
        prov_evidences=(_opportunity_evidence(opportunity),),
    )

    assert result.status == "EVALUABLE"
    assert result.outcome == "TRUE"


def test_r_prov_001_false_requires_complete_and_exhaustive_negative_proof():
    supplier_input = _supplier_input()
    coverage = _coverage(supplier_input, "COMPLETE")
    opportunity = _opportunity(supplier_input, "NOT_POTENTIALLY_BETTER")

    result = evaluate_r_prov_001(
        purchase=supplier_input.purchase_operation,
        context=supplier_input.context,
        rule=authorized_rule(R_PROV_001, "rules-v1"),
        supplier_input=supplier_input,
        coverage=coverage,
        opportunity_determinations=(opportunity,),
        prov_evidences=(
            _coverage_evidence(coverage),
            _opportunity_evidence(opportunity),
        ),
    )

    assert result.status == "EVALUABLE"
    assert result.outcome == "FALSE"


def test_r_prov_001_partial_negative_remains_not_evaluable():
    supplier_input = _supplier_input()
    coverage = _coverage(supplier_input, "PARTIAL")
    opportunity = _opportunity(supplier_input, "NOT_POTENTIALLY_BETTER")

    result = evaluate_r_prov_001(
        purchase=supplier_input.purchase_operation,
        context=supplier_input.context,
        rule=authorized_rule(R_PROV_001, "rules-v1"),
        supplier_input=supplier_input,
        coverage=coverage,
        opportunity_determinations=(opportunity,),
        prov_evidences=(_opportunity_evidence(opportunity),),
    )

    assert result.status == "NOT_EVALUABLE"
    assert result.outcome is None


def test_r_prov_001_complete_with_unresolved_candidate_is_not_evaluable():
    supplier_input = _supplier_input(candidate_state="REFERENCE_ONLY")
    coverage = _coverage(supplier_input, "COMPLETE")
    opportunity = _opportunity(supplier_input, "NOT_POTENTIALLY_BETTER")

    result = evaluate_r_prov_001(
        purchase=supplier_input.purchase_operation,
        context=supplier_input.context,
        rule=authorized_rule(R_PROV_001, "rules-v1"),
        supplier_input=supplier_input,
        coverage=coverage,
        opportunity_determinations=(opportunity,),
        prov_evidences=(
            _coverage_evidence(coverage),
            _opportunity_evidence(opportunity),
        ),
    )

    assert result.status == "NOT_EVALUABLE"
    assert result.outcome is None


def test_r_prov_001_complete_empty_universe_can_prove_false():
    supplier_input = _supplier_input(with_candidate=False)
    coverage = _coverage(supplier_input, "COMPLETE")

    result = evaluate_r_prov_001(
        purchase=supplier_input.purchase_operation,
        context=supplier_input.context,
        rule=authorized_rule(R_PROV_001, "rules-v1"),
        supplier_input=supplier_input,
        coverage=coverage,
        opportunity_determinations=(),
        prov_evidences=(_coverage_evidence(coverage),),
    )

    assert result.status == "EVALUABLE"
    assert result.outcome == "FALSE"


def test_r_prov_002_true_requires_same_evidenced_candidate():
    supplier_input = _supplier_input()
    coverage = _coverage(supplier_input, "PARTIAL")
    comparability = _comparability(supplier_input, "COMPARABLE")
    significant = _significant(supplier_input, "SIGNIFICANT_IMPROVEMENT")

    result = evaluate_r_prov_002(
        purchase=supplier_input.purchase_operation,
        context=supplier_input.context,
        rule=authorized_rule(R_PROV_002, "rules-v1"),
        supplier_input=supplier_input,
        coverage=coverage,
        comparability_determinations=(comparability,),
        significant_improvement_determinations=(significant,),
        prov_evidences=(
            _comparability_evidence(comparability),
            _significant_evidence(significant),
        ),
    )

    assert result.status == "EVALUABLE"
    assert result.outcome == "TRUE"


def test_r_prov_002_false_requires_complete_and_fully_determined_universe():
    supplier_input = _supplier_input()
    coverage = _coverage(supplier_input, "COMPLETE")
    comparability = _comparability(supplier_input, "COMPARABLE")
    significant = _significant(supplier_input, "NO_SIGNIFICANT_IMPROVEMENT")

    result = evaluate_r_prov_002(
        purchase=supplier_input.purchase_operation,
        context=supplier_input.context,
        rule=authorized_rule(R_PROV_002, "rules-v1"),
        supplier_input=supplier_input,
        coverage=coverage,
        comparability_determinations=(comparability,),
        significant_improvement_determinations=(significant,),
        prov_evidences=(
            _coverage_evidence(coverage),
            _comparability_evidence(comparability),
            _significant_evidence(significant),
        ),
    )

    assert result.status == "EVALUABLE"
    assert result.outcome == "FALSE"


def test_r_prov_002_indeterminate_carrier_blocks_false():
    supplier_input = _supplier_input()
    coverage = _coverage(supplier_input, "COMPLETE")
    comparability = _comparability(supplier_input, "COMPARABLE")
    significant = _significant(supplier_input, "NOT_DETERMINABLE")

    result = evaluate_r_prov_002(
        purchase=supplier_input.purchase_operation,
        context=supplier_input.context,
        rule=authorized_rule(R_PROV_002, "rules-v1"),
        supplier_input=supplier_input,
        coverage=coverage,
        comparability_determinations=(comparability,),
        significant_improvement_determinations=(significant,),
        prov_evidences=(
            _coverage_evidence(coverage),
            _comparability_evidence(comparability),
        ),
    )

    assert result.status == "NOT_EVALUABLE"
    assert result.outcome is None


def test_supplier_evidence_ref_mismatch_fails_closed():
    supplier_input = _supplier_input()
    coverage = _coverage(supplier_input, "PARTIAL").model_copy(
        update={"supplier_evidence_ref": "supplier_evidence:forged"}
    )
    opportunity = _opportunity(supplier_input, "POTENTIALLY_BETTER")

    with pytest.raises(ValueError, match="supplier_evidence_ref incompatible"):
        evaluate_r_prov_001(
            purchase=supplier_input.purchase_operation,
            context=supplier_input.context,
            rule=authorized_rule(R_PROV_001, "rules-v1"),
            supplier_input=supplier_input,
            coverage=coverage,
            opportunity_determinations=(opportunity,),
            prov_evidences=(_opportunity_evidence(opportunity),),
        )


def test_purchase_operation_ref_mismatch_fails_closed():
    supplier_input = _supplier_input()
    coverage = _coverage(supplier_input, "PARTIAL")
    opportunity = _opportunity(supplier_input, "POTENTIALLY_BETTER").model_copy(
        update={"purchase_operation_ref": "prov_purchase:forged"}
    )

    with pytest.raises(ValueError, match="purchase_operation_ref incompatible"):
        evaluate_r_prov_001(
            purchase=supplier_input.purchase_operation,
            context=supplier_input.context,
            rule=authorized_rule(R_PROV_001, "rules-v1"),
            supplier_input=supplier_input,
            coverage=coverage,
            opportunity_determinations=(opportunity,),
            prov_evidences=(),
        )


def test_candidate_supplier_mismatch_fails_closed():
    supplier_input = _supplier_input()
    coverage = _coverage(supplier_input, "PARTIAL")
    opportunity = _opportunity(supplier_input, "POTENTIALLY_BETTER").model_copy(
        update={"supplier_id": "SUP-OTHER"}
    )

    with pytest.raises(ValueError, match="supplier_id incompatible"):
        evaluate_r_prov_001(
            purchase=supplier_input.purchase_operation,
            context=supplier_input.context,
            rule=authorized_rule(R_PROV_001, "rules-v1"),
            supplier_input=supplier_input,
            coverage=coverage,
            opportunity_determinations=(opportunity,),
            prov_evidences=(),
        )


def test_forged_determination_evidence_is_rejected():
    supplier_input = _supplier_input()
    coverage = _coverage(supplier_input, "PARTIAL")
    opportunity = _opportunity(supplier_input, "POTENTIALLY_BETTER")
    forged = _evidence(
        evidence_id="EV-OPPORTUNITY",
        source_type=PROV_OPPORTUNITY_EVIDENCE_SOURCE_TYPE,
        demonstration_ref="prov_opportunity:forged",
    )

    with pytest.raises(ValueError, match="carrier exacto"):
        evaluate_r_prov_001(
            purchase=supplier_input.purchase_operation,
            context=supplier_input.context,
            rule=authorized_rule(R_PROV_001, "rules-v1"),
            supplier_input=supplier_input,
            coverage=coverage,
            opportunity_determinations=(opportunity,),
            prov_evidences=(forged,),
        )


def test_rule_apis_do_not_accept_detached_supplier_result():
    params_001 = signature(evaluate_r_prov_001).parameters
    params_002 = signature(evaluate_r_prov_002).parameters
    assert "supplier_result" not in params_001
    assert "supplier_result" not in params_002
    assert "supplier_input" in params_001
    assert "supplier_input" in params_002


def test_structural_supplier_comparison_is_not_a_rule_input():
    params_002 = signature(evaluate_r_prov_002).parameters
    assert "structural_comparisons" not in params_002
    assert "difference_decimal" not in params_002


def test_metadata_matches_authorized_prov_rules():
    metadata_001 = authorized_rule_metadata(R_PROV_001, "rules-v1")
    metadata_002 = authorized_rule_metadata(R_PROV_002, "rules-v1")
    assert (metadata_001.effect, metadata_001.severity, metadata_001.active_result) == (
        "R2",
        "MEDIA",
        "NEGOCIAR",
    )
    assert (metadata_002.effect, metadata_002.severity, metadata_002.active_result) == (
        "R2",
        "ALTA",
        "NEGOCIAR",
    )


def test_orchestrator_runs_both_prov_rules_independently():
    supplier_input = _supplier_input()
    coverage = _coverage(supplier_input, "PARTIAL")
    opportunity = _opportunity(supplier_input, "POTENTIALLY_BETTER")
    comparability = _comparability(supplier_input, "COMPARABLE")
    significant = _significant(supplier_input, "SIGNIFICANT_IMPROVEMENT")

    result = run_domain_rules(
        purchase=supplier_input.purchase_operation,
        context=supplier_input.context,
        base_result="COMPRAR",
        supplier_alternative_opportunity=SupplierAlternativeOpportunityRuleInputs(
            supplier_input=supplier_input,
            coverage=coverage,
            opportunity_determinations=(opportunity,),
            prov_evidences=(_opportunity_evidence(opportunity),),
        ),
        supplier_alternative_comparison=SupplierAlternativeComparisonRuleInputs(
            supplier_input=supplier_input,
            coverage=coverage,
            comparability_determinations=(comparability,),
            significant_improvement_determinations=(significant,),
            prov_evidences=(
                _comparability_evidence(comparability),
                _significant_evidence(significant),
            ),
        ),
    )

    assert result.executed_rule_ids == (R_PROV_001, R_PROV_002)
    assert tuple(item.outcome for item in result.assessments) == ("TRUE", "TRUE")
    assert result.crc_result.consolidated_result == "NEGOCIAR"
