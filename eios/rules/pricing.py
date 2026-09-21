"""Rules-layer bridges for closed Price Intelligence C1 outputs."""
from __future__ import annotations

import calendar
import hashlib
import json
from datetime import date
from decimal import Decimal, InvalidOperation

from eios.core.models import Assessment, DecisionContext, Evidence, PurchaseOperation, Rule
from eios.core.validation import validate_evidence
from eios.parameters import ResolvedConfiguration
from eios.pricing import (
    COMPARABLE_PRICE_REFERENCE_EVIDENCE_SOURCE_TYPE,
    CRITICAL_PRICE_BASELINE_EVIDENCE_SOURCE_TYPE,
    HISTORICAL_REFERENCE_TEMPORAL_EVIDENCE_SOURCE_TYPE,
    RECOMMENDED_PRICE_CEILING_EVIDENCE_SOURCE_TYPE,
    ComparablePriceReference,
    CriticalPriceBaseline,
    HistoricalReferenceTemporalObservation,
    PriceIntelligenceAssessmentContext,
    PriceIntelligenceInput,
    PriceIntelligenceResult,
    RecommendedPriceCeiling,
    comparable_price_purchase_ref,
    comparable_price_reference_ref,
    critical_price_baseline_ref,
    critical_price_purchase_ref,
    historical_reference_purchase_ref,
    historical_reference_temporal_ref,
    recommended_price_ceiling_ref,
    recommended_price_purchase_ref,
    run_price_intelligence,
)


R_HIS_001 = "R-HIS-001"
R_HIS_002 = "R-HIS-002"
R_PRE_001 = "R-PRE-001"
R_PRE_002 = "R-PRE-002"
R_PRE_003 = "R-PRE-003"
P_DAT_002 = "P-DAT-002"
P_PRE_001 = "P-PRE-001"
P_PRE_004 = "P-PRE-004"
P_PRE_005 = "P-PRE-005"
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


def _validate_pre001_identity(
    purchase: PurchaseOperation,
    context: DecisionContext,
    rule: Rule,
    reference: ComparablePriceReference,
) -> None:
    if purchase.decision_id != context.decision_id:
        raise ValueError("PurchaseOperation y DecisionContext tienen decision_id distintos")
    if purchase.scenario_id != context.scenario_id:
        raise ValueError("PurchaseOperation y DecisionContext tienen scenario_id distintos")
    if rule.rule_id != R_PRE_001:
        raise ValueError("El bridge solo evalúa R-PRE-001")
    if rule.version != context.rules_version:
        raise ValueError("Rule.version incompatible con DecisionContext.rules_version")
    if not rule.requires_evidence:
        raise ValueError("R-PRE-001 requiere evidencia")
    if reference.decision_id != context.decision_id:
        raise ValueError("ComparablePriceReference pertenece a otra decisión")
    if reference.scenario_id != context.scenario_id:
        raise ValueError("ComparablePriceReference pertenece a otro escenario")
    if reference.data_snapshot_id != context.data_snapshot_id:
        raise ValueError("ComparablePriceReference usa otro data_snapshot_id")
    if reference.article_id != purchase.article_id:
        raise ValueError("ComparablePriceReference pertenece a otro artículo")
    if reference.evaluation_date != purchase.operation_date:
        raise ValueError("ComparablePriceReference usa otra evaluation_date")
    if reference.currency != purchase.currency:
        raise ValueError("ComparablePriceReference usa otra moneda")
    if reference.purchase_operation_ref != comparable_price_purchase_ref(purchase):
        raise ValueError("ComparablePriceReference no está vinculada a la PurchaseOperation exacta")
    if reference.reference_date > reference.evaluation_date:
        raise ValueError("reference_date no puede ser futura respecto a evaluation_date")


def _validate_pre001_reference_evidence(
    reference: ComparablePriceReference,
    evidence: Evidence,
) -> None:
    if evidence.source_type != COMPARABLE_PRICE_REFERENCE_EVIDENCE_SOURCE_TYPE:
        raise ValueError("reference_evidence.source_type incompatible")
    if evidence.captured_at != reference.evaluation_date:
        raise ValueError("reference_evidence debe corresponder a evaluation_date")
    if (
        evidence.state == "DEMONSTRATED"
        and evidence.demonstration_ref != comparable_price_reference_ref(reference)
    ):
        raise ValueError("reference_evidence no está vinculada a ComparablePriceReference")


