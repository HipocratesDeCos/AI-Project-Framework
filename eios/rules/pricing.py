"""Rules-layer bridges for closed Price Intelligence C1 outputs."""
from __future__ import annotations

import hashlib
import json
from decimal import Decimal, InvalidOperation

from eios.core.models import Assessment, DecisionContext, Evidence, PurchaseOperation, Rule
from eios.core.validation import validate_evidence
from eios.parameters import ResolvedConfiguration
from eios.pricing import (
    RECOMMENDED_PRICE_CEILING_EVIDENCE_SOURCE_TYPE,
    PriceIntelligenceAssessmentContext,
    PriceIntelligenceInput,
    PriceIntelligenceResult,
    RecommendedPriceCeiling,
    recommended_price_ceiling_ref,
    recommended_price_purchase_ref,
    run_price_intelligence,
)


R_HIS_002 = "R-HIS-002"
R_PRE_003 = "R-PRE-003"
P_PRE_006 = "P-PRE-006"
PRICE_INTELLIGENCE_EVIDENCE_SOURCE_TYPE = "PriceIntelligenceResultEvidence"
PARAMETER_CONFIGURATION_EVIDENCE_SOURCE_TYPE = "ParameterConfigurationEvidence"


def price_intelligence_result_ref(result: PriceIntelligenceResult) -> str:
    """Deterministic technical reference for one exact C1 pricing result."""
    payload = json.dumps(
        result.model_dump(mode="json"),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return f"price_intelligence:{hashlib.sha256(payload).hexdigest()}"


def _validate_identity(
    purchase: PurchaseOperation,
    context: DecisionContext,
    rule: Rule,
    pricing_input: PriceIntelligenceInput,
) -> None:
    if purchase.decision_id != context.decision_id:
        raise ValueError("PurchaseOperation y DecisionContext tienen decision_id distintos")
    if purchase.scenario_id != context.scenario_id:
        raise ValueError("PurchaseOperation y DecisionContext tienen scenario_id distintos")
    if rule.rule_id != R_HIS_002:
        raise ValueError("El bridge solo evalúa R-HIS-002")
    if rule.version != context.rules_version:
        raise ValueError("Rule.version incompatible con DecisionContext.rules_version")
    if not rule.requires_evidence:
        raise ValueError("R-HIS-002 requiere evidencia")
    if pricing_input.decision_context != context:
        raise ValueError("PriceIntelligenceInput pertenece a otro DecisionContext")
    if pricing_input.purchase_operation != purchase:
        raise ValueError("PriceIntelligenceInput pertenece a otra PurchaseOperation")


def _validate_pricing_evidence(
    purchase: PurchaseOperation,
    result: PriceIntelligenceResult,
    evidence: Evidence,
) -> None:
    if evidence.source_type != PRICE_INTELLIGENCE_EVIDENCE_SOURCE_TYPE:
        raise ValueError("pricing_evidence.source_type incompatible")
    if evidence.captured_at != purchase.operation_date:
        raise ValueError("pricing_evidence debe corresponder a la fecha de la operación evaluada")
    if (
        evidence.state == "DEMONSTRATED"
        and evidence.demonstration_ref != price_intelligence_result_ref(result)
    ):
        raise ValueError("pricing_evidence no está vinculada al PriceIntelligenceResult evaluado")


def _minimum_comparable_operations(
    *,
    purchase: PurchaseOperation,
    context: DecisionContext,
    company_id: str,
    resolved: ResolvedConfiguration,
    evidence: Evidence,
) -> int | None:
    if not company_id or not company_id.strip():
        raise ValueError("company_id no puede estar vacío")
    if resolved.parameter_id != P_PRE_006:
        raise ValueError("R-HIS-002 requiere P-PRE-006")
    if resolved.parameters_version != context.parameters_version:
        raise ValueError("P-PRE-006 está vinculada a otra parameters_version")
    if resolved.company_id != company_id:
        raise ValueError("P-PRE-006 pertenece a otro company_id")
    if resolved.effective_at.date() != purchase.operation_date:
        raise ValueError("P-PRE-006 debe resolverse para la fecha de la operación evaluada")
    if resolved.unit != "operaciones":
        return None
    if evidence.source_type != PARAMETER_CONFIGURATION_EVIDENCE_SOURCE_TYPE:
        raise ValueError("parameter_evidence.source_type incompatible")
    if evidence.captured_at != purchase.operation_date:
        raise ValueError("parameter_evidence debe corresponder a la fecha de la operación evaluada")
    if (
        evidence.state == "DEMONSTRATED"
        and evidence.demonstration_ref != resolved.configuration_ref
    ):
        raise ValueError("parameter_evidence no está vinculada a P-PRE-006")

    try:
        value = Decimal(resolved.value)
    except (InvalidOperation, ValueError):
        return None
    if not value.is_finite() or value <= 0 or value != value.to_integral_value():
        return None
    return int(value)


def _validate_pre003_identity(
    purchase: PurchaseOperation,
    context: DecisionContext,
    rule: Rule,
    ceiling: RecommendedPriceCeiling,
) -> None:
    if purchase.decision_id != context.decision_id:
        raise ValueError("PurchaseOperation y DecisionContext tienen decision_id distintos")
    if purchase.scenario_id != context.scenario_id:
        raise ValueError("PurchaseOperation y DecisionContext tienen scenario_id distintos")
    if rule.rule_id != R_PRE_003:
        raise ValueError("El bridge solo evalúa R-PRE-003")
    if rule.version != context.rules_version:
        raise ValueError("Rule.version incompatible con DecisionContext.rules_version")
    if not rule.requires_evidence:
        raise ValueError("R-PRE-003 requiere evidencia")
    if ceiling.decision_id != context.decision_id:
        raise ValueError("RecommendedPriceCeiling pertenece a otra decisión")
    if ceiling.scenario_id != context.scenario_id:
        raise ValueError("RecommendedPriceCeiling pertenece a otro escenario")
    if ceiling.data_snapshot_id != context.data_snapshot_id:
        raise ValueError("RecommendedPriceCeiling usa otro data_snapshot_id")
    if ceiling.article_id != purchase.article_id:
        raise ValueError("RecommendedPriceCeiling pertenece a otro artículo")
    if ceiling.evaluation_date != purchase.operation_date:
        raise ValueError("RecommendedPriceCeiling usa otra evaluation_date")
    if ceiling.currency != purchase.currency:
        raise ValueError("RecommendedPriceCeiling usa otra moneda")
    if ceiling.purchase_operation_ref != recommended_price_purchase_ref(purchase):
        raise ValueError("RecommendedPriceCeiling no está vinculada a la PurchaseOperation exacta")


def _validate_pre003_evidence(
    ceiling: RecommendedPriceCeiling,
    evidence: Evidence,
) -> None:
    if evidence.source_type != RECOMMENDED_PRICE_CEILING_EVIDENCE_SOURCE_TYPE:
        raise ValueError("ceiling_evidence.source_type incompatible")
    if evidence.captured_at != ceiling.evaluation_date:
        raise ValueError("ceiling_evidence debe corresponder a evaluation_date")
    if (
        evidence.state == "DEMONSTRATED"
        and evidence.demonstration_ref != recommended_price_ceiling_ref(ceiling)
    ):
        raise ValueError("ceiling_evidence no está vinculada al RecommendedPriceCeiling evaluado")


def evaluate_r_pre_003(
    purchase: PurchaseOperation,
    context: DecisionContext,
    rule: Rule,
    ceiling: RecommendedPriceCeiling,
    ceiling_evidence: Evidence,
) -> Assessment:
    """Evaluate proposed price at or below an independently authorized PMR."""
    _validate_pre003_identity(purchase, context, rule, ceiling)
    _validate_pre003_evidence(ceiling, ceiling_evidence)

    evidence_ids = [ceiling_evidence.evidence_id]
    if validate_evidence(ceiling_evidence).status != "VALID":
        return Assessment(
            rule_id=R_PRE_003,
            status="NOT_EVALUABLE",
            outcome=None,
            evidence_ids=evidence_ids,
            reason="R-PRE-003 no evaluable: PMR no demostrada.",
        )

    if ceiling.state != "AVAILABLE":
        return Assessment(
            rule_id=R_PRE_003,
            status="NOT_EVALUABLE",
            outcome=None,
            evidence_ids=evidence_ids,
            reason=f"R-PRE-003 no evaluable: PMR {ceiling.state}.",
        )

    assert ceiling.ceiling_price is not None
    triggered = purchase.unit_price <= ceiling.ceiling_price
    return Assessment(
        rule_id=R_PRE_003,
        status="EVALUABLE",
        outcome="TRUE" if triggered else "FALSE",
        evidence_ids=evidence_ids,
        reason=(
            "R-PRE-003 demostrada: precio propuesto igual o inferior al PMR."
            if triggered
            else "R-PRE-003 no demostrada: precio propuesto superior al PMR."
        ),
    )


def evaluate_r_his_002(
    purchase: PurchaseOperation,
    context: DecisionContext,
    rule: Rule,
    pricing_input: PriceIntelligenceInput,
    pricing_assessment_context: PriceIntelligenceAssessmentContext,
    pricing_evidence: Evidence,
    company_id: str,
    minimum_resolution: ResolvedConfiguration | None,
    parameter_evidence: Evidence | None,
) -> Assessment:
    """Evaluate whether comparable historical operations are below P-PRE-006."""
    _validate_identity(purchase, context, rule, pricing_input)
    pricing_result = run_price_intelligence(
        pricing_input.model_copy(deep=True),
        pricing_assessment_context.model_copy(deep=True),
    )
    _validate_pricing_evidence(purchase, pricing_result, pricing_evidence)
    evidence_ids = [pricing_evidence.evidence_id]

    if validate_evidence(pricing_evidence).status != "VALID":
        return Assessment(
            rule_id=R_HIS_002,
            status="NOT_EVALUABLE",
            outcome=None,
            evidence_ids=evidence_ids,
            reason="R-HIS-002 no evaluable: Price Intelligence no está demostrado.",
        )

    if minimum_resolution is None or parameter_evidence is None:
        return Assessment(
            rule_id=R_HIS_002,
            status="NOT_EVALUABLE",
            outcome=None,
            evidence_ids=evidence_ids,
            reason="R-HIS-002 no evaluable: P-PRE-006 no está resuelta/evidenciada.",
        )

    evidence_ids.append(parameter_evidence.evidence_id)
    threshold = _minimum_comparable_operations(
        purchase=purchase,
        context=context,
        company_id=company_id,
        resolved=minimum_resolution,
        evidence=parameter_evidence,
    )
    if validate_evidence(parameter_evidence).status != "VALID" or threshold is None:
        return Assessment(
            rule_id=R_HIS_002,
            status="NOT_EVALUABLE",
            outcome=None,
            evidence_ids=evidence_ids,
            reason="R-HIS-002 no evaluable: P-PRE-006 no es utilizable con evidencia suficiente.",
        )

    comparable = pricing_result.counts.n_comparable
    triggered = comparable < threshold
    return Assessment(
        rule_id=R_HIS_002,
        status="EVALUABLE",
        outcome="TRUE" if triggered else "FALSE",
        evidence_ids=evidence_ids,
        reason=(
            "R-HIS-002 demostrada: histórico comparable inferior al mínimo P-PRE-006."
            if triggered
            else "R-HIS-002 no demostrada: histórico comparable alcanza P-PRE-006."
        ),
    )


__all__ = [
    "P_PRE_006",
    "PARAMETER_CONFIGURATION_EVIDENCE_SOURCE_TYPE",
    "PRICE_INTELLIGENCE_EVIDENCE_SOURCE_TYPE",
    "R_HIS_002",
    "R_PRE_003",
    "evaluate_r_his_002",
    "evaluate_r_pre_003",
    "price_intelligence_result_ref",
]
