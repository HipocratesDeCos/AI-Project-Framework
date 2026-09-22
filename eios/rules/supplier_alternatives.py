"""Provenance-safe executable bridges for R-PROV-001 and R-PROV-002."""
from __future__ import annotations

from collections.abc import Iterable

from eios.core.models import Assessment, DecisionContext, Evidence, PurchaseOperation, Rule
from eios.core.validation import validate_evidence
from eios.supplier.alternatives import (
    PROV_COMPARABILITY_EVIDENCE_SOURCE_TYPE,
    PROV_COVERAGE_EVIDENCE_SOURCE_TYPE,
    PROV_OPPORTUNITY_EVIDENCE_SOURCE_TYPE,
    PROV_SIGNIFICANT_IMPROVEMENT_EVIDENCE_SOURCE_TYPE,
    SupplierAlternativeComparabilityDetermination,
    SupplierAlternativeOpportunityDetermination,
    SupplierAlternativeSetCoverage,
    SupplierAlternativeSignificantImprovementDetermination,
    supplier_alternative_comparability_ref,
    supplier_alternative_coverage_ref,
    supplier_alternative_opportunity_ref,
    supplier_alternative_purchase_operation_ref,
    supplier_alternative_significant_improvement_ref,
    supplier_evidence_result_ref,
)
from eios.supplier.engine import evaluate_supplier_evidence
from eios.supplier.models import CandidateResolution, SupplierEvidenceInput, SupplierEvidenceResult


R_PROV_001 = "R-PROV-001"
R_PROV_002 = "R-PROV-002"


def _validate_rule_identity(
    *,
    purchase: PurchaseOperation,
    context: DecisionContext,
    rule: Rule,
    expected_rule_id: str,
) -> None:
    if purchase.decision_id != context.decision_id:
        raise ValueError("PurchaseOperation y DecisionContext tienen decision_id distintos")
    if purchase.scenario_id != context.scenario_id:
        raise ValueError("PurchaseOperation y DecisionContext tienen scenario_id distintos")
    if rule.rule_id != expected_rule_id:
        raise ValueError(f"El bridge solo evalúa {expected_rule_id}")
    if rule.version != context.rules_version:
        raise ValueError("Rule.version incompatible con DecisionContext.rules_version")
    if not rule.requires_evidence:
        raise ValueError(f"{expected_rule_id} requiere evidencia")


def _rebuild_supplier_evidence(
    *,
    purchase: PurchaseOperation,
    context: DecisionContext,
    supplier_input: SupplierEvidenceInput,
) -> SupplierEvidenceResult:
    if supplier_input.purchase_operation != purchase:
        raise ValueError(
            "SupplierEvidenceInput.purchase_operation no coincide con la operación evaluada"
        )
    if supplier_input.context != context:
        raise ValueError(
            "SupplierEvidenceInput.context no coincide con DecisionContext evaluado"
        )

    result = evaluate_supplier_evidence(supplier_input)
    identity = result.identity
    if identity.decision_id != context.decision_id:
        raise ValueError("SupplierEvidenceResult decision_id incompatible")
    if identity.scenario_id != context.scenario_id:
        raise ValueError("SupplierEvidenceResult scenario_id incompatible")
    if identity.rules_version != context.rules_version:
        raise ValueError("SupplierEvidenceResult rules_version incompatible")
    if identity.parameters_version != context.parameters_version:
        raise ValueError("SupplierEvidenceResult parameters_version incompatible")
    if identity.data_snapshot_id != context.data_snapshot_id:
        raise ValueError("SupplierEvidenceResult data_snapshot_id incompatible")
    if identity.article_id != purchase.article_id:
        raise ValueError("SupplierEvidenceResult article_id incompatible")
    if result.current_supplier_id != purchase.supplier_id:
        raise ValueError("SupplierEvidenceResult current_supplier_id incompatible")
    return result