def _validated_parameter_decimal(
    *,
    expected_id: str,
    expected_unit: str,
    purchase: PurchaseOperation,
    context: DecisionContext,
    company_id: str,
    resolved: ResolvedConfiguration,
    evidence: Evidence,
    positive_integer: bool = False,
) -> Decimal | None:
    if resolved.parameter_id != expected_id:
        raise ValueError(f"Se requiere {expected_id}")
    if resolved.parameters_version != context.parameters_version:
        raise ValueError(f"{expected_id} está vinculada a otra parameters_version")
    if resolved.company_id != company_id:
        raise ValueError(f"{expected_id} pertenece a otro company_scope")
    if resolved.effective_at.date() != purchase.operation_date:
        raise ValueError(f"{expected_id} debe resolverse para evaluation_date")

    configuration = resolved.configuration
    try:
        active = configuration.valid_from <= resolved.effective_at and (
            configuration.valid_to is None
            or resolved.effective_at < configuration.valid_to
        )
    except TypeError as exc:
        raise ValueError(f"{expected_id} usa semántica temporal incompatible") from exc
    if not active:
        raise ValueError(f"{expected_id} no está vigente en effective_at")

    if resolved.unit != expected_unit:
        return None
    if evidence.source_type != PARAMETER_CONFIGURATION_EVIDENCE_SOURCE_TYPE:
        raise ValueError("parameter_evidence.source_type incompatible")
    if evidence.captured_at != purchase.operation_date:
        raise ValueError("parameter_evidence debe corresponder a evaluation_date")
    if (
        evidence.state == "DEMONSTRATED"
        and evidence.demonstration_ref != resolved.configuration_ref
    ):
        raise ValueError(f"parameter_evidence no está vinculada a {expected_id}")

    try:
        value = Decimal(resolved.value)
    except (InvalidOperation, ValueError, TypeError):
        return None
    if not value.is_finite():
        return None
    if positive_integer:
        if value <= 0 or value != value.to_integral_value():
            return None
    elif value < 0:
        return None
    return value


def _subtract_calendar_months(value: date, months: int) -> date:
    total_months = value.year * 12 + (value.month - 1) - months
    target_year, month_index = divmod(total_months, 12)
    target_month = month_index + 1
    target_day = min(value.day, calendar.monthrange(target_year, target_month)[1])
    return date(target_year, target_month, target_day)


def evaluate_r_pre_001(
    purchase: PurchaseOperation,
    context: DecisionContext,
    rule: Rule,
    reference: ComparablePriceReference,
    reference_evidence: Evidence,
    recency_resolution: ResolvedConfiguration | None,
    recency_evidence: Evidence | None,
    alert_resolution: ResolvedConfiguration | None,
    alert_evidence: Evidence | None,
) -> Assessment:
    """Evaluate one explicit comparable recent price against P-PRE-004."""
    _validate_pre001_identity(purchase, context, rule, reference)
    _validate_pre001_reference_evidence(reference, reference_evidence)
    evidence_ids = [reference_evidence.evidence_id]

    if validate_evidence(reference_evidence).status != "VALID":
        return Assessment(
            rule_id=R_PRE_001,
            status="NOT_EVALUABLE",
            outcome=None,
            evidence_ids=evidence_ids,
            reason="R-PRE-001 no evaluable: referencia comparable no demostrada.",
        )
    if reference.comparability_state != "COMPARABLE":
        return Assessment(
            rule_id=R_PRE_001,
            status="NOT_EVALUABLE",
            outcome=None,
            evidence_ids=evidence_ids,
            reason=f"R-PRE-001 no evaluable: comparabilidad {reference.comparability_state}.",
        )
    if reference.reference_price is None:
        return Assessment(
            rule_id=R_PRE_001,
            status="NOT_EVALUABLE",
            outcome=None,
            evidence_ids=evidence_ids,
            reason="R-PRE-001 no evaluable: reference_price ausente.",
        )

    if recency_resolution is None or recency_evidence is None:
        return Assessment(
            rule_id=R_PRE_001,
            status="NOT_EVALUABLE",
            outcome=None,
            evidence_ids=evidence_ids,
            reason="R-PRE-001 no evaluable: P-PRE-001 no resuelta/evidenciada.",
        )
    evidence_ids.append(recency_evidence.evidence_id)
    months_value = _validated_parameter_decimal(
        expected_id=P_PRE_001,
        expected_unit="meses",
        purchase=purchase,
        context=context,
        company_id=reference.company_scope,
        resolved=recency_resolution,
        evidence=recency_evidence,
        positive_integer=True,
    )
    if validate_evidence(recency_evidence).status != "VALID" or months_value is None:
        return Assessment(
            rule_id=R_PRE_001,
            status="NOT_EVALUABLE",
            outcome=None,
            evidence_ids=evidence_ids,
            reason="R-PRE-001 no evaluable: P-PRE-001 no utilizable.",
        )

    cutoff = _subtract_calendar_months(reference.evaluation_date, int(months_value))
    if reference.reference_date < cutoff:
        return Assessment(
            rule_id=R_PRE_001,
            status="EVALUABLE",
            outcome="FALSE",
            evidence_ids=evidence_ids,
            reason="R-PRE-001 no demostrada: referencia comparable fuera del horizonte reciente.",
        )

    if alert_resolution is None or alert_evidence is None:
        return Assessment(
            rule_id=R_PRE_001,
            status="NOT_EVALUABLE",
            outcome=None,
            evidence_ids=evidence_ids,
            reason="R-PRE-001 no evaluable: P-PRE-004 no resuelta/evidenciada.",
        )
    evidence_ids.append(alert_evidence.evidence_id)
    threshold = _validated_parameter_decimal(
        expected_id=P_PRE_004,
        expected_unit="%",
        purchase=purchase,
        context=context,
        company_id=reference.company_scope,
        resolved=alert_resolution,
        evidence=alert_evidence,
    )
    if validate_evidence(alert_evidence).status != "VALID" or threshold is None:
        return Assessment(
            rule_id=R_PRE_001,
            status="NOT_EVALUABLE",
            outcome=None,
            evidence_ids=evidence_ids,
            reason="R-PRE-001 no evaluable: P-PRE-004 no utilizable.",
        )

    uplift_pct = (
        (purchase.unit_price - reference.reference_price)
        / reference.reference_price
        * Decimal("100")
    )
    triggered = uplift_pct >= threshold
    return Assessment(
        rule_id=R_PRE_001,
        status="EVALUABLE",
        outcome="TRUE" if triggered else "FALSE",
        evidence_ids=evidence_ids,
        reason=(
            "R-PRE-001 demostrada: uplift igual o superior a P-PRE-004 sobre referencia comparable reciente."
            if triggered
            else "R-PRE-001 no demostrada: uplift inferior a P-PRE-004."
        ),
    )


