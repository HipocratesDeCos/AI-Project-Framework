"""Rules-layer bridges for authorized Stock Intelligence results."""
from __future__ import annotations

from eios.core.models import Assessment, DecisionContext, Evidence, PurchaseOperation, Rule
from decimal import Decimal, InvalidOperation

from eios.core.validation import validate_evidence
from eios.parameters import ResolvedConfiguration
from eios.stock.models import ConfirmedDemandAbsorptionResult, ExcessResult
from eios.stock.rule_inputs import (
    JUSTIFIED_NEED_EVIDENCE_SOURCE_TYPE,
    PROJECTED_COVERAGE_EVIDENCE_SOURCE_TYPE,
    JustifiedNeedState,
    ProjectedCoverageAfterPurchase,
    justified_need_ref,
    projected_coverage_ref,
    stock_purchase_operation_ref,
)


R_STK_002 = "R-STK-002"
R_STK_003 = "R-STK-003"
R_STK_004 = "R-STK-004"
P_STK_004 = "P-STK-004"
PARAMETER_CONFIGURATION_EVIDENCE_SOURCE_TYPE = "ParameterConfigurationEvidence"
STOCK_EXCESS_EVIDENCE_SOURCE_TYPE = "StockExcessEvaluationEvidence"
STOCK_CONFIRMED_DEMAND_EVIDENCE_SOURCE_TYPE = "StockConfirmedDemandMitigationEvidence"


def _validate_stk002_identity(
    purchase: PurchaseOperation,
    context: DecisionContext,
    rule: Rule,
    coverage: ProjectedCoverageAfterPurchase,
    need: JustifiedNeedState,
) -> None:
    if purchase.decision_id != context.decision_id:
        raise ValueError("PurchaseOperation y DecisionContext tienen decision_id distintos")
    if purchase.scenario_id != context.scenario_id:
        raise ValueError("PurchaseOperation y DecisionContext tienen scenario_id distintos")
    if rule.rule_id != R_STK_002:
        raise ValueError("El bridge solo evalúa R-STK-002")
    if rule.version != context.rules_version:
        raise ValueError("Rule.version incompatible con DecisionContext.rules_version")
    if not rule.requires_evidence:
        raise ValueError("R-STK-002 requiere evidencia")

    expected_ref = stock_purchase_operation_ref(purchase)
    for label, carrier in (("coverage", coverage), ("need", need)):
        if carrier.decision_id != context.decision_id:
            raise ValueError(f"{label} pertenece a otra decisión")
        if carrier.scenario_id != context.scenario_id:
            raise ValueError(f"{label} pertenece a otro escenario")
        if carrier.data_snapshot_id != context.data_snapshot_id:
            raise ValueError(f"{label} usa otro data_snapshot_id")
        if carrier.article_id != purchase.article_id:
            raise ValueError(f"{label} pertenece a otro artículo")
        if carrier.evaluation_date != purchase.operation_date:
            raise ValueError(f"{label} usa otra evaluation_date")
        if carrier.purchase_operation_ref != expected_ref:
            raise ValueError(f"{label} no está vinculada a la PurchaseOperation exacta")

    for field in (
        "decision_id",
        "scenario_id",
        "data_snapshot_id",
        "company_scope",
        "article_id",
        "evaluation_date",
        "purchase_operation_ref",
    ):
        if getattr(coverage, field) != getattr(need, field):
            raise ValueError(f"coverage y need difieren en {field}")


def _validate_stk002_carrier_evidence(
    coverage: ProjectedCoverageAfterPurchase,
    coverage_evidence: Evidence,
    need: JustifiedNeedState,
    need_evidence: Evidence,
) -> None:
    if coverage_evidence.source_type != PROJECTED_COVERAGE_EVIDENCE_SOURCE_TYPE:
        raise ValueError("coverage_evidence.source_type incompatible")
    if need_evidence.source_type != JUSTIFIED_NEED_EVIDENCE_SOURCE_TYPE:
        raise ValueError("need_evidence.source_type incompatible")
    if coverage_evidence.captured_at != coverage.evaluation_date:
        raise ValueError("coverage_evidence debe corresponder a evaluation_date")
    if need_evidence.captured_at != need.evaluation_date:
        raise ValueError("need_evidence debe corresponder a evaluation_date")
    if (
        coverage_evidence.state == "DEMONSTRATED"
        and coverage_evidence.demonstration_ref != projected_coverage_ref(coverage)
    ):
        raise ValueError("coverage_evidence no está vinculada al carrier evaluado")
    if (
        need_evidence.state == "DEMONSTRATED"
        and need_evidence.demonstration_ref != justified_need_ref(need)
    ):
        raise ValueError("need_evidence no está vinculada al carrier evaluado")