def _validate_common_binding(
    carrier,
    *,
    purchase: PurchaseOperation,
    context: DecisionContext,
    expected_purchase_ref: str,
    expected_supplier_ref: str,
) -> None:
    expected = {
        "decision_id": context.decision_id,
        "scenario_id": context.scenario_id,
        "data_snapshot_id": context.data_snapshot_id,
        "parameters_version": context.parameters_version,
        "article_id": purchase.article_id,
        "purchase_operation_ref": expected_purchase_ref,
        "supplier_evidence_ref": expected_supplier_ref,
    }
    for field, value in expected.items():
        if getattr(carrier, field) != value:
            raise ValueError(f"PROV {field} incompatible con la ejecución actual")


def _evidence_map(evidences: tuple[Evidence, ...]) -> dict[str, Evidence]:
    ids = tuple(item.evidence_id for item in evidences)
    if len(ids) != len(set(ids)):
        raise ValueError("prov_evidences contiene evidence_id duplicados")
    return {item.evidence_id: item for item in evidences}


def _validate_carrier_evidence(
    *,
    evidence_ids: tuple[str, ...],
    evidence_by_id: dict[str, Evidence],
    source_type: str,
    exact_ref: str,
    requires_demonstrated: bool,
) -> None:
    for evidence_id in evidence_ids:
        evidence = evidence_by_id.get(evidence_id)
        if evidence is None:
            raise ValueError(f"PROV evidence_id desconocido: {evidence_id}")
        if evidence.source_type != source_type:
            raise ValueError("PROV evidence source_type incompatible")
        if evidence.state == "DEMONSTRATED":
            if evidence.demonstration_ref != exact_ref:
                raise ValueError("PROV evidence no está vinculada al carrier exacto")
            if validate_evidence(evidence).status != "VALID":
                raise ValueError("PROV evidence DEMONSTRATED debe ser válida")
        elif requires_demonstrated:
            raise ValueError("Una determinación PROV concluyente requiere evidence DEMONSTRATED")


def _resolution_map(
    supplier_result: SupplierEvidenceResult,
) -> dict[str, CandidateResolution]:
    return {
        resolution.candidate_id: resolution
        for resolution in supplier_result.candidate_resolutions
    }


def _index_and_validate_determinations(
    determinations: tuple,
    *,
    purchase: PurchaseOperation,
    context: DecisionContext,
    supplier_result: SupplierEvidenceResult,
    expected_purchase_ref: str,
    expected_supplier_ref: str,
    evidence_by_id: dict[str, Evidence],
    source_type: str,
    ref_builder,
    indeterminate_state: str,
) -> dict[str, object]:
    candidate_ids = tuple(item.candidate_id for item in determinations)
    if len(candidate_ids) != len(set(candidate_ids)):
        raise ValueError("PROV contiene determinaciones duplicadas para candidate_id")

    resolutions = _resolution_map(supplier_result)
    indexed: dict[str, object] = {}
    for determination in determinations:
        _validate_common_binding(
            determination,
            purchase=purchase,
            context=context,
            expected_purchase_ref=expected_purchase_ref,
            expected_supplier_ref=expected_supplier_ref,
        )
        resolution = resolutions.get(determination.candidate_id)
        if resolution is None:
            raise ValueError("PROV determination referencia candidate_id inexistente")
        if determination.supplier_id != resolution.supplier_id:
            raise ValueError("PROV determination supplier_id incompatible con candidate_id")
        _validate_carrier_evidence(
            evidence_ids=determination.evidence_ids,
            evidence_by_id=evidence_by_id,
            source_type=source_type,
            exact_ref=ref_builder(determination),
            requires_demonstrated=determination.state != indeterminate_state,
        )
        indexed[determination.candidate_id] = determination
    return indexed