def _validate_pre002_identity(
    purchase: PurchaseOperation,
    context: DecisionContext,
    rule: Rule,
    baseline: CriticalPriceBaseline,
) -> None:
    if purchase.decision_id != context.decision_id:
        raise ValueError("PurchaseOperation y DecisionContext tienen decision_id distintos")
    if purchase.scenario_id != context.scenario_id:
        raise ValueError("PurchaseOperation y DecisionContext tienen scenario_id distintos")
    if rule.rule_id != R_PRE_002:
        raise ValueError("El bridge solo evalúa R-PRE-002")
    if rule.version != context.rules_version:
        raise ValueError("Rule.version incompatible con DecisionContext.rules_version")
    if not rule.requires_evidence:
        raise ValueError("R-PRE-002 requiere evidencia")
    if baseline.decision_id != context.decision_id:
        raise ValueError("CriticalPriceBaseline pertenece a otra decisión")
    if baseline.scenario_id != context.scenario_id:
        raise ValueError("CriticalPriceBaseline pertenece a otro escenario")
    if baseline.data_snapshot_id != context.data_snapshot_id:
        raise ValueError("CriticalPriceBaseline usa otro data_snapshot_id")
    if baseline.article_id != purchase.article_id:
        raise ValueError("CriticalPriceBaseline pertenece a otro artículo")
    if baseline.evaluation_date != purchase.operation_date:
        raise ValueError("CriticalPriceBaseline usa otra evaluation_date")
    if baseline.currency != purchase.currency:
        raise ValueError("CriticalPriceBaseline usa otra moneda")
    if baseline.purchase_operation_ref != critical_price_purchase_ref(purchase):
        raise ValueError("CriticalPriceBaseline no está vinculada a la PurchaseOperation exacta")


def _validate_pre002_evidence(
    baseline: CriticalPriceBaseline,
    evidence: Evidence,
) -> None:
    if evidence.source_type != CRITICAL_PRICE_BASELINE_EVIDENCE_SOURCE_TYPE:
        raise ValueError("baseline_evidence.source_type incompatible")
    if evidence.captured_at != baseline.evaluation_date:
        raise ValueError("baseline_evidence debe corresponder a evaluation_date")
    if (
        evidence.state == "DEMONSTRATED"
        and evidence.demonstration_ref != critical_price_baseline_ref(baseline)
    ):
        raise ValueError("baseline_evidence no está vinculada al CriticalPriceBaseline evaluado")