def _coverage_maximum(
    coverage: ProjectedCoverageAfterPurchase,
    context: DecisionContext,
    resolved: ResolvedConfiguration,
    evidence: Evidence,
) -> Decimal | None:
    if resolved.parameter_id != P_STK_004:
        raise ValueError("R-STK-002 requiere P-STK-004")
    if resolved.parameters_version != context.parameters_version:
        raise ValueError("P-STK-004 está vinculada a otra parameters_version")
    if resolved.company_id != coverage.company_scope:
        raise ValueError("P-STK-004 pertenece a otro company_scope")
    if resolved.effective_at.date() != coverage.evaluation_date:
        raise ValueError("P-STK-004 debe resolverse para evaluation_date")

    configuration = resolved.configuration
    try:
        active = configuration.valid_from <= resolved.effective_at and (
            configuration.valid_to is None
            or resolved.effective_at < configuration.valid_to
        )
    except TypeError as exc:
        raise ValueError("P-STK-004 usa semántica temporal incompatible") from exc
    if not active:
        raise ValueError("P-STK-004 no está vigente en effective_at")

    if evidence.source_type != PARAMETER_CONFIGURATION_EVIDENCE_SOURCE_TYPE:
        raise ValueError("parameter_evidence.source_type incompatible")
    if evidence.captured_at != coverage.evaluation_date:
        raise ValueError("parameter_evidence debe corresponder a evaluation_date")
    if (
        evidence.state == "DEMONSTRATED"
        and evidence.demonstration_ref != resolved.configuration_ref
    ):
        raise ValueError("parameter_evidence no está vinculada a P-STK-004")

    if resolved.unit != "días":
        return None
    try:
        value = Decimal(resolved.value)
    except (InvalidOperation, ValueError, TypeError):
        return None
    if not value.is_finite() or value < 0:
        return None
    return value


def evaluate_r_stk_002(
    purchase: PurchaseOperation,
    context: DecisionContext,
    rule: Rule,
    coverage: ProjectedCoverageAfterPurchase,
    coverage_evidence: Evidence,
    need: JustifiedNeedState,
    need_evidence: Evidence,
    maximum_resolution: ResolvedConfiguration | None,
    parameter_evidence: Evidence | None,
) -> Assessment:
    """Evaluate high projected coverage with demonstrated absence of justified need."""
    _validate_stk002_identity(purchase, context, rule, coverage, need)
    _validate_stk002_carrier_evidence(
        coverage,
        coverage_evidence,
        need,
        need_evidence,
    )
    evidence_ids = [coverage_evidence.evidence_id, need_evidence.evidence_id]

    if (
        validate_evidence(coverage_evidence).status != "VALID"
        or validate_evidence(need_evidence).status != "VALID"
    ):
        return Assessment(
            rule_id=R_STK_002,
            status="NOT_EVALUABLE",
            outcome=None,
            evidence_ids=evidence_ids,
            reason="R-STK-002 no evaluable: facts STK002 no demostrados.",
        )

    if coverage.state not in {"FINITE", "UNBOUNDED"}:
        return Assessment(
            rule_id=R_STK_002,
            status="NOT_EVALUABLE",
            outcome=None,
            evidence_ids=evidence_ids,
            reason=f"R-STK-002 no evaluable: coverage {coverage.state}.",
        )
    if need.state not in {"PRESENT", "ABSENT"}:
        return Assessment(
            rule_id=R_STK_002,
            status="NOT_EVALUABLE",
            outcome=None,
            evidence_ids=evidence_ids,
            reason=f"R-STK-002 no evaluable: need {need.state}.",
        )

    if maximum_resolution is None or parameter_evidence is None:
        return Assessment(
            rule_id=R_STK_002,
            status="NOT_EVALUABLE",
            outcome=None,
            evidence_ids=evidence_ids,
            reason="R-STK-002 no evaluable: P-STK-004 no resuelta/evidenciada.",
        )

    evidence_ids.append(parameter_evidence.evidence_id)
    threshold = _coverage_maximum(
        coverage,
        context,
        maximum_resolution,
        parameter_evidence,
    )
    if (
        validate_evidence(parameter_evidence).status != "VALID"
        or threshold is None
    ):
        return Assessment(
            rule_id=R_STK_002,
            status="NOT_EVALUABLE",
            outcome=None,
            evidence_ids=evidence_ids,
            reason="R-STK-002 no evaluable: P-STK-004 no utilizable.",
        )

    if coverage.state == "UNBOUNDED":
        coverage_high = True
    else:
        assert coverage.coverage_days is not None
        coverage_high = coverage.coverage_days > threshold

    triggered = coverage_high and need.state == "ABSENT"
    return Assessment(
        rule_id=R_STK_002,
        status="EVALUABLE",
        outcome="TRUE" if triggered else "FALSE",
        evidence_ids=evidence_ids,
        reason=(
            "R-STK-002 demostrada: cobertura proyectada alta sin necesidad justificada."
            if triggered
            else "R-STK-002 no demostrada: cobertura/need no cumplen la condición conjunta."
        ),
    )