def _validate_coverage(
    coverage: SupplierAlternativeSetCoverage,
    *,
    purchase: PurchaseOperation,
    context: DecisionContext,
    expected_purchase_ref: str,
    expected_supplier_ref: str,
    evidence_by_id: dict[str, Evidence],
) -> None:
    _validate_common_binding(
        coverage,
        purchase=purchase,
        context=context,
        expected_purchase_ref=expected_purchase_ref,
        expected_supplier_ref=expected_supplier_ref,
    )
    _validate_carrier_evidence(
        evidence_ids=coverage.evidence_ids,
        evidence_by_id=evidence_by_id,
        source_type=PROV_COVERAGE_EVIDENCE_SOURCE_TYPE,
        exact_ref=supplier_alternative_coverage_ref(coverage),
        requires_demonstrated=coverage.state == "COMPLETE",
    )


def _reject_unreferenced_evidence(
    evidence_by_id: dict[str, Evidence],
    carriers: Iterable,
) -> None:
    referenced = {
        evidence_id
        for carrier in carriers
        for evidence_id in carrier.evidence_ids
    }
    extra = set(evidence_by_id) - referenced
    if extra:
        raise ValueError(
            "prov_evidences contiene evidencia no referenciada por carriers PROV"
        )


def _assessment_evidence_ids(
    supplier_result: SupplierEvidenceResult,
    carriers: Iterable,
) -> list[str]:
    values: list[str] = []
    for resolution in supplier_result.candidate_resolutions:
        values.extend(resolution.evidence_refs)
    for carrier in carriers:
        values.extend(carrier.evidence_ids)
    return list(dict.fromkeys(values))


def evaluate_r_prov_001(
    *,
    purchase: PurchaseOperation,
    context: DecisionContext,
    rule: Rule,
    supplier_input: SupplierEvidenceInput,
    coverage: SupplierAlternativeSetCoverage,
    opportunity_determinations: tuple[
        SupplierAlternativeOpportunityDetermination, ...
    ],
    prov_evidences: tuple[Evidence, ...],
) -> Assessment:
    """Evaluate R-PROV-001 from reconstructed Supplier Evidence and explicit authority."""

    _validate_rule_identity(
        purchase=purchase,
        context=context,
        rule=rule,
        expected_rule_id=R_PROV_001,
    )
    supplier_result = _rebuild_supplier_evidence(
        purchase=purchase,
        context=context,
        supplier_input=supplier_input,
    )
    purchase_ref = supplier_alternative_purchase_operation_ref(purchase)
    supplier_ref = supplier_evidence_result_ref(supplier_result)
    evidence_by_id = _evidence_map(prov_evidences)

    _validate_coverage(
        coverage,
        purchase=purchase,
        context=context,
        expected_purchase_ref=purchase_ref,
        expected_supplier_ref=supplier_ref,
        evidence_by_id=evidence_by_id,
    )
    opportunity_by_candidate = _index_and_validate_determinations(
        opportunity_determinations,
        purchase=purchase,
        context=context,
        supplier_result=supplier_result,
        expected_purchase_ref=purchase_ref,
        expected_supplier_ref=supplier_ref,
        evidence_by_id=evidence_by_id,
        source_type=PROV_OPPORTUNITY_EVIDENCE_SOURCE_TYPE,
        ref_builder=supplier_alternative_opportunity_ref,
        indeterminate_state="NOT_DETERMINABLE",
    )
    carriers = (coverage, *opportunity_determinations)
    _reject_unreferenced_evidence(evidence_by_id, carriers)
    evidence_ids = _assessment_evidence_ids(supplier_result, carriers)

    for resolution in supplier_result.candidate_resolutions:
        determination = opportunity_by_candidate.get(resolution.candidate_id)
        if (
            resolution.state == "EVIDENCED_CANDIDATE"
            and determination is not None
            and determination.state == "POTENTIALLY_BETTER"
        ):
            return Assessment(
                rule_id=R_PROV_001,
                status="EVALUABLE",
                outcome="TRUE",
                evidence_ids=evidence_ids,
                reason=(
                    "R-PROV-001 demostrada: existe una candidatura evidenciada "
                    "con oportunidad POTENTIALLY_BETTER autorizada."
                ),
            )

    if coverage.state != "COMPLETE":
        return Assessment(
            rule_id=R_PROV_001,
            status="NOT_EVALUABLE",
            outcome=None,
            evidence_ids=evidence_ids,
            reason="R-PROV-001 no evaluable: cobertura de alternativas no completa.",
        )

    if any(
        resolution.state != "EVIDENCED_CANDIDATE"
        for resolution in supplier_result.candidate_resolutions
    ):
        return Assessment(
            rule_id=R_PROV_001,
            status="NOT_EVALUABLE",
            outcome=None,
            evidence_ids=evidence_ids,
            reason="R-PROV-001 no evaluable: existe candidatura no resuelta como EVIDENCED_CANDIDATE.",
        )

    expected_candidates = {
        resolution.candidate_id for resolution in supplier_result.candidate_resolutions
    }
    if set(opportunity_by_candidate) != expected_candidates:
        return Assessment(
            rule_id=R_PROV_001,
            status="NOT_EVALUABLE",
            outcome=None,
            evidence_ids=evidence_ids,
            reason="R-PROV-001 no evaluable: faltan determinaciones de oportunidad.",
        )

    if any(
        determination.state == "NOT_DETERMINABLE"
        for determination in opportunity_by_candidate.values()
    ):
        return Assessment(
            rule_id=R_PROV_001,
            status="NOT_EVALUABLE",
            outcome=None,
            evidence_ids=evidence_ids,
            reason="R-PROV-001 no evaluable: oportunidad no determinable.",
        )

    return Assessment(
        rule_id=R_PROV_001,
        status="EVALUABLE",
        outcome="FALSE",
        evidence_ids=evidence_ids,
        reason=(
            "R-PROV-001 no demostrada: cobertura COMPLETE y todas las "
            "candidaturas aplicables son NOT_POTENTIALLY_BETTER."
        ),
    )