def evaluate_r_pre_002(
    purchase: PurchaseOperation,
    context: DecisionContext,
    rule: Rule,
    baseline: CriticalPriceBaseline,
    baseline_evidence: Evidence,
    critical_resolution: ResolvedConfiguration | None,
    critical_evidence: Evidence | None,
) -> Assessment:
    """Evaluate purchase price strictly above an authorized critical price limit."""
    _validate_pre002_identity(purchase, context, rule, baseline)
    _validate_pre002_evidence(baseline, baseline_evidence)
    evidence_ids = [baseline_evidence.evidence_id]

    if validate_evidence(baseline_evidence).status != "VALID":
        return Assessment(
            rule_id=R_PRE_002,
            status="NOT_EVALUABLE",
            outcome=None,
            evidence_ids=evidence_ids,
            reason="R-PRE-002 no evaluable: baseline crítico no demostrado.",
        )
    if baseline.state != "AVAILABLE":
        return Assessment(
            rule_id=R_PRE_002,
            status="NOT_EVALUABLE",
            outcome=None,
            evidence_ids=evidence_ids,
            reason=f"R-PRE-002 no evaluable: baseline crítico {baseline.state}.",
        )
    if baseline.baseline_price is None:
        return Assessment(
            rule_id=R_PRE_002,
            status="NOT_EVALUABLE",
            outcome=None,
            evidence_ids=evidence_ids,
            reason="R-PRE-002 no evaluable: baseline_price ausente.",
        )
    if critical_resolution is None or critical_evidence is None:
        return Assessment(
            rule_id=R_PRE_002,
            status="NOT_EVALUABLE",
            outcome=None,
            evidence_ids=evidence_ids,
            reason="R-PRE-002 no evaluable: P-PRE-005 no resuelta/evidenciada.",
        )

    evidence_ids.append(critical_evidence.evidence_id)
    threshold = _validated_parameter_decimal(
        expected_id=P_PRE_005,
        expected_unit="%",
        purchase=purchase,
        context=context,
        company_id=baseline.company_scope,
        resolved=critical_resolution,
        evidence=critical_evidence,
    )
    if validate_evidence(critical_evidence).status != "VALID" or threshold is None:
        return Assessment(
            rule_id=R_PRE_002,
            status="NOT_EVALUABLE",
            outcome=None,
            evidence_ids=evidence_ids,
            reason="R-PRE-002 no evaluable: P-PRE-005 no utilizable.",
        )

    critical_limit = baseline.baseline_price * (Decimal("1") + threshold / Decimal("100"))
    triggered = purchase.unit_price > critical_limit
    return Assessment(
        rule_id=R_PRE_002,
        status="EVALUABLE",
        outcome="TRUE" if triggered else "FALSE",
        evidence_ids=evidence_ids,
        reason=(
            "R-PRE-002 demostrada: precio propuesto superior al límite crítico."
            if triggered
            else "R-PRE-002 no demostrada: precio propuesto no supera el límite crítico."
        ),
    )


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



def _validate_his001_identity(
    purchase: PurchaseOperation,
    context: DecisionContext,
    rule: Rule,
    observation: HistoricalReferenceTemporalObservation,
) -> None:
    if purchase.decision_id != context.decision_id:
        raise ValueError("PurchaseOperation y DecisionContext tienen decision_id distintos")
    if purchase.scenario_id != context.scenario_id:
        raise ValueError("PurchaseOperation y DecisionContext tienen scenario_id distintos")
    if rule.rule_id != R_HIS_001:
        raise ValueError("El bridge solo evalúa R-HIS-001")
    if rule.version != context.rules_version:
        raise ValueError("Rule.version incompatible con DecisionContext.rules_version")
    if not rule.requires_evidence:
        raise ValueError("R-HIS-001 requiere evidencia")
    if observation.decision_id != context.decision_id:
        raise ValueError("HistoricalReferenceTemporalObservation pertenece a otra decisión")
    if observation.scenario_id != context.scenario_id:
        raise ValueError("HistoricalReferenceTemporalObservation pertenece a otro escenario")
    if observation.data_snapshot_id != context.data_snapshot_id:
        raise ValueError("HistoricalReferenceTemporalObservation usa otro data_snapshot_id")
    if observation.evaluation_date != purchase.operation_date:
        raise ValueError("HistoricalReferenceTemporalObservation usa otra evaluation_date")
    if observation.purchase_operation_ref != historical_reference_purchase_ref(purchase):
        raise ValueError("HistoricalReferenceTemporalObservation no está vinculada a la PurchaseOperation exacta")


