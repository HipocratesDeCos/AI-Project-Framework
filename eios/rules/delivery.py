"""Rules-layer bridge from ENT factual analysis to C0 Assessment for R-ENT-001."""
from __future__ import annotations

from collections.abc import Iterable

from eios.core.models import Assessment, DecisionContext, Evidence, PurchaseOperation, Rule
from eios.core.validation import validate_evidence
from eios.delivery.models import DeliveryStockoutAnalysisInput, DeliveryStockoutAnalysisResult


R_ENT_001 = "R-ENT-001"
BASELINE_EVIDENCE_SOURCE_TYPE = "BaselineStockoutQualification"
DELIVERY_EVIDENCE_SOURCE_TYPE = "PurchaseSpecificDeliveryTimingEvidence"


def _non_null_refs(*groups: Iterable[str | None]) -> set[str]:
    return {ref for group in groups for ref in group if ref}


def _validate_identity(
    purchase: PurchaseOperation,
    context: DecisionContext,
    rule: Rule,
    analysis_input: DeliveryStockoutAnalysisInput,
    analysis: DeliveryStockoutAnalysisResult,
) -> None:
    if purchase.decision_id != context.decision_id:
        raise ValueError("PurchaseOperation y DecisionContext tienen decision_id distintos")
    if purchase.scenario_id != context.scenario_id:
        raise ValueError("PurchaseOperation y DecisionContext tienen scenario_id distintos")
    if rule.rule_id != R_ENT_001:
        raise ValueError("El bridge solo evalúa R-ENT-001")
    if rule.version != context.rules_version:
        raise ValueError("Rule.version incompatible con DecisionContext.rules_version")
    if not rule.requires_evidence:
        raise ValueError("R-ENT-001 requiere evidencia según sus dependencias canónicas")

    if analysis_input.decision_id != purchase.decision_id:
        raise ValueError("ENT input pertenece a otra decisión")
    if analysis_input.article_id != purchase.article_id:
        raise ValueError("ENT input pertenece a otro artículo")
    if analysis_input.delivery.supplier_id != purchase.supplier_id:
        raise ValueError("ENT input pertenece a otro proveedor")

    if analysis.decision_id != purchase.decision_id:
        raise ValueError("ENT result pertenece a otra decisión")
    if analysis.article_id != purchase.article_id:
        raise ValueError("ENT result pertenece a otro artículo")
    if analysis.supplier_id != purchase.supplier_id:
        raise ValueError("ENT result pertenece a otro proveedor")

    if analysis.decision_id != analysis_input.decision_id:
        raise ValueError("ENT result/input decision_id incompatibles")
    if analysis.article_id != analysis_input.article_id:
        raise ValueError("ENT result/input article_id incompatibles")
    if analysis.evaluation_date != analysis_input.evaluation_date:
        raise ValueError("ENT result/input evaluation_date incompatibles")
    if analysis.evaluated_purchase_ref != analysis_input.evaluated_purchase_ref:
        raise ValueError("ENT result/input evaluated_purchase_ref incompatibles")
    if analysis.supplier_id != analysis_input.delivery.supplier_id:
        raise ValueError("ENT result/input supplier_id incompatibles")
    if analysis.baseline_projection_ref != analysis_input.baseline.baseline_projection_ref:
        raise ValueError("ENT result/input baseline_projection_ref incompatibles")

    projection_identity = analysis_input.baseline.projection.identity
    if projection_identity.decision_id != context.decision_id:
        raise ValueError("Proyección STK pertenece a otra decisión")
    if projection_identity.rules_version != context.rules_version:
        raise ValueError("Proyección STK usa otra rules_version")
    if projection_identity.parameters_version != context.parameters_version:
        raise ValueError("Proyección STK usa otra parameters_version")
    if projection_identity.data_snapshot_id != context.data_snapshot_id:
        raise ValueError("Proyección STK usa otro data_snapshot_id")

    if analysis.expected_delivery_date != analysis_input.delivery.expected_delivery_date:
        raise ValueError("ENT result/input expected_delivery_date incompatibles")
    if analysis.depletion_date != analysis_input.baseline.projection.depletion_date.value:
        raise ValueError("ENT result/input depletion_date incompatibles")
    if analysis.horizon_end != analysis_input.baseline.projection.horizon.horizon_end:
        raise ValueError("ENT result/input horizon_end incompatibles")


