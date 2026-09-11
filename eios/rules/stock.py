"""Rules-layer bridges for authorized Stock Intelligence results."""
from __future__ import annotations

from eios.core.models import Assessment, DecisionContext, Evidence, PurchaseOperation, Rule
from eios.core.validation import validate_evidence
from eios.stock.models import ConfirmedDemandAbsorptionResult, ExcessResult


R_STK_003 = "R-STK-003"
R_STK_004 = "R-STK-004"
STOCK_EXCESS_EVIDENCE_SOURCE_TYPE = "StockExcessEvaluationEvidence"
STOCK_CONFIRMED_DEMAND_EVIDENCE_SOURCE_TYPE = "StockConfirmedDemandMitigationEvidence"


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
    "R_STK_003",
    "R_STK_004",
    "STOCK_CONFIRMED_DEMAND_EVIDENCE_SOURCE_TYPE",
    "STOCK_EXCESS_EVIDENCE_SOURCE_TYPE",
    "evaluate_r_stk_003",
    "evaluate_r_stk_004",
]
