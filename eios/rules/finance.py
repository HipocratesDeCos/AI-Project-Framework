"""Rules-layer bridge for Finance Basic capacity into R-FIN-001."""
from __future__ import annotations

import hashlib
import json
from decimal import Decimal, InvalidOperation

from eios.core.models import Assessment, DecisionContext, Evidence, PurchaseOperation, Rule
from eios.core.validation import validate_evidence
from eios.finance import FinanceBasicInput, FinanceBasicResult
from eios.parameters import ResolvedConfiguration


R_FIN_001 = "R-FIN-001"
P_FIN_002 = "P-FIN-002"
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
    finance_input: FinanceBasicInput,
    finance_result: FinanceBasicResult,
) -> None:
    if purchase.decision_id != context.decision_id:
        raise ValueError("PurchaseOperation y DecisionContext tienen decision_id distintos")
    if purchase.scenario_id != context.scenario_id:
        raise ValueError("PurchaseOperation y DecisionContext tienen scenario_id distintos")
    if rule.rule_id != R_FIN_001:
        raise ValueError("El bridge solo evalúa R-FIN-001")
    if rule.version != context.rules_version:
        raise ValueError("Rule.version incompatible con DecisionContext.rules_version")
    if not rule.requires_evidence:
        raise ValueError("R-FIN-001 requiere evidencia")
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


def _validate_parameter_resolution(
    finance_input: FinanceBasicInput,
    context: DecisionContext,
    resolved: ResolvedConfiguration,
    evidence: Evidence,
) -> Decimal | None:
    if resolved.parameter_id != P_FIN_002:
        raise ValueError("R-FIN-001 requiere P-FIN-002")
    if resolved.parameters_version != context.parameters_version:
        raise ValueError("P-FIN-002 está vinculada a otra parameters_version")
    if resolved.company_id != finance_input.snapshot.company_scope:
        raise ValueError("P-FIN-002 pertenece a otro company_scope")
    if resolved.effective_at.date() != finance_input.snapshot.as_of_date:
        raise ValueError("P-FIN-002 debe resolverse para la fecha del snapshot financiero")
    if evidence.source_type != PARAMETER_CONFIGURATION_EVIDENCE_SOURCE_TYPE:
        raise ValueError("parameter_evidence.source_type incompatible")
    if evidence.captured_at != finance_input.snapshot.as_of_date:
        raise ValueError("parameter_evidence debe corresponder a la fecha del snapshot financiero")
    if evidence.state == "DEMONSTRATED" and evidence.demonstration_ref != resolved.configuration_ref:
        raise ValueError("parameter_evidence no está vinculada a la configuración P-FIN-002")

    unit = resolved.unit
    if finance_input.snapshot.currency == "EUR" and unit not in {"EUR", "€"}:
        return None

    try:
        value = Decimal(resolved.value)
    except (InvalidOperation, ValueError):
        return None
    if not value.is_finite() or value < 0:
        return None

    supplied_minimum = finance_input.treasury_minimum
    if supplied_minimum is not None and supplied_minimum != value:
        return None
    return value


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
    """Evaluate the authorized R-FIN-001 condition conservatively.

    Authorized quantitative condition:
    ``financial_capacity_forecast < P-FIN-002``.
    Missing/uncertain finance or parameter evidence remains NOT_EVALUABLE.
    """
    _validate_identity(purchase, context, rule, finance_input, finance_result)
    _validate_finance_evidence(finance_input, finance_result, finance_evidence)
    evidence_ids = [finance_evidence.evidence_id]

    if validate_evidence(finance_evidence).status != "VALID":
        return Assessment(
            rule_id=R_FIN_001,
            status="NOT_EVALUABLE",
            outcome=None,
            evidence_ids=evidence_ids,
            reason="R-FIN-001 no evaluable: Finance Basic no está demostrado.",
        )

    projection = finance_result.projection
    if projection.status != "DETERMINED" or projection.financial_capacity_forecast is None:
        return Assessment(
            rule_id=R_FIN_001,
            status="NOT_EVALUABLE",
            outcome=None,
            evidence_ids=evidence_ids,
            reason=f"R-FIN-001 no evaluable: proyección financiera {projection.status}.",
        )

    if threshold_resolution is None or parameter_evidence is None:
        return Assessment(
            rule_id=R_FIN_001,
            status="NOT_EVALUABLE",
            outcome=None,
            evidence_ids=evidence_ids,
            reason="R-FIN-001 no evaluable: P-FIN-002 no está resuelta/evidenciada.",
        )

    evidence_ids.append(parameter_evidence.evidence_id)
    threshold = _validate_parameter_resolution(
        finance_input, context, threshold_resolution, parameter_evidence
    )
    if validate_evidence(parameter_evidence).status != "VALID" or threshold is None:
        return Assessment(
            rule_id=R_FIN_001,
            status="NOT_EVALUABLE",
            outcome=None,
            evidence_ids=evidence_ids,
            reason="R-FIN-001 no evaluable: P-FIN-002 no es utilizable con evidencia suficiente.",
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


__all__ = [
    "FINANCE_BASIC_EVIDENCE_SOURCE_TYPE",
    "PARAMETER_CONFIGURATION_EVIDENCE_SOURCE_TYPE",
    "P_FIN_002",
    "R_FIN_001",
    "evaluate_r_fin_001",
    "finance_basic_result_ref",
]
