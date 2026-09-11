"""Rules-layer bridges for Finance Basic results into authorized FIN rules."""
from __future__ import annotations

import hashlib
import json
from decimal import Decimal, InvalidOperation

from eios.core.models import Assessment, DecisionContext, Evidence, PurchaseOperation, Rule
from eios.core.validation import validate_evidence
from eios.finance import FinanceBasicInput, FinanceBasicResult
from eios.parameters import ResolvedConfiguration


R_FIN_001 = "R-FIN-001"
R_FIN_003 = "R-FIN-003"
P_FIN_002 = "P-FIN-002"
P_FIN_004 = "P-FIN-004"
FINANCE_BASIC_EVIDENCE_SOURCE_TYPE = "FinanceBasicResultEvidence"
PARAMETER_CONFIGURATION_EVIDENCE_SOURCE_TYPE = "ParameterConfigurationEvidence"


def finance_basic_result_ref(result: FinanceBasicResult) -> str:
    """Deterministic technical reference for binding C0 evidence to a FIN result."""
    payload = json.dumps(
        result.model_dump(mode="json"),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return f"finance_basic:{hashlib.sha256(payload).hexdigest()}"


def _validate_identity(
    purchase: PurchaseOperation,
    context: DecisionContext,
    rule: Rule,
    expected_rule_id: str,
    finance_input: FinanceBasicInput,
    finance_result: FinanceBasicResult,
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
    if finance_input.context != context:
        raise ValueError("FinanceBasicInput pertenece a otro DecisionContext")
    if finance_result.decision_id != context.decision_id:
        raise ValueError("FinanceBasicResult pertenece a otra decisión")
    if finance_result.scenario_id != context.scenario_id:
        raise ValueError("FinanceBasicResult pertenece a otro escenario")
    if finance_result.data_snapshot_id != context.data_snapshot_id:
        raise ValueError("FinanceBasicResult usa otro data_snapshot_id")
    if finance_result.parameters_version != context.parameters_version:
        raise ValueError("FinanceBasicResult usa otra parameters_version")
    if finance_result.currency != finance_input.snapshot.currency:
        raise ValueError("FinanceBasicResult y FinanceBasicInput usan monedas distintas")


def _validate_finance_evidence(
    finance_input: FinanceBasicInput,
    result: FinanceBasicResult,
    evidence: Evidence,
) -> None:
    if evidence.source_type != FINANCE_BASIC_EVIDENCE_SOURCE_TYPE:
        raise ValueError("finance_evidence.source_type incompatible")
    if evidence.captured_at != finance_input.snapshot.as_of_date:
        raise ValueError("finance_evidence debe corresponder a la fecha del snapshot financiero")
    if evidence.state == "DEMONSTRATED" and evidence.demonstration_ref != finance_basic_result_ref(result):
        raise ValueError("finance_evidence no está vinculada al FinanceBasicResult evaluado")


def _numeric_parameter(
    finance_input: FinanceBasicInput,
    context: DecisionContext,
    resolved: ResolvedConfiguration,
    evidence: Evidence,
    expected_parameter_id: str,
) -> Decimal | None:
    if resolved.parameter_id != expected_parameter_id:
        raise ValueError(f"La regla requiere {expected_parameter_id}")
    if resolved.parameters_version != context.parameters_version:
        raise ValueError(f"{expected_parameter_id} está vinculada a otra parameters_version")
    if resolved.company_id != finance_input.snapshot.company_scope:
        raise ValueError(f"{expected_parameter_id} pertenece a otro company_scope")
    if resolved.effective_at.date() != finance_input.snapshot.as_of_date:
        raise ValueError(f"{expected_parameter_id} debe resolverse para la fecha del snapshot financiero")
    if evidence.source_type != PARAMETER_CONFIGURATION_EVIDENCE_SOURCE_TYPE:
        raise ValueError("parameter_evidence.source_type incompatible")
    if evidence.captured_at != finance_input.snapshot.as_of_date:
        raise ValueError("parameter_evidence debe corresponder a la fecha del snapshot financiero")
    if evidence.state == "DEMONSTRATED" and evidence.demonstration_ref != resolved.configuration_ref:
        raise ValueError(f"parameter_evidence no está vinculada a {expected_parameter_id}")

    try:
        value = Decimal(resolved.value)
    except (InvalidOperation, ValueError):
        return None
    if not value.is_finite():
        return None
    return value


def _not_evaluable(rule_id: str, evidence_ids: list[str], reason: str) -> Assessment:
    return Assessment(
        rule_id=rule_id,
        status="NOT_EVALUABLE",
        outcome=None,
        evidence_ids=evidence_ids,
        reason=reason,
    )


def evaluate_r_fin_001(
    purchase: PurchaseOperation,
    context: DecisionContext,
    rule: Rule,
    finance_input: FinanceBasicInput,
    finance_result: FinanceBasicResult,
    finance_evidence: Evidence,
    threshold_resolution: ResolvedConfiguration | None,
    parameter_evidence: Evidence | None,
) -> Assessment:
    """Evaluate ``financial_capacity_forecast < P-FIN-002`` conservatively."""
    _validate_identity(purchase, context, rule, R_FIN_001, finance_input, finance_result)
    _validate_finance_evidence(finance_input, finance_result, finance_evidence)
    evidence_ids = [finance_evidence.evidence_id]

    if validate_evidence(finance_evidence).status != "VALID":
        return _not_evaluable(
            R_FIN_001, evidence_ids, "R-FIN-001 no evaluable: Finance Basic no está demostrado."
        )

    projection = finance_result.projection
    if projection.status != "DETERMINED" or projection.financial_capacity_forecast is None:
        return _not_evaluable(
            R_FIN_001,
            evidence_ids,
            f"R-FIN-001 no evaluable: proyección financiera {projection.status}.",
        )

    if threshold_resolution is None or parameter_evidence is None:
        return _not_evaluable(
            R_FIN_001,
            evidence_ids,
            "R-FIN-001 no evaluable: P-FIN-002 no está resuelta/evidenciada.",
        )

    evidence_ids.append(parameter_evidence.evidence_id)
    threshold = _numeric_parameter(
        finance_input, context, threshold_resolution, parameter_evidence, P_FIN_002
    )
    if threshold_resolution.unit not in {"EUR", "€"}:
        threshold = None
    if threshold is not None and threshold < 0:
        threshold = None
    supplied_minimum = finance_input.treasury_minimum
    if threshold is not None and supplied_minimum is not None and supplied_minimum != threshold:
        threshold = None

    if validate_evidence(parameter_evidence).status != "VALID" or threshold is None:
        return _not_evaluable(
            R_FIN_001,
            evidence_ids,
            "R-FIN-001 no evaluable: P-FIN-002 no es utilizable con evidencia suficiente.",
        )

    capacity = projection.financial_capacity_forecast
    assert capacity is not None
    triggered = capacity < threshold
    return Assessment(
        rule_id=R_FIN_001,
        status="EVALUABLE",
        outcome="TRUE" if triggered else "FALSE",
        evidence_ids=evidence_ids,
        reason=(
            "R-FIN-001 demostrada: capacidad financiera prevista inferior a P-FIN-002."
            if triggered
            else "R-FIN-001 no demostrada: capacidad financiera prevista cumple P-FIN-002."
        ),
    )


def evaluate_r_fin_003(
    purchase: PurchaseOperation,
    context: DecisionContext,
    rule: Rule,
    finance_input: FinanceBasicInput,
    finance_result: FinanceBasicResult,
    finance_evidence: Evidence,
    margin_resolution: ResolvedConfiguration | None,
    parameter_evidence: Evidence | None,
) -> Assessment:
    """Evaluate ``financial_safety_margin_pct < P-FIN-004`` conservatively."""
    _validate_identity(purchase, context, rule, R_FIN_003, finance_input, finance_result)
    _validate_finance_evidence(finance_input, finance_result, finance_evidence)
    evidence_ids = [finance_evidence.evidence_id]

    if validate_evidence(finance_evidence).status != "VALID":
        return _not_evaluable(
            R_FIN_003, evidence_ids, "R-FIN-003 no evaluable: Finance Basic no está demostrado."
        )

    margin = finance_result.safety_margin
    if margin.status != "DETERMINED" or margin.value_pct is None:
        return _not_evaluable(
            R_FIN_003,
            evidence_ids,
            f"R-FIN-003 no evaluable: margen financiero {margin.status}.",
        )

    if margin_resolution is None or parameter_evidence is None:
        return _not_evaluable(
            R_FIN_003,
            evidence_ids,
            "R-FIN-003 no evaluable: P-FIN-004 no está resuelta/evidenciada.",
        )

    evidence_ids.append(parameter_evidence.evidence_id)
    threshold = _numeric_parameter(
        finance_input, context, margin_resolution, parameter_evidence, P_FIN_004
    )
    if margin_resolution.unit != "%":
        threshold = None

    if validate_evidence(parameter_evidence).status != "VALID" or threshold is None:
        return _not_evaluable(
            R_FIN_003,
            evidence_ids,
            "R-FIN-003 no evaluable: P-FIN-004 no es utilizable con evidencia suficiente.",
        )

    safety_margin = margin.value_pct
    assert safety_margin is not None
    triggered = safety_margin < threshold
    return Assessment(
        rule_id=R_FIN_003,
        status="EVALUABLE",
        outcome="TRUE" if triggered else "FALSE",
        evidence_ids=evidence_ids,
        reason=(
            "R-FIN-003 demostrada: margen de seguridad financiera inferior a P-FIN-004."
            if triggered
            else "R-FIN-003 no demostrada: margen de seguridad financiera cumple P-FIN-004."
        ),
    )


__all__ = [
    "FINANCE_BASIC_EVIDENCE_SOURCE_TYPE",
    "PARAMETER_CONFIGURATION_EVIDENCE_SOURCE_TYPE",
    "P_FIN_002",
    "P_FIN_004",
    "R_FIN_001",
    "R_FIN_003",
    "evaluate_r_fin_001",
    "evaluate_r_fin_003",
    "finance_basic_result_ref",
]