def _validate_his001_evidence(
    observation: HistoricalReferenceTemporalObservation,
    evidence: Evidence,
) -> None:
    if evidence.source_type != HISTORICAL_REFERENCE_TEMPORAL_EVIDENCE_SOURCE_TYPE:
        raise ValueError("reference_evidence.source_type incompatible")
    if evidence.captured_at != observation.evaluation_date:
        raise ValueError("reference_evidence debe corresponder a evaluation_date")
    if (
        evidence.state == "DEMONSTRATED"
        and evidence.demonstration_ref != historical_reference_temporal_ref(observation)
    ):
        raise ValueError("reference_evidence no está vinculada al carrier temporal HIS001")


def evaluate_r_his_001(
    purchase: PurchaseOperation,
    context: DecisionContext,
    rule: Rule,
    observation: HistoricalReferenceTemporalObservation,
    reference_evidence: Evidence,
    maximum_age_resolution: ResolvedConfiguration | None,
    parameter_evidence: Evidence | None,
) -> Assessment:
    """Evaluate whether one historical reference exceeds P-DAT-002 maximum age."""
    _validate_his001_identity(purchase, context, rule, observation)
    _validate_his001_evidence(observation, reference_evidence)
    evidence_ids = [reference_evidence.evidence_id]

    if validate_evidence(reference_evidence).status != "VALID":
        return Assessment(
            rule_id=R_HIS_001,
            status="NOT_EVALUABLE",
            outcome=None,
            evidence_ids=evidence_ids,
            reason="R-HIS-001 no evaluable: referencia temporal no demostrada.",
        )
    if observation.state != "AVAILABLE":
        return Assessment(
            rule_id=R_HIS_001,
            status="NOT_EVALUABLE",
            outcome=None,
            evidence_ids=evidence_ids,
            reason=f"R-HIS-001 no evaluable: estado temporal {observation.state}.",
        )
    reference_date = observation.reference_operation_date
    if reference_date is None:
        return Assessment(
            rule_id=R_HIS_001,
            status="NOT_EVALUABLE",
            outcome=None,
            evidence_ids=evidence_ids,
            reason="R-HIS-001 no evaluable: reference_operation_date ausente.",
        )
    if reference_date > observation.evaluation_date:
        return Assessment(
            rule_id=R_HIS_001,
            status="NOT_EVALUABLE",
            outcome=None,
            evidence_ids=evidence_ids,
            reason="R-HIS-001 no evaluable: referencia futura respecto a evaluation_date.",
        )
    if maximum_age_resolution is None or parameter_evidence is None:
        return Assessment(
            rule_id=R_HIS_001,
            status="NOT_EVALUABLE",
            outcome=None,
            evidence_ids=evidence_ids,
            reason="R-HIS-001 no evaluable: P-DAT-002 no resuelta/evidenciada.",
        )

    evidence_ids.append(parameter_evidence.evidence_id)
    months_value = _validated_parameter_decimal(
        expected_id=P_DAT_002,
        expected_unit="meses",
        purchase=purchase,
        context=context,
        company_id=observation.company_scope,
        resolved=maximum_age_resolution,
        evidence=parameter_evidence,
        positive_integer=True,
    )
    if validate_evidence(parameter_evidence).status != "VALID" or months_value is None:
        return Assessment(
            rule_id=R_HIS_001,
            status="NOT_EVALUABLE",
            outcome=None,
            evidence_ids=evidence_ids,
            reason="R-HIS-001 no evaluable: P-DAT-002 no utilizable.",
        )

    cutoff = _subtract_calendar_months(observation.evaluation_date, int(months_value))
    triggered = reference_date < cutoff
    return Assessment(
        rule_id=R_HIS_001,
        status="EVALUABLE",
        outcome="TRUE" if triggered else "FALSE",
        evidence_ids=evidence_ids,
        reason=(
            "R-HIS-001 demostrada: la referencia supera la antigüedad máxima P-DAT-002."
            if triggered
            else "R-HIS-001 no demostrada: la referencia está dentro del límite P-DAT-002."
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
    "P_DAT_002",
    "P_PRE_001",
    "P_PRE_004",
    "P_PRE_005",
    "P_PRE_006",
    "PARAMETER_CONFIGURATION_EVIDENCE_SOURCE_TYPE",
    "PRICE_INTELLIGENCE_EVIDENCE_SOURCE_TYPE",
    "R_HIS_001",
    "R_HIS_002",
    "R_PRE_001",
    "R_PRE_002",
    "R_PRE_003",
    "evaluate_r_his_001",
    "evaluate_r_his_002",
    "evaluate_r_pre_001",
    "evaluate_r_pre_002",
    "evaluate_r_pre_003",
    "price_intelligence_result_ref",
]