def _validate_evidence_binding(
    analysis_input: DeliveryStockoutAnalysisInput,
    baseline_evidence: Evidence,
    delivery_evidence: Evidence,
) -> None:
    if baseline_evidence.source_type != BASELINE_EVIDENCE_SOURCE_TYPE:
        raise ValueError("baseline_evidence.source_type incompatible")
    if delivery_evidence.source_type != DELIVERY_EVIDENCE_SOURCE_TYPE:
        raise ValueError("delivery_evidence.source_type incompatible")

    baseline = analysis_input.baseline
    baseline_refs = _non_null_refs(
        baseline.evidence_refs,
        baseline.trace_refs,
        baseline.issue_refs,
        baseline.unresolved_refs,
        (
            baseline.baseline_relation_ref,
            baseline.projection_provenance_ref,
            baseline.purchase_exclusion_ref,
        ),
    )
    if baseline_evidence.state == "DEMONSTRATED":
        if baseline_evidence.demonstration_ref not in baseline_refs:
            raise ValueError("baseline_evidence.demonstration_ref no pertenece a la provenance baseline")

    delivery = analysis_input.delivery
    delivery_refs = _non_null_refs(
        delivery.evidence_refs,
        delivery.trace_refs,
        delivery.issue_refs,
        (
            delivery.delivery_semantic_ref,
            delivery.purchase_applicability_ref,
            delivery.source_ref,
        ),
    )
    if delivery_evidence.state == "DEMONSTRATED":
        if delivery_evidence.demonstration_ref not in delivery_refs:
            raise ValueError("delivery_evidence.demonstration_ref no pertenece a la provenance delivery")


def evaluate_r_ent_001(
    purchase: PurchaseOperation,
    context: DecisionContext,
    rule: Rule,
    analysis_input: DeliveryStockoutAnalysisInput,
    analysis: DeliveryStockoutAnalysisResult,
    baseline_evidence: Evidence,
    delivery_evidence: Evidence,
) -> Assessment:
    """Map a closed ENT factual result into the individual Assessment of R-ENT-001."""
    _validate_identity(purchase, context, rule, analysis_input, analysis)
    _validate_evidence_binding(analysis_input, baseline_evidence, delivery_evidence)

    baseline_validation = validate_evidence(baseline_evidence)
    delivery_validation = validate_evidence(delivery_evidence)
    evidence_ids = [baseline_evidence.evidence_id, delivery_evidence.evidence_id]

    if analysis.state == "NOT_EVIDENCED":
        return Assessment(
            rule_id=R_ENT_001,
            status="NOT_EVALUABLE",
            outcome=None,
            evidence_ids=evidence_ids,
            reason="R-ENT-001 no evaluable: evidencia factual ENT insuficientemente demostrada.",
        )

    if analysis.state == "CONFLICTING_DATA":
        return Assessment(
            rule_id=R_ENT_001,
            status="NOT_EVALUABLE",
            outcome=None,
            evidence_ids=evidence_ids,
            reason="R-ENT-001 no evaluable: evidencia factual ENT contradictoria.",
        )

    if analysis.state == "NOT_DETERMINABLE":
        return Assessment(
            rule_id=R_ENT_001,
            status="NOT_EVALUABLE",
            outcome=None,
            evidence_ids=evidence_ids,
            reason="R-ENT-001 no evaluable: relación temporal ENT no determinable.",
        )

    both_valid = baseline_validation.status == "VALID" and delivery_validation.status == "VALID"
    if not both_valid:
        return Assessment(
            rule_id=R_ENT_001,
            status="NOT_EVALUABLE",
            outcome=None,
            evidence_ids=evidence_ids,
            reason="R-ENT-001 no evaluable: una o más dependencias C0 no están demostradas.",
        )

    if analysis.state == "LATE_DELIVERY_DEMONSTRATED":
        return Assessment(
            rule_id=R_ENT_001,
            status="EVALUABLE",
            outcome="TRUE",
            evidence_ids=evidence_ids,
            reason="R-ENT-001 demostrada: entrega posterior al agotamiento estimado.",
        )

    if analysis.state == "NOT_LATE_DEMONSTRATED":
        if "SAME_DAY_ORDER_NOT_DEMONSTRATED" in analysis.limitation_codes:
            reason = (
                "R-ENT-001 no demostrada: entrega y agotamiento en la misma fecha; "
                "orden intradía no demostrado."
            )
        else:
            reason = "R-ENT-001 no demostrada: entrega no posterior al agotamiento estimado."
        return Assessment(
            rule_id=R_ENT_001,
            status="EVALUABLE",
            outcome="FALSE",
            evidence_ids=evidence_ids,
            reason=reason,
        )

    if analysis.state == "NOT_LATE_WITHIN_EVIDENCED_HORIZON":
        return Assessment(
            rule_id=R_ENT_001,
            status="EVALUABLE",
            outcome="FALSE",
            evidence_ids=evidence_ids,
            reason="R-ENT-001 no demostrada dentro del horizonte STK evidenciado.",
        )

    raise ValueError(f"Estado ENT no soportado para R-ENT-001: {analysis.state}")


__all__ = [
    "BASELINE_EVIDENCE_SOURCE_TYPE",
    "DELIVERY_EVIDENCE_SOURCE_TYPE",
    "R_ENT_001",
    "evaluate_r_ent_001",
]