def evaluate_r_prov_002(
    *,
    purchase: PurchaseOperation,
    context: DecisionContext,
    rule: Rule,
    supplier_input: SupplierEvidenceInput,
    coverage: SupplierAlternativeSetCoverage,
    comparability_determinations: tuple[
        SupplierAlternativeComparabilityDetermination, ...
    ],
    significant_improvement_determinations: tuple[
        SupplierAlternativeSignificantImprovementDetermination, ...
    ],
    prov_evidences: tuple[Evidence, ...],
) -> Assessment:
    """Evaluate R-PROV-002 without deriving comparability or significance."""

    _validate_rule_identity(
        purchase=purchase,
        context=context,
        rule=rule,
        expected_rule_id=R_PROV_002,
    )
    supplier_result = _rebuild_supplier_evidence(
        purchase=purchase,
        context=context,
        supplier_input=supplier_input,
    )
    purchase_ref = supplier_alternative_purchase_operation_ref(purchase)
    supplier_ref = supplier_evidence_result_ref(supplier_result)
    evidence_by_id = _evidence_map(prov_evidences)

    _validate_coverage(
        coverage,
        purchase=purchase,
        context=context,
        expected_purchase_ref=purchase_ref,
        expected_supplier_ref=supplier_ref,
        evidence_by_id=evidence_by_id,
    )
    comparability_by_candidate = _index_and_validate_determinations(
        comparability_determinations,
        purchase=purchase,
        context=context,
        supplier_result=supplier_result,
        expected_purchase_ref=purchase_ref,
        expected_supplier_ref=supplier_ref,
        evidence_by_id=evidence_by_id,
        source_type=PROV_COMPARABILITY_EVIDENCE_SOURCE_TYPE,
        ref_builder=supplier_alternative_comparability_ref,
        indeterminate_state="NOT_DETERMINABLE",
    )
    significant_by_candidate = _index_and_validate_determinations(
        significant_improvement_determinations,
        purchase=purchase,
        context=context,
        supplier_result=supplier_result,
        expected_purchase_ref=purchase_ref,
        expected_supplier_ref=supplier_ref,
        evidence_by_id=evidence_by_id,
        source_type=PROV_SIGNIFICANT_IMPROVEMENT_EVIDENCE_SOURCE_TYPE,
        ref_builder=supplier_alternative_significant_improvement_ref,
        indeterminate_state="NOT_DETERMINABLE",
    )
    carriers = (
        coverage,
        *comparability_determinations,
        *significant_improvement_determinations,
    )
    _reject_unreferenced_evidence(evidence_by_id, carriers)
    evidence_ids = _assessment_evidence_ids(supplier_result, carriers)

    for resolution in supplier_result.candidate_resolutions:
        comparability = comparability_by_candidate.get(resolution.candidate_id)
        significant = significant_by_candidate.get(resolution.candidate_id)
        if (
            resolution.state == "EVIDENCED_CANDIDATE"
            and comparability is not None
            and significant is not None
            and comparability.state == "COMPARABLE"
            and significant.state == "SIGNIFICANT_IMPROVEMENT"
        ):
            return Assessment(
                rule_id=R_PROV_002,
                status="EVALUABLE",
                outcome="TRUE",
                evidence_ids=evidence_ids,
                reason=(
                    "R-PROV-002 demostrada: existe una candidatura evidenciada "
                    "COMPARABLE con SIGNIFICANT_IMPROVEMENT autorizada."
                ),
            )

    if coverage.state != "COMPLETE":
        return Assessment(
            rule_id=R_PROV_002,
            status="NOT_EVALUABLE",
            outcome=None,
            evidence_ids=evidence_ids,
            reason="R-PROV-002 no evaluable: cobertura de alternativas no completa.",
        )

    if any(
        resolution.state != "EVIDENCED_CANDIDATE"
        for resolution in supplier_result.candidate_resolutions
    ):
        return Assessment(
            rule_id=R_PROV_002,
            status="NOT_EVALUABLE",
            outcome=None,
            evidence_ids=evidence_ids,
            reason="R-PROV-002 no evaluable: existe candidatura no resuelta como EVIDENCED_CANDIDATE.",
        )

    expected_candidates = {
        resolution.candidate_id for resolution in supplier_result.candidate_resolutions
    }
    if (
        set(comparability_by_candidate) != expected_candidates
        or set(significant_by_candidate) != expected_candidates
    ):
        return Assessment(
            rule_id=R_PROV_002,
            status="NOT_EVALUABLE",
            outcome=None,
            evidence_ids=evidence_ids,
            reason="R-PROV-002 no evaluable: faltan determinaciones por candidatura.",
        )

    if any(
        determination.state == "NOT_DETERMINABLE"
        for determination in comparability_by_candidate.values()
    ) or any(
        determination.state == "NOT_DETERMINABLE"
        for determination in significant_by_candidate.values()
    ):
        return Assessment(
            rule_id=R_PROV_002,
            status="NOT_EVALUABLE",
            outcome=None,
            evidence_ids=evidence_ids,
            reason="R-PROV-002 no evaluable: comparabilidad o mejora no determinable.",
        )

    return Assessment(
        rule_id=R_PROV_002,
        status="EVALUABLE",
        outcome="FALSE",
        evidence_ids=evidence_ids,
        reason=(
            "R-PROV-002 no demostrada: cobertura COMPLETE y ninguna candidatura "
            "satisface simultáneamente COMPARABLE + SIGNIFICANT_IMPROVEMENT."
        ),
    )


__all__ = [
    "R_PROV_001",
    "R_PROV_002",
    "evaluate_r_prov_001",
    "evaluate_r_prov_002",
]