def _validate_common_identity(
    purchase: PurchaseOperation,
    context: DecisionContext,
    rule: Rule,
    excess: ExcessResult,
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

    identity = excess.identity
    if identity.decision_id != context.decision_id:
        raise ValueError("ExcessResult pertenece a otra decisión")
    if identity.scenario_id != context.scenario_id:
        raise ValueError("ExcessResult pertenece a otro escenario")
    if identity.rules_version != context.rules_version:
        raise ValueError("ExcessResult usa otra rules_version")
    if identity.parameters_version != context.parameters_version:
        raise ValueError("ExcessResult usa otra parameters_version")
    if identity.data_snapshot_id != context.data_snapshot_id:
        raise ValueError("ExcessResult usa otro data_snapshot_id")
    if identity.article_id != purchase.article_id:
        raise ValueError("ExcessResult pertenece a otro artículo")
    if excess.stock_reference.reference_kind != "PROJECTED":
        raise ValueError(f"{expected_rule_id} requiere referencia de stock PROJECTED posterior a la compra")


def _validate_m07_evidence(excess: ExcessResult, evidence: Evidence) -> None:
    if evidence.source_type != STOCK_EXCESS_EVIDENCE_SOURCE_TYPE:
        raise ValueError("stock_evidence.source_type incompatible")
    if evidence.state != "DEMONSTRATED":
        return
    allowed_refs = {*excess.trace_refs, *excess.stock_reference.trace_refs}
    if excess.stock_reference.source_ref:
        allowed_refs.add(excess.stock_reference.source_ref)
    if evidence.demonstration_ref not in allowed_refs:
        raise ValueError("stock_evidence.demonstration_ref no pertenece a la provenance M07")


def evaluate_r_stk_003(
    purchase: PurchaseOperation,
    context: DecisionContext,
    rule: Rule,
    excess: ExcessResult,
    stock_evidence: Evidence,
) -> Assessment:
    """Map the closed M07 excess result into R-STK-003."""
    _validate_common_identity(purchase, context, rule, excess, R_STK_003)
    _validate_m07_evidence(excess, stock_evidence)
    evidence_ids = [stock_evidence.evidence_id]

    if excess.state in {"UNKNOWN", "NOT_EVIDENCED", "CONFLICTING_DATA"}:
        return Assessment(
            rule_id=R_STK_003,
            status="NOT_EVALUABLE",
            outcome=None,
            evidence_ids=evidence_ids,
            reason=f"R-STK-003 no evaluable: estado M07 {excess.state}.",
        )
    if validate_evidence(stock_evidence).status != "VALID":
        return Assessment(
            rule_id=R_STK_003,
            status="NOT_EVALUABLE",
            outcome=None,
            evidence_ids=evidence_ids,
            reason="R-STK-003 no evaluable: la evidencia M07 no está demostrada.",
        )
    if excess.state == "EXCESS":
        return Assessment(
            rule_id=R_STK_003,
            status="EVALUABLE",
            outcome="TRUE",
            evidence_ids=evidence_ids,
            reason="R-STK-003 demostrada: stock proyectado por encima del máximo y tolerancia autorizados.",
        )
    if excess.state in {"NO_EXCESS", "WITHIN_TOLERANCE"}:
        reason = (
            "R-STK-003 no demostrada: no existe exceso de stock."
            if excess.state == "NO_EXCESS"
            else "R-STK-003 no demostrada: stock sobre máximo pero dentro de la tolerancia autorizada."
        )
        return Assessment(
            rule_id=R_STK_003,
            status="EVALUABLE",
            outcome="FALSE",
            evidence_ids=evidence_ids,
            reason=reason,
        )
    raise ValueError(f"Estado M07 no soportado para R-STK-003: {excess.state}")


def _validate_m08_evidence(absorption: ConfirmedDemandAbsorptionResult, evidence: Evidence) -> None:
    if evidence.source_type != STOCK_CONFIRMED_DEMAND_EVIDENCE_SOURCE_TYPE:
        raise ValueError("confirmed_demand_evidence.source_type incompatible")
    if evidence.state != "DEMONSTRATED":
        return
    allowed_refs = set(absorption.trace_refs)
    allowed_refs.update(absorption.excess_result.trace_refs)
    for item in absorption.allocation_plan:
        allowed_refs.add(item.allocation_source_ref)
        allowed_refs.update(item.trace_refs)
    if absorption.resulting_ledger is not None:
        if absorption.resulting_ledger.source_ref:
            allowed_refs.add(absorption.resulting_ledger.source_ref)
        allowed_refs.update(absorption.resulting_ledger.trace_refs)
    if evidence.demonstration_ref not in allowed_refs:
        raise ValueError("confirmed_demand_evidence.demonstration_ref no pertenece a la provenance M08")


def evaluate_r_stk_004(
    purchase: PurchaseOperation,
    context: DecisionContext,
    rule: Rule,
    absorption: ConfirmedDemandAbsorptionResult,
    confirmed_demand_evidence: Evidence,
) -> Assessment:
    """Map closed M08 confirmed-demand mitigation into R-STK-004.

    M08 preserves the original excess. TRUE means the exception is evidenced;
    it does not erase or rewrite the R-STK-003 Assessment.
    """
    _validate_common_identity(
        purchase,
        context,
        rule,
        absorption.excess_result,
        R_STK_004,
    )
    if absorption.identity != absorption.excess_result.identity:
        raise ValueError("M08 identity incompatible con M07")
    _validate_m08_evidence(absorption, confirmed_demand_evidence)
    evidence_ids = [confirmed_demand_evidence.evidence_id]

    if absorption.business_state == "NO_VERIFICABLE":
        return Assessment(
            rule_id=R_STK_004,
            status="NOT_EVALUABLE",
            outcome=None,
            evidence_ids=evidence_ids,
            reason="R-STK-004 no evaluable: la mitigación por pedido confirmado no es verificable.",
        )
    if validate_evidence(confirmed_demand_evidence).status != "VALID":
        return Assessment(
            rule_id=R_STK_004,
            status="NOT_EVALUABLE",
            outcome=None,
            evidence_ids=evidence_ids,
            reason="R-STK-004 no evaluable: la evidencia M08 no está demostrada.",
        )
    if absorption.business_state == "APLICABLE_Y_VALIDADA":
        return Assessment(
            rule_id=R_STK_004,
            status="EVALUABLE",
            outcome="TRUE",
            evidence_ids=evidence_ids,
            reason="R-STK-004 demostrada: pedido confirmado absorbe total o parcialmente el exceso M07.",
        )
    if absorption.business_state in {"NO_EXISTE", "NO_APLICABLE"}:
        return Assessment(
            rule_id=R_STK_004,
            status="EVALUABLE",
            outcome="FALSE",
            evidence_ids=evidence_ids,
            reason=f"R-STK-004 no demostrada: estado M08 {absorption.business_state}.",
        )
    raise ValueError(f"Estado M08 no soportado para R-STK-004: {absorption.business_state}")


__all__ = [
    "P_STK_004",
    "R_STK_002",
    "R_STK_003",
    "R_STK_004",
    "STOCK_CONFIRMED_DEMAND_EVIDENCE_SOURCE_TYPE",
    "STOCK_EXCESS_EVIDENCE_SOURCE_TYPE",
    "evaluate_r_stk_002",
    "evaluate_r_stk_003",
    "evaluate_r_stk_004",
]
